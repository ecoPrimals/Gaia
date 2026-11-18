<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Deep Debt Audit & Refactoring (May 24, 2026)

**Date**: 2026-05-24  
**Author**: coralReef team  
**Context**: Post-Wave 47 comprehensive debt audit and evolution pass

---

## Audit Results — Zero Debt Confirmed

| Category | Status | Detail |
|----------|--------|--------|
| Unsafe code | Zero | `#![forbid(unsafe_code)]` on all crates |
| TODO/FIXME/HACK | Zero | No markers in any `.rs` file |
| Mocks/stubs in production | Zero | `coral-reef-stubs` fully evolved (pure Rust) |
| Hardcoded primal names | Zero | Runtime capability-based discovery only |
| Hardcoded paths | Zero | All via `$XDG_RUNTIME_DIR`, env vars, or CLI |
| `.unwrap()` in library | Zero | `Result<T, E>` + `thiserror` throughout |
| `Result<_, String>` | Zero | Typed errors everywhere |
| Deprecated/dead_code | Zero | No stale markers |
| C/FFI dependencies | Zero direct | Transitive `libc` only via tokio/getrandom |
| `*-sys` crates | Zero | Only `linux-raw-sys` (pure Rust) |
| Clippy warnings | Zero | `pedantic` + `nursery`, `-D warnings` |

## Refactoring Executed

### `ptx_emit/ray_query.rs` extraction (smart refactor)

- **Source**: `crates/coral-reef/src/codegen/nv/ptx_emit/statements.rs` (1078 → 893 lines)
- **Target**: New `ray_query.rs` submodule (199 lines)
- **Rationale**: RT core emission (5 methods) forms a cohesive domain — SM75+ traversal state machine. Isolated for clarity and future hardware-specific evolution.
- **Impact**: Zero behavioral change. All tests pass unchanged.

### Files >800 lines — disposition

| File | Lines | Disposition |
|------|-------|-------------|
| `ptx_emit/statements.rs` | 893 | Just under limit after refactor; remaining methods are distinct domains (atomic, subgroup, image, inline) with no clean split |
| `gpu_arch.rs` | 948 | 668 production + 279 tests — production under 800 |
| `amd/isa_generated/vop3/mod.rs` | 929 | Auto-generated from AMD ISA XML — not hand-editable |
| `amd/isa_generated/mimg/table.rs` | 801 | Auto-generated ISA table |
| `sm75_instr_latencies/gpr.rs` | 814 | Hardware latency model data table |
| Test files (5×) | 838–928 | Naturally large test suites — not refactoring targets |

## Documentation Synchronized

All root docs updated to reflect 3204 tests and Wave 47 state:
- `README.md`, `STATUS.md`, `WHATS_NEXT.md`, `EVOLUTION.md`
- `CONTEXT.md`, `ABSORPTION.md`, `CONTRIBUTING.md`, `START_HERE.md`
- `specs/CORALREEF_SPECIFICATION.md`, `sporeprint/validation-summary.md`
- `genomebin/manifest.toml`

## Debris Review

- Zero `.bak`, `.tmp`, `.old`, `.orig` files
- Zero stale scripts (only `scripts/coverage.sh` — active, legitimate)
- Zero commented-out code in `.rs` files
- All `EVOLUTION()` markers represent tracked future work (legitimate)
- `whitePaper/` and `docs/` content is fossil record (preserved)

## Current State

- **3204 tests**, 0 failed, 0 ignored (hardware-gated)
- Zero clippy warnings (pedantic + nursery)
- Zero unsafe code ecosystem-wide
- Fully sovereign dependency tree (no C, no vendor SDK)
- `primal.announce` operational (Wave 44 wire fix applied)
- `--socket` CLI flag and `{"status":"alive"}` health response (Wave 47)
