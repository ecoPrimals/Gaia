# rhizoCrypt — Wave 120 Deep Debt Evolution

**Date:** Jun 20, 2026
**Commit:** `b3bdf89` (eastGate)
**Version:** v0.14.17

## Summary

Wave 120 focuses on three pillars: adapter-agnostic runtime messaging,
coverage expansion (77 new tests), and env-configurable operational tuning.

## Changes

### P0: Adapter-agnostic runtime messaging
- All runtime `RhizoCryptError::integration(...)` strings and tracing
  messages in songbird/ now use "discovery service/mesh" instead of
  "Songbird" — the module path provides adapter context.
- `toadstool_http.rs` runtime messages → capability-based ("compute
  provider", "BYOB compute server").
- `transport.rs` mesh relay error → "discovery routing".
- `safe_env/capability.rs` SONGBIRD_ADDRESS message clarifies "legacy".

### P1: Coverage expansion (1,748 → 1,825 tests)
- `method_gate.rs`: 27 new tests — all `parse_verify_ionic` error
  branches, `extract_scope_list` alternate keys, `expires_in_from_claims`,
  `CapabilityVerifier` sync path, `EnforcementMode::from_env` variants.
- `transport.rs`: 30 new tests — `try_parse_address`, `parse_address`,
  `Display`, serde roundtrip, `connect_transport` UDS/MeshRelay,
  `socket_is_alive`, `JsonRpcTransportError` Display/source.
- `neural_api.rs`: 6 new tests — `build_announce_request` pid=None,
  `parse_announce_response` NoResult, `send_jsonrpc_uds` failures.
- `safe_env`: 3 new tests — `get_duration_secs` parse/default/fallback.
- `TransportStream` now derives `Debug`.

### P2: Test isolation
- `discovery/manifest.rs`: 3 `temp_env` tests converted from
  `#[tokio::test] async fn` to `#[test] fn` — `manifest_dir()` is
  synchronous, removing env-var race under parallel test execution.

### P3: Env-configurable operational tuning
- New `SafeEnv::get_duration_secs` helper for reading env vars as Duration.
- 4 new env vars with compiled-in defaults:
  - `RHIZOCRYPT_MESH_POLL_INTERVAL_SECS` (default 30)
  - `RHIZOCRYPT_HEARTBEAT_INTERVAL_SECS` (default 45)
  - `RHIZOCRYPT_CB_FAILURE_THRESHOLD` (default 5)
  - `RHIZOCRYPT_CB_COOLDOWN_SECS` (default 30)
- `docs/ENV_VARS.md` updated with new section.

### P6: Documentation
- `histogram.rs`, `prometheus.rs`: Added `//!` module-level docs.

## Gate checks

| Gate | Status |
|------|--------|
| `cargo fmt` | pass |
| `cargo clippy` | pass (0 warnings) |
| `cargo doc` | pass (0 warnings) |
| `cargo deny` | pass |
| `cargo test` | pass (1,825 tests) |

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,825 |
| Files | 199 .rs |
| Lines | ~58,900 |
| Max file | 756 LOC |

## Remaining deferred items

- P1: Coverage push toward 90% on `method_gate.rs` (now ~82%, up from 70%)
- P3: Ed25519 `CapabilityVerifier` implementation (awaits JH-11)
- P3: axum 0.8, redb 4.x migration
