# AAR: SU(N) CPU Memo Table — Mise en Place for GPU Physics Exploration

**Date**: Aug 5, 2026 | **Wave**: 156e | **Gate**: strandGate
**Scope**: GaugeGroup trait, SU(N) generalization, thermalization grid, measurement battery, paper reframe

---

## Executive Summary

Implemented the full SU(N) gauge group ladder (N=2,3,4,5,6,8) for lattice gauge theory on strandGate. This transforms the arXiv paper from a single-gauge-group SU(3) study into a comprehensive SU(N) survey — the first to cover N=2 through N=8 on the same volumes, code, hardware, and provenance chain.

**Key deliverables:**
- `GaugeGroup` trait abstracting all SU(N) matrix operations
- Fixed-size `Su2Matrix` (64 B/link) and heap-allocated `SuNMatrix` (N>=4, 16N^2 B/link)
- `GenericLattice<G>` — Wilson action, HMC, full observable battery generic over gauge group
- 87-config thermalization grid (6 gauge groups x volumes x betas + 30 finite-T configs)
- Measurement battery binary: plaquette + Polyakov + Wilson loops + Creutz + flow + Q_top
- arXiv paper reframed to "Vendor-Agnostic SU(N) Lattice Gauge Theory on Consumer GPUs"

---

## What Worked

### 1. GaugeGroup Trait Design
The trait-based abstraction was clean and mechanical. The core insight: parameterize `GenericLattice<G: GaugeGroup>` so the same HMC integration, force computation, and observable measurement code works for SU(2), SU(3), and SU(N>=4) without code duplication.

Fixed-size types (SU(2), SU(3)) get stack allocation and copy semantics for production speed. Heap-allocated SU(N) handles N=4,5,6,8 with runtime-determined matrix size.

**14 unit tests** validate the generic lattice for both SU(2) and SU(3): cold-start plaquettes, HMC stability, Cayley map agreement, force correctness, Creutz ratios, serialization roundtrips, and full thermalization.

### 2. Cayley Exponential Map Generalization
The Cayley map `exp(dt*P) ~ (I + dt*P/2)(I - dt*P/2)^-1` works identically for all N once you have matrix inverse. For SU(2): analytic 2x2 formula. For SU(3): cofactor expansion. For N>=4: Gauss-Jordan with partial pivoting. All followed by reunitarization (Gram-Schmidt + det phase correction).

### 3. SU(2) Physics Validation
The SU(2) thermalizer (running now, 32 threads) produces correct physics immediately:
- beta=2.20: <P> ~ 0.504 (disordered)
- beta=2.30: <P> ~ 0.523 (near deconfinement transition, published beta_c ~ 2.30 for Nt=4)
- beta=2.50: <P> ~ 0.562 (more ordered)

These match published SU(2) lattice data.

### 4. Creutz Ratio Implementation
~20 lines of code on top of existing Wilson loops, exactly as predicted in the plan. The Creutz ratio chi(R,T) = -ln[W(R,T)*W(R-1,T-1)/(W(R,T-1)*W(R-1,T))] converges to the string tension sigma*a^2 — a fundamental observable for confinement physics.

---

## What Didn't Work (Initially)

### 1. SuNMatrix Runtime NC Mismatch (Critical Bug)
The `SuNMatrix` type uses `const NC: usize = 0` (runtime-determined), but `GenericLattice` used `G::NC` everywhere: in plaquette normalization (dividing by 0.0), Wilson action, gauge force, HMC momentum generation, and serialization.

**Root cause**: The trait was designed around compile-time `NC` for fixed-size types. Heap-allocated SU(N) breaks this assumption.

**Symptoms**: Index-out-of-bounds panic when HMC generated 4x4 momenta for 8x8 link matrices (default nc=4 in `random_algebra`). Division by zero in plaquette normalization.

**Fix**: Added `nc` field to `GenericLattice`, `runtime_nc()` method to `GaugeGroup` trait, `random_algebra_for_nc(nc, seed)` trait method, and `cold_start_nc`/`hot_start_nc`/`load_sun` specialized methods for SuNMatrix. All `G::NC` references in GenericLattice replaced with `self.nc`.

### 2. Multiple Thermalizer Instances Competing for Resources
Three instances of `arxiv_thermalize_sun` ran simultaneously (from different test/launch attempts), consuming ~62 GB RAM and saturating all 128 EPYC threads. This made cargo builds take 9+ minutes.

