# Protocol Negotiation Specification (G65)

**Date**: Aug 6, 2026 | **Wave**: 156k | **Author**: eastGate overwatch
**Status**: REFERENCE IMPLEMENTATION in squirrel — ecosystem standard pending adoption
**Origin**: squirrel (first primal) evolved this pattern independently; formalized as G65

---

## Overview

Protocol negotiation enables a primal to serve multiple RPC protocols on a
**single UDS socket**. The client announces which protocols it supports; the
server selects the best mutual match. If no negotiation occurs, JSON-RPC is
assumed (full backward compatibility).

This replaces the C2 dual-socket pattern (`.sock` + `.tarpc.sock`) as the
long-term architecture. C2 was a necessary stepping stone to deploy tarpc
listeners across the ecosystem. G65 unifies them back to a single socket
with protocol intelligence at connection time.

---

## Evolutionary Arc

| Phase | Pattern | Sockets per primal | Status |
|-------|---------|-------------------|--------|
| **Phase 1** | JSON-RPC only | 1 (`.sock`) | COMPLETE — all 15 primals |
| **Phase 2 (C2)** | Dual-socket | 2 (`.sock` + `.tarpc.sock`) | 13/15 shipped |
| **Phase 3 (G65)** | Protocol negotiation | 1 (`.sock`) | squirrel reference impl |

Phase 2 proved tarpc works at scale and gave cellMembrane concrete discovery
targets. Phase 3 eliminates the socket proliferation while preserving all
tarpc benefits.

---

## Wire Protocol

### Connection Handshake

```text
Client → Server: "PROTOCOLS: tarpc,jsonrpc\n"
Server → Client: "PROTOCOL: tarpc\n"
[Connection proceeds in selected protocol]
```

The negotiation is a **single round-trip** prepended to the connection. After
selection, the socket operates exclusively in the chosen protocol for the
lifetime of that connection.

### Backward Compatibility

If the first bytes from the client are NOT a `PROTOCOLS:` line, the server
assumes JSON-RPC. This means:

- Existing JSON-RPC clients work with **zero changes**
- Existing BTSP riboCipher-prefixed connections work unchanged
- Only clients that want tarpc need to send the negotiation line

The server uses a **100ms timeout** on the first line read. If no negotiation
line arrives within that window, the connection proceeds as JSON-RPC.

### Protocol Names

| Name | Wire value | Serialization | Use case |
|------|-----------|---------------|----------|
| `jsonrpc` | `"jsonrpc"` | serde_json | Default, diagnostics, browser, cross-language |
| `tarpc` | `"tarpc"` | bincode 2.x | Performance, type-safe, intra-gate composition |

Future protocols (e.g., `ribocipher-encrypted`, `quic`) extend the enum
without changing the negotiation wire format.

### Selection Algorithm

```rust
fn select_protocol(
    client_supported: &[IpcProtocol],
    server_supported: &[IpcProtocol],
) -> IpcProtocol {
    for client_proto in client_supported {
        if server_supported.contains(client_proto) {
            return *client_proto;
        }
    }
    IpcProtocol::JsonRpc // fallback — always supported
}
```

Client preference order wins. If the client sends `tarpc,jsonrpc` and the
server supports both, tarpc is selected. If the server only supports
JSON-RPC, the client gracefully falls back.

---

## Why This Is Better Than Dual-Socket

### 1. Socket Proliferation

C2 doubles the file descriptors per NUCLEUS gate:
- 15 primals × 2 sockets = 30 sockets in `/run/membrane/`
- 30 systemd `ExecStart` entries, 30 health checks, 30 cellMembrane registry entries

G65 returns to 15 sockets with no capability loss.

### 2. Protocol Transparency for Callers

With C2, the caller must decide which socket to connect to **before** the
call. This leaks protocol awareness into every consumer:

```rust
// C2 — caller decides protocol
let path = if use_tarpc {
    "/run/membrane/nestgate.tarpc.sock"
} else {
    "/run/membrane/nestgate.sock"
};
```

With G65, the caller just connects and asks for what it wants:

```rust
// G65 — server decides best match
let stream = UnixStream::connect("/run/membrane/nestgate.sock").await?;
let protocol = negotiate_client(&mut stream, vec![Tarpc, JsonRpc]).await?;
```

### 3. Graceful Capability Discovery

When a primal adds tarpc support for new methods, C2 requires clients to
know about the `.tarpc.sock` path. G65 discovers capabilities at connection
time — if the server gained tarpc since last call, the client auto-upgrades.

