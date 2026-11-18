# hotSpring Science Validation Handoff — Strandgate

**Date:** May 15, 2026
**From:** biomeGate (hotSpring hardware team)
**For:** Strandgate (hotSpring physics/math team)
**License:** AGPL-3.0-or-later

---

## Summary

biomeGate is handing off 7 science validation issues to Strandgate before
continuing GPU sovereign dispatch work. These are physics math failures,
numerical precision frontiers, runtime regressions, and baseline coverage
gaps that belong to the physics validation side of hotSpring. biomeGate
will continue owning toadStool diesel engine evolution, VFIO dispatch,
and cross-generation NVIDIA hardware bring-up.

The two immediate blockers for clean `validate_all --tier smoke` are items
1 and 2. The remaining items are documented gaps and precision frontiers
that affect validation coverage and confidence.

---

## Issue 1: `validate_dynamical_qcd` — ΔH O(dt^2) Scaling Failure

**Severity:** Smoke tier failure (blocks clean `validate_all`)
**Binary:** `barracuda/src/bin/validate_dynamical_qcd.rs`
**Suite registration:** `validate_all.rs` line 91, tier `Smoke`

**Symptom:** Phase 1 checks leapfrog ΔH scaling by comparing single
trajectories at dt=0.02 vs dt=0.01 (n_steps=10, mass=2.0, β=5.5,
cold start, seed=42). The ratio `|ΔH(dt_coarse)| / |ΔH(dt_fine)|`
must be in (2, 8) for O(dt^2) confirmation. This check currently fails.

**Code reference:**

```rust
// barracuda/src/bin/validate_dynamical_qcd.rs:53-67
let dt_coarse = 0.02;
let dt_fine = 0.01;
let n_steps = 10;

let dh_coarse = single_trajectory_dh(dims, beta, 2.0, dt_coarse, n_steps, 42);
let dh_fine = single_trajectory_dh(dims, beta, 2.0, dt_fine, n_steps, 42);

let ratio = dh_coarse.abs() / dh_fine.abs().max(1e-15);
let scaling_ok = ratio > 2.0 && ratio < 8.0;
```

**Possible causes:**
- Acceptance band (2, 8) too brittle for single cold-start trajectory
- Leapfrog integrator regression in pseudofermion HMC path
- Fermion force computation introducing O(dt) errors that break scaling
- Cold-start lattice producing near-zero ΔH at fine dt, inflating ratio

**Provenance:** Gottlieb et al., PRD 35, 2531 (1987); Gattringer & Lang
(2010), Ch. 8.1-8.3. Quenched reference (`validate_production_qcd`)
passes 10/10 checks.

**Action:** Profile ΔH values at both dt settings. Consider increasing
n_steps, using warm-start instead of cold, or widening acceptance band
with documented justification. If integrator itself is regressed, check
`pseudofermion::dynamical_hmc_trajectory` force term.

---

## Issue 2: `validate_stanton_murillo` — Runtime / Hang

**Severity:** Smoke tier hang (blocks `validate_all` completion)
**Binary:** `barracuda/src/bin/validate_stanton_murillo.rs`
**Suite registration:** `validate_all.rs` line 152, tier `Smoke`

**Symptom:** Suite runs 6 (κ, Γ) transport cases with full MD + ACF
(Green-Kubo) pipeline at N=500. Takes 20+ minutes without completing,
effectively hanging the smoke tier.

**Code reference:**

```rust
// barracuda/src/bin/validate_stanton_murillo.rs:67-79
let cases = config::transport_cases(500, true);
let selected: Vec<_> = cases
    .into_iter()
    .filter(|c| {
        ((c.kappa - 1.0).abs() < 0.01 && (c.gamma - 50.0).abs() < 0.01)
            || ((c.kappa - 2.0).abs() < 0.01 && (c.gamma - 100.0).abs() < 0.01)
            || ((c.kappa - 1.0).abs() < 0.01 && (c.gamma - 72.0).abs() < 0.01)
            || ((c.kappa - 2.0).abs() < 0.01 && (c.gamma - 31.0).abs() < 0.01)
            || ((c.kappa - 3.0).abs() < 0.01 && (c.gamma - 100.0).abs() < 0.01)
            || ((c.kappa - 2.0).abs() < 0.01 && (c.gamma - 158.0).abs() < 0.01)
    })
    .collect();
```

**Provenance:** `DALIGAULT_FIT_PROVENANCE` (commit `0a6405f`),
`TRANSPORT_MD_BASELINE_PROVENANCE` (commit `381fdb64`). See
`docs/BASELINE_PROVENANCE_CATALOG.md` Paper 5 rows.

**Action:** Profile which case dominates runtime. Consider splitting
into 2-case fast smoke (the original κ=1/Γ=50 and κ=2/Γ=100) vs
6-case nightly. If MD equilibration itself is the bottleneck, check
whether N=500 particle count can be reduced for smoke without losing
validation fidelity.

---

## Issue 3: DF64 NVK ΔH NaN Precision Frontier

