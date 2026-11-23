# nestGate Session 107 — Deep Debt Sweep (Wave 139a)

**Date**: Jul 14, 2026
**Wave**: 139a
**Head**: `2a6b2151`
**Posture**: Zero-debt continuation. No blocking tasks from Wave 139a (AlphaFold registration is BLOCKED on westGate hardware).

---

## Changes

### `String::from("literal")` → `.into()` sweep (3 rounds)

~425 conversions across 36 production files in 9 crates:

**Round 1** (12 files, ~125): nestgate-canonical, nestgate-bin, nestgate-config,
nestgate-core, nestgate-discovery, nestgate-installer, nestgate-zfs

**Round 2** (8 files, ~163): nestgate-api (ai_first_example 61, rpc_router 33,
native_async 32, remote 17), nestgate-rpc (federation_ops 3, content_stream 1),
nestgate-fsmonitor (security 14)

**Round 3** (10 files, ~137): nestgate-config (migrator 22, network_config 22,
handler_config 11), nestgate-discovery (introspection 13, network 8),
nestgate-zfs (capacity 13, reporting 20, compression 5), nestgate-api
(websocket 8, universal_storage_bridge 15)

Fixed `.into()` ambiguity in `impl Into<String>` contexts (4 sites in
UniversalZfsError::internal). Added Vec type annotations for inference.

### `Result<_, String>` → `Result<_, &'static str>`

8 functions converted:
- `validate_primal_sovereignty` (adapter_types.rs)
- `ZfsConfig::validate`, `StorageServiceConfig::validate` (config.rs)
- `validate_api_response`, `validate_unified_error_response`, `validate_success_response` (response/mod.rs)
- `get_current_metrics` (websocket.rs)
- `with_default_backend` (tarpc_server.rs)

3 promoted to `const fn`: `validate_api_response`, `validate_success_response`, `ZfsConfig::validate`

### thiserror + enum #[default]

- `ZfsError` (dev_stubs) → `thiserror::Error` derive
- `RequestPriority`, `LogLevel`, `Environment` → `#[default]` variant attribute
- Removed unused `ZeroCostDatasetInfoExtended` type + 8 redundant doc comments

### Hardcoded path → env override

- `/opt/nestgate` → `NESTGATE_INSTALL_PATH` env var (4 sites)

### Production mock audit

All stub/mock surfaces confirmed feature-gated:
- `http_client_stub.rs` → `#![cfg(feature = "dev-stubs")]`
- `orchestrator_registration.rs` → `#![cfg(any(feature = "dev-stubs", test))]`
- `dev_stubs/` → feature-gated modules

### Clone elimination

1 redundant `.clone()` removed (pool_operations.rs); 6 others verified necessary.

---

## Test Results

- **3,790 passed**, 1 failed (pre-existing `universal_storage_bridge_list_pools`), 73 ignored
- 0 clippy warnings
- No regressions across all 3 rounds

## Remaining Debt (from audit)

| Priority | Item | Status |
|----------|------|--------|
| P1 | NestGateError/ValidationError thiserror | Deferred (conditional Option Display) |
| P2 | Remaining `String::from` in production | Minimal (test-only remains dominant) |
| P3 | `map_err(format!)` → context helpers (~200 sites) | Deferred (individual analysis needed) |

## Wave 139a nestGate Status

- **AlphaFold CAS registration**: BLOCKED on westGate power-on
- **footPrint server**: Deployment concern (code is ready via FP-PERSIST)
- **No P1/P2 blockers**
