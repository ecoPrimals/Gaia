<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 145b Docs Refresh (July 16, 2026)

## Commit

`c28980e` on `main`

## Summary

Full root documentation refresh — 10 files updated to Wave 145 with
reconciled test count (3650 total: 3646 passed, 4 ignored).

## Changes

### Test Count Reconciliation

Canonical `cargo test --all-features` run produced 3650 total (3646
passed, 0 failed, 4 ignored hardware-gated). Previous docs cited 3648
or 3649 inconsistently. All 10 root docs + `genomebin/manifest.toml`
now agree on 3650.

### CONTEXT.md IPC Method Fix

Removed 5 phantom IPC methods (`shader.compile.module`,
`shader.validate`, `shader.bio`, `shader.dispatch`, `shader.health`)
that never existed in `config.rs` SERVED_METHODS. Replaced with actual
18 served / 5 consumed method listing matching production code.

### WHATS_NEXT.md LOC Monitor

Updated stale LOC monitor section — former >800 LOC files
(`tests_unix_edge.rs`, `nv_metal.rs`, `vfio/memory.rs`) are either
resolved by Wave 143 splits or excised Sprint 9. Current near-threshold
monitors: `sm20/encoder.rs` (795), `amd/encoding.rs` (795).

### Resolved Gaps

CONTEXT.md "Remaining Gaps" (GAP-HS-124, GAP-HS-115) both marked as
historical — resolved in Wave 68/126.

### Spec Footer

Fixed duplicate June 2, 2026 footer in `CORALREEF_SPECIFICATION.md` →
July 16, 2026.

### cargo clean

Reclaimed 8.4 GiB build artifacts.

## Files Modified

- `README.md` — Wave 145, 3650 tests, Phase 10 row
- `STATUS.md` — 3650 tests (resolved internal 3648/3649/3645 contradiction)
- `CHANGELOG.md` — (already current)
- `WHATS_NEXT.md` — Wave 145, LOC monitor, footer
- `CONTEXT.md` — IPC methods, resolved gaps, Wave 145
- `EVOLUTION.md` — Wave 145, 3650 tests
- `ABSORPTION.md` — Wave 145, 3650 tests
- `sporeprint/validation-summary.md` — Wave 145, 3650 tests, date
- `genomebin/README.md` — 3650 tests, Wave 145
- `genomebin/manifest.toml` — tests = 3650
- `specs/CORALREEF_SPECIFICATION.md` — Wave 145, footer date

## Quality Gates

- `cargo clippy --all-features -- -D warnings` — PASS (zero warnings)
- `cargo test --all-features` — PASS (3650 total, 0 failures)
- `cargo check --target x86_64-pc-windows-gnu` — PASS
