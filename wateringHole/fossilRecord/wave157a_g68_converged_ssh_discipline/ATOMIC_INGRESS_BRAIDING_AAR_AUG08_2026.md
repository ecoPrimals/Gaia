# AAR: Atomic Ingress Braiding — No Data Without Provenance

**Date**: August 8, 2026
**Gate**: westGate (155f)
**Team**: Hardware / Overwatch
**Context**: Eliminating the download-then-braid anti-pattern across the data federation

## The Problem We Solved

The data federation pipeline had a structural flaw: download and braiding
were separate, sequential phases. rsync pulled data to cold storage, then
a separate process (eventually) braided it. This created:

1. **Unprovenanced windows**: Data sat on disk for hours/days without
   provenance. Any corruption, mutation, or loss during this window was
   invisible to the provenance chain.

2. **Jelly string accumulation**: Five Python scripts (`prov_inline.py`,
   `bulk_braid.py`, `revalidate_data.py`, `alphafold_prov_convoy.py`,
   `alphafold_bulk_download.py`) each reimplemented parts of the provenance
   pipeline in Python, bypassing Rust primal capabilities.

3. **Cold-tier computation**: Braiding scripts read directly from spinning
   disks, ignoring the 4-tier storage hierarchy. The staging experiment
   (same day) proved this was 3.9x slower than NVMe-staged processing.

4. **The 256 MB ceiling**: `nestGate content.ingest` silently skips files
   larger than 256 MB. AlphaFold tarballs (1-38 GB each) were silently
   dropped from CAS, creating gaps in the provenance chain.

## What We Changed

### 1. Jelly Script Cleanup

Archived 5 scripts to `scripts/deprecated/`:
- `prov_inline.py` (736 lines) — Python blake3, Python CAS put, Python DAG
- `bulk_braid.py` (521 lines) — Python orchestrator using prov_inline
- `revalidate_data.py` (210 lines) — Python re-ingestion
- `alphafold_prov_convoy.py` (434 lines) — multiprocessing Python braider
- `alphafold_bulk_download.py` (184 lines) — async downloader

Total: **2,085 lines of jelly removed from active use.**

### 2. native_braid.py Enhancements

`native_braid.py` is now the sole braiding tool. New capabilities:

- **`--incremental` mode**: Re-scans already-braided datasets for new files.
  Detects chunk growth (e.g., v6 went from 47→48→49 files as tarballs
  arrived) and re-braids only the changed chunks.

- **Streaming BLAKE3 for large files**: Files >256 MB that `content.ingest`
  skips are caught by a sweep in `ingest_directory()`. Each is hashed with
  streaming BLAKE3 (4 MB chunks, no OOM risk) and registered via
  `content.put`. The 256 MB ceiling is now transparent.

- **Root-level file handling**: Datasets with both subdirectories and
  top-level files (e.g., alphafold has v1-v6 dirs plus metadata CSVs)
  get a `_root` chunk that stages and braids root files separately.

- **Incremental claim management**: When `--incremental` detects a chunk
  grew, it releases the stale `.claim` file so the chunk can be re-entered
  and re-braided with the new files included.

- **Incremental finalization**: The `.braided` marker is updated even when
  re-braiding an already-marked dataset.

### 3. Atomic Ingress Script

`alphafold_full_sync.sh` restructured from:

```
for VER in v1..v6: rsync $VER
rsync sequences.fasta
rsync metadata
braid_everything_at_the_end   ← 18-hour unprovenanced gap
```

To:

```
for VER in v1..v6:
  rsync $VER
  braid_now   ← immediate, no gap
rsync sequences.fasta
braid_now
rsync metadata
braid_now
```

Every rsync phase is immediately followed by `native_braid.py --incremental`.
The braid is the ingress receipt. No data exists on disk without provenance.

### 4. I/O Hygiene

- `ionice -c3` applied to all rsync processes (idle scheduling class)
- All braiding stages to NVMe before processing (experiment-informed)
- `choose_staging_method()` auto-selects tar vs. rsync based on file count

## Results

### AlphaFold Backlog Cleared

| Chunk | Files | Data | Method | Time |
|-------|-------|------|--------|------|
| _root | 53 | 126.6 GB | NVMe stage + streaming BLAKE3 | 25 min |
| v1 | 20 | 45 GB | NVMe rsync stage | ~15 min |
| v2 | 49 | 137 GB | NVMe rsync stage | ~25 min |
| v3 | 51 | 121.6 GB | NVMe rsync stage | 19 min |
| v4 | 52 | 641 GB | NVMe rsync stage | 86 min |
| v5 | 50 | 144 GB | NVMe rsync stage | ~25 min |
| v6 | 49 | 157 GB | NVMe rsync stage (incremental) | 15 min |
| **Total** | **324** | **~1.3 TB** | | **~3.5 hours** |

