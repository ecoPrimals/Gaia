# biomeOS v3.94 — Wave 71: L4 Weighted Routing + Topology Affinity

**Owner**: southGate
**Date**: June 2, 2026
**FRAGO**: wave68-biomeos-l4-weighted-routing (P1 complete), wave69-southgate-mesh-routing-evolution (partial)
**Predecessor**: v3.93 (Wave 70b — taxonomy-first provider resolution)

## Mission Status

| Mission | Priority | Status |
|---------|----------|--------|
| L4 weighted routing | P1 | **COMPLETE** — all 4 discovery paths use `select_best()` |
| Topology affinity factor | P1 | **COMPLETE** — multiplier in `score()`, auto-inferred from transport |
| `--tcp-only` deprecation | P2 | **COMPLETE** — deprecated, blocked in release builds |

## Changes

### L4 Weighted Routing (5 files, ~60 new lines)

**Gap**: `discover_capability` always returned `providers[0]` — routing weights were
computed and recorded but never used for selection.

**Fix**: Added `NeuralRouter::select_primary()` which collects candidate primal names,
calls `RoutingWeightTable::select_best()` (EWMA latency × error rate × affinity ×
topology × circuit breaker), and returns the index of the highest-scoring provider.

Wired into:
- `discovery_registry.rs` — `try_registry_lookup`, `try_prefix_lookup`, `discover_by_capability_category`
- `discovery_composite.rs` — `find_primal_by_capability`
- `capability_call.rs` + `capability.rs` — `primary_name` now derived from `primary_endpoint` match

**A/B shadow logging**: First 1000 multi-provider dispatches log both weighted and
first-match choices at INFO level (`L4 shadow [n/1000]`). Counter is `AtomicU64` on
`NeuralRouter`.

### Topology Affinity (3 files, ~80 new lines)

**New field**: `ProviderWeight::topology_affinity: f64` — multiplier reflecting transport
proximity. Score formula: `topology_affinity * affinity * reliability * latency_factor - cost`.

**Constants** (`scoring::topology`):
| Tier | Value |
|------|-------|
| same_gate | 1.0 |
| same_segment | 0.9 |
| cross_segment | 0.7 |
| vps | 0.4 |
| wan | 0.3 |

**Auto-inference**: `topology_affinity_for_endpoint()` maps transport type to tier.
Called automatically during `register_capability()`.

**Reference**: `wateringHole/TOPOLOGY_MAP.toml` defines the canonical affinity table.

### --tcp-only Deprecation (2 files)

- CLI flag hidden (`hide = true`), doc string marks deprecated since v3.94
- Runtime deprecation warning via `tracing::warn!` at dispatch
- Release builds: `#[cfg(not(debug_assertions))]` guard bails with error
- Debug builds: accepted with warning (for testing)

## Verification

- `cargo check` — zero errors
- `cargo clippy` — zero warnings
- `cargo check --release` — zero errors (tcp-only block compiles)
- `cargo test --workspace` — all passing

## Downstream Impact

- **primalSpring observatory**: will detect weighted vs first-match behavior change via
  shadow log pattern `L4 shadow`
- **All primals**: no code changes needed — selection change is internal to Neural API
- **Topology**: existing Unix/Abstract socket providers score 1.0 (no regression);
  HTTP/TCP cross-gate providers now score lower (by design)
