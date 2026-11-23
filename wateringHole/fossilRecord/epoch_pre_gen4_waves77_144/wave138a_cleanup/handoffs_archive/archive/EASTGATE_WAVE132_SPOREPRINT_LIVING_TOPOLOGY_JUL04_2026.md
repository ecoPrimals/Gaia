# eastGate Handoff — Wave 132: sporePrint Living Topology

**Date**: Jul 4, 2026  
**Gate**: eastGate  
**Primal**: petalTongue  
**From**: eastGate overwatch  
**Type**: Feature evolution — real-time mesh visualization on sporePrint

---

## Objective

Evolve sporePrint from a static documentation site into a living topology dashboard. The gate mesh visualization currently serves hardcoded `MeshNode` / `MeshLink` data. Wire it to query the local songBird `mesh.peers` endpoint and render real-time peer state, latency, and capability routing.

---

## Current State

| Component | State |
|-----------|-------|
| `petal_tongue_core::gate_mesh` | Static: 9 gates, 1 VPS, 7 WG links, `GateEnrollment` enum |
| `/api/gate-mesh` handler | Returns `"source": "static"` JSON |
| `/viz/gate-mesh` handler | Static SceneGraph → SVG via `SvgCompiler` |
| `DataService` | Queries biomeOS Neural API (`primal.list`, `neural_api.get_topology`) every 30s |
| songBird IPC client | **Does not exist** — only discovery registration + heartbeat |
| `viz_embed` shortcode | Works — `expand_viz_embeds()` in `content_direct.rs` |
| `gate.mesh.live` | Documented in code comments, not implemented |

---

## Architecture

```
songBird UDS (/run/user/1000/biomeos/songbird.sock)
    │
    │ JSON-RPC: mesh.peers, mesh.topology
    ▼
┌──────────────────────────────────────────────┐
│  petalTongue DataService                      │
│    refresh_mesh() — new periodic query        │
│    LiveMeshState { peers, latencies, paths }  │
└──────────────────────┬───────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    ▼                  ▼                  ▼
/api/mesh-live    /viz/gate-mesh       SSE /api/events
(raw JSON)        (live SVG)           (push updates)
                       │
                       ▼
              sporePrint page
        content/architecture/mesh-topology.md
        {{ viz_embed(src="/viz/gate-mesh?live=true") }}
```

---

## Work Item 1: Wire DataService to songBird `mesh.peers`

**File**: `petalTongue/src/data_service.rs`

### A. Add songBird UDS client

Create a lightweight JSON-RPC client that connects to the local songBird UDS socket:

```rust
pub struct SongbirdMeshClient {
    socket_path: PathBuf,
}

impl SongbirdMeshClient {
    pub fn from_env() -> Option<Self> {
        // SONGBIRD_SOCKET or default: /run/user/{uid}/biomeos/songbird.sock
    }

    pub async fn mesh_peers(&self) -> Result<Vec<MeshPeerState>> {
        // Connect UDS, send {"method":"mesh.peers","params":{},"id":1}
        // Parse response
    }
}
```

### B. Add `refresh_mesh()` to DataService

Alongside the existing `refresh()` (Neural API), add `refresh_mesh()`:

```rust
pub async fn refresh_mesh(&self) -> Result<()> {
    if let Some(client) = &self.songbird_client {
        let peers = client.mesh_peers().await?;
        let mut state = self.mesh_state.write().await;
        state.update_from_peers(peers);
    }
    Ok(())
}
```

### C. `LiveMeshState` struct

```rust
pub struct LiveMeshState {
    pub peers: Vec<LivePeer>,
    pub last_refresh: Instant,
}

pub struct LivePeer {
    pub gate_id: String,
    pub address: String,
    pub latency_ms: Option<u32>,
    pub reachable: bool,
    pub path_type: PathType,  // Direct, Relay, Unknown
    pub capabilities: Vec<String>,
}
```

### D. Periodic refresh in web mode

Add to the existing web mode heartbeat loop in `web_mode/mod.rs`:

```rust
if let Err(e) = refresh_service.refresh_mesh().await {
    tracing::debug!("mesh refresh: {e}");
}
```

---

## Work Item 2: `/api/mesh-live` Endpoint

**File**: `petalTongue/src/web_mode/handlers.rs`

### New handler

```rust
pub(super) async fn mesh_live_handler(
    State(state): State<AppState>,
) -> Json<serde_json::Value> {
    let mesh = state.data_service.mesh_state().await;
    Json(serde_json::json!({
        "peers": mesh.peers,
        "last_refresh_ms": mesh.last_refresh.elapsed().as_millis(),
        "source": if mesh.peers.is_empty() { "offline" } else { "live" },
    }))
}
```

