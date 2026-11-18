# rhizoCrypt — Wave 133e Handoff

**Date**: Jul 7, 2026 | **Commit**: `edd950c` | **From**: eastGate overwatch

## Changes

### P0: Server Startup Readiness Bug Fix

- `serve_with_tcp`: replaced `yield_now()` spin-loop polling `is_running` flag with direct `server.ready_notifier().notified().await`. Eliminates race where `Notify::notify_waiters()` fires before readiness task registers its waiter.
- `server.rs`: changed `notify_waiters()` → `notify_one()` which stores a permit if no waiter exists, preventing the lost-signal race entirely.
- Both `test_run_server_host_override_enables_tcp` and `test_run_server_tcp_via_jsonrpc_port_env` now pass reliably (previously timed out in 10s under load).

### Test File Splits (>800L → under limit)

- `method_gate_tests.rs` (1,023L) → core tests (746L) + `method_gate_tests_provider.rs` (298L)
- `lib_tests_startup.rs` (1,003L) → startup config (636L) + `lib_tests_lifecycle.rs` (387L)

### Mock Isolation

- `CapabilityClientFactory::with_mocks()` gated behind `#[cfg(any(test, feature = "test-utils"))]` — removed from production API surface.

### Doc SSOT Sweep

- 9 files updated with current dates (Jun 28 → Jul 7)
- CHANGELOG: Wave 128 + 128c entries added
- Metrics: 1,869 tests, 206 `.rs` files, ~61,071 lines

## Gate Checks

- `cargo fmt`: clean
- `cargo clippy` (pedantic+nursery): 0 warnings
- `cargo doc` (-D warnings): 0 warnings
- `cargo test` (--all-features): 1,869 passing, 0 failures
- Zero unsafe, zero TODOs/FIXMEs
