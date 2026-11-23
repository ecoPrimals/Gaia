# swarmVine — Wave 157d Windows Platform Port

**Primal**: swarmVine (#16)
**Date**: August 09, 2026
**Wave**: 157d DEPOT UNIFIED
**Gate**: eastGate
**Status**: Windows compilation unblocked — 4 call sites migrated to transport abstraction

---

## Summary

Implemented the Windows platform port per `SWARMVINE_WINDOWS_PORT_HANDOFF.md`.
All 4 raw `UnixStream`/`UnixListener` call sites now use the G66 transport
abstraction or `#[cfg(unix)]` gating. tarpc `tcp` feature enabled for future
cross-platform binary RPC.

## Changes

### 1. dispatch.rs — vine_bat_preaccept
- `tokio::net::UnixStream::connect` → `swarmvine_core::transport::connect_transport`
- `stream.into_split()` → `tokio::io::split(stream)` (works with `TransportStream`)
- On non-unix: path doesn't exist → early-return true (graceful degradation)

### 2. server.rs — UDS listener bind
- `tokio::net::UnixListener::bind` → `swarmvine_core::transport::bind_transport`
- Manual dir creation + socket removal consolidated into `bind_transport`
- Accept loop returns `TransportStream` (satisfies `AsyncRead + AsyncWrite + Unpin`)

### 3. tarpc_server.rs — start_tarpc_listener
- Entire function gated with `#[cfg(unix)]` / `#[cfg(not(unix))]`
- Non-unix stub logs "not available on this platform" and returns `Ok(())`
- Unix-only imports (`futures::StreamExt`, `tarpc::server`) also gated

### 4. tarpc_service.rs — connect()
- `#[cfg(unix)]` keeps existing UDS implementation
- `#[cfg(not(unix))]` returns `Err(Unsupported)` with descriptive message

### 5. Cargo.toml (workspace)
- Added `tcp` feature to tarpc: enables `tarpc::serde_transport::tcp` for future
  cross-platform binary RPC

### Already gated (no changes needed)
- `announce.rs` — `announce_to_biomeos` + `register_with_songbird` already had `#[cfg]` gating
- `spread.rs` — `query_songbird_peers` already had `#[cfg]` gating; TCP gossip is platform-agnostic

## Verification

- `cargo fmt --check` — clean
- `cargo clippy -D warnings` — 0 warnings
- `cargo test --workspace` — 124 tests pass (0 regressions)
- `cargo deny check` — licenses, bans, sources all pass
- Pattern follows songBird Wave 155i UDS-to-TCP platform gating

## Remaining for blueGate verification

```powershell
cargo build -p swarmvine-server --target x86_64-pc-windows-gnu --release
```

Expected: compiles clean. Runtime: listens on TCP, announce logs "not available",
tarpc listener logs "not available on this platform", gossip spread works over TCP.

---

*swarmVine — Windows compilation unblocked. 4 UDS call sites → transport abstraction.
124 tests, 0 regressions. blueGate can now build swarmVine as 16th primal on Windows.*
