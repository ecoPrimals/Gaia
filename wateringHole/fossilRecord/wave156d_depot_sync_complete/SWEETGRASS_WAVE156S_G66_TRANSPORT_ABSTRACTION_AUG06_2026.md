# sweetGrass — G66 Transport Abstraction — Wave 156s AAR

**Date**: Aug 6, 2026 | **Gate**: eastGate | **Commit**: `ca8484e`
**Status**: SHIPPED — G66 transport abstraction live on main

---

## What Was Done

Implemented G66 Transport Abstraction Standard for sweetGrass. Eliminates
silicon deism — all platform conditionals (`#[cfg(unix)]`) are now confined
to the transport layer. Business logic never imports `tokio::net::UnixStream`
or makes platform assumptions.

### Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `platform_default()` | `sweet-grass-core/transport.rs` | Unix→UDS, non-Unix→TCP localhost |
| `from_env_or_default()` | `sweet-grass-core/transport.rs` | Env injection with platform fallback |
| `TransportListener` | `sweet-grass-service/transport_connect.rs` | Server-side bind+accept abstraction |
| `perform_client_handshake<S>` | `btsp_client.rs` | Generic over any `AsyncRead+AsyncWrite` |
| `CryptoDelegate.endpoint` | `crypto_delegate.rs` | Stores `TransportEndpoint`, uses `connect_transport()` |

### Metrics

| Metric | Before G66 | After G66 |
|--------|-----------|----------|
| Unconditional `UnixStream` imports (prod) | 1 (`btsp_client.rs`) | 0 |
| `#[cfg(unix)]` in business logic | 0 (already clean) | 0 |
| Transport-generic BTSP handshake | No (`&mut UnixStream`) | Yes (`<S: AsyncRead+AsyncWrite+Unpin>`) |
| `CryptoDelegate` transport | Raw `PathBuf` + `UnixStream::connect` | `TransportEndpoint` + `connect_transport()` |
| Server-side abstraction | None | `TransportListener` (UDS + TCP) |

### Design Decisions

1. **Convergent evolution**: Pattern adapted from sourDough reference (no shared crate).
2. **`TransportEndpoint` in core**: Stays in `sweet-grass-core` for use across crates.
3. **`TransportListener`/`TransportStream` in service**: Runtime types with `tokio` deps.
4. **Backward compat**: `CryptoDelegate::with_socket()` still works (wraps in `TransportEndpoint::uds()`).
5. **Port derivation**: Non-Unix `platform_default()` uses deterministic hash-based port (10000–60000 range).

### Test Results

- 1,679 tests passing (+3 new transport tests)
- 0 clippy warnings
- All files ≤484L

---

## What This Enables

- **Windows cross-arch**: sweetGrass now compiles AND works on Windows via TCP fallback.
- **songBird routing**: `MeshRelay` variant ready for cross-gate transparent routing.
- **Future transports**: WebSocket, QUIC, named pipes — new `TransportStream` variants, zero business logic changes.

---

*sweetGrass G66 — silicon-agnostic IPC. The transport layer decides how bytes move.
Business logic just reads and writes. No more trusting that the silicon is always Linux.*
