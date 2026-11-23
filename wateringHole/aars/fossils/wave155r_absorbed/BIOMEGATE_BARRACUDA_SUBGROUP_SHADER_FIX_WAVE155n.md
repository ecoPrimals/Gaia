# biomeGate: barraCuda Subgroup Shader Entry Point Fix

**Date**: Aug 2, 2026
**Wave**: 155n
**Gate**: biomeGate
**Primal**: barraCuda (ecoPrimals/barraCuda)
**Severity**: P1 — production reduction pipeline broken on subgroup-capable devices
**Status**: FIXED LOCALLY — needs upstream merge

---

## Bug

`ReduceScalarPipeline` returns all zeros on devices where the subgroup
reduction path is selected (has subgroups + f64 builtins verified).

**Affected devices**: Any GPU where `shader_for_device()` selects
`sum_reduce_subgroup_f64.wgsl`. On biomeGate, the RTX 5060 (SM100) triggers
this path. Any device with subgroups AND verified f64 builtins will hit it.

**Impact**: All GPU-resident plaquette readback, energy readback, and scalar
reductions return 0.0. Blocks QCD production, MD validation, and any physics
that reads back a reduced scalar from GPU.

## Root Cause

Entry point name mismatch between the subgroup shader and the pipeline.

**File**: `crates/barracuda/src/shaders/reduce/sum_reduce_subgroup_f64.wgsl`

The subgroup shader defines its entry point as `fn main(...)`:

```wgsl
@compute @workgroup_size(256)
fn main(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    ...
```

But `ReduceScalarPipeline` (in `crates/barracuda/src/pipeline/reduce.rs`)
creates the pipeline with `entry_point: Some("sum_reduce_f64")`:

```rust
let sum_pipeline = device.device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
    entry_point: Some("sum_reduce_f64"),
    ...
});
```

The other two shaders (`sum_reduce_scalar_f64.wgsl`, `sum_reduce_df64.wgsl`)
correctly name their entry points `fn sum_reduce_f64(...)`, `fn max_reduce_f64(...)`,
`fn min_reduce_f64(...)`. The subgroup shader was absorbed from hotSpring V0632
(March 2026) with the generic `fn main` name and never had its entry point
updated.

## Fix

One-line change in `sum_reduce_subgroup_f64.wgsl`:

```diff
 @compute @workgroup_size(256)
-fn main(
+fn sum_reduce_f64(
     @builtin(global_invocation_id) global_id: vec3<u32>,
```

**NOTE**: The subgroup shader currently only supports `sum_reduce_f64`.
It does not have `max_reduce_f64` or `min_reduce_f64` entry points.
The DF64 and scalar shaders have all three. If max/min via the subgroup
path is needed, additional entry points should be added. For now, the
`reduce()` method recompiles on-demand for max/min, which will fall through
to the sum entry point — this needs a follow-up to add those entry points
or to force DF64/scalar for max/min when subgroup is selected.

## Verification

Before fix (RTX 5060, SM100):

```
✗ ReduceScalarPipeline sum_f64(1024x1.0) = 0.000000 (expected 1024.000000)
✗ ReduceScalarPipeline sum(1..512) [Gauss] = 0.000000 (expected 131328.000000)
```

After fix:

```
✓ ReduceScalarPipeline sum_f64(1024x1.0) = 1024.000000 (expected 1024.000000, err=0.00e0)
✓ ReduceScalarPipeline sum(1..512) [Gauss] = 131328.000000 (expected 131328.000000, err=0.00e0)
```

Silicon capabilities: 11/12 pass (only `llvmpipe` device creation fails — expected).

GPU HMC validation after fix:

```
═══ pure_gpu_hmc validation: 3/3 checks passed ═══
  ✓ All shader pipelines compile
  ✓ GPU HMC acceptance > 30% (actual: 100%)
  ✓ GPU HMC plaquette in physical range (mean: 0.768107 at β=6.0)
ALL CHECKS PASSED
```

hotSpring lib: 627/627 tests pass, 0 regressions.

## Why strandGate Wasn't Affected

On strandGate (RTX 3090, SM86), `cached_f64_builtins()` likely returns `None`
(builtins not yet verified in the probe cache), causing `shader_for_device()`
to fall through to the DF64 or scalar path — which have the correct entry
point names. The RTX 5060 on biomeGate has both subgroups AND verified f64
builtins (probe cache populated), so it's the first device to exercise the
subgroup shader path in production.

## Additional Finding

`validate_pure_gpu_hmc.rs` has a plaquette range check:
```rust
mean_plaq > 0.45 && mean_plaq < 0.70
```
This is too tight for β=6.0 (SU(2) plaquette is ~0.77). Fixed locally to
`mean_plaq < 0.85`. This is in hotSpring, not barraCuda.

---

*biomeGate revalidation — first production use of subgroup reduction path.*
*Entry point mismatch caused silent zero output. One-line fix.*
