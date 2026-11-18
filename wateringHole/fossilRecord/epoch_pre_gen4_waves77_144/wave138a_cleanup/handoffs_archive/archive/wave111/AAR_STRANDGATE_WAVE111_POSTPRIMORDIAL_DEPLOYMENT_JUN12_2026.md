# AAR: strandGate Wave 111 — postPrimordial Deployment + Hardware Registration

**Date**: 2026-06-12
**Gate**: strandGate
**Spring**: hotSpring v0.6.32 (barracuda v0.6.32, barracuda-local feature)
**Scope**: NUCLEUS Tower Atomic startup, hardware registration, postPrimordial math validation

---

## Summary

strandGate brought up a live NUCLEUS Tower Atomic stack and hotSpring primal server
against local hardware: NVIDIA RTX 3090 (24GB), AMD RX 6950 XT (16GB), and BrainChip
AKD1000 Akida NPU. Hardware was detected by hotSpring's wgpu adapter enumeration but
NOT auto-registered by toadStool — manual `lifecycle.register` to biomeOS was required.

## Hardware Inventory (PCI bus confirmed)

| Device | BDF | VRAM | Driver | IOMMU |
|--------|-----|------|--------|-------|
| NVIDIA GeForce RTX 3090 | 41:00.0 | 24GB GDDR6X | nvidia 580.126.18 | group 34 |
| AMD Radeon RX 6950 XT | 25:00.0 | 16GB GDDR6 | amdgpu (RADV Navi21) | group 55 |
| BrainChip AKD1000 Akida | e2:00.0 | 12MB SRAM | no module loaded | group 92 |
| Dual AMD EPYC 7452 | — | — | 128 threads, 256GB ECC | — |

## NUCLEUS Stack Brought Up

| Primal | Socket | Status |
|--------|--------|--------|
| bearDog | `beardog-e8b62b6e.sock` | alive, v0.9.0 |
| songBird | `songbird-e8b62b6e.sock` + TCP :7700 | alive, federation to golgiBody |
| biomeOS | `neural-api-e8b62b6e.sock` | alive, v0.1.0, BTSP optional |
| hotSpring | TCP :9800 | alive, v0.6.32, 2 GPUs detected, 139 capabilities |

## Validation Results

| Suite | Pass/Total | Notes |
|-------|-----------|-------|
| Tier 1 (Rust) scenarios | 265/282 (94%) | 5 IPC liveness (primals not running), 12 tolerance/stochastic |
| GPU f64 builtins | 12/12 | Native sqrt/exp sub-microsecond precision |
| Yukawa OCP MD forces | 20/20 | LJ, Coulomb, Morse, Newton 3rd law, Velocity-Verlet |
| Special functions | 19/19 | Digamma, beta, log-gamma, chi-squared at 10^-10 |

## Evolution Gap Discovered: TOADSTOOL-AUTO-REGISTER

**Severity**: P2 (blocks autonomous gate bootstrap for compute gates)

**Symptom**: toadStool `capabilities` subcommand reports "No platforms detected yet".
Despite NVIDIA and AMD GPUs being active on the PCI bus with loaded kernel drivers,
toadStool does not auto-discover or register them with biomeOS. hotSpring detected
both GPUs via wgpu adapter enumeration, but toadStool (the compute dispatch layer)
has no equivalent hardware discovery on startup.

**Impact**: Every gate with GPUs requires manual `lifecycle.register` calls to biomeOS
to make compute capabilities visible to the NUCLEUS topology. This blocks the
`gate.bootstrap` autonomous enrollment pipeline (cellMembrane Stream 1) for compute
gates — a gate that enrolls via `gate.bootstrap` will have security and discovery
but NO compute dispatch until hardware is manually registered.

**Recommended evolution**: toadStool should perform PCI/sysfs hardware enumeration on
startup and auto-register detected compute devices with biomeOS. This is a natural
fit for the **diesel engine ignition sequence** — the engine that bootstraps toadStool
should light off hardware discovery as part of its ignition, before the biome manifests
are loaded. The sequence would be:

1. **Ignition**: toadStool starts, enumerates PCI bus for GPU/NPU devices
2. **Registration**: Each detected device → `lifecycle.register` to biomeOS with
   capabilities derived from device class (NVIDIA SM → `compute.gpu.nvidia_*`,
   AMD GCN/RDNA → `compute.gpu.amd_*`, Akida → `compute.npu.akida`)
3. **Readiness**: biomeOS topology includes compute resources before any biome
   manifest or dispatch request arrives

**Upstream handoff**: toadStool team — this should be filed as a P2 evolution item,
potentially `TOADSTOOL-IGNITION-DISCOVERY` or wired into the existing diesel engine
architecture as a new ignition phase.

## Akida NPU Status

- PCI device visible (`e2:00.0`, BrainChip Inc AKD1000)
- No kernel module loaded — needs `akida-driver` package install
- hotSpring has `npu-hw` feature flag for Akida integration
- Blocked on driver availability, not on code

## Startup Notes

- **biomeOS BTSP**: Required `--btsp-optional` / `BIOMEOS_BTSP_ENFORCE=0` for local dev.
  Production deployment should use proper BTSP handshake.
- **songBird TCP bind**: Logs `Address in use` error on :7700 after successful bind —
  cosmetic log issue, UDS socket created successfully.
- **hotSpring PRIMAL_BIND_MODE=tcp_only**: TCP :9800 listener worked. UDS socket was
  not created in this mode (expected — `tcp_only` skips UDS).
- **cargo clean recovery**: 180GB reclaimed in previous session. Full rebuild including
  `barracuda-local` feature completed in 61 seconds (release profile).

## Files Changed

- `wateringHole/handoffs/hotSpring/` — this AAR
- `wateringHole/impulses/active/` — FRAGO updated with TOADSTOOL-AUTO-REGISTER gap
