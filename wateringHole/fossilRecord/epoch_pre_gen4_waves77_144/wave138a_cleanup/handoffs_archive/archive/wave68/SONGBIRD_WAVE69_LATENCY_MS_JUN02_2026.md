# Songbird Wave 69 — `latency_ms` in `discovery.peers`

**Date**: June 2, 2026  
**Version**: v0.2.3-wave69  
**Gate**: southGate  

---

## Summary

Wired RTT measurement (`latency_ms`) from the mesh layer into `discovery.peers`
response on both code paths (orchestrator dynamic JSON + universal IPC typed struct).
This fulfills the P2 wire contract extension from primalSpring Wave 69.

## Changes

### `crates/songbird-orchestrator/src/ipc/handlers/mod.rs`
- `discovery_peers_json()`: mesh peer objects now include `"latency_ms"` field,
  forwarded directly from `mesh.peers` response.

### `crates/songbird-universal-ipc/src/handlers/discovery_handler/types.rs`
- `DiscoveredPeerInfo`: added `pub latency_ms: Option<u64>` with
  `#[serde(skip_serializing_if = "Option::is_none")]` — absent from wire when null.

### `crates/songbird-universal-ipc/src/handlers/discovery_handler/mod.rs`
- `collect_mesh_peers()`: extracts `path.latency` from `BeaconMesh::get_best_path()`
  and converts to milliseconds via `u64::try_from(d.as_millis())`.

### `crates/songbird-universal-ipc/src/handlers/discovery_bridge.rs`
- `convert_discovered_peer()`: sets `latency_ms: None` (UDP discovery does not
  currently track latency).

## Behavior

- `latency_ms` is **null** (omitted from JSON) for bootstrap peers and UDP-discovered
  peers until a real connection probe measures RTT.
- primalSpring validation scenario handles graceful skip (field optional in schema).
- When `BeaconMesh::record_direct_connection()` is called with measured latency,
  subsequent `discovery.peers` calls will include the value.

## Verification

```
cargo check -p songbird-universal-ipc -p songbird-orchestrator  # zero errors
cargo test -p songbird-universal-ipc --lib -- discovery          # 58 passed
cargo clippy -p songbird-universal-ipc -p songbird-orchestrator  # zero warnings
```

## Wave 69 Status Summary

| Item | Status |
|------|--------|
| Mesh validation partner (P0) | READY — infrastructure confirmed |
| `latency_ms` in discovery.peers (P2) | DONE — this wave |
| sled → redb (P2) | ALREADY DONE (Wave 135/SB-03) |
| Virtual endpoint relay (P2) | BLOCKED — design doc not published, gated on biomeOS L4 |

---

*Handoff for primalSpring cascade validation.*
