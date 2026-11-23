# BTSP Transport Signal Specification

**Date**: Aug 3, 2026 | **Wave**: 156b | **Author**: eastGate overwatch
**Status**: IMPLEMENTED — cellMembrane `signal.rs` + `ribocipher.rs`

---

## Overview

All primal-to-primal UDS (Unix Domain Socket) JSON-RPC communication in the
ecoPrimals ecosystem uses a 2-byte transport signal prefix called the
**riboCipher clear signal**. This prefix tells the receiving primal which
protocol the caller will use, enabling the server to multiplex different
transport modes on a single socket.

## Signal Format

```
Byte 0: 0xEC  — "ecoPrimals Clear" signal (always 0xEC for cleartext)
Byte 1: 0x01  — Protocol: NDJSON JSON-RPC
```

The constant `CLEAR_JSONRPC` is defined in `cellmembrane-types/src/signal.rs`:

```rust
pub const CLEAR_JSONRPC: [u8; 2] = [prefix::CLEAR, protocol::JSONRPC];
// => [0xEC, 0x01]
```

## How It Works

### Caller (client) side

Before sending the JSON-RPC payload, prepend `[0xEC, 0x01]`:

```
[0xEC][0x01]{"jsonrpc":"2.0","method":"health","id":1}\n
```

cellMembrane's `jsonrpc::raw()` handles this automatically when
`with_signal: true` is passed.

### Receiver (server) side

On accepting a UDS connection, peek the first 2 bytes:

```rust
use cellmembrane_types::signal::{peek_signal, SignalResult};

match peek_signal(&first_bytes) {
    SignalResult::Clear(protocol::JSONRPC) => {
        // Strip 2-byte prefix, process JSON-RPC
    }
    SignalResult::Unsignalled => {
        // Legacy: no prefix, attempt raw JSON-RPC parse
    }
    SignalResult::Encrypted(_) => {
        // BTSP encrypted channel (future)
    }
}
```

### Policy: Unsignalled connections

Each primal declares an `UnsignalledPolicy` for connections that arrive
without the 2-byte prefix:

| Policy | Behavior |
|--------|----------|
| `Accept` | Allow raw JSON-RPC without prefix (backward compatible) |
| `Reject` | Return error — require `0xEC 0x01` prefix |
| `AcceptWithWarning` | Allow but log a warning (transitional) |

## Protocol Byte Table

| Byte | Constant | Protocol |
|------|----------|----------|
| `0x01` | `JSONRPC` | NDJSON JSON-RPC 2.0 |
| `0x02` | `MSGPACK_RPC` | MessagePack-RPC (reserved) |
| `0x03` | `GRPC` | gRPC-over-UDS (reserved) |
| `0x04` | `CBOR_RPC` | CBOR-RPC (reserved) |
| `0x05` | `TARPC` | TarPC (used by toadStool compute) |
| `0x06` | `RAW_BINARY` | Raw binary stream (reserved) |
| `0x07` | `MESH_RELAY` | songBird mesh relay (inter-gate) |

## Prefix Byte Table

| Byte | Meaning |
|------|---------|
| `0xEC` | Clear (unencrypted) — ecoPrimals standard |
| `0xED` | Encrypted (BTSP handshake follows) |
| Other | Unsignalled — assume raw protocol |

## Primal Transport Requirements

Primals that require the `0xEC 0x01` prefix:

| Primal | Socket | Prefix Required? | Notes |
|--------|--------|-------------------|-------|
| **sweetGrass** | `sweetgrass.sock` | **Yes** | Strict: rejects unsignalled with `-32002` |
| **bearDog** | `beardog.sock` | Yes | BTSP handshake for crypto sockets |
| **rhizoCrypt** | `rhizocrypt.sock` | Yes | Certificate operations |
| **loamSpine** | `loamspine.sock` | Yes | Ledger operations |
| **squirrel** | `squirrel.sock` | Recommended | Signal dispatch |
| **petalTongue** | `petaltongue.sock` | No | Accepts raw JSON-RPC + REST `:3001` fallback |
| **nestGate** | `nestgate.sock` | No | CAS accepts raw |
| **toadStool** | `toadstool.sock` | No | Server mode accepts raw |
| **songBird** | `songbird.sock` | No | Mesh hub accepts raw |

## Integration Pattern

For a new primal connecting to sweetGrass:

```rust
// Using cellMembrane's jsonrpc module (recommended)
let result = membrane_shadow::jsonrpc::call(
    Path::new("/run/membrane/sweetgrass.sock"),
    "braid.batch_create",
    &params,
).await?;

// Manual (if not using cellMembrane)
let mut stream = UnixStream::connect("/run/membrane/sweetgrass.sock").await?;
stream.write_all(&[0xEC, 0x01]).await?;          // signal prefix
stream.write_all(json_rpc_request.as_bytes()).await?;
stream.write_all(b"\n").await?;                   // NDJSON delimiter
// read response...
```

## Discovery and Fallback

The recommended connection sequence (from esotericWebb V26 patterns):

1. **XDG user socket** — `$XDG_RUNTIME_DIR/membrane/<primal>.sock`
2. **membrane standard** — `/run/membrane/<primal>.sock`
3. **env override** — `${PRIMAL}_SOCKET_PATH`
4. **TCP well-known** — `127.0.0.1:<primal_port>`
5. **HTTP REST** — `http://127.0.0.1:<primal_port>/health`

For UDS connections, try with `[0xEC, 0x01]` prefix first. If the primal
returns error code `-32002` (transport error), it may require BTSP
encrypted transport instead.

---

*This spec documents the transport signal layer that enables the ecoPrimals
primal-to-primal IPC composition. All primals should declare their transport
requirements in their capability manifests so the biomeOS compositor can
wire connections correctly.*
