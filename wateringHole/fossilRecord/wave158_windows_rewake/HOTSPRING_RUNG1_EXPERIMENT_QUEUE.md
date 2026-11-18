# Experiment Queue: Rung 1 Preprint Validation

**Date**: Aug 2, 2026 (updated) | **Wave**: post-155n
**From**: sporePrint team | **To**: hotSpring team (strandGate)
**Context**: Two AI reviews identified validation gaps in SU(2) preprint.
**Priority**: **BLOCKED** — resolve plaquette ×4 normalization FIRST.

---

## TL;DR

A second AI review identified that the reported plaquette values (~0.15
at β=2.3) are **exactly 1/4** of published SU(2) values (~0.60). This
must be resolved before any further production runs. The diagnostic
tests below take ~30 minutes of compute, not days.

**Do NOT run long statistics campaigns until the normalization is confirmed.**

---

## IMMEDIATE — RESOLVE FIRST

### 0. Plaquette ×4 normalization (BLOCKER)

**The problem**: 4 × 0.15024 = 0.60096. Published SU(2) at β=2.3 gives
≈ 0.60. The GPU-CPU agreement does not resolve this because both
implementations share the same normalization convention.

**Quick diagnostics** (run these first, ~30 min total):

**A. Cold-lattice check**: On a cold 4⁴ lattice (U=I), run the exact
production measurement path. Must report P=1.0. If it reports P=0.25,
the measurement divides by 24V instead of 6V (or applies 1/N twice).

**B. Code audit**: Search for every use of β, N, 6V, 24V in:
- Wilson action computation
- Gauge force computation
- Metropolis ΔH computation
- Plaquette measurement

Look for: β/2 vs β, N=2 applied twice, division by 4 dimensions,
averaging over directions in kernel AND on host, `4V` used where
`6V` is needed, quaternion Tr/2 conventions.

**C. Numerical force derivative**: For one random link component q:
```
F_code = your force function
F_num  = -(S(q+ε) - S(q-ε)) / 2ε
```
If F_code = F_num/4, the force has a missing factor. If equal, the
force is correct and the bug is in measurement only.

**D. Quick β-scan**: At 8⁴, run 50+50 trajectories at β = 1.0, 2.0,
2.3, 3.0. Plot plaquette. If ×4 repairs the curve, it's measurement.
If not, fix the action.

**Report**: Is P=0.25 or P=1.0 on cold lattice? That single number
tells us which class of bug this is.

---

## MUST COMPLETE (after normalization resolved)

### 1. β-scan — verify engine follows the theory

**What**: Plaquette values at multiple coupling strengths.
**Points**: β = 1.8, 2.0, 2.2, 2.3, 2.4, 2.5
**Volume**: 8⁴ minimum (4⁴ is fine for quick checks)
**Runs**: cpu_mom path, 200+ thermalization, 200+ production per point
**Deliverable**:

```markdown
| β   | ⟨P⟩ (GPU) | ⟨P⟩ (CPU) | |Δ|/σ | Accept |
|-----|-----------|-----------|-------|--------|
| 1.8 |           |           |       |        |
| 2.0 |           |           |       |        |
| 2.2 |           |           |       |        |
| 2.3 | (existing)|           |       |        |
| 2.4 |           |           |       |        |
| 2.5 |           |           |       |        |
```

**Why**: One β cannot show the engine follows the theory. Reviewers
will ask for this. If GPU and CPU track the same plaquette curve,
the engine is validated across the coupling range.

**Published comparison**: Compare against any published SU(2) plaquette
dataset (Creutz 1980 or similar) to provide external validation.

---

### 2. Increased statistics — strengthen headline numbers

**What**: Multiple independent seeds and longer chains.
**Minimum**:
- 4 independent seeds per volume (4⁴ and 8⁴)
- Both hot start and cold start for each seed
- 1,000 post-thermalization trajectories at the headline point (8⁴, β=2.3)
- Bootstrap or jackknife error estimation (not just σ/√N)
- Chain-by-chain plaquette means

**Deliverable**: Per-chain plaquette table + combined mean ± bootstrap error.

**Why**: Current N_eff = 30 at 8⁴ is an early signal. Reviewers will want
to see independent chains agree and error bars from resampling.

