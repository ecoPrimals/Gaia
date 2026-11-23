# Handoff: Songbird Wave 157e — MeshRelay Gossip + Test Hardening

**Date**: August 10, 2026  
**Primal**: songBird  
**Wave**: 157e  
**Gate**: eastGate  
**Status**: Complete — pushed to golgiBody

---

## Summary

Wave 157e delivers two primary capabilities:

1. **MeshRelay Gossip Transport** — `gossip.relay` + `gossip.inject` RPC methods enable cross-gate gossip propagation through songBird's `:7700` federation mesh when swarmVine's direct TCP 7800 is unreachable.

2. **Dispatch Test Suite Hardening** — Fixed indefinite hangs in the dispatch test suite caused by real network IO (IGD SSDP, STUN UDP, Tor circuit building) and live UDS reads with no timeout. Suite runtime: 47s+ (or infinite hang) → 0.71s.

---

## What Was Done

### MeshRelay Gossip Transport

- Added `GossipMethod` enum (`Relay`, `Inject`) to `songbird-types` type system
- Created `dispatch/gossip.rs` module for `gossip.*` routing
- Implemented `handle_gossip_relay`:
  - Resolves target gate via `BeaconMesh::get_best_path()`
  - POSTs `gossip.inject` JSON-RPC to remote songBird's `:7700` federation port
  - Falls back to local injection for local/empty target
- Implemented `handle_gossip_inject`:
  - Discovers local swarmVine UDS socket
  - Injects gossip payload via JSON-RPC over UDS
- Updated `capability_registry.toml` with `gossip` capability section
- Updated introspection (`capability_tokens.rs`) with `network.gossip` + methods
- 4 unit tests covering relay/inject dispatch paths

### Test Suite Hardening

- **Root cause**: Dispatch tests were calling live network services (SSDP multicast for IGD, UDP STUN binding, Tor consensus fetch, TCP onion start) and a live UDS (`/run/user/1000/biomeos/security.sock`) with no read timeout — blocking indefinitely when services were present but unresponsive.
- **Fix (tests)**: Introduced `dispatched!` macro wrapping all real-network-IO calls with `tokio::time::timeout(Duration::from_millis(100), ...)`. Verifies dispatch arm routing without waiting for full network operation timeouts.
- **Fix (production)**: Added 5-second `tokio::time::timeout` around `stream.read_to_end()` in `SecurityRelayAuthority::call_security_rpc()` — prevents indefinite blocking against unresponsive security provider sockets.

### RiboCipher Tier 2 Chain Closing (Wave 157d, this session)

- Federation port `:7700` now accepts `0xED` riboCipher framing with full `IpcServiceHandler` dispatch
- Replaces previous stub `dispatch_federation_rpc()` with `dispatch_ribocipher_rpc()` that routes all methods through the handler
- Intrinsic methods (`health.liveness`, `health`, `ping`, `system.capabilities`) handled directly
- Unit tests updated and passing

---

## Files Changed

| Crate | File | Change |
|-------|------|--------|
| `songbird-types` | `src/json_rpc_method/domain_methods.rs` | `GossipMethod` enum |
| `songbird-types` | `src/json_rpc_method/mod.rs` | `Gossip(GossipMethod)` variant + wire mappings |
| `songbird-universal-ipc` | `src/service/dispatch/gossip.rs` | New dispatch module |
| `songbird-universal-ipc` | `src/service/dispatch/mod.rs` | Gossip arm in dispatch table |
| `songbird-universal-ipc` | `src/service/gossip_relay.rs` | Handler implementation |
| `songbird-universal-ipc` | `src/service/dispatch/tests.rs` | `dispatched!` macro + timeout fences |
| `songbird-universal-ipc` | `src/introspection/capability_tokens.rs` | `network.gossip` capability |
| `songbird-lineage-relay` | `src/security/relay_authority.rs` | 5s read timeout on UDS |
| `songbird-orchestrator` | `src/app/http_server.rs` | riboCipher dispatch rewrite |
| Root | `config/capability_registry.toml` | `[capabilities.gossip]` section |

---

## Verification

```
cargo clippy -p songbird-universal-ipc -D warnings  ✓
cargo clippy -p songbird-lineage-relay -D warnings   ✓
cargo test -p songbird-universal-ipc                 ✓ (0.71s)
cargo test -p songbird-lineage-relay                 ✓
cargo test -p songbird-orchestrator                  ✓
```

---

## Upstream Notes for Overwatch

- **swarmVine team**: songBird now accepts `gossip.inject` on local UDS — swarmVine can directly receive cross-gate gossip from songBird's MeshRelay without any changes. The `gossip.inject` payload format is `{topic, key, payload, origin_gate}`.
- **biomeOS team**: P1 FD exhaustion (`LimitNOFILE=65536`) confirmed as biomeOS-level responsibility for fleet-wide deployment.
- **Test infra note**: Any new dispatch test arms that call real network services should use the `dispatched!` macro pattern to avoid future CI hangs.
