# Handoff: swarmVine Windows Platform Port

**Date**: Aug 9, 2026 | **Wave**: 157d | **From**: sporeGate topology
**To**: swarmVine primal team, eastGate overwatch
**Priority**: P2 (blocks blueGate running swarmVine as 16th primal on Windows)
**Pattern**: Same as songBird Wave 155i UDS-to-TCP platform gating

---

## Context

blueGate (primary Windows builder) built 14/14 primals from vertebrate HEAD.
swarmVine is the 16th primal and does not compile on Windows due to 6 direct
`tokio::net::UnixStream` / `UnixListener` call sites that bypass the G66
transport abstraction already present in `swarmvine-core/src/transport.rs`.

The transport abstraction (`TransportEndpoint`, `TransportStream`, `bind_transport`,
`connect_transport`) already handles `#[cfg(unix)]` / `#[cfg(not(unix))]` correctly.
The fix is to use it instead of raw Unix imports.

Additionally, `tarpc::serde_transport::unix` (UDS-only tarpc transport) needs
`#[cfg(unix)]` gating since tarpc's TCP transport is available but not wired.

---

## Call Sites Requiring Platform Gating

### 1. dispatch.rs — vine-bat skunkBat validation (line ~290)

**File**: `crates/swarmvine-server/src/dispatch.rs`
**Function**: `vine_bat_preaccept`

```rust
// CURRENT — raw UnixStream, won't compile on Windows
let Ok(Ok(stream)) = timeout(
    Duration::from_millis(500),
    tokio::net::UnixStream::connect(&sock_path),
).await

// FIX — use transport abstraction
let endpoint = swarmvine_core::transport::TransportEndpoint::Uds {
    path: sock_path.clone(),
};
let Ok(Ok(stream)) = timeout(
    Duration::from_millis(500),
    swarmvine_core::transport::connect_transport(&endpoint),
).await
// Then use tokio::io::split(stream) instead of stream.into_split()
```

Also gate `skunkbat_sock_path()` to return empty string on non-Unix
(sock file won't exist, early-returns before connect attempt).

### 2. server.rs — UDS listener bind (line ~55)

**File**: `crates/swarmvine-server/src/server.rs`
**Function**: `run` (inside `TransportEndpoint::Uds` match arm)

```rust
// CURRENT — raw UnixListener
let listener = tokio::net::UnixListener::bind(&socket_path)?;

// FIX — use transport abstraction (already handles cfg(unix))
let listener = swarmvine_core::transport::bind_transport(&endpoint).await?;
// listener.accept() returns TransportStream which implements AsyncRead+AsyncWrite
```

The `handle_connection<S>` and `handle_negotiated_connection<S>` are already
generic over `S: AsyncRead + AsyncWrite + Unpin` — `TransportStream` satisfies this.

### 3. tarpc_server.rs — tarpc UDS listener (line ~52-54)

**File**: `crates/swarmvine-server/src/tarpc_server.rs`
**Function**: `start_tarpc_listener`

```rust
// CURRENT — tarpc unix-only transport
let mut listener =
    tarpc::serde_transport::unix::listen(&socket_path, tokio_serde::formats::Bincode::default)
        .await?;

// FIX — gate entire function with #[cfg(unix)]
#[cfg(unix)]
pub(crate) async fn start_tarpc_listener(...) -> Result<()> {
    // existing implementation unchanged
}

#[cfg(not(unix))]
pub(crate) async fn start_tarpc_listener(...) -> Result<()> {
    info!("tarpc listener not available on this platform (UDS-only)");
    Ok(())
}
```

Also gate unix-only imports (`futures::StreamExt`, `tarpc::server`, etc.)
with `#[cfg(unix)]`.

### 4. tarpc_service.rs — tarpc UDS client connect (line ~83-84)

**File**: `crates/swarmvine-core/src/tarpc_service.rs`
**Function**: `connect`

```rust
// CURRENT — tarpc unix-only transport
let transport =
    tarpc::serde_transport::unix::connect(path, tokio_serde::formats::Bincode::default).await?;

// FIX — gate with #[cfg(unix)] / #[cfg(not(unix))]
#[cfg(unix)]
pub async fn connect(socket_path: Option<&str>) -> Result<SwarmVineServiceClient, std::io::Error> {
    // existing implementation unchanged
}

#[cfg(not(unix))]
pub async fn connect(_socket_path: Option<&str>) -> Result<SwarmVineServiceClient, std::io::Error> {
    Err(std::io::Error::new(
        std::io::ErrorKind::Unsupported,
        "tarpc UDS transport not available on this platform",
    ))
}
```

### 5. announce.rs — ALREADY GATED (no action needed)

`announce_to_biomeos` and `register_with_songbird` already have proper
`#[cfg(unix)]` / `#[cfg(not(unix))]` implementations. No changes needed.

### 6. spread.rs — ALREADY GATED (no action needed)

`query_songbird_peers` already has `#[cfg(unix)]` / `#[cfg(not(unix))]`
implementations. `spread_to_peer` uses TCP (cross-gate gossip). No changes needed.

---

## Cargo.toml Change

**File**: `Cargo.toml` (workspace root)

```toml
# CURRENT
tarpc = { version = "0.37", features = ["tokio1", "serde-transport", "serde-transport-bincode", "unix"] }

# ADD tcp feature for future cross-platform tarpc transport
tarpc = { version = "0.37", features = ["tokio1", "serde-transport", "serde-transport-bincode", "unix", "tcp"] }
```

The `tcp` feature enables `tarpc::serde_transport::tcp` which can replace
`tarpc::serde_transport::unix` on Windows when tarpc-over-TCP support is wired.

---

## Test Considerations

- All tests using `#[cfg(unix)]` paths (e.g., `discover_songbird_socket_none_when_missing`)
  are already properly gated
- New tests for `#[cfg(not(unix))]` paths should verify graceful degradation
  (no-op announce, `Unsupported` error from tarpc connect, etc.)
- The `handle_connection` tests in `server.rs` use `tokio::io::duplex` (platform-agnostic)
  and will continue to work

---

## Verification

After the port, blueGate should be able to:

```powershell
cargo build -p swarmvine --target x86_64-pc-windows-gnu --release
# Expected: compiles clean, no UnixStream/UnixListener errors

# Runtime (Windows):
swarmvine.exe server --bind-mode tcp
# Expected: listens on TCP, announce/songbird registration log as "not available"
# Expected: tarpc listener logs "not available on this platform"
# Expected: gossip spread works over TCP (already platform-agnostic)
```

---

## Reference: songBird Wave 155i Fix Pattern

songBird solved this exact problem in Wave 155i by:
1. Moving all UDS code behind `#[cfg(unix)]`
2. Adding TCP fallback paths for non-Unix
3. Using `PRIMAL_BIND_MODE=tcp` env var for platform override
4. Keeping the transport abstraction as the primary interface

swarmVine already has the transport abstraction (`transport.rs`) — it just
needs to be used consistently instead of bypassed by raw Unix imports.

---

*sporeGate topology scope: this handoff documents the fix pattern. Implementation
belongs to the swarmVine primal team. The transport abstraction is already in place;
4 call sites need to use it instead of bypassing it.*
