# cellMembrane Team — Wave 123 Handoff: relay.forward Graduation

**Date**: Jun 22, 2026 | **Wave**: 123 | **From**: sporeGate Overwatch
**Status**: `TransportEndpoint::MeshRelay` is now wired end-to-end

---

## What Shipped

### relay.forward Handler (songBird)

The integration gap between cellMembrane's `call_via_relay` and songBird's cross-gate transport is closed.

**Before**: `resolve_endpoint()` built `MeshRelay{peer_id, capability}` endpoints. `call_endpoint()` dispatched to `call_via_relay()`. But songBird had no `relay.forward` method — the request hit a dead end.

**After**: songBird accepts `relay.forward` JSON-RPC requests on its UDS socket, extracts the envelope (`{peer_id, capability, payload}`), and routes through its existing `forward_to_remote_gate` infrastructure (TCP direct → TURN relay fallback).

**Files changed** (songBird):
- `songbird-types/src/json_rpc_method/domain_methods.rs` — `RelayMethod::Forward`
- `songbird-types/src/json_rpc_method/mod.rs` — parse + display
- `songbird-universal-ipc/src/service/dispatch/network.rs` — dispatch route
- `songbird-universal-ipc/src/service/remote_dispatch.rs` — `handle_relay_forward()`
- `songbird-universal-ipc/src/introspection/` — rpc.rs, capability_tokens.rs, identity_payloads.rs

**Test status**: All songBird tests pass (unit + integration + local infrastructure CI). All cellMembrane tests pass (769 tests).

---

## Call Chain (Now Complete)

```
cellMembrane primal (e.g. membrane cascade)
  └─ resolve_endpoint(ctx, "ironGate", CryptoSigner)
       └─ returns TransportEndpoint::MeshRelay { peer_id: "ironGate", capability: "cryptosigner" }
            └─ call_endpoint(endpoint, request)
                 └─ call_via_relay("ironGate", "cryptosigner", request)
                      └─ JSON-RPC to songbird.sock:
                           { "method": "relay.forward", "params": { "peer_id": "ironGate", "capability": "cryptosigner", "payload": "<request>" } }
                                └─ songBird handle_relay_forward()
                                     └─ forward_to_remote_gate() → TCP to ironGate's songBird → TURN fallback
                                          └─ capability.call on remote gate (routing: "local")
```

---

## What cellMembrane Needs to Do Next

### 1. Wire `call_endpoint` Into Active Callers
`call_endpoint()` in `jsonrpc.rs` is implemented but **not yet called** by any membrane-shadow operation. The bridge code and impulse relay still use direct UDS paths. Wire `resolve_endpoint` + `call_endpoint` into:
- `bridge.rs` — `try_bridge()` should resolve+call instead of hardcoded socket paths
- `impulse/primal.rs` — `try_relay_impulse()` should use `call_endpoint` for cross-gate delivery
- `sovereignty_ledger.rs` — `rootpulse_commit()` could resolve neural-api endpoint instead of assuming local

### 2. TCP Transport Stub
`call_endpoint` returns `Err("TCP transport not yet implemented")` for `TransportEndpoint::Tcp`. For WireGuard-reachable peers, this is the direct fast path. Implement raw TCP JSON-RPC (similar to songBird's `http_post_jsonrpc` but via NDJSON stream).

### 3. Transport Envelope Phase 2 Integration
The Sovereign Transport Envelope impulse (`impulses/active/2026-06-22T07-40_sporeGate__wave121-sovereign-transport-envelope.toml`) outlines 4 phases. Phase 3 (this graduation) is done. Phase 4 involves Dark Forest protocol beacons — that's further out. Phase 2 (songBird relay on golgi-ext) is a flockGate/songBird task.

### 4. skunkBat Consumer Fix
`skunkBat/crates/skunk-bat-integrations/src/rpc.rs` has its own `call_endpoint` that explicitly errors on `MeshRelay`. Should be updated to delegate to songBird via the same `relay.forward` path, or import cellMembrane's `call_endpoint`.

---

## Infrastructure Context

- **[ISP] Passthrough now live**: sporeGate is the true WAN edge (`[NUCLEUS_WAN]`). No more double-NAT. WireGuard on port 51821 ([ISP] BGW320 UDP bug workaround).
- **Quorum Phase 1 running**: golgi pulls from Forgejo every 15 min and relays to GitHub. Autonomous cascade is operational.
- **IPC audit completed**: UDS dominates local primal communication. Network-facing services are songBird (relay infrastructure) and rustdesk (remote access). Transport envelope work is for multi-hop privacy, not plaintext exposure.

---

*This handoff enables cellMembrane to wire `relay.forward` into active transport paths. The plumbing is laid — the abstraction layer needs callers.*
