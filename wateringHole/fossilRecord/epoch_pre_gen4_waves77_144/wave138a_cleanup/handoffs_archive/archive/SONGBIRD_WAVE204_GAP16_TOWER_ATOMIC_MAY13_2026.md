# Songbird Wave 204 — GAP-16 Tower Atomic Resolution

**Date**: May 13, 2026  
**Wave**: 204  
**Audit Reference**: Upstream Primal Evolution — Glacial Debt Escalation (May 13, 2026)  
**Gap Resolved**: GAP-16 (Tower atomic — bearDog / songbird / skunkBat)

---

## Summary

ludoSpring wired a complete Tower atomic validation scenario (9 checks across 5 capabilities: BTSP auth, crypto seed fingerprint, **mesh peer discovery**, defense audit, skunkBat lineage). Live validation was blocked because `mesh.*` methods were only dispatched on the TCP IPC transport (`IpcServiceHandler`) — **not** on the canonical orchestrator UDS socket (`songbird.sock` / `network.sock`) that other primals and springs connect to.

This wave resolves the gap: all 8 `mesh.*` methods are now routed through the canonical UDS handler.

---

## What Shipped

### `mesh.*` dispatch on orchestrator UDS

| Method | Status |
|--------|--------|
| `mesh.init` | Routed → `MeshHandler::handle_init` |
| `mesh.status` | Routed → `MeshHandler::handle_status` |
| `mesh.find_path` | Routed → `MeshHandler::handle_find_path` |
| `mesh.announce` | Routed → `MeshHandler::handle_announce` |
| `mesh.peers` | Routed → `MeshHandler::handle_peers` |
| `mesh.topology` | Routed → `MeshHandler::handle_topology` |
| `mesh.health_check` | Routed → `MeshHandler::handle_health_check` |
| `mesh.auto_discover` | Routed → `MeshHandler::handle_auto_discover` |

### Implementation

- `IpcHandlers` struct gains `mesh_handler: Arc<MeshHandler>` field
- `IpcHandlers::mesh_dispatch()` — single-entrypoint method dispatching `MeshMethod` variants with `Result<Value, String>` → `Result<Value, JsonRpcError>` error mapping
- `handle_jsonrpc_request` match arm: `Ok(JsonRpcMethod::Mesh(m)) => self.handlers.mesh_dispatch(m, request.params).await`

### Test Coverage (15 new tests)

- 11 socket-level routing tests: mesh init/status/peers/topology/health_check/auto_discover, capability.resolve, discover_capabilities, ipc.register, invalid jsonrpc version, mesh-without-init error
- 4 mesh handler unit tests: mesh_status_requires_init, mesh_status_works_after_init, mesh_init_succeeds_with_valid_params, mesh_init_fails_without_node_id

---

## What This Unblocks

- **ludoSpring Tower atomic validation**: Can now connect to `network.sock` and exercise `mesh.peers`, `mesh.status`, `mesh.health_check` as part of the 9-check Tower scenario
- **All springs with Tower in their composition**: Same socket path, same methods, same behavior as the TCP transport
- **`capabilities.list` truthfulness**: Previously advertised `mesh.*` methods that returned `-32601`; now all advertised methods are live

---

## Verification

- 0 clippy warnings (full workspace `--exclude songbird-types -D warnings`)
- 29 socket routing tests pass (24 `server::tests` + 5 `ipc_handlers_tests`)
- `cargo fmt -- --check` clean

---

## Niche Tasks Status (per audit)

| Task | Status |
|------|--------|
| `capability.resolve` (H2) | **DONE** (Wave 201) |
| Coverage 73→90% (H2) | In progress — 15 new tests this wave |
| Tor/TLS delegation (H2) | Blocked on security provider — documented |

---

## Next Steps

- Deploy Songbird on local UDS (alongside bearDog + skunkBat) for ludoSpring live validation
- Continue coverage expansion toward 90% target
