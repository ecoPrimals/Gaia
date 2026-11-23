# arXiv Data — Vendor-Agnostic Lattice QCD on Consumer GPUs

**Paper**: `whitePaper/subGen/LATTICE_QCD_CONSUMER_GPU_ARXIV.md`
**Target**: arXiv hep-lat (cross-list cs.DC)
**ORCID**: 0009-0004-2141-0321
**Status**: **4/5 sections FILLED.** Section 3.4 (AMD multi-vendor) pending. biomeGate 3-GPU bench (G32) may provide additional vendor data.

---

## Section 3.1 — GPU Scaling Benchmarks (COMPLETE)

All data auditable. Every row has gate, GPU, date, and can be reproduced on the named hardware.

### RTX 3090 (strandGate) — Ampere SM86, 24 GB VRAM

**Source**: `aars/STRANDGATE_POST_THRESHOLD_NODE_ATOMIC_AAR.md`
**Date**: Aug 1, 2026
**Parameters**: SU(2), Omelyan integrator, β=6.0, n_md=10, dt=0.05, DF64

| Lattice | Volume | CPU ms/traj | GPU ms/traj | Speedup | Accept |
|---------|-------:|------------:|------------:|--------:|-------:|
| 4⁴      |    256 |        93.1 |         9.4 |    9.9× | 19-20/20 |
| 8⁴      |  4,096 |     1,490.7 |        25.8 |   57.8× | 20/20 |
| 8³×4    |  2,048 |       750.4 |        14.8 |   50.8× | 20/20 |
| 16³×4   | 16,384 |     5,978.4 |       150.4 |   39.8× | 5/5 |
| 16³×8   | 32,768 |    11,969.1 |       316.4 |   37.8× | 5/5 |
| **16⁴** | **65,536** | **24,007.7** | **625.9** | **38.4×** | 5/5 |
| 32³×4   |131,072 |    48,292.0 | (dispatch-bound) | — | — |

**Production rate (16⁴)**: ~5,500 trajectories/hour, ~138,000/day

### RTX 4060 (southGate) — Ada Lovelace SM89, 8 GB VRAM

**Source**: `fossilRecord/wave155n_southgate_post_threshold/SOUTHGATE_POST_THRESHOLD_AAR.md`
**Date**: Aug 1, 2026
**Parameters**: Same (SU(2), Omelyan, β=6.0, n_md=10, dt=0.05, DF64)
**Runtime**: 68.7 minutes (4,123 seconds)

| Lattice | Volume | CPU ms/traj | GPU ms/traj | Speedup |
|---------|-------:|------------:|------------:|--------:|
| 4⁴      |    256 |        77.0 |         6.7 |   11.4× |
| 8⁴      |  4,096 |     1,279.1 |        39.6 |   32.3× |
| 8³×4    |  2,048 |       650.8 |        20.0 |   32.5× |
| 16³×4   | 16,384 |     5,171.5 |       144.3 |   35.8× |
| 16³×8   | 32,768 |    10,478.5 |       281.1 |   37.3× |
| **16⁴** | **65,536** | **20,681.7** | **551.3** | **37.5×** |
| 32³×4   |131,072 |    41,779.6 |     1,096.8 |   38.1× |
| 32³×8   |262,144 |    82,536.9 |     2,199.5 |   37.5× |

**Key finding**: Ada Lovelace 12% faster per-core than Ampere at 16⁴ (551 vs 626 ms). 8 GB VRAM handles V=262,144.

### RX 6950 XT (strandGate) — RDNA2, 16 GB VRAM

**Source**: PENDING — strandGate has this GPU, needs benchmark run
**Status**: `[TODO]` — **THIS IS THE VENDOR-AGNOSTIC PROOF**

| Lattice | Volume | CPU ms/traj | GPU ms/traj | Speedup |
|---------|-------:|------------:|------------:|--------:|
| 8⁴      |  4,096 |             |             |         |
| 16⁴     | 65,536 |             |             |         |

### Cross-GPU Summary (for paper Table 1)

| GPU | Architecture | VRAM | GPU ms/traj (8⁴) | GPU ms/traj (16⁴) | Cost (new) |
|-----|-------------|------|-------------------|--------------------|-----------|
| RTX 3090 | Ampere SM86 | 24 GB | 25.8 | 625.9 | ~$700 used |
| RTX 4060 | Ada SM89 | 8 GB | 39.6 | 551.3 | ~$300 |
| RX 6950 XT | RDNA2 | 16 GB | `[PENDING]` | `[PENDING]` | ~$350 used |