### 4. songBird Routing

songBird mesh routing becomes protocol-transparent. When routing cross-gate
calls, songBird can negotiate tarpc on high-bandwidth 10G links and fall
back to JSON-RPC on constrained links, without the caller knowing.

### 5. Future Protocols

The negotiation format is extensible. Adding a third protocol (QUIC,
encrypted riboCipher, etc.) requires no new socket files — just an
additional entry in the `PROTOCOLS:` line. Dual-socket scales linearly
(3 sockets, 4 sockets...); negotiation stays at 1.

---

## Relationship to BTSP and riboCipher

The BTSP transport signal (`0xEC 0x01`) is a byte-level protocol prefix
used for the existing JSON-RPC UDS framing. Protocol negotiation operates
at a higher layer — it's a text-line exchange that precedes the BTSP
framing. They compose cleanly:

```text
[TCP/UDS connect]
  → Protocol negotiation (text lines, optional)
    → BTSP signal bytes (per-message framing)
      → JSON-RPC or tarpc payload
```

When a connection negotiates tarpc, the BTSP signal is skipped — tarpc
uses its own bincode framing directly on the stream.

---

## Adoption Plan

### Phase 1: sourDough Reference Implementation

sourDough (standards holder, nascent spawning primal) implements protocol
negotiation as its own code — the **reference by example**. sourDough does
NOT publish a shared crate. Each primal reads the pattern and implements
it independently in their own codebase. This is how primals work: no
cross-primal code dependencies. Convergent evolution, not shared libraries.

squirrel's existing `protocol_negotiation.rs` (432 lines) serves as the
prior art. sourDough's implementation becomes the canonical pattern that
other teams study when adding G65 to their primal.

### Phase 2: Primal Adoption (Convergent Evolution)

Each primal adds protocol negotiation to its existing UDS listener.
Each team implements on their own timeline, reading the sourDough
reference and adapting to their own domain:

1. Add negotiation to the JSON-RPC socket listener (server side)
2. The existing tarpc server logic (from C2) handles tarpc connections
3. Remove the separate `.tarpc.sock` listener once negotiation is stable
4. cellMembrane registry drops `has_tarpc` field — all sockets negotiate

No primal imports code from another primal. The pattern propagates by
example, like bats, birds, and insects each evolving flight independently.

### Phase 3: cellMembrane Discovery Evolution

cellMembrane evolves from socket-path tracking to capability negotiation:

- `MembraneService` tracks `supported_protocols: Vec<IpcProtocol>`
  instead of `has_tarpc: bool`
- Health sweep connects once, negotiates, and reports protocol capabilities
- systemd units return to single `ExecStart` with one socket path

### Phase 4: songBird Cross-Gate Negotiation

songBird mesh relay gains protocol negotiation for inter-gate calls.
Cross-gate tarpc elevation becomes automatic — no configuration needed.

---

## Reference Implementation

squirrel `crates/main/src/rpc/`:

| File | Lines | Purpose |
|------|-------|---------|
| `protocol_negotiation.rs` | 432 | Core negotiation logic (client + server + tests) |
| `protocol.rs` | 215 | `IpcProtocol` enum + wire names |
| `tarpc_server.rs` | 389 | tarpc RPC server (delegates to JSON-RPC handlers) |
| `tarpc_client.rs` | 535 | tarpc RPC client |
| `tarpc_dispatch.rs` | 479 | tarpc method dispatch |
| `tarpc_service.rs` | 726 | `SquirrelRpc` trait definition |
| `tarpc_transport.rs` | 157 | Transport abstraction |
| **Total** | **2,933** | |

The negotiation itself is ~200 lines of logic + ~230 lines of tests. The
rest is squirrel-specific service implementation that each primal replaces
with its own domain methods.

---

## Interaction with Other Glacial Goals

| Goal | Interaction |
|------|-------------|
| **G64** (Cephalization) | G65 is Phase 3 of G64's dual-protocol convergence |
| **G60** (Federated CAS) | Protocol negotiation enables tarpc for high-throughput CAS ops |
| **G61** (Compute Memoization) | tarpc binary framing eliminates serde overhead for config transfer |
| **G56** (Neural API) | biomeOS capability routing can delegate protocol selection to negotiation |

---

*G65 — Protocol Negotiation. Single socket, best protocol, auto-negotiation.
squirrel evolved it first; the ecosystem converges to it as Phase 3 of
cephalization. C2 dual-socket was the stepping stone that proved tarpc
works at scale. G65 is the destination.*
