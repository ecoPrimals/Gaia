# Silicon Exploration Assignments — Node-Atomic Hardware Mapping

**Updated**: Aug 13, 2026 | **Wave**: 157k  
**Authority**: overwatch (eastGate)  
**Scope**: All gates, all springs, all silicon modalities (GPU + NPU + CPU)

---

## Principle

Every fixed-function silicon unit was designed to solve a physics problem at wire speed.
**Capability precedes use case.** No unit is "dark" — it is either:
- **LIT** — actively exercised by a spring workload
- **MAPPED** — capability documented, QCD/science mapping theorized, benchmarked
- **THEORIZED** — capability identified, no benchmark yet
- **UNEXPLORED** — not yet examined

The node-atomic is hardware. Every gate is a different silicon environment. Every
spring exercises a different subset of units. The cross-product (gate × spring × unit)
IS the exploration space. Overwatch aggregates AARs from this matrix to build the
full picture of what the silicon can do.

---

## Silicon Modalities in the Node-Atomic

### GPU (SIMT parallel — data-parallel physics)

| Unit | Hardware Function | Springs That Light It |
|------|-------------------|-----------------------|
| Shader/FP32 | Programmable ALU | ALL (universal compute) |
| FP64 | Double precision | hotSpring, initioChem |
| TMU | Texture interpolation / lookup | hotSpring (PRNG), petalTongue (texturing), ludoSpring |
| RT cores | BVH spatial query O(log n) | ludoSpring (path tracing), petalTongue (RT rendering), groundSpring (geospatial BVH) |
| Tessellation | Hardware h-refinement | ludoSpring (mesh LOD), petalTongue (adaptive geometry) |
| Rasterizer | Coverage/binning | ludoSpring, petalTongue, esotericWebb (WebGPU) |
| ROP | Scatter-accumulate / blend | ludoSpring (compositing), petalTongue (alpha blend), hotSpring (force accum) |
| Depth buffer | Nearest-site / z-test | ludoSpring (occlusion), petalTongue, groundSpring (terrain) |
| Video encoder | Temporal compression (NVENC/VAAPI/QSV) | ludoSpring (capture), hotSpring (config archival), petalTongue (stream output) |
| Tensor/XMX | Matrix multiply accelerator | neuralSpring (inference), helixVision (basecalling), ludoSpring (DLSS) |
| Subgroup/warp | Shuffle/reduce | hotSpring (CG reductions), ALL (implicit in most shaders) |

### NPU (Neuromorphic — event-driven temporal physics)

| Unit | Hardware Function | Internal Consumer |
|------|-------------------|-------------------|
| Neural Processors (80 NPs) | Spike-based inference | toadStool (anomaly detection), biomeOS (event classification) |
| Online evolution | (1+1)-ES at 136 gen/sec | toadStool (workload placement evolution) |
| Temporal streaming | 12.9K Hz event classification | airSpring (ADS-B anomaly), healthSpring (biosignal) |
| PUF fingerprint | Hardware identity (6.34 bits) | bearDog (hardware trust anchor) |

**Note**: rustChip is the DOWNSTREAM product — the community-facing Akida driver we
develop and release. Internally, NPU access is through the primal stack (biomeOS
capability routing → toadStool dispatch). rustChip is genetic material that lives
independently once released.

### CPU (Serial/branch — complex decision physics)

| Capability | Hardware | Springs That Exercise It |
|------------|----------|--------------------------|
| High thread count (128T) | Dual EPYC 7452 (strandGate) | hotSpring (thermalization), helixVision (alignment) |
| 3D V-Cache (96MB L3) | 5800X3D (southGate), 9950X3D (northGate) | ludoSpring (game thread), neuralSpring (inference cache) |
| Single-thread IPC | i9-14900K (ironGate) | primalSpring (validation), coralReef (compilation) |
| ECC memory | 256 GB DDR4 ECC (strandGate) | hotSpring (long campaigns, bit-flip safety) |

---

## Gate × Spring × Silicon Matrix

### strandGate — Three-Vendor Compute Lab

