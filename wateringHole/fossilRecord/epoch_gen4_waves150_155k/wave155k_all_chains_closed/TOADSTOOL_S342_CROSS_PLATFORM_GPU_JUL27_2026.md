# ToadStool S342–S343 — Cross-Platform GPU Pipeline

**Date**: Jul 27, 2026 | **Sessions**: S342–S343 | **Wave**: 155b

## Summary

S342: Wired wgpu adapter enumeration into the self-knowledge pipeline as
cross-platform GPU fallback. Fixed doctor false positives and documented
unsafe MMIO operations.

S343: Extended wgpu coverage to all GPU system query functions and dispatch
capabilities. Every GPU detection path now has a cross-platform fallback.

## Changes

### Cross-Platform GPU Discovery (capabilities/gpu.rs)

`query_gpu_devices()` now falls back to `wgpu::Instance::enumerate_adapters()`
when platform-native detection finds no GPUs:
- Linux: sysfs/DRM + `/proc/driver/nvidia` (unchanged)
- macOS: System Profiler (unchanged)
- **All platforms (new)**: wgpu adapter enumeration — DX12, Vulkan, Metal

CPU-type wgpu adapters are filtered out. Vendor ID → label mapping covers
NVIDIA (0x10DE), AMD (0x1002), Intel (0x8086), Apple (0x106B),
Microsoft (0x1414), Qualcomm (0x5143).

### Doctor GPU Check Fix (doctor/checks.rs)

`check_gpu_available()` no longer returns `true` unconditionally on
non-Linux. Platform-specific checks:
- Windows: `vulkan-1.dll` or `d3d12.dll` in System32
- macOS: Metal.framework
- Other: returns `false`

### Unsafe SAFETY Documentation

5 MMIO operations in `rm_trigger/main.rs` quench loop and
`nv/registers/pmc.rs` given individual `// SAFETY:` comments
(previously covered by a group comment).

### Lint Attribute Evolution

2 production `#[allow]` without `reason` → `#[expect]` with reasons:
- `sandbox/manager.rs`: `used_underscore_binding` (reserved param)
- `connection/unix.rs`: `needless_pass_by_value` (consumed into response)

## Quality Gates

- 9,232 lib tests, 0 failures
- Zero clippy warnings (`-D warnings` on Rust 1.96)
- Zero fmt diff

## S343 — GPU System Queries + Dispatch Capabilities

### gpu_system.rs Evolutions

- **`query_gpu_devices()`**: Static `"wgpu-default"` placeholder replaced
  with real `wgpu::Instance::enumerate_adapters()`. Reports name, vendor ID,
  device ID, backend, device type, driver for each adapter.
- **`query_gpu_memory()`**: `nvidia-smi` invocation ungated — works on
  Windows when NVIDIA drivers installed. No longer Linux-only.
- **`query_available_backends()`**: Windows checks `d3d12.dll`/`vulkan-1.dll`;
  macOS checks `Metal.framework`. No longer hardcoded.

### dispatch/capabilities.rs Evolution

When `sysmon::discover_gpus()` returns empty (non-Linux), falls back to
wgpu adapter enumeration. New `wgpu_gpus` array in JSON-RPC response.
`dispatch_modes` dynamically computed: `["vfio"]` / `["drm"]` / `["wgpu"]`
/ `["cpu"]` based on what's actually detected.

## Cross-Platform Gap Analysis (after S343)

| Layer | Cross-platform? |
|-------|-----------------|
| capabilities/gpu.rs | **Yes** (wgpu fallback, S342) |
| gpu_system queries | **Yes** (wgpu + nvidia-smi, S343) |
| dispatch/capabilities | **Yes** (wgpu fallback, S343) |
| sysmon::discover_gpus | Linux-only (by design — reads procfs/sysfs) |
| dispatch routing/state | Linux-only (VFIO/DRM kernel APIs) |
| doctor check_gpu_available | **Yes** (fixed S342) |
| resource_validator | **Yes** (wgpu probe with timeout) |

Next: WMI `Win32_VideoController` for VRAM enrichment when blueGate
validates (requires live Windows hardware testing).
