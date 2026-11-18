# NestGate v0.5.0 Session 97 — Transport Evolution Phase 1

**Date**: 2026-06-08
**Session**: 97
**Tests**: 13,116 (21 new) | 0 failures | 0 clippy warnings
**Directive**: Wave 100 "All Primals — Transport Evolution Trigger"

## Summary

NestGate now accepts `TRANSPORT_ENDPOINT` as an ecosystem-standard JSON env var.
The sourDough wire format (`uds`/`tcp`/`mesh_relay` serde-tagged enum) is implemented
in `nestgate-types::transport` with full round-trip test coverage. Outbound IPC has a
`connect_transport()` function and `resolve_outbound_endpoint()` helper that checks
`TRANSPORT_ENDPOINT` first, then falls back to legacy XDG/TCP discovery.

## What Shipped

### Type Layer (`nestgate-types`)
- `TransportEndpoint` enum: `Uds { path }`, `Tcp { host, port }`, `MeshRelay { peer_id, capability }`
- `from_env()` / `from_env_with()` parsing from `TRANSPORT_ENDPOINT`
- `is_local()` classification, `Display` formatting
- 13 unit tests: wire format compatibility, roundtrip, env parsing, error cases

### Connection Layer (`nestgate-rpc`)
- `connect_transport(&TransportEndpoint)` → `IpcStream` (UDS/TCP dispatch, MeshRelay error with guidance)
- `transport_to_ipc_endpoint()` bridge for backward-compatible code paths
- `IpcStream` now `#[derive(Debug)]`
- `JsonRpcClient` internal: `BufReader<UnixStream>` → `BufReader<IpcStream>`
  - New: `connect_transport(endpoint)`, `connect_tcp(host, port)`
  - All 10 existing tests pass unchanged
- 6 new tests (connect_transport, transport_to_ipc)

### Resolution Layer
- `resolve_outbound_endpoint(service_name)` → `OutboundEndpoint::Transport` | `OutboundEndpoint::Legacy`
- `OutboundEndpoint.connect()` — unified async connect regardless of resolution source
- 3 new tests (prefer transport, fallback to legacy, invalid JSON fallback)

### Binary Entry (`nestgate-bin`)
- `run_daemon()` calls `log_transport_endpoint()` at startup
- Logs: `TRANSPORT_ENDPOINT: uds:/run/...` or `not set (using legacy discovery)` or `parse error`
- `start_http_mode()` documented as **Tier 5 fallback** (debug/standalone only)

### Registry
- `capability_registry.toml`: `transport_evolution = "phase1"`

## Compliance Matrix

| Requirement | Status |
|---|---|
| Accept `TRANSPORT_ENDPOINT` env var | **Done** — parsed at startup, logged, available to outbound paths |
| `connect_transport()` for outbound IPC | **Done** — available in `nestgate-rpc`, wired into `JsonRpcClient` |
| Remove hardcoded `TcpListener::bind("0.0.0.0:PORT")` | **Guarded** — production default is socket-only; HTTP mode is explicit Tier 5 |
| Keep `--port` as Tier 5 fallback | **Done** — `--enable-http` / `--port` retained for debug |
| `sourdough validate transport` clean | **Expected clean** — NestGate self-knowledge only, no self-binding in default path |

## Migration Path (Phase 2 — future sessions)

~30 outbound IPC call sites identified by audit. Priority migration targets:
1. `btsp_client.rs` — security provider (3 connect sites)
2. `primal_announce.rs` — coordinator announce
3. `storage_encryption.rs` — key retrieval
4. `capability_discovery.rs` — orchestration bootstrap

Each site can incrementally adopt `resolve_outbound_endpoint()` + `.connect()` instead of
raw `UnixStream::connect`. The `OutboundEndpoint` abstraction ensures backward compatibility.

## Files Changed

- `code/crates/nestgate-types/src/transport.rs` (NEW)
- `code/crates/nestgate-types/src/lib.rs`
- `code/crates/nestgate-rpc/src/rpc/isomorphic_ipc/streams.rs`
- `code/crates/nestgate-rpc/src/rpc/isomorphic_ipc/mod.rs`
- `code/crates/nestgate-rpc/src/rpc/isomorphic_ipc/launcher.rs`
- `code/crates/nestgate-rpc/src/rpc/mod.rs`
- `code/crates/nestgate-rpc/src/rpc/jsonrpc_client.rs`
- `code/crates/nestgate-bin/src/commands/service.rs`
- `config/capability_registry.toml`
- `CHANGELOG.md`
- `sporeprint/validation-summary.md`
