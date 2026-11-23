# barraCuda Wave 156p — G65 Protocol Negotiation

**Date**: 2026-08-06
**Gate**: eastGate
**HEAD**: `d92f571a`
**Status**: G65 SHIPPED

---

## What Was Done

Implemented G65 Protocol Negotiation per `PROTOCOL_NEGOTIATION_SPEC.md`. barraCuda
now supports single-socket protocol selection on all accept loops (UDS + TCP).

### Wire Protocol

```
Client → Server: PROTOCOLS: tarpc,jsonrpc\n
Server → Client: PROTOCOL: tarpc\n
```

Client preference wins. Legacy clients that skip negotiation default to JSON-RPC.

### New Modules

| File | LOC | Purpose |
|------|-----|---------|
| `ipc_protocol.rs` | 107 | `IpcProtocol` enum (JsonRpc, Tarpc) with feature-gated Tarpc variant |
| `protocol_negotiation.rs` | 258 | Wire types, `select_protocol()`, `try_negotiate()` server-side, `negotiate_client()` |
| `g65_protocol_negotiation.rs` | 172 | 4 E2E integration tests |

### Architecture

1. `serve_listener` accept loop peeks first byte via `TransportStream::peek()`
2. If `P` (0x50) → G65 negotiation path:
   - Read `PROTOCOLS:` line byte-by-byte (no BufReader over-read)
   - `select_protocol()` — client preference wins
   - Write `PROTOCOL: selected\n`
   - If tarpc → `handle_tarpc_negotiated()` wraps stream in serde_transport
   - If jsonrpc → fall through to existing BTSP guard + JSON-RPC path
3. If not `P` → existing BTSP guard + JSON-RPC path (backward compatible)

### Peek Implementation

- **TCP**: Native `TcpStream::peek()` (safe)
- **Unix**: `libc::recv(fd, buf, len, MSG_PEEK)` via `try_io` (single `unsafe` site)
- `#![forbid(unsafe_code)]` → `#![deny(unsafe_code)]` in barracuda-core
- `barracuda` crate retains `#![forbid(unsafe_code)]`

### Tests

| Test | What it validates |
|------|-------------------|
| `g65_negotiate_jsonrpc` | Client sends `PROTOCOLS: jsonrpc`, gets JSON-RPC, makes JSON-RPC call |
| `g65_negotiate_tarpc_then_call` | Client sends `PROTOCOLS: tarpc,jsonrpc`, gets tarpc, makes tarpc `health_liveness` + `identity_get` calls |
| `g65_backward_compat_legacy_jsonrpc` | Legacy client sends JSON directly, no negotiation, JSON-RPC works |
| `g65_protocols_list_advertises_negotiation` | `protocols.list` returns `negotiation.g65: true` |
| 17 unit tests | `IpcProtocol` roundtrip, `select_protocol` preference logic, wire format parsing |

### protocols.list Update

Now returns:
```json
{
  "negotiation": {
    "g65": true,
    "supported": ["tarpc", "jsonrpc"],
    "endpoint": "unix:///run/user/1000/biomeos/math.sock",
    "header": "PROTOCOLS: tarpc,jsonrpc"
  },
  "dual_socket": true,
  "protocols": [...]
}
```

---

## Cephalization Status

| Phase | Status |
|-------|--------|
| C2 (dual-socket) | COMPLETE (retained for backward compat) |
| **G65 (negotiation)** | **SHIPPED** |

---

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --all --check` | CLEAN |
| `cargo clippy --workspace --all-features` | ZERO warnings |
| `cargo check --target x86_64-pc-windows-gnu` | CLEAN |
| G65 integration tests | 4/4 pass |
| G65 unit tests | 17/17 pass |
| barracuda-core full suite | ALL pass |

---

## Upstream Notes

- C2 dual-socket (`.tarpc.sock`) retained during rollout for backward compat
- cellMembrane discovery evolution pending — will need to recognize `negotiation.g65: true`
- Other primals can reference barraCuda's `ipc_protocol.rs` and `protocol_negotiation.rs`
  as implementation examples (each primal implements independently per G65 standard)
