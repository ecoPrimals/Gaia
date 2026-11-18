# Visualization Integration Guide for petalTongue

**Version**: 2.1.0  
**Date**: April 2, 2026  
**Audience**: Any primal or spring team that wants petalTongue to visualize their data  
**Status**: Active Standard

---

## Quick Summary

petalTongue is evolving from a fixed-widget UI to a **Grammar of Graphics** engine.
Any primal can send a grammar expression via JSON-RPC, and petalTongue will render it
across all available modalities (GUI, TUI, audio, SVG, API).

If you have data you want a human to understand, this guide tells you how to get
petalTongue to render it.

---

## Three Ways to Integrate

### 1. Send Raw Data (Simplest)

Send your data as JSON arrays over JSON-RPC. petalTongue will auto-detect the schema
and generate a default visualization.

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render",
  "params": {
    "data": {
      "inline": [
        {"timestamp": "2026-03-08T14:00:00Z", "cpu_pct": 42.3, "host": "alpha"},
        {"timestamp": "2026-03-08T14:01:00Z", "cpu_pct": 67.1, "host": "alpha"},
        {"timestamp": "2026-03-08T14:00:00Z", "cpu_pct": 31.8, "host": "beta"}
      ]
    }
  },
  "id": 1
}
```

petalTongue will infer:
- `timestamp` is temporal → X axis
- `cpu_pct` is numeric → Y axis
- `host` is categorical → color or facet

This is the lowest-effort path. petalTongue applies Tufte constraints automatically.

### 2. Send a Grammar Expression (Recommended)

Specify exactly how your data should be visualized using the Grammar of Graphics:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render",
  "params": {
    "data": {"source": "capability:health.metrics", "filter": "last_hour"},
    "variables": [
      {"name": "time", "field": "timestamp", "role": "x"},
      {"name": "value", "field": "cpu_pct", "role": "y"},
      {"name": "host", "field": "primal_id", "role": "facet"}
    ],
    "scales": [
      {"variable": "time", "type": "temporal"},
      {"variable": "value", "type": "linear", "domain": [0, 100]}
    ],
    "geometry": [{"type": "line"}, {"type": "area", "alpha": 0.15}],
    "coordinates": {"type": "cartesian"},
    "facets": {"variable": "host", "layout": "wrap", "columns": 2}
  },
  "id": 1
}
```

This gives you full control over the visual mapping while petalTongue handles
multi-modal rendering and accessibility.

### 3. Stream Data (Real-Time)

For live data (simulation output, health metrics, sensor streams), use the
streaming endpoint:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render.stream",
  "params": {
    "grammar": { ... },
    "subscription": {
      "capability": "health.metrics",
      "interval_ms": 1000
    }
  },
  "id": 1
}
```

petalTongue subscribes to your data stream and incrementally updates the
visualization without recompiling the entire grammar.

For high-throughput streams (> 1000 rows/sec), use tarpc with `bytes::Bytes`
payloads for zero-copy transfer. See the tarpc section below.

### 4. Send DataBinding Payloads (Springs)

For springs that produce typed chart data (TimeSeries, Distribution, Bar, Gauge,
Heatmap, Scatter, Scatter3D, FieldMap, Spectrum, GameScene, Soundscape), send structured `DataBinding` payloads.
This is the recommended path for spring-to-petalTongue integration.

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render",
  "params": {
    "session_id": "healthspring-pkpd-001",
    "title": "PK/PD Study: Hill Dose-Response",
    "domain": "health",
    "bindings": [
      {
        "channel_type": "timeseries",
        "id": "oral-pk-curve",
        "label": "Oral PK Concentration",
        "x_label": "Time (hr)",
        "y_label": "Concentration (mg/L)",
        "unit": "mg/L",
        "x_values": [0, 1, 2, 4, 8, 12, 24],
        "y_values": [0, 8.2, 12.1, 9.8, 5.4, 2.9, 0.7]
      },
      {
        "channel_type": "gauge",
        "id": "shannon-diversity",
        "label": "Shannon Diversity Index",
        "value": 3.2,
        "min": 0, "max": 5,
        "unit": "nats",
        "normal_range": [2.5, 4.5],
        "warning_range": [1.5, 2.5]
      },
      {
        "channel_type": "heatmap",
        "id": "attention-weights",
        "label": "Evoformer Attention",
        "x_labels": ["Q1", "Q2", "Q3", "Q4"],
        "y_labels": ["K1", "K2", "K3", "K4"],
        "values": [0.9, 0.1, 0.0, 0.0, 0.2, 0.7, 0.1, 0.0, 0.0, 0.1, 0.8, 0.1, 0.0, 0.0, 0.2, 0.8],
        "unit": "weight"
      }
    ],
    "thresholds": [
      {"label": "Normal", "min": 2.5, "max": 4.5, "status": "normal"},
      {"label": "Low", "min": 0.0, "max": 2.5, "status": "warning"}
    ]
  },
  "id": 1
}
```

