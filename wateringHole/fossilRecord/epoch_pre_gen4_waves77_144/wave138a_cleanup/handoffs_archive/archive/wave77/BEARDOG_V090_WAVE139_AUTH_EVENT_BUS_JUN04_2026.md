# bearDog — Wave 139: Auth Event Bus + tarpc Cleanup

**Date**: Jun 4, 2026
**Version**: 0.9.0
**Wave**: 139
**Tests**: 14,999 passing (169 suites, 0 failures)
**Methods**: 226 dispatchable (218 registry + 8 pre-dispatch gate)

---

## Delivered — strandGate FRAGO Response

### FRAGO: `wave76c-beardog-auth-events-subscribe`

**Selected**: Option C (poll-based) via `auth.events.poll`. Simplest for immediate
delivery. Broadcast channel is wired for future streaming upgrade (Option A).

### 1. Auth Event Bus (`auth_event_bus.rs`)

New module in `beardog-tunnel`:

- **`AuthEventKind`** — 5 variants matching rhizoCrypt's wire DTOs:
  - `TrustIssuerRegistered { issuer_did, issuer_fingerprint, trust_method }`
  - `KeyExchangeCompleted { remote_gate, method }`
  - `FamilyEnrollment { family_id, primal_count }`
  - `MeshJoin { mesh_id }`
  - `MeshLeave { mesh_id, reason }`

- **`AuthEvent`** — struct: `kind`, `source_gate`, `timestamp` (unix seconds)

- **`AuthEventBus`** — thread-safe bounded ring buffer (`VecDeque`) + `tokio::sync::broadcast`
  - `emit()` — appends to buffer (evicts oldest if full) + broadcasts
  - `poll_since(timestamp)` — returns events >= timestamp
  - `subscribe()` — returns `broadcast::Receiver` for future streaming
  - Capacity configurable (default 10,000; aligns with `event_bus_capacity` config)

### 2. `auth.events.poll` RPC Method

Gate-handled (Protected). Wired via `dispatch_auth_method` in `method_gate.rs`.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "auth.events.poll",
  "params": { "since_timestamp": 1717500000 },
  "id": 1
}
```

**Response:**
```json
{
  "events": [
    {
      "kind": {
        "type": "TrustIssuerRegistered",
        "payload": {
          "issuer_did": "did:key:z6Mk...",
          "issuer_fingerprint": "aabbccdd...",
          "trust_method": "family_seed"
        }
      },
      "source_gate": "beardog",
      "timestamp": 1717500042
    }
  ],
  "count": 1,
  "since_timestamp": 1717500000
}
```

### 3. Event Emission

`handle_auth_trust_issuer` now emits `TrustIssuerRegistered` on successful registration.
This completes the first link in the provenance chain:

```
auth.trust_issuer (bearDog) → TrustIssuerRegistered event
  → auth.events.poll (rhizoCrypt polls) → DAG record
    → loamSpine → sweetGrass
```

### 4. tarpc Cleanup

- Removed stale tarpc references from 10+ doc comments
- Deleted orphan `multi_transport_tests.rs` (references deleted APIs)
- Updated test fixtures from `"tarpc"` to `"json-rpc"` protocol
- `Protocol::Tarpc` enum retained in `beardog-ipc` for binary frame detection

---

## rhizoCrypt Integration Guide

rhizoCrypt's `MeshEventListener` should poll bearDog at the signing endpoint (UDS):

1. Connect to bearDog's UDS at startup (as currently implemented)
2. Authenticate via `auth.issue_ionic` / existing BTSP token
3. Poll periodically: `auth.events.poll` with `since_timestamp` of last seen event
4. Deserialize events — the wire format matches `MeshTrustEvent` DTOs exactly

Future upgrade path: when bearDog adds `auth.events.subscribe` (Option A streaming),
rhizoCrypt can switch from polling to streaming by subscribing once and receiving
JSON-RPC notifications.

---

## Remaining Work

| Item | Priority | Notes |
|------|----------|-------|
| S4 7-day gate graduation | P0 (passive) | Ends ~Jun 9 |
| Emit `KeyExchangeCompleted` events | P2 | When key exchange handlers exist |
| Emit `MeshJoin`/`MeshLeave` events | P2 | When mesh lifecycle is wired |
| `auth.events.subscribe` (streaming) | P3 | Broadcast channel ready |
| `Protocol::Tarpc` → `Protocol::Binary` rename | P3 | Dedicated wave |

---

## Quality Gates

- `cargo fmt` — clean
- `cargo clippy --workspace -- -D warnings` — 0 warnings
- `cargo test --workspace` — 14,999 passed, 0 failed, 169 suites
