# NestGate Wave 128b — Evolution Pass

**Date**: June 28, 2026  
**Author**: eastGate overwatch (convergence + debt posture)  
**Verification**: 12,885 passed, 0 failed, 420 ignored; clippy clean; fmt clean

---

## Changes

### Dependency Evolution

- **Dead deps purged**: `lru` (unused in any crate), `getrandom` (workspace-only, unreferenced), `fastrand` (consolidated → `rand`)
- **5 callsites migrated**: `fastrand::f64()` / `fastrand::u64(..)` → `rand::random::<f64>()` / `rand::random_range(..)` in retry_strategy.rs, fault_injection_tests.rs, performance_stress_battery.rs
- **Full dependency audit** completed — supply-chain posture documented: `bincode` (unmaintained via tarpc, tracked), `rustls-rustcrypto` (alpha, vendored), `blake3` pure build needs C-toolchain verification

### Clone Optimization (Arc patterns)

- `PrimalSelfKnowledge::discovered_primals` DashMap: `DiscoveredPrimal` → `Arc<DiscoveredPrimal>` — cache hits are pointer clones
- `discover_primal()` returns `Arc<DiscoveredPrimal>` instead of cloning the full struct on every cache hit
- `RuntimeDiscovery::CachedDiscovery.capabilities` wrapped in `Arc<Vec<CapabilityDescriptor>>` — same O(1) cache-hit pattern

### Smart File Refactoring

- `content_handlers.rs` (795L, largest production file) → directory module:
  - `mod.rs` — validation, sidecar merge, `maybe_decrypt()` (DRY), re-exports (~90L)
  - `cas.rs` — `content_put`, `content_get`, `content_exists`, `content_list` (~230L)
  - `manifest.rs` — `content_publish`, `content_resolve`, `content_promote`, `content_collections`, resolve helpers (~275L)
  - `raw.rs` — `RawContent`, `content_get_raw` (~70L)
- Zero API surface change — all re-exports preserved

### Fabricated Metrics Eliminated

| Function | Before | After |
|----------|--------|-------|
| `get_zfs_cache_hit_ratio` | `Ok(85.0)` fallback | `Ok(None)` when `/proc/spl` unavailable |
| `get_real_queue_depth` | Fake "real" values in `Result` | Renamed `default_queue_depth`, returns `f64` directly |
| `get_active_migration_jobs` | `Ok(1)` always | `Ok(0)` (no migration engine wired) |
| `execute_fallback_operation` | Silent `Ok(())` | `Err(ServiceUnavailable)` |
| `announce_via_method` (capability_based_config) | `debug!()` + `Ok(())` for mDNS/DNS-SD/Consul | `anyhow::bail!()` |

### Documentation Cleanup

- **Fossilized** 4 stale guides to `ecoPrimals/infra/fossilRecord/nestgate/historical-docs-jun2026-wave128b/`:
  - `COMMON_TASKS.md` (fictional REST routes, non-existent Docker/API)
  - `TROUBLESHOOTING.md` (stale REST paths, wrong env var names)
  - `ZERO_COPY_OPTIMIZATIONS.md` (references removed modules)
  - `DEVELOPER_ONBOARDING.md` (9,083 test count, wrong Rust version, missing doc tree)
- **Updated** `ENVIRONMENT_VARIABLES.md`: HTTP default, `nestgate server`, removed dead integration links
- **Updated** `DOCS_QUICK_GUIDE.md`: trimmed to current docs/ tree
- **Synced** test counts (12,885/420) across 8 root docs

---

## Remaining Items for Upstream

### P1 — Supply Chain
- `blake3` `pure` feature: `Cargo.lock` still lists `cc` — verify no C compilation in production build
- `bincode` unmaintained (RUSTSEC-2025-0141) — blocked on tarpc upstream
- `rustls-rustcrypto` alpha disclaimer — track upstream releases

### P2 — Remaining Stubs (~25 production paths)
- `FailSafeZfsService` dataset_operations: circuit-open path now errors (honest)
- Remote ZFS backend (`implementation.rs`): `get_metrics`/`optimize`/`predict_tier`/`get_configuration` still return structured zeros/defaults on error
- `create_optimal_config` (auto_configurator): synthetic config with `confidence_score: 0.8`
- `start_discovery`/`start_health_monitoring` (consolidated_canonical): `Ok(())` no-ops
- `register_capability_endpoint` (registry.rs): log-only, no outbound registration

### P3 — Code Quality
- `parking_lot` vs `std::sync::RwLock` — pick one convention
- `crossbeam` single-usage — evaluate `tokio::sync::mpsc` replacement
- `sysinfo` pin 0.30 → current

---

## Test Delta

| Metric | Wave 128 | Wave 128b |
|--------|----------|-----------|
| Passed | 12,885 | 12,885 |
| Failed | 0 | 0 |
| Ignored | 420 | 420 |
| Workspace deps | 41 | 38 (−3 dead) |
| Largest .rs file | 795L | 275L (post-split) |