**Supported `channel_type` values:**

| Type | Domain Examples | Fields |
|------|----------------|--------|
| `timeseries` | PK curves, training loss, soil moisture | x_values, y_values, labels, unit |
| `distribution` | Population PK, Monte Carlo risks | values, mean, std, comparison_value |
| `bar` | Genus abundances, categorical comparisons | categories, values, unit |
| `gauge` | Shannon diversity, SpO2, composite risk | value, min, max, normal_range, warning_range |
| `heatmap` | Plasma density, attention weights, correlation | x_labels, y_labels, values (row-major), unit |
| `scatter` | 2D scatter (PCoA, UMAP) | x, y, point_labels, x_label, y_label, unit |
| `scatter3d` | PCoA ordination, phase space, latent embeddings | x, y, z, point_labels, unit |
| `fieldmap` | ET0 maps, Richards PDE, sensor grids | grid_x, grid_y, values (row-major), unit |
| `spectrum` | FFT, HRV power spectrum, noise analysis | frequencies, amplitudes, unit |
| `game_scene` | 2D tilemaps, CRPG narratives, combat grids | scene (JSON: tilemap/sprites/entities or description/npcs/choices) |
| `soundscape` | Ambient audio, game audio, sonification | definition (JSON: layers with waveform/frequency/amplitude/pan) |

See `SCENE_FORMAT_REFERENCE.md` for full GameScene and Soundscape JSON schemas.

### 5. Stream Incremental Updates

After establishing a session with `visualization.render`, push incremental
updates without resending the full dataset:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render.stream",
  "params": {
    "session_id": "healthspring-pkpd-001",
    "binding_id": "oral-pk-curve",
    "operation": {
      "type": "append",
      "x_values": [36, 48],
      "y_values": [0.3, 0.1]
    }
  },
  "id": 2
}
```

**Stream operation types:**

| Operation | Use Case | Applies To |
|-----------|----------|------------|
| `append` | Add new data points | TimeSeries, Spectrum |
| `set_value` | Update current value | Gauge |
| `replace` | Replace entire binding | Any type (Heatmap, FieldMap, etc.) |

### 6. Render a Multi-Panel Dashboard (NEW in v1.5.0)

Send multiple DataBindings and get back a composed multi-panel dashboard as SVG:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render.dashboard",
  "params": {
    "session_id": "healthspring-full-study",
    "title": "Full Clinical Dashboard",
    "domain": "health",
    "max_columns": 3,
    "bindings": [
      { "channel_type": "timeseries", "id": "pk", "label": "PK Curve", ... },
      { "channel_type": "gauge", "id": "hr", "label": "Heart Rate", ... },
      { "channel_type": "bar", "id": "labs", "label": "Lab Panel", ... },
      { "channel_type": "spectrum", "id": "hrv", "label": "HRV Power", ... },
      { "channel_type": "heatmap", "id": "corr", "label": "Correlations", ... }
    ]
  },
  "id": 3
}
```

Response includes `panel_count`, `columns`, `rows`, and the composed SVG (or description).
Each binding is auto-compiled through the Grammar of Graphics engine with domain palette.
The session can then be exported via `visualization.export` to retrieve SVG/description.

**DataBinding auto-compilation** (v1.5.0): When springs call `visualization.render` with
DataBinding payloads, petalTongue now auto-compiles each binding to a scene graph via
the Grammar of Graphics pipeline. The compiled scenes are stored and can be exported
individually via `visualization.export`.

### 7. Load Scenario Files from CLI

