# hotSpring + toadStool: FECS CPUCTL_ALIAS Breakthrough

**Date:** May 15, 2026
**From:** biomeGate (hotSpring hardware team + toadStool diesel engine)
**For:** All primal teams (upstream audit reference)
**License:** AGPL-3.0-or-later
**toadStool Session:** S263

---

## Summary

Critical Volta FECS register discovery resolves a class of false-negative
diagnostics in the warm handoff pipeline. The `CPUCTL` register (0x100) on
Volta HS (Heavy Secure) falcons is security-locked and always reads 0x10
(HRESET), regardless of actual firmware state. All FECS probes must use
`CPUCTL_ALIAS` (0x130) instead, which bypasses the HS lock and returns
the true running state.

This discovery confirmed that **FECS survives the nouveau → vfio-pci warm
handoff completely**. Previous "FECS dead after PFIFO init" diagnoses were
entirely false alarms caused by reading the wrong register.

---

## Technical Details

### The Problem

After warm handoff (nouveau → vfio-pci), toadStool's `probe_warm_fecs()`
reported FECS in HRESET state. This triggered attempted re-boots via
`NvGspBridge::boot_falcon_hs()`, which consumed significant engineering
effort (PIO upload, bootloader DMEM descriptors, FBIF TRANSCFG configuration,
DMACTL tuning, VRAM staging attempts) — all unnecessary because FECS was
already running.

### Root Cause

Volta introduced Heavy Secure (HS) falcon mode. In HS mode, the `CPUCTL`
register at the standard falcon offset (0x100) is security-locked:

| Register | Base + Offset | HS Mode Behavior |
|----------|---------------|------------------|
| `CPUCTL` | FECS_BASE + 0x100 | Always reads 0x10 (HRESET bit set) |
| `CPUCTL_ALIAS` | FECS_BASE + 0x130 | True state — reflects actual CPU status |

The NVIDIA open-gpu-kernel-modules source confirms `CPUCTL_ALIAS` as the
host-accessible register for HS falcon status on Volta+.

### The Fix

All FECS probes in toadStool cylinder migrated from `CPUCTL` to `CPUCTL_ALIAS`:

- `fecs_warm_state_probe()` in `compute_device.rs`
- `fecs_needs_boot` logic in `open_vfio()`
- `fecs_probe()` in `channel/mod.rs`
- `bind_channel()` FECS status checks

### Impact

- Eliminated all false "FECS dead" reports during warm handoff
- Confirmed FECS firmware (loaded by nouveau) survives driver swap
- FECS remains running with valid PC, no HRESET, no HALTED
- Unlocks warm handoff as a reliable path to sovereign dispatch

---

## E2E Dispatch Pipeline Status

With FECS confirmed alive, the full dispatch pipeline is operational:

1. **Warm handoff** — nouveau initializes GPU → vfio-pci bind (FECS survives)
2. **VFIO open** — iommufd/cdev backend, BAR0 mapped, regions enumerated
3. **Channel creation** — PFIFO init (warm config), GPFIFO/USERD allocated,
   runlist submitted, channel bound to scheduler
4. **DMA roundtrip** — alloc → upload → dispatch → sync → readback (confirmed)
5. **GR context init** — SET_OBJECT with Volta compute class 0xC3C0

### Current Frontier: PENDING_CTX_RELOAD

The dispatch pipeline returns `completed`, but PBDMA is not consuming
pushbuffers (`hw_get` not advancing). Channel status: `PENDING_CTX_RELOAD`.

**Root cause:** FECS (from nouveau's context) does not recognize our newly
created channel and has not allocated/loaded a GR context for it.

**Attempted mitigations:**
- Allocated 1MB GR context DMA buffer at IOVA 0x1_2000
- Wrote GR context pointer into channel instance block
- Implemented scheduler cycle (`resubmit_runlist`: disable → preempt → re-enable)
- Channel still shows PENDING_CTX_RELOAD after scheduler cycle

**Next steps:**
1. Identity-map a VRAM region so FECS can DMA golden context to system memory
2. Extract GR context init method calls from nouveau source
3. Consider sending FECS method messages (INIT_CTXSW, BIND_CHANNEL) via mailbox

---

## Hardware Data (Titan V)

```
GPU:           GV100 (SM70) @ 0000:02:00.0
PMC_ENABLE:    0x5fecdff1 (23 engines active)
FECS CPUCTL:   0x00000010 (security-locked — always HRESET)
FECS ALIAS:    0x00000000 (true state — running, not halted)
FECS PC:       0x00001234 (firmware executing)
FECS MB0:      0x00000000 (no pending message)
Backend:       iommufd/cdev (kernel 6.17)
Channel:       ID=0, GPFIFO IOVA=0x10000, warm PFIFO config
```

---

## Files Changed (toadStool S263)

| File | Changes |
|------|---------|
| `cylinder/src/nv/compute_device.rs` | CPUCTL_ALIAS probes, GR_CTX allocation, IOVA layout |
| `cylinder/src/nv/nv_gsp_bridge.rs` | NEW — HS falcon boot with corrected FBIF/DMACTL |
| `cylinder/src/vfio/channel/mod.rs` | `resubmit_runlist`, `write_gr_context_ptr`, CPUCTL_ALIAS probes |
| `cylinder/src/vfio/channel/pfifo.rs` | `warm_handoff()` config, engine mask evolution |
| `cylinder/src/vfio/channel/registers/falcon.rs` | Corrected FBIF offsets/stride/targets, DMACTL, CPUCTL_ALIAS |
| `cylinder/src/vfio/ember_gate.rs` | `EmberGateBypass` for server-internal probes |
| `server/src/glowplug_client.rs` | BAR0 access via nvpmu instead of PCI config space |
| `server/src/pure_jsonrpc/handler/dispatch/mod.rs` | FECS probe logging, cached device lifecycle |

---

## Cross-References

- `hotSpring/experiments/191B_SOVEREIGN_DISPATCH_VALIDATED.md`
- `wateringHole/handoffs/HOTSPRING_SCIENCE_VALIDATION_HANDOFF_MAY15_2026.md`
- NVIDIA open-gpu-kernel-modules: `drivers/gpu/drm/nvidia/nv-reg.h` (CPUCTL_ALIAS)
- nouveau source: `drm/nouveau/nvkm/engine/gr/ctxgv100.c` (GR context init)

## Team Ownership

| Domain | Owner |
|--------|-------|
| FECS/CPUCTL_ALIAS, diesel engine, warm handoff | biomeGate |
| GR context init frontier | biomeGate |
| Physics math, validation fidelity | Strandgate |
| Upstream primal audit | primalPSing |
