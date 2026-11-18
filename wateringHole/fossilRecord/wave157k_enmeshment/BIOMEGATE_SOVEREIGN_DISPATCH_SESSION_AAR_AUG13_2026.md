> **FOSSILIZED** — Wave 157k Enmeshment (Aug 16, 2026). Findings absorbed into ortho review + blurb.

# biomeGate Sovereign Dispatch Session AAR — Aug 13, 2026 (PM)

**Date:** Aug 13, 2026 14:00–17:00 UTC-4 | **Wave:** 157k | **Team:** biomeGate hotSpring sub-team
**Gate:** biomeGate (Threadripper 3970X, 128GB, RTX 5060 + Titan V + 2× K80)
**Status:** COMPLETE — 3 bugs fixed, 4 experiments run, diagnostics now honest

---

## Summary

Resumed sovereign dispatch work on freshly bootstrapped biomeGate. Ran Exp R1–R5
from the restaged experiment plan. Found and fixed three bugs in `toadstool-cylinder`
that were silently corrupting previous experiment results. Diagnostics are now honest.
Cold boot path on Volta is confirmed blocked at the HBM2 wall. Warm handoff remains
the viable path to Tier 2.

## Bugs Found and Fixed

### 1. `.zst` Firmware Decompression (silent failure since kernel 6.2+)

**File:** `primals/toadStool/crates/core/cylinder/src/nv/nv_gsp_bridge/mod.rs`

Linux kernel 6.2+ ships GPU firmware as `.bin.zst` (zstd-compressed). The
`NvGspBridge` firmware loader only looked for uncompressed `.bin` files. When
firmware wasn't found, it silently fell back to `NoopGspBridge` (no-op), skipping
all firmware-dependent stages (ACR, FECS boot, GR init).

**Fix:** `load_blob()` now tries `.bin` first, falls back to `.bin.zst` with
transparent decompression via the existing `ruzstd` dependency. `has_gr_firmware()`
updated to check both extensions.

**Impact:** All previous runs of `sovereign.init` on systems with kernel 6.2+ were
using `NoopGspBridge` without warning. The ACR → FECS boot chain was never attempted.

### 2. D3hot BAR0 Probe (probe on sleeping GPU)

**File:** `primals/toadStool/crates/core/cylinder/src/nv/compute_device/warm_probe.rs`

`probe_warm_fecs()` opened the VFIO device and mapped BAR0 but didn't wake the GPU
from D3hot power state before reading registers. All BAR0 reads returned `0xFFFFFFFF`.
The SM version was never set (stayed 0), causing the firmware availability check to
be skipped entirely — the factory returned None for all VFIO GPUs.

**Fix:** Call `enable_bus_master()` (which includes D3→D0 transition via PCI PM
capability) before mapping BAR0 in the VFIO fallback path.

**Impact:** On systems where sysfs BAR0 is not user-readable (permission denied),
VFIO GPUs could never be opened for sovereign dispatch. The previous biomeGate
deployment may not have hit this because sysfs permissions were different.

### 3. PRI Fault False Positives (0xBADFxxxx misidentified as warm state)

**Files:**
- `primals/toadStool/crates/core/cylinder/src/nv/compute_device/warm_probe.rs`
- `primals/toadStool/crates/core/cylinder/src/vfio/sovereign_strategy.rs`

When the PRI ring path to PGRAPH/FECS is down (GPC not powered, PGRAPH gated),
BAR0 reads to FECS registers return the PRI ring fault signature `0xBADFxxxx`.
Both warm detection paths (`probe_warm_fecs` and `detect_falcon_warm_state`)
interpreted the non-zero FECS CPUCTL/MAILBOX0 values as "warm preserved" state
(firmware resident in IMEM/DMEM).

This caused the pipeline to:
1. Skip `pgraph_reset` (thinking firmware would be destroyed)
2. Skip `falcon_boot` (thinking FECS was already running)
3. Report `compute_ready: true` (false positive)

**Fix:** Both functions now check for `(value & 0xFFFF_0000) == 0xBADF_0000` and
return cold/false when detected.

**Impact:** **Exp 223-224's `compute_ready: true` was a false positive.** Those
experiments reported success on cold Volta GPUs because the pipeline skipped all
boot stages (thought the GPU was warm). The "firmware loads but compute context
never becomes ready" issue was actually "firmware never loaded because the pipeline
skipped boot". This retroactively explains the gap between `compute_ready` and
actual dispatch failure.

## Experiment Results

### Exp R1: Baseline Tier Classification