petalTongue supports loading scenario JSON files directly:

```bash
petaltongue ui --scenario path/to/healthspring_scenario.json
petaltongue tui --scenario path/to/healthspring_scenario.json
```

Scenario files follow the healthSpring schema with `ecosystem.primals[].data_channels`.

### Domain Themes

petalTongue applies domain-appropriate color palettes based on the `domain` field:

| Domain | Colors | Springs |
|--------|--------|---------|
| `health` / `clinical` | Green/amber/red | healthSpring |
| `physics` / `plasma` | Purple/orange/cyan | hotSpring |
| `ecology` / `metagenomics` | Greens/browns | wetSpring |
| `agriculture` / `atmospheric` | Blues/teals | airSpring |
| `measurement` / `calibration` | Grays/blue | groundSpring |
| `ml` / `neural` | Electric blue/magenta | neuralSpring |

### Spring Discovery Pattern

Springs should NOT have compile-time dependencies on petalTongue. Instead:

1. Discover petalTongue socket at runtime:
   - Check `PETALTONGUE_SOCKET` environment variable
   - Scan `$XDG_RUNTIME_DIR/petaltongue/*.sock`
   - Scan `/tmp/petaltongue-*.sock`
2. Send JSON-RPC over the Unix socket
3. If petalTongue is not available, fall back to writing JSON files

healthSpring's `barracuda/src/visualization/ipc_push.rs` provides a reference
implementation of this pattern.

---

## Grammar Expression Reference

### Data Sources

| Type | Format | Use Case |
|------|--------|----------|
| `inline` | JSON array in the request | Small datasets, one-shot |
| `source` (capability) | `"capability:health.metrics"` | Dynamic discovery |
| `source` (primal) | `"primal:<id>.method"` | Direct primal call (not recommended; use capability) |
| `file` | `"file:///path/to/data.csv"` | Local file |
| `stream` | Streaming subscription | Real-time data |

**Sovereignty rule**: Prefer `"capability:X"` over `"primal:name.method"`.
petalTongue resolves capabilities via Songbird discovery. Never hardcode primal names.

### Variable Roles

| Role | Aesthetic Channel | Notes |
|------|-------------------|-------|
| `x` | Horizontal position | Required for most geometries |
| `y` | Vertical position | Required for most geometries |
| `z` | Depth (3D only) | Requires 3D coordinate system |
| `color` | Hue / categorical color | Automatic palette assignment |
| `fill` | Fill color | For area, bar, tile |
| `size` | Mark size | Area-proportional (Tufte-correct) |
| `shape` | Point shape | Circle, square, triangle, etc. |
| `alpha` | Opacity | 0.0 - 1.0 |
| `label` | Text annotation | Shown on hover or directly |
| `facet` | Small multiples | Splits into panels |
| `pitch` | Audio frequency | For sonification |
| `volume` | Audio amplitude | For sonification |

### Scale Types

| Type | Domain | Notes |
|------|--------|-------|
| `linear` | Numeric | Default for continuous data |
| `log` | Numeric | Logarithmic (specify base) |
| `temporal` | DateTime | Calendar-aware breaks |
| `categorical` | String | Evenly spaced categories |
| `ordinal` | Integer | Rank-order |
| `color_sequential` | Numeric → Color | Single-hue gradient |
| `color_diverging` | Numeric → Color | Two-hue with midpoint |
| `color_qualitative` | Categorical → Color | Distinct colors per category |

### Geometry Types

| Type | Required Roles | Output |
|------|---------------|--------|
| `point` | x, y | Scatter dots |
| `line` | x, y | Connected line |
| `bar` | x, y | Rectangular bars |
| `area` | x, y | Filled area under line |
| `ribbon` | x, ymin, ymax | Filled band (confidence intervals) |
| `text` | x, y, label | Text annotations |
| `tile` | x, y, fill | Heatmap cells |
| `arc` | angle, fill | Pie / donut segments |
| `errorbar` | x, ymin, ymax | Error bars |
| `mesh3d` | x, y, z | 3D mesh (forwarded to GPU) |
| `sphere` | x, y, z, radius | Molecular atoms |
| `cylinder` | x1,y1,z1,x2,y2,z2,radius | Molecular bonds |

### Coordinate Systems

