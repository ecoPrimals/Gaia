# coralReef — Wave 53 Mountain Status Ack

**Date**: May 26, 2026
**Primal**: coralReef
**Version**: 0.2.0 — Sprint 13
**Tests**: 3209 passing (was 3204), 0 failed
**From**: Sprint 12 / Wave 49
**To**: Sprint 13 / Wave 53

---

## Wave 53 Guidance Addressed

### Depth texture comparison PTX — DONE

- Fixed broken stub: old code evaluated `depth_ref` but never used it,
  emitting standard `tex.2d.v4.f32.f32` (wrong)
- Now emits correct `tex.level.compare.{dim}.f32.f32` with:
  - Reference value appended to coordinate tuple per PTX ISA convention
  - Scalar f32 return (0.0 or 1.0) instead of v4
  - LOD level support (Auto/Zero/Exact)
- New test: `ptx_depth_compare_sample_2d` asserts `tex.level.compare.2d.f32.f32`

### Array/cube texture support — DONE

- Extended `ImageDim` enum: added `Cube`, `A1d`, `A2d`, `Acube` with proper
  PTX suffixes and `coord_components()` / `is_arrayed()` methods
- Fixed `collect_textures()` to read naga's `arrayed` flag and map correctly
  (`(D2, true)` → `A2d`, `(Cube, false)` → `Cube`, etc.)
- Wired `array_index` through `eval_image_sample` (was discarded as `_`)
- Updated `format_tex_coord` to prepend layer index for arrayed dimensions
- New tests: `ptx_image_sample_2d_array` (asserts `tex.level.a2d`),
  `ptx_image_sample_cube` (asserts `tex.level.cube`)

### Live toadStool discovery integration tests — DONE

- `live_discovery_toadstool_gpu_target_to_compile`: simulates toadStool
  publishing a discovery JSON with 2 GPU devices (nvidia/sm86 + amd/rdna2),
  verifies coralReef discovers both, then compiles a shader for the discovered
  architecture (sm86 → SASS binary produced)
- `live_discovery_mixed_primals_only_gpu_resolved`: multiple primals in
  discovery dir (toadStool + bearDog + nestGate), verifies only GPU
  capabilities are resolved

### Coverage push — IN PROGRESS

- 5 new tests added this sprint (3209 total)
- PTX emitter submodules and optimizer passes remain the biggest gaps
- `coral-reef` crate at ~83% → ongoing incremental push to 90%

---

## Remaining Wave 53 Items (Low Priority / Incremental)

| Item | Status | Notes |
|------|--------|-------|
| Sampled texture load (`tld.*`) | Deferred Sprint 14 | Non-blocking; storage surfaces work |
| `ImageQuery::NumLayers` | Deferred Sprint 14 | Returns `NotImplemented` currently |
| Storage array surfaces | Deferred Sprint 14 | `sust.b.a2d` coord needs layer prepend |
| PTX `normalize()` | Enhancement | Blocks cube map usage with unit vectors |
| 90% coverage target | Ongoing | ~83% → need optimizer/RA test expansion |

---

## State Summary

| Category | Status |
|----------|--------|
| Unsafe code | Zero |
| TODO/FIXME/HACK | Zero |
| Clippy warnings | Zero |
| Debt | Zero |
| Stale files | None |
| Blocked on external | None |
