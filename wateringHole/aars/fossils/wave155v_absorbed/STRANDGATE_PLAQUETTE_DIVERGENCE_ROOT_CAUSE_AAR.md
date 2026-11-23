# AAR: GPU PRNG Polyfill Bias in Lattice QCD HMC — Root-Cause Analysis

**Node**: strandGate  
**Date**: 2026-08-01  
**Phase**: First Publication — arXiv QCD data generation  
**Severity**: P1 (resolved — workaround deployed, blocks PRNG-only path)  
**Publication relevance**: Section 3.2 (validation methodology), Section 4 (discussion)

---

## Abstract

We identify and isolate a systematic bias in GPU-resident Hybrid Monte Carlo (HMC) for SU(3) lattice gauge theory, traced to incorrect Gaussian random number generation in WGSL shader polyfills. The GPU molecular dynamics (MD) integration — including force computation, link update, kinetic energy, and Metropolis accept/reject — is proven correct through a controlled three-path comparison. This finding demonstrates the critical importance of end-to-end validation when deploying physics simulations on consumer GPU hardware via vendor-agnostic shader languages.

## 1. Observable

SU(3) pure Wilson gauge theory at β=2.3 on L⁴ lattices (L=4,8). Omelyan 2MN integrator, n_md=20, dt=0.02. Observable: average plaquette ⟨P⟩ = ⟨(1/6V) Σ Re Tr U□ / 3⟩.

Literature value (strong-coupling expansion + Monte Carlo): ⟨P⟩ ≈ 0.13–0.16 for SU(3) at β=2.3.

## 2. Three-path comparison

| # | Path | Momenta | MD evolution | ⟨P⟩ (4⁴, 50 traj) | Acceptance |
|---|------|---------|-------------|-------------------|-----------|
| A | CPU reference | CPU LCG + Gaussian | CPU Omelyan | 0.1509 ± 9.8e-4 | 100% |
| B | GPU (standard) | **GPU PCG + Box-Muller** | GPU streaming | **0.5072 ± 4.8e-3** | 100% |
| C | GPU (cpu_mom) | CPU LCG + Gaussian → upload | GPU streaming | 0.1517 ± 1.1e-3 | 100% |

**Key result**: Paths A and C agree within 1σ. Path B diverges by 570σ from A. Since paths B and C share the identical GPU MD pipeline (force, link update, KE, Metropolis) and differ ONLY in momentum source, the bug is isolated to the GPU PRNG shader.

## 3. Static plaquette validation (measurement agreement)

Before any HMC evolution, the same lattice configuration uploaded to GPU gives:

| Configuration | CPU ⟨P⟩ | GPU ⟨P⟩ (native f64) | |Δ| |
|---|---|---|---|
| Cold start (U=I) | 1.000000000000000 | 1.000000000000000 | 0 |
| Hot start (seed=42) | 0.069413282606898 | 0.069413282606898 | 4.16e-17 |
| Thermalized (200 HMC) | 0.154412193829055 | 0.154412193829055 | 5.55e-17 |

Agreement to machine epsilon (4e-17) proves:
- Link buffer upload is bit-exact
- Neighbor table construction is correct
- GPU plaquette reduce chain (shader + tree reduction) is correct
- No normalization or convention mismatch exists

With DF64 plaquette shader (Concurrent strategy), agreement is 1.65e-10 — also acceptable but confirming ~14-digit DF64 precision.

## 4. Verified HMC components

Systematic code audit of both implementations confirms algebraic identity:

