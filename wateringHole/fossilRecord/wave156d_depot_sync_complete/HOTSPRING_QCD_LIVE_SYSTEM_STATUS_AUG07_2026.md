# hotSpring QCD — Live System Status & Next Goals

**Date**: Aug 7, 2026 | **Wave**: 156 (post-cascade)  
**Gate**: strandGate  
**Philosophy**: The system IS the deliverable. Paper is external validation. Reviewers use the system.

---

## Project Posture

The arXiv paper is **ancillary** — an external validator, not the primary output. The primary output is a **live, usable lattice QCD system** on consumer hardware that domain experts (Murillo, Chuna, Bazavov) can interact with directly:

- Run configurations on their own inputs
- Validate against their own reference implementations (MILC)
- Reproduce published results independently
- Extend to new gauge groups, couplings, volumes

The paper documents what the system does. The system proves what the paper claims.

---

## Remaining "Open" Items — All Upstream

The 3 items tracked as "OPEN" in the rubric are **not hotSpring deliverables**:

| Item | Owner | Nature |
|---|---|---|
| **C5**: naga Box-Muller bias | naga/gfx-rs upstream | External compiler bug in WGSL `log`/`cos` polyfills. Documented, workaround deployed (cpu_mom path). Bug report is a courtesy to the Rust graphics ecosystem, not a science blocker. |
| **M7**: pseudoSpore URL resolves | lithoSpore + sporePrint | Live site infrastructure. URL routing, artifact hosting, DNS. Not physics. |
| **X2**: pseudoSpore URL naming | sporePrint | Text correction in URL path (`su2` → `sun`). Copy edit. |

**hotSpring's Rung 1 science is COMPLETE.** The remaining work is making the system *live and accessible* for reviewers.

---

## Current System Capabilities (validated Aug 7, 2026)

### Physics Engine

| Capability | Status | Evidence |
|---|---|---|
| SU(N) HMC for N=2,3,4,5,6,8 | ✅ Production | `GaugeGroup` trait, Cabibbo-Marinari for N≥4 |
| DF64 on FP32 ALUs (~14 sig digits) | ✅ Validated | Precision matrix ALL PASS, per-op 10⁻¹⁴ |
| Omelyan 2MN integrator (λ=0.1932) | ✅ | 4× ΔH reduction vs leapfrog |
| Cross-vendor NVIDIA/AMD (6 ppm) | ✅ Confirmed | Same WGSL → identical physics |
| Deterministic bitwise reproducibility | ✅ | Forward=Backward diff=0.0 |
| β-scan reproduces literature (0.01%) | ✅ | GL98, Necco-Sommer, Bali matches |
| Deconfinement transition detection | ✅ | Polyakov loop + susceptibility peak |
| Wilson loops + Creutz ratios | ✅ | String tension extraction |
| Gradient flow + topological charge | ✅ | Full observable battery |
| Cryptographic provenance (BLAKE3 DAG) | ✅ | Every trajectory content-addressed |

### Performance

| Volume | GPU ms/traj | Speedup vs CPU |
|---|---|---|
| 4^4 | 9.4 | 9.9× |
| 8^4 | 28.4 | 53× |
| 16^4 | 617 | 40× |
| Hardware cost | $2,250 total | RTX 3090 + RX 6950 XT |

### Infrastructure

| Component | Status |
|---|---|
| MILC v5 format reader/writer | ✅ Implemented (native, roundtrip validated) |
| ILDG format interop | ✅ (14/14 configs roundtrip) |
| Jackknife/bootstrap error analysis | ✅ |
| NPU phase classification (AKD1000) | ✅ (100% accuracy, 2 µs/sample) |
| Config memo table (cache + replay) | ✅ (~100 configs across SU(2)–SU(8)) |

---

## What "Live and Usable for Reviewers" Means

### For Bazavov (MILC collaboration)

| Need | Status | Gap |
|---|---|---|
| Read a MILC config, compute plaquette, match MILC's answer | Code ready | Need a real MILC config from him (or public archive) |
| Write hotSpring configs in MILC format for him to validate | Code ready | — |
| Reproduce published MILC plaquette values at matched β/V | ✅ Done (0.01% agreement) | — |
| ILDG roundtrip (read/write/verify) | ✅ Done | — |

### For Chuna (algorithmic)

| Need | Status | Gap |
|---|---|---|
| Run HMC with custom parameters (β, V, n_traj) | ✅ Binaries exist | Need clean CLI or config-file interface |
| Verify integrator order (ΔH vs dt²) | ✅ Done | — |
| Reversibility test | ✅ Done (dt² scaling) | — |
| Action-force finite-difference | ✅ Done (Δ/F = 8×10⁻⁶) | — |
| Compare against his own code | Possible via MILC/ILDG | — |

