# Transport Abstraction Specification (G66)

**Date**: Aug 6, 2026 | **Wave**: 156s | **Author**: eastGate overwatch
**Status**: REFERENCE IMPLEMENTATION in sourDough — ecosystem standard pending adoption
**Origin**: sourDough (standards holder) already implements the full pattern; formalized as G66 after Windows cross-arch failures exposed silicon deism in 7/15 primals

---

## Overview

Transport abstraction eliminates silicon deism — the implicit assumption that
the underlying platform is Unix. Primals express *what* they connect to (a
service, a capability) without encoding *how* bytes move. The transport layer
selects the best available mechanism for the current platform and topology.

This is not a new library or shared crate. sourDough's `transport/` module
is the reference *by example*. Each primal reads the pattern and implements
it independently in their own codebase. Convergent evolution, not shared
dependencies.

---

## The Problem: Silicon Deism

G65 protocol negotiation was a protocol-level success (15/15 primals). But
the implementation exposed a deeper violation: 7/15 primals imported
`tokio::net::UnixStream`, `rustix`, or `std::os::unix` unconditionally in
their IPC modules. These primals assume — without questioning — that the
silicon underneath is always Linux.

```rust
// Silicon deism: the code trusts that Unix exists.
// Compiles on Linux. Fails on Windows. Dead on WASM.
use tokio::net::UnixStream;

pub async fn connect(path: &str) -> io::Result<UnixStream> {
    UnixStream::connect(path).await
}
```

The 8 primals that built on Windows didn't have a better abstraction — they
just had less IPC code. The fix isn't `#[cfg(unix)]` guards (that's
arch-exclusion, not arch-abstraction). The fix is a transport layer that
makes the platform decision at runtime, not compile time.

---

## The Pattern: Transport Injection

sourDough already implements this fully. Three components:

### 1. `TransportEndpoint` — Where to connect (platform-neutral)

An enum describing the *destination* without prescribing the transport:

```rust
#[derive(Serialize, Deserialize)]
#[serde(tag = "transport")]
pub enum TransportEndpoint {
    #[serde(rename = "uds")]
    Uds { path: String },

    #[serde(rename = "tcp")]
    Tcp { host: String, port: u16 },

    #[serde(rename = "mesh_relay")]
    MeshRelay { peer_id: String, capability: String },
}
```

The primal never constructs this directly in production. The launcher,
biomeOS, or songBird decides the transport and injects it via environment:

```text
TRANSPORT_ENDPOINT='{"transport":"uds","path":"/run/membrane/beardog.sock"}'
TRANSPORT_ENDPOINT='{"transport":"tcp","host":"127.0.0.1","port":7700}'
```

Key method: `platform_default()` — on Unix, returns UDS. On non-Unix,
returns TCP localhost. No `#[cfg]` in the caller.

### 2. `TransportStream` — The connected byte pipe (platform-aware)

```rust
pub enum TransportStream {
    #[cfg(unix)]
    Unix(tokio::net::UnixStream),

    Tcp(tokio::net::TcpStream),
}
```

Implements `AsyncRead + AsyncWrite`. The `#[cfg(unix)]` is here — in the
transport layer — not scattered across every IPC module. Business logic
receives a `TransportStream` and reads/writes bytes without knowing what's
underneath.

### 3. `connect_transport()` — The bridge

```rust
pub async fn connect_transport(
    endpoint: &TransportEndpoint,
) -> io::Result<TransportStream> {
    match endpoint {
        #[cfg(unix)]
        TransportEndpoint::Uds { path } => {
            let stream = tokio::net::UnixStream::connect(path).await?;
            Ok(TransportStream::Unix(stream))
        }
        #[cfg(not(unix))]
        TransportEndpoint::Uds { path } => Err(io::Error::new(
            io::ErrorKind::Unsupported,
            format!("UDS not available on this platform for {path}"),
        )),
        TransportEndpoint::Tcp { host, port } => {
            let stream = tokio::net::TcpStream::connect(
                format!("{host}:{port}")
            ).await?;
            Ok(TransportStream::Tcp(stream))
        }
        TransportEndpoint::MeshRelay { .. } => Err(io::Error::new(
            io::ErrorKind::Unsupported,
            "mesh relay requires songBird routing",
        )),
    }
}
```

