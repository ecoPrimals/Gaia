# sporePrint — Plaquette ×4 Normalization Discovery AAR

**Date**: 2026-08-02
**Wave**: post-155n (Publication phase)
**Gate**: eastGate (sporePrint team)
**Operator**: sporePrint/overwatch
**Task**: Absorb second AI review; resolve plaquette normalization blocker
**Priority**: **BLOCKER** — must resolve before any further production runs

---

## Summary

A second external AI review of the live Rung 1 preprint identified a
critical finding: the reported plaquette values (~0.15 at β=2.3) are
**exactly 1/4** of the conventional SU(2) Monte Carlo value (~0.60).

    4 × 0.15023811 = 0.60095244    (GPU, cpu_mom, 4⁴)
    4 × 0.15105782 = 0.60423128    (CPU, f64, 8⁴)

This is too precise a correspondence to be accidental.

---

## Why This Matters

The GPU-vs-CPU agreement (|Δ|/σ < 1) does NOT resolve this question.
Both implementations could share the same normalization bug. The
agreement proves they compute the same function — it does not prove
that function is the standard SU(2) plaquette.

**If the defect is in the measurement only** (extra 1/4 in the observable):
all generated configurations are correct, and multiplying reported values
by 4 recovers the standard convention. The HMC dynamics are unaffected.

**If the defect is in the action/force** (effective β/4 ≈ 0.575):
all generated configurations sample the wrong distribution. Every
production run to date is physically mislabelled. This would require
re-running everything.

**Running more trajectories before resolving this would produce more
potentially mislabelled data.** This is the first blocker.

---

## Diagnostic Protocol for hotSpring

These are small, fast, decisive tests — not production campaigns.

### Test A: Cold-lattice normalization check

On a cold 4⁴ lattice (all U = I), run the **exact production measurement
path** and record:

| Quantity | Expected | What to check |
|----------|----------|---------------|
| Raw trace sum: Σ_{x,μ<ν} (1/2) Re Tr U_{μν} | 1536 | Count of plaquettes |
| 6V | 1536 | Standard denominator |
| 24V | 6144 | Potential wrong denominator |
| P = raw_sum / denominator | 1.0 | Must be exactly 1.0 |

If the production path reports P = 0.25 on a cold lattice, the code
divides by 24V (or 4×6V) instead of 6V. That's the measurement bug.

### Test B: Coupling audit

Search the code for every use of β and verify the same convention in:

1. The Wilson action: S_g = β Σ_P (1 - (1/N) Re Tr U_P)
2. The gauge force: F_q = -∂S_g/∂q
3. The Metropolis ΔH: S_g(new) + K(new) - S_g(old) - K(old)

Look specifically for:
- β/2 vs β (common SU(2) convention difference)
- N=2 applied where N is already in the formula
- Division by number of dimensions (4) inside measurement
- `num_links = 4V` used where `num_plaquettes = 6V` is needed
- Averaging over directions inside a kernel AND on the host (double-average)
- Quaternion trace conventions (Tr/2 vs Tr for SU(2))

### Test C: Numerical force derivative

For one random link component q:

    F_analytic = code's force computation
    F_numeric  = -(S_g(q+ε) - S_g(q-ε)) / 2ε

If F_analytic = F_numeric / 4, the force has a missing factor of 4.
If F_analytic = F_numeric, the force is correct and the bug is in measurement.

### Test D: Quick β-scan against published data

At 8⁴, run SHORT CPU ensembles (50 thermalization + 50 production) at:

    β = 1.0, 2.0, 2.3, 3.0

Plot the results. If multiplying by 4 aligns them with published SU(2)
plaquette curves, the defect is observational. If not, the action needs
fixing.

---

## What sporePrint Did

### Paper changes
- Added normalization warning to Section 2.1 with explicit note
- Reordered experiment queue (Section 4.4): normalization first
- Added Appendix B: full diagnostic protocol
- Fixed "SU(3)" → "SU(2)" in three-path section
- Fixed "bit-exact" → "agrees to machine precision"
- Fixed Naga compilation path (WGSL → SPIR-V → Vulkan driver → native ISA)
- Qualified Intel GPU claim
- Removed unsupported $0.03/10K cost claim

### Site page changes
- pseudoSpore QCD page: "arXiv complete" → "preprint under refinement"
- pseudoSpore QCD page: "lattice QCD trajectories" → "SU(2) lattice gauge theory trajectories"
- pseudoSpore catalog: updated to match
- Paper page: added normalization as CRITICAL known issue
- Audit trail: added Phase 8 with full normalization analysis

---

## Experiment Queue (reordered)

| # | Experiment | Why first |
|---|-----------|-----------|
| 1 | **Resolve plaquette ×4** | Determines if existing data is correct |
| 2 | Action–force finite-difference | Validates HMC equations |
| 3 | Short β-scan vs published data | Establishes physical normalization |
| 4 | Reversibility + ΔH scaling | HMC correctness |
| 5 | Independent seeds + longer chains | Statistical authority |
| 6 | PRNG characterization | Documents the failed GPU path |
| 7 | 12⁴/16⁴ production | Scaling extension |
| 8 | Freeze + sign pseudoSpore | Final release |

**Do NOT run items 5-7 until items 1-3 are resolved.**

---

## What Others Need to Do

| Team | Action | Priority |
|------|--------|----------|
| **hotSpring** | Run diagnostic A-D (30 min of compute, not days) | **IMMEDIATE** |
| **hotSpring** | Report: is P=0.25 or P=1.0 on cold lattice? | **IMMEDIATE** |
| **hotSpring** | Code audit: search for β, N, 6V, 24V in action/force/measurement | **IMMEDIATE** |
| sporePrint | Update paper + site when resolved | Waiting |
| sporePrint | Regenerate LaTeX after resolution | Waiting |

---

## Key Insight

This is the pattern again: **internal consistency passes, external
calibration fails.** GPU agrees with CPU (internal). Both disagree
with published data by exactly 4× (external). The three-path validation
caught the PRNG bug because it compared paths within the system. The
normalization bug requires comparison against something outside the system.

The AI review caught it. That's why the paper is open for review.

---

*sporePrint Wave post-155n — Plaquette ×4 normalization is the first
blocker. Small diagnostic tests (not production campaigns) will resolve
it. Do not generate more data until the normalization is confirmed.*
