# coralReef Wave 152 — Deep Debt Deduplication + Doc Refresh

**Date**: Jul 26, 2026
**Gate**: eastGate
**Wave**: 152
**Primal**: coralReef

---

## Summary

Wave 152 focused on deep debt deduplication and documentation refresh.
All root docs aligned to Wave 152 / 3669 tests.

### Deep Debt (completed earlier this wave)

- **PTX math arg dedup**: Created `require_math_arg()` helper in `ptx_emit/mod.rs`,
  replaced 18 repetitive error-handling patterns across `math.rs`, `math_ext.rs`,
  `math_ext_trig.rs`.
- **Test helper consolidation**: 5 codegen coverage test files now import shared
  helpers from `codegen_sat/helpers.rs` via `#[path]` module linking instead of
  duplicating ~50 LOC each.
- **Assertion dedup**: Created `assert_ok_or_not_implemented()` in
  `compiler_integration/main.rs`, replaced 26 verbose assertion patterns across
  `pipeline.rs`, `sm70.rs`, `stress.rs`.
- **File size**: Extracted 478 lines of tests from `dataflow.rs` (768→293 LOC) into
  `dataflow_tests.rs`.

### Doc Refresh (this session)

All 11 root docs updated from stale Wave 146/151b → Wave 152:

1. `README.md` — version line, quick start, quality gates table, phase table
2. `STATUS.md` — header, test table
3. `WHATS_NEXT.md` — position, completed waves, test count, date
4. `CONTEXT.md` — test count, sprint 14 history
5. `EVOLUTION.md` — header, inline count, history footer
6. `ABSORPTION.md` — header, inline count
7. `CONTRIBUTING.md` — quick start test count
8. `START_HERE.md` — quick start test count
9. `sporeprint/validation-summary.md` — TOML front matter, status section
10. `genomebin/README.md` — inline count + wave
11. `genomebin/manifest.toml` — `tests = 3669`
12. `specs/CORALREEF_SPECIFICATION.md` — date, status, phase table, fixed broken
    cross-reference (`specs/SOVEREIGN_MULTI_GPU_EVOLUTION.md` → `docs/archive/...`)
13. `CHANGELOG.md` — current status line

## Metrics

| Metric | Previous (151b) | Current (152) | Delta |
|--------|-----------------|---------------|-------|
| Tests total | 3700 | **3669** | -31 (test binary consolidation from helper dedup) |
| Tests passing | 3696 | **3665** | -31 |
| Tests ignored | 4 | **4** | — |
| Line coverage | 84% | **84%** | — |
| Clippy warnings | 0 | **0** | — |
| Unsafe blocks | 0 | **0** | — |

## Debris Audit

- No `.bak`/`.old`/`.orig`/`.swp`/`.tmp` files
- No Python scripts in production
- No Makefile/CMakeLists.txt
- No log files
- `scripts/coverage.sh` — active, referenced in CONTRIBUTING.md
- `docs/archive/` (3 files) — historical, kept as fossil record
- `config/capability_registry.toml` — intentional external manifest

## Remaining Work (unchanged from 151b)

- Coverage push toward 90% (compiler backends are main gap)
- `sm20/encoder.rs` (795 LOC), `amd/encoding.rs` (795 LOC) near threshold
- 81 `CompileError::NotImplemented` sites (intentional feature gaps, not debt)
- Custom `getrandom` backend via `rustix` (remove transitive `libc` from crypto)
- Server-side BTSP `ClientHello` handling (currently first-byte heuristic)

## Quality Gates

```
cargo fmt --check          ✓
cargo clippy --all-features -- -D warnings  ✓
cargo test --all-features  ✓ (3669 total, 3665 passed, 4 ignored)
cargo check --target x86_64-pc-windows-gnu  ✓
```
