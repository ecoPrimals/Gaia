# songBird — Windows Platform Gate Fix (Wave 155i)

**Date**: July 29, 2026  
**Primal**: songBird (Network Orchestration & Discovery)  
**Wave**: 155i  
**Priority**: P0 — unblocks G1 (Tower on Windows)  
**Reporter**: blueGate Tower Atomic AAR  
**Resolver**: eastGate overwatch

---

## Summary

songBird's orchestrator had a compile-time platform gate (`#[cfg(not(unix))]`) that
rejected all non-Unix platforms before evaluating `--listen`/`--bind` flags. This
blocked Tower Atomic on Windows despite the TCP transport code already existing in
`songbird-universal-ipc`.

**Fixed**: The gate is now a TCP IPC fallback — songBird starts on Windows using
TCP on `SONGBIRD_IPC_PORT` (default 9901), following the same pattern bearDog uses
successfully with `--bind-mode tcp`.

---

## Changes

### Primary: `songbird-orchestrator/src/app/core/mod.rs`

The `#[cfg(not(unix))]` version of `start_ipc_server()` evolved from:
```rust
Err(anyhow!("IPC server requires Unix domain sockets..."))
```

To a full TCP IPC server that:
- Reads `SONGBIRD_IPC_PORT` env (configurable, default 9901)
- Binds to the configured `bind_host`
- Accepts TCP connections with line-delimited JSON-RPC 2.0
- Dispatches via the same `IpcServiceHandler` + `JsonRpcHandler` trait

### Secondary: `songbird-universal-ipc/src/service/virtual_relay.rs`

The `#[cfg(not(unix))]` `start_relay()` evolved from `bail!("unsupported")` to a
TCP-based virtual relay using `tokio::io::copy_bidirectional` on an ephemeral
localhost port.

### Tertiary: `songbird-orchestrator/src/bin_interface/server.rs`

The `--socket` CLI path on non-Unix now falls back to `start_tcp_ipc_server` on
port 9901 instead of logging "coming in Phase 2" and doing nothing.

---

## Additional Wave 155i Deep Debt (same session)

| Item | Resolution |
|------|-----------|
| Clippy `--all-features` failures | Fixed: wildcard imports in genesis mock, `#[must_use]` in federation mock |
| Failing test `establish_connection_exhausts_fallback_chain` | Emergency tunnel tier gated to opt-in via `StunRelayConfig::emergency_tunnel_enabled` (sovereignty-first default: disabled) |
| Doc warning: `evict_stale` links to private `MAX_IDLE_DURATION` | Inlined duration value in prose |
| `service_tests.rs` (1,018L) | Refactored into 5 thematic modules |
| `mesh_handler/tests.rs` (998L) | Refactored into 5 thematic modules |
| Hardcoded `"0.0.0.0"` in production | Evolved to `songbird_types::constants::PRODUCTION_BIND_ADDRESS` |
| `anyhow` in response module | Evolved to `SongbirdError::ResponseExtraction` |

---

## Validation

- **Clippy** (workspace, all-targets, all-features, `-D warnings`): 0 issues
- **Format**: Clean
- **Doc**: 0 warnings
- **Tests**: 8,937 passing (0 regressions)
- **Files >800L**: 0
- **Unsafe blocks**: 0

---

## What This Unblocks (downstream)

- G1 Tower on Windows (blueGate deployment)
- `tower.health` and `tower.mesh_status` on Windows
- Discovery beacons and inter-primal IPC on Windows
- `mesh.gate_enroll` for Windows gates
- ACME HTTP-01 challenge responder
- Full Tower Atomic validation
- Downstream Nest Atomic and Node Atomic on blueGate

---

## For Upstream Teams

### bearDog
No changes required. bearDog's TCP pattern (`--bind-mode tcp`) was the reference
implementation that songBird now follows.

### skunkBat
No changes required. skunkBat already works on Windows via TCP.

### primalSpring
The `IpcStream` trait (shipped Wave 142b) gains practical validation — Windows
TCP fallback exercises the `TcpLocal` variant that was previously untested in
production startup paths.

### overwatch
- Emergency tunnel tier is now **opt-in** (`emergency_tunnel_enabled: false` default)
- This aligns with sovereignty-first posture documented in wateringHole standards
- Existing deployments using cloudflared must set `emergency_tunnel_enabled: true`
  in their `StunRelayConfig` or environment

---

*Pushed via cascade → golgiBody. Upstream overwatch audit pending.*