| Type | Dimensions | Notes |
|------|-----------|-------|
| `cartesian` | 2D | Standard X/Y |
| `polar` | 2D | Angle + radius (pie, radar) |
| `perspective` | 3D | Camera with FOV |
| `orthographic` | 3D | No perspective distortion |
| `hierarchical` | N-D | Nested LOD (universe-scale) |

### Faceting

```json
{
  "facets": {
    "variable": "region",
    "layout": "wrap",
    "columns": 3,
    "scales": "fixed"
  }
}
```

- `layout`: `"wrap"` (single variable) or `"grid"` (row + column variables)
- `scales`: `"fixed"` (same axes, enables comparison), `"free"` (independent axes)

---

## IPC Methods

### Methods petalTongue Exposes (Your Primal Calls These)

| Method | Purpose | Params | Returns |
|--------|---------|--------|---------|
| `visualization.render` | Render a grammar expression | `GrammarExpr` | `RenderResult` (panel IDs) |
| `visualization.render.stream` | Streaming visualization | `GrammarExpr` + subscription | `StreamHandle` |
| `visualization.export` | Export to SVG/PNG/JSON | `GrammarExpr` + format | `Bytes` (file content) |
| `visualization.validate` | Check grammar without rendering | `GrammarExpr` | `ValidationResult` (Tufte score) |
| `visualization.capabilities` | What can petalTongue render? | None | `CapabilitySet` |
| `visualization.dismiss` | Remove a rendered visualization | Panel ID | `Ok` |
| `visualization.interact.subscribe` | Subscribe to interaction events | `grammar_id?`, `events[]?`, `callback_method` | `SubscriptionId` |
| `visualization.interact.apply` | Programmatically trigger an interaction | `intent`, `targets[]` | `InteractionResult` |
| `visualization.interact.perspectives` | List active perspectives | None | `Perspective[]` |
| `visualization.interact.sync` | Set perspective sync mode | `perspective_id`, `sync_mode` | `Ok` |
| `visualization.render.scene` | Render a scene (game/narrative) | DataBinding payloads | `RenderResult` |
| `audio.synthesize` | Synthesize soundscape to PCM/WAV | `definition`, `format?` | Metadata + optional `wav_base64` |

### Methods petalTongue Calls (Your Primal Exposes These)

petalTongue will call your primal's methods when the grammar references your data
via capability discovery:

| Method | Purpose | Notes |
|--------|---------|-------|
| `{domain}.list` | List available data | Schema discovery |
| `{domain}.get` | Fetch data rows | One-shot fetch |
| `{domain}.subscribe` | Stream data updates | Continuous feed |
| `{domain}.schema` | Describe data columns | Type inference |

Follow `SEMANTIC_METHOD_NAMING_STANDARD.md` for all method names.

### Events petalTongue Emits (Your Primal Subscribes)

When a human interacts with a visualization of your data, petalTongue sends
an interaction event carrying `DataObjectId` targets (data-space references,
not screen coordinates). Any modality or primal can interpret these:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.interact",
  "params": {
    "event": "select",
    "targets": [
      {"source": "health_metrics", "row_key": {"primal_id": "alpha"}}
    ],
    "perspective_id": "user_a_egui",
    "grammar_id": "health_overview",
    "timestamp": "2026-03-09T14:23:00Z"
  }
}
```

Semantic event types (modality-agnostic):

| Event | Meaning | Data Included |
|-------|---------|---------------|
| `select` | User selected data object(s) | `targets[]` with DataObjectIds |
| `focus` | User is hovering/focusing (non-committed) | Single `target` |
| `inspect` | User requested detail view | `target` + `depth` (summary/detail/raw) |
| `filter` | User applied a data filter | `variable`, `range` or `predicate` |
| `navigate` | Viewport or position changed | `viewport` with new bounds |
| `annotate` | User added an annotation | `target` + `content` |
| `command` | User issued a free-form command | `verb` + `arguments` |
| `dismiss` | User dismissed a view | `grammar_id` |

### Subscribing to Interaction Events

Your primal can subscribe to receive interaction events as they happen:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.interact.subscribe",
  "params": {
    "grammar_id": "health_overview",
    "events": ["select", "focus", "filter"],
    "callback_method": "my_primal.on_visualization_interact"
  },
  "id": 1
}
```

