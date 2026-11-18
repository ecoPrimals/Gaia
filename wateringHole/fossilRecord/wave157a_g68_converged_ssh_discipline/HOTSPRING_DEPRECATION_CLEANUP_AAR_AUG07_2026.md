# AAR: hotSpring Deprecation Cleanup — Aug 7, 2026

## Summary

Removed deprecated `low_level/` MMIO module and fossilized 15 dependent sovereign-boot experiment binaries. Marked `fleet_client` and `fleet_ember` as deprecated (retained temporarily for `bin_helpers/sovereignty` and `glowplug_client`). Moved 51 previously-fossilized binaries from `src/bin/_fossilized/` to `archive/_fossilized/` so cargo no longer builds them.

## What Was Removed

| Module / File | LOC | Disposition |
|---|---|---|
| `src/low_level/bar0.rs` | 608 | → `archive/_fossilized/low_level_legacy/` |
| `src/low_level/falcon.rs` | 496 | → `archive/_fossilized/low_level_legacy/` |
| `src/low_level/mod.rs` | 30 | → `archive/_fossilized/low_level_legacy/` |
| 15 exp binaries (exp070–exp234, validate_ember_resilience) | ~9,500 | → `archive/_fossilized/` |
| 32 previously-fossilized binaries (src/bin/_fossilized/) | ~14,609 | → `archive/_fossilized/` |

**Total removed from active build**: ~24,000+ LOC

## What Was Retained (Deprecated)

| Module | Reason | Migration Target |
|---|---|---|
| `ember_types.rs` | Types-only; consumed by `glowplug_client` and `s_cold_boot_sentinel` validation | Absorb into `glowplug_client/types.rs` |
| `fleet_client.rs` | Socket discovery used by `bin_helpers/sovereignty/connect.rs` | toadStool fleet RPCs |
| `fleet_ember.rs` | `EmberClient`, `FleetEmberHub` used by `ipc/mod.rs` re-exports | toadStool dispatch RPCs |

All three are marked `#[deprecated(since = "0.6.32")]` with compiler warnings guiding toward toadStool.

## Cargo.toml Changes

- `low-level` feature: commented out (no longer needed; rustix dep can be removed in next cleanup)
- 15 `[[bin]]` entries: commented out with `# FOSSILIZED (v0.6.32)` markers

## Upstream Absorption Requests

### barraCuda should absorb:

1. **PrecisionEval** (`src/precision_eval.rs`) — empirical GPU precision probing that builds on `barraCuda::PrecisionTier`. The primal already defines the tier enum; it should also own the hardware measurement harness.

2. **HardwareCalibration probes** (`src/calibration/`) — GPU-specific calibration (clock domains, thermal throttling, memory bandwidth measurement) that should live in barraCuda's device layer alongside existing GPU discovery.

3. **Compensated summation primitives** — The WGSL `df64_compensated_sum.wgsl` shader pattern should be upstreamed into `barraCuda::shaders::math::` alongside the existing `df64_core.wgsl`.

### toadStool already replaces:

| Fossilized Module | toadStool RPC Equivalent |
|---|---|
| `low_level::bar0` (MMIO mmap) | `ember.mmio.read32` / `ember.mmio.write32` |
| `low_level::falcon` (ucode upload) | `ember.falcon.upload` / `ember.falcon.start` |
| `fleet_client` (socket discovery) | `toadstool.fleet.discover` |
| `fleet_ember` (per-ember JSON-RPC) | `toadstool.ember.*` RPC surface |

## Build Verification

- `cargo check --lib`: ✅ clean (0 errors, warnings only from deprecated markers)
- Pre-existing error in `arxiv_measure_battery` (type inference, unrelated): noted but not fixed here

## Next Steps

1. Migrate `bin_helpers/sovereignty/connect.rs` to use toadStool fleet RPCs → then fully remove `fleet_client.rs`
2. Migrate `glowplug_client` types into its own `types.rs` → then remove `ember_types.rs`
3. Remove `fleet_ember.rs` once IPC re-exports are no longer consumed
4. Remove commented `low-level` feature and `dep:rustix` from Cargo.toml
5. Upstream PrecisionEval and compensated summation to barraCuda
