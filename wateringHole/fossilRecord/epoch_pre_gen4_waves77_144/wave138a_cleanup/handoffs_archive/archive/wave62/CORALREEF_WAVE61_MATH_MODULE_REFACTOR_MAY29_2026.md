# coralReef — Wave 61: Math Completeness & Module Refactor

**Date**: 2026-05-29  
**Commit**: `b8dd3d8`  
**Tests**: 3234 passing (was 3222)

---

## Completed

### New Math Functions (9 total)
| Function | PTX Strategy |
|----------|-------------|
| `tan` | `sin.approx` / `cos.approx` → `div.rn` |
| `atan` | Polynomial approx: `x / (1 + 0.28125·x²)` via `fma` + `div` |
| `atan2` | `div.rn(y,x)` → atan polynomial |
| `asin` | rsqrt-scaled → atan polynomial |
| `acos` | π/2 − asin(x) |
| `reflect` | `I − 2·dot(N,I)·N` via `fma` + `sub` |
| `faceForward` | `setp.lt.f32` + `selp.f32` conditional negate |
| `extractBits` | PTX native `bfe.u32` |
| `insertBits` | PTX native `bfi.b32` |

### Texture Query Routing
- `eval_image_query` now tries texture bindings first (`txq.*`), falls back to surfaces (`suq.*`)
- `textureNumLevels` → `txq.num_mip_levels.b32`
- `textureDimensions` (texture) → `txq.width/height/depth.b32`
- `textureNumLayers` (texture) → `txq.array_size.b32`

### Module Refactoring (1000-line compliance)
| File | Before | After |
|------|--------|-------|
| `ptx_emit/mod.rs` | 1814 | 143 |
| `ptx_emit/math.rs` | 1296 | 655 |
| New: `ptx_emit/math_ext.rs` | — | 651 |
| New: `ptx_emit/tests_core.rs` | — | 451 |
| New: `ptx_emit/tests_image.rs` | — | 787 |
| New: `ptx_emit/tests_math_ext.rs` | — | 494 |

### Dependency Hygiene
- All transitive deps bumped to latest compatible patches (19 updates)
- Zero C/C++ deps, zero `*-sys` crates, zero `unsafe`

---

## Remaining `NotImplemented` (Defensive)
All remaining `NotImplemented` returns are:
- **Defensive guards** for impossible states in valid IR (non-global image pointers, break outside loop)
- **Hardware limitations** (subgroup multiply reduction — no PTX `redux.mul`)
- **Non-compute features** (task payload, vertex/fragment builtins)
- **Catch-all** for unimplemented naga math funcs (Modf, Frexp, Ldexp, Outer, Refract, Transpose, Determinant, Inverse, data packing)

None block production WGSL compute shader compilation.

---

## Signals for `primalSpring`
- `clippy::pedantic` + `clippy::nursery`: ZERO warnings
- All files < 1000 lines
- Test count: 3234
- Zero `/tmp` writes (DH-1 completed prior commit)