All platform conditionals live in this one function and the `TransportStream`
enum. Everything above — protocol negotiation, JSON-RPC, tarpc, BTSP,
riboCipher — operates on the `TransportStream` trait object.

---

## Server Side: `TransportListener`

The same pattern applies to the server (listener) side. sourDough's
`RiboCipherAcceptLoop` currently accepts on `UnixListener`. The G66
evolution adds:

```rust
pub enum TransportListener {
    #[cfg(unix)]
    Unix(tokio::net::UnixListener),

    Tcp(tokio::net::TcpListener),
}

impl TransportListener {
    pub async fn accept(&self) -> io::Result<TransportStream> {
        match self {
            #[cfg(unix)]
            Self::Unix(l) => {
                let (stream, _) = l.accept().await?;
                Ok(TransportStream::Unix(stream))
            }
            Self::Tcp(l) => {
                let (stream, _) = l.accept().await?;
                Ok(TransportStream::Tcp(stream))
            }
        }
    }
}
```

G65 protocol negotiation then operates on `TransportStream` regardless of
whether the connection arrived via UDS or TCP:

```rust
// G65 + G66 composed: protocol negotiation on any transport
let stream: TransportStream = listener.accept().await?;
let protocol = negotiate_server(&mut stream).await?;
match protocol {
    IpcProtocol::Tarpc => handle_tarpc(stream).await,
    IpcProtocol::JsonRpc => handle_jsonrpc(stream).await,
}
```

---

## What This Unlocks

### Immediate (this wave)

- **Windows cross-arch builds**: All 15 primals compile on Windows by
  falling back to TCP localhost. No dead `#[cfg(unix)]` stubs — the
  primals actually *work* on Windows.
- **macOS development**: Same UDS paths but different `/var/run` conventions.
  `resolve_socket_path()` handles it.

### Near-term

- **Port-aesthetic architecture**: songBird routes based on capability, not
  socket paths. Transport injection means a primal on gate A connects to a
  primal on gate B without knowing whether it's UDS (same gate), TCP (cross-
  gate 10G), or mesh relay (WAN).
- **BTSP local-trust (G63)**: `SO_PEERCRED` only exists on UDS. Transport
  abstraction lets the auth layer check `is_local()` on the endpoint and
  skip BTSP handshake for UDS connections without leaking that decision
  into business logic.

### Long-term

- **WASM/browser targets**: petalTongue in browser connects via WebSocket
  (new `TransportStream::WebSocket` variant). Same protocol negotiation,
  different transport.
- **QUIC**: Wide-area connections with built-in encryption. New variant,
  zero changes to protocol layer.
- **Named pipes**: Windows-native IPC (faster than TCP localhost). New
  variant when Windows becomes a first-class target.

---

## Relationship to Other Specs

| Spec | Relationship |
|------|-------------|
| **G65 (Protocol Negotiation)** | G65 negotiates *protocol* (tarpc vs JSON-RPC). G66 abstracts *transport* (UDS vs TCP vs mesh). They compose: negotiate protocol on any transport. |
| **BTSP Transport Signal** | riboCipher signal bytes (`0xEC 0x01`) are protocol-layer framing. They ride on top of `TransportStream` regardless of underlying transport. |
| **G63 (BTSP Local-Trust)** | `SO_PEERCRED` requires UDS. Transport abstraction exposes `is_local()` so auth can make trust decisions without knowing transport details. |
| **songBird mesh routing** | `MeshRelay` variant is the songBird entry point. songBird resolves capability → gate → transport, injecting the concrete endpoint. |
| **rustix** | `rustix` provides safe Unix syscall wrappers. With G66, `rustix` usage is confined to the transport layer (and OS-level utilities like uid/gid), not scattered across IPC modules. |

---

## Adoption Plan