---

### 3. HMC validation — prove the algorithm is correct

**What**: Standard HMC diagnostic battery.
**Deliverables**:

| Test | Format | Why |
|------|--------|-----|
| ΔH histogram (both volumes) | Plot data (CSV) | Shows Hamiltonian conservation |
| ⟨exp(-ΔH)⟩ | Single number ± error | Must equal 1 (Creutz equality) |
| Acceptance vs step size | Table: δτ vs acc% | Integrator order verification |
| Forward-reverse trajectory error | |ΔU|, |ΔP| after forward+reverse | Reversibility (must be ~machine epsilon) |
| SU(2) unitarity drift | max |U†U - I| over trajectory | Numerical stability |
| det(U) drift | max |det(U) - 1| over trajectory | SU(2) constraint |
| Energy violation vs δτ | log-log table | Should scale as δτ² for Omelyan |

**Why**: These are standard in every HMC paper. The three-path comparison
proved the PRNG isolation, but these prove the HMC algorithm itself is
correctly implemented.

---

### 4. PRNG isolation completion — finish the three-path story

**What**: Quantify exactly what's wrong with the GPU PRNG.
**Deliverables**:

| Test | Format |
|------|--------|
| Mean and variance of each momentum component (GPU vs CPU) | Table |
| Gaussian QQ plot of GPU Box-Muller output | Plot data |
| Tail statistics (excess kurtosis, skewness) | Table |
| Uniform input distribution test | Table/plot |
| CPU vs GPU Box-Muller side-by-side (same seeds) | Comparison table |
| Acceptance RNG source verification | Note on which RNG |

**Why**: The PRNG failure is itself a valuable result. "WGSL transcendental
approximations can silently corrupt HMC stochastic sampling" is a finding
that benefits the broader community. Make it rigorous.

---

### 5. Plaquette normalization verification

**What**: Confirm the reported observable matches the standard definition.
**Equation in paper**:

    P = (1/6V) Σ_x Σ_{μ<ν} (1/N) Re Tr U_{μν}(x)

**Verify**: Cold start gives P=1. Hot random start gives P ≈ 0 (for SU(2)).
Compare thermalized P at β=2.3 against at least one published dataset.

**Why**: Central numerical sanity check. If the normalization is wrong,
all plaquette values are wrong.

---

## SHOULD COMPLETE (strengthen paper)

### 6. Larger volume production

**What**: Full plaquette + autocorrelation data at 12⁴ and 16⁴.
**Minimum**: cpu_mom path, β=2.3, 200 thermalization + 200 production.
**Deliverables**: Same format as existing 4⁴/8⁴ tables + VRAM usage.

**Why**: The paper currently claims "sizes tested up to 16⁴" without
production plaquette data at those volumes. Either add the data or
restrict all quantitative claims to 8⁴.

### 7. pseudoSpore freeze

**What**: Create a versioned, signed pseudoSpore release.
**Deliverables**:

- Release version tag (e.g., v1.0.0-rung1)
- Git commit hash
- Artifact BLAKE3 root hash
- bearDog Ed25519 public key fingerprint
- Exact driver and adapter metadata for both GPUs
- Complete validation command with expected output
- README describing exact reproduction steps

**Why**: Turns provenance from an architectural promise into a paper result.

---

## NOT NEEDED FOR RUNG 1 (future rungs)

The following are explicitly NOT blockers:

- SU(3) (Rung 2)
- Quarks/fermions (Rungs 3-4)
- 32⁴+ volumes
- Multi-GPU decomposition
- Physical thermodynamics (Rung 6)
- Intel GPU validation
- Fixed GPU PRNG (cpu_mom is validated)

These belong in the "Future Work" section, not in the experiment queue.

---

## Handoff Protocol

1. Run experiments on strandGate
2. Push results to whitePaper repo in standard table format
3. File completion AAR in wateringHole
4. sporePrint integrates into paper + site pages
5. sporePrint regenerates LaTeX
6. Final hype compliance review
7. arXiv submission

---

*Rung 1 preprint. The data we have is solid. These experiments close the
gaps between "promising first result" and "rigorous preprint." The β-scan
and HMC validation are the highest priority.*
