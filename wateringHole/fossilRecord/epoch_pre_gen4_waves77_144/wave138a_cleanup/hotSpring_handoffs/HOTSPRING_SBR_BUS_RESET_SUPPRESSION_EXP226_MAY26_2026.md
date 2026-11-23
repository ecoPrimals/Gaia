# Handoff: SBR Bus Reset Suppression (Exp 226)

**From**: hotSpring (GPU sovereign compute team)
**To**: primalSpring / upstream primals teams
**Date**: 2026-05-26
**Experiment**: 226 (SBR Bus Reset Suppression)
**toadStool crates modified**: `cylinder`

## Summary

Experiment 225's FLR-first fix suppressed per-device resets via
`reset_method` sysfs. However, testing revealed the GPU still went cold
after anchor release. The kernel's `vfio_pci_dev_set_try_reset()` fires
`pci_reset_bus()` — a **Secondary Bus Reset (SBR)** at the PCIe bridge
level — when all devices in the dev_set have `open_count==0`.

SBR resets every device behind the bridge (`00:01.3`), bypassing
per-device `reset_method` entirely. `dmesg` showed both `02:00.0` (GPU)
and `02:00.1` (HD Audio) being reset simultaneously.

## Root Cause

The VFIO dev_set (devices behind the same PCIe bridge) contains both
`02:00.0` and `02:00.1`. The anchor only holds a cdev fd for `02:00.0`.
`02:00.1` was never opened by userspace (`open_count=0`). When the GPU
fd closes:

1. Per-device reset attempted → fails (reset_method cleared) → `needs_reset=true`
2. `vfio_pci_dev_set_try_reset()` checks: all devices `open_count==0`? YES
3. `pci_reset_bus()` → `pci_bus_resetable()` → `pci_bridge_secondary_bus_reset()`
4. Bridge control register bit 6 toggled → SBR fires → GPU cold

## Fix: `no_bus_reset.ko` Kernel Module

`pci_bus_resetable()` checks `PCI_DEV_FLAGS_NO_BUS_RESET` on the bridge
and all downstream devices. If any device has this flag, SBR is skipped.

Kernel 6.17 does not expose `no_bus_reset` via sysfs, so a tiny GPL module
(~25 lines C) is compiled via kbuild and loaded before the anchor drop:

```
BEFORE (Exp 225 fix alone):
  clear reset_method → drop anchor → per-device reset blocked ✓ → SBR fires ✗ → GPU cold

AFTER (Exp 226 three-layer defense):
  clear reset_method → load no_bus_reset.ko → drop anchor → per-device reset blocked ✓ → SBR blocked ✓ → GPU warm
```

## New APIs

### `guarded_sysfs::suppress_bus_reset(bdf: &str)`
- Compiles `no_bus_reset.ko` in `/tmp/toadstool-no-bus-reset/`
- Loads via `insmod_guarded()` with `bdf=<target>` parameter
- Module sets `PCI_DEV_FLAGS_NO_BUS_RESET` on the device

### `guarded_sysfs::restore_bus_reset()`
- `rmmod_guarded("no_bus_reset")`
- Cleans up build artifacts

### Updated: `guarded_sysfs::prepare_anchor_release(bdf: &str)`
Now has three-layer defense:
1. `pin_bridge_hierarchy()` — prevent D3cold
2. `disable_flr()` — suppress per-device FLR/PM reset
3. `suppress_bus_reset()` — suppress bus-level SBR

### Updated: Step 9 in `execute_handoff`
Calls `restore_bus_reset()` after `restore_flr()` to unload the module.

## Key Files Changed

- `crates/core/cylinder/src/vfio/guarded_sysfs/` (was `guarded_sysfs.rs` — split S276): `suppress_bus_reset()`, `restore_bus_reset()`, updated `prepare_anchor_release()` in `driver_ops.rs`
- `crates/core/cylinder/src/vfio/sovereign_handoff/` (was `sovereign_handoff.rs` — split S276): Step 9 restore in `pipeline.rs`, Step 0e diagnostic in `runtime_probe.rs`

## Test Results

- 710 cylinder lib tests pass
- 861 server lib tests pass
- Release binary built and installed

## Upstream Impact

- **toadStool**: `guarded_sysfs` API expanded (non-breaking)
- **No other primals affected**: changes are internal to sovereign handoff pipeline
- Requires kernel headers at `/lib/modules/$(uname -r)/build/` for kbuild compilation
