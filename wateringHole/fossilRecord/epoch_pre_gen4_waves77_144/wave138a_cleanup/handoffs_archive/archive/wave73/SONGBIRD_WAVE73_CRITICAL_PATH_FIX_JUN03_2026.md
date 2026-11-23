# Songbird Wave 73 — Critical Path Fix

**Date**: June 3, 2026  
**Gate**: southGate  
**Commit**: `d6a6f714`  
**Priority**: P1 GLACIAL BLOCKER RESOLVED

---

## What Was Fixed

### P1 #1: remote_dispatch.rs — HTTP POST (CRITICAL)

**Problem**: `forward_to_remote_tcp()` and `peer_has_capability()` sent raw TCP
NDJSON to peer port 7700. But peers run axum HTTP servers — not NDJSON streams.
Result: "Invalid JSON from remote gate: expected value at line 1 column 1"

**Fix**: Replaced raw TCP socket I/O with proper HTTP/1.1 POST to `/jsonrpc`
using `hyper` + `http-body-util`. Both capability probe and dispatch now use
`http_post_jsonrpc()` helper that:
- Builds HTTP request with `Content-Type: application/json`
- Uses hyper legacy client with TokioExecutor
- Respects `DEFAULT_SOCKET_IO_TIMEOUT` for the full HTTP cycle
- Returns parsed JSON-RPC response body

### P1 #2: mesh_seed wired into startup (AUTO-BOOTSTRAP)

**Problem**: `SONGBIRD_PEERS` env var was parsed by `mesh_seed` module, but
`spawn_mesh_seed()` was never called during boot. Users had to manually send
`mesh.init` RPC after startup.

**Fix**: `start_broker_with_discovery()` now returns a `BrokerHandle` containing
both the registry and the mesh handler. Stage 2 startup calls
`crate::mesh_seed::spawn_mesh_seed(handle.mesh_handler)` immediately after
broker initialization. Peers auto-bootstrap from SONGBIRD_PEERS on boot.

### P2 #3: mesh.init string format

**Problem**: `bootstrap_peers` only accepted object format `[{node_id, address}]`.
String format `"node@host:port"` silently rejected with `peers_added: 0`.

**Fix**: Parser now supports three formats:
- Object: `{"node_id": "...", "address": "host:port"}`
- String with ID: `"node_id@host:port"`
- Bare address: `"host:port"` (auto-generates `peer-{ip}` node_id)

Mixed arrays work. 2 new tests cover string and mixed formats.

### P2 #4: latency_ms in health cycle

**Problem**: `discovery.peers` returned `latency_ms: null` because
`mesh.probe_latency` was never invoked automatically.

**Fix**: Health monitoring loop (30s interval) now invokes `mesh.probe_latency`
every 4th tick (~2 minutes). Latency measurements accumulate in BeaconMesh and
appear in subsequent `discovery.peers` responses.

---

## What This Unblocks

- Cross-gate `capability.call` (ALL multi-gate science dispatch)
- 3-gate plasmodium collective (add ironGate)
- biomeOS cross-gate endpoint resolution
- primalSpring full `s_covalent_mesh` scenario
- Cross-subnet southGate via TURN relay

---

## Test Results

- `songbird-universal-ipc`: 537 passed (incl. 2 new string format tests)
- `songbird-orchestrator`: 1751 passed
- Full workspace clippy: zero warnings
- Known flaky: `discovery_http_port_overlay_override_numeric` (passes in isolation)

---

## Files Changed

| File | Change |
|------|--------|
| `songbird-universal-ipc/src/service/remote_dispatch.rs` | TCP→HTTP POST rewrite |
| `songbird-universal-ipc/Cargo.toml` | Added hyper, hyper-util, http-body-util |
| `songbird-universal-ipc/src/service/mod.rs` | Added `mesh_handler()` accessor |
| `songbird-universal-ipc/src/handlers/mesh_handler/mod.rs` | String format parsing |
| `songbird-universal-ipc/src/handlers/mesh_handler/tests.rs` | 2 new tests |
| `songbird-orchestrator/src/ipc/universal_broker.rs` | BrokerHandle, mesh_handler exposure |
| `songbird-orchestrator/src/app/startup_orchestration.rs` | spawn_mesh_seed on boot |
| `songbird-orchestrator/src/app/core/mod.rs` | broker_mesh_handler field |
| `songbird-orchestrator/src/app/health.rs` | Latency probe in health cycle |

---

## Ready For

eastGate can now initiate live `discovery.peers` + `capability.call` cross-gate
test. Songbird will:
1. Auto-bootstrap mesh from `SONGBIRD_PEERS` on startup
2. Accept HTTP JSON-RPC requests from remote peers on federation port
3. Forward `capability.call` via HTTP POST to remote peers' `/jsonrpc` endpoint
4. Populate `latency_ms` via periodic health probes
