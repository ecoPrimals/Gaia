<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 124: Code Size Compliance + Named Constants

**Date**: June 22, 2026
**Primal**: coralReef
**Commit**: `3cba397`
**Tests**: 3601 passing, 0 failed
**Coverage**: 84% line
**Quality**: fmt ✅, clippy (pedantic+nursery) ✅, doc ✅, test ✅

---

## Summary

Code size compliance pass: all hand-written production `.rs` files now
under 800 LOC. Magic numbers in capability advertisement extracted to
named constants. Encapsulation improved via `PrmtSelByte::is_valid()`.

## Changes

### File Splits (semantic, not mechanical)

| File | Before | After | Strategy |
|------|--------|-------|----------|
| `codegen/ir/op_conv.rs` | 801 LOC | 365 LOC `op_conv.rs` + 448 LOC `op_shuffle.rs` | Conversion/move ops vs permute/shuffle/predicate/reduction ops — operations grouped by data-flow pattern |
| `codegen/nv/sm75_instr_latencies/gpr.rs` | 814 LOC | 376 LOC `gpr.rs` + 467 LOC `gpr_hazards.rs` | Enum + categorization vs WAW/WAR/pred hazard tables — restricted `pub(in ...)` visibility preserves encapsulation |

### Named Constants (zero magic numbers)

Extracted from `capability.rs` `self_description()`:

| Constant | Value | Purpose |
|----------|-------|---------|
| `LATENCY_WGSL_NV_P50_MS` | 10.0 | WGSL→NVIDIA p50 latency estimate |
| `LATENCY_WGSL_NV_P99_MS` | 25.0 | WGSL→NVIDIA p99 latency estimate |
| `LATENCY_WGSL_AMD_P50_MS` | 12.0 | WGSL→AMD p50 latency estimate |
| `LATENCY_WGSL_AMD_P99_MS` | 30.0 | WGSL→AMD p99 latency estimate |
| `LATENCY_SPIRV_NV_P50_MS` | 8.0 | SPIR-V→NVIDIA p50 latency estimate |
| `LATENCY_SPIRV_NV_P99_MS` | 20.0 | SPIR-V→NVIDIA p99 latency estimate |
| `MAX_CONCURRENT_COMPILES` | 64 | Concurrent compilation limit |
| `MAX_MULTI_TARGETS` | 64 | Multi-target compilation limit |

### API Improvement

- `PrmtSelByte::is_valid()`: public method replacing private field access
  pattern after `PrmtSelByte` moved to `op_shuffle.rs`

## Generated Code Exemption

AMD ISA generated files (latency tables) are machine-generated and
explicitly exempt from hand-authored file size limits.

## Remaining File Sizes (monitored)

| File | LOC | Notes |
|------|-----|-------|
| `crates/coralreef-core/src/ipc/btsp.rs` | 796 | BTSP + discovery — cohesive, no obvious split boundary |
| `crates/coralreef-core/src/main.rs` | 759 | Feature-gated duplication is structural |

## Upstream Impact

None — internal refactor, no IPC contract changes, no API changes.

## For Overwatch

- All quality gates green: fmt, clippy (pedantic+nursery -D warnings), test (3601), doc
- Zero hand-written production files >800 LOC
- Zero TODO/FIXME in committed `.rs` code
- Zero unsafe in workspace
