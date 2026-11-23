# Songbird Wave 60 — Mesh Federation Methods + DH-1 /tmp Elimination

**Date**: May 29, 2026  
**Primal**: songBird  
**Wave**: 60 (primalSpring upstream evolution targets)  
**Author**: Cursor Agent (deep debt executor)

---

## Summary

Two Wave 60 audit items resolved for Songbird:

1. **3 new mesh federation methods** — `mesh.discover_remotes`, `mesh.mirror`, `mesh.publish`
2. **DH-1 `/tmp` hardcoding cleanup** — zero `/tmp` writes in production path resolution

---

## Mesh Federation Methods (New Capabilities)

### `mesh.discover_remotes`
- **Signal graph**: `ecosystem.pull`
- **Purpose**: Discover remote gates and their content sources via the mesh
- **Returns**: List of reachable remote peers with `node_id`, `address`, `type`, `reachable`
- **Pattern**: Uses `get_reachable_nodes()` + `get_best_path()` — same API surface as `mesh.peers`

### `mesh.mirror`
- **Signal graph**: `ecosystem.push`
- **Purpose**: Mirror content/repos to a remote target (e.g., GitHub)
- **Params**: `target` (required string), `refs` (optional array of ref names)
- **Pattern**: Fire-and-forget — queues operation, returns immediately with status

### `mesh.publish`
- **Signal graph**: `ecosystem.pull/push/check` (all three)
- **Purpose**: Publish freshness/drift status to the mesh (how gates advertise sync state)
- **Params**: `topic` (optional, defaults to "status"), `payload` (optional JSON)
- **Pattern**: Fire-and-forget broadcast to all connected mesh peers

### Wiring
- `MeshMethod` enum: 3 new variants (`DiscoverRemotes`, `Mirror`, `Publish`)
- `JsonRpcMethod` from_str / as_str: `"mesh.discover_remotes"`, `"mesh.mirror"`, `"mesh.publish"`
- `IpcHandlers::mesh_dispatch()`: dispatch arm for all 3
- `capability_tokens.rs`: registered in CAPABILITY_METHODS
- `rpc.methods` introspection: included in method listing

---

## DH-1: /tmp Hardcoding Elimination

### Problem
`env_config::data_dir()`, `deployment_dir()`, `cache_dir()` fell back to `/tmp/songbird-*`
when `XDG_RUNTIME_DIR` and `TMPDIR` were unset. This violated `ProtectSystem=strict`
requirements for VPS deployment.

### Fix
New resolution chains (zero `/tmp` writes):

| Function | Chain |
|----------|-------|
| `data_dir()` | `$SONGBIRD_DATA_DIR` → `$XDG_DATA_HOME/songbird` → `$HOME/.local/share/songbird` → `/var/lib/songbird` |
| `cache_dir()` | `$SONGBIRD_CACHE_DIR` → `$XDG_CACHE_HOME/songbird` → `$HOME/.cache/songbird` → `/var/cache/songbird` |
| `deployment_dir()` | `$SONGBIRD_DEPLOY_DIR` → `data_dir()/deployments` |

### Impact
- Desktop: Same behavior (XDG vars are typically set)
- VPS systemd: Falls to `/var/lib/songbird` and `/var/cache/songbird` (writable under `ProtectSystem=strict`)
- Test code: Still uses `/tmp` paths (tests are isolated, not affected by this change)

---

## Verification

- `cargo check`: 0 errors, 0 warnings
- `cargo clippy --lib`: 0 warnings across affected crates
- `cargo test -p songbird-orchestrator -- env_config::tests`: 32 passed
- `cargo test -p songbird-universal-ipc -- mesh`: 24 passed
- `cargo test -p songbird-universal-ipc -- introspection`: 34 passed
- `cargo test -p songbird-orchestrator --test coverage_env_config_tests`: 44 passed
- `cargo test -p songbird-types --lib -- json_rpc`: 12 passed

---

## Files Modified

| File | Change |
|------|--------|
| `songbird-types/src/json_rpc_method/domain_methods.rs` | +3 `MeshMethod` variants |
| `songbird-types/src/json_rpc_method/mod.rs` | from_str/as_str for new methods |
| `songbird-universal-ipc/src/handlers/mesh_handler/mod.rs` | Handler implementations |
| `songbird-universal-ipc/src/introspection/rpc.rs` | Method listing + test array |
| `songbird-universal-ipc/src/introspection/capability_tokens.rs` | Capability registration |
| `songbird-orchestrator/src/ipc/handlers/mod.rs` | mesh_dispatch arms |
| `songbird-orchestrator/src/env_config/paths.rs` | DH-1 path resolution |
| `songbird-orchestrator/src/env_config/tests.rs` | Updated assertions |
| `songbird-orchestrator/src/commands/server.rs` | Log message update |
| `songbird-orchestrator/tests/coverage_env_config_tests.rs` | Updated assertions |

---

## primalSpring Absorption Expected

primalSpring validation should detect the 3 new methods via `birdsong.schema` introspection
and promote `mesh.discover_remotes`, `mesh.mirror`, `mesh.publish` from structural to
semantic testing when they go live on deployed gates.

DH-1 for Songbird is complete. Remaining DH-1 work is in other primals (toadStool, coralReef,
barraCuda, sweetGrass, squirrel) — per Wave 60 timeline, sweep is targeted for Wave 66.

---

## Coverage Expansion (Same Session)

+21 new tests added to `songbird-network-federation` pure-logic modules:

| Module | Tests Added | Coverage Targets |
|--------|-------------|-----------------|
| `state.rs` | +9 | `active_endpoints` filter, `update_endpoint_status` (match/noop), `preferred_endpoint` (degraded-only/empty), `add_endpoint` deduplication |
| `protocol_capability.rs` | +12 | `best_encrypted_protocol` (selection/inactive/none), `supports_protocol`, `best_protocol` tiers, `negotiate_protocol` (no-mutual/unknown-peer), `get_active_peers`, `register_feature`, encryption classification |

**Total test count**: 8,179 (up from 8,158).
