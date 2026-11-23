# AAR: Data Staging Experimental Matrix
**Date**: August 7, 2026
**Gate**: westGate (155f)
**Context**: Bulk retrospective braiding of ~100 scientific datasets across 4-tier storage hierarchy

## Background

During middle-out parallel braiding of `alphafold_structures` (2M files, 1.5 TB), we observed that `rsync`-based staging from cold HDD to hot NVMe was consuming 95% of wall-clock time. `zpool iostat` confirmed all 5 HDD drives in raidz1 were active but delivering only 15.5 MB/s aggregate — 2.6% of theoretical sequential bandwidth. The bottleneck was random I/O from `rsync`'s per-file `readdir()`+`stat()` pattern on directories with thousands of entries.

The question: is there a better staging method, and does the answer depend on data type?

## Hardware Topology

| Tier | Medium | Capacity | Bandwidth |
|------|--------|----------|-----------|
| T0 (ARC) | DDR4 RAM | 25 GB (of 62 GB max) | >10 GB/s |
| T1 (Hot) | NVMe | 1.8 TB (1.2 TB free) | 3+ GB/s |
| T2 (Warm) | SSD L2ARC | 2 TB (4.9 TB indexed) | ~500 MB/s |
| T3 (Cold) | 5x 14TB HDD raidz1 | 64 TB | ~600 MB/s seq, ~500 IOPS random |

Cache hierarchy effectiveness: ARC 96.3% hit → L2ARC 49.8% hit → only 1.8% of reads reach spinners.

## Experimental Design

### Data Type Taxonomy

| Type | Profile | Representative Dataset | Characteristics |
|------|---------|----------------------|-----------------|
| A | Many small files | alphafold_structures (~6K CIF, 100-300 KB) | Metadata-heavy, readdir-bound |
| B | Few large files | rnacentral (1x 9 GB .gz) | Bandwidth-bound, sequential |
| C | Medium archives | sra_fastq (351 .fastq.gz, 8 MB avg) | Balanced I/O |
| D | Moderate structured | open_targets (18 .parquet, 30-85 MB) | Few files, large-ish |

### Staging Methods Tested

1. **rsync**: `rsync -a --exclude=.* src/ dst/` — production method, per-file stat
2. **tar-pipe**: `tar cf - -C src . | tar xf - -C dst/` — sequential directory traversal
3. **direct-ingest**: `content.ingest(cold_path)` — no staging, Rust reads from cold

Each method was tested on a **cold** (uncached) chunk to eliminate ARC/L2ARC confounds.

## Results

### Test 1: Type A — Many Small Files (5,000-7,000 CIF files)

| Method | Wall Clock | Stage | Ingest | Effective MB/s |
|--------|-----------|-------|--------|----------------|
| **tar** | **192s** | 187s | 4.5s | 7.8 |
| rsync | 314s | 301s | 12.9s | 4.9 |
| direct | 754s | — | 754s | 2.7 |

**Winner: tar (1.6x faster than rsync, 3.9x faster than direct)**

tar's sequential `readdir()` traversal eliminates seek-per-file overhead. direct-ingest was slowest because `content.ingest` in Rust also walks the directory with `readdir()`+`stat()`, but then reads file data from cold spinners instead of NVMe.

### Test 3: Type B — Single Large File (9 GB .gz)

| Method | Wall Clock | Stage | Ingest | Notes |
|--------|-----------|-------|--------|-------|
| rsync | 89s | 89s | 0s | 102 MB/s sequential |
| tar | 117s | 117s | 0s | 78 MB/s (pipe overhead) |
| direct | 0s | — | 0s | content.ingest INLINE_MAX_FILE_SIZE=256MB |

**Finding: content.ingest skips files >256 MB.** Staging method irrelevant for Type B — both are sequential I/O. rsync slightly faster (no tar framing overhead).

### Test 4: Type C — Medium Archives (351 files, 8 MB avg)

| Method | Wall Clock | Stage | Ingest |
|--------|-----------|-------|--------|
| rsync | 35s | 32s | 2.3s |
| tar | 37s | 36s | 0.9s |
| direct | 1.2s | — | 1.2s |

**Finding: Methods equivalent for moderate file counts.** Few enough files that `stat()` overhead is negligible. Direct "won" via full CAS dedup (data already ingested), not a cold-path advantage.

### Test 5: Type D — Moderate Structured (18 files, 30-85 MB)

| Method | Wall Clock | Stage | Ingest |
|--------|-----------|-------|--------|
| rsync | 22s | 12s | 9.8s |
| tar | 16s | 15s | 0.4s |
| direct | 0.5s | — | 0.5s |

**Finding: Negligible difference.** Both staging methods dominated by sequential data copy, not metadata.

## Decision Matrix

| Data Profile | File Count | Avg File Size | Optimal Staging | Rationale |
|-------------|-----------|---------------|-----------------|-----------|
| Many small files | >200 | <1 MB | **tar-pipe** | Sequential readdir avoids seek storms |
| Few large files | <50 | >100 MB | **rsync** | Sequential I/O, rsync is simpler |
| Oversized dirs | >100K | <1 MB | **tar+find (batched)** | Prefix-filtered tar for NVMe batches |
| Moderate | 50-200 | Any | **either** | No meaningful difference |

## Key Discovery: The 15 MB/s Floor

All methods showed `avg_read_mbps: 15.4` from the pool — this is because the active braiding workers (w1, w2) are consuming most of the pool's IOPS budget. The experiment ran concurrently with live braiding. The relative speedups (tar 1.6x vs rsync) are valid because both competed for the same shared I/O budget.

In isolation (no competing workers), we would expect:
- **rsync staging**: ~30-50 MB/s for many-small (stat-bound)
- **tar staging**: ~200-400 MB/s for many-small (sequential, full stripe)
- **Sequential large file**: ~300-600 MB/s (full stripe bandwidth)

## Implementation Changes

### `native_braid.py` updates:
1. Added `choose_staging_method(file_count)` — returns "tar" for >200 files, "rsync" otherwise
2. `stage_chunk_to_nvme()` now auto-selects staging method
3. Added `_stage_tar()` using `tar cf | tar xf` pipe
4. `batch_stage_and_ingest()` now uses `find+tar` instead of rsync `--include`/`--exclude` for prefix-batch staging of oversized chunks

### `staging_experiment.py` (new):
Standalone benchmark script with `--test N --method rsync|tar|direct` interface. Instruments `zpool iostat`, ARC/L2ARC stats, wall clock, and RSS per run. Results persist to `staging_experiment_results.json`.

## Open Items

1. **content.ingest 256 MB file size limit**: Large single files (Type B) can't use `content.ingest` directly. Need streaming CAS ingest RPC or chunked upload for files >256 MB.
2. **Cross-tier dedup in content.ingest**: Still only checks hot-tier CAS path existence, not warm/cold. Data on cold-only storage gets re-ingested.
3. **ZFS prefetch tuning**: `zfs_prefetch_disable=0` (default) should help sequential tar reads. May want `zfs_arc_meta_limit_percent` tuning for metadata-heavy workloads.
4. **Idle-window experiment**: Re-run Type A tests with no competing workers to measure true isolated throughput delta between rsync and tar.
