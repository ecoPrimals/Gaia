<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 143: Deep Debt Pass

**Date**: July 15, 2026
**Commit**: `899f1d3` (coralReef main)
**Gate**: ironGate / eastGate
**Tests**: 3649 (3645 pass + 4 ignored hardware-gated)
**Clippy**: zero warnings (`--all-features -- -D warnings`)

---

## Summary

Wave 143 is a deep-debt evolution pass focused on file-size compliance,
namespace de-hardcoding, and warning cleanup.

## Changes

### File Size Compliance (all hand-authored .rs files under 800 LOC)

| File | Before | After | New File |
|------|--------|-------|----------|
| `codegen_coverage_extended.rs` | 926 | 540 | `codegen_coverage_crossarch.rs` (422) |
| `spring_absorption.rs` | 925 | 601 | `spring_absorption_advanced.rs` (349) |
| `codegen_coverage_targeted.rs` | 858 | 431 | `codegen_coverage_ops.rs` (431) |
| `btsp.rs` | 797 | 416 | `btsp/tests_btsp.rs` (388) |

**Exception**: Auto-generated ISA files (`vop3/mod.rs` 929L, `mimg/table.rs`
801L) are under the 1000L hard cap, marked `DO NOT EDIT BY HAND`, and split
would require generator changes.

### Namespace-Agnostic Paths

`socket_base_dir()` tier 3 and tier 4 now use `ecosystem_namespace()` instead
of hardcoded `"biomeos"`:

- `/run/{namespace}` (was `/run/biomeos`)
- `$TMPDIR/{namespace}-runtime` (was `biomeos-runtime`)

Full support for `$BIOMEOS_ECOSYSTEM_NAMESPACE` override propagates to all
socket resolution tiers. Integration tests updated to assert dynamically.

### Warning Cleanup

Removed 4 unused imports across test files that accumulated during prior
splits (`service`, `Bytes`, `DeviceTarget`, `super::*`).

### Root Documentation Refresh

All root docs (README, STATUS, CHANGELOG, CONTEXT, EVOLUTION, ABSORPTION,
WHATS_NEXT, sporeprint, genomebin, specs) updated to Wave 143:

- STATUS.md: excised GlowPlug/boot-sovereignty rows (Sprint 9), fixed
  served count (19→18), consumed count (4→5), date to July 15
- CHANGELOG.md: added entries for Waves 133b, 141a, 143
- IPC method inventories reconciled everywhere: 18 served / 5 consumed

## Audit Scorecard (Post-Wave 143)

| Category | Status |
|----------|--------|
| Files >800 lines (hand-authored) | **Zero** |
| Unsafe code | **Zero** (test-only exception in `test_env.rs`) |
| Hardcoded primal names | **Zero** (`biomeos` namespace now configurable) |
| TODO/FIXME/HACK | **Zero** |
| Production mocks | **Zero** (`coral-reef-stubs` is architectural) |
| `.unwrap()` in library code | **Zero** |
| Commented-out code | **Zero** |
| SPDX headers | 447/447 |
| `#![warn(missing_docs)]` | All lib crates |

## Upstream Notes

- **wateringHole `freshness.toml`**: updated to `899f1d3`
- **Cross-arch**: `cargo check --target x86_64-pc-windows-gnu` still clean
  (Wave 141a `cfg` gates preserved)
- **No new dependencies** added this wave