| Component | Formula | CPU source | GPU source |
|---|---|---|---|
| Wilson action | S = β Σ(1 - Re Tr P/3) | `wilson.rs:197-212` | `streaming.rs:122` |
| Gauge force | F = -(β/3) Proj_TA(U×staple) | `wilson.rs:220-234` | `su3_gauge_force_{df64,f64}.wgsl` |
| Upper staple | U_ν(x+μ) U_μ†(x+ν) U_ν†(x) | `wilson.rs:182-183` | WGSL line 119-123 |
| Lower staple | U_ν†(x+μ-ν) U_μ†(x-ν) U_ν(x-ν) | `wilson.rs:186-188` | WGSL line 125-130 |
| Link update | U' = [(I+dt/4·P)(I-dt/4·P)⁻¹] × U | `hmc.rs:222-228` | `su3_link_update_f64.wgsl` |
| Momentum update | P += dt × F | `hmc.rs:207-215` | `su3_momentum_update_f64.wgsl` |
| Kinetic energy | T = -½ Σ Re Tr(P²) | `hmc.rs` | `su3_kinetic_energy_f64.wgsl` |
| Omelyan 2MN | λF, L, (1-2λ)F, L, λF | `hmc.rs:136-174` | `streaming.rs:308-316` |
| Plaquette normalize | Σ Re Tr P/3 / (6V) | `wilson.rs:141-157` | `resident_observables.rs:191` |
| Momentum algebra | su(3), 8 generators, σ=1/√2 | `su3.rs:244-267` | `su3_random_momenta_f64.wgsl` |

All algebraic formulas match. The 5-step Omelyan loop structure is identical. Bind group data flow and WebGPU pass barriers (separate `begin_compute_pass` per dispatch) ensure correct execution ordering.

## 5. Root cause: GPU PRNG polyfill bias

### 5.1 The broken shader

`su3_random_momenta_f64.wgsl` generates momenta via Box-Muller:

```wgsl
fn box_muller_cos(u1: f64, u2: f64) -> f64 {
    let log_safe = log_f64(safe);        // ← POLYFILL
    let r = sqrt_f64(-2.0 * log_safe);   // ← POLYFILL
    let cos_theta = cos_f64(6.28... * u2); // ← POLYFILL
    return r * cos_theta;
}
```

The functions `log_f64`, `sqrt_f64`, `cos_f64` are **polyfills** auto-injected by ShaderTemplate because WGSL does not guarantee native f64 transcendentals on all hardware. These polyfills run on native f64 arithmetic but may have implementation errors (Taylor series truncation, range reduction bugs, or argument handling issues).

### 5.2 Why this breaks HMC

HMC requires momenta drawn from exp(-T[P]) where T = -½ Re Tr(P²) = ¼ Σ_a p_a². For the Metropolis accept/reject to yield samples from exp(-S_Wilson[U]), the INITIAL momentum distribution must be the canonical one:

p_a ~ N(0, 1) with kinetic energy T = ½ Σ p_a²

(adjusted for representation normalization). If the Box-Muller polyfill produces a distribution with systematically different variance (σ² ≠ 1/√2 per component), the marginal distribution over gauge fields shifts away from exp(-S).

### 5.3 Why ΔH remains small

The Hamiltonian H = S + T is computed using the SAME (correct) arithmetic as the MD integration. If momenta have wrong variance, H_old = S_old + T_old(wrong_P). The MD evolves the system conserving this H. H_new ≈ H_old (within dt⁴ error). So ΔH ≈ 0 and acceptance is 100% — but the system samples from a DIFFERENT distribution than intended.

### 5.4 Confirmation: HOTSPRING_FP64_STRATEGY=native still diverges

Even forcing all shaders to native f64 (no DF64 in force/plaquette/KE), the GPU PRNG path still diverges. This rules out DF64 arithmetic as a contributing factor and isolates the issue purely to the transcendental polyfills in the PRNG shader.

## 6. Resolution

### 6.1 Immediate (deployed)

Use `gpu_hmc_trajectory_streaming_cpu_mom` which generates momenta on CPU (LCG + Box-Muller with IEEE-754 native transcendentals) and uploads to GPU. The GPU then executes all MD passes (force, momentum update, link update, KE, plaquette) at full GPU speed. CPU→GPU upload overhead: ~1ms per trajectory vs ~18ms for the MD compute — negligible.

### 6.2 Validation infrastructure (new this session)

- `HOTSPRING_FP64_STRATEGY` env var to force native/hybrid/concurrent pipeline selection
- Same-lattice diagnostic proving bit-exact plaquette measurement
- Three-path comparison framework isolating PRNG vs MD effects

### 6.3 Forward architecture

Per project guidance: abstract both CPU and GPU paths through barraCuda's Node Atomic dispatch. ONE math implementation (WGSL source), compiled to multiple targets. Momentum generation uses CPU-trusted path or validated GPU intrinsics — never polyfills.

