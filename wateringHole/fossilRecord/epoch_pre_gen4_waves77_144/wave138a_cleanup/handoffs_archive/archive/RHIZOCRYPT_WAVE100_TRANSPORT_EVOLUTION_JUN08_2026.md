# rhizoCrypt — Wave 100 Handoff: Transport Evolution (sourdough-core)

**Date**: 2026-06-08
**Version**: 0.14.3
**Wave**: 100
**Tests**: 1,683 (`--all-features`), 0 clippy, 0 unsafe
**Priority**: MEDIUM (per Wave 100 transport evolution trigger)

## Summary

Adopted `sourdough-core` `TransportEndpoint` standard for outbound IPC.
rhizoCrypt's mesh event listener and provenance notifier now use
`connect_transport()` instead of raw `TcpStream::connect()`, making them
transport-agnostic (UDS, TCP, or mesh relay).

## Changes

### 1. sourdough-core dependency

Added `sourdough-core = { path = "../sourDough/crates/sourdough-core" }` as
workspace dep. Re-exported `TransportEndpoint`, `TransportStream`, and
`connect_transport` from `rhizo-crypt-core` root.

### 2. Outbound IPC evolution (2 clients)

**MeshEventListener** (`types_ecosystem/mesh/listener.rs`):
- `endpoint` field: `SocketAddr` → `TransportEndpoint`
- `send_jsonrpc()`: `TcpStream::connect` → `connect_transport()`
- `TCP_NODELAY` applied only when `TransportStream::Tcp` (correct per type)
- `tokio::io::split()` replaces `TcpStream::into_split()` (works on any `AsyncRead+AsyncWrite`)

**ProvenanceNotifier** (`types_ecosystem/provenance/client.rs`):
- Same evolution pattern as mesh listener
- `connect()` fallback: accepts both legacy `host:port` and JSON `TransportEndpoint`

### 3. TRANSPORT_ENDPOINT env var

- `SafeEnv::TRANSPORT_ENDPOINT` constant added
- `SafeEnv::transport_endpoint()` helper parses JSON from env
- Logged at service startup when set
- `main.rs` doc updated to list it first

### 4. Remaining outbound TCP sites (future waves)

| Client | Pattern | Notes |
|--------|---------|-------|
| discovery/registry.rs | HTTP POST over TCP | Different protocol (HTTP, not NDJSON-RPC) |
| compute/client.rs | Reachability probe | Probe pattern, not sustained connection |
| songbird/connection.rs | tarpc connect | tarpc has its own transport abstraction |
| doctor.rs | Health check probe | Diagnostic tool, not production IPC |

These are lower priority — different protocols that need different treatment.

### 5. Self-binding status

TCP self-binding is already gated:
- `TcpListener::bind` in `jsonrpc/mod.rs` — only when `--port` is set
- `tarpc::tcp::listen` in `server.rs` — same gate
- `UnixListener::bind` in `uds.rs` — unconditional on Unix (correct)
- `--port` is Tier 5 fallback (standalone/debug only) per directive

## Key Files

- `Cargo.toml` — workspace dep added
- `crates/rhizo-crypt-core/src/lib.rs` — re-exports
- `crates/rhizo-crypt-core/src/types_ecosystem/mesh/listener.rs` — evolved
- `crates/rhizo-crypt-core/src/types_ecosystem/provenance/client.rs` — evolved
- `crates/rhizo-crypt-core/src/safe_env/mod.rs` — TRANSPORT_ENDPOINT
- `crates/rhizocrypt-service/src/lib.rs` — startup logging
- `crates/rhizocrypt-service/src/main.rs` — doc updated

## Ecosystem Parity (Wave 100)

- Zero clippy (pedantic + nursery) ✓
- Zero `#[allow]` in production ✓
- `config/capability_registry.toml` ✓
- `forbid(unsafe_code)` ✓
- `TRANSPORT_ENDPOINT` accepted ✓ (2/14 primals, with sporePrint)
- `sourdough-core` wired ✓
- Self-binding: 0 anti-patterns (TCP opt-in only)
