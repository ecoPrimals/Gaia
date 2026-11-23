# FRAGO: coralReef — Sovereign Compute Cascade

**From:** hotSpring (Exp 234 pipeline validation)
**To:** coralReef team
**Priority:** P0/P1 mix
**Date:** June 1, 2026
**Type:** Fragmentary Order — evolution targets for next cascade

---

## Context

hotSpring validated the full sovereign compute pipeline (coralReef compile →
toadStool dispatch → VFIO bare-metal → readback) on Titan V GPUs. coralReef
is performing well as the shader compiler — WGSL → SPIR-V compilation works
for all standard shaders. Two issues surfaced that need coralReef evolution.

## P0: opt_copy_prop crash on subgroupAdd

**GAP-CR-002 / GAP-HS confirmed**

`sum_reduce_subgroup_f64.wgsl` crashes coralReef with:

```
assertion failed: entry_ssa.comps() == 1
location: crates/coral-reef/src/codegen/opt_copy_prop/mod.rs:142:21
```

This kills the coralReef process entirely — no graceful error return. The panic
propagates through the JSON-RPC handler and terminates the daemon.

**Repro:** Send any WGSL containing `subgroupAdd()` to `shader.compile.wgsl`
with `optimize: true`.

**Impact:** All subgroup-accelerated reductions (a performance-critical path for
lattice QCD and MD simulations) must fall back to wgpu or use manual tree
reduction. This blocks barraCuda's optimized shader library from using coralReef.

**Ask:** Fix or guard the assertion in `opt_copy_prop/mod.rs:142`. A graceful
fallback (skip the optimization pass, return unoptimized SPIR-V) would unblock
downstream immediately.

## P1: sm_120 (Blackwell) codegen target

**GAP-HS-122**

All compilations return `target: sm_70` regardless of requested architecture.
The RTX 5060 (Blackwell, sm_120) runs sm_70 code via compatibility mode, but
native codegen would be optimal.

hotSpring confirmed Blackwell wgpu compute works (256/256 exact match) — the
silicon is capable. coralReef just needs the codegen target.

**Ask:** Add sm_120 target to the codegen pipeline. If sm_120 is non-trivial,
document which sm targets are supported so downstream can make informed
dispatch decisions.

## P2: f64 pow() WGSL extension

hotSpring's `deformed_wavefunction_f64.wgsl` used `pow()` on f64 types, which
coralReef correctly rejects (not in WGSL spec). We rewrote to integer-power
loop locally. If f64 transcendentals are a common need, consider a coralReef
extension or intrinsic.

## plasmidBin deployment note

The NUCLEUS launcher (`nucleus_launcher.sh`) works for standing up the primal
stack. Socket management has some quirks (circular symlinks if sockets pre-exist).
These are documented in:
- `hotSpring/HOTSPRING_NUCLEUS_DEPLOYMENT_LESSONS_JUN01_2026.md`

This is NOT blocking — do not gate evolution on deployment issues. Focus on the
codegen fixes above.

---

**Handback:** `docs/PRIMAL_GAPS.md` GAP-HS-122, plus `HOTSPRING_PIPELINE_INTELLIGENCE_JUN01_2026.md`
