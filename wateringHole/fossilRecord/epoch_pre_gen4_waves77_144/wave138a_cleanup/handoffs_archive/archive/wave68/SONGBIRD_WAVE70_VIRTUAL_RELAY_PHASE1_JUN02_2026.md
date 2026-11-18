# Songbird Wave 70 — Virtual Endpoint Relay Phase 1

**Date**: June 2, 2026  
**Version**: v0.2.4-wave70  
**Gate**: southGate  
**Design Reference**: `SONGBIRD_VIRTUAL_ENDPOINT_RELAY_DESIGN.md`

---

## Summary

Phase 1 (shadow mode) of the virtual endpoint relay. Songbird now creates
per-primal relay UDS sockets alongside native endpoints. Traffic can be
optionally routed through Songbird for centralized audit, rate limiting,
and Dark Forest enforcement.

## Architecture

```
BEFORE:  Client → ipc.resolve → native UDS → direct connection to primal
AFTER:   Client → ipc.resolve(virtual:true) → songbird/virtual/primal.sock → Songbird → native UDS
```

## New Files

### `crates/songbird-universal-ipc/src/service/virtual_relay.rs`
- `VirtualRelayManager`: manages per-primal relay lifecycle
- `relay_accept_loop`: tokio accept loop per virtual socket
- `relay_connection`: NDJSON streaming proxy (multi-request sessions)
- `forward_single_request` / `forward_inner`: request→native→response relay
- 4 tests: path format, lifecycle, full round-trip with mock provider

## Modified Files

### `crates/songbird-universal-ipc/src/service/mod.rs`
- Added `pub mod virtual_relay`
- Added `virtual_relay: Arc<VirtualRelayManager>` field to `IpcServiceHandler`

### `crates/songbird-universal-ipc/src/service/construction.rs`
- Initializes `VirtualRelayManager::new(default_base_dir())` in `assemble()`

### `crates/songbird-universal-ipc/src/service/ipc_registry.rs`
- `handle_register`: after registry insert, calls `virtual_relay.start_relay()`
- `handle_resolve`: checks `params.prefer_virtual` / `params.native`, returns
  relay socket path when virtual is requested and relay is active

### `crates/songbird-universal-ipc/src/service_types.rs`
- `ResolveParams`: added `prefer_virtual: bool`, `native: bool`
- `ResolveResult`: added `relay: bool`, `relay_socket: Option<String>`

## Wire Contract

```json
// ipc.resolve with virtual opt-in (Phase 1)
REQUEST:  { "primal_id": "beardog", "virtual": true }
RESPONSE: {
  "socket": "/run/user/1000/biomeos/songbird/virtual/beardog.sock",
  "virtual_endpoint": "/primal/beardog",
  "native_endpoint": "unix:///run/user/1000/biomeos/beardog-ecoPrimal.sock",
  "capabilities": ["security", "crypto", "auth"],
  "relay": true,
  "relay_socket": "/run/user/1000/biomeos/songbird/virtual/beardog.sock"
}

// ipc.resolve without virtual (default behavior, Phase 1)
REQUEST:  { "primal_id": "beardog" }
RESPONSE: {
  "socket": "/run/user/1000/biomeos/beardog-ecoPrimal.sock",
  "virtual_endpoint": "/primal/beardog",
  "native_endpoint": "unix:///run/user/1000/biomeos/beardog-ecoPrimal.sock",
  "capabilities": ["security", "crypto", "auth"],
  "relay": false,
  "relay_socket": "/run/user/1000/biomeos/songbird/virtual/beardog.sock"
}

// Force native (bypass relay even in Phase 2+)
REQUEST:  { "primal_id": "beardog", "native": true }
RESPONSE: { ... "relay": false, "relay_socket": null ... }
```

## Phase 1 Limitations (intentional)

- Virtual is opt-in (`"virtual": true` required)
- No BTSP session validation on relay traffic (Phase 2)
- No rate limiting (Phase 2)
- No Dark Forest enforcement (Phase 3)
- Relay opens fresh UDS connection per request (no connection pooling yet)

## Verification

```
cargo check -p songbird-universal-ipc       # zero errors
cargo clippy -p songbird-universal-ipc      # zero warnings
cargo test -p songbird-universal-ipc --lib  # 533 passed, 0 failed
cargo test -- virtual_relay                 # 4 targeted tests pass
```

## Next Steps (Phase 2)

- `ipc.resolve` returns virtual by default (flip the default)
- BTSP session validation on relay traffic
- Connection pooling to native endpoints
- primalSpring CompositionContext update to prefer virtual_endpoint
- Performance baselining (relay overhead measurement)

---

*Handoff for primalSpring cascade validation.*
