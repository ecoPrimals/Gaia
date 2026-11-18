# AAR: biomeGate GPU Crankshaft — VFIO Live, Revalidation Prepped

**Date**: Aug 2, 2026 08:50 EDT
**Gate**: biomeGate
**Wave**: 155n (springs+gardens phase)
**Author**: biomeGate overwatch (agent-assisted)
**Status**: 3 GPUs VFIO-bound, toadStool + hotSpring built, revalidation matrix staged

---

## TL;DR

biomeGate GPU crankshaft is online. Three sovereign GPUs bound to vfio-pci: Titan V
(GV100, SM70), Tesla K80 (GK210×2, SM37 — **new card, replacing fire-destroyed unit**).
RTX 5060 remains host display for wgpu compute. toadStool and hotSpring release binaries
built and verified. VFIO device nodes live at `/dev/vfio/{49,35,36}`. Full 6-phase
revalidation matrix staged covering 44 experiments across sovereign boot, warm handoff,
cross-generation quench, and QCD science. **Exp 231 (K80 cross-gen quench probe) is
ready for its first-ever hardware run.**

---

## GPU Fleet — VFIO Status

| GPU | Arch | SM | Bus | VFIO Group | Driver | Role |
|-----|------|----|-----|-----------|--------|------|
| RTX 5060 | Ada/Blackwell | 89+ | `02:00.0` | — | `nvidia` | Host display, wgpu compute |
| **Titan V** | Volta (GV100) | 70 | `21:00.0` | `/dev/vfio/49` | `vfio-pci` | Sovereign dispatch, warm handoff |
| **K80 die 0** | Kepler (GK210) | 37 | `4b:00.0` | `/dev/vfio/35` | `vfio-pci` | Cross-gen quench, diesel engine |
| **K80 die 1** | Kepler (GK210) | 37 | `4c:00.0` | `/dev/vfio/36` | `vfio-pci` | Cross-gen quench, diesel engine |

### PCIe Topology

```
TRX40 Root Complex
  ├─ [02:00.0] RTX 5060 (IOMMU 69) — nvidia host
  ├─ [21:00.0] Titan V (IOMMU 49) — vfio-pci ← sovereign
  └─ [49:00.0] PLX PEX 8747 switch
       ├─ [4b:00.0] K80 die 0 (IOMMU 35) — vfio-pci ← sovereign
       └─ [4c:00.0] K80 die 1 (IOMMU 36) — vfio-pci ← sovereign
```

**K80 PLX caution**: Exp 193 proved unbinding ALL endpoints from the PLX switch causes
D3cold → kills the entire switch fabric (requires chassis power cycle). Hierarchy pinning
prevents this: never unbind both K80 dies simultaneously.

### Driver Resolution

- **nvidia-595-open** (Ubuntu default) only supports SM75+ (Turing and later)
- Switched to **nvidia-595 proprietary** for Titan V (Volta SM70) support on host path
- K80 (Kepler SM37) dropped from ALL nvidia drivers after 470.xx — irrelevant for
  sovereign compute (VFIO bypasses the host driver entirely)
- **Silicon deism**: the diesel engine sees all GPUs through BAR0, regardless of host
  driver support. BOOT0 register → chip ID → generation-aware pipeline.

---

## Builds Verified

| Component | Build | Time | Status |
|-----------|-------|------|--------|
| toadStool | `cargo build --release` | 2m17s | Clean (all diesel engine binaries) |
| hotSpring | `cargo build --release` | 25s | Clean (10 exp + 8 validation + unibin) |
| coralReef | `cargo test --workspace` | 72s | **3,553 tests passing**, 0 failures |

### Experiment Binaries Ready

| Binary | Target |
|--------|--------|
| `exp070_register_dump` | BAR0 register capture |
| `exp168_pmu_firmware_probe` | PMU firmware determinism |
| `exp170_sovereign_cold_boot` | Cold sovereign init |
| `exp171_sovereign_sec2_boot` | SEC2 DMA boot |
| `exp182_k80_fecs_pio_boot` | K80 FECS PIO |
| `exp183_k80_fecs_int_boot` | K80 FECS interrupt |
| `exp184_k80_gr_sovereign` | K80 GR sovereign init |
| `exp227_pmu_acr_revalidation` | PMU ACR → Tier 2 |
| `exp234_sovereign_warm_handoff` | Catalyst warm handoff |