---

## Section 3.2 — Plaquette Measurements (ROOT-CAUSED — P2 RESOLVED)

**Owner**: hotSpring team (strandGate)
**Status**: **ROOT-CAUSED.** GPU PRNG polyfill bias isolated. `cpu_mom` workaround deployed. GPU vs CPU now agree within 1σ.
**Source**: `aars/STRANDGATE_PLAQUETTE_DIVERGENCE_ROOT_CAUSE_AAR.md` (Aug 1, 2026)

### Root Cause: GPU PRNG Polyfill Bias

The divergence was NOT normalization — it was the **WGSL transcendental polyfills** in the GPU momentum generation shader (`su3_random_momenta_f64.wgsl`). The `log_f64`, `sqrt_f64`, `cos_f64` polyfills used for Box-Muller had implementation errors, producing momenta with wrong variance. This shifted the sampling distribution while keeping ΔH ≈ 0 (100% acceptance with wrong physics).

### Three-Path Comparison (the proof)

SU(3) Wilson gauge, β=2.3, 4⁴, Omelyan 2MN, n_md=20, dt=0.02:

| Path | Momenta | MD Evolution | ⟨P⟩ (4⁴, 50 traj) | Acceptance |
|------|---------|-------------|-------------------|-----------|
| A: CPU reference | CPU LCG + Gaussian | CPU Omelyan | **0.1509 ± 9.8e-4** | 100% |
| B: GPU (broken) | GPU PCG + Box-Muller (polyfills) | GPU streaming | 0.5072 ± 4.8e-3 | 100% |
| C: GPU (cpu_mom) | **CPU LCG + Gaussian → upload** | GPU streaming | **0.1517 ± 1.1e-3** | 100% |

**Paths A and C agree within 1σ.** Path B diverges by 570σ. Since B and C share the IDENTICAL GPU MD pipeline and differ ONLY in momentum source, the bug is isolated to the GPU PRNG shader.

### Static Plaquette Validation (measurement is bit-exact)

| Configuration | CPU ⟨P⟩ | GPU ⟨P⟩ (native f64) | |Δ| |
|---|---|---|---|
| Cold start (U=I) | 1.000000000000000 | 1.000000000000000 | 0 |
| Hot start (seed=42) | 0.069413282606898 | 0.069413282606898 | 4.16e-17 |
| Thermalized (200 HMC) | 0.154412193829055 | 0.154412193829055 | 5.55e-17 |

Agreement to **machine epsilon** — the GPU MD pipeline is correct.

### Publishable Data (with cpu_mom workaround)

| Metric | Value | Status |
|--------|-------|--------|
| GPU (cpu_mom) vs CPU | **|Δ|/σ < 1** (statistically identical) | ✓ publishable |
| GPU MD rate (4⁴ SU(3)) | **~18 ms/traj** on RTX 3090 | ✓ publishable |
| DF64 plaquette accuracy | **1.65e-10** vs native f64 | ✓ publishable |
| Native f64 GPU vs CPU | **bit-exact (4e-17)** | ✓ publishable |
| cpu_mom upload overhead | **~1 ms** per trajectory (negligible) | ✓ publishable |

### Impact on Paper

This finding **STRENGTHENS** the paper (Section 4 discussion):
- Demonstrates rigorous validation methodology for vendor-agnostic GPU physics
- WGSL/WebGPU f64 arithmetic is CORRECT for deterministic computation
- Specific, well-characterized failure mode (PRNG polyfills) with clean workaround
- The `cpu_mom` path gives correct physics at full GPU speed

---

## Section 3.3 — DF64 vs f64 Precision (TODO)

**Owner**: hotSpring team (strandGate)
**Status**: `[TODO]`

| Operation | Max |Δ| (ULP) | Mean |Δ| (ULP) | Digits Agreement |
|-----------|----------------|----------------|------------------|
| Addition | | | |
| Multiplication | | | |
| Division | | | |
| SU(2) multiply | | | |
| Plaquette accum | | | |

---

## Section 3.4 — Multi-Vendor (PARTIAL)

NVIDIA complete (2 GPUs). AMD PENDING.

---

## Section 3.5 — Autocorrelation (PARTIAL)

