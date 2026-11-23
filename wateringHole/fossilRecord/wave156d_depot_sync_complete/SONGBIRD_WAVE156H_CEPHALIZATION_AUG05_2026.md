# songBird — Wave 156h: G64 Cephalization (tarpc 0.37 + Dual-Socket)

**Date**: August 5, 2026  
**Wave**: 156h  
**From**: eastGate overwatch  
**Status**: COMPLETE — C1 + C2 delivered

---

## What Was Done

### C1: tarpc Version Alignment (0.34 → 0.37)

Upgraded songBird's tarpc dependency from 0.34 to 0.37, absorbing 3 versions of breaking changes:

| Version | Breaking Change | Impact on songBird |
|---------|----------------|-------------------|
| 0.35 | `SystemTime` → `Instant` for deadlines | Transparent (we pass `context::current()`) |
| 0.35 | `RpcError::Receive` → `RpcError::Transport` | None (we don't pattern-match tarpc errors) |
| 0.35 | `serde_transport::tcp::Connect` → `TcpConnect` | None (we use `tcp::connect()` function) |
| 0.35 | Request hooks → `RequestHook` extension trait | None (we don't use hooks) |
| 0.36 | `deranged` crate conflict | None |
| 0.37 | OpenTelemetry dep update | None (we don't use OTel) |

**Key insight**: tarpc 0.37 still uses bincode 1.3 via tokio-serde 0.9. The blurb's "bincode 2.x" note was aspirational — tarpc upstream PR #529 (bincode 2.0 migration) remains open/unmerged. No serialization format change was needed.

**Dependency cleanup**: Removed direct `tokio-serde 0.8` and `tokio-util` dependencies from `songbird-universal` and `songbird-orchestrator`. tarpc 0.37 re-exports both via `tarpc::tokio_serde` and `tarpc::tokio_util` — all internal code now uses these re-exports, eliminating version conflicts.

### C2: UDS Dual-Socket Pattern

Implemented the canonical cephalization dual-socket pattern:

```
songbird.sock       → JSON-RPC 2.0 (discovery, diagnostics, browser/diagnostic)
songbird.tarpc.sock → tarpc binary  (high-frequency primal-to-primal, sub-ms)
```

**Server side** (`songbird-orchestrator`):
- `run_tarpc_uds_accept_loop!` macro in `rpc/tarpc_server/accept.rs`
- `start_tarpc_uds_server()` in `rpc/tarpc_server/mod.rs`
- Wired into orchestrator startup: spawns alongside TCP tarpc (auto on Unix)

**Client side** (`songbird-universal`):
- `TarpcClient::connect_uds(socket_path, timeout)` in `tarpc_client/connection.rs`
- Uses same bincode + length-delimited framing as TCP

**Path constant** (`songbird-types`):
- `tarpc_uds_socket_path()` → `{biomeos_socket_dir}/songbird.tarpc.sock`

---

## Verification

| Check | Result |
|-------|--------|
| `cargo clippy --workspace --all-targets -- -D warnings` | PASS (zero warnings) |
| `cargo test -p songbird-orchestrator --test integration_tarpc` | 9/9 PASS |
| `cargo test --workspace` | 14,840+ passing (2 pre-existing flaky in universal-ipc) |
| `cargo check --workspace --all-targets` | PASS (zero errors) |

---

## What This Unblocks

1. **G64 cephalization Phase 1**: songBird is now version-aligned with the 5 tarpc-default primals (coralReef, barraCuda, toadStool, nestGate, squirrel). UDS binary framing eliminates 5ms JSON-RPC overhead for intra-gate hot paths.

2. **Ecosystem convergence**: Other primals on tarpc 0.37 can now connect to songBird's `.tarpc.sock` for direct binary RPC without TCP overhead.

3. **Cross-gate elevated path** (Phase 2, future): With all primals on tarpc 0.37, the relay can bridge tarpc connections across gates.

---

## For Downstream Teams

- **biomeOS**: Can route tarpc UDS connections to `songbird.tarpc.sock` for high-frequency operations (service registration, capability queries)
- **nestGate**: `content.get`/`content.put` hot path can use tarpc UDS when co-located
- **petalTongue**: Already on tarpc 0.34 — needs same 0.37 upgrade (same migration: `tarpc::tokio_util`/`tarpc::tokio_serde` re-exports)
- **All primals**: `TarpcClient::connect_uds()` available in `songbird-universal` for any Rust client

---

*C1 + C2 complete. songBird tarpc now at 0.37 with dual-socket UDS. Next: petalTongue tarpc alignment (same migration pattern).*
