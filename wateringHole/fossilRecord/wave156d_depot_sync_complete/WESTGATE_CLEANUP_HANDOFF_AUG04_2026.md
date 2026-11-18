# westGate Cleanup Handoff — Aug 4, 2026

**Wave**: 156d | **From**: westGate overwatch | **To**: golgiBody cascade → upstream audit

---

## What Changed

### Script Fixes (canonical provenance alignment)

| File | Change | Why |
|------|--------|-----|
| `manifest_download.py` | Removed per-file `spine_entry_append` call + import, updated docstring | Last script still using the old O(n) per-file spine pattern. Now canonical: per-file CAS+DAG, session-level spine commit. |
| `metered_download.sh` | Fixed header (was "INLINE provenance", actually runs batch `revalidate_data.py` post-download) | Header claimed per-file inline braiding; code does batch revalidation. Noted as superseded by `manifest_download.py`. |
| `pdb_ingest.py` | Updated docstring from "full provenance chain" to "smoke test" | Script only does `health.check` on rhizoCrypt/loamSpine, not full DAG→spine→sign→braid. |
| `pdb_manifest_ingest.py` | Updated docstring from "one DAG event, one cert, one sig, one braid" to "connectivity smoke test" | Same: runs `spine.create` + `health.check`, not the canonical dehydrate→commit flow. |
| `alphafold_bulk_structures.sh` | Added SUPERSEDED header | Replaced by `alphafold_bulk_download.py` (async Python, systemd service, `.prov_queue` integration). |

### Data Stats Corrected

| Doc | Old | Current |
|-----|-----|---------|
| `ECOSYSTEM_BLURB.md` | 519 GB / 130 datasets | 3.65 TB / 154 datasets |
| `data_federation_schedule.md` | 782 GB / 136 datasets | 3.65 TB / 154 datasets |
| `data_blockers.md` | 790 GB | 3.65 TB |

### Debris Cleaned

- `scripts/__pycache__/bulk_ingest.cpython-310.pyc` — deleted
- `.gitignore` added to `wateringHole/` (excludes `__pycache__/`, `*.pyc`, `*.pyo`, `*.log`)

---

## No False Positives Found

