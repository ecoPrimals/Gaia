# Songbird Wave 74 — Virtual Endpoint Relay Phase 2

**Date**: June 3, 2026  
**Gate**: southGate  
**Commit**: `f36bd71d`  

---

## What Was Delivered

### Phase 2: Virtual Relay is Now Default

The virtual endpoint relay graduates from shadow/opt-in to default mode.

#### 1. Default Virtual Endpoints

`ipc.resolve` now returns the virtual relay socket by default when a relay is
active for the resolved primal. The `prefer_virtual` serde field defaults to
`true` (was `false` in Phase 1).

**Opt-out**: Clients pass `"native": true` to bypass relay and get the raw
native socket path directly.

**Backward compatibility**: Existing callers that never set `virtual: true`
now automatically get relay traffic — they don't need code changes since the
socket is just a path.

#### 2. BTSP Session Validation

Relay connections now validate `_btsp_session` fields:
- Requests with valid (non-empty) `_btsp_session`: PASS
- Requests without `_btsp_session`: PASS (backward compat / standalone)
- Requests with empty `_btsp_session`: REJECT (-32600)

Full cryptographic validation (Ed25519 signature check against BearDog session
tokens) deferred until BearDog BTSP Phase 4.

#### 3. Performance Metrics

Atomic counters track relay overhead:
- `RelayMetrics.requests`: total relayed request count
- `RelayMetrics.overhead_us`: cumulative microseconds (includes serialization + native I/O)
- `RelayMetrics.avg_overhead_us()`: per-request average

New `ipc.relay_stats` JSON-RPC method returns:
```json
{
  "active_relays": 3,
  "relays": [{"primal": "beardog", "socket": "/run/user/.../beardog.sock"}],
  "total_requests": 1024,
  "avg_overhead_us": 342,
  "total_overhead_us": 350208
}
```

Target: <5ms (5000μs) average for same-subnet relay. Actual measured overhead
is dominated by UDS round-trip to native endpoint.

#### 4. Connection Pooling (Phase 1 — Already Complete)

Per-session persistent `NativeConn` with auto-reconnect. No per-request
connection establishment overhead.

---

## Test Results

- `songbird-universal-ipc`: 543 tests (incl. 4 new: 3 BTSP validation + 1 metrics)
- `songbird-types`: 560 tests
- `songbird-orchestrator`: 1751 tests
- Zero clippy warnings workspace-wide

---

## Files Changed

| File | Change |
|------|--------|
| `songbird-universal-ipc/src/service/virtual_relay.rs` | Phase 2 header, metrics, BTSP validation |
| `songbird-universal-ipc/src/service_types.rs` | `prefer_virtual` default flipped to `true` |
| `songbird-universal-ipc/src/service/ipc_registry.rs` | `handle_relay_stats` method |
| `songbird-universal-ipc/src/service/dispatch.rs` | Wire `ipc.relay_stats` |
| `songbird-types/src/json_rpc_method/domain_methods.rs` | `IpcMethod::RelayStats` |
| `songbird-types/src/json_rpc_method/mod.rs` | String mappings for `ipc.relay_stats` |

---

## Architecture After Phase 2

```
Client (primal) ─── ipc.resolve ──→ Songbird
                                     │
                    "native: true" ←─┤── returns native socket directly
                                     │
                    default ←────────┤── returns virtual relay socket
                                     │
                                     ▼
Client ──── virtual relay socket ──→ Songbird VirtualRelayManager
                                     │ (BTSP validation, metrics)
                                     ▼
                              native primal socket
```

---

## Remaining for Phase 3 (Horizon)

- Full BTSP crypto validation (Ed25519 signature check on `_btsp_session`)
- TLS termination (Songbird absorbs Caddy's Channel 3)
- Cross-subnet relay via TURN (southGate ↔ eastGate)
