# hotSpring → toadStool: Tier 2 PBDMA Root Cause Analysis

**Date:** June 1, 2026 (late session)
**From:** hotSpring Exp 234 pipeline validation
**To:** toadStool diesel engine team
**Priority:** P0 — single blocker for compute kernel execution on VFIO

---

## Summary

VFIO dispatch on Titan V GPUs completes the full pipeline (coralReef compile →
cylinder alloc → upload → dispatch → sync → readback) but returns all zeros.
FECS is alive but GP_GET never advances — the Host engine/PBDMA never consumes
the pushbuffer entries.

## Evidence

### FECS State (both Titan Vs identical)

```
ember.fecs.state:
  running: true
  halted: false
  pc: 4057 (advancing — idle firmware loop)
  os: 0 (no context loaded)
  mailbox0: 0, mailbox1: 1

ember.device.health:
  alive: true
  boot0: 335544481 (0x14000101 — GV100)
  engines_enabled: 23
  ptimer_ticking: true
```

### FECS Context Registers

```
FECS_CTXSW_STATUS_0: 0x00000000 (no context switch)
FECS_CTXSW_STATUS_1: 0x00000000
FECS_NEW_CTX:        0x00000000 (no context queued)
FECS_NEXT_CTX:       0x00000000
FECS_IDLESTAT:       0x00000001 (idle)
GR_ENGINE_STATUS:    0xbadf5040 (uninitialized)
```

### Host Engine / PBDMA Registers

```
PFIFO_RUNLIST_BASE:     0x00000000  ← NO RUNLIST
PFIFO_SCHED_DISABLE:   0x00000000
PFIFO_STATUS:           0xbad00200
PBDMA_GP_PUT(0):        0x00000000
PBDMA_GP_GET(0):        0x00000000
PBDMA_STATUS(0):        0x10011111
PBDMA_CHANNEL(0):       0x00000000
```

### PBDMA Diagnostics During Dispatch

```
pre-sync:
  gp_base=0x00010000, hw_put=0x00000005, hw_get=0x00010000
  gp_state=0x00090000, ch_state=0x07800000
  userd_lo=0x00011002, signature=0x00003ace

post-sync:
  hw_put=0x00000005, hw_get=0x00010000
  userd_gp_get=0, userd_gp_put=7, target=7

→ 7 pushbuffer entries submitted, 0 consumed by hardware
→ GP_GET never advanced from 0
→ sync timed out after ~1s polling
```

## Diagnosis

The cylinder creates a channel, allocates GPFIFO + USERD + GR context, builds
correct pushbuffers (compute_init + QMD launch + semaphore release), and writes
GP_PUT. But:

1. **RUNLIST_BASE = 0** — no runlist is configured at the Host engine level
2. **PBDMA_CHANNEL(0) = 0** — PBDMA is not bound to any channel
3. **hw_get = 0x00010000** — PBDMA GET pointer equals the GPFIFO base address
   rather than an entry offset, suggesting the PBDMA never started fetching

The Host engine scheduler needs a runlist to know which channels to schedule
on which PBDMAs. Without RUNLIST_BASE configured, the scheduler has nothing
to dispatch.

## Fix Path

The `init_channel_buffers` and `open_vfio` code create the channel structures
in DMA-mapped memory. The missing step is Host engine registration:

1. **Build a runlist** in DMA-mapped memory containing the channel descriptor
2. **Write RUNLIST_BASE** register (0x002270) with the runlist IOVA + entry count
3. **Trigger runlist submit** via RUNLIST_SUBMIT (0x002274)
4. **Optionally**: Poke FECS via mailbox to load the GR context

The new `ember.pramin.write` primitive can write instance memory, and the
existing pushbuffer submission machinery is correct. The channel code exists —
the runlist binding is the single missing piece.

## What's Working

- FECS firmware is alive and executing
- VFIO anchor FDs are held, BAR0 is mapped R/W
- DMA allocation and upload work correctly
- Pushbuffer generation (QMD, compute_init, dispatch) is correct
- Sync polling infrastructure works (just never sees GP_GET advance)
- Buffer readback returns data (just zeros since kernel didn't execute)
- coralReef sm_70 and sm_120 compilation both work

## Hardware Tested

- Titan V #1 (0000:02:00.0) — vfio-pci
- Titan V #2 (0000:49:00.0) — vfio-pci
- Both show identical behavior

## Related Gaps

- GAP-HS-118 (revised): Wire format resolved, FECS execution is the real gap
- sovereign.warm_status reports `sovereign_tier: 2` ("full shader dispatch and
  readback") — this tier assessment should be revised to account for the PBDMA
  binding state