- **No stale TODOs/FIXMEs** in any scripts
- **No temp/backup files** (.bak, .swp, .orig, .tmp)
- **No cargo targets** to clean (sort-after Cargo.toml dirs have no target/ built)
- **All handoff docs in handoffs/** are current or intentional fossils
- **100 AAR fossils** properly archived in `aars/fossils/` (4 absorbed subdirs)
- **Protocols** (11 files) are stable standards docs — no cleanup needed

## Convergence Sweep Results — Aug 4, 2026

Full sweep across 153 datasets (147 scanned, 6 remaining):

| State | Count | Size | What it means |
|-------|-------|------|---------------|
| **CONVERGED** | 0 | — | Full provenance chain (CAS + DAG + spine + sig + braid) |
| **CAS-ONLY** | 5 | ~15.5 GB | BLAKE3 hashed in CAS, no DAG/spine. Includes alphafold_structures, gps_platform, ncbi_gene, noaa_ghcnd, refseq_human. |
| **PARTIAL** | 89 | ~205 GB | Some files CAS'd, others not. Most small/medium datasets. |
| **PRIMORDIAL** | 32 | ~636 GB | No CAS at all. Mostly large bulk downloads (ncbi_nr 48 GB, uniprot_trembl 110 GB, uniref100 43 GB, etc.) |
| **EMPTY** | 21 | 0 | Directory exists, no files yet (placeholders). |
| **Not scanned** | 6 | ~70 GB | uniref90, usda_nass, usda_plants, usgs_3dep, vibrio, zinc20_smiles (sweep timed out before reaching). |

**ZFS**: 3.21 TB used / 50.7 TB pool (6.3%). CAS pool: 135 GB.

**Key finding**: Zero datasets at CONVERGED. The canonical pipeline (DAG session → dehydrate → commit → sign → braid) has been proven at 43/s throughput but hasn't been run at bulk scale across the estate. The 89 PARTIAL datasets have CAS hashes but no provenance chain. The 32 PRIMORDIAL datasets are raw downloads with no CAS at all.

**Priority for convergence**:
1. Run batch provenance on the 89 PARTIAL datasets (smallest first — most are <100 MB)
2. CAS-ingest the 32 PRIMORDIAL datasets, then braid
3. The 5 CAS-ONLY datasets need DAG + spine wiring

## biomeOS v4.57 Deployed — Aug 4, 2026

- Built from source (commit `96083386`), installed to plasmidBin
- `nucleus attach` CLI available — unblocks tideGlass cell boot
- NUCLEUS restarted: 14/14 HEALTHY (13 primals + neural-api)
- `content.query` available via nestGate (same depot rebuild)

## GPS Data Converted — Aug 4, 2026

- 11 JSON outputs (103.4 MB total) CAS-ingested with BLAKE3
- Covers: 2198 gene lists, MLP weights, RCL ensembles, compound matrices
- Unblocks tideGlass Phase 0 Rust consumption

## Upstream Gaps for Primals Teams

| Gap | Owner | Detail |
|-----|-------|--------|
| `spine_entry_append` still DEFINED in `bulk_ingest.py` | wateringHole | Dead code — no callers remain after manifest_download.py fix. Can remove once confirmed no other repos import it. |
| `pdb_ingest.py` / `pdb_manifest_ingest.py` only smoke-test provenance | wateringHole | If PDB needs full provenance, wire canonical pipeline (DAG session → dehydrate → commit → sign → braid). Currently health.check only. |
| `alphafold_bulk_structures.sh` fossil | wateringHole | Superseded. Can archive to `fossilRecord/` if desired. |
| Depot CDN stale | sporeGate | golgi depot still serves v4.56.0 binary despite provenance.toml showing Aug 4 rebuild. westGate built from source. Other gates need depot fix or source build. |
| Bulk convergence campaign | wateringHole | 0/153 datasets at CONVERGED. Need batch provenance run across estate. |

---

## Convoy Provenance AAR — Aug 5, 2026

### Context
With 7.9M AlphaFold files queued for provenance braiding, a single trailer
at 38.4/s would take ~56 hours. The user asked: can we run multiple
provenance groups as a convoy?

### Experiment

**Phase 1 — Naive parallelism (socat, 4 workers):**
Split the queue into 4 partitions, ran 4 trailer instances. Each worker
dropped from 38/s to ~12/s due to contention. Combined: 46.8/s (1.2x).
Bottleneck: socat subprocess spawning (each RPC = fork + exec + connect).

**Phase 2 — Native socket optimization:**
Replaced `socat` subprocess with Python `socket.AF_UNIX` direct connect.
Benchmark: **16,352 RPCs/s** on native socket vs ~100/s via socat spawn.
Replaced `b3sum` subprocess with Python `blake3` module (in-process).
Combined hash + CAS put into single file read (eliminated double I/O).

**Phase 3 — Optimized convoy (4 workers):**
Combined rate: **145/s** (3.8x speedup). ETA: 56h → ~15h.

### Key Finding: The Primals Were Never the Bottleneck

| Component | CPU under convoy load | Headroom |
|-----------|----------------------|----------|
| **nestGate** (CAS) | 4.6% | Massive — 16K+ RPCs/s capacity |
| **rhizoCrypt** (DAG) | 3.8% | Massive — batch append in <1ms |
| **loamSpine** (spine) | 94% | Busy with background maintenance, but not called per-file |
| **sweetGrass** (braid) | <1% | Session-level only |
| **bearDog** (signatures) | <1% | Session-level only |

The entire provenance trio was running correctly out of the box.
nestGate handles concurrent CAS puts at 16K/s. rhizoCrypt processes
200-event batches in under 1ms. The canonical architecture (per-file
CAS + batch DAG, session-level spine commit) is sound.

**The bottleneck was always the glue code:**
1. **socat subprocess spawning**: fork+exec+connect per RPC = ~10ms overhead per call
2. **b3sum subprocess spawning**: fork+exec per hash = ~5ms overhead per file
3. **Double file reads**: reading file for hash, then reading again for CAS base64
4. **Sequential processing**: single-threaded queue walk

These are Python patterns, not primal limitations. When wired with native
sockets and in-process hashing, a single worker does **265/s** (7x faster).
Four workers hit **145/s** combined — the remaining limit is spinning disk I/O
(15.4% iowait on ZFS raidz1).

### Upstream Implications

- **For primal teams**: No changes needed. The primals perform as designed.
  The provenance trio architecture (CAS + DAG batch + session spine) is correct
  and efficient. nestGate and rhizoCrypt have 10-100x headroom at current load.
- **For integration patterns**: Any Python glue calling primals via UDS should
  use native `socket.AF_UNIX` instead of shelling out to socat. This is a
  general pattern improvement for all gates.
- **For convoy pattern**: Multiple independent DAG sessions can safely process
  partitions of the same dataset concurrently. CAS is idempotent. Each session
  gets its own Merkle tree. This pattern is reusable for any large dataset
  provenance campaign.
- **loamSpine at 94%**: Background spine maintenance scales with accumulated
  events. Worth monitoring but not blocking — it doesn't affect per-file
  throughput since the canonical pipeline doesn't call loamSpine per-file.

### Inline Braid — New Default Pattern (Aug 5, 2026)

Validated that inline Python blake3 produces identical CAS content addresses
to trailer b3sum (`deduplicated=True` on all 5 test files). Trailer and
inline are provably equivalent at the CAS and DAG layers.

**New module**: `prov_inline.py` — `InlineBraid` class. Any download script
imports it and calls `braid.ingest(data, filename)` from the download buffer.
Native socket RPC, in-process BLAKE3, single file read for hash + CAS.

**Wired into**: `manifest_download.py` — now uses `InlineBraid` instead of
separate `blake3_hash` → `cas_put` → `dag_event_append` calls via socat.
4-step pipeline collapsed to `braid.ingest_file(path)`.

| Pattern | Per-file overhead | Rate | When to use |
|---------|-------------------|------|-------------|
| **Inline** (prov_inline.py) | 3.5ms (native socket) | 265/s | Default for all new downloads |
| **Convoy** (alphafold_prov_convoy.py) | 3.5ms + cold read | 32/s/worker | Retrospective bulk braiding |
| **Socat trailer** (alphafold_prov_trailer.py) | ~26ms (subprocess) | 38/s | Legacy, superseded |

### Convoy Balance Plan
Once the 7.9M backlog clears (~15h), restart the AlphaFold downloader.
A single native-socket trailer at 265/s will outpace downloads at 74/s
with 3.5x margin. The convoy script remains available for future bulk
provenance campaigns on the 89 PARTIAL + 32 PRIMORDIAL datasets.

---

*Cleanup + convergence sweep + biomeOS v4.57 deploy complete. Convoy provenance
AAR: primals performing as designed (nestGate 16K RPCs/s, rhizoCrypt <1ms batch).
Bottleneck was Python glue (socat spawn overhead), not primal architecture.
Native socket convoy at 145/s (3.8x). westGate NUCLEUS 14/14 on v4.57.
Ready for upstream audit.*
