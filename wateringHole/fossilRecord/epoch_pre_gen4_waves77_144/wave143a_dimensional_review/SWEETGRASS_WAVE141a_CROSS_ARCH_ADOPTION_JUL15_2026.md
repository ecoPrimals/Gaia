# sweetGrass — Cross-Architecture Adoption (Wave 141a)

**Date**: Jul 15, 2026
**Commit**: `d4f7da9` on `main`
**Status**: COMPLETE
**Target**: `cargo check --target x86_64-pc-windows-gnu` succeeds

## Summary

All UDS transport code gated behind `#[cfg(unix)]` following the songBird
reference pattern. TCP remains as the cross-platform transport path.
`PRIMAL_BIND_MODE=tcp_only` enables full operation on non-Unix platforms.

## Files Modified (10 files)

| Crate | File | Change |
|-------|------|--------|
| `sweet-grass-service` | `src/transport_connect.rs` | `TransportStream::Uds` + connect arm gated |
| `sweet-grass-service` | `src/neural_announce.rs` | `send_jsonrpc_uds`, `announce_to_neural_api`, helpers gated |
| `sweet-grass-service` | `src/handlers/health/mod.rs` | `probe_integration`, `try_liveness_probe` gated |
| `sweet-grass-service` | `src/handlers/jsonrpc/composition.rs` | `probe_capability_in_dir`, `try_liveness_probe` gated |
| `sweet-grass-service` | `src/tcp_jsonrpc.rs` | `debug` import gated (only used in `#[cfg(unix)]` fns) |
| `sweet-grass-service` | `src/bin/service.rs` | `socket` field annotated for non-unix |
| `sweet-grass-service` | `tests/btsp_mock_beardog.rs` | `#![cfg(unix)]` crate-level gate |
| `sweet-grass-store-nestgate` | `src/client.rs` | `NestGateClient::call` returns `ConnectionFailed` on non-unix |
| `sweet-grass-store-nestgate` | `src/store.rs` | Test module gated `#[cfg(all(test, unix))]` |

## Pattern Applied

- `#[cfg(unix)]` on UDS-only production functions
- `#[cfg(not(unix))]` fallback returns `Unsupported` or `"unavailable"`
- Test modules using UDS mocks gated with `#[cfg(all(test, unix))]` or `#![cfg(unix)]`
- No Windows implementation yet — just compilation gates
- TCP path is fully cross-platform (no changes needed)

## Previously Gated (no changes needed)

These modules were already `#[cfg(unix)]` in `lib.rs`:
- `pub mod btsp;`
- `pub mod crypto_delegate;`
- `pub mod uds;`

## Verification

- `cargo check --target x86_64-pc-windows-gnu` — PASS (0 errors)
- `cargo clippy --all-features --all-targets -- -D warnings` — PASS (0 warnings)
- `cargo test --all-features` — 1,604 tests, 0 failures
- No version bump (patch-level mechanical change)

## Notes for Overwatch

- 6 pre-existing warnings remain on Windows target (unused `mut`, unused variable)
  — these are cross-platform logic debt, not platform-gate issues
- `sweet-grass-store-nestgate` crate is fundamentally UDS-only; if Windows
  support is needed, a TCP-based NestGate client variant would be required
- `TransportEndpoint::Uds` variant still exists in `sweet-grass-core` (the enum
  is cross-platform); the _connection_ is gated, not the type
