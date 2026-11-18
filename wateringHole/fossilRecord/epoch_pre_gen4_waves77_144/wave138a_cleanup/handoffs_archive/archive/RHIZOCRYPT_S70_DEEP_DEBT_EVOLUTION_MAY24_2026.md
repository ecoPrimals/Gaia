# rhizoCrypt — S70 Deep Debt Evolution + Wave 47 Convergence

**Date**: 2026-05-24
**Sprint**: S70
**Status**: Complete — 1,646 tests, zero debt across 12 categories

---

## Summary

S70 addresses the remaining deep debt items in rhizoCrypt and aligns with
Wave 47 deployment behavior convergence. The codebase is now at zero
production debt across all audit categories.

## Deep Debt Audit (12-Category)

| Category | Status |
|----------|--------|
| `unsafe` blocks | Zero (`deny`) |
| `unwrap()`/`expect()` in production | Zero (`deny`) |
| `async-trait` | Zero |
| `Arc<Mutex>` | Zero (only `Arc<RwLock>` — no `Mutex`) |
| `Box<dyn Error>` in production | **Zero** (was 1, fixed in `send_jsonrpc_uds`) |
| `todo!()`/`unimplemented!()`/`unreachable!()` | Zero |
| TODO/FIXME/HACK/XXX comments | Zero |
| `&Vec<`/`&String` params | Zero |
| `#[allow(dead_code)]` in production | Zero |
| Files >800L (production) | Zero (max: 755L `niche.rs`) |
| Mock in production | Documented: `BearDogVerifier` placeholder (JH-11 pending) |
| External deps | All pure Rust (OS FFI via tokio/redb expected) |

## Changes Made

### Production Code

1. **`Box<dyn Error>` → `ServiceError`**: `send_jsonrpc_uds` now uses
   `ServiceError::Discovery` instead of `Box<dyn std::error::Error>`.

2. **Songbird scaffolded registration**: `register()` without `live-clients`
   now returns `success: false` with `"Discovery unavailable"` instead of
   faking `success: true` with a synthetic service ID.

3. **Magic numbers → constants**: Inline timeouts (2s, 5s) moved to
   `NEURAL_API_CONNECT_TIMEOUT_SECS` / `NEURAL_API_READ_TIMEOUT_SECS`.
   Storage cap (1 GiB) moved to `DEFAULT_MAX_MEMORY_BYTES`.

### Test Infrastructure

4. **Method gate tests extracted**: `method_gate.rs` dropped from 825 → 489
   production lines. Tests live in `method_gate_tests.rs` via `#[path]`.

5. **Handler test harness deduplicated**: Shared helpers (`test_gate`,
   `test_caller`, `create_test_primal`, `make_request`) extracted to
   `handler_test_support.rs`, eliminating duplication between
   `handler_tests.rs` and `handler_tests_validation.rs`.

### Dependency Hygiene

6. **`base64`/`hex` hoisted to workspace**: Resolves `hex 0.4` vs `0.4.3`
   pin inconsistency between core and rpc crates.

7. **`serde` `rc` feature removed**: Was enabled but unused anywhere in the
   codebase. Reduces compile surface.

### Wave 47 Compliance

8. **`--socket` CLI alias**: `visible_alias = "socket"` on `--unix` flag
   lets `plasmidBin/start_primal.sh` pass `--socket` uniformly. The
   per-rhizoCrypt workaround in the launcher can be removed.

### Documentation Reconciliation

9. **Metrics reconciled**: Test count (→1,646), file count (→175), method
   count (→32), domain count (→6) synchronized across README, CONTEXT,
   DEPLOYMENT_CHECKLIST, and sporeprint.

10. **Coverage wording**: Changed from "CI gate: 90%" to "last measured"
    (coverage job not in current CI workflow).

11. **Spec status headers**: 4 specs updated from "Draft" to "Implemented"
    (DATA_MODEL, STORAGE_BACKENDS, SLICE_SEMANTICS, DEHYDRATION_PROTOCOL).

12. **`capability_registry.toml`**: Fixed duplicate `stability` key on
    `dag.partial_dehydrate` (was both "stable" and "evolving"; now "evolving").

13. **Dead doc reference**: Removed stale `SPRING_PROVENANCE_PATTERN.md`
    reference from `provenance/client.rs`.

## Compliance Matrix (Wave 47)

| Check | Status |
|-------|--------|
| `--socket` flag | PASS |
| `health.liveness` shape | PASS (`{"status":"alive"}`) |
| `lifecycle.status` | PASS |
| `primal.announce` | PASS (Wave 43) |
| Socket cleanup | PASS (since S23) |
| Signal handling | PASS (SIGTERM + SIGINT) |

## Gate Metrics

- **1,646 tests**, 0 failures
- **0 clippy warnings** (pedantic + nursery + cargo + cast)
- **0 fmt diffs**
- **175 `.rs` files**, ~53,852 lines
- **32 methods**, 6 domains (31 stable, 1 evolving)

## Prior Handoffs (archived)

- `RHIZOCRYPT_S68_GAP36_WIRE_ALIASES_MAY13_2026.md`
- `RHIZOCRYPT_S69_WAVE22_STADIAL_GATE_MAY17_2026.md`
- `RHIZOCRYPT_WAVE43_NEURAL_API_ANNOUNCE_MAY23_2026.md`
