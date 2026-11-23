# Songbird Wave 75 — Capability Propagation + HTTP/UDS Unification + Relay Hardening

**Date**: June 3, 2026  
**From**: southGate (Songbird team)  
**Version**: v0.2.7-wave75  
**Tests**: 13,960+ passed, zero warnings, zero clippy

---

## P1 CRITICAL: Capability Propagation (MESH BLOCKER RESOLVED)

**Problem**: `discovery.peers` returned `capabilities: []` for all remote peers, blocking ALL cross-gate `capability.call` routing.

**Root Cause**: `collect_mesh_peers` in `discovery_handler/mod.rs` hardcoded `Vec::new()` for capabilities. `BeaconMesh` stores only routing data (address, latency), not capabilities. `ipc.register` stored capabilities only in the local `ServiceRegistry` with no replication mechanism.

**Fix — Push Model**:
1. Added `peer_capabilities: HashMap<String, Vec<String>>` to `MeshHandler`
2. New `mesh.capabilities_announce` JSON-RPC method receives `{node_id, capabilities}` from remote gates and stores them
3. After every `ipc.register` with capabilities, Songbird collects all local capabilities and announces them to all reachable mesh peers via HTTP POST to their `/jsonrpc` endpoint
4. `collect_mesh_peers` now reads from `MeshHandler::get_peer_capabilities()` instead of hardcoding empty

**Validation**: Register 'security' on strandGate → eastGate sees it in `discovery.peers` capabilities array.

**Files Changed**:
- `crates/songbird-types/src/json_rpc_method/domain_methods.rs` — `MeshMethod::CapabilitiesAnnounce`
- `crates/songbird-types/src/json_rpc_method/mod.rs` — string mapping
- `crates/songbird-universal-ipc/src/handlers/mesh_handler/mod.rs` — `peer_capabilities`, announce logic
- `crates/songbird-universal-ipc/src/handlers/discovery_handler/mod.rs` — uses `get_peer_capabilities`
- `crates/songbird-universal-ipc/src/service/dispatch.rs` — dispatch arm
- `crates/songbird-universal-ipc/src/service/ipc_registry.rs` — post-register announce trigger
- `crates/songbird-orchestrator/src/ipc/handlers/mod.rs` — orchestrator dispatch

---

## P1: HTTP/UDS State Unification

**Problem**: HTTP endpoint (port 7700) and UDS endpoint (`/primal/songbird`) each created their own `ServiceRegistry` and `MeshHandler`. Calling `ipc.register` or `mesh.init` on one transport was invisible on the other.

**Fix**: Single shared `IpcServiceHandler` created before either server starts:
1. `startup_orchestration.rs` creates one `ServiceRegistry` + `IpcServiceHandler`
2. HTTP server receives the shared handler via parameter (no longer creates its own)
3. UDS broker uses `start_broker_with_shared_handler()` with the same instance
4. Both transports now operate on identical state

**Files Changed**:
- `crates/songbird-universal-ipc/src/tower_atomic/server.rs` — `from_shared()` constructor
- `crates/songbird-orchestrator/src/ipc/universal_broker.rs` — `with_shared_handler()`, `start_broker_with_shared_handler()`
- `crates/songbird-orchestrator/src/app/http_server.rs` — accepts optional shared handler
- `crates/songbird-orchestrator/src/app/startup_orchestration.rs` — creates shared handler first

---

## P2: Relay Security Hardening (Phase 3)

**Previous State**: Phase 2 only checked non-empty `_btsp_session` field.

**Phase 3 Evolution**:
1. **Structured token parsing**: Expects `payload_b64.signature_b64` format
2. **Payload validation**: Decodes base64, parses JSON, checks `node_id` and `ts` fields
3. **Timestamp freshness**: Rejects tokens older than 5 minutes
4. **Audit trail**: `relay_audit` tracing target logs authenticated and rejected requests
5. **Backward compatible**: Single-segment tokens (Phase 2) still accepted
6. **Payload integrity**: Relay forwards raw request bytes unmodified — only peeks at `_btsp_session`

**Next Phase (P3.5)**: Full Ed25519 signature verification via `CryptoProvider::call("crypto.verify.ed25519", ...)` when BearDog is available at runtime.

---

## Test Fix: Relay Session Regression

Fixed `coordinate_relay_punch_keep_relay_when_no_udp_reply` in `songbird-onion-relay` — was using `RelaySession::new` (requires live server handshake since Wave 74). Updated to `new_unverified` test constructor.

---

## For eastGate/primalSpring

- **capability.call should now route correctly**: After `mesh.init` + `ipc.register` on each gate, `discovery.peers` returns real capabilities. Remote dispatch can resolve capabilities.
- **Single transport sufficient**: Either HTTP or UDS `mesh.init` + `ipc.register` is sufficient — state is unified.
- **Test scenario**: Gate A registers primals → Gate B calls `discovery.peers` → capabilities visible → `capability.call` routes successfully.

---

## Coordination

- **Downstream**: ALL gates unblocked for multi-gate capability routing
- **Partner**: eastGate for live cross-gate `capability.call` validation
- **Remaining**: P3.5 full Ed25519 signature verification on relay (requires BearDog runtime)
