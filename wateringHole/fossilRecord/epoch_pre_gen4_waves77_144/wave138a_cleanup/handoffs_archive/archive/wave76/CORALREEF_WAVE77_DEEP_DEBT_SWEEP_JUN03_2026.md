<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# coralReef — Wave 77: Deep Debt Sweep & Full Audit

**Gate**: strandGate  
**Date**: June 3, 2026  
**Type**: Deep debt / hygiene / structural evolution  

---

## Summary

Comprehensive deep debt sweep across the `coralReef` codebase. Smart
refactoring of the last two production files over 800 lines, plus a
full-spectrum audit validating the codebase against all primal standards.

## Changes

### Smart Refactoring

| File | Before | After | Extraction |
|------|--------|-------|-----------|
| `ptx_emit/expr_eval.rs` | 834L | 340L | → `expr_image.rs` (492L) |
| `ptx_emit/math.rs` | 809L | 646L | → `math_ext_trig.rs` (+164L) |

**`expr_image.rs`** — Cohesive PTX image/texture/surface evaluation:
- `eval_image_load`, `eval_surface_load`, `eval_texture_load`
- `eval_image_sample`, `eval_depth_compare_sample`
- `eval_texture_gather`, `eval_image_query`, `eval_texture_query`
- `format_tex_coord`, `format_depth_compare_coord`

**`math_ext_trig.rs`** — Consolidated hyperbolic functions:
- `Tanh` (ex2 approximation identity: `1 - 2/(exp(2x)+1)`)
- `Sinh` (`(exp(x) - exp(-x))/2` via ex2.approx)
- `Cosh` (`(exp(x) + exp(-x))/2` via ex2.approx)

### Full Audit (all clean)

| Category | Status | Detail |
|----------|--------|--------|
| Unsafe code | CLEAN | All in test files only (env var mutation, Rust 1.85+). All prod crates `#![forbid(unsafe_code)]` |
| External deps | CLEAN | 100% pure Rust. Zero C/C++, zero `*-sys`, zero openssl/ring |
| Hardcoded values | CLEAN | 3-tier resolution (env → XDG → fallback). Zero primal name coupling |
| Production mocks | CLEAN | None found. `coral-reef-stubs` is legitimate compiler IR |
| NotImplemented stubs | CLEAN | All are architecture boundaries or defensive error paths |
| `.unwrap()` in prod | CLEAN | Zero. All in `#[cfg(test)]` modules only |
| Files >800L (prod) | CLEAN | Zero after this wave |

## Metrics

- **3303 tests**, 0 failures
- **0 clippy warnings** (pedantic + nursery)
- **0 unsafe blocks** in production
- **0 production files** over 800 lines
- All dependencies pure Rust

## Remaining Gaps (upstream)

| Gap | Owner | Status |
|-----|-------|--------|
| GAP-HS-124: IR-to-SPIR-V emitter (beyond naga wrapper) | coralReef | Future — naga backend sufficient for current needs |
| SM120 hardware validation | biomeGate | Blocked on hardware recovery |
| `capability.call` cross-gate testing | Songbird + mesh | Awaiting eastGate rebuild |

## Upstream Asks

None. This was a self-contained hygiene pass. Downstream consumers
are unaffected — wire protocol and capability metadata unchanged.

---

*Filed by strandGate coralReef team, Wave 77.*
