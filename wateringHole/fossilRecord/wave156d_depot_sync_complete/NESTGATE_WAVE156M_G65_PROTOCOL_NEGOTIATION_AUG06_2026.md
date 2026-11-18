# NestGate — G65 Protocol Negotiation (Wave 156m, Session 139)

**Date**: Aug 6, 2026
**Gate**: eastGate overwatch
**Primal**: nestGate 0.5.0
**Phase**: Phase 3 Cephalization (G65)

---

## Summary

NestGate implements G65 protocol negotiation on its primary Unix socket,
becoming the second primal (after squirrel reference impl) to ship Phase 3
cephalization. A single socket now handles both JSON-RPC and tarpc connections
via a lightweight text handshake. The C2 dual-socket pattern is retained for
backward compatibility.

## Changes

### New files
- `nestgate-rpc/src/rpc/ipc_protocol.rs` — `IpcProtocol` enum (JsonRpc, Tarpc)
  with wire-name parsing, display, and supported-protocol enumeration.
- `nestgate-rpc/src/rpc/protocol_negotiation.rs` — G65 wire format:
  `ProtocolRequest`/`ProtocolResponse` types, `negotiate_client()`,
  `select_protocol()`, `read_negotiation_line()` (byte-level reader to avoid
  BufReader read-ahead). 100ms negotiation timeout.

### Modified files
- `transport_stream.rs` — Added `TransportStream::peek()` using
  `rustix::net::recv(PEEK)` for non-destructive first-byte detection on Unix
  sockets (TCP delegates to `TcpStream::peek`).
- `isomorphic_ipc/server/mod.rs` — `TarpcStreamHandler` trait; `handle_connection`
  evolved: peek first byte → if `P` (0x50), run `try_g65_negotiation` → delegate
  to tarpc handler or fall through to JSON-RPC.
- `tarpc_server/mod.rs` — `handle_tarpc_negotiated()` accepts an already-connected
  stream (post-negotiation) and serves tarpc via bincode.
- `nestgate-bin/src/commands/service.rs` — `G65TarpcHandler` struct implementing
  `TarpcStreamHandler`; wired into NUCLEUS `start_socket_server` via
  `IsomorphicIpcServer::with_tarpc_handler`.
- `primal_announce.rs` — `endpoints.g65_negotiation: true` advertised in announce
  payload.
- `capability_registry.toml` — `transport_evolution` → `phase3-g65`;
  `protocol` → `["jsonrpc-2.0", "tarpc"]`; `g65_negotiation = true`.
- `Cargo.toml` (workspace) — `rustix` features: added `"net"`.

### Test results
- 6 new unit tests (ipc_protocol: 4, protocol_negotiation: 2) — all pass.
- Full `nestgate-rpc` test suite: 3 pre-existing failures unrelated to G65
  (mesh relay runtime-in-runtime panic, stale `content.ingest` assertion).
- Zero new clippy warnings.

## Wire Protocol (recap)

```
Client → Server:  PROTOCOLS: tarpc,jsonrpc\n
Server → Client:  PROTOCOL: tarpc\n
```

No negotiation line = legacy JSON-RPC client → server falls through to JSON-RPC.
100ms timeout on negotiation prevents stall from misbehaving clients.

## Backward Compatibility

- C2 dual-socket (`.tarpc.sock`) remains operational alongside the primary socket.
- Non-negotiating JSON-RPC clients connect as before — no behavior change.
- `primal.announce` still advertises `tarpc_uds` endpoint for C2 peers.

## Follow-up

- Ecosystem blurb update: nestGate moves from "C2 dual-socket SHIPPED" to "G65
  protocol negotiation SHIPPED" in the tarpc state table.
- Integration test with squirrel's G65 client (cross-primal negotiation).
- Once all primals ship G65, C2 dual-socket can be sunset.
