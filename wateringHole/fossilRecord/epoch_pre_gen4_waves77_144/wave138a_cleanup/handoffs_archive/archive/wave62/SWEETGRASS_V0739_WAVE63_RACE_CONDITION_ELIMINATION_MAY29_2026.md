# Wave 63 — SweetGrass Race Condition Elimination

**Date**: May 29, 2026
**Version**: v0.7.39
**Scope**: Test infrastructure evolution — three race condition patterns identified and fixed

---

## Summary

8 pre-existing test failures (7 TCP JSON-RPC + 1 capabilities alias) were traced to
three distinct race condition patterns. All three root causes were eliminated via
dependency injection and API evolution — no sleeps, no retries, no `#[serial]`.

**Before**: 1,557 passed / 8 failed (flaky, env-dependent)
**After**: 1,565 passed / 0 failed (deterministic, 3x stress-verified at 16 threads)

---

## Three Patterns Fixed

### Pattern 1: Port-Rebind Race (TCP tests)

**Anti-pattern**: `TcpListener::bind(:0)` → get port → `drop(listener)` → spawn server
that re-binds same port → `sleep(100ms)` → connect.

**Failure mode**: Between drop and re-bind, another parallel test steals the ephemeral
port. Test connects to wrong listener or gets connection refused.

**Fix**: New `run_tcp_jsonrpc_listener(state, listener, shutdown, btsp_required)` accepts
a pre-bound `TcpListener`. No drop, no re-bind, no sleep.

### Pattern 2: Port-Rebind Race (tarpc tests)

Same anti-pattern as Pattern 1 but with tarpc transport. Leveraged tarpc's existing
`listen_on()` API via new `run_tarpc_server(listener, server, shutdown)`.

### Pattern 3: Environment Variable Pollution (capability handler)

**Anti-pattern**: `handle_capability_list()` reads `SWEETGRASS_PORT` and `FAMILY_ID`
from env vars at handler call time. Parallel tests using `temp_env::with_vars` mutate
the global process environment between sequential calls.

**Failure mode**: `test_capabilities_list_canonical_returns_same_as_alias` calls
`capabilities.list` then `capability.list`. Between calls, a parallel test modifies
`FAMILY_ID`, causing `btsp.required` to differ.

**Fix**: `AppState` now snapshots `tcp_transport_active` and `btsp_required` at
construction time. The handler reads from state, not env. Test state (`new_memory`)
defaults to `false`/`false`.

---

## Files Changed

| File | Change |
|------|--------|
| `tcp_jsonrpc.rs` | Split `start_tcp_jsonrpc_listener` → delegates to `run_tcp_jsonrpc_listener`; BTSP decision is a parameter |
| `tcp_jsonrpc/tests.rs` | Rewritten: `bind_ephemeral()` + `spawn_listener()` helpers; no drop, no sleep |
| `server/mod.rs` | Split `start_tarpc_server` → delegates to `run_tarpc_server` via `listen_on` |
| `server/tests/tarpc_roundtrip.rs` | Rewritten: `bind_ephemeral()` + `spawn_server()` helpers |
| `state.rs` | Added `tcp_transport_active: bool` and `btsp_required: bool` snapshot fields |
| `handlers/jsonrpc/capability.rs` | Reads transport/BTSP from `state` instead of env |
| `tests/btsp_mock_beardog.rs` | Uses `run_tcp_jsonrpc_listener` with pre-bound listener |
| `lib.rs` | Exports `run_tcp_jsonrpc_listener`, `run_tarpc_server` |

---

## Debt Status

| Category | Count | Status |
|----------|-------|--------|
| Test failures | 0 | Clean (was 8) |
| Race conditions | 0 | Eliminated |
| `drop(listener)` anti-pattern | 0 | Removed from all tests |
| Env-reading in handlers | 0 | Snapshotted in `AppState` |
| Clippy warnings | 0 | Clean |

---

## Verification

```
cargo test --all-features        → 1,565 passed, 0 failed
cargo clippy ... -D warnings     → 0 warnings
3x stress at --test-threads=16   → 0 flaky failures
```

---

## Downstream Impact

- `run_tcp_jsonrpc_listener` and `run_tarpc_server` are new public APIs — any
  downstream code that starts TCP/tarpc listeners in tests can adopt these for
  race-free setup
- `AppState` gained two new `bool` fields — `new_memory()` defaults both to `false`;
  `with_store()` and `with_self_knowledge()` snapshot from env at construction
- No wire protocol changes, no method changes, no behavioral changes in production