---

## Revalidation Matrix (6 Phases)

### Phase 1: Safety (prevents fires)
- Exp 193: PLX D3cold keepalive — validate hierarchy pin on new PCIe topology
- Exp 200: Power safety profiles — generation-aware PMC_ENABLE staging
- Exp 214: D-state hardening — RAII guards, watchdog

### Phase 2: Sovereign Init (cold probe, low risk)
- Exp 197: `sovereign.init` RPC — Titan V (~203ms), K80 (PRAMIN dead expected)
- Exp 199: Diesel engine sovereign boot — `bar0_source=ember`, all BDFs
- Exp 201: Volta cold boot CG sweep
- Exp 204: VBIOS interpreter — Titan V: 422 ops, 231 BAR0 writes

### Phase 3: Warm Handoff (Titan V, progressive trust)
- Exp 213: Live warm handoff — IOMMU sibling unbind, tier classification
- Exp 219: Catalyst driver pattern — nvidia-470 catalyst, 83K alive regs
- Exp 227: Tier 2 breakthrough — TPC probe fix, pre-PRI-recovery FECS
- Exp 230: Diesel abstraction revalidation — `InterruptProfile` dispatch

### Phase 4: K80 Cross-Generation (biomeGate first)
- **Exp 231**: K80 cross-gen quench probe — **FIRST-EVER HARDWARE RUN**
- Exp 182: K80 FECS PIO boot
- Exp 183: K80 FECS interrupt boot
- Exp 184: K80 GR sovereign init

### Phase 5: Dispatch Validation
- Exp 234: Catalyst warm handoff — VFIO dispatch, coralReef WGSL→SPIR-V
- Exp 228: Sovereign dispatch sprint — Tier 2.5 mechanics
- Exp 191: toadStool PBDMA validation — compute trio pipeline

### Phase 6: QCD Science
- `hotspring_unibin validate` — 18 default scenarios
- `validate_compute_trio_pipeline` — Yukawa + Wilson plaquette
- Silicon profiling — RTX 5060, Titan V, K80 (new profiles needed)
- PRNG polyfill validation — coralReef f64 transcendental preambles vs CPU reference

---

## K80 Status Update

The SOVEREIGN_VALIDATION_MATRIX marks K80 as "Hardware Destroyed (Exp 199), RETIRED."
**biomeGate has a replacement K80.** This K80:
- Same silicon: GK210 (Kepler, SM37), dual-die behind PLX PEX 8747
- BDFs: `4b:00.0` (die 0) + `4c:00.0` (die 1)
- IOMMU groups 35 + 36 (separate — good for independent VFIO binding)
- Exp 200 power safety profiles prevent the PMC_ENABLE bulk-write that caused the fire

The cross-generation quench probe (Exp 231) validates `InterruptProfile::PRE_VOLTA`
dispatch on live Kepler silicon — the most critical safety mechanism in the diesel engine.

---

## Observations

- IOMMU groups are clean on Threadripper TRX40 — each GPU in its own group (K80 dies
  in separate groups). No IOMMU group sibling issues unlike strandGate's Exp 213.
- K80 HD audio function is absent (3D controller only, no fn 1) — simplifies VFIO binding.
- The nvidia-595 proprietary module will also allow Titan V visibility in nvidia-smi after
  reboot (useful for wgpu/NVK path validation alongside VFIO sovereign path).
- 128GB RAM enables full 4-layer brain pipeline (Exp 028-030) without memory pressure.
- Threadripper 3970X (32c/64t) gives substantial parallel build capacity for
  coralReef multi-arch compilation tests.

---

*biomeGate GPU crankshaft LIVE. 3 sovereign GPUs on VFIO. K80 UNRETIRED. 44 experiments
staged for revalidation. Exp 231 first-ever hardware run queued. Silicon deism: all cards
are the same to the diesel engine.*