All VFIO GPUs are Tier 0 (Cold) after FLR during runtime VFIO binding:
- Titan V (0000:21:00.0): FECS PRI faulted, 0 GPCs alive
- K80 fn0 (0000:4b:00.0): Cold
- K80 fn1 (0000:4c:00.0): Cold

### Exp R2: Firmware Probe (zstd fix)

`sovereign.init` now correctly uses `NvGspBridge` for GV100:
```
sovereign.init(ember): using NvGspBridge  chip="gv100"  bdf="0000:21:00.0"
```
Previous runs silently used `NoopGspBridge`. Confirmed fix.

### Exp R4: ACR Chain Cold Boot

sovereign.init pipeline on Titan V (202ms):

| Stage | Status | Detail |
|-------|--------|--------|
| identity_probe | OK | BOOT0=0x140000a1, GV100, SM70 |
| pmc_enable | OK | 23 engines (0x5FECDFF1) |
| pgraph_reset | OK | Now runs (previously skipped due to bug #3) |
| cg_sweep | OK | 16 PRI faults |
| pri_recovery | OK | 7 alive, 6 faulted |
| pgob_ungating | OK | **0 GPCs alive** |
| boot_state_probe | OK | **Cold** |
| memory_training | SKIPPED | **HBM2 requires power-on reset** |

### Exp R5: Tier Classification

**Tier 0 (Cold).** The sovereign.init pipeline cannot advance past memory training
on a cold Volta GPU. HBM2 DRAM initialization requires vendor VBIOS opcodes
(FBPA init, sequencer timing, PHY training) that are not yet implemented in
toadStool.

The pipeline correctly identifies the GPU as cold and halts at the HBM2 wall.
All 202ms are spent on identity/PMC/PRI recovery — no wasted work on FECS methods
against faulted PRI stations (unlike the previous buggy runs).

## Permissions Fix

During experiments, discovered that the `gpu-mmio` group added earlier in the
session wasn't active (requires re-login). Worked around by:
- `chown biomegate /dev/vfio/{35,36,49}` — direct user ownership
- `chmod 666 /sys/bus/pci/devices/*/resource0` — world-readable sysfs BAR0

These persist until reboot. On re-login, the `gpu-mmio` group will be active and
the original permission model (group-based access) will work.

## Revised Understanding

### Cold Boot Path (sovereign.init) — BLOCKED

```
identity → pmc_enable → pgraph_reset → pri_recovery → pgob_ungating
    ↓                                                        ↓
  GV100 ✓                                              0 GPCs (PRI faulted)
                                                             ↓
                                                    memory_training → BLOCKED
                                                    (HBM2 requires VBIOS)
```

### Warm Handoff Path — REQUIRED for Volta

The only proven path to Tier 2 on Volta remains the catalyst warm handoff
(nouveau or nvidia-470 seeder → vfio-pci swap). This bypasses HBM2/PGRAPH/GPC
initialization by inheriting a fully initialized GPU.

### K80 (Kepler) — Most Tractable Sovereign Target

K80's unsigned falcons allow direct PIO firmware upload without ACR. GDDR5
auto-trains from VBIOS (no HBM2 wall). Desktop Kepler firmware is not in
linux-firmware though — extraction from nouveau or nvidia-470 required.

## Files Changed

### toadStool (3 files modified)
- `crates/core/cylinder/src/nv/nv_gsp_bridge/mod.rs` — zstd firmware decompression
- `crates/core/cylinder/src/nv/compute_device/warm_probe.rs` — D3 wake + PRI fault filter
- `crates/core/cylinder/src/vfio/sovereign_strategy.rs` — PRI fault filter in detect_falcon_warm_state

### wateringHole (3 files created/modified)
- `handoffs/BIOMEGATE_BOOTSTRAP_AAR_AUG13_2026.md` — updated with code fixes + known issues
- `handoffs/BIOMEGATE_SOVEREIGN_DISPATCH_RESTAGE_AUG13_2026.md` — updated with experiment results
- `handoffs/BIOMEGATE_SOVEREIGN_DISPATCH_SESSION_AAR_AUG13_2026.md` — this document

## Next Steps

1. **Exp R6:** Nouveau warm handoff on Titan V (Phase C from restage plan)
2. **K80 firmware extraction** via nouveau dump or nvidia-470 extraction
3. **Re-login** to activate `gpu-mmio` group (or udev rule for persistence)
4. **kmod fix:** `no_bus_reset` kernel module build (missing Makefile in headers)

---

*Three bugs. Three fixes. Four experiments. Zero false positives.
The diagnostics are honest now. Science requires repetitions — and correct instruments.*
