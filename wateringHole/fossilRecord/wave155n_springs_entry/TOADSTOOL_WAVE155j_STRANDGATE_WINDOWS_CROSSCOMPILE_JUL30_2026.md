# ToadStool — Wave 155j Windows Cross-Compile Fix

**Date**: Jul 30, 2026 | **Session**: S347 | **Gate**: strandGate | **Priority**: P1
**Wave**: 155j | **Blocker Chain**: 3 (Windows Depot Freshness)

---

## Summary

Fixed the P1 blocker preventing `toadstool.exe` from building for Windows.
`cargo check -p toadstool-cli --target x86_64-pc-windows-msvc` now passes.

## Root Cause

`toadstool-server` declared `toadstool-runtime-gpu` as a Linux-only Cargo dependency
(`[target.'cfg(target_os = "linux")'.dependencies]`), but `wgpu_dispatch.rs` referenced
`toadstool_runtime_gpu::shader_spirv::create_spirv_shader_module` unconditionally whenever
the default `gpu-discovery` feature was enabled. This created an unresolved crate error on
Windows for any crate depending on `toadstool-server`, including `toadstool-cli` (the
binary crate that produces `toadstool.exe`).

## Fix

1. **Moved `toadstool-runtime-gpu`** from Linux-only deps to general `[dependencies]`
   as an optional dep tied to the `gpu-discovery` feature. The crate itself already
   cross-compiles cleanly (its Linux-only deps `hw-safe` and `nvpmu` are internally
   cfg-gated).

2. **Updated `RuntimeEngineDispatch::Gpu`** variant and all match arms in
   `runtime_engine_dispatch.rs` from `#[cfg(target_os = "linux")]` to
   `#[cfg(all(target_os = "linux", feature = "gpu-discovery"))]` — correctly reflecting
   that the GPU engine dispatch requires both Linux AND the GPU crate.

## Files Changed

| File | Change |
|------|--------|
| `crates/server/Cargo.toml` | GPU dep moved from linux-only to optional + `gpu-discovery` feature |
| `crates/server/src/runtime_engine_dispatch.rs` | 11 cfg gates: `target_os = "linux"` → `all(target_os = "linux", feature = "gpu-discovery")` |

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo check --target x86_64-pc-windows-msvc` | **PASS** (was FAIL) |
| `cargo clippy --workspace --all-targets -- -D warnings` | 0 warnings |
| `cargo test --workspace --lib` | **9,193 passed**, 0 failed |
| Linux build | Clean |

## Upstream Notes

### sporeGate (depot)
- `toadstool.exe` is now unblocked for Windows depot rebuild
- Remaining Windows depot blockers: `beardog.exe` (UnixStream), `coralreef.exe` (unix_jsonrpc)

### blueGate
- `toadstool.exe` can now be cross-compiled and deployed to blueGate for Node Atomic on Windows

### Latent Items (not blocking, future consideration)
- `wgpu_dispatch.rs` hardcodes `wgpu::Backends::VULKAN` — on Windows, DX12 backend may be preferred
- Workspace `wgpu` config disables `dx12` feature — would need enabling for native Windows GPU perf
- CLI `feature = "gpu"` uses `RuntimeEngineDispatch::Gpu` which is Linux-only; Windows GPU dispatch
  would route through `wgpu_dispatch` path (Vulkan/DX12) rather than VFIO

---

*Wave 155j P1 resolved. toadstool.exe Windows depot unblocked. 2 of 3 Chain 3 blockers remain (bearDog, coralReef).*