### Phase 1: sourDough Reference (ALREADY DONE)

sourDough's `crates/sourdough-core/src/transport/` already implements:
- `TransportEndpoint` (UDS / TCP / MeshRelay) with `platform_default()`
- `TransportStream` with `#[cfg(unix)]` on `Unix` variant
- `connect_transport()` with `#[cfg(not(unix))]` error for UDS
- `from_env_or_default()` for transport injection
- Full test suite including proptest roundtrips
- Wire-compatible with `songbird_types::TransportEndpoint`

This IS the reference. No new code needed in sourDough.

### Phase 2: Primal Adoption (Convergent Evolution)

Each primal independently evolves their transport layer by studying
sourDough's pattern:

1. Create a `transport/` module with `TransportEndpoint`, `TransportStream`,
   `connect_transport()` — adapted to their domain
2. Refactor G65 protocol negotiation to operate on `TransportStream` instead
   of `tokio::net::UnixStream`
3. Refactor server listener to accept on `TransportListener`
4. Move all `rustix` usage into the transport layer (or OS utility modules)
5. Remove unconditional `tokio::net::Unix*` imports from IPC modules
6. Verify: `cargo build --target x86_64-pc-windows-gnu` passes

No primal imports code from another primal. The pattern propagates by
example.

### Phase 3: cellMembrane + biomeOS

- cellMembrane discovery evolves from socket paths to `TransportEndpoint`
  values in the registry
- biomeOS deploy graphs specify transport preferences per gate
- systemd units inject transport via `TRANSPORT_ENDPOINT` env var

### Phase 4: songBird Cross-Gate Transport Selection

songBird mesh routing selects transport based on topology:
- Same gate → UDS (fastest, `SO_PEERCRED` for local trust)
- Same LAN → TCP direct (10G link)
- Cross-WAN → QUIC or mesh relay
- Browser → WebSocket

The caller just says `connect_transport(&endpoint)`. songBird resolves
the best path.

---

## Anti-Patterns

### 1. Don't import `UnixStream` in business logic

```rust
// WRONG — silicon deism
use tokio::net::UnixStream;
let stream = UnixStream::connect("/run/membrane/foo.sock").await?;

// RIGHT — transport injection
let endpoint = TransportEndpoint::from_env_or_default("foo", None);
let stream = connect_transport(&endpoint).await?;
```

### 2. Don't use `#[cfg(unix)]` as the fix

```rust
// WRONG — arch exclusion (compiles on Windows but does nothing)
#[cfg(unix)]
mod ipc {
    pub async fn connect() -> UnixStream { ... }
}
#[cfg(not(unix))]
mod ipc {
    pub async fn connect() -> ! { unimplemented!() }
}

// RIGHT — transport abstraction (works on all platforms)
mod ipc {
    pub async fn connect(ep: &TransportEndpoint) -> TransportStream {
        connect_transport(ep).await
    }
}
```

### 3. Don't scatter `rustix` across modules

`rustix` is a Unix-specific crate. Confine it to:
- The transport layer (`TransportStream::Unix` construction)
- OS utility modules (uid/gid, process info)
- Guard both with `#[cfg(unix)]`

Everything else operates on platform-neutral types.

---

## Metrics

| Metric | Before G66 | After G66 |
|--------|-----------|----------|
| Windows cross-arch | 8/15 build | 15/15 build |
| `#[cfg(unix)]` locations | 0 (in 7 primals) | Confined to transport layer |
| Unconditional `UnixStream` imports | Scattered across IPC modules | Zero outside transport/ |
| Platform-neutral IPC | Accidental (less IPC code) | By design (TransportStream) |

---

*G66 — Transport Abstraction. Silicon-agnostic IPC. sourDough has the
reference. Each primal converges independently. `#[cfg(unix)]` lives in
the transport layer, not in business logic. UDS on Linux, TCP on Windows,
WebSocket in browser, QUIC on WAN — same protocol negotiation, same
business logic, different bytes-on-wire. The next step after cephalization:
the ecosystem stops trusting that the silicon is always Linux.*