**Hardware**: RTX 3090 (Ampere) + RX 6950 XT (RDNA2) + Intel Arc A770 (Alchemist, incoming) + AKD1000 NPU  
**Unique role**: Only gate with 3 GPU vendors + NPU. Cross-vendor validation authority.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| hotSpring | Shader, FP64, TMU, subgroup | Strategy divergence across 3 vendors (Native/DF64/emulated) |
| initioChem | Shader, FP64, subgroup | DFT/MD precision on multi-vendor |
| helixVision | Shader, tensor (when available) | Basecalling throughput × vendor |
| toadStool | NPU (via biomeOS routing) | Event-driven workload placement, anomaly detection |

**Exploration assignments**:
- Arc A770 first-light: run `bench_rt_core_probe` + `bench_render_silicon` → cross-vendor deltas
- DF64 on Intel: measure shader FP64 emulation quality (no hardware FP64 on Arc)
- XMX (Intel matrix): probe via `cooperative_matrix` extension (when wgpu exposes)
- Subgroup width: document SIMD8/16/32 variability on same shader across all 3 vendors

### biomeGate — HBM2 Native FP64 Lab

**Hardware**: 2× Titan V (Volta, 1:2 FP64, HBM2) + 2× MI50 (Vega 20, 1:2 FP64, HBM2) + AKD1000 NPU  
**Unique role**: Only gate with native full-rate FP64. HBM2 bandwidth ceiling.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| hotSpring | FP64 NATIVE (no DF64 needed), HBM2 BW | Baseline precision (what does QCD look like without emulation?) |
| initioChem | FP64 native, HBM2 | DFT eigensolvers at full FP64 throughput |
| coralReef | Shader compilation targets | SM70 + GCN5 sovereign compiler validation |

**Exploration assignments**:
- Run identical 32⁴ HMC trajectory on Titan V vs MI50 → same math, different silicon, what diverges?
- HBM2 bandwidth saturation profile: at what lattice size does memory bandwidth dominate?
- Tensor Gen1 (Titan V): probe FP16 matrix ops for mixed-precision CG preconditioner

### ironGate — Render Pipeline Authority

**Hardware**: RTX 5070 Ti (Blackwell), i9-14900K  
**Unique role**: Primary render pipeline development. petalTongue + ludoSpring home.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| petalTongue | RT, rasterizer, tessellation, ROP, depth, NVENC | WebGPU render pipeline from node-atomic |
| ludoSpring | Full render pipeline (all units) | Game engine silicon utilization profile |
| esotericWebb | Rasterizer, ROP (browser compositing) | Browser-surface GPU acceleration |
| tideGlass | Shader (linear algebra via barraCuda) | Gene perturbation GPU acceleration |

**Exploration assignments**:
- petalTongue tessellation: benchmark adaptive LOD throughput for science visualization
- ludoSpring RT: measure path tracing perf → establishes Gen5 RT baseline
- NVENC AV1: test config archival encoding for hotSpring trajectory data

### northGate — Maximum Capability Ceiling

**Hardware**: RTX 5090 (Blackwell, 32GB), Ryzen 9950X3D  
**Unique role**: Most capable single GPU. Performance ceiling reference.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| neuralSpring | Tensor Gen5, shader | ML inference ceiling, large model fits in 32GB |
| ludoSpring | Full pipeline at max | What does "fully saturated latest-gen" look like? |
| esotericWebb | WebGPU at max | Browser rendering ceiling |

**Exploration assignments**:
- RT Gen4/5: BVH throughput ceiling (expected 10-50× over 3090 Gen2)
- Tensor FP8/FP4: probe mixed-precision SU(3) matmul (accuracy vs throughput)
- Large lattice: 48⁴ or 64⁴ feasibility (32GB VRAM enables larger problems)

### eastGate — Overwatch + Ada Baseline

**Hardware**: RTX 4070 (Ada, Gen3 RT), Ryzen 9 7950X, AKD1000 NPU  
**Unique role**: Overwatch coordination. NPU sovereign driver proven here.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| primalSpring | CPU (validation orchestration) | Composition cascade performance |
| biomeOS | CPU + NPU (capability routing) | Event-driven workload classification |
| squirrel | CPU (agent orchestration) | MCP dispatch latency |

