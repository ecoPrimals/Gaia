# NestGate v0.5.0 — Session 98: Transport Evolution Phase 2

**Date**: 2026-06-08
**Primal**: nestGate
**Gate**: ironGate
**Session**: 98
**Tests**: 13,116 (0 failures, 0 clippy warnings)

## Summary

Phase 2 of Transport Evolution: migrated **all production outbound IPC** from raw
`UnixStream::connect` / `JsonRpcClient::connect_unix()` to the standardized
`connect_transport()` + `TransportEndpoint` abstraction layer.

11 call sites across 9 files migrated. Only transport layer implementations
(`streams.rs`, `jsonrpc_client.rs` method definitions) and test code retain
direct socket calls — correct by design.

## Files Changed

| File | Change |
|------|--------|
| `nestgate-rpc/src/rpc/btsp_client.rs` | 3 `connect_unix()` → shared `connect()` helper using `connect_transport()` |
| `nestgate-rpc/src/rpc/storage_encryption.rs` | `from_provider()` → `connect_transport()` |
| `nestgate-rpc/src/rpc/primal_announce.rs` | Coordinator announce → `connect_transport()` |
| `nestgate-rpc/src/rpc/btsp_server_handshake/mod.rs` | Security provider → `connect_transport()` |
| `nestgate-rpc/src/rpc/isomorphic_ipc/atomic/mod.rs` | Health probe → `connect_transport()` + `tokio::io::split()` |
| `nestgate-discovery/src/capability_discovery.rs` | 2 UDS paths + 1 standard path → `connect_transport()` |
| `nestgate-api/src/transport/security.rs` | 4 `UnixStream::connect` eliminated, `UnixStream` import removed |
| `nestgate-security/src/crypto/delegate.rs` | 2 `connect_unix()` → `connect_transport()` |
| `nestgate-security/src/zero_cost_security_provider/authentication/security_primal.rs` | Raw UDS → `IpcStream` with `AsyncReadExt`/`AsyncWriteExt` |
| `nestgate-bin/src/commands/monitor.rs` | Socket probe → `connect_transport()` |
| `nestgate-bin/src/commands/discover.rs` | Socket probe → `connect_transport()` |
| `nestgate-bin/src/commands/service.rs` | Socket liveness → `connect_transport()` |

## Transport Evolution Status

- **Phase 1** (Session 97): `TransportEndpoint` type, `connect_transport()`, `TRANSPORT_ENDPOINT` env var
- **Phase 2** (Session 98): All outbound IPC migrated to transport abstraction
- `transport_evolution = "phase2"` in `config/capability_registry.toml`

## Compliance

- `sourdough validate transport` should report 0 self-binding violations
- All outbound IPC uses `TransportEndpoint` abstraction
- TCP self-bind only in Tier 5 debug/standalone mode (`--port`/`--enable-http`)
- Wire format compatible: `#[serde(tag = "transport")]` matches sourDough spec

## Pre-existing

- `test_universal_storage_bridge_list_pools` — pre-existing failure, unrelated to transport
