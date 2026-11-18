# Songbird Wave 70 — Evolution Pass

**Date**: June 2, 2026  
**From**: southGate (Songbird team)  
**Version**: v0.2.5-wave70  
**Status**: All evolution targets complete. Zero warnings. Zero debt.

---

## Delivered

### 1. `mesh.probe_latency` — Active RTT Measurement (NEW METHOD)

Active peer probing that populates `latency_ms` in `discovery.peers` responses with real measured data.

- Connects to each reachable peer's TCP endpoint
- Sends minimal `health.ping` JSON-RPC request
- Measures round-trip time end-to-end
- Updates `BeaconMesh::record_direct_connection()` with measured latency
- Skips non-TCP endpoints (relay, onion) gracefully
- Configurable `timeout_ms` parameter (default 5000ms)
- Wired into both dispatch tables (universal-ipc + orchestrator)
- 4 new tests: init guard, empty peers, relay skip, unreachable timeout

**Wire**: `{"jsonrpc":"2.0","method":"mesh.probe_latency","params":{"timeout_ms":3000},"id":1}`

### 2. Virtual Relay Connection Pooling

Persistent native connections instead of fresh-per-request for the virtual endpoint relay.

- `relay_connection()` maintains a single `NativeConn` (writer + buffered reader) per client session
- Automatic reconnect-and-retry on native endpoint failure
- Falls back to one-shot fresh connection if pool cannot establish
- Zero API changes — transparent performance improvement
- Eliminates connect overhead for long-lived NDJSON sessions

### 3. `hickory-resolver` 0.24 → 0.25 (RUSTSEC-2026-0119)

Dependency evolution across 4 crates.

- `TokioAsyncResolver::tokio(config, opts)` → `Resolver::builder_with_config(config, TokioConnectionProvider::default()).build()`
- Type alias `TokioAsyncResolver` → `TokioResolver`
- Feature `tokio-runtime` → `tokio`
- Collapsible `if let` chains modernized
- All 9 DNS-SD tests + 938 songbird-config tests pass
- 0.26 deferred: SRV/TXT type removal requires full iteration rewrite

### 4. Workspace Hygiene

- Zero clippy warnings (31 crates, pedantic + nursery)
- Zero fmt diffs
- Zero compilation warnings
- `bincode` 1.x RUSTSEC-2025-0141 documented as blocked on tarpc upstream

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 8,530+ lib passed |
| Clippy | Zero warnings (31 crates) |
| Methods | 49 registered (up from 48) |
| Crates | 31 workspace members |
| Lines | ~422,000 Rust |
| Dependencies | hickory-resolver 0.25, zero new deps added |

---

## For primalSpring

- `mesh.probe_latency` is ready for validation scenarios (RTT measurement → `latency_ms` in `discovery.peers`)
- Virtual relay connection pooling is transparent — no contract changes
- hickory-resolver advisory resolved (0.24 → 0.25)
- Songbird remains mesh validation partner for eastGate `discovery.peers` + `capability.call` test

## Gaps Acknowledged (not Songbird-actionable)

- `bincode` 1.x: blocked on tarpc upstream codec migration
- hickory-resolver 0.26: deferred until upstream stabilizes SRV/TXT API
- Membrane TLS sovereignty (Phase C): waiting on ironGate S1 graduation
