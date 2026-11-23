<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# hotSpring — Sovereign Boot Abstraction + Profiling Handoff

**Date**: 2026-05-18
**From**: biomeGate (hotSpring hardware team)
**For**: Upstream primals (toadStool, coralReef, barraCuda), primalPSing audit
**Hardware**: Dual Titan V (GV100), RTX 5060

---

## Summary

Four-phase evolution formalizing GPU warm/cold boot state and building a
profiling framework for twin-card experimentation. All work lives in
toadStool (cylinder + ember crates), exposed via JSON-RPC.

### What Was Built

1. **Unified Boot State** (`cylinder::vfio::boot_state`): `SovereignBootState`
   enum (Warm/Cold) with `ColdBootReason`, `BootCapability` flags, and
   `probe_boot_state()` as the single authoritative detection function.

2. **WarmKeepalive Facade** (`ember::warm_keepalive`): `WarmKeepalive` owns
   `VfioAnchor` with lifecycle semantics. `WarmKeepaliveRef` for non-owning
   dispatch use. `DmaSpec` bridges ember→cylinder DMA backends.

3. **Profiling Framework** (`cylinder::vfio::sovereign_profile`):
   `sovereign.profile` JSON-RPC method returning µs-precision per-stage
   timings and register snapshots (BOOT0/PMC_ENABLE/PTIMER/FECS/GPCCS).

4. **Twin-Card Experiments**: Both Titan Vs profiled cold. Card #1: 11.3s
   total (5.4s memory, 3.7s falcon). Card #2: 13.0s total (10.5s memory).

### Hardware Line (Codified)

Cold boot = power-on reset = boot ROM trains HBM2. This is the same wall
NVIDIA's proprietary driver faces. Software cannot train HBM2 — only the
boot ROM, triggered by board-level voltage regulator sequencing, can.

**Keepalive strategy**: VfioAnchor + systemd FileDescriptorStore prevents
transition from warm→cold between daemon restarts by persisting VFIO fds.

---

## Impact on Upstream Teams

| Team | Impact |
|------|--------|
| **toadStool** | `SovereignBootState` is the new authority for warm/cold. Pipeline uses `probe_boot_state()` instead of `is_warm_gpu()`. `sovereign.profile` added to RPC surface. |
| **coralReef** | No direct changes. Compile-then-dispatch chain unchanged. |
| **barraCuda** | No direct changes. Validation scenarios unaffected. |
| **primalPSing** | New experiment 207 + handoff for audit. Cylinder test count: 606→634. |

## Gaps for Upstream Review

| Gap | Owner | Priority |
|-----|-------|----------|
| `WarmKeepalive` systemd fd store send/receive not yet wired | toadStool | High |
| `ColdBootReason::BusReset` vs `D3Cold` classification needs PCI link probes | toadStool | Medium |
| AMD `probe_boot_state` equivalent needed for `amd_metal.rs` | toadStool | Future |
| `sovereign.profile` not tested on Kepler (GK210) or Turing | hotSpring | Next |
| Long-running warm keepalive endurance test (48h+) | hotSpring | Next |

## toadStool Code State

toadStool has **uncommitted changes** (34 files, +3248 / -379 lines) spanning:
- `cylinder`: boot_state.rs, sovereign_profile.rs, sovereign_init.rs rewire,
  hardware.rs, VBIOS interpreter enhancements, AMD metal expansion
- `ember`: warm_keepalive.rs, lib.rs re-exports
- `server`: dispatch handler, sovereign.rs, RPC routing, method registry
- `cli`: unibin module updates

These should be committed and pushed before further evolution.

## hotSpring Experiment Count

207 experiments total (001-189 archived, 190 archived final coral-ember,
191-207 active). 634 cylinder / 596 barracuda-default / 1,045 barracuda-local
lib tests. 14 JSON-RPC methods (sovereign.profile added).
