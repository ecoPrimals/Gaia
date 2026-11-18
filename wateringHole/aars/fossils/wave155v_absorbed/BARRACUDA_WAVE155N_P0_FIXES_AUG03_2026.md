# barraCuda Wave 155n — P0 Shader Fixes + Doc Refresh

**Date**: Aug 3, 2026
**Gate**: eastGate
**Wave**: 155n
**Primal**: barraCuda
**Commit**: b315eec9 (shader fixes), pending (doc refresh)

---

## Summary

Three P0 items from the Wave 155n primal infrastructure blurb addressed.
Root docs refreshed with ground-truth metrics post-remote integration.

## P0 Items Completed

### P0 #1 — Subgroup Reduction Entry Point (S) — FIXED

`sum_reduce_subgroup_f64.wgsl` had `fn main()` but Rust dispatches
`entry_point: "sum_reduce_f64"`. Pipeline creation silently failed on SM100+
(Blackwell), returning **0.0** for all GPU scalar readbacks.

**Fix**: Renamed entry point to `fn sum_reduce_f64()`. One-line change.
**Impact**: Unblocks hotSpring QCD production on biomeGate, G32 cross-vendor.

### P0 #2 — GPU PRNG Pipeline (L) — ANALYZED

Active HMC path uses `lcg_f64.wgsl` → `prng_gaussian()` → native sqrt/log/cos,
polyfilled on NVIDIA via `compile_shader_f64`. Polyfill injection and
duplicate-definition guards are sound.

9.5% KE deficit is likely a measurement artifact from the broken subgroup
reduction (P0 #1) — fixing the readback may resolve it.

`cpu_mom` workaround remains deployed. Full GPU PRNG fix is Week 3+ item.

**Bonus**: Fixed `diversity_f64.wgsl` self-recursion bug — inline `log_f64()`
caused infinite recursion when transcendental workaround rewrites body's
`log()` → `log_f64()`.

### P0 #3 — Gauge Group Labeling (M) — NO CODE CHANGES

barraCuda code is correctly SU(3) throughout (zero SU(2) references).
6 docs disambiguated from "lattice QCD" → "SU(3) lattice QCD".
SU(2) mislabel is in external paper/site artifacts.

## Metrics Reconciliation

| Metric | Previous (docs) | Ground Truth | Delta |
|--------|----------------|--------------|-------|
| Tests | 4,959 | **5,037** | +78 |
| Shaders | 860 | **859** | −1 |
| Rust files | 1,213 | **1,208** | −5 |
| Integration tests | 49 | 49 | — |

Per-crate: barracuda 4,249, barracuda-core 772, naga-exec 16.

## Deep Debt Audit (re-confirmed clean)

| Axis | Status |
|------|--------|
| Files >800L | **0** |
| `#[allow]` | **0** |
| `unsafe` (prod) | **1** (barracuda-spirv, annotated) |
| TODO/FIXME | **0** |
| C/FFI deps | **0** |
| Clippy (incl. pedantic) | **0 warnings** |
| Production mocks | **0** |
| Hardcoded primals | **0** |
| Empty dirs / temp files | **0** |

## For Upstream

- P0 #1 (subgroup fix) unblocks hotSpring GPU readbacks on SM100+
- P0 #2 KE deficit should be re-tested with the subgroup fix merged
- P0 #3 gauge group: paper/site SU(2)→SU(3) correction is NOT in barraCuda scope
- barraCuda remains YELLOW until PRNG pipeline is fully validated (Week 3+)
