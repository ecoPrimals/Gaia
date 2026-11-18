# After Action Review — sporeGate Wave 157e Jelly String Cleanup + Pepti Layer

**Date**: Aug 10, 2026 | **Gate**: sporeGate (topology owner) | **Wave**: 157e

---

## Summary

Two implementation sessions: (1) **Golgi Thin Pepti Layer** plan — full 7-todo implementation for depot evolution, and (2) **Jelly string cleanup** — 7 legacy patterns excised from the codebase.

## Pepti Layer Implementation (Session 1)

### Completed

| Item | What shipped |
|------|-------------|
| **Wire `depot.prune`** | Auto-prune non-registry binaries in `finalize_depot()` after every harvest. `swarmvine` allow-listed. |
| **Unify depot path** | golgi Caddyfile updated to serve from `/opt/ecoPrimals/plasmidBin/primals`. Old `/opt/ecoPrimals/depot` removed. Broken symlinks cleaned. All 4 arch dirs consolidated. |
| **Disk health guard** | `push_depot_to_remote()` checks remote disk: warns at 80%, blocks at 90%. |
| **G69 Phase 3: CAS archival** | `archive_superseded_binary()` in `sovereignty_ledger.rs`. Wired into `stage_to_depot_async()` — before atomic rename, computes BLAKE3 diff, executes `depot_lineage` graph (sign→spine→braid→CAS). Best-effort, never blocks pipeline. |
| **Multi-arch manifest** | Registered `graftGate` (M4 Mac Mini, aarch64-apple-darwin), `eastGate` (aarch64-musl cross), `sporeGate` (android NDK cross) in `ecosystem_manifest.toml`. graftGate gate profile updated with `build_authority = true`. |
| **Forgejo GC timer** | `generate_forgejo_gc_timer()` + `install_forgejo_gc_timer()` in `systemd_units.rs`. Weekly Sunday 04:00. Wired via `gate.quorum --with-gc`. |
| **Ecosystem blurb** | Full Pepti-Layer Doctrine section added to `ECOSYSTEM_BLURB.md`: invariants, sub-builder fleet, binary evolution, gate role clarity. |

### Operational Notes

- golgi disk at 74% after cleanup (was 87% before depot pruning in prior session)
- Windows depot still has 25 binaries (includes non-primal artifacts from blueGate) — next wave prune will clean
- Caddy validated and reloaded successfully after path unification

## Jelly String Cleanup (Session 2)

### Excised

| Jelly string | Action |
|-------------|--------|
| **`MESH_REGISTRY` static IP table** | Added missing gates (strandGate, graftGate). Marked as deprecated fallback. Updated `KNOWN_MESH_GATES` and `KNOWN_GATES` const slices. New consumers must use manifest-based resolution. |
| **`freshness.toml` unify path** | Removed `unify_freshness()` function, `dispatch_unify_freshness` command, post_sync caller, `is_freshness_publisher()` function, dead test, `FRESHNESS_HEADER` constant. Per-gate `heads/*.toml` is now the sole freshness mechanism. |
| **SSH transport fallback in `sovereign.rs`** | Removed `transport = "ssh"` branch from `resolve_builder_endpoint()`. Mesh relay is now the only transport for sub-builders. Updated test. |
| **`golgi-post-receive-ci.sh` SSH dispatch** | Replaced `ssh root@10.13.37.2` with local `membrane sovereign.ci.trigger` which dispatches via mesh. No more hardcoded WireGuard IP. |
| **Broken `prov_inline` Python scripts** | Moved 7 scripts with broken `from prov_inline import` to `deprecated/`: `federation_test.py`, `gps_to_json.py`, `manifest_download.py`, `pdb_ingest.py`, `pdb_manifest_ingest.py`, `staging_experiment.py`, `convergence_drain.py`. Only `native_braid.py` remains active in scripts/. |
| **`depot-push-golgi.sh`** | Moved to `fossilRecord/depot-scripts/`. Fully replaced by `membrane plasmid.harvest --push` / `depot_sync_push_standalone`. |

### Not Excised (Deferred)

| Item | Reason |
|------|--------|
| **`caddy/mod.rs` SSH admin** | `caddy/depot.rs` submodule still actively used for depot route provisioning. Cannot delete parent module. |
| **`native_braid.py`** | 1,259-line bulk provenance braider — active pipeline on westGate. Needs dedicated Rust replacement (`membrane content.braid`). Multi-session effort. |
| **WireGuard core** | Active inner membrane overlay. Not a deprecation target — only the static IP table duplication was the jelly string. |

## Build Validation

- **852 tests pass** (membrane-shadow), 3 pre-existing UDS resolution failures unrelated to changes
- **Compiler warnings**: reduced from 5 to 2 (pre-existing unused struct warnings)
- **membrane binary**: rebuilt, installed locally, pushed to golgi depot
- **WAN fetch**: HTTP 200 confirmed at `depot.primals.eco`
- **Staleness**: 0 stale primals (13/13 current)

## Remaining Jelly Strings (for future waves)

1. `native_braid.py` → Rust `membrane content.braid` (largest remaining jelly string)
2. `caddy/mod.rs` SSH admin functions → fully retire when Tower gateway replaces all Caddy admin
3. `MESH_REGISTRY` → eventually remove when all consumers use manifest-based resolution
4. `westgate_boot_check.sh` → could become `membrane gate.preflight` extension

---

*sporeGate topology owner — pepti layer established, 7 jelly strings excised, depot unified at canonical path, pipeline revalidated.*
