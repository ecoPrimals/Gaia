# NestGate v0.5.0 — Session 91 Zero Test Failures

**Date**: 2026-06-03
**Gate**: ironGate (eastGate)
**Primal**: nestgate v0.5.0
**Session**: 91

## Context

Wave 76 parity sprint. primalSpring identified 12 pre-existing test failures
as known debt. These were not env-var races (as previously diagnosed) but
stale test assertions from Session 88's honest-error evolution that were
never updated. Additionally, true env-var races in `nestgate-rpc` were fixed
with `serial_test`.

## Delivered

### Stale Assertion Sweep (16 tests across 5 crates)

Session 88 evolved 9 production code paths from fake successes to honest errors
(401, 501, NotImplemented). Tests in separate files were never updated to match.

| Crate | Tests Fixed | Root Cause |
|-------|------------|------------|
| `nestgate-api` (auth_production/tests.rs) | 4 | Expected `Ok` from `create_user`/`authenticate`, now assert 501/401 |
| `nestgate-api` (auth_production_tests.rs) | 8 | Expected `StatusCode::OK` from auth handlers, now assert UNAUTHORIZED/NOT_IMPLEMENTED |
| `nestgate-config` (migration_framework/mod.rs) | 1 | Expected `Ok` from `migrate()`, now asserts NotImplemented |
| `nestgate-discovery` (network.rs) | 3 | Expected `Ok` from `discover_service_endpoint`, now asserts NotImplemented |
| `nestgate-security` (tests.rs + hybrid_manager.rs) | 9 | Expected token self-minting success, now asserts external-provider-required error |

### Env-Var Race Condition Fix (55 tests serialized)

Added `#[serial]` from `serial_test` to all filesystem-backed storage tests in
`nestgate-rpc` that read `NESTGATE_STORAGE_BASE_PATH`. These tests were racing
with `temp_env::async_with_vars` in crossgate federation tests.

**Files**: `content_handler_tests.rs` (19), `crossgate_federation_tests.rs` (9),
`storage_handler_tests.rs` (23), `nat_handlers_tests.rs` (4)

## Metrics

- **2,279 lib tests**, **749 RPC tests**, **3,732 workspace total**
- **0 failures** — serial AND parallel
- **0 clippy warnings**
- **11,546 test functions** across codebase

## westGate ZFS Readiness

Verified via audit:
- `NESTGATE_STORAGE_BASE_PATH` env override: operational
- ZFS dataset detection logic: operational
- `content.replicate.pull` with BLAKE3 verification: operational (Session 90)
- `route.register` mesh capability registration: operational
- westGate enrollment FRAGO reviewed — NestGate is in `repos_needed`

## Next

- HTTP transport parity for `content.replicate.pull` and `content.store_stream*`
  (currently UDS-only)
- Cross-gate live integration test via benchScale topology
- westGate physical onboarding when hardware arrives
