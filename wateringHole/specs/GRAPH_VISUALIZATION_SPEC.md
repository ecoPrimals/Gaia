# Graph Visualization Architecture Spec — biomeOS → petalTongue → nestgate.io

**Date**: Aug 13, 2026 | **Wave**: 157k | **From**: overwatch (eastGate)
**Owner**: petalTongue team (ironGate) + biomeOS team (eastGate)
**Status**: ARCHITECTURE SPEC — ready for implementation

---

## Goal

Render biomeOS TOML deployment/signal graphs as interactive visualizations on the nestgate.io peptidoglycan surface. This makes the ecosystem's composition architecture visible to operators and external researchers.

---

## What Exists

### biomeOS Graph System (79 TOML files)

| Category | Count | Location |
|----------|-------|----------|
| Deploy/orchestration graphs | 47 | `biomeOS/graphs/*.toml` |
| Signal graphs | 32 | `biomeOS/graphs/signals/*.toml` |

Format: `[graph]` header + `[[nodes]]` with `id`, `depends_on`, `capabilities`, `[nodes.primal]`, `[nodes.operation]`. Coordination modes: Sequential, Parallel, Pipeline, Continuous, ConditionalDAG.

Key graphs for visualization:
- `nucleus_simple.toml` — NUCLEUS composition (core primals + dependencies)
- `tower_atomic_bootstrap.toml` — Tower cold-start sequence
- `nucleus_complete.toml` — Full NUCLEUS with all 14+ primals
- `science_pipeline.toml` — GPU data → provenance → NFT
- `deploy_result.toml` — Signal graph for deployment health

### biomeOS Graph API

| Method | Purpose |
|--------|---------|
| `graph.list` | List all available graphs (bundled + runtime) |
| `graph.get` | Return parsed graph as JSON |
| `graph.execute` | Execute a graph |
| `graph.status` | Execution status/history |

`graph.get` returns the full graph structure as JSON — nodes, edges, metadata, coordination pattern. This is the data source for visualization.

### petalTongue GraphEngine

Location: `petalTongue/crates/petal-tongue-core/src/graph_engine/`

| Component | Purpose |
|-----------|---------|
| `GraphEngine` | Node/edge storage, layout computation |
| `LayoutAlgorithm` | Force-directed (Fruchterman-Reingold), hierarchical, circular |
| `Visual2DRenderer` | Interactive egui rendering |
| `SvgCompiler` | Scene graph → SVG export |
| `WebGlCompiler` | Scene graph → WebGL draw commands |
| `/viz/{slug}` | Web route for registered visualizations |
| `/api/topology/live` | Live Neural API topology JSON |

The GraphEngine can already render node-edge diagrams with multiple layout algorithms and export to SVG, DOT, PNG, and HTML.

### Current Web Surface

- `/viz/gate-mesh` — Static SVG of enrolled gates (manifest-derived)
- `/api/topology/live` — Live biomeOS topology as JSON tables (not visual graph)
- No TOML graph visualization exists

---

## Architecture

### Pipeline

```
biomeOS (graph.list + graph.get)
    │ JSON-RPC via Neural API UDS socket
    ▼
petalTongue DataService
    │ Fetches graph definitions on refresh cycle
    │ Converts graph JSON → GraphEngine nodes + edges
    ▼
GraphEngine
    │ Applies layout (hierarchical for deploy DAGs,
    │ force-directed for mesh topology)
    ▼
SvgCompiler → SceneGraph → SVG
    │
    ▼
nestgate.io web routes
    /viz/graphs/          — catalog of all available graphs
    /viz/graphs/{id}      — SVG render of specific graph
    /viz/graphs/{id}.json — raw graph data as JSON
    /viz/graphs/{id}.dot  — Graphviz DOT export
```

### New Capability: `graph.export`

Add to biomeOS `capability_registry.toml`:

```toml
[visualization.graph_export]
provider = "petalTongue"
method = "visualization.render.graph"
description = "Render biomeOS graph as SVG/DOT/JSON"
```

petalTongue handler receives graph data from biomeOS `graph.get`, builds `GraphEngine` with appropriate layout, renders to requested format.

### Layout Selection

| Graph Type | Layout | Rationale |
|------------|--------|-----------|
| Deploy/orchestration (`nucleus_*`, `*_deploy`) | Hierarchical (top-down) | Shows dependency ordering |
| Signal graphs (`signals/*`) | Hierarchical (left-right) | Shows signal flow |
| Pipeline graphs (`*_pipeline`) | Hierarchical (left-right) | Shows data flow |
| Continuous graphs (`game_engine_tick`) | Circular | Shows feedback loops |
| Mesh topology (`/api/topology/live`) | Force-directed | Shows mesh relationships |

### Node Rendering

| Primal Role | Visual |
|-------------|--------|
| Tower primals (bearDog, songBird, skunkBat, swarmVine) | Shared group box |
| Nest primals (nestGate, rhizoCrypt, loamSpine, sweetGrass) | Cluster |
| Node primals (toadStool, barraCuda, coralReef) | Cluster |
| biomeOS, cellMembrane, squirrel, petalTongue | Individual nodes |
| External dependencies | Dashed border |

Edge rendering: solid for `depends_on`, dashed for `feedback_to`, colored by capability domain.

---

## Implementation Steps

1. **biomeOS**: Ensure `graph.list` and `graph.get` work via Neural API socket (likely already functional)
2. **petalTongue DataService**: Add graph discovery — call `graph.list`, fetch each graph via `graph.get`
3. **petalTongue GraphEngine**: Convert biomeOS graph JSON → `Node` + `TopologyEdge` structs
4. **petalTongue web routes**: Register `/viz/graphs/` catalog and `/viz/graphs/{id}` render routes
5. **Layout**: Use hierarchical for deploy/signal/pipeline, force-directed for topology
6. **Export**: SVG (primary), DOT (secondary), JSON (raw data)

---

## Scope Control

Phase 1 (minimum viable): Static SVG renders of the 5 most important graphs served at `/viz/graphs/`. Data fetched from biomeOS `graph.get` on startup, cached, re-fetched on cascade signal.

Phase 2 (stretch): Live topology canvas with SSE push updates. Force-directed layout in browser (via WASM or server-rendered SVG with periodic refresh).

Phase 3 (future): Interactive graph editor on nestgate.io — operators can compose and deploy graphs from the browser.

---

## References

- biomeOS graph format: `biomeOS/crates/biomeos-graph/src/graph.rs`
- petalTongue GraphEngine: `petalTongue/crates/petal-tongue-core/src/graph_engine/mod.rs`
- petalTongue viz routes: `petalTongue/src/web_mode/mod.rs`
- Three-domain topology: `wateringHole/specs/THREE_DOMAIN_TOPOLOGY_SPEC.md`
- Existing manual visualizations: `biomeOS/visualizations/` (3 topics × 3 formats, Jan 2026)

---

*Graph visualization spec for team handoff. biomeOS 79 TOML graphs → petalTongue GraphEngine → nestgate.io `/viz/graphs/`. Hierarchical layout for deploy DAGs, force-directed for mesh topology. Phase 1: static SVG of top 5 graphs.*
