# Songbird Wave 74 — Full Evolution Pass

**Date**: June 3, 2026  
**From**: southGate (Songbird)  
**Version**: v0.2.6-wave74  
**Tests**: 8,530+ passed, 0 failures  
**Clippy**: Zero warnings (--workspace --all-targets, pedantic+nursery+cargo)

---

## Summary

Wave 74 completes the critical path fixes from Wave 73 and delivers the Virtual Relay
Phase 2 evolution, cross-subnet relay handshake fix, and env var alignment. All glacial
blockers resolved. Songbird is mesh-ready for live cross-gate capability.call testing.

---

## Delivered (Wave 73→74)

### P1 Critical Path (Wave 73)
1. **`remote_dispatch.rs` HTTP POST**: Fixed cross-gate `capability.call` — was sending raw TCP
   to HTTP servers. Now uses proper HTTP POST to `/jsonrpc` with `Content-Type: application/json`.
2. **`mesh_seed` auto-bootstrap**: `SONGBIRD_PEERS` env var now triggers automatic mesh initialization
   at startup. No more manual `mesh.init` RPC required.
3. **`mesh.init` string format**: `bootstrap_peers` accepts `"node@host:port"` and `"host:port"`
   string formats in addition to `{node_id, address}` objects.
4. **`latency_ms` in health cycle**: `mesh.probe_latency` runs every ~2 minutes via health monitor.

### P1 Virtual Relay Phase 2 (Wave 74)
1. **Default virtual endpoints**: `ipc.resolve` returns relay socket by default (`prefer_virtual: true`).
2. **BTSP session validation**: Relay rejects requests with empty `_btsp_session` tokens.
3. **Performance metrics**: `ipc.relay_stats` JSON-RPC method exposes request count and avg overhead.
4. **Connection pooling**: Already delivered in Phase 1, confirmed operational.

### P2 Cross-Subnet Relay Fix
1. **`RelaySession` allocate handshake**: Production `RelaySession::new` now sends `AllocateRequest`,
   waits for `AllocationResponse`, uses server-assigned `session_id`. Previously generated client-side
   UUID that never matched server sessions — this was the fundamental integration gap.
2. **`relay.allocate` real implementation**: Evolved from test stub (echo JSON) to production handler
   with lineage authorization and proper response format.

### P3 Env Var Alignment
- **Canonical**: `SONGBIRD_FEDERATION_ENABLED` (bool-parsed, default `false`)
- **Legacy alias**: `FEDERATION_ENABLED` honored as fallback in startup + health
- **Tower CLI**: Fixed to write canonical `SONGBIRD_FEDERATION_ENABLED`
- **Unified config**: Fixed presence-only check to proper bool parsing
- **`SONGBIRD_MESH_ENABLED`**: Does NOT exist (mesh is implicit via `SONGBIRD_PEERS`)

### Deep Debt Cleanup
- `multi_tier_coordinator.rs` refactored (799→655L) — `CloudflaredTunnel` extracted to own module
- Zero files >800 lines (largest: `mesh_handler/mod.rs` at 772L)
- All external deps are pure Rust (zero C/FFI)
- `forbid(unsafe_code)` on all 31 crates
- All mocks `#[cfg(test)]` or `#[cfg(any(test, feature = "test-mocks"))]`
- `SONGBIRD_SERVICE_CONFIG_PATH` env override added for file-based service discovery
- 6 clippy idiom fixes (redundant clone, match arms, approx_constant, IP constant, etc.)

---

## For eastGate (Mesh Validation Partner)

Songbird is ready for live `discovery.peers` + `capability.call` cross-gate test:
- Latest code on `origin/main`
- `SONGBIRD_FEDERATION_PORT` configurable (default 7700)
- `SONGBIRD_PEERS` auto-seeds mesh at startup
- `remote_dispatch.rs` uses HTTP POST (matches axum server at port 7700)
- `mesh.probe_latency` keeps latency data fresh

---

## For primalSpring (Audit Context)

### Methods added since last audit
- `ipc.relay_stats` — virtual relay performance metrics
- `mesh.probe_latency` — active RTT measurement (Wave 70)

### Key architectural facts
- 31 crates, ~422,000 lines Rust
- Zero unsafe, zero panics, zero TODO in production
- All env via `songbird-process-env` (zero `std::env` in production)
- Federation: `SONGBIRD_FEDERATION_ENABLED` (canonical) / `FEDERATION_ENABLED` (alias)
- Mesh: implicit via `SONGBIRD_PEERS` (no enable flag)

### Known limitations
- `bincode` 1.x blocked on tarpc upstream (RUSTSEC-2025-0141)
- `hickory-resolver` 0.26 deferred (breaking SRV/TXT API changes)
- Relay `lineage_proof` not validated server-side (auth uses node IDs only)
- `MaskingLevel::Full` is padding-only (no encryption layer yet)
- 1 known flaky test (env leakage in parallel: `test_migration_helper`)
