# Songbird Wave 58 — Process-Env Full Adoption + #[expect] Lint Evolution

**Date**: May 28, 2026  
**Wave**: 58  
**Status**: COMPLETE  
**Triggered by**: primalSpring Wave 58 audit — "~70 env sites. Adopt `songbird-process-env` crate fully." + "~180 test `#[allow(clippy::` → batch `#[expect` migration."

---

## Summary

Two Tier 2 team-owned evolution tasks completed in one pass:

### 1. `songbird-process-env` Full Adoption (~48 sites migrated)

All production `std::env::var()` / `std::env::var_os()` calls in library and binary code
migrated to `songbird_process_env::var()` / `songbird_process_env::var_os()`.

**Crates with new `songbird-process-env` dependency added**:
- `songbird-stun` (Cloudflare DDNS `from_env()`)
- `songbird-turn-client` (TURN session `from_env()`)

**Production sites migrated** (partial list):
- `neural_announce.rs` — NEURAL_API_SOCKET, XDG_RUNTIME_DIR, FAMILY_ID chains (5)
- `introspection/primal.rs` — socket path resolution (4)
- `turn_client/session.rs` — SONGBIRD_TURN_SERVER/USERNAME/KEY (3)
- `ddns_cloudflare.rs` — SONGBIRD_CF_API_TOKEN/ZONE_ID (2)
- `cli/commands/status.rs` — BIOMEOS_SOCKET_DIR/XDG_RUNTIME_DIR (2)
- `config/paths.rs` — XDG_DATA_HOME/XDG_CONFIG_HOME (2)
- `test_runner.rs` — SONGBIRD_URL (1)
- `test-utils/network_fixtures.rs` — 9 test port/address functions
- `test-utils/fixtures/` — endpoint/port/binary discovery (9)
- Plus 24 integration test files

**Remaining `std::env` (legitimate exceptions)**:
- `songbird-process-env/src/lib.rs` — IS the implementation
- `examples/*.rs` — standalone demo binaries
- Doc comments — illustrative code
- `error_helpers_comprehensive_tests.rs` — tests std::env error conversion traits

### 2. `#[allow(clippy::` → `#[expect(clippy::` Migration (146 items evolved)

**Migrated to `#[expect]`** (146 items):
- `clippy::too_many_lines` — function-level (lint always fires)
- `clippy::type_complexity` — item-level
- `clippy::cast_possible_truncation` — item-level
- `clippy::cast_precision_loss` — item-level
- `clippy::cast_sign_loss` — item-level
- `clippy::float_cmp` — test module with comparisons
- `clippy::useless_vec` — test module with vec![]
- `clippy::unreadable_literal` — test module with literals
- `clippy::items_after_statements` — test module with pattern
- `clippy::uninlined_format_args` — test module with pattern

**Correctly kept as `#[allow]`** (module-level blanket suppressions):
- `clippy::unwrap_used` / `clippy::expect_used` — module-scope `#[expect]` requires
  the lint to fire exactly once in that scope, which doesn't work for blanket test
  module suppression where individual functions may use `.unwrap()` but not `.expect()`
  (or vice versa). `#[allow]` is the correct idiom for module-level blanket suppression.

---

## Verification

- `cargo clippy --workspace --lib --bins` — 0 warnings, 0 unfulfilled expectations
- `cargo clippy --workspace --tests` — 0 unfulfilled expectations (pre-existing
  `songbird-universal` test compilation issues unrelated to this work)
- `cargo test -p songbird-orchestrator` — all pass
- `cargo test -p songbird-config -p songbird-cli -p songbird-stun -p songbird-turn-client -p songbird-test-utils -p songbird-discovery -p songbird-crypto-provider` — all pass
- `cargo fmt --check` — clean

---

## Impact

- **Testability**: All production env access now goes through the injectable overlay,
  enabling proper test isolation without global env pollution
- **Lint hygiene**: `#[expect]` will warn if underlying code is refactored such that
  the suppressed lint no longer fires (e.g., function shortened below `too_many_lines`
  threshold), catching stale suppressions automatically
- **primalSpring audit**: Both Wave 58 Songbird items resolved

---

## Additional: Coverage Expansion (+67 tests)

Following the env/expect migration, a deep debt sweep confirmed zero files >800L,
zero unsafe, zero hardcoding, zero production mocks, and all-pure-Rust deps. Then
**67 new tests** were added to 4 previously-untested pure-logic modules:

- `songbird-config/src/canonical/constants/env_helpers.rs` (+23): boolean/port/parse edge cases
- `songbird-config/src/canonical/constants/logging_cors_env.rs` (+11): log level chains, CORS policy
- `songbird-orchestrator/src/server/compute_api/compute_types.rs` (+18): job status serde, API errors
- `songbird-discovery/src/production/real_service_discovery/conversions.rs` (+15): type conversions

**Total test count**: 8,091 → **8,158** (+67)

---

## Files Changed

65 files (wave58) + 4 files (coverage), +994 insertions, -169 deletions across 10 crates.