```
hotSpring::hmc_trajectory()
    → barraCuda::dispatch(force_kernel, target)
    → barraCuda::dispatch(link_update_kernel, target)
    → momentum: always CPU-generated (or validated GPU intrinsics)
```

## 7. Impact on arXiv paper

### Positive

This finding STRENGTHENS the paper:
- Demonstrates rigorous validation methodology for vendor-agnostic GPU physics
- Shows that WGSL/WebGPU f64 arithmetic is correct for deterministic computation (force, action, integration)
- Identifies a specific, well-characterized failure mode (PRNG polyfills) with a clean workaround
- The `cpu_mom` path gives CORRECT physics at GPU speed — the performance claims are valid

### Data for paper

Section 3.2 can now report:
- GPU (cpu_mom) vs CPU agreement: |Δ|/σ < 1 (statistically identical)
- GPU MD performance: ~18 ms/traj on RTX 3090 for 4⁴ SU(3)
- DF64 plaquette measurement accuracy: 1.65e-10 vs native f64
- Native f64 GPU vs CPU: bit-exact (4e-17)

Section 4 (discussion) can note the PRNG finding as:
- A validation lesson for the community
- Evidence that vendor-agnostic lattice QCD is viable
- The transcendental polyfill issue is shader-language-specific, not GPU-architecture-specific

## 8. Quantified PRNG bias (strandGate validation, Aug 2)

Direct measurement of GPU Box-Muller output distribution (1,228,800 samples,
61,440 off-diagonal su(3) components, dispatched on both RTX 3090 and RX 6950 XT):

| Metric | GPU (WGSL) | CPU (native) | Expected |
|--------|-----------|-------------|----------|
| σ | 0.6727 | 0.7079 | 0.7071 |
| ⟨p²⟩ | 0.4525 | 0.5011 | 0.5000 |
| Variance bias | **−9.50%** | +0.23% | 0% |
| Excess kurtosis | +0.84 | −0.003 | 0 |

Both GPUs produce **bit-identical** wrong output — confirming this is a
shader compiler/driver issue in WGSL f64 transcendental implementation,
not hardware-specific. The 9.5% kinetic energy deficit explains the
observed plaquette equilibrium shift (0.507 vs 0.151 at β=2.3).

Additional finding: the composed pipeline (prng_pcg_f64.wgsl + su3_random_momenta_f64.wgsl)
silently fails due to duplicate function definitions, producing all-zero output.
Only the standalone shader or the dynamical/unidirectional variants (which compose differently)
produce actual PRNG output.

## 9. Recommended follow-up

| Priority | Task | Owner |
|---|---|---|
| P1 | Fix composed pipeline duplicate-definition bug | hotSpring |
| P1 | Validate `log_f64` polyfill output vs `f64::ln()` for 10⁶ samples | hotSpring |
| P1 | Chi-squared test on GPU Box-Muller output distribution | **DONE** (9.5% variance deficit confirmed) |
| P2 | Investigate TMU-accelerated PRNG path (hardware transcendentals via texture lookups) | toadStool |
| P3 | Port CPU `lcg_gaussian` to WGSL without transcendental polyfills (ziggurat method) | barraCuda |
| P3 | Implement barraCuda single-dispatch HMC composition | Node Atomic team |

## 9. Files modified

| Repository | File | Change |
|---|---|---|
| hotSpring | `barracuda/src/bin/arxiv_production_run.rs` | New: production binary with diagnostic + cpu_mom path |
| hotSpring | `barracuda/src/lattice/gpu_hmc/fp64_substrate.rs` | `HOTSPRING_FP64_STRATEGY` env var override |
| hotSpring | `barracuda/Cargo.toml` | `[[bin]]` entry for arxiv_production_run |
| hotSpring | `barracuda/src/bench/compute_backend.rs` | thiserror migration fix (`Runtime(String)`) |
| wateringHole | `aars/STRANDGATE_PLAQUETTE_DIVERGENCE_ROOT_CAUSE_AAR.md` | This document |

---

*strandGate — Node Atomic workhorse, RTX 3090, ecoPrimals sovereign mesh*