petalTongue will call `my_primal.on_visualization_interact` whenever a matching
interaction occurs. The callback receives the same event payload shown above.

**Subscribe to all grammars** by omitting `grammar_id`. **Subscribe to all
events** by omitting `events`.

### Programmatically Driving Interactions

Your primal can tell petalTongue to highlight, select, or focus data objects:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.interact.apply",
  "params": {
    "intent": "select",
    "targets": [
      {"source": "health_metrics", "row_key": {"primal_id": "alpha"}}
    ]
  },
  "id": 2
}
```

This enables patterns like:
- **Squirrel** detects an anomaly and tells petalTongue to highlight it
- **biomeOS** selects a primal during orchestration and petalTongue tracks it
- **healthSpring** marks a critical vital sign and petalTongue focuses the view

The interaction uses `DataObjectId` (data-space), so it works regardless of
which modality the human is using (GUI, TUI, audio, Braille).

### Listing Active Perspectives

Query which perspectives are currently active:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.interact.perspectives",
  "id": 3
}
```

Response:

```json
{
  "perspectives": [
    {
      "id": "user_a_egui",
      "modalities": ["gui"],
      "selection": [{"source": "health_metrics", "row_key": {"primal_id": "alpha"}}],
      "sync_mode": "shared_selection"
    },
    {
      "id": "user_b_tui",
      "modalities": ["tui", "audio"],
      "selection": [],
      "sync_mode": "shared_selection"
    }
  ]
}
```

---

## tarpc Integration (High Performance)

For data transfer > 1,000 rows/sec or binary payloads (meshes, images, audio),
use tarpc with `bytes::Bytes`:

```rust
#[tarpc::service]
pub trait VisualizationService {
    async fn render(expr: GrammarExpr, viewport: Viewport) -> RenderResult;
    async fn render_stream(expr: GrammarExpr, viewport: Viewport) -> StreamHandle;
    async fn export(expr: GrammarExpr, format: ExportFormat) -> Bytes;
    async fn validate(expr: GrammarExpr) -> ValidationResult;
    async fn capabilities() -> CapabilitySet;
}
```

petalTongue discovers your tarpc service via capability:
`{"capability": "visualization.render", "transport": "tarpc"}`.

All binary payloads (`Bytes`) are zero-copy over Unix sockets.

---

## barraCuda Integration (GPU Compute)

If your primal produces data that needs heavy computation before visualization
(statistical transforms, 3D tessellation, physics simulation), route the compute
through barraCuda rather than asking petalTongue to do it.

The pipeline:

```
Your Primal (raw data)
    → petalTongue (grammar expression)
    → barraCuda (GPU compute: statistics, projection, tessellation)
    → petalTongue (render the result)
```

petalTongue handles the barraCuda dispatch automatically when the grammar
expression requires computation that exceeds its local capabilities. Your primal
doesn't need to know about barraCuda.

Capabilities petalTongue offloads to barraCuda:

| Capability | Trigger |
|-----------|---------|
| `math.stat.*` | StatDensity, StatSmooth on > 10K rows |
| `math.tessellate.*` | Any 3D geometry (sphere, cylinder, mesh) |
| `math.project.*` | 3D → 2D projection with lighting |
| `math.physics.*` | Simulation steps (N-body, MD, collision) |

---

## Tufte Validation