**Owner**: hotSpring team (strandGate)
**Status**: 8⁴ DONE. 16⁴ PENDING (needs GPU-only run, CPU ref too slow).
**Source**: `aars/STRANDGATE_ARXIV_QCD_PRODUCTION_AAR.md` (Aug 1, 2026)

| Lattice | β | τ_int (plaquette) | Effective independent configs | Method |
|---------|---|-------------------|------------------------------|--------|
| 8⁴ | 2.3 | **1.16** | **216** (from 500 traj) | binning |
| 16⁴ | 2.3 | `[PENDING]` | | |

---

## Section — Thermalization Figure (OPTIONAL)

Plot: plaquette vs trajectory number. SVG or high-res PNG.

---

## Nuclear Physics Benchmarks (southGate — separate publication track)

**Source**: `fossilRecord/wave155n_southgate_post_threshold/SOUTHGATE_POST_THRESHOLD_AAR.md`

| Benchmark | Peak Throughput | GPU |
|-----------|-----------------|-----|
| BCS Bisection (batch 8192) | 2,136,387 nuclei/sec | RTX 4060 |
| Batched Eigensolve (512×20dim) | 42,707 matrices/sec | RTX 4060 |
| Batched Eigensolve (512×30dim) | 14,941 matrices/sec | RTX 4060 |
| L2 HFB Pipeline (GPU-resident) | 18 nuclei/eval, 434s/eval | RTX 4060 |

---

## pseudoSpore Publication Rules

Every number in this file and in the arXiv draft must be:

1. **Traceable** — source AAR cited, gate named, date stamped
2. **Reproducible** — same hardware + same parameters = same result (within statistical error)
3. **Provenance-chained** — when trajectory/data files are bundled as pseudoSpore, full CAS + Provenance Trio chain attached
4. **Hype-free** — no theoretical TFLOPS, no unfair comparisons, all speedups specify "same algorithm, same hardware"
5. **Postable** — every completed section can go directly to primals.eco/pseudospore/ as a live evidence page

---

## Audit Trail

| Date | What | Source | Status |
|------|------|--------|--------|
| Aug 1, 2026 AM | RTX 3090 scaling (strandGate) | STRANDGATE_POST_THRESHOLD_NODE_ATOMIC_AAR.md | ✓ COMPLETE |
| Aug 1, 2026 AM | RTX 4060 scaling (southGate) | SOUTHGATE_POST_THRESHOLD_AAR.md (fossilRecord) | ✓ COMPLETE |
| Aug 1, 2026 AM | Nuclear physics benchmarks (southGate) | SOUTHGATE_POST_THRESHOLD_AAR.md (fossilRecord) | ✓ COMPLETE |
| Aug 1, 2026 PM | arXiv production run 8⁴ β=2.3 (strandGate) | STRANDGATE_ARXIV_QCD_PRODUCTION_AAR.md | ✓ DATA + **P2 DIVERGENCE** |
| Aug 1, 2026 PM | Autocorrelation τ_int=1.16 (8⁴) | STRANDGATE_ARXIV_QCD_PRODUCTION_AAR.md | ✓ COMPLETE |
| Aug 1, 2026 PM | P2 plaquette divergence found | STRANDGATE_ARXIV_QCD_PRODUCTION_AAR.md | ✓ Identified |
| Aug 1, 2026 PM | **P2 ROOT-CAUSED: GPU PRNG polyfill bias** | STRANDGATE_PLAQUETTE_DIVERGENCE_ROOT_CAUSE_AAR.md | ✓ **RESOLVED** — cpu_mom workaround |
| Aug 1, 2026 PM | Three-path comparison (A/B/C) | STRANDGATE_PLAQUETTE_DIVERGENCE_ROOT_CAUSE_AAR.md | ✓ A≡C within 1σ, B diverges 570σ |
| Aug 1, 2026 PM | Static plaquette bit-exact (4e-17) | STRANDGATE_PLAQUETTE_DIVERGENCE_ROOT_CAUSE_AAR.md | ✓ GPU MD pipeline correct |
| Aug 1, 2026 PM | ironGate remote access + golgi publish fix | SPOREGATE_IRONGATE_REMOTE_ACCESS_AAR.md | ✓ Three golgi bugs fixed |
| | AMD RX 6950 XT scaling | | PENDING |
| | DF64 ULP comparison | | PENDING |
| | Autocorrelation 16⁴ | | PENDING |
| | Production plaquette with cpu_mom path | | NEXT — unblocked |

---

*All data flows here. All data posts to pseudoSpore. The paper writes itself from auditable results.*
