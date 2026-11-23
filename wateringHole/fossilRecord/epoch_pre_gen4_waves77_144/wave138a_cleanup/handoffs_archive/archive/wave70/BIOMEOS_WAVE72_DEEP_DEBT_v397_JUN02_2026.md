# biomeOS — Wave 72+ Deep Debt Cleanup (v3.94 → v3.97)

**Date**: 2026-06-02
**Author**: southGate (biomeOS)
**Waves**: 71–72+ (v3.94 → v3.97)
**Status**: Delivered — ready for primalSpring audit

---

## Executive Summary

Four waves of deep debt cleanup since L4 weighted routing went live (v3.94).
Focus: idiomatic Rust error handling, file size reduction via test extraction,
deprecated transport removal, and environment safety hardening.

---

## v3.94 → v3.95: L4 Shadow Analysis + PathwayLearner

- A/B shadow analysis: disagreement counter + milestone summaries at 100/500/1000 dispatches
- `neural_api.weight_health` RPC exposes shadow routing stats
- PathwayLearner: per-node graph execution timing feeds routing weights
- Perceptron shadow mode prep: NeuralRouter consumes perceptron recommendations alongside rule-based
- Cross-gate mesh partner: biomeOS endpoints verified for eastGate mesh validation

## v3.95 → v3.96: Env SSOT + Context Evolution + Test Extraction Wave 1

- **Env SSOT**: 14 new constants in `env_config::vars`, 44 production `env::var()` calls wired across 22 files
- **map_err → .context()**: 56 call sites evolved (metrics/mod.rs: 35, genome.rs: 6, endpoint_probe: 7, atomic_transport: 3, discovery_bootstrap: 3, connection: 2)
- **Test extraction wave 1**: 5 files (security_client, verification, beacon_verification, config/mod, orchestrator/mod)
- **#[allow] → #[expect]**: 100% migrated
- **Primal-name hardcoding**: `resolve_name_fallback()` helper surfaces taxonomy gaps

## v3.96 → v3.97: map_err Sweep + Test Extraction Wave 2 + HTTP Removal

- **map_err sweep**: 27 of 28 remaining sites converted across 18 files. 5 residuals are legitimate (`Result<_, String>` types)
- **Test extraction wave 2**: 7 files — identifiers.rs (748→483), incubation/mod.rs (715→325), manifest.rs (771→392), unix_server.rs (743→373), nucleus/mod.rs (744→401), continuous.rs (712→280), device_management (707→317)
- **HTTP transport removed**: `primal_impls.rs` no longer creates HTTP endpoints; `http_port` config logs warning
- **Env safety**: empty `USER` in genomebin-v3/runtime.rs logs warning instead of silent empty path

---

## Metrics

| Metric | Before (v3.94) | After (v3.97) |
|--------|----------------|---------------|
| `map_err(anyhow!)` sites | ~85 | 5 (all legitimate) |
| Files with >700L tests inline | 12+ | 0 |
| Test files extracted | 1 | 12 |
| HTTP transport | Active (deprecated) | Removed |
| env::var() with string literals | 44+ | 0 in wired crates |
| #[allow] lint suppressions | 1 | 0 |
| Production unsafe blocks | 0 | 0 |
| Workspace tests | 595+ pass, 0 fail | 595+ pass, 0 fail |

---

## For primalSpring Audit

### Review items
1. **Weighted routing shadow data**: A/B shadow logging is active (first 1000 dispatches). Monitor `L4 shadow [n/1000]` in INFO logs for divergence rate.
2. **HTTP removal impact**: Any downstream consumers expecting HTTP endpoints from biomeOS should migrate to Unix socket or mesh dispatch.
3. **Test extraction pattern**: All 12 extractions use `#[cfg(test)] #[path = "..."] mod tests;` — verify this pattern is canonical across ecosystem.

### Upstream gaps identified
- `GeneticsTier::parse()` returns `Result<_, String>` — should evolve to `thiserror` enum
- `EscalationManager::{escalate,fallback}_connection` returns `Result<_, String>` — same
- SSE streaming in biomeos-ui blocked on Songbird exposing streaming endpoints
- CI workflow runs `--lib` only — integration and bin tests not exercised

### Documentation updated
- CHANGELOG.md, CURRENT_STATUS.md, README.md, CONTEXT.md, START_HERE.md, DOCUMENTATION.md
- specs/README.md: +2 missing specs indexed (BIOMEOS_NUCLEUS_EVOLUTION, CAPABILITY_CALL_ROUTING_CONTRACT)
- sporeprint/validation-summary.md: refreshed to v3.97
- Cargo.toml: removed stale cosmetic comments, removed commented-out dep

---

## Next Wave Targets

1. **Remaining large files**: `sovereignty_guardian.rs` (716L), `capability_taxonomy/definition.rs` (715L), `btsp_client.rs` (721L) — production code, not test-heavy
2. **String error types**: Evolve `GeneticsTier::parse()` and `EscalationManager` to `thiserror`
3. **CI scope**: Expand workflow to include `--all-targets`
4. **Perceptron L5**: When barraCuda `ml.mlp_train` is wired, activate perceptron shadow mode
