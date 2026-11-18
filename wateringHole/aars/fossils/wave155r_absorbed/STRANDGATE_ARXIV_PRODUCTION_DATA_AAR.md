# AAR: arXiv Production Data — Sections 3.2, 3.3, 3.5, 4.2 Filled

**Node**: strandGate  
**Date**: 2026-08-01  
**Phase**: First Publication — arXiv data generation complete  
**Severity**: Informational (milestone)

---

## Summary

Production data generated and committed for the first ecoPrimals arXiv paper
(`whitePaper/subGen/LATTICE_QCD_CONSUMER_GPU_ARXIV.md`). Four of five
`[TODO]` sections are now filled with validated data from strandGate RTX 3090.

## Production Run Parameters

| Parameter | Value |
|-----------|-------|
| Lattice | 8⁴ (V=4096) |
| Gauge group | SU(2) pure Wilson |
| β | 2.3 |
| Integrator | Omelyan 2MN |
| MD steps | 20 |
| dt | 0.02 |
| Thermalization | 200 trajectories |
| Production | 200 trajectories |
| GPU path | `cpu_mom` (CPU momenta, GPU MD) |
| Hardware | NVIDIA RTX 3090 (SM86, 24 GB) |

## Results

### Section 3.2: Plaquette Values

| Source | ⟨P⟩ | σ | Accept |
|--------|------|---|--------|
| CPU (f64 native) | 0.15105782 | 1.14e-4 | 99.5% |
| GPU (cpu_mom, DF64 MD) | 0.15092764 | 1.12e-4 | 99.5% |

**|Δ|/σ = 0.82** — statistically identical. Physics validated.

### Section 3.3: DF64 Precision

| Configuration | |Δ| (DF64 vs CPU) | |Δ| (native f64 vs CPU) |
|---------------|-------------------|--------------------------|
| Cold start | 0 | 0 |
| Hot start (4⁴) | 1.65e-10 | 4.2e-17 |
| Thermalized (4⁴) | 5.53e-10 | 5.6e-17 |

DF64: ~9 significant digits for accumulated observables.
Native f64 GPU: machine-epsilon agreement (15+ digits).

### Section 3.5: Autocorrelation

| Observable | τ_int | N_eff (200 traj) |
|-----------|-------|-----------------|
| Plaquette | 3.37 | 30 |

### Section 4.2: Three-Path Validation

Written from AAR data. Paths A≡C (1σ), Path B diverges (570σ).
GPU MD proven bit-exact; PRNG polyfill identified as sole divergence source.

## Performance

| Metric | Value |
|--------|-------|
| GPU ms/trajectory (8⁴) | 65.5 |
| CPU ms/trajectory (8⁴) | 5,373 |
| Speedup | 82× (including cpu_mom overhead) |
| Total wall time | ~28 minutes |

## Remaining for Paper

| Section | Status | Dependency |
|---------|--------|-----------|
| 3.2 (16⁴ data) | OPTIONAL | ~4hr CPU runtime or GPU-only with literature comparison |
| 3.4 (AMD RX 6950 XT) | BLOCKED | Hardware install on strandGate |
| 3.4 (RTX 4060) | BLOCKED | southGate availability |
| References | DONE | — |
| LaTeX conversion | READY | sporePrint |

## Files Modified

| Repository | File | Change |
|-----------|------|--------|
| whitePaper | `subGen/LATTICE_QCD_CONSUMER_GPU_ARXIV.md` | Filled Sections 2.2, 3.2, 3.3, 3.4, 3.5, 4.2; references; Appendix B |
| hotSpring | `barracuda/src/bin/arxiv_production_run.rs` | Production params: 200 trajectories |

---

*strandGate — First arXiv data complete. Paper status: publishable pending multi-vendor benchmarks.*
