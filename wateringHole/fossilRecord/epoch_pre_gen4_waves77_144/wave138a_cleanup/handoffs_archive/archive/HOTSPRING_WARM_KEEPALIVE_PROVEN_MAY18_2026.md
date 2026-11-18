<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# hotSpring — Warm Keepalive PROVEN: 183ms Sovereign GPU Init

**Date**: 2026-05-18
**From**: biomeGate (hotSpring hardware team)
**For**: Upstream primals (toadStool, coralReef, barraCuda), primalPSing audit, cross-platform testing
**Hardware**: Dual Titan V (GV100, 0000:02:00.0 + 0000:49:00.0), RTX 5060
**Experiment**: 208 — Reboot-Efficient Sovereign Evolution

---

## Summary

Sovereign GPU initialization on dual Titan V validated at **183ms**
(`compute_ready: true`). This is a 76× improvement over cold (14s) and
21× over the pre-falcon-fix warm (3.9s). The full keepalive lifecycle
— power cycle → first init → daemon restart → second init — is proven
end-to-end. No vendor driver, no kernel module beyond VFIO.

**This is ready for cross-platform ingestion and testing on other hardware.**

---

## What Was Built (toadStool, Exp 208)

### 1. `sovereign.warm_status` RPC

Lightweight JSON-RPC method reporting anchor state, boot state, PMC
engines, PRAMIN sentinel, and fd store capability per GPU. No pipeline
execution. Probes BAR0 via sysfs mmap.

### 2. Cold Pipeline Early-Exit

`skip_cold_memory_training` flag on `SovereignInitOptions`. Cold GPUs
skip doomed `memory_training` stage. Cold pipeline: 200ms (vs 14s).

### 3. Falcon Warm Preservation

Early falcon state probe **before** `pgraph_reset`. Reads FECS CPUCTL
(0x409100) and PC (0x409110). When falcon is `WarmRunning` (PC >= 0x40),
pgraph_reset and falcon_boot are skipped entirely. FLR PC threshold
prevents false positives from Function Level Reset artifacts.

### 4. systemd FileDescriptorStore

4 VFIO fds (2 device + 2 iommufd) stored on SIGTERM, retrieved on
startup. Anchors reconstructed. GPUs remain warm across daemon restarts.
Enables zero-downtime live patching.

---

## Validated Results

| Scenario | Pipeline (ms) | compute_ready | vs Cold |
|----------|-------------|---------------|---------|
| Cold full | 14,000 | false | — |
| Cold early-exit | 200 | false | 70× |
| Warm pre-falcon | 3,900 | true | 3.6× |
| **Warm + falcon** | **183** | **true** | **76×** |

Twin-card consistency: 183ms ± 5ms across both Titan Vs.

Warm state persists across `systemctl restart` — verified.

---

## Cross-Platform Testing Guide

The following must be validated on each new hardware target:

### Required Tests

| Test | What to Check | GV100 Baseline |
|------|--------------|----------------|
| **Falcon register layout** | FECS CPUCTL at generation-correct offset | 0x409100 (Volta) |
| **Post-boot-ROM falcon state** | PC value after power-on (before any driver) | PC=0xB0+ (WarmRunning) |
| **FLR residual PC** | PC value after VFIO device re-open | PC=0x00–0x10 (filter threshold: 0x40) |
| **pgraph_reset engine bit** | Which PMC_ENABLE bit resets PGRAPH | Bit 12 (Volta) |
| **ACR boot entry point** | Code section offset in firmware blob | 0x80+ (Volta) |
| **fd store round-trip** | `systemctl restart` preserves VFIO fds | 4 fds stored/retrieved |

### Architecture-Specific Notes

| Architecture | FECS Offset | Expected Differences |
|-------------|------------|---------------------|
| **Kepler (GK210)** | 0x409100 | No HS security — PIO boot, not ACR. Falcon detection may differ. |
| **Maxwell (GM200)** | 0x409100 | ACR boot similar to Volta. PC thresholds may differ. |
| **Pascal (GP100/GP102)** | 0x409100 | ACR boot. CPUCTL semantics similar. |
| **Turing (TU10x)** | 0x409100 | GSP-RM transition begins. Check if GSP replaces FECS. |
| **Ampere+ (GA10x)** | 0x409100? | GSP-RM dominant. Falcon warm detection may not apply. |
| **AMD Vega/RDNA** | N/A | No falcons. Warm detection uses GRBM_STATUS/SRBM_STATUS. Different pattern entirely. |

### Testing Procedure

1. Power cycle machine (gives boot ROM state)
2. `sovereign.init` on target GPU — record pipeline time and falcon detection result
3. `sovereign.init` again — should find WarmRunning, skip pgraph_reset
4. `systemctl restart toadstool-ember`
5. `sovereign.warm_status` — verify anchors held
6. `sovereign.init` again — verify 183ms-class pipeline time

---

## Files Changed (toadStool)

| File | Change |
|------|--------|
| `cylinder/src/vfio/sovereign_init.rs` | Early falcon probe, conditional pgraph_reset skip |
| `cylinder/src/vfio/sovereign_strategy.rs` | `detect_falcon_warm_state()` — CPUCTL/PC classification |
| `cylinder/src/vfio/sovereign_types.rs` | `skip_cold_memory_training` flag |
| `server/src/pure_jsonrpc/handler/dispatch/mod.rs` | `sovereign.warm_status` RPC, cold early-exit, anchor logging |
| `server/src/pure_jsonrpc/handler/mod.rs` | Route `sovereign.warm_status` |
| `server/src/pure_jsonrpc/handler/core/mod.rs` | Method registry |

---

## Impact on Upstream Teams

| Team | Impact | Action |
|------|--------|--------|
| **toadStool** | `detect_falcon_warm_state()` is the new warm pipeline gate. Falcon probe runs before pgraph_reset. `sovereign.warm_status` is a new RPC method. | Review register classification logic for non-Volta GPUs. |
| **coralReef** | No direct changes. Dispatch chain benefits from faster init. | Consider GPU readiness probes in composition graphs. |
| **barraCuda** | No direct changes. Compute dispatch unaffected. | Benefit: faster GPU availability after restarts. |
| **primalPSing** | Exp 208 + this handoff for audit. | Validate handoff claims against experiment log. |

---

## Gaps / Next Steps

| Gap | Owner | Priority |
|-----|-------|----------|
| Cross-generation falcon behavior (Maxwell/Pascal/Turing) | toadStool + hotSpring | High |
| AMD Vega/RDNA warm detection equivalent | toadStool | Medium |
| GSP-RM interaction on Turing+ (does GSP replace FECS warm?) | toadStool | Medium |
| Long-running warm endurance test (48h+) | hotSpring | Next |
| pmc_enable optimization (73ms, 40% of remaining time) | hotSpring | Next |
| Kepler PIO vs ACR warm detection path | hotSpring | Future |

---

## Whitepaper Reference

Full architectural deep-dive: `infra/whitePaper/gen4/architecture/SOVEREIGN_WARM_KEEPALIVE.md`

Experiment write-up: `springs/hotSpring/experiments/208_REBOOT_EFFICIENT_SOVEREIGN_EVOLUTION.md`

---

## hotSpring State

208 experiments (001-189 archived, 190+ active). 634 cylinder / 596
barracuda-default / 1,045 barracuda-local lib tests. 15 JSON-RPC methods
(`sovereign.warm_status` added). guideStone Level 6 CERTIFIED.
