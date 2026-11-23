# cellMembrane Wave 157d — Deep Debt Sweep + G69 Depot Lineage

**Date:** 2026-08-09 | **Gate:** eastGate overwatch | **Wave:** 157d

---

## Session Summary

Three commits pushed to git.primals.eco covering G69 Phase 1, systematic
hardcode elimination, and error hardening across the entire crate surface.

---

## Commit 1: G69 depot.prune (1e9d32b)

**G69 Depot Lineage Phase 1** — registry-driven depot cleanup.

| Item | Detail |
|------|--------|
| `depot.prune` command | Scans `primals/{arch}/`, compares against service registry, removes unknown binaries |
| `--dry-run` | Reports what would be pruned without deleting |
| `--allow=<name>` | Permits binaries not yet in registry (e.g. swarmvine) |
| Unified dispatch | `depot.*` commands now route through `dispatch_depot()` |
| `BLAKE3SUMS_FILE` | Promoted from local constant to `cellmembrane-types` |
| `format_bytes()` | Elevated to `pub(crate)` for cross-module reuse |
| Tests | 4 new prune tests |
| Registry | 103→104 entries (`depot_prune`) |

**Files:** +366/-63 across 16 files

---

## Commit 2: Hardcode Elimination + Zero Clippy (18e5cdb)

Systematic hardcode sweep across both crates.

| Category | Changes |
|----------|---------|
| Port literals | 14 in registry.rs → named constants; 7 new (builder 9800, skunkbat 9140, rhizocrypt 9601/9602, loamspine 9700, sweetgrass 9850, hbbs-NAT 21116) |
| IP literals | `0.0.0.0`/`127.0.0.1` in builder.rs + transport.rs → `BIND_ALL`/`BIND_LOOPBACK` |
| Self-knowledge | `"blueGate"` fallback in sovereign.rs → empty vec (manifest-only). Sporeprint unit filenames → registry-derived |
| Silent IPC | Non-Unix `sync_ipc.rs` no-ops → `tracing::warn` |
| Deprecation | `DEFAULT_SERVICE_FILTER` formally `#[deprecated]` |
| Clippy | 3 pre-existing warnings fixed → **first zero-warning run** |

**Files:** +112/-60 across 12 files

---

## Commit 3: Error Hardening + Dead Code Audit (4420780)

Silent error swallowing eliminated across I/O boundaries.

| Path | Before | After |
|------|--------|-------|
| Webhook listener (6 sites) | `let _ = write_all` | `send_response()` + `tracing::debug` |
| BTSP handshake (7 sites) | `.ok()?` | Explicit `match` + `debug!` per failure |
| Tower timer benchmark | `let _ = atomic_write` | `if let Err` + logged |
| `StalenessEntry` | Struct-level `#[allow(dead_code)]` (incorrect) | Field-level on `source_commit` only |
| Transport/ribocipher | Bare `#[allow(dead_code)]` | `reason = "G66 ..."` annotations |

**Files:** +95/-27 across 7 files

---

## Deep Debt Audit Findings

Full codebase audit confirmed:

| Category | Status |
|----------|--------|
| Unsafe code | **ZERO** — `#![forbid(unsafe_code)]` on both crates |
| Production `.unwrap()` | **ZERO** in async/network/file paths |
| External deps | Already lean + pure Rust (reqwest already gone) |
| Files >800L | **ZERO** (max 735, down from 855) |
| `todo!()` / `unimplemented!()` | **ZERO** in production code |
| Production mocks | Named Pipe stubs only (platform parity, not debt) |

### Remaining known patterns (not immediately actionable)

- ~70 functions >60 lines (dispatch/lifecycle pipelines — incremental splits)
- `MESH_REGISTRY` / `cytoplasm.rs` gate constants (bootstrap-only, manifest-preferred)
- Named Pipe / Windows IPC stubs (platform parity scope)
- `chrono` → `time` crate (minor, optional)

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | **1347** (up from 1329) |
| Clippy warnings | **0** (first time) |
| Capabilities registered | **104** |
| Files changed | 35 |
| Lines | +573/-150 net |

---

## `native_braid.py` Assessment

Located at `infra/wateringHole/scripts/native_braid.py` (1224 lines). This is a
**westGate-specific** data braiding orchestrator that RPCs into nestGate/rhizoCrypt/
loamSpine/sweetGrass primals via UDS. The Rust conversion is westGate garden scope,
not cellMembrane code. Filed as upstream note.

---

## Upstream Notes for Primal Teams

- **All gates**: `LimitNOFILE=65536` code shipped but needs redeploy on westGate, strandGate, blueGate, southGate, eastGate
- **sourDough**: `rpc-surface` audit tool should validate against expanded `capability_registry.toml` (104 entries)
- **westGate**: `native_braid.py` → Rust conversion is westGate garden scope
- **biomeOS**: Neural API `capability.resolve` can now use `ServiceCapability::from_wire()` for string-to-enum parsing

---

*Wave 157d — 3 commits, +573/-150, 1347 tests, zero clippy, zero unsafe. Depot pruning operational. Hardcodes eliminated. Error paths hardened.*
