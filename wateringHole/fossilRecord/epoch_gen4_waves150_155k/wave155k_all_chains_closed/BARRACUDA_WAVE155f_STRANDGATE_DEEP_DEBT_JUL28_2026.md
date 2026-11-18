# barraCuda Wave 155f — strandGate Deep Debt Sweep + Bug Fixes

**Date**: Jul 28, 2026 | **Gate**: strandGate | **Wave**: 155f
**Team**: barraCuda code team

---

## Summary

Deep debt sweep + dependency evolution + 4 bug fixes on strandGate.
All 4,957 workspace tests pass. Zero SIGSEGV. Zero failures. All quality gates green.

---

## Bugs Fixed

### 1. SIGSEGV in barracuda-core tests (process teardown crash)

**Root cause**: Multiple `BarraCudaPrimal::start()` calls from parallel test threads each
created independent wgpu devices via `Auto::new()`. Mesa's llvmpipe crashed during
concurrent device destruction at process exit.

**Fix**: Crate-level `GPU_TEST_GUARD` (`tokio::sync::Mutex` in `test_util`) serializes
all GPU-touching tests. `start_primal_guarded()` returns primal + mutex guard so only one
wgpu device exists at a time. Previously 2/3 runs crashed; now 5/5 clean.

**Files**: `lib.rs`, `rpc_tests.rs`, `math_stats_tests.rs`

### 2. ESN BindGroupLayout crash (`test_esn_timeseries_integration`)

**Root cause**: `TimeSeriesAnalyzer::build()` called `ESN::new()` which created its own
wgpu device via `Auto::new_wgpu()`, even though the analyzer already held a device reference.
Under llvmpipe, two wgpu devices sharing the same internal ID space caused resource handle
collisions: `BindGroupLayout[Id(0,1)] does not exist`.

**Fix**: Changed `timeseries.rs` to `ESN::with_device(config, Arc::new(self.device.clone()))`.
`test_concurrent_apis` fixed to pass pool device directly into `ESN::with_device()`.

**Files**: `timeseries.rs`, `api_integration_tests.rs`

### 3. BTSP socket compliance env var races

**Root cause**: Tests in `btsp_socket_compliance.rs` used `unsafe { std::env::set_var() }`
to manipulate global environment variables. Under `cargo test` (shared process, parallel
threads), concurrent tests clobbered each other's env vars.

**Fix**: `ENV_MUTEX` (`std::sync::Mutex`) in each integration test binary. `clear_family_env()`
returns `MutexGuard` held for full test scope. Applied to `btsp_socket_compliance.rs`,
`no_gpu_probe.rs`, `btsp_discovery.rs`, `transport_config.rs`.

### 4. KernelTarget::Sovereign doctest

**Root cause**: `Sovereign` variant added to `KernelTarget` enum but doc example `match`
never updated. **Fix**: Added `KernelTarget::Sovereign { .. } => {}` arm.

---

## Deep Debt Evolution

- **BatchError → thiserror** — last manual error type in codebase eliminated
- **BTSP_STRICT_MODE** — new env key constant; `BEARDOG_UDS_REQUIRE_BTSP` deprecated with
  graceful fallback + warning
- **LOCALHOST consolidation** — `DEFAULT_LOOPBACK` single source of truth
- **wgpu backend target-gating** — Linux builds no longer compile metal/dx12 backends
- **env_keys** — all test code evolved from raw string literals to `env_keys::` constants

---

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo check --workspace` | PASS |
| `cargo fmt --check` | PASS |
| `cargo clippy --workspace --all-targets --all-features` | PASS (zero warnings) |
| `cargo test --workspace` | 4,957 passed, 0 failed, 205 ignored |
| `cargo doc --workspace --no-deps` | PASS |
| SIGSEGV | ZERO |
| Production `unwrap()` | ZERO |
| Production `unsafe` | 1 (justified, barracuda-spirv passthrough) |
| Files > 800L | ZERO |

---

## For Upstream Review

- **No gaps found** for upstream primals teams — all identified debt items resolved
- Test infrastructure now correctly serializes GPU device lifecycle and env var mutation
- `TimeSeriesAnalyzer` device sharing fix may affect any consumer that calls
  `TimeSeriesAnalyzer::build()` — behavior is now correct (single device, no crash)
- The `test-tiered.sh` script in `scripts/` remains valid and functional

---

## Files Changed (22 files, +260 −143)

- `crates/barracuda-core/src/lib.rs` — `test_util` module + GPU test guard
- `crates/barracuda-core/src/rpc_tests.rs` — GPU guard for readiness test
- `crates/barracuda-core/src/ipc/methods_coverage_tests/math_stats_tests.rs` — GPU guard
- `crates/barracuda-core/tests/btsp_socket_compliance.rs` — ENV_MUTEX serialization
- `crates/barracuda-core/tests/no_gpu_probe.rs` — ENV_MUTEX serialization
- `crates/barracuda-core/tests/btsp_discovery.rs` — ENV_MUTEX serialization
- `crates/barracuda-core/tests/transport_config.rs` — ENV_MUTEX serialization
- `crates/barracuda/src/timeseries.rs` — `ESN::with_device()` instead of `ESN::new()`
- `crates/barracuda/tests/api_integration_tests.rs` — pool device sharing
- `crates/barracuda/src/device/kernel_router.rs` — Sovereign doctest arm
- `crates/barracuda-core/src/ipc/methods/batch.rs` — thiserror evolution
- `crates/barracuda-core/src/env_keys.rs` — BTSP_STRICT_MODE
- `crates/barracuda-core/src/ipc/btsp_client.rs` — BTSP_STRICT_MODE usage
- `crates/barracuda-core/src/ipc/btsp_tests.rs` — env_keys constants
- `crates/barracuda-core/src/ipc/transport_config.rs` — DEFAULT_LOOPBACK
- `crates/barracuda/src/env_keys.rs` — DEFAULT_LOOPBACK constant
- `crates/barracuda/src/device/coral_compiler/discovery.rs` — LOCALHOST consolidation
- `crates/barracuda/Cargo.toml` — target-gated wgpu backends
- `crates/barracuda-spirv/Cargo.toml` — target-gated wgpu backends
- `Cargo.toml` — workspace wgpu base features only
- `WHATS_NEXT.md` — Wave 155f entry
- `README.md` — updated counts and recent section
