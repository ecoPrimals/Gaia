# ToadStool Wave 155i — S346 Deep Debt Evolution Sprint

**Date**: July 29, 2026
**Gate**: strandGate (eastGate)
**Sprint**: S346
**Operator**: strandGate overwatch

---

## Summary

Comprehensive deep debt evolution sprint addressing 42 actionable items across
security, unsafe containment, stubs, lints, version alignment, and hardcoding.

## Changes

### Phase 1: P0 — Clippy Green + Security Honesty

- **Clippy blockers fixed**: Removed phantom `duration_suboptimal_units` lint
  from `Cargo.toml` (lint never existed in clippy). Fixed unused variable
  `sandbox` in macOS sandbox test.

- **Security fail-closed**: macOS and Windows sandbox `apply_sandbox`,
  `remove_sandbox`, `monitor_sandbox` now return `PlatformNotSupported` /
  `not_supported` errors instead of logging success without enforcement.
  `WindowsSandboxManager::start_execution`, `apply_security_policy`,
  `monitor_sandbox` also fail-closed.

- **PKI auth/authz fail-closed**: `authenticate()` and `authorize()` in
  `security_client/client.rs` no longer silently fall back to standalone mode.
  Now require `TOADSTOOL_STANDALONE=1` env var for standalone operation.
  Tests updated to explicitly set the env var.

- **Entropy hardened**: `build_system_entropy_fallback()` in
  `integration/security/src/discovery.rs` now uses `getrandom::getrandom()`
  (OS CSPRNG) instead of timestamp bytes. `getrandom` added as workspace dep.

### Phase 2: P1 — Silent Stubs + Unsafe Containment

- **BLE deploy stub evolved**: `bluetooth.rs` `deploy()` now returns
  `not_supported("BLE deploy requires edge transport")` instead of
  `Ok(String::new())`.

- **Migration verify evolved**: `verify_migration_success()` now returns
  `Err(NotImplemented)` instead of `Ok(false)`. Callers can no longer confuse
  "not implemented" with "verification ran and failed". Test updated.

- **Migration plan marked**: `create_migration_plan()` has explicit `Pending:`
  marker for future capability-based plan generation.

- **Unsafe containment — 4 migrations completed**:
  - `madvise_dontdump()` → `hw-safe::locked_memory` (secure_enclave now calls
    safe wrapper)
  - DRM ioctl → `hw-safe::drm_ioctl` module (hw-learn no longer has
    `#![allow(unsafe_code)]`)
  - systemd fd adoption (`from_raw_fd` + `remove_var`) → `hw-safe::systemd_fds`
    module. Server test `unsafe` blocks replaced with `temp_env`.
  - SPIR-V shader creation → `runtime/gpu::shader_spirv` safe wrapper.
    Server wgpu_dispatch calls safe API.

### Phase 3: P2 — Hardcoding, Versions, Docs

- **Magic numbers extracted**: Workload resource defaults (memory 512MB,
  storage 100/1000MB, network 100Mbps/50ms, GPU 1024MB) moved to `defaults`
  module. `DEFAULT_METRICS_PORT = 9090` added to `discovery_ports`.
  `cache_telemetry.rs` uses the constant.

- **Hardcoded path eliminated**: `glowplug_client::run_dir()` now delegates to
  `primal_sockets::get_runtime_dir()` instead of hardcoding `/run/toadstool`.

- **Version alignment**: 27 crates migrated from `version = "0.1.0"` to
  `version.workspace = true`. Total: 46 crates using workspace version.

- **75 rustdoc warnings fixed**: cylinder bit-field register notation escaped
  with backticks (38 warnings), unresolved links across 10 crates wrapped in
  backticks, redundant explicit link targets simplified, unclosed HTML tags
  escaped.

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo clippy --workspace --all-targets -- -D warnings` | 0 warnings |
| `cargo doc --workspace --no-deps` | 0 warnings |
| `cargo test --workspace --lib` | 9,193+ passed, 0 failed |
| `cargo fmt --check` | 0 diffs |
| `cargo deny check bans` | pass |

## Files Modified

**Cargo.toml (workspace)**: Removed `duration_suboptimal_units` lint, added
`getrandom` workspace dep.

**27 crate Cargo.toml files**: `version = "0.1.0"` → `version.workspace = true`

**Security**:
- `crates/security/sandbox/src/macos.rs` — fail-closed
- `crates/security/sandbox/src/windows.rs` — fail-closed
- `crates/integration/protocols/src/security_client/client.rs` — TOADSTOOL_STANDALONE gate
- `crates/integration/security/src/discovery.rs` — getrandom

**Unsafe containment (new files)**:
- `crates/core/hw-safe/src/drm_ioctl.rs`
- `crates/core/hw-safe/src/systemd_fds.rs`
- `crates/runtime/gpu/src/shader_spirv.rs`

**Stub evolution**:
- `crates/runtime/edge/src/discovery/bluetooth.rs`
- `crates/cli/src/universal/operations/migration.rs`

**Doc fixes**: ~40 files in cylinder, glowplug, hw-learn, toadstool, display,
distributed, runtime-gpu, runtime-specialty, server, cli.

## Notes for Upstream Teams

- **Tower**: No changes needed. ToadStool now requires `TOADSTOOL_STANDALONE=1`
  for standalone mode — Tower compositions are unaffected (PKI service available).
- **biomeOS**: Ensure `TOADSTOOL_STANDALONE=1` is set in unit files for
  deployments without Tower security service.
- **barraCuda / coralReef**: No impact. SPIR-V shader path unchanged; safe
  wrapper is internal.