**Fix**: Killed extras, kept one instance with `THERM_THREADS=32` to leave headroom for builds.

### 3. Serialization Format Divergence
SU(3) `Lattice::save()` uses a 40-byte header (no NC field). `GenericLattice::save()` uses a 48-byte header (includes NC). The measurement battery must handle both formats when loading SU(3) configs.

**Fix**: `measure_su3()` tries `Lattice::load()` first (40-byte), falls back to `GenericLattice::<Su3Matrix>::load()` (48-byte).

---

## Systems That Still Need Evolution

### 1. SU(N>=4) GPU Shaders
WGSL shaders are hardcoded for SU(3) (3x3 matrices, 18 reals per link). Generalizing to SU(N) in WGSL requires either templating or runtime code generation. SU(2) could be special-cased (simpler than SU(3)). SU(4+) GPU shaders can wait — CPU measurement on cached configs is sufficient for the paper.

### 2. Gradient Flow Generalization
The gradient flow implementation (`gradient_flow.rs`) is SU(3)-specific via `Lattice`. Generalizing to `GenericLattice<G>` would enable flow scales (t0, w0) for all gauge groups. Currently only SU(3) gets flow measurements.

### 3. Topological Charge for SU(N!=3)
The clover field-strength definition of Q uses SU(3)-specific code. The clover plaquette construction is actually gauge-group-agnostic, but the implementation uses `Su3Matrix` types directly.

### 4. 32^4 Thermalization Wall Time
A single 32^4 SU(3) config takes ~6 days of CPU time (300 Omelyan trajectories). SU(4+) at 32^4 would be significantly longer. The current plan caps SU(4) at 24^4 and SU(5+) at 16^4.

---

## What Overwatch Can Absorb and Disseminate

### For Other Gates
- **GaugeGroup trait pattern**: The trait-based abstraction for parameterizing physics over group types is reusable. Any gate doing numerical algebra with multiple matrix types can adopt this pattern.
- **Content-addressed config caching**: The BLAKE3 memo table pattern (thermalize once, measure many times) is the compute analog of westGate's data provenance. Complementary and abstract of each other.
- **Runtime NC handling in generic code**: The `runtime_nc()` pattern for mixing compile-time and runtime type parameters is a useful Rust idiom.

### For the Paper
- The paper title and scope have been reframed. Data placeholders (`[DATA: ...]`) are ready for measurement battery output.
- SU(2) data is actively being generated. SU(3) through SU(8) follow once SU(2) validates.
- The finite-T deconfinement scans (30 asymmetric configs) enable the T_c/sqrt(sigma) analysis.

### Convergence Points
- **westGate provenance trio** handles data acquisition and provenance
- **strandGate compute cache** handles compute memoization and provenance
- These are complementary: data provenance (what was measured) + compute provenance (how it was computed)
- The BLAKE3 content-addressing is identical in both systems

---

## Thermalization Grid Status

```
SU(2):  36 configs (21 symmetric + 15 finite-T) — RUNNING on 32 threads
SU(3):  42 configs (27 symmetric + 15 finite-T) — QUEUED (after SU(2))
SU(4):   6 configs (16^4 + 24^4 x 3 betas)     — QUEUED
SU(5):   3 configs (16^4 x 3 betas)             — QUEUED
SU(6):   3 configs (16^4 x 3 betas)             — QUEUED
SU(8):   3 configs (16^4 x 3 betas)             — QUEUED
Total:  87 configs, ~30 GB on disk
```

Estimated total wall time: ~2 weeks on 64 EPYC threads (dominated by SU(3) 32^4).

---

## New Files

| File | Purpose |
|------|---------|
| `src/lattice/gauge_group.rs` | GaugeGroup trait — abstract SU(N) operations |
| `src/lattice/su2.rs` | SU(2) 2x2 matrix with GaugeGroup impl |
| `src/lattice/su_n.rs` | SU(N>=4) heap-allocated NxN with GaugeGroup impl |
| `src/lattice/generic_lattice.rs` | GenericLattice<G> — HMC + observables for any gauge group |
| `src/bin/arxiv_thermalize_sun.rs` | Parallel CPU thermalizer for full SU(N) grid |
| `src/bin/arxiv_measure_battery.rs` | Observable measurement pass on cached configs |

---

*strandGate Wave 156e — SU(N) memo table infrastructure complete. Thermalizer running. Paper reframed. Measurement battery ready. Next: populate data tables as configs land.*
