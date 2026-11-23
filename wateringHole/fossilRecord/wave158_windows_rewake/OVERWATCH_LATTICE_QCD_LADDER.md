# Lattice QCD Ladder — 6-Rung Research Program

**Date**: Aug 2, 2026 | **Wave**: post-155n
**From**: sporePrint team | **To**: eastGate overwatch
**Context**: AI review of arXiv preprint reframed the work as Rung 1
of a lattice QCD program. This document defines the full ladder.

---

## Status Summary

The arXiv preprint has been refined from "lattice QCD paper" to:

> **"Toward Vendor-Agnostic Lattice QCD on Consumer GPUs: SU(2) Hybrid
> Monte Carlo with DF64 WebGPU/WGSL and Cryptographic Provenance"**

This correctly frames the SU(2) result as the foundation layer, with
SU(3), fermions, and hot-QCD as subsequent rungs. The preprint is
under validation — an experiment queue has been handed to hotSpring.

### What the AI review said was right

- The self-contained, falsifiable claims check out (plaquette values,
  precision measurements, PRNG isolation)
- The title should indicate SU(2) + "toward lattice QCD"
- The paper needs explicit plaquette normalization, β-scan, more
  statistics, and HMC validation diagnostics
- 16⁴ claims should match actual production data
- Future rungs are not weaknesses — they're a research program

### What sporePrint did

- Retitled to "Toward Vendor-Agnostic Lattice QCD on Consumer GPUs"
- Added Section 1.2: Scope and Ladder (6-rung table)
- Added explicit plaquette normalization equation
- Added precision path matrix (CPU/DF64/native-f64 per component)
- Reframed limitations as "present result" + "remaining validation work"
- Created experiment queue for hotSpring (β-scan, statistics, HMC validation)
- Removed 16⁴ overclaims from abstract and cost analysis

---

## The 6-Rung Ladder

### Rung 1 — SU(2) Execution and Arithmetic Validation (CURRENT)

**What it proves**: Non-Abelian gauge HMC can execute through WebGPU/WGSL.
DF64 is accurate. Common shader source produces equivalent distributions on
AMD and NVIDIA. The deterministic GPU MD path can be separated from the
faulty stochastic path. Trajectory artifacts carry verifiable provenance.

**Status**: Data complete. Experiment queue in progress (β-scan, statistics,
HMC diagnostics). Preprint will be submitted after queue completes.

**Owner**: hotSpring (experiments) + sporePrint (paper)

### Rung 2 — SU(3) Pure Gauge

**What it proves**: The engine runs the gauge sector of lattice QCD.

**Required implementation**:
- 3×3 complex SU(3) link matrices
- 8-component Lie-algebra momenta (su(3) generators)
- Gell-Mann generator conventions
- SU(3) Wilson or improved gauge action
- SU(3) staple and gauge-force kernels
- Exponential or Cayley SU(3) link update
- Reunitarization/projection strategy
- Plaquette, Polyakov loop, and topology measurements

**Required evidence**:
- Cold and hot starts
- Known SU(3) plaquette values across several β
- Agreement with independent CPU implementation
- Reversibility and ΔH scaling
- Unitarity and determinant drift
- Finite-temperature deconfinement on N_s³ × N_τ

**Owner**: hotSpring + barraCuda (WGSL shader infrastructure)

### Rung 3 — Dirac Operator and Valence Quarks (Quenched QCD)

**What it proves**: Quark propagators can be computed on SU(3) backgrounds.

**Required implementation**:
- Fermion discretization (Wilson, staggered, or clover)
- Gauge-covariant nearest-neighbor hopping
- Spin/color structure
- Even-odd preconditioning
- CG or BiCGStab solver
- Mixed/DF64 solver refinement
- Residual and true-residual checking

**Required evidence**:
- Pion and rho correlators
- Effective masses
- Chiral condensate (quenched)
- Solver convergence and gauge covariance
- CPU reference comparison