### Spine Verification

- **Spine**: 244 entries (genesis + 243 session commits)
- **Total provenance events**: 990,648 across all commits
- **All primals responding**: nestGate, rhizoCrypt, loamSpine, sweetGrass, bearDog
- **sweetGrass braids**: Queryable via `braid.query`, W3C PROV JSON-LD format
- **bearDog key**: Ed25519 `9hD1X+...` active for signing

### Atomic Pipeline Verified

The restarted sync service successfully:
1. Detected v6 had grown 48→49 files (swissprot_pdb_v6.tar arrived)
2. Staged v6 to NVMe (809s)
3. Braided 49 files (42 large via streaming BLAKE3, 7 dedup)
4. Committed to spine, finalized dataset
5. Moved to next phase (sequences.fasta download, currently at 26 GB/118 GB)
6. All with no manual intervention

## biomeOS Neural API Interaction

### What Worked

- **Capability registry**: 2,088 capabilities auto-discovered across all
  primals. The registry at `/run/user/1000/membrane/capability-registry.json`
  provides a complete map of what each primal can do.

- **Direct primal queries**: All provenance verification (spine reads, DAG
  queries, braid queries, CAS existence checks) works through direct UDS
  socket connections with ribocipher framing. Response times <200ms.

- **biomeos-api routing hint**: The biomeos-api socket correctly reports
  that `capability.call` and `graph.execute` are the auto-proxied methods,
  pointing consumers toward the Stage 2 interface.

### What Needs Evolution

1. **`capability.call` timeout**: Routing through `neural-api` via
   `capability.call` times out for provenance queries. The neural-api
   process is alive (PID visible, responds to method-not-found errors)
   but the proxy to backend primals hangs. This may be a graph executor
   configuration issue or a missing route in the capability dispatch table.

2. **sweetGrass not in capability registry**: The 2,088 registered
   capabilities include nestGate, rhizoCrypt, loamSpine, bearDog, and
   12+ other primals — but sweetGrass is absent. It responds on its
   direct socket but hasn't announced to the registry. This means
   `capability.call("braid.query", ...)` can't route.

3. **No `rpc.discover` on any primal**: None of the 14 primals support
   method introspection. Consumers must know method signatures a priori.
   Adding `rpc.discover` or `help` would make the capability registry
   self-documenting.

4. **`native_braid.py` is still Stage 1**: It connects directly to primal
   sockets via hardcoded paths. When `capability.call` routing is fixed,
   it should be migrated to call through neural-api, eliminating the last
   socket path jelly strings. The script would become gate-portable: same
   code works on any gate without path changes.

5. **DAG session lifecycle**: `dag.session.list` returns 0 sessions after
   dehydration. Sessions appear to be ephemeral — created, events appended,
   dehydrated to Merkle root, then discarded. This is correct for storage
   efficiency but means post-hoc session inspection requires the spine
   commits (which do persist). A `dag.session.history` or similar would
   help forensic provenance analysis.

6. **content.ingest streaming**: The 256 MB ceiling is now worked around
   with streaming BLAKE3 + `content.put`, but this is a Python shim over
   a Rust limitation. A native `content.ingest_stream` RPC that handles
   arbitrarily large files would complete the NVMe-only processing story.

## Architecture Principle Established

**No data ingress without braids.** This is not just a tooling decision —
it's an architectural invariant. The braid IS the ingress receipt. If data
arrives and isn't braided, it doesn't exist in the federation. The atomic
sync script enforces this at the pipeline level, and the `--incremental`
mode ensures late arrivals are caught.

The corollary: **cold storage is for durability, not for work.** Every byte
is warmed to NVMe before processing. The staging experiment quantified this
(3.9x speedup for Type A data), and the atomic pipeline enforces it
structurally.

## Open Items

1. Fix neural-api `capability.call` proxy timeout
2. Register sweetGrass in capability registry
3. Migrate `native_braid.py` from Stage 1 (direct sockets) to Stage 2
   (capability.call routing)
4. Implement `content.ingest_stream` in nestGate for large-file native
   CAS ingestion
5. Add backpressure gating: pause rsync when NVMe staging space is low
   or interactive I/O latency exceeds threshold
6. Wire up cellMembrane convergence for night-window download scheduling