### Route registration

In `web_mode/mod.rs` router setup:
```rust
.route("/api/mesh-live", get(handlers::mesh_live_handler))
```

---

## Work Item 3: Evolve `gate_mesh.rs` SceneGraph

**File**: `petalTongue/src/viz_data/gate_mesh.rs`

### A. Accept optional `LiveMeshState`

Modify `build_gate_mesh_scene()` to accept `Option<&LiveMeshState>`:

```rust
pub fn build_gate_mesh_scene(live: Option<&LiveMeshState>) -> SceneGraph {
    // Existing static layout (zones, gates, links)
    // If live data present:
    //   - Override enrollment colors with reachability (green/yellow/red/grey)
    //   - Replace static latency labels with live values
    //   - Add "LIVE" indicator badge
}
```

### B. Color mapping

| State | Color |
|-------|-------|
| reachable, latency < 5ms | Green (#4CAF50) |
| reachable, latency < 50ms | Yellow (#FFC107) |
| reachable, latency >= 50ms | Orange (#FF9800) |
| unreachable | Grey (#9E9E9E) |
| no live data (static fallback) | Current enrollment colors |

### C. Link animation data

For the `animation-json` format, include per-link latency change events so the WASM renderer can animate routing paths when `capability.call` traverses a link.

---

## Work Item 4: sporePrint Mesh Topology Page

**File**: `petalTongue/content/architecture/mesh-topology.md` (new)

```markdown
---
title: Mesh Topology
description: Real-time view of the ecoPrimals gate mesh
---

# Gate Mesh — Live Topology

{{ viz_embed(src="/viz/gate-mesh?live=true") }}

## How it works

The mesh is maintained by **songBird** on each gate. Peers connect via:
- **LAN direct** (0ms, /proc/net/fib_trie subnet detection)
- **WireGuard overlay** (via golgi VPS hub)
- **TURN relay** (NAT traversal fallback)

Services bind to `localhost` — songBird handles all cross-gate routing via `capability.call`.

## Live Data

The visualization above updates every 30 seconds from the local songBird `mesh.peers` endpoint. Green links indicate active, low-latency connections. Grey indicates unreachable peers.
```

### Viz query parameter

The `?live=true` query parameter tells `viz_handler` to fetch `LiveMeshState` and pass it to `build_gate_mesh_scene(Some(&live_state))` instead of `build_gate_mesh_scene(None)`.

---

## Work Item 5 (Optional): WASM Live Mesh Widget

**Crate**: `petal-tongue-wasm`

If client-side updates are desired (without full page reload):

1. Add `render_live_mesh(peers_json: &str) -> String` export
2. JavaScript fetches `/api/mesh-live` every 30s
3. Calls WASM to produce updated SVG
4. Replaces `<div class="viz-mesh">` inner content

This is optional — server-side SVG via `viz_embed` with periodic page refresh is sufficient for Phase 1.

---

## Key Files to Modify

| File | Change |
|------|--------|
| `src/data_service.rs` | Add `SongbirdMeshClient`, `LiveMeshState`, `refresh_mesh()` |
| `src/web_mode/handlers.rs` | Add `mesh_live_handler` |
| `src/web_mode/mod.rs` | Register `/api/mesh-live` route, add mesh refresh to heartbeat |
| `src/viz_data/gate_mesh.rs` | Accept `Option<&LiveMeshState>`, color/latency overrides |
| `crates/petal-tongue-core/src/gate_mesh.rs` | Add `LivePeer`, `LiveMeshState` types (optional, can stay in `data_service`) |
| `content/architecture/mesh-topology.md` | New page |

---

## Acceptance Criteria

1. `GET /api/mesh-live` returns live peer data from songBird (or `"source": "offline"` if songBird unreachable)
2. `GET /viz/gate-mesh?format=svg&live=true` returns SVG with green links for reachable peers and real latency labels
3. sporePrint mesh-topology page renders the live visualization via `viz_embed`
4. Graceful degradation: if songBird is down, falls back to static topology
5. All tests pass, zero clippy warnings

---

## Dependencies

- songBird must be running on eastGate with mesh initialized (already validated Wave 132b)
- Socket path: `/run/user/1000/biomeos/songbird.sock` (standard biomeos socket location)

---

*sporePrint becomes a living window into the mesh.*