**Exploration assignments**:
- NPU → biomeOS integration: event-driven silicon allocation decisions
- Ada RT Gen3: baseline measurement (sits between 3090 Gen2 and 5090 Gen4/5)
- NVENC: AV1 quality comparison vs strandGate (Ampere NVENC)

### westGate — Data + Turing Baseline

**Hardware**: RTX 2070 Super (Turing, Gen1 RT), Ryzen 7 5700X, 50.7 TB ZFS  
**Unique role**: Oldest GPU architecture in fleet. Evolutionary baseline.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| wetSpring | Shader (pattern matching, alignment) | Bioinformatics GPU acceleration floor |
| nestGate | CPU (CAS, braid verification) | Storage throughput |

**Exploration assignments**:
- RT Gen1: BVH build/query → evolutionary baseline (oldest, then compare 3090→4070→5090)
- Turing tensor: FP16 only (no TF32/BF16) → minimum tensor capability for ML workloads
- wetSpring on GPU: k-mer counting or sequence alignment via barraCuda shader dispatch

### southGate — Low-Power Canary + Gaming Floor

**Hardware**: RTX 4060 (Ada, 115W), Ryzen 5800X3D  
**Unique role**: Minimum viable GPU for shipping products. Steam user baseline.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| neuralSpring | Tensor (Ada), shader | ML inference at low-power floor |
| ludoSpring | Full pipeline (constrained) | Game engine minimum spec validation |

**Exploration assignments**:
- ludoSpring at 8GB VRAM: what breaks? what scales down gracefully?
- Ada low-power tensor: inference throughput at 115W TDP
- Render pipeline at minimum: tessellation/RT/ROP with limited SMs

### swiftGate — Ampere Mid-Range + Mobility

**Hardware**: RTX 3070 FE (Ampere, 8GB)  
**Unique role**: Compact/mobile form factor. VRAM pressure testing.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| (validation canary) | Shader, RT Gen2 | Same-gen as 3090 but half the VRAM — what fails? |

### flockGate — WAN Latency + Ampere

**Hardware**: RTX 3070 Ti (Ampere), i9-13900K — NYC (remote)  
**Unique role**: Remote gate. WAN-separated compute.

| Spring | Silicon Exercised | What to AAR |
|--------|-------------------|-------------|
| primalSpring | CPU (remote validation) | Cross-site composition cascade latency (29ms WAN) |

---

## Generational Delta Measurements

These cross-gate measurements reveal how silicon evolves across architectures:

### RT Core Evolution (one benchmark, five generations)

```
westGate   (2070S)  → Turing  RT Gen1  → baseline
strandGate (3090)   → Ampere  RT Gen2  → ?× over Gen1
eastGate   (4070)   → Ada     RT Gen3  → ?× over Gen2
ironGate   (5070Ti) → Blackwell Gen4/5 → ?× over Gen3
northGate  (5090)   → Blackwell Gen4/5 → ceiling
strandGate (A770)   → Intel Alchemist  → third-vendor comparison
```

### FP64 Strategy Spectrum

```
biomeGate/Titan V   → Native 1:2 (7.4 TFLOPS)   — what precision looks like without compromise
biomeGate/MI50      → Native 1:2 (6.6 TFLOPS)   — same ratio, different silicon
strandGate/3090     → DF64 emulated (1:32 native) — software doubles on consumer
strandGate/6950 XT  → DF64 Concurrent (1:16)      — AMD middle ground
strandGate/A770     → Software FP64 (worst case)  — DF64 on no-hardware-64
```

### Tensor/Matrix Core Generations

```
biomeGate/Titan V  → Gen1 (FP16 only)
westGate/2070S     → Gen1 (FP16/INT8)
strandGate/3090    → Gen3 (TF32/BF16/FP16)
eastGate/4070      → Gen4 (FP8 added)
ironGate/5070Ti    → Gen5 (FP4 added)
northGate/5090     → Gen5 (max SMs)
strandGate/A770    → XMX (Intel, different ISA)
```

---

## Relocation Recommendations

