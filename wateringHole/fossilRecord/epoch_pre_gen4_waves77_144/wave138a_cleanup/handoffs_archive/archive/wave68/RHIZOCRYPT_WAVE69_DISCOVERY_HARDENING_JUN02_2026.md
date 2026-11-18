# rhizoCrypt — Wave 69 Discovery Fallback Hardening

**Date**: 2026-06-02
**Primal**: rhizoCrypt
**Version**: 0.14.1
**Gate**: strandGate

## Summary

Wave 69 mission items completed: lazy discovery fallback hardened with tests,
split handler test modules expanded with edge cases, sled→redb audit confirmed
clean. Wave 68 FRAGO acked.

## Changes

### P2: Eager Peer Population Fallback Hardening

Three new discovery registry tests verify the full fallback chain:

- **`test_lazy_fallback_after_eager_population_failure`**: Simulates `populate_registry()` failure at startup, then verifies `discover()` resolves lazily via `query_discovery_source`. Confirms cache persists after source is cleared.
- **`test_standalone_mode_no_source_no_population`**: Pure standalone — no discovery source, no eager population. All capabilities return `Unavailable`.
- **`test_lazy_source_unreachable_returns_failed`**: Unreachable source returns `DiscoveryStatus::Failed`, not panic.

### P2: sled→redb Audit

**Result: No action required.** rhizoCrypt completed sled→redb migration at session s20 (~March 2026). Current state:
- Zero sled references in active code, deps, or lockfile
- redb 2.6.3 sole persistent backend (feature-gated, default on)
- `DagStore` trait + `DagBackend` enum provides clean migration model for downstream primals
- `zstd-sys` banned in `deny.toml` (former sled transitive dep)
- Songbird+BearDog sled→redb migration owned by southGate

### P3: Handler Test Edge Cases (+8 tests)

- **Dehydrate**: `test_partial_dehydrate_missing_session_id`, `test_partial_dehydrate_nonexistent_session`, `test_partial_dehydrate_idempotent`
- **Gates**: `test_readiness_gate_allows_health_prefix_when_not_running`, `test_readiness_gate_allows_exact_public_methods_when_not_running`

## FRAGO Acknowledgments

| FRAGO | Status | Notes |
|-------|--------|-------|
| `wave68-dependency-evolution-coordination` | **ACKED** | Item 1 (sled→redb): rhizoCrypt is clean, no action. southGate owns Songbird+BearDog. Item 2 (ring/sqlx): eastGate. Items 3-4: informational. |
| `wave69-strandgate-provenance-deployment` | **IN PROGRESS** | Provenance trio wiring complete on rhizoCrypt side. Blocked on sweetGrass v0.8.0 + mesh validation. |

## Stadial Gate

| Metric | Value |
|--------|-------|
| Tests | 1,663 passing (all features) |
| Clippy | 0 warnings |
| Source files | 180 `.rs` |
| Max production file | 686 lines (`service.rs`) |
| unsafe blocks | 0 |

## Upstream Gaps for Primal Teams

| Blocker | Owner | Status |
|---------|-------|--------|
| Songbird+BearDog sled→redb | southGate | Tracked in `wave68-dependency-evolution-coordination` |
| Songbird `ipc.watch` + `discovery.peers` | southGate | Awaiting mesh validation |
| bearDog BTSP S4 auth config | southGate | Blocking `PresenceVerifier` evolution |
| sweetGrass v0.8.0 `provenance.create_braid` | strandGate (local) | Braid integration stays no-op |
| biomeOS `compute.dispatch` | biomeGate | Cross-gate compute dispatch unimplemented |