### For Murillo (computational)

| Need | Status | Gap |
|---|---|---|
| Reproduce results from source (`git clone` + `cargo run`) | ✅ Documented | Need to verify on fresh machine |
| DF64 benchmark vs native f64 | ✅ Data exists | — |
| See provenance chain for a trajectory | ✅ Code works | Need clean CLI for inspection |
| Memory scaling analysis | ✅ In paper | — |

---

## Next Goals — Making It Live

### Priority 1: Reviewer-Ready Interface (immediate)

| Goal | Description | Owner |
|---|---|---|
| **MILC validation loop** | Acquire a small public MILC config (NERSC gauge archive or from Bazavov), load it, compute plaquette, confirm match | hotSpring |
| **One-command reproduction** | `cargo run --release --bin validate_production_qcd` already works. Document the 60-second path from clone to physics. | hotSpring |
| **Config exchange workflow** | Document how to: (1) export a hotSpring config as MILC, (2) import a MILC config, (3) measure observables on it | hotSpring |

### Priority 2: Production Data Campaigns (ongoing)

| Goal | Description | Timeline |
|---|---|---|
| **SU(N≥4) thermalization** | Fill large-N table with production statistics at matched couplings | Days–weeks (CPU-bound) |
| **32⁴ production runs** | Large-volume SU(3) at β=6.0, 6.2 for continuum-limit evidence | Hours (GPU-bound) |
| **Finite-T scans** | Asymmetric lattices (24³×{4,6,8}) crossing deconfinement | Days |

### Priority 3: Live Infrastructure (sporePrint + lithoSpore)

| Goal | Owner | Status |
|---|---|---|
| pseudoSpore live site + artifact hosting | lithoSpore | In progress |
| sporePrint preprint surface (LaTeX → web) | sporePrint | In progress |
| naga upstream bug report (courtesy) | community contribution | Not blocking |

### Priority 4: Optimization Targets (from today's profiling)

| Target | Expected Impact | Complexity |
|---|---|---|
| SU3 matmul → cooperative matrix (tensor core) | 5–10× for matmul kernel | High — needs WMMA WGSL extension |
| PRNG Box-Muller → TMU LUT path | 2× for heat bath | Medium — texture sampling in WGSL |
| Tiled dispatch for 16⁴+ volumes | Recover 53×→40× plateau | Medium — workgroup scheduling |
| DF64 compensated summation in hot loops | Improved precision at no throughput cost | Low — shader already written |
| AMD DF64 preference routing | Better precision on AMD hardware | Low — PrecisionBrain routing |

### Priority 5: Rung 2 Preparation

| Goal | Description | Dependency |
|---|---|---|
| Dynamical fermion action | Staggered or Wilson Dirac operator on GPU | barraCuda solver infrastructure |
| Multi-shift CG solver (GPU-resident) | Already implemented (`resident_cg.rs`) | Needs production hardening |
| RHMC rational approximation | Code exists in `gpu_rhmc.rs` | Needs unidirectional path validation |
| Physical-mass approach | Progressive mass reduction toward m_π=135 MeV | Rung 3+ |

---

## Summary: What's Done vs What's Next

```
DONE (Rung 1 — system works, science validated):
├── SU(N) engine for N=2,3,4,5,6,8
├── DF64 precision validated (14 digits, matrix ALL PASS)
├── Cross-vendor confirmed (6 ppm NVIDIA/AMD)
├── Literature agreement (0.01% at β=6.0/6.2)
├── Full observable battery (plaquette, Polyakov, Wilson, Creutz, flow, Q)
├── MILC + ILDG interop code written
├── Cryptographic provenance chain
├── NPU phase classification
├── GPU HMC: 40–53× speedup on consumer cards
└── Paper: 40/42 rubric items complete

NEXT (make it live for reviewers):
├── MILC validation loop with real external config
├── One-command reproduction documentation
├── SU(N≥4) production statistics
├── 32⁴ large-volume campaign
├── Live pseudoSpore site (lithoSpore/sporePrint)
├── Optimization: tensor core matmul path
└── Rung 2 dynamical fermion preparation

UPSTREAM (not our problem, tracked):
├── naga Box-Muller polyfill bias (C5)
├── pseudoSpore URL routing (M7, lithoSpore)
└── URL naming fix (X2, sporePrint)
```

---

## For Overwatch

The hotSpring QCD system is **science-complete for Rung 1**. The remaining work is:
1. Making it *accessible* to external domain experts (Bazavov, Chuna, Murillo)
2. Running longer production campaigns for publication-quality statistics
3. Upstream teams delivering live infrastructure (site, URLs)

The paper publishes when the live system is ready for reviewer hands — not the other way around.
