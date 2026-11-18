# Songbird Wave 209 — Full Evolution Pass

**Date**: June 2, 2026  
**From**: southGate / Songbird team  
**Type**: Deep debt evolution + integration fix  
**Version**: v0.2.2-wave209

---

## Summary

Full codebase evolution pass achieving zero-warning, zero-bypass, zero-hardcoding status across the entire 31-crate workspace. Fixes long-standing integration test compilation failures and completes the `songbird-process-env` migration.

---

## Changes

### 1. `songbird-process-env` Adoption Complete

Migrated last 7 `std::env::vars()` call sites to `songbird_process_env::vars()`:

| File | Context |
|------|---------|
| `songbird-config/src/agnostic_primal_config.rs` | Custom capability endpoint discovery |
| `songbird-config/src/canonical/constants/primal_discovery.rs` (×3) | `get_configured_primal_names`, `get_common_primal_ports`, `find_primals_with_capability` |
| `songbird-discovery/src/discovery/backends/container_orchestration/environment.rs` | Container service discovery |
| `songbird-discovery/src/discovery/backends/service_discovery.rs` (×2) | Environment service detection |

**Result**: Zero `std::env` calls in production code. All env access goes through overlay-aware abstraction.

### 2. Integration Test Compilation Fixed

**`songbird-universal`** (7 test files):
- `futures::future::join_all` → `futures_util::future::join_all` (11 call sites)
- The `futures` facade crate was never a dependency; tests incorrectly imported it

**`songbird-universal` + `songbird-types`** (4 test files):
- `assert_eq!` on `anyhow::Error` → `.to_string()` comparison (6 sites)
- `matches!` guards comparing `&anyhow::Error` with `==` → `.to_string()` (3 sites)
- `url_edge_cases.rs` return type: `SongbirdResult<()>` → `anyhow::Result<()>` for `?` compat

### 3. Clippy Zero-Warning (workspace-wide including tests)

- Removed 36 unfulfilled `#[expect(clippy::...)]` across 5 files (lints no longer fire)
- Fixed redundant closures: `|v| v.to_string()` → `ToString::to_string` (2 sites)
- Fixed `cast_possible_truncation` in stun test → `u16::try_from().unwrap()`
- Removed unused imports (`Ipv6Addr`, `StunCredentials`)
- Fixed `Arc::clone` idiom (`call_count.clone()` → `Arc::clone(&call_count)`)
- Moved `hex_decode` above test module (items_after_test_module)
- Added `#[allow(deprecated)]` on tests intentionally exercising deprecated functions

### 4. File Size Refactoring

- `songbird-network-federation/src/state.rs`: 877→459 lines (tests extracted to `state_tests.rs`)
- Zero source files exceed 800 lines (largest: 799L)

---

## Verification

```
cargo check --workspace --tests    # zero errors
cargo clippy --workspace           # zero warnings (prod)
cargo fmt --check                  # clean
cargo test -p songbird-network-federation -p songbird-universal-ipc  # 958 tests pass
cargo test -p songbird-universal --tests  # all integration tests compile + pass
cargo test -p songbird-types --tests      # all integration tests compile + pass
```

---

## Codebase Health (post-wave)

| Metric | Value |
|--------|-------|
| Crates | 31 |
| `forbid(unsafe_code)` | 31/31 |
| Clippy warnings (prod) | 0 |
| `std::env` in production | 0 |
| `/tmp` in production | 0 |
| Files >800L | 0 |
| TODO/FIXME/HACK | 0 |
| Tests | 8,500+ |
| C/FFI deps (default) | 0 |
| Mocks in production | 0 |

---

## For primalSpring

No action needed from upstream. This is internal quality evolution. All method contracts, wire formats, and capabilities unchanged. Integration tests now compile clean for the first time since the `futures-util` migration in Wave 165.
