# biomeOS v3.80 — Deep Debt Wave 56

**Date**: 2026-05-27
**From**: biomeOS
**For**: primalSpring re-audit

## Summary

Comprehensive deep debt cleanup across 6 dimensions: large file refactoring,
hardcoding elimination, scaffold cleanup, dead code/lint evolution, and
dependency unification. All 8,038 tests pass with 0 failures.

## Changes

### Smart file refactoring (>800L → <800L)

| File | Before | After | Method |
|------|--------|-------|--------|
| `routing.rs` | 920L | 551L | Extracted `Route` enum + `ROUTE_TABLE` to `route_table.rs`, DRY'd duplicated semantic call logic, extracted handler helpers |
| `nucleus.rs` | 883L | 605L | Extracted process/binary/socket utilities to `nucleus_procs.rs` |

**No production files remain >800 lines.**

### Hardcoding → capability-based

- `examples/full_ecosystem_demo.rs`: raw primal name strings (`"nestgate"`,
  `"songbird"`, etc.) replaced with `primal_names::` constants.
- `crates/biomeos-spore/src/spore/config.rs`: hardcoded `"test_family"` in
  generated `tower.toml` replaced with `self.config.family_id`. Hardcoded
  `/tmp/` socket paths replaced with XDG-compliant `SystemPaths::new_lazy()`
  runtime directory.

### Scaffold cleanup

- `SporeInstantiate` route: previously executed a graph with an unread
  `_deferred` flag that no executor code consumed. Now returns a clean
  structured deferred response: `{status: "deferred", reason: "...", ...}`.

### Dead code / lint cleanup

- `weights/store.rs`: removed `#[allow(clippy::result_large_err)]` by changing
  return types to `Result<(), anyhow::Error>` (wraps the large `redb::Error`).
- `observability/mod.rs`: converted `share_metrics_securely` from `&self`
  method to associated function, removing `#[expect(clippy::unused_self)]`.
- `BtspSessionState::session_id`: confirmed intentional — field is populated
  during `register_session()` and available on cloned states.

### Dependency evolution

- **rustix 0.38 → 1.x**: Unified workspace dependency. Migrated all 5
  affected crates (7 files): `Signal::Term` → `Signal::TERM`,
  `Signal::Kill` → `Signal::KILL`, `mount()` data param `""` → `None::<&CStr>`.
  Only transitive 0.38 remains via `which v6` (third-party).

### Audit results (clean)

| Category | Finding |
|----------|---------|
| Production files >800L | **0** (was 2) |
| `unsafe` in production | **0** |
| `todo!()` / `unimplemented!()` | **0** |
| `#[allow]` in production | **0** (was 2) |
| Raw primal name strings | **0** in production (was 1) |
| Hardcoded paths/values | Config-driven (was hardcoded `/tmp/`, `test_family`) |
| Mocks in production | **0** ungated (NC-1.4 resolved in v3.81) |

## Test results

- **8,038** tests pass, **0** failures, **113** ignored (env-dependent)
- Full workspace `cargo test --workspace` clean
