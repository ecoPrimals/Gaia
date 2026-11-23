# Squirrel Wave 129 — Mock Evolution + Timeout Threading + Dead Module Purge

**Date**: June 28, 2026
**Gate**: eastGate
**Agent**: overwatch
**Status**: GREEN — 6,809 tests passing, 0 failures, zero clippy warnings

---

## Changes

### Dead Module Purge (−1,810 lines)
- `chaos/mod.rs` (682 lines) — canned resilience simulation, zero callers. Deleted.
- `universal_provider.rs` + `universal_provider_tests.rs` (1,128 lines) — fake inference echo, zero callers. Deleted.

### Deprecated Item Deletion (6 items + 7 tests)
- `niche::DEPENDENCIES` — superseded by `REQUIRED_CAPABILITIES`
- `niche::required_dependency_count()` — alias of `required_capability_count()`
- `primal_names::SONGBIRD_SOCKET_NAME` — alias of `DISCOVERY_SOCKET_NAME`
- `TarpcClient::from_transport()` — use `connect()` with protocol negotiation
- `SecurityProviderConfig::security_provider()` — use capability-based discovery
- `DiscoveryOps::get_capabilities_for_primal()` — use `get_capabilities_for_service()`

### Production Mocks → Honest Behavior
- **self_healing**: `simulate_component_health_check()` (always `true`) → staleness-based `evaluate_component_health()`. `attempt_auto_recovery()` now resets to `Unknown` for re-evaluation.
- **universal_adapters**: `coordinate_computation/storage/ai_workflow` → `NotImplemented` error (was fabricated success JSON).
- **mDNS/DNS-SD**: `announce/register/unregister` → `MechanismFailed` error (was silent `Ok(())`).

### ServerConfig Timeout Threading
- `heartbeat_interval_secs` → `main.rs` biomeOS + discovery heartbeat loops
- `connection_timeout_secs` → `JsonRpcServer.connection_timeout` + UDS handler
- `inference_timeout_secs` → `SQUIRREL_INFERENCE_TIMEOUT_SECS` env override in `remote_inference.rs`

### Stale Lint Suppression
- Removed `#![expect(deprecated)]` from `universal/endpoints.rs` (module uses no deprecated items)

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 6,809 passing / 0 failures |
| Source | ~1,023 `.rs` files, ~321k lines |
| Net delta | +312 / −2,515 (−2,203 lines) |
| Clippy | 0 warnings |
| Formatting | Clean |

## Remaining Evolution Targets

- `action_registry.rs` — orphan stub awaiting Phase 6 wiring
- `EcosystemPrimalType` → capability strings migration (phased, widely used)
- Probe timeout constants (14 files) not yet threaded from `ServerConfig.probe_timeout_secs`
- `ecosystem/manager.rs` `find_services_by_capability` hardcodes `BiomeOS` primal type
- Universal adapter IPC transport — `NotImplemented` awaiting biomeOS composition

## Upstream Notes

No action required from upstream primals teams. Changes are squirrel-local.
Discovery stub evolution (mDNS/DNS-SD returning errors) is internal only — socket registry remains canonical for all LAN discovery.
