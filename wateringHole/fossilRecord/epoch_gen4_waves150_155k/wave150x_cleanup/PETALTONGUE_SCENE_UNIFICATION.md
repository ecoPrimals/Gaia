# petalTongue Scene Unification — 2D-as-3D-Slice + Correct Consumer Integration

**Date**: Jul 18, 2026 | **Wave**: 150h | **From**: eastGate overwatch
**For**: petalTongue team, esotericWebb team
**Priority**: P2 (architectural evolution)

---

## Part 1: esotericWebb Integration Correction

### Problem

esotericWebb V21 AAR reports using `ui.render` with `{"type": "text",
"content": "...", "metadata": {...}}` for scene pushing. Investigation
reveals this is **incorrect usage** — `ui.render` only accepts
`content_type: "graph"` and is a desktop graph-display trigger, not a
general-purpose content renderer. Webb may be getting success
acknowledgments without actual rendering.

### Webb AAR Errors

| Webb Claim | Actual |
|------------|--------|
| SceneGraph is 3D (position/rotation/scale) | **2D** — `Transform2D` affine matrix (`a,b,tx,c,d,ty`) |
| Edges with `a` field | **No edges** — hierarchy via `children: [node_id]` |
| `ui.render` accepts `{"type":"text","content":"..."}` | Only accepts `content_type: "graph"` |

### Correct Integration Path

petalTongue already has `DataBinding::GameScene` with a dedicated narrative
renderer (`chart_renderer/game_scene_renderer.rs`) that auto-detects
narrative vs tilemap scenes. Webb's scene format maps directly.

**esotericWebb ACTION**: Switch from `ui.render` to `visualization.render`:

```json
{
  "method": "visualization.render",
  "params": {
    "session_id": "webb-session",
    "title": "Current Scene",
    "bindings": [{
      "channel_type": "game_scene",
      "id": "scene-1",
      "label": "Forest Clearing",
      "scene": {
        "node": "clearing_01",
        "description": "Moonlight filters through ancient oaks...",
        "npcs": [{"name": "Mira", "status": "friendly", "health": 1.0}],
        "turn": 3,
        "is_ending": false,
        "choices": ["Approach Mira", "Hide in shadows"]
      }
    }]
  }
}
```

This feeds into petalTongue's existing pipeline:
- `DataBinding::GameScene` → `GrammarExpr` → SceneGraph (for visual)
- `DataBinding::GameScene` → `describe_narrative_scene()` (for accessibility)
- `DataBinding::GameScene` → `AudioCompiler` (for sonification)
- `DataBinding::GameScene` → egui `draw_narrative_scene()` (for native UI)

**Benefits over `ui.render`**:
- Real rendering through the grammar pipeline
- Multi-modal output (SVG, accessibility text, audio, haptic)
- Session management (state tracked, stream updates work)
- Semantic fields preserved (`choices`, NPC status, turn count)

### Spring Envelope Alternative

If Webb runs as a songBird-registered capability, it can use the spring
data adapter format directly:

```json
{
  "channel_type": "game_scene",
  "scene": { ... }
}
```

This is auto-adapted by `SpringDataAdapter` into the full
`VisualizationRenderRequest`.

---

## Part 2: 2D-as-3D-Slice — Manim-Style Scene Unification

### Motivation

petalTongue's current architecture is **2D-first with parallel 3D paths**.
`SceneNode` uses `Transform2D` exclusively; 3D is handled via separate
`GpuCompiler` and z-band scatter plots. This creates two problems:

1. **Consumers must know which path to use** — the grammar compiler has
   `Perspective3D` as a coordinate system but doesn't wire it through to
   SceneNode transforms.
2. **2D and 3D cannot share a scene** — a visualization mixing text labels,
   2D charts, and 3D molecular structures requires three separate pipelines.

### Proposed Architecture: Unified Projective Scene Graph

Treat 2D as a degenerate case of 3D, where the camera is an orthographic
projection at z=0. This is how Manim handles the 2D/3D continuum.

```
                    Unified SceneGraph
                          │
              ┌───────────┼────────────┐
              ▼           ▼            ▼
         Transform3D  Transform3D  Transform3D
         (x,y,z=0)   (x,y,z=0)   (x,y,z>0)
              │           │            │
              ▼           ▼            ▼
         Text/Rect    Line/Arc    Mesh/Sphere
              │           │            │
              └───────────┼────────────┘
                          │
                      Camera
                    ┌─────┼─────┐
                    ▼           ▼
              Orthographic  Perspective
              (2D output)   (3D output)
                    │           │
                    ▼           ▼
              SvgCompiler   GpuCompiler
              EguiCompiler  EguiCompiler
```

### Changes Required

#### Phase 1: Transform Unification (non-breaking)

**`SceneNode`** gains `Transform3D` while keeping backward compatibility:

```rust
pub struct SceneNode {
    pub id: NodeId,
    pub transform: Transform3D,  // was Transform2D
    pub primitives: Vec<Primitive>,
    pub children: Vec<NodeId>,
    pub visible: bool,
    pub opacity: f32,
    pub label: Option<String>,
    pub data_source: Option<String>,
}
```

