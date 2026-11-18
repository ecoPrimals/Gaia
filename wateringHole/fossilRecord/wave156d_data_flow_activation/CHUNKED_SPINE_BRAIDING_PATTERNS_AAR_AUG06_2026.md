# AAR: Chunked Spine Braiding — Patterns for Ecosystem Adoption

**Date**: Aug 6, 2026 | **Wave**: 156d | **Gate**: westGate (Data NAS)
**Event**: Bulk retrospective braiding of 153 datasets through provenance trio
**Status**: 71/153 braided, ChunkedBraid deployed, AlphaFold (1.3 TB) in progress
**Team**: Hardware / Overwatch

---

## What We Built

Over three operational sessions (Aug 5–6), westGate evolved from a flat
provenance convoy (single session per dataset, no crash resume, no tier
awareness) to a production chunked braiding system. Every pattern emerged
from hitting a wall, diagnosing it, and evolving.

---

## Pattern 1: Never Braid on Spinners

**Discovery**: Bulk braider reading directly from HDD achieved 0.1 files/s.
The same files from NVMe staging: 81–1500 files/s.

**Why**: BLAKE3 hashing requires sequential reads. ZFS raidz1 on spinners
serves random I/O at ~28 MB/s. The same pool serves sequential reads at
~161 MB/s. But `ingest_file()` reads one file, hashes it, issues a CAS put,
reads the next — to the drive, this is random I/O across the entire pool.

**Pattern**: Stage → Braid → Unstage.
```
HDD (cold)  →  rsync  →  NVMe (hot staging)  →  BLAKE3 + CAS  →  rm staging
sequential reads           random reads are fast    dedup prevents re-writes
```

**Measured**: HDD→NVMe staging at 183–254 MB/s (sequential), NVMe braiding
reads at 1040 MB/s. The topology converts slow random HDD reads into fast
sequential copies followed by fast NVMe random reads.

**Ecosystem adoption**: Any gate braiding existing data MUST stage to its
fastest available tier first. If a gate has no NVMe, stage to SSD. If no
SSD, stage to a RAM tmpfs for small datasets. Never braid in-place on the
archive tier.

---

## Pattern 2: Ephemeral Hot Tier — Not Permanent Storage

**Discovery**: Repointing nestGate CAS writes to NVMe gave 2.4× throughput
improvement (131→313 files/s convoy). Five hours later, the NVMe (OS drive)
filled to 100%, crashing the convoy and degrading the system.

**Root cause**: The hot tier was treated as a permanent CAS sink. No drain
mechanism, no high-water mark, no cross-tier dedup.

**Pattern**: Hot tier is ephemeral working memory.
```
Ingest → NVMe (ephemeral)
                ↓ spine.commit triggers drain
         ZFS cold (permanent)
                ↓ NVMe freed
         Ready for next chunk
```

**What we wired**: Cross-tier dedup in `content.put` (check warm AND cold
before writing), high-water mark backpressure (reject writes when <10 GB
free), `NESTGATE_WARM_PATHS`/`NESTGATE_COLD_PATHS` environment variables
replacing the fragile XDG symlink.

**Ecosystem adoption**: Every gate with tiered storage must configure
`NESTGATE_WARM_PATHS` and `NESTGATE_COLD_PATHS`. The `nestgate.env` file
is the tier control surface. Never point CAS at a shared OS drive without
a high-water mark.

---

## Pattern 3: One Spine, N Sessions (Chunked Braiding)

**Discovery**: `InlineBraid` creates one DAG session per dataset. If the
process crashes, all progress is lost. For AlphaFold (1.3 TB, 6 version
dirs), a crash at 80% means re-braiding 1 TB of data.

**Pattern**: `ChunkedBraid` — one loamSpine per dataset, one rhizoCrypt
session per chunk (subdirectory). Each chunk is independently dehydrated
and committed to the spine. The `.braid_state` file persists after each
commit.

```
spine.create("federation:alphafold")  →  spine_id
  ├─ begin_chunk("v1")  →  session_id_1
  │    ├─ ingest files → dag.event.append_batch
  │    └─ commit_chunk() → dehydrate → session.commit → save .braid_state
  ├─ begin_chunk("v2")  →  session_id_2
  │    └─ ... (crash here → v1 is safe, resume from v2)
  └─ finalize() → sign → braid.create
```

**Crash resume verified**: Simulated interrupt after 2/4 chunks on
nf_data_portal. Restarted braider → "2 already committed (resume)", braided
only chunks 3-4, finalized with all 4. Zero re-work.

**Ecosystem adoption**: All retrospective braiding should use `ChunkedBraid`.
`InlineBraid` remains appropriate for inline (download-time) braiding where
the dataset is small and the session is short-lived.

---

## Pattern 4: CAS Dedup as Write Amplification Guard

**Discovery**: When the XDG symlink moved CAS writes from ZFS to NVMe,
`content.put`'s dedup check (`object_path.exists()`) only checked the new
path. ~600 GB of already-CAS'd data was re-written because the objects
didn't exist at the NVMe path.

**Pattern**: Cross-tier dedup. `content.put` must check all configured tiers
before writing. This turns re-braiding from O(n) disk writes into O(n) RPC
calls with near-zero disk I/O.

**Measured**: Second braid of nf_data_portal (644 files, 246 MB): 1481 files/s.
First braid: 81 files/s. The 18× speedup is entirely CAS dedup — the data
was already stored from the first run.

