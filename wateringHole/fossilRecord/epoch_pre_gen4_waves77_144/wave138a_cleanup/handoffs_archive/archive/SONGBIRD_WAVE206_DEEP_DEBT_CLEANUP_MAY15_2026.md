# Songbird Wave 206 — Deep Debt Cleanup

**Date**: May 15, 2026  
**Wave**: 206  
**Audit Reference**: primalSpring Glacial Debt Escalation (May 13, 2026)  
**Category**: Deep debt resolution, smart refactors, bug fixes, production hardening

---

## Summary

Wave 206 resolves the last two files exceeding 800 lines, fixes two TURN server bugs, gates a test-only mock out of production, deprecates legacy socket names, and removes dead code. All quality gates pass: zero clippy warnings, zero test failures, cargo-deny clean.

---

## Smart Refactors

### `turn_server.rs` (898L → 679L)

Extracted shared TURN attribute parsing/construction into `crates/songbird-stun/src/turn_attrs.rs` (281L):

- `TurnAttrs::parse_peer_addr()`, `parse_lifetime()`, `parse_channel()`, `parse_data()` — attribute extraction
- `TurnAttrs::build_allocate_success()`, `build_lifetime_response()`, `build_channel_data()`, `build_data_indication()` — response builders
- `TurnAttrs::build_error_code()` — RFC 5389 §15.6 compliant ERROR-CODE attribute
- `rand_transaction_id()` — centralized helper
- 10 new unit tests

### `bin_interface/server.rs` (878L → 360L)

Extracted per-connection IPC protocol stack into `ipc_session.rs` (317L) and tests into `server_tests.rs` (151L):

- `dispatch_gated()` — unified bearer token extraction + method gate + handler dispatch
- Eliminates duplication between plaintext and encrypted dispatch paths
- `handle_connection`, `handle_json_rpc_lines`, `handle_encrypted_json_rpc`, `dispatch_json_rpc_line` now in `ipc_session`

---

## Bug Fixes

| Bug | Impact | Fix |
|-----|--------|-----|
| `handle_refresh` used `MessageType::RefreshSuccess` for auth failures | TURN auth bypass — unauthorized refresh would succeed | Changed to `MessageType::RefreshError` |
| `send_error()` discarded error code/reason | Clients received empty error responses | Now emits proper ERROR-CODE attribute via `TurnAttrs::build_error_code()` |

---

## Production Hardening

- **`NoopVerifier` gated `#[cfg(test)]`** — previously available in production builds; now only accessible in test code
- **Legacy socket constants deprecated** — `LEGACY_SECURITY_SOCKET_FILENAME`, `LEGACY_COMPUTE_SOCKET_FILENAME`, `LEGACY_AI_SOCKET_FILENAME` marked `#[deprecated(since = "0.2.1")]` with backward-compat `#[allow(deprecated)]` at 5 fallback sites
- **New TURN error types** — `MessageType::RefreshError`, `CreatePermissionError`, `ChannelBindError` added for correct error signaling

---

## Dead Code Removed

| Function | Crate | Reason |
|----------|-------|--------|
| `validate_security_provider_2fa` | songbird-orchestrator | Zero call sites |
| `integrate_plugins` | songbird-registry | Zero call sites |
| `check_system_health` | songbird-registry | Zero call sites |
| `calculate_metrics` | songbird-universal | Zero call sites |
| `is_allocated` | songbird-orchestrator | Zero call sites |

---

## Metrics After Wave 206

| Metric | Before | After |
|--------|--------|-------|
| Files >800 lines | 2 | **0** |
| Mocks in production | 1 (`NoopVerifier`) | **0** |
| Clippy warnings | 0 | 0 |
| Test failures | 0 | 0 |
| Build warnings | 0 | 0 |
| Workspace crates | 31 | 31 |

---

## Verification

```
cargo check --workspace          ✅ zero errors
cargo fmt --check                ✅ clean
cargo clippy --workspace -D warnings  ✅ zero warnings
cargo test --workspace           ✅ all pass
```

---

## Files Changed

```
crates/songbird-stun/src/turn_attrs.rs           (NEW, 281L)
crates/songbird-stun/src/turn_server.rs          (898L → 679L)
crates/songbird-stun/src/lib.rs                  (mod declaration)
crates/songbird-stun/src/message/types.rs        (3 new MessageType variants)
crates/songbird-orchestrator/src/bin_interface/ipc_session.rs  (NEW, 317L)
crates/songbird-orchestrator/src/bin_interface/server_tests.rs (NEW, 151L)
crates/songbird-orchestrator/src/bin_interface/server.rs       (878L → 360L)
crates/songbird-orchestrator/src/bin_interface/mod.rs          (mod declaration)
crates/songbird-orchestrator/src/ipc/pure_rust_server/method_gate/token.rs  (#[cfg(test)] gate)
crates/songbird-orchestrator/src/ipc/pure_rust_server/method_gate/mod.rs    (#[cfg(test)] re-export)
crates/songbird-orchestrator/src/access_control/auth.rs        (dead fn removed)
crates/songbird-orchestrator/src/service_registry.rs           (dead fn removed)
crates/songbird-universal/src/capabilities/adapter/mod.rs      (dead fn removed)
crates/songbird-registry/src/plugin/mod.rs                     (dead fns removed)
crates/songbird-types/src/defaults/paths.rs                    (#[deprecated] on legacy names)
crates/songbird-http-client/src/crypto/socket_discovery.rs     (#[allow(deprecated)])
crates/songbird-lineage-relay/src/security.rs                  (#[allow(deprecated)])
crates/songbird-universal-ipc/src/handlers/tor_handler.rs      (#[allow(deprecated)])
```

---

## What This Unblocks

- **primalSpring coverage target**: 0 files >800L means all coverage tooling works without thresholds
- **Downstream TURN consumers** (lithoSpore): Proper error codes enable correct retry logic
- **Security audit**: NoopVerifier cannot accidentally appear in release builds
- **Legacy migration**: Deprecated socket names produce compiler warnings to guide teams toward capability-based discovery
