# coralReef Wave 156a+156b — Deep Debt Deduplication + Doc Refresh

**Date**: Aug 3, 2026
**Gate**: eastGate
**Wave**: 156a → 156b
**Primal**: coralReef

---

## Summary

Wave 156 focused on deep structural debt elimination through deduplication,
allocation optimization, test hygiene, and comprehensive doc alignment.

### Wave 156a — Test Extraction & Coverage

- **btsp.rs test extraction**: 99-line inline test module → `btsp/btsp_guard_tests.rs`
  (747 → 648 LOC)
- **types.rs test extraction**: 41-line `identity_tests` → `types_identity_tests.rs`
  (753 → 712 LOC)
- **Coverage gap fill**: 2 tests for `env_keys.rs` (CORAL prefix invariant,
  SCREAMING_SNAKE_CASE), 7 tests for `tolerances.rs` (constant range, cross-constant
  ordering, hardware-spec anchoring)

### Wave 156b — Deduplication, Allocation & Test Hygiene

- **ShaderInfo::compute()**: Constructor added to `shader_info.rs`, replaced 14
  verbose construction sites across naga_translate, test_shader_helpers, opt_bar_prop,
  legalize, opt_prmt, opt_out, lower_fma, lower_f64, sm70_encode, spill_values
  (~220 LOC eliminated)
- **infer_arch_from_adapter → &'static str**: Eliminates 8 heap allocations per
  adapter inference in the IPC compile path. `resolve_arch` simplified to
  `unwrap_or(arch).to_owned()`
- **Duplicate test removal**: `codegen_coverage_saturation.rs` (551 LOC, 30 tests)
  removed — 100% duplicated by `sat_part01.rs` (20 tests) + `sat_part02.rs` (10 tests)
- **Import cleanup**: Stale `ComputeShaderInfo`, `ShaderIoInfo`, `ShaderStageInfo`
  imports removed from 3 files

### Doc Refresh

All 13 root docs aligned from stale Wave 155i/155j → Wave 156b:

1. `README.md` — version line, quick start, quality gates table, phase table
2. `STATUS.md` — header, date, wave, phase table
3. `WHATS_NEXT.md` — position, completed waves, test count, date, footer
4. `CONTEXT.md` — test count, sprint 14 history
5. `EVOLUTION.md` — header, inline count, history footer
6. `ABSORPTION.md` — header, inline count, footer
7. `CONTRIBUTING.md` — quick start test count
8. `START_HERE.md` — quick start test count
9. `sporeprint/validation-summary.md` — TOML front matter, status section (fixed
   internal contradiction where L14 said 155i/3527 while L13 said 3512)
10. `genomebin/README.md` — inline count + wave
11. `genomebin/manifest.toml` — `tests = 3512`
12. `specs/CORALREEF_SPECIFICATION.md` — date, status, phase table, footer
13. `CHANGELOG.md` — current status line, new Wave 156a+156b entries

### Debris Audit

- No `.bak`/`.old`/`.orig`/`.swp`/`.tmp` files
- No Python scripts in production
- No Makefile/CMakeLists.txt
- No log files
- `scripts/coverage.sh` — active, referenced in CONTRIBUTING.md
- `docs/archive/` (3 files, 32 KB) — historical, kept as fossil record
- `config/capability_registry.toml` — intentional external manifest
- `cargo clean` reclaimed 8.6 GB

## Metrics

| Metric | Previous (155j) | Current (156b) | Delta |
|--------|-----------------|----------------|-------|
| Tests total | 3533 | **3512** | -21 (30 dupes removed, +9 coverage) |
| Tests passing | 3527 | **3506** | -21 |
| Tests ignored | 6 | **6** | — |
| Line coverage | 84% | **84%** | — |
| Clippy warnings | 0 | **0** | — |
| Unsafe blocks | 0 | **0** | — |
| Net LOC change | — | **-770** (156b) | Major dedup |

## Remaining Work

- Coverage push toward 90% (compiler backends are main gap)
- 9 EVOLUTION markers (dual-issue, jump threading, CBuf ALU — intentional feature tracking)
- Auto-generated ISA files (929/801/777/759 LOC) — exempt, generator-level
- 81 `CompileError::NotImplemented` sites (intentional feature gaps)
- `tarpc-transport` feature gate simplification (~20 cfg sites)
- Custom `getrandom` backend via `rustix` (remove transitive `libc` from crypto)
- Server-side BTSP `ClientHello` handling

## Quality Gates

```
cargo fmt --check          ✓
cargo clippy --all-features -- -D warnings  ✓
cargo test --all-features  ✓ (3512 total, 3506 passed, 6 ignored)
cargo check --target x86_64-pc-windows-gnu  ✓
```
