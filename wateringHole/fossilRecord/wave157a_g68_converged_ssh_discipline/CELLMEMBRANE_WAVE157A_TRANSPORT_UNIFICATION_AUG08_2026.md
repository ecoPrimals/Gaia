# cellMembrane Wave 157a — Transport Unification + Dead Code Cleanup

**Date:** 2026-08-08  
**Commit:** `f5033f2`  
**From:** eastGate overwatch  
**Pushed to:** golgiBody (git.primals.eco)

---

## Summary

G66 transport layer graduation — `jsonrpc.rs` platform conditionals reduced
from 7 to 3. UDS and TCP JSON-RPC calls now share a single implementation
through `TransportStream`, eliminating duplicated write/read/signal logic.

## Changes

### Transport Unification (jsonrpc.rs)

| Function | Before | After |
|----------|--------|-------|
| `raw()` | `#[cfg(unix)]` + `#[cfg(not(unix))]` pair, direct `UnixStream` | Routes through `connect_transport()` → `rpc_over_stream()` |
| `call_tcp()` | Duplicate write/read/signal logic | Routes through `connect_transport()` → `rpc_over_stream()` |
| `send_notify()` | `#[cfg(unix)]` + `#[cfg(not(unix))]` pair | Routes through `connect_transport()` → `notify_over_stream()` |

New shared helpers:
- `rpc_over_stream(TransportStream, request, with_signal, label)` — write + read over any transport
- `notify_over_stream(TransportStream, request)` — fire-and-forget write over any transport

Remaining `#[cfg(unix)]`: `call_btsp()` pair (BTSP handshake requires raw `UnixStream`
access for challenge/response) + 1 test-only gate.

### Dead Code Cleanup

| Item | Before | After |
|------|--------|-------|
| `CommitPayload` struct | `#[allow(dead_code)]` on entire struct | Allow removed; field-level `#[allow(dead_code)]` on `.id` only |
| `PushEvent.commits` | `#[allow(dead_code)]` | Allow removed (used via `has_harvest_signal`) |

### Hardcode Elimination

| Literal | Location | Fix |
|---------|----------|-----|
| `"security.sock"` | `dispatch/infra.rs:300` | `MembraneService::binary_for(CryptoSigner)` registry lookup |
| `"webhook.sock"` | `webhook/listener.rs:23` | New `WEBHOOK_SOCKET_NAME` constant |

### New Constants

- `WEBHOOK_SOCKET_NAME: &str = "webhook.sock"` in `cellmembrane-types/src/service/constants.rs`

## Metrics

- **1329 tests** passing (zero regressions)
- **0 clippy warnings** (pedantic + nursery)
- **0 unsafe code** (`#![forbid(unsafe_code)]`)
- **Net: +133/-127 lines** (dead code removed, shared helpers added)

## Upstream Notes

- `call_btsp()` BTSP handshake still requires direct `UnixStream` — cannot generalize
  through transport layer without redesigning the challenge/response protocol
- `native_braid.py` → Rust remains open (1171L Python orchestrator in wateringHole/scripts/)
