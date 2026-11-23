# groundSpring Wave 156b — Deep Debt Evolution

**Date**: Aug 3, 2026
**Gate**: westGate (Data NAS)
**Wave**: 156b
**Primal**: groundSpring
**Version**: V147
**Commit**: `8d789b4` (pushed to golgiBody)

---

## Summary

Full deep-debt evolution session on groundSpring. 5 large files (>600L) refactored into
coherent submodule trees, all self-knowledge violations resolved (primal names → role-based
IDs), production stubs completed, discovery caching added, idioms modernized, 54 new
integration/property tests added. Zero TODOs, zero clippy warnings, zero fmt diff.

## Deep Debt Completed

### Large File Refactoring (Phase 1)

All production files now under 600 lines. Smart splits into coherent submodules:

| File | Lines | Result |
|------|-------|--------|
| `pipeline.rs` | 647 | `pipeline/{types,planner,summary}.rs` |
| `atomic.rs` | 641 | `atomic/{types,tower,node,nest,nucleus}.rs` |
| `spectral_recon.rs` | 621 | `spectral_recon/{kernel,tikhonov,linalg,fft}.rs` |
| `esn/brain.rs` | 555 | + `esn/{uncertainty,concepts}.rs` |
| `niche.rs` | 539 | `niche/{mod,capabilities}.rs` |

### Self-Knowledge Evolution (Phase 2)

| Location | Before | After |
|----------|--------|-------|
| `dispatch/mod.rs` | `LEGACY_COMPUTE_PREFIX` | `LEGACY_NAMESPACE_PREFIX` |
| `certification/composition.rs` | `tower:beardog_alive` | `tower:security_alive` |
| `certification/composition.rs` | `tower:songbird_alive` | `tower:federation_alive` |
| `validation/s_gate_deployment.rs` | `gate:beardog-ipc` | `gate:security-ipc` |
| `validation/s_gate_deployment.rs` | `gate:barracuda-ipc` | `gate:gpu-math-ipc` |
| `biomeos/interaction.rs` docs | BearDog/toadStool | security/compute dispatch provider |
| `niche.rs` descriptions | skunkBat/Songbird | audit provider/discovery provider |

### Production Stubs (Phase 3)

- `dispatch_submit` takes owned `Value`, handles non-object params
- `prng-xoshiro-default` feature doc corrected
- Silent parse errors in health/interaction → `tracing::trace!`/`tracing::debug!`

### Zero-Copy + Caching (Phase 4)

- `discover_primals()` → 30s TTL cache via `OnceLock<Mutex<DiscoveryCache>>`
- `refresh_discovered_primals()` added for explicit invalidation
- Prior session: `probe_gpus()` returns `&'static [Substrate]`, nestgate `move` closures

### Idiom Modernization (Phase 7)

- `NdjsonSink` → `serde_json::json!()` (was manual format+escape)
- `wright_fisher_fixation_batch` → `Result<usize, InputError>` (was hiding errors)
- RPC server → JSON-RPC 2.0 strict (-32600 on bad method)

### Coverage Expansion (Phase 6)

| Test file | Tests | Coverage target |
|-----------|-------|-----------------|
| `certification_bonding.rs` | 5 | Bonding harness |
| `validation_scenarios.rs` | 6 | Scenario registry |
| `fao56_methods.rs` | 22 | Alternate ET₀ methods |
| `tissue_anderson_drug_scoring.rs` | 12 | Drug scoring properties |
| `wdm_methods.rs` | 9 | Extrapolation/ACF/block_size |

### Dependency Evaluation (Phase 5)

- `blake3` is transitive (primalSpring). barraCuda/bingoCube already `features = ["pure"]`.
- primalSpring needs `default-features = false` on blake3 to drop `cc` from build.

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Rust tests | 1,123 | 1,166 |
| Files >600L | 5 | 0 |
| Self-knowledge violations | ~12 | 0 |
| TODOs/FIXMEs | 0 | 0 |
| Clippy warnings | 0 | 0 |
| Production stubs | 3 | 0 |

## Status

- **CI**: All green (clippy + fmt + doc + tests)
- **Blocker**: biomeOS live deploy (ironGate must prove Phases 1–3 first)
- **Next**: Push to golgiBody → eastGate overwatch audit → Phase 4 westGate boot

## Upstream Notes (for overwatch)

- primalSpring: `blake3` dependency should set `default-features = false` (drops `cc`)
- primalSpring: 2 dead-code warnings (`aarch64_depot_path`, `chrono_lite_cutoff`)
- wateringHole: `GATE_SPRING_OWNERSHIP.md` still says eastGate owns groundSpring (stale)
- specs: `LAN_DEPLOYMENT_READINESS.md` lags at V145, `PAPER_EXTENSION_ROADMAP.md` says 6 deploy graphs (is 7)
