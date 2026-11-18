<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 157i: Proactive File Split + EVOLUTION Assessment

**Date**: Aug 10, 2026
**Primal**: coralReef (GPU compiler)
**Wave**: 157i
**Author**: coralReef on strandGate

---

## Summary

Proactive code-size compliance split, EVOLUTION marker re-assessment, and
hygiene pass. No functional changes.

## Changes

### Proactive File Split: sm20/encoder.rs (795 → 343 + 464 LOC)

`encoder.rs` was 795 LOC, approaching the 800 LOC threshold. Split into:

- **`encoder.rs`** (343 LOC): `ShaderModel20` struct, `ShaderModel` trait impl,
  `KeplerInstructionEncoder` impl, `AluSrc`/`SM20Unit`/`SM20Op` types, dispatch macro.
- **`encoder_fields.rs`** (464 LOC): All `impl SM20Encoder<'_>` bit-field packing
  methods (`set_opcode`, `set_pred_*`, `set_reg`, `set_dst`, `set_carry_*`,
  `encode_form_a/b`, `set_rnd_mode`, `set_*_cmp_op`, `set_tex_*`, `set_mem_type`,
  `set_*_cache_op`, `set_rel_offset`), plus `legalize_ext_instr`.

Re-exports wired so downstream modules (`alu/`, `control.rs`, `mem.rs`, `tex.rs`)
require zero import changes.

### EVOLUTION Markers Re-Assessed

| Marker | File | Assessment |
|--------|------|------------|
| SM32 `.s` peephole | `sm32/control.rs` | **Deferred** — requires IR-level `.sync` flag, label recomputation, scheduler awareness. Not a simple peephole. |
| PTX emitter `.clone()` hot paths | `ptx_emit/expr_eval.rs`, `emitter.rs`, `statements.rs` | **Deferred** — borrow-checker workarounds, cached/amortized. Structural `PtxEmitter` refactor needed. |
| 7 others (dual-issue, co-issue, reserved GPR, PrmtSel, CBuf ALU, OpBra `.u`, jump threading) | various | Genuinely deferred — hardware modeling or IR extension work. |

### Hygiene

- Bare `unreachable!()` in `builder/mod.rs` test code given descriptive messages.
- `.unwrap()` re-audit: zero in production code (all 178 are in `#[cfg(test)]`).

## Verification

- `cargo clippy --all-features -- -D warnings`: zero warnings
- `cargo test --workspace`: 3,963 passed, 4 ignored, 0 failures
- `cargo fmt --check`: clean

## For Upstream

No action required. Pure code-structure improvement.
