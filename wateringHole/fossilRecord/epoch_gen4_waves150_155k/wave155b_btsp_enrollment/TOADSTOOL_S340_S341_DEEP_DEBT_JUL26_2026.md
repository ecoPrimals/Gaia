# ToadStool S340–S341 Deep Debt Resolution

**Date**: Jul 26, 2026 | **Wave**: 151a | **Primal**: toadStool | **Gate**: eastGate

## Summary

Two sessions of deep debt resolution: stale reference cleanup, dead legacy type
removal, and hardcoded production stub evolution to provider-queried APIs.

## S340 — Stale Refs + Dead Legacy Types

- Cross-references to deleted `PRIMAL_CAPABILITY_SYSTEM.md` updated to
  `CAPABILITY_BASED_DISCOVERY_STANDARD.md` (wateringHole) in 5 spec files + DEBT.md
- `DISPATCH_WIRE_CONTRACT.md` added to `specs/README.md`
- Dead `ConnectionStatus` variants (`_Connecting`, `_Disconnected`, `_Error`) and
  `_auth_token` field removed from legacy `ServiceConnection`
- `cargo fmt` normalization after S339 bulk `sed` replacements

## S341 — Hardcoded Economics & Silent Fallback Elimination

### Migration Planner Evolution (Class C → Class B)

`evaluate_migration_targets` previously returned fabricated data: hardcoded `$5/hr`,
`us-west-1`, and fixed `CostImpact` values without ever calling registered
`CloudProvider`s. Now queries:
- `provider.capabilities()` to find GPU-capable providers
- `provider.estimate_cost()` for real per-region pricing
- Selects cheapest GPU-capable provider/region combination
- Reports actual costs with degraded confidence when data unavailable

### Security Discovery — Silent Fallback Elimination

Two `unwrap_or_else(|_| 127.0.0.1:8081)` sites in mDNS and coordination discovery
silently fabricated loopback endpoints on URL parse failure. Replaced with
`tracing::warn` logging + empty result. Callers handle empty discovery via
`get_best_endpoint()` typed error.

### Storage Config — Centralized Port

`StorageConfig::default()` magic `8082` → `discovery_ports::DEFAULT_STORAGE_PORT`.

### Mock/Stub Audit

Comprehensive audit of 10 production stub files:
- **5 Class A** (test-gated): security mock, dispatch mock, mock primal, policy
  test substrate, inline test providers
- **4 Class B** (evolved sentinels): unix client stub, glowplug client stub,
  stub runtime engine, noop cloud/crypto providers
- **1 Class C** (resolved): migration planner hardcoded economics → provider API queries

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo clippy --workspace --all-targets -- -D warnings` | **CLEAN** (Rust 1.96) |
| `cargo fmt --all -- --check` | **0 diffs** |
| `cargo test --workspace --lib` | **9,232 tests, 0 failures** |
| Largest production file | **713L** (target <750L) |
| Production TODO/FIXME/HACK | **0** |
| Production mocks (Class C) | **0** (all evolved) |

## Upstream Notes

- **BTSP standard**: toadStool marked SKIP for Wave 151a BTSP evolution — no
  protocol work required this wave.
- **`#[ignore]` tests**: 60+ ignored tests all properly documented with
  hardware/infrastructure reasons (Akida hardware, GPU drivers, root privileges,
  built binary requirements, live cluster needs).
- **`#[expect(deprecated)]`**: All 9 sites are legitimate migration shims for
  backward-compat env vars and legacy `EcosystemService` layer.
