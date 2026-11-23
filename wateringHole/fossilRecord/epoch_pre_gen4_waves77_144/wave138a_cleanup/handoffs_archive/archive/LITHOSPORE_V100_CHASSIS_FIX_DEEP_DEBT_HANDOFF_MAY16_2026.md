# lithoSpore v1.0.0 — Chassis Fix + Deep Debt Resolution

**Date**: 2026-05-16
**From**: lithoSpore workstream (post-CATHEDRAL split)
**For**: primalPing audit, upstream primal teams, spring teams

## Summary

The scope-driven chassis abstraction (landed in `4dc6e61`) introduced a
regression that broke all 7 LTEE modules at runtime. Root cause identified,
fixed, and regression-guarded with integration tests. Deep debt pass
executed across the full codebase: hardcoding evolved to capability-based,
duplicate module tables consolidated, `#[allow]` eliminated, redundant
deps removed, stale script references cleaned.

**Result**: 75/75 checks PASS, 116/116 tests PASS, zero clippy errors,
`cargo publish --dry-run` clean for litho-core.

## Regression: Scope-Driven Module Resolution

### Root Cause

Three bugs in `validate.rs` introduced by the chassis abstraction:

1. **`find_expected_json` didn't strip `ltee_` prefix** — Searched for
   `ltee_fitness` in filenames, but expected files are named
   `module1_fitness.json`. The parallel function in `fetch.rs` correctly
   handled this; `validate.rs` did not.

2. **Empty expected path resolved to root directory** — When
   `find_expected_json` returned `""`, `root_path.join("")` yielded the
   root directory, which `.exists()` returned true for, causing modules
   to try parsing a directory as JSON → "Cannot parse expected values JSON".

3. **Multi-dataset module picked wrong data dir** — The anderson module
   has two datasets in `data.toml`. The scope resolver took the first
   match (`dfe_2024`) whose directory doesn't exist, instead of
   `anderson_predictions` which does.

### Fix

- `find_expected_json` now checks both full suffix and short form
- Added `!entry.expected.is_empty()` and `expected_path.is_file()` guards
- Multi-dataset resolution prefers datasets whose `local_path` exists on disk

### Regression Tests Added (4 new integration tests)

- `validate_uses_scope_toml_for_module_table` — scope-driven path with
  minimal scope.toml + data.toml + synthetic data
- `validate_falls_back_to_ltee_constants_without_scope` — verifies
  fallback to compiled LTEE constant table
- `assemble_dry_run_uses_scope_for_binary_list` — scope-driven binary staging
- `scope_with_empty_modules_produces_no_entries` — empty scope edge case

## Deep Debt Resolution

### Hardcoding → Capability-Based Discovery

| Before | After |
|--------|-------|
| `discover_petaltongue_socket()` with hardcoded socket paths | `discover_visualization_socket()` using `litho_core::discover("visualization")` |
| Inline `"ipc.resolve"` string literal | Named constant `RPC_METHOD_RESOLVE` |
| Inline `"visualization.render"` | Named constant `RPC_VIZ_RENDER` |
| Inline `"ecoPrimals/discovery.sock"` | Named constants `RUNTIME_SUBDIR` / `DISCOVERY_SOCKET_NAME` |
| `$PETALTONGUE_SOCKET` env var only | `$VISUALIZATION_SOCKET` (capability-generic) with legacy fallback |

### Duplicate Module Tables Consolidated

**Before**: 6 separate declarations of the 7-module LTEE table across
`validate.rs`, `visualize.rs`, `ops.rs` (cmd_status, cmd_self_test,
cmd_tier, cmd_deploy_report).

**After**: Single source of truth (`LTEE_MODULES` + `LTEE_NOTEBOOKS` in
`validate.rs`), all other sites derive from it.

### Idiomatic Rust Evolution

| Pattern | Before | After |
|---------|--------|-------|
| `#[allow(clippy::cast_possible_truncation)]` (harness.rs) | Suppress warning | `u32::try_from(...).unwrap_or(u32::MAX)` |
| `#[allow(clippy::cast_precision_loss)]` (stats.rs) | Suppress warning | `#[expect()]` with documented reason |
| `#[cfg_attr(not(unix), allow(dead_code))]` | `allow` | `#[expect()]` with reason |
| `#[allow(dead_code)]` on `resolve_binary` | Suppress | `#[cfg(test)]` — properly gated |
| `.map().unwrap_or_else()` (3 sites) | Clippy warning | `.map_or_else()` |

### Dependency Cleanup

- Removed redundant `serde` from 6 module crates (only `ltee-fitness`
  uses it directly)
- Removed redundant `serde_json` from `ltee-cli` dev-dependencies
- Added `repository.workspace = true` to litho-core for crates.io readiness

### Stale Reference Cleanup

All 7 module crates referenced dead `scripts/fetch_*.sh` bash scripts in
user-facing error messages. Updated to `litho fetch --all`.

## Files Modified (25 files, +341 -166 lines)

- **litho-core**: `discovery.rs`, `harness.rs`, `stats.rs`, `Cargo.toml`
- **ltee-cli**: `validate.rs`, `visualize.rs`, `ops.rs`, `assemble.rs`,
  `cli_integration.rs`, `Cargo.toml`
- **Module crates** (7): `lib.rs` (error messages), `Cargo.toml` (deps)
- `Cargo.lock`, `artifact/liveSpore.json`

## Upstream Gaps for primalPing Audit

### Gap 1: Visualization Primal Discovery Protocol

lithoSpore now uses `litho_core::discover("visualization")` for
capability-based socket discovery. The visualization primal (petalTongue)
needs to:
- Register `visualization` capability via the discovery socket protocol
- Accept `visualization.render` JSON-RPC method over UDS
- Respond to `$VISUALIZATION_SOCKET` env var convention

**Owner**: petalTongue team
**Priority**: P2 (lithoSpore degrades gracefully to JSON stdout)

### Gap 2: Discovery Socket Availability

`$XDG_RUNTIME_DIR/ecoPrimals/discovery.sock` must be created by whatever
service manages primal lifecycle (biomeOS / toadStool / NUCLEUS). Currently
lithoSpore probes for it but never finds it in standalone mode.

**Owner**: biomeOS / toadStool
**Priority**: P3 (standalone mode works without it)

### Gap 3: Module 5 Missing from CI Python Baselines

`ci.yml` `python-baselines` job runs 6/7 module notebooks but skips
`module5_biobricks/biobrick_burden.py`. If this is intentional (data
availability), document it. If not, add it.

**Owner**: lithoSpore (self)
**Priority**: P3

### Gap 4: litho-core Public API Documentation

99 public items (struct fields, enum variants, functions) lack `///` doc
comments. Required for crates.io publish with `#![warn(missing_docs)]`.

**Owner**: lithoSpore (self)
**Priority**: P2 (blocks crates.io publish)

### Gap 5: viz/ LTEE-Specific Code in litho-core

`litho-core::viz` still contains LTEE-specific adapters (modules.rs,
baselines.rs) that should live in `ltee-cli`. Generic channel builders
(timeseries, bar, scatter, gauge, etc.) should be extracted as the
domain-agnostic API. This blocks litho-core from being a truly
instance-agnostic engine.

**Owner**: lithoSpore (self)
**Priority**: P2 (blocks clean crates.io publish)

## Verification

```
cargo test --workspace:  116 passed, 0 failed
litho validate --json:   75/75 checks, 7/7 PASS, exit 0
cargo clippy:            0 errors
cargo publish --dry-run: clean (litho-core)
```
