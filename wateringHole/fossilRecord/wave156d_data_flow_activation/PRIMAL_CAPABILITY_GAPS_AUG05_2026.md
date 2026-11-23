# Upstream Primal Capability Gaps — westGate Field Report

**Date**: Aug 5, 2026 | **Wave**: 156d | **From**: westGate overwatch
**Context**: After migrating all Python glue from socat subprocess to native
socket RPC, we found that the primals themselves are fast (nestGate 16K RPCs/s,
rhizoCrypt <1ms batch). The remaining Python scripts exist only because the
primals don't yet expose certain operations natively.

---

## Capabilities That Would Eliminate Python Scripts

### nestGate

| Gap | Current Python Workaround | What It Would Do |
|-----|---------------------------|------------------|
| `content.fetch` | `curl` subprocess + `content.put` | Download URL directly into CAS. Fetch → hash → store in one RPC. Eliminates all download-then-ingest scripts. |
| `content.ingest` | Filesystem walk + per-file `read_bytes()` + `content.put` | Scan a directory, hash all files, bulk store. Eliminates `revalidate_data.py` entirely. |
| `dataset.convergence` | `convergence_check.py` (183 lines) — sample files, check CAS membership, query braids | Report provenance state (CONVERGED/PARTIAL/PRIMORDIAL/EMPTY) for a dataset path. Would be one RPC call. |
| `dataset.list` | Python `pathlib.iterdir()` on `/mnt/nestgate/cold/zfs/data/` | List known datasets with CAS stats. |
| `content.query` | Not currently possible | Query CAS by metadata (dataset, hash prefix, size range). |

### rhizoCrypt

| Gap | Current Python Workaround | What It Would Do |
|-----|---------------------------|------------------|
| `dag.pipeline.ingest` | Multi-step Python: `session.create` → per-file `event.append_batch` → `dehydration.trigger` | Full pipeline in one RPC: accept file list, create session, batch events, dehydrate, return Merkle root. |
| `dag.session.list` | No way to enumerate sessions | List active/completed sessions with stats. |

### sweetGrass

| Gap | Current Python Workaround | What It Would Do |
|-----|---------------------------|------------------|
| `convergence.check` | Manual chain: CAS exists? → DAG has events? → spine committed? → braid exists? → signed? | Verify full provenance chain for a dataset in one call. The trust gate for spring consumption. |
| `braid.list` | No way to enumerate braids | List braids by dataset, time range, committer. |
| `braid.validate` | Not possible without manual chain walk | Verify braid integrity: Merkle proof → signature → spine → DAG → CAS content hashes. |

### loamSpine

| Gap | Current Python Workaround | What It Would Do |
|-----|---------------------------|------------------|
| `spine.status` | `spine.list` exists but limited | Report spine health: entry count, last commit, Merkle root, associated sessions. |

---

## What Stays in Python (Appropriate)

These are data-specific or coordination tasks that don't belong in primals:

| Script | Lines | Why It's Python |
|--------|-------|-----------------|
| `alphafold_bulk_download.py` | 183 | HTTP API client for AlphaFold. Network I/O, API-specific retry/pagination. |
| `gps_to_json.py` | 309 | NumPy/pickle → JSON data transformation. Domain-specific. |
| `pdb_manifest_ingest.py` | 360 | PDB-specific batch hashing (b3sum multi-threaded, 257K files). |
| `westgate_boot_check.sh` | 309 | System health check (bash, systemd, ZFS). |

---

## What We Archived (Fossils)

| Script | Superseded By |
|--------|---------------|
| `bulk_ingest.py` | `prov_inline.py` (native sockets, in-process blake3) |
| `alphafold_prov_trailer.py` | `prov_inline.py` + `alphafold_prov_convoy.py` |
| `alphafold_bulk_structures.sh` | `alphafold_bulk_download.py` |
| `metered_download.sh` | `manifest_download.py` |

---

### nestGate — Multi-Tier CAS (P0 — DEPLOYED Aug 6, 2026)