**Ecosystem adoption**: Cross-tier dedup is now live in nestGate's
`content.put`. Any gate running multi-tier CAS gets this automatically after
the Aug 6 upstream merge.

---

## Pattern 5: Convergence Backpressure

**Design** (partially implemented): `convergence_gate()` checks two pressure
signals before allowing the pipeline to proceed:

1. Warm tier free space (via `os.statvfs`)
2. sweetGrass convergence lag (via `convergence.batch_check` RPC)

Returns GO/WAIT/STOP verdict. Download and braiding scripts call this in
their main loops.

**Ecosystem adoption**: Any gate pulling data should integrate
`convergence_gate()` into its download loop. This prevents the hot tier from
filling and ensures provenance keeps pace with acquisition.

---

## Pattern 6: Streaming Hash for Large Files

**Discovery**: `InlineBraid.ingest_file()` calls `fp.read_bytes()` — loading
the entire file into memory. For ncbi_nr (49 GB single file), this OOM-killed
the braider (exit 137).

**Pattern**: `ChunkedBraid.ingest_file()` uses streaming BLAKE3 for files
larger than 100 MB. Reads in 8 MB chunks, never holds the full file in memory.
For files under 100 MB, the full-read path remains (faster for small files).

**Ecosystem adoption**: All braiding code should use `ChunkedBraid` or adopt
the streaming pattern for large-file datasets.

---

## Pattern 7: Owner Field on spine.create

**Discovery**: `InlineBraid`'s `spine.create` call was silently failing
because loamSpine requires an `owner` field. The spine_id was always
`"pending"`, meaning no spine commits, no signatures, no spine-level
verification.

**Pattern**: Always pass `"owner": COMMITTER_DID` to `spine.create`.

**Ecosystem adoption**: All primal RPC callers should test for `None` returns
from `_rpc_result` and treat them as errors, not silently degrade. The
primals' error messages are precise — the `owner` missing error was
`"missing field 'owner'"` — but `_rpc_result` swallowed it.

---

## Jelly Strings Resolved This Wave

| Jelly String | Impact | Fix |
|-------------|--------|-----|
| `NESTGATE_STORAGE_PATH` env var ignored | CAS wrote to wrong tier | Use XDG symlink or `NESTGATE_WARM_PATHS` |
| XDG symlink as tier control | Fragile, no cross-tier dedup | `NESTGATE_WARM_PATHS`/`COLD_PATHS` env vars |
| `object_path.exists()` single-tier dedup | 600 GB re-written to NVMe | `resolve_cas_object` cross-tier check |
| No high-water mark | NVMe filled to 100% | `warm_tier_capacity()` guard |
| `spine.create` missing `owner` | All spines returned `"pending"` | Added `owner: COMMITTER_DID` |
| `fp.read_bytes()` for large files | OOM on ncbi_nr (49 GB) | Streaming 8 MB chunk hash |
| `ureq` v3 body API change | `content.fetch` wouldn't compile | `body.as_reader().read()` |
| No crash resume for braiding | Full re-braid on any failure | `.braid_state` + `ChunkedBraid` |

---

## Hardware Topology Profile

| Tier | Device | Seq Read | Rand Read | Write | Role |
|------|--------|----------|-----------|-------|------|
| T0 | RAM (ZFS ARC, 18-31 GB) | 5.9 GB/s | 5.9 GB/s | — | Hot CAS cache |
| T1 | NVMe (Samsung 980 Pro 2TB, OS) | 2.5 GB/s | — | 1.5 GB/s | Staging + ephemeral CAS |
| T2 | SSD (Samsung 860 EVO 2TB) | ~500 MB/s | — | — | ZFS L2ARC (warm read cache) |
| T3 | 5× Seagate 14TB raidz1 | 161 MB/s | 28 MB/s | — | Archive (permanent CAS + data) |

**Measured staging throughput**: 183–254 MB/s (HDD→NVMe rsync)
**Measured NVMe braiding reads**: 1040 MB/s
**ZFS ARC hit rate**: 97.2% (3.4B hits / 122M misses)

---

## Current Run Status

| Metric | Value |
|--------|-------|
| Datasets braided | 71/153 (46%) |
| In progress | AlphaFold (1.3 TB, 3/6 chunks committed) |
| Remaining | 79 datasets after AlphaFold |
| Empty (no files) | 22 datasets |
| Skipped (too large for current run) | alphafold_structures, sra_fastq |
| Wall time so far | ~67 min |

---

## Recommendations for Other Gates

1. **Profile before braiding.** Run `zpool iostat`, check ARC hit rate, measure
   tier speeds. The topology determines throughput, not the primals.

2. **Stage to fastest tier.** Even a tmpfs is better than braiding on spinners.

3. **Use `ChunkedBraid` for anything with subdirectories.** The crash resume
   alone justifies the pattern.

4. **Configure `NESTGATE_WARM_PATHS`/`NESTGATE_COLD_PATHS`.** The multi-tier
   CAS is live — use it.

5. **Watch NVMe free space.** Until `nestGate` has native drain hooks, manual
   monitoring or `convergence_gate()` integration is required.

6. **Repurpose, don't purchase.** westGate's upcoming NVMe + RAM upgrade is $0
   from ecosystem inventory.