**Severity:** Medium (blocks GPU HMC acceptance on Ampere+ consumer)
**Location:** `specs/CROSS_SPRING_EVOLUTION.md:331-337`

**Symptom:** RTX 3090 (NVK, DF64-compute) achieves correct quenched
thermalization (P=0.557 at β=6.0) but produces NaN ΔH in measurement
trajectories. The 48-bit mantissa of DF64 (vs 53-bit native f64) causes
the Metropolis accept/reject test to fail when comparing two large
Hamiltonians that differ by O(1).

**Key finding:** DF64 is sufficient for local observables (plaquette,
force) but insufficient for global energy-difference tests.

**Documented paths forward:**
1. Mixed-precision HMC: force/plaquette via DF64, kinetic energy +
   action accumulation via native f64 (Titan V as oracle)
2. Stochastic ΔH: accept/reject based on estimated ΔH variance
3. Proprietary driver: NVIDIA proprietary Vulkan supports full f64

**Action:** Decide precision policy for HMC accept/reject on DF64
hardware. Document whether mixed-precision is physics-safe for
production lattice runs.

---

## Issue 4: Baseline Coverage Gaps

**Severity:** Low (no failures, but validation confidence gaps)
**Source:** Deep debt sprint handoff (May 13, 2026)

| Gap | Description |
|-----|-------------|
| HotQCD EOS | Validated against published tables only — no independent Python control run |
| 3D Anderson | Possibly Rust-first implementation — no independent Python baseline for Kachkovskiy localization length |
| Hofstadter | Possibly Rust-first — butterfly symmetry validated against mathematical identities, not Python |
| DF64 NVK parity | No formal benchmark comparing DF64 vs native f64 across full validation suite |
| Tensor-core GEMM | Baseline pending coralReef HMMA (tensor-core GEMM via `mma.sync.aligned`) |

**Action:** Prioritize Python control runs for HotQCD and Anderson 3D.
DF64 parity benchmark should be a systematic comparison, not ad-hoc
per-binary checks.

---

## Issue 5: TensorSession Adoption (GAP-HS-007/027)

**Severity:** Low (performance, not correctness)
**Location:** `docs/PRIMAL_GAPS.md`, GAP-HS-007 and GAP-HS-027

**Description:** hotSpring uses `TensorContext` but not `TensorSession`
fused multi-op pipeline. Adopting TensorSession would enable fused GPU
dispatch for multi-step physics pipelines (HMC trajectory = leapfrog +
force + gauge update as single session). Relevant for heavy validation
runs where kernel launch overhead dominates.

**Status:** Upstream unblocked (barraCuda Sprint 66 shipped `sub`/`negate`).

**Action:** Wire TensorSession for the HMC trajectory loop when API
stabilizes for lattice workloads.

---

## Issue 6: Sarkas DSF Study Follow-up

**Severity:** Low
**Location:** `control/sarkas/simulations/dsf-study/results/all_observables_validation.json`

**Description:** Structural peak / compressibility analysis from the DSF
(dynamic structure factor) study was deferred to Strandgate. The Sarkas
MD control data exists but the structural analysis pipeline needs to be
completed for full Paper 5 coverage.

**Action:** Complete DSF structural analysis and integrate results into
the transport validation suite.

---

## Issue 7: Chuna Parity — Hot-Start Dynamical ΔH Context

**Severity:** Low (context for Item 1)
**Location:** `CHUNA_PARITY_STATUS.md`

**Description:** Chuna parity notes document that hot-start dynamical
trajectories produce |ΔH| blow-up without quenched warm-start. This is
relevant context for the dynamical QCD scaling failure (Item 1) — the
current test uses cold start, but the quenched pre-thermalization may
not be sufficient to stabilize the dynamical force term.

**Action:** Cross-reference with Item 1 diagnosis. Consider whether
longer quenched pre-thermalization or warm-start from a saved
configuration improves ΔH scaling.

---

## Cross-References

- `docs/BASELINE_PROVENANCE_CATALOG.md` — full binary-to-baseline mapping
- `docs/PRIMAL_GAPS.md` — GAP-HS-007/027 TensorSession
- `specs/CROSS_SPRING_EVOLUTION.md` — DF64 precision frontier
- `barracuda/src/provenance/` — machine-readable `BaselineProvenance` records
- `barracuda/src/tolerances/` — centralized validation tolerances
- `wateringHole/handoffs/HOTSPRING_DEEP_DEBT_SPRINT_MAY13_2026.md` — debt sprint
- `CHUNA_PARITY_STATUS.md` — hot-start dynamical ΔH analysis

## Team Ownership

| Domain | Owner | Scope |
|--------|-------|-------|
| Physics math, validation fidelity, Python baselines | Strandgate | Items 1-7 in this handoff |
| toadStool diesel engine, VFIO dispatch, FECS/PBDMA | biomeGate | GPU hardware bring-up |
| coralReef shader compilation | shared | Compilation correctness (coralReef), physics shaders (Strandgate) |
| hotSpring validation harness | shared | Infrastructure (biomeGate), physics checks (Strandgate) |