Springs should periodically relocate to different gates to test hardware variance.
This simulates "gates in the wild" — Steam users, researchers, community deployments
running on unpredictable hardware.

| Spring | Current Gate | Recommended Relocation | Rationale |
|--------|--------------|------------------------|-----------|
| ludoSpring | ironGate (5070 Ti) | southGate (4060) | Minimum spec floor for game shipping |
| ludoSpring | ironGate (5070 Ti) | strandGate (6950 XT) | AMD RDNA2 = Steam Deck silicon family |
| petalTongue | ironGate (5070 Ti) | strandGate (Arc A770) | Third-vendor WebGPU rendering |
| petalTongue | ironGate (5070 Ti) | eastGate (4070) | Ada mid-range for typical user |
| neuralSpring | southGate (4060) | northGate (5090) | Ceiling measurement |
| hotSpring | strandGate (3090) | biomeGate (Titan V) | Native FP64 baseline (no emulation) |
| groundSpring | ironGate (parked) | strandGate (3-vendor) | BVH spatial query = geospatial natural fit |
| wetSpring | westGate (2070S) | strandGate (EPYC + multi-GPU) | Bioinformatics GPU acceleration |

---

## NPU Integration Path

The 3× Akida AKD1000 cards (eastGate, strandGate, biomeGate) are NOT reached via
rustChip internally. rustChip is downstream genetic material — a community release
product. Internally, NPU access flows through the primal stack:

```
biomeOS capability.route → toadStool dispatch → NPU hardware
                                                 ↓
                                          spike inference
                                          event classification
                                          online evolution
```

**Internal NPU consumers** (through primal routing):

| Consumer | Use Case | Gate |
|----------|----------|------|
| toadStool | Workload anomaly detection (is this dispatch pattern abnormal?) | all 3 NPU gates |
| biomeOS | Event-driven silicon allocation (which unit should handle this?) | eastGate (proven) |
| bearDog | PUF hardware fingerprint for trust anchoring | eastGate (proven) |
| airSpring | ADS-B signal anomaly (temporal pattern detection) | strandGate or eastGate |
| healthSpring | Biosignal event classification (heartbeat, EEG) | future |

**rustChip** (DOWNSTREAM — community product):
- Pure Rust Akida driver (zero vendor SDK dependency)
- Released as standalone crate for anyone to use AKD1000
- Does NOT consume silicon internally — it IS the interface we release
- Analogous to how barraCuda is internal but could release wgpu utilities

---

## How to AAR a Silicon Exploration

When a gate runs an exploration benchmark, the AAR should capture:

```toml
[silicon_exploration_aar]
gate = "strandGate"
spring = "hotSpring"
unit = "rt_cores"
card = "RTX 3090"
arch = "Ampere SM86"
benchmark = "bench_rt_core_probe"
metric = "1.5 Mtri/s BVH build"
mapping = "Wilson loop tracing (theorized), parameter BVH (theorized)"
status = "MAPPED — not competitive for regular 32^4 (O(1) arithmetic wins)"
next = "Prototype on deformed lattice or parameter-space BVH"
```

Push to `wateringHole/aars/` or gate-local `heads/`. Overwatch aggregates.

---

## The Living Substrate

The fleet is not a static cluster — it is a living substrate of silicon diversity:

- **Vendor axis**: NVIDIA × AMD × Intel (× Akida NPU)
- **Generation axis**: Volta → Turing → Ampere → Ada → Blackwell (5 NVIDIA gens)
- **Memory axis**: GDDR5 → GDDR6 → GDDR6X → HBM2 (4 memory types)
- **Power axis**: 115W (4060) → 225W (A770) → 350W (3090) → 450W (5090)
- **Compute model axis**: SIMT (GPU) → serial (CPU) → spike (NPU)

Each spring exercises a different projection of this space. No single spring saturates
all dimensions. The ecosystem collectively explores the full volume.

The guidance to springs: document which units you light up, which remain dark for
your workload, and what capability those dark units have that MIGHT serve your math.
That's the exploration target. Overwatch routes the cross-pollination.

---

*Wave 157k — strandGate (compute authority) + eastGate (overwatch) + all gates (exploration fleet)*