| Gap | Status | Resolution |
|-----|--------|-----------|
| `content.put` tier-aware writes | **DEPLOYED** | `content_cas_write_path()` routes to first warm tier. `SubstrateTiers` wired via `OnceLock` in `storage_paths.rs`. Config: `NESTGATE_WARM_PATHS=/mnt/cas-hot`. |
| Cross-tier dedup check | **DEPLOYED** | `content_cas_find_across_tiers()` walks all warm + cold `SubstrateMount` paths before writing. Eliminates the 600 GB re-write bug from symlink-era tier switches. |
| High-water mark backpressure | **DEPLOYED** | `warm_tier_capacity()` via `statvfs`, rejects writes when free bytes < `NESTGATE_WARM_MIN_FREE_BYTES` (default 10 GB). |
| `content.archive` / drain hook | **P1 — NEXT** | Post-`spine.commit` hook: migrate committed CAS objects from warm → cold. `TierMigrationPlan` (ZFS `send/receive`) exists, needs wiring to RPC. |
| `NESTGATE_STORAGE_PATH` env var | **SUPERSEDED** | `NESTGATE_WARM_PATHS` / `NESTGATE_COLD_PATHS` now control tier routing, bypassing the XDG symlink. Old env var removed from `nestgate.env`. |

**What was unwired (now wired)**:
- `nestgate-config/substrate_tiers.rs`: `SubstrateTiers` — **now used by `content.put`** via `OnceLock` in `storage_paths.rs`
- `nestgate-zfs/automation/tier_migration.rs`: `TierMigrationPlan` — still unwired (P1 drain hook)
- `nestgate-cache/multi_tier.rs`: `MultiTierCache` — still unwired (future optimization)

**Deployment verification** (live on westGate Aug 6 07:43 EDT):
- New content → NVMe warm tier ✓
- Duplicate content (same tier) → dedup hit ✓
- Duplicate content (cross-tier, cold→warm) → dedup hit ✓
- Response includes `"tier"` field with write path ✓

---

## Priority for Upstream

**P0** (caused production outage — NVMe filled to 100%):
1. ~~`nestGate content.put` tier-aware writes~~ — **DEPLOYED Aug 6** (warm writes, cross-tier dedup, backpressure)
2. `nestGate content.archive` — drain warm → cold on spine commit

**P1** (would eliminate the most Python):
3. `nestGate content.ingest` — eliminates revalidate + convergence check + manual CAS orchestration
4. `sweetGrass convergence.check` — eliminates `convergence_check.py`, becomes the trust gate

**P2** (would simplify download pipelines):
5. `nestGate content.fetch` — download URL → CAS in one RPC
6. `rhizoCrypt dag.pipeline.ingest` — full pipeline in one call

**P3** (observability):
7. `sweetGrass braid.list` — enumerate braids for audit
8. `rhizoCrypt dag.session.list` — enumerate sessions
9. `nestGate dataset.list` — enumerate datasets with stats

---

## Metrics

| Before (socat era) | After (native socket) |
|---|---|
| 6 independent socat RPC copies | 1 canonical module (`prov_inline.py`) |
| 38 files/s provenance | 265 files/s inline, 130/s convoy |
| ~10ms per RPC (fork+exec+connect) | ~0.06ms per RPC (socket connect) |
| 4 fossil scripts | Archived to `fossilRecord/` |
| 11 active Python scripts | 10 active (bulk_ingest archived) |
| 0 scripts using native sockets | 8 scripts using `prov_inline` |

---

*The primals were always fast. nestGate handles 16K RPCs/s, rhizoCrypt <1ms
batch, bearDog signs in <5ms. Every performance issue we found was in the Python
glue layer — subprocess spawning, double file reads, sequential processing,
and most critically, storage topology (symlink routing, single-tier CAS,
no drain mechanism). P0 is now deployed: nestGate's `SubstrateTiers` is wired
into the CAS write path — warm writes, cross-tier dedup, high-water backpressure.
The nest atomic owns its pools. Remaining: P1 drain hook (`content.archive`
on `spine.commit`) to close the ephemeral lifecycle.*
