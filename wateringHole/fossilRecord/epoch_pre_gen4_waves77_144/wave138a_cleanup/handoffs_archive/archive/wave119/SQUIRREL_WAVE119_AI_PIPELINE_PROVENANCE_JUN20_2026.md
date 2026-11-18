<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Squirrel — Wave 119: AI Pipeline + Provenance Proxy + BTSP Transport Switch

**Date**: June 20, 2026
**Author**: eastGate overwatch
**Gate**: eastGate (Meta Atomic)
**Commit**: `f5ddc700` on `main`

## Gate Status

| Gate | Tests | Clippy | Build | Fmt |
|------|-------|--------|-------|-----|
| squirrel | 7,499 | 0 warnings | GREEN | clean |

## Key Changes

### BTSP Phase 3 Transport Switch (P1 → LIVE)

Server now auto-transitions from NDJSON to encrypted frame loop after a
successful `btsp.negotiate` with `chacha20-poly1305`. Implementation:
- `detect_btsp_switch()` inspects each request for negotiate intent
- `encrypted_frame_loop()` processes frames with c2s/s2c key separation
- Both `handle_jsonrpc_loop` and `handle_jsonrpc_with_first_line` support switch
- 3 integration tests on live Unix socket pairs (full roundtrip, null cipher,
  multi-frame) — previously orphaned, now wired into CI

### Provenance Proxy Layer (P2 → LIVE)

`provenance.*`, `dag.*`, `anchoring.*`, `attribution.*` methods dynamically
routed to discovered primals via:
1. Provider registry (springs that registered via `provider.register`)
2. Socket directory scanning with `capability.discover` probe

When no provider is discovered, returns structured error with domain and
resolution guidance. 6 unit tests including registry-based routing validation.

### Shared ContextManager (BUG FIX)

`JsonRpcServer.context_manager: Arc<ContextManager>` replaces per-request
`ContextManager::new()`. `context.create` → `context.update` → `context.summarize`
now correctly persists state across requests. 2 new integration tests.

### tarpc Parity (P2 → LIVE)

`provider_register`, `provider_list`, `provider_deregister`, `btsp_negotiate`
tarpc trait methods now delegate to JSON-RPC handlers instead of returning
stub failures.

### Real Request Metrics (DEBT → LIVE)

`RequestTracker` with atomic counters replaces:
- Hardcoded `125.3` avg response time
- Always-zero request_rate and error_rate
- `HttpMetrics` summary wired to real tracker

### Dead Code Cleanup

`btsp_encrypted_framing` functions (`encrypt_frame`, `decrypt_frame`,
`read_encrypted_frame`, `FrameError`) no longer need `#[cfg_attr(not(test),
allow(dead_code))]` — they're called by the live `encrypted_frame_loop`.
Only `write_encrypted_frame` retains `#[allow(dead_code)]` (convenience
wrapper used only by test clients).

## Files Changed

| File | Change |
|------|--------|
| `rpc/handlers_provenance.rs` | **NEW** — provenance proxy layer |
| `rpc/jsonrpc_server.rs` | `context_manager` field, transport switch, encrypted frame loop |
| `rpc/jsonrpc_dispatch.rs` | Provenance proxy routing |
| `rpc/mod.rs` | Wire `handlers_provenance`, `btsp_transport_switch_tests` |
| `rpc/tarpc_dispatch.rs` | provider/BTSP delegation to JSON-RPC handlers |
| `rpc/handlers_context.rs` | Use shared `context_manager`, 2 new tests |
| `rpc/btsp_encrypted_framing/mod.rs` | Remove dead_code annotations |
| `monitoring/metrics/collector.rs` | `RequestTracker`, wire to system metrics |
| `universal-patterns/registry/discovery.rs` | Fix stale comment |
| Docs | README, CURRENT_STATUS, CHANGELOG, sporeprint updated |

## Remaining Carry

| Item | Status | Notes |
|------|--------|-------|
| `RequestTracker` instrumentation | Ready | Wire `record_request()` in `handle_request_or_batch` |
| Provenance end-to-end | Blocked | Needs rhizoCrypt/sweetGrass running |
| Nuclear Lineage `0xEE` | Blocked | Needs BearDog per-user key material |
| NestGate context persistence | Blocked | Needs NestGate `storage.put/get` |
| Plugin WASM sandbox | Blocked | Needs runtime choice (wasmtime etc.) |
| Federation cross-node | Blocked | Needs peer mesh IPC |