Every grammar expression is evaluated against Tufte constraints. Your primal
can pre-validate before rendering:

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.validate",
  "params": { "grammar": { ... } },
  "id": 1
}
```

Response includes a score (0.0-1.0) and per-constraint results:

| Constraint | What It Checks |
|------------|---------------|
| `data_ink_ratio` | Proportion of visual elements that carry data |
| `lie_factor` | Whether visual effect matches data effect |
| `chartjunk` | Unnecessary decorative elements |
| `small_multiples` | Suggests faceting over overlaid color |
| `data_density` | Information per unit area |
| `color_accessibility` | Colorblind-safe, redundant encoding |
| `smallest_effective_difference` | Visual weight proportional to need |

Score > 0.75 is good. petalTongue auto-corrects common issues (extends Y-axis
to zero, applies colorblind-safe palette, reduces grid lines) when `auto_correct`
is enabled (default).

---

## Domain-Specific Examples

### biomeOS: Primal Topology

```json
{
  "data": {"source": "capability:orchestration.topology"},
  "variables": [
    {"name": "id", "field": "primal_id", "role": "label"},
    {"name": "health", "field": "health_status", "role": "color"},
    {"name": "connections", "field": "edge_count", "role": "size"}
  ],
  "geometry": [{"type": "point"}, {"type": "line"}],
  "coordinates": {"type": "force_directed"}
}
```

### healthSpring: Patient Vitals

```json
{
  "data": {"source": "capability:health.vitals"},
  "variables": [
    {"name": "time", "field": "timestamp", "role": "x"},
    {"name": "heart_rate", "field": "hr_bpm", "role": "y"},
    {"name": "patient", "field": "patient_id", "role": "facet"}
  ],
  "geometry": [{"type": "line"}, {"type": "ribbon", "ymin": "hr_lower", "ymax": "hr_upper", "alpha": 0.2}],
  "scales": [{"variable": "heart_rate", "type": "linear", "domain": [40, 200]}]
}
```

### barraCuda: Shader Performance

```json
{
  "data": {"source": "capability:math.metrics"},
  "variables": [
    {"name": "shader", "field": "shader_name", "role": "x"},
    {"name": "gflops", "field": "throughput_gflops", "role": "y"},
    {"name": "precision", "field": "fp_mode", "role": "color"}
  ],
  "geometry": [{"type": "bar"}],
  "facets": {"variable": "precision", "layout": "wrap", "columns": 2}
}
```

### ToadStool: GPU Hardware Discovery

```json
{
  "data": {"source": "capability:hardware.gpu.list"},
  "variables": [
    {"name": "adapter", "field": "name", "role": "y"},
    {"name": "vram", "field": "vram_mb", "role": "x"},
    {"name": "driver", "field": "driver_name", "role": "color"},
    {"name": "f64", "field": "f64_support", "role": "shape"}
  ],
  "geometry": [{"type": "point"}],
  "coordinates": {"type": "cartesian"}
}
```

### ludoSpring: RPGPT Dialogue Scene

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render.scene",
  "params": {
    "session_id": "ludospring-campaign-01",
    "bindings": [{
      "channel_type": "game_scene",
      "id": "tavern_entrance",
      "label": "The Rusty Anchor",
      "scene": {
        "scene_type": "dialogue_tree",
        "node": "tavern_1",
        "description": "You push open the heavy oak door. Warm light and roasting meat greet you.",
        "npcs": [
          {"name": "Innkeeper", "status": "friendly", "health": 1.0},
          {"name": "Wounded Guard", "status": "friendly", "health": 0.4}
        ],
        "choices": ["Talk to the innkeeper", "Help the wounded guard", "Order a drink"],
        "turn": 3,
        "is_ending": false
      }
    }]
  },
  "id": 1
}
```

