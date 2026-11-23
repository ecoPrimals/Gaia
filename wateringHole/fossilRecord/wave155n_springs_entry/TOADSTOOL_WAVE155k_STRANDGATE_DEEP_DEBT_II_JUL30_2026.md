# ToadStool — Wave 155k Deep Debt Evolution II

**Date**: Jul 30, 2026 | **Sessions**: S348–S349 | **Gate**: strandGate
**Wave**: 155k | **42 files changed**, +215 / −246

---

## Summary

Comprehensive deep debt sprint driven by 5-axis audit (file size, dependencies,
hardcoding, mocks/stubs, unsafe containment). All code chains closed per Wave 155k;
this sprint addressed P2 divergences and systemic debt.

## Changes

### 1. Dead Dependency Removal (~15 declarations)

| Dependency | Removed From |
|------------|-------------|
| `parking_lot` | runtime/gpu |
| `serde_yaml_ng` | integration/primals, management/performance, runtime/container, runtime/gpu, runtime/wasm, testing |
| `config` (crates.io) | distributed, management/analytics |
| `regex` | auto_config, runtime/specialty |
| `ndarray` | management/analytics, management/performance |
| `statrs` | management/performance |
| `futures-intrusive` | runtime/universal |

Also: `serde_yaml_ng` moved from `[dependencies]` to `[dev-dependencies]` in core/config.
`pub use serde_yaml_ng` removed from testing/src/lib.rs.

### 2. Unsafe Lint Compliance (S211 standard)

5 cylinder `#[allow(unsafe_code)]` attributes given `reason = "..."`:
- `src/lib.rs`, `bin/rm_trigger/main.rs`, `bin/capture_pmu_falcon.rs`,
  `bin/sovereign_pmu_boot.rs`, `bin/sovereign_acr_boot.rs`

### 3. Silent Stubs → Fail-Closed

| Stub | Was | Now |
|------|-----|-----|
| Terminal3270::connect/disconnect | `Ok(())` (fake success) | `Err(not_supported)` |
| IBM get_system_info | Hardcoded z14 specs | `Err(not_supported)` |
| Non-Unix probe_unix_socket | `Ok(())` (health check passes) | `Err(not_supported)` |
| InMemoryBackend export | Always compiled | `#[cfg(any(test, feature = "test-mocks"))]` |
| Akida state_extraction | `Ok` with fake layer | `Err(InvalidState)` |

### 4. Hardcoding Consolidation

| Pattern | Before | After |
|---------|--------|-------|
| `/run/user/{uid}` | 4 duplicate implementations | Single `get_runtime_dir()` call |
| BYOB web ports | Module-local 8443/3000/8000/9000 | `constants/byob_defaults.rs` |
| Container port ranges | Inline 8000-8999/3000-3999 | `container/src/constants.rs` |
| Alert thresholds | Magic 300/600/60/1800 | Named constants in `alerting.rs` |
| Daemon config | Magic 1024/1000/3600/30/10 | Named constants in `config.rs` |

### 5. Legacy Symlink Fix (S348)

`toadstool.sock` symlink was pointing at `compute-tarpc.sock` (tarpc binary protocol)
instead of `compute.sock` (JSON-RPC primary). Root cause of westGate P2 "tarpc-only".

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --check` | 0 diffs |
| `cargo clippy --workspace --all-targets -D warnings` | 0 warnings |
| `cargo test --workspace --lib` | **9,193 passed**, 0 failed, 20 ignored |
| `cargo check --target x86_64-pc-windows-msvc` | PASS |

## Audit Findings (for tracking — not addressed this sprint)

### Dependencies (future consideration)
- `wasmi_wasi` → pulls `anyhow` transitively; evolve to pure-Rust WASI stubs
- `bollard`/`axum` in container BYOB path; evolve to Unix JSON-RPC
- `rayon` actively used — keep (pure Rust, parallel CPU kernels)

### Unsafe (future consolidation)
- Cylinder carries 85/134 unsafe blocks — many duplicate patterns in hw-safe
- `cylinder/vfio/dma.rs` (11 blocks) → candidate for `hw-safe::LockedMemory`
- `cylinder/vfio/ioctl.rs` (19 blocks) → candidate for `hw-safe::vfio_setup`

### Hardcoding (remaining P3)
- `/var/lib/toadstool`, sandbox log dir, udev rule paths → consolidate to platform_paths
- CLI template ports (Postgres 5432, TensorBoard 6006) → parameterize
- `/etc/biomeos/discovery.json` fallback → platform_paths constant

---

*Wave 155k deep debt sprint complete. 42 files, ~15 dead deps purged, 5 stubs
evolved, 4 hardcoding patterns consolidated. All quality gates green.*