`Transform3D` already exists in `transform.rs`. For 2D scenes, z
components default to identity (z=0, no rotation around x/y).

**Backward compat**: `Transform2D::into_3d()` and `Transform3D::to_2d()`
converters. JSON deserialization accepts both formats (6-field → 2D
promoted to 3D; 16-field → native 3D).

#### Phase 2: Camera + Projection

Add a `Camera` to `SceneGraph`:

```rust
pub struct SceneGraph {
    nodes: HashMap<NodeId, SceneNode>,
    root_id: NodeId,
    camera: Camera,
}

pub enum Camera {
    Orthographic { center: Vec2, zoom: f32 },
    Perspective { position: Vec3, target: Vec3, fov: f32 },
}
```

Default camera is `Orthographic { center: (0,0), zoom: 1.0 }` — pure 2D.
Consumers creating 3D scenes set a `Perspective` camera.

**SvgCompiler**: Projects through camera before emitting SVG paths.
For orthographic, this is identity (current behavior).

**EguiCompiler**: Uses camera for viewport transform (replaces current
`ViewCamera` pan/zoom).

**GpuCompiler**: Uses camera directly for vertex shader projection
(already does something similar).

#### Phase 3: Grammar Compiler Unification

The grammar compiler currently extracts only x,y from data:

```
GrammarExpr { coord: Perspective3D } → SceneGraph (currently ignores z)
```

Wire z through:
- `Scatter3D` → z coordinates in `Transform3D.tz`
- `Surface` geometry → mesh primitives with z
- `Bar3D` → extruded rects with z depth
- Text/labels → always z=0 (screen-space overlay)

#### Phase 4: Narrative as Scene Space

With unified transforms, narrative content maps naturally:

```
GameScene {
    node: "clearing_01"
    description: "Moonlight filters..."
    npcs: [Mira, Aldric]
}
  ↓ DataBinding → GrammarCompiler
  ↓
SceneGraph {
    camera: Orthographic  // 2D slice
    nodes: {
        "bg":    { transform: identity, primitives: [Rect(scene_bg)] }
        "title": { transform: translate(0, -h/2), primitives: [Text("Forest Clearing")] }
        "desc":  { transform: translate(0, 0), primitives: [Text("Moonlight...")] }
        "npc-0": { transform: translate(-w/4, h/4), primitives: [Text("Mira"), Circle(status)] }
        "npc-1": { transform: translate(w/4, h/4), primitives: [Text("Aldric"), Circle(status)] }
    }
}
```

When petalTongue has a 3D rendering surface (toadStool GPU dispatch), the
same scene can be rendered with `Camera::Perspective` — NPCs become 3D
entities in a spatial environment. The **data and scene graph are identical**;
only the camera changes.

### Phasing

| Phase | Scope | Breaking? | Effort |
|-------|-------|-----------|--------|
| 1 | Transform3D on SceneNode + compat layer | No | Small |
| 2 | Camera + projection in compilers | No (default orthographic) | Medium |
| 3 | Grammar compiler z-wiring | No (z defaults to 0) | Medium |
| 4 | Narrative layout in scene space | No | Small |

All phases are **non-breaking** — existing 2D consumers see no change.
The `Transform2D` JSON format continues to work via promotion.

### Why This Matters for the Ecosystem

- **tideGlass** (computational chemistry): molecular structures are
  inherently 3D. A unified scene graph lets tideGlass scenes include both
  3D molecular visualizations and 2D data charts without pipeline switching.
- **footPrint** (GIS): elevation data and terrain are 3D. The grammar
  compiler can render topographic surfaces with perspective cameras.
- **esotericWebb** (CRPG): game worlds gain spatial depth. Same narrative
  data renders as 2D text or 3D environment depending on the client.
- **sporePrint** (docs): SVG diagrams gain optional depth for architecture
  visualization while defaulting to flat 2D.

---

## Action Items

| Team | Action | Priority |
|------|--------|----------|
| **esotericWebb** | Switch `ui.render` → `visualization.render` with `game_scene` binding | P1 (integration bug) |
| **petalTongue** | Document `visualization.render` as canonical path for all composition rendering | P2 |
| **petalTongue** | Phase 1: `SceneNode.transform` → `Transform3D` with 2D compat layer | P2 |
| **petalTongue** | Phase 2: Add `Camera` to `SceneGraph`, wire through compilers | P2 |
| **petalTongue** | Phase 3: Grammar compiler z-wiring for Perspective3D | P3 |
| **petalTongue** | Phase 4: Narrative layout engine in scene space | P3 |

---

*This evolution makes petalTongue a universal rendering engine: any data
type (narrative, scientific, geospatial, molecular) enters through the
grammar pipeline, lives in a unified 3D scene graph, and exits through
any modality (SVG, GPU, audio, accessibility, haptic). The 2D case is
just an orthographic camera at z=0 — a slice of the full space.*
