# sporePrint Wave 68: Deep Debt Resolution + Live Ecosystem Visualizations

**Date:** June 1, 2026
**Author:** flockGate automated session
**Repos touched:** sporePrint, petalTongue

---

## Summary

Wave 68 addresses deep technical debt in sporePrint and petalTongue while
delivering live ecosystem visualizations with progressive enhancement.

## Deliverables

### 1. Live Ecosystem Visualizations (petalTongue)

Three visualization modules built using petalTongue's scene graph + SVG compiler:

- **Entity Graph** (`/viz/entity-graph`) — 66-node force-directed layout
- **K-Derm Topology** (`/viz/kderm-topology`) — 5-layer cross-section with relay animation
- **NUCLEUS Composition** (`/viz/nucleus-composition`) — Nested layers with expand/collapse

Each serves 4 formats: SVG (default), scene-JSON, description (accessible text),
animation-JSON (client-side playback).

### 2. VizRegistry (petalTongue)

Capability-based discovery replaces hardcoded route dispatch. Registry probes the
filesystem at startup and exposes only visualizations whose data sources exist.
New visualizations can be added without modifying the route handler.

### 3. Deep Debt Resolution (sporePrint + petalTongue)

| Issue | Fix |
|-------|-----|
| 3 production `unwrap()`/`expect()` on regex | `LazyLock<Regex>` statics |
| 16 notebook files with `/home/eastgate/` | `ECOPRIMALS_ROOT` env var |
| 882-line viz_data.rs | Split into 4 modules (max 242L) |
| Shell-only parity tests | Rust `tests/parity.rs` (6 integration tests) |
| gonzales/ JS (Plotly) | Marked deprecated, timeline added |
| refresh-metrics.sh duplication | Deprecated (Rust `spore-validate refresh`) |

### 4. WASM Progressive Enhancement

- `petal-tongue-wasm` built and deployed to `static/wasm/` (593KB)
- `viz-hydrate.js` adds pan/zoom/tooltips/animation without breaking static SVG
- Server-side SVG works without JavaScript (accessibility-first)

## Architecture Notes

```
petalTongue/src/viz_data/
├── mod.rs           # VizRegistry, re-exports
├── entity_graph.rs  # Force-directed layout + scene builder
├── kderm.rs         # K-Derm topology + relay animation
└── nucleus.rs       # NUCLEUS composition + expand animation
```

Content pages embed `{{ viz_embed(src="/viz/...") }}` which is expanded to inline
SVG during rendering. Client-side JS optionally hydrates with WASM for interactivity.

## Upstream Review Requests

### For petalTongue team
- [ ] Review `viz_data/` module structure — appropriate for scene crate or stays in binary?
- [ ] VizRegistry pattern acceptable for other viz-enabled backends?
- [ ] `wasm-opt` disabled due to validation error — investigate root cause

### For primalSpring
- [ ] Validate parity test coverage against existing scenario
- [ ] Consider adding viz endpoint health check to sporeprint-pure-primal scenario

### For projectNUCLEUS
- [ ] `sporeprint_composition.toml` may need update for viz data dependencies
- [ ] Consider viz data as NestGate CAS assets vs embedded in binary

## Test Results

```
spore-validate: 89+ tests passing (3 test files, zero warnings)
petalTongue:    release build clean (22 warnings: missing docs only)
parity.rs:     6 integration tests registered (require running server)
clippy:         zero warnings on both crates (pedantic + nursery)
```

## Next Targets

- Wave 69: Provenance Trio data system (BLAKE3 content addressing)
- Wave 70: Live science dashboards from primal APIs
- gonzales/ data migration to entity-graph/NestGate (Wave 70)
- gonzales/ removal (Wave 72)