### esotericWebb: Narrative Game Scene

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render.scene",
  "params": {
    "bindings": [{
      "channel_type": "game_scene",
      "id": "forest_path",
      "label": "Forest Crossroads",
      "scene": {
        "node": "scene_7",
        "description": "The forest path splits ahead. An old hermit sits on a moss-covered stone.",
        "npcs": [{"name": "Old Hermit", "status": "friendly"}],
        "choices": ["Take the left path", "Take the right path", "Ask the hermit for directions"],
        "turn": 5,
        "is_ending": false
      }
    }]
  },
  "id": 1
}
```

### ludoSpring: Game Audio Soundscape

```json
{
  "jsonrpc": "2.0",
  "method": "visualization.render",
  "params": {
    "bindings": [{
      "channel_type": "soundscape",
      "id": "dungeon_ambient",
      "label": "Dungeon Ambience",
      "definition": {
        "name": "Deep Dungeon",
        "duration_secs": 60.0,
        "layers": [
          {"id": "drip", "waveform": "sine", "frequency": 300.0, "amplitude": 0.2, "duration_secs": 60.0, "pan": -0.6},
          {"id": "rumble", "waveform": "white_noise", "frequency": 80.0, "amplitude": 0.15, "duration_secs": 60.0, "pan": 0.0, "fade_in_secs": 5.0}
        ],
        "master_amplitude": 0.7
      }
    }]
  },
  "id": 1
}
```

### Molecular Visualization (Future)

```json
{
  "data": {"source": "file:///data/protein.pdb"},
  "variables": [
    {"name": "x", "field": "x_coord", "role": "x"},
    {"name": "y", "field": "y_coord", "role": "y"},
    {"name": "z", "field": "z_coord", "role": "z"},
    {"name": "element", "field": "element", "role": "color"},
    {"name": "radius", "field": "vdw_radius", "role": "size"}
  ],
  "geometry": [{"type": "sphere"}, {"type": "cylinder"}],
  "coordinates": {"type": "perspective", "camera": {"orbit": true}}
}
```

---

## Sovereignty Checklist

Before integrating, confirm your primal follows these rules:

- [ ] Data sources use capability strings, not primal names
- [ ] No hardcoded ports or socket paths in grammar expressions
- [ ] Grammar expressions are JSON-serializable (no closures, no raw pointers)
- [ ] Sensitive data is not embedded in inline grammar expressions (use capability references)
- [ ] Your data methods follow `SEMANTIC_METHOD_NAMING_STANDARD.md`
- [ ] Your tarpc service uses `bytes::Bytes` for binary payloads
- [ ] Your primal announces visualization-relevant capabilities via Songbird

---

## Discovery

petalTongue finds your data via capability-based discovery. Announce your
capabilities through Songbird:

```json
{
  "jsonrpc": "2.0",
  "method": "discovery.announce",
  "params": {
    "capabilities": ["health.metrics", "health.vitals"],
    "transport": ["jsonrpc", "tarpc"],
    "schema_endpoint": "health.schema"
  }
}
```

petalTongue queries:

```json
{"method": "discovery.query", "params": {"capability": "health.metrics"}}
```

And receives your socket path and transport type. No hardcoded names.

---

## Sensory Capability Negotiation

Before rendering, consumer primals can query what the user can do:

```json
{"jsonrpc": "2.0", "method": "capabilities.sensory", "params": {}, "id": 1}
```

Returns a `SensoryCapabilityMatrix` with input/output capability flags,
validated interaction paths, and recommended modality. Use this to adapt
your visualization requests to the user's abilities.

For agentic AI sessions (Squirrel), pass `"agent": true` to get an API-only matrix.

For explicit capability overrides (e.g. from NestGate user preferences):

```json
{
  "jsonrpc": "2.0",
  "method": "capabilities.sensory.negotiate",
  "params": {
    "input": { "keyboard": true, "switch_input": true },
    "output": { "audio": true, "description": true }
  },
  "id": 2
}
```

See `wateringHole/petaltongue/SENSORY_CAPABILITY_MATRIX.md` for the full matrix specification.

---

## Related Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Sensory Capability Matrix | `wateringHole/petaltongue/SENSORY_CAPABILITY_MATRIX.md` | Input x output capability negotiation |
| Toadstool Sensor Contract | `wateringHole/TOADSTOOL_SENSOR_CONTRACT.md` | Hardware sensor event IPC protocol |
| Scene Format Reference | `wateringHole/petaltongue/SCENE_FORMAT_REFERENCE.md` | GameScene, Soundscape, narrative JSON schemas |
| Grammar of Graphics Architecture | `petalTongue/specs/GRAMMAR_OF_GRAPHICS_ARCHITECTURE.md` | Full grammar type system |
| Universal Visualization Pipeline | `petalTongue/specs/UNIVERSAL_VISUALIZATION_PIPELINE.md` | End-to-end pipeline spec |
| Interaction Engine Architecture | `petalTongue/specs/INTERACTION_ENGINE_ARCHITECTURE.md` | Bidirectional interaction, perspectives, multi-user |
| Tufte Constraint System | `petalTongue/specs/TUFTE_CONSTRAINT_SYSTEM.md` | Visualization quality constraints |
| Semantic Method Naming | `wateringHole/SEMANTIC_METHOD_NAMING_STANDARD.md` | IPC method names |
| Universal IPC Standard V3 | `wateringHole/UNIVERSAL_IPC_STANDARD_V3.md` | Transport protocol |
| biomeOS API Specification | `wateringHole/petaltongue/BIOMEOS_API_SPECIFICATION.md` | biomeOS integration |