**Owner**: hotSpring (physics) + barraCuda (GPU solvers)

### Rung 4 — Dynamical Fermions (Full QCD)

**What it proves**: The engine generates gauge configurations that respond
to sea quarks. This is the decisive QCD threshold.

**Required implementation**:
- Pseudofermion generation
- Dirac solves inside every force evaluation
- Fermion-force kernels
- RHMC for fractional determinant powers
- Multi-shift solvers
- Multiple integration time scales
- Mass preconditioning
- Exact Metropolis correction across solver tolerances

**Required evidence**:
- Two-flavor heavy-quark dynamical ensembles
- Plaquette and pion mass vs quark mass
- Reversibility across solver tolerances
- Acceptance rates with fermion action

**Owner**: hotSpring (physics) + barraCuda (GPU infrastructure)

### Rung 5 — (2+1)-Flavor QCD

**What it proves**: Physical-mass QCD on sovereign hardware.

**Required**:
- Two degenerate light quarks + one strange quark
- RHMC for strange-quark determinant
- Line of constant physics
- Progressive mass reduction toward physical pion mass
- Volume and lattice-spacing studies

**Owner**: hotSpring (long-term)

### Rung 6 — Finite-Temperature Lattice QCD (Hot QCD)

**What it proves**: QCD thermodynamics on sovereign hardware.

**Required**:
- N_s³ × N_τ lattices (T = 1/aN_τ)
- Temperature scan crossing crossover
- Zero-temperature companion ensembles
- Scale setting
- Multiple N_τ (6, 8, 10, 12)
- Continuum extrapolation
- Observable ladder: plaquette, Polyakov loop, chiral condensate,
  susceptibilities, trace anomaly, pressure, entropy, speed of sound

**Owner**: hotSpring (long-term)

---

## Publication Plan

Each rung gets its own preprint:

| Rung | Title Pattern | Venue |
|------|--------------|-------|
| 1 | "Toward...: SU(2) HMC with DF64 WebGPU/WGSL" | arXiv hep-lat |
| 2 | "SU(3) Pure Gauge on Consumer GPUs via WebGPU" | arXiv hep-lat |
| 3 | "Quenched QCD with DF64 Dirac Operator on Consumer GPUs" | arXiv hep-lat |
| 4 | "Dynamical QCD on Consumer GPUs" | arXiv hep-lat + journal |
| 5 | "(2+1)-Flavor QCD on Sovereign Hardware" | Journal |
| 6 | "Finite-Temperature QCD on Consumer GPUs" | Journal |

Plus a software paper (JOSS) for the barraCuda + coralReef stack,
likely timed with Rung 2 or 3.

---

## Team Dependencies

| Team | Rung 1 | Rung 2 | Rung 3+ |
|------|--------|--------|---------|
| hotSpring | Experiment queue (β-scan, HMC validation) | SU(3) physics | Fermion physics |
| barraCuda | (done — DF64 arithmetic) | SU(3) matrix WGSL kernels | Dirac operator GPU solvers |
| coralReef | (done — shader compilation) | — | — |
| sporePrint | Paper + site + pseudoSpore | Paper + site | Paper + site |
| Node Atomic | (done — multi-vendor benchmarks) | — | — |

---

## Immediate Next Steps

1. **hotSpring**: Run experiment queue (β-scan is highest priority)
2. **sporePrint**: Update site paper + audit trail pages with reframing
3. **sporePrint**: Regenerate LaTeX when experiments complete
4. **overwatch**: Confirm Rung 2 timeline and barraCuda SU(3) work
5. **sporePrint**: Submit Rung 1 preprint to arXiv

---

*The AI review was right: this is Rung 1 of a ladder, not a finished QCD
paper. The SU(2) result is a strong preprint on its own merits. Name it
correctly, validate it thoroughly, and publish the later rungs as the
SU(3), fermion, and hot-QCD data arrive.*
