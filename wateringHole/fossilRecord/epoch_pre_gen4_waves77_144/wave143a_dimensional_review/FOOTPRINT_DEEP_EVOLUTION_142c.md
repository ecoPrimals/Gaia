# footPrint Deep Evolution — Wave 142c

**Date:** 2026-07-16
**Scope:** Architecture cleanup, type safety evolution, constants centralization, dead code removal, docs alignment

---

## Summary

Third wave of deep debt cleanup completing all remaining P0–P2 items from the footPrint audit. This wave focused on architectural gaps (WMS source type, discovery geometry), type safety (layerToFeature helper, Overpass type guards, DOM instanceof guards), constants centralization (basemap URLs, discovery tuning, ArcGIS layer IDs), and dead code/debris removal.

---

## Changes

### P0 — Architecture

| Item | Action | Files |
|------|--------|-------|
| **Soils WMS hack** | Added `WmsSourceDef` to source type system; `registerSource()` now handles WMS natively. Soils source no longer post-mutates internal state | `types/source.ts`, `client/datasources.ts`, `client/sources/soils.ts` |
| **Discovery geometry** | Discovery now uses `extractCoords()` from `core/geometry.ts` instead of assuming flat coordinate arrays. Polygons, MultiLineStrings, and Points now trigger discovery correctly | `client/discover.ts` |

### P1 — Type Safety

| Item | Action | Files |
|------|--------|-------|
| **`layerToFeature()` helper** | Extracted shared helper eliminating ~15 `(layer as L.Path & { toGeoJSON(): ... }).toGeoJSON() as ...` casts | `client/geojson.ts` (new), `client/intelligence.ts`, `client/discover.ts`, `client/drawing.ts`, `client/measurement.ts`, `client/snap.ts` |
| **Overpass type guards** | Added `isOverpassNode/Way/Relation` guards to `types/overpass.ts`; applied in `osm.ts` | `types/overpass.ts`, `client/sources/osm.ts` |
| **DOM instanceof guards** | Replaced `as HTMLInputElement` casts with `instanceof` checks in `properties.ts`, `storage.ts`, `map.ts` | `client/properties.ts`, `client/storage.ts`, `client/map.ts` |
| **Source type guards** | Added `isVectorSource/isTileSource/isWmsSource` guards to `types/source.ts`; used in `datasources.ts` | `types/source.ts`, `client/datasources.ts` |

### P1 — Constants Centralization

All inline magic values moved to `src/constants.ts`:

| Constant | Value | Replaces |
|----------|-------|----------|
| `BASEMAP_SATELLITE_URL` | ESRI World Imagery URL | Inline in `map.ts` |
| `BASEMAP_STREET_URL` | OSM tile URL | Inline in `map.ts` |
| `BASEMAP_LABELS_URL` | ESRI Transportation URL | Inline in `map.ts` |
| `PARCELS_TILE_URL` | Regrid tile URL | Inline in `parcels.ts` |
| `FEMA_FLOOD_ZONE_LAYER` | 28 | `FLOOD_ZONE_LAYER` in `fema.ts` |
| `MI_ROADS_LAYER` | 14 | `ROADS_LAYER` in `michigan.ts` |
| `DISCOVERY_BUFFER_RADIUS_M` | 100 | `BUFFER_RADIUS_M` in `discover.ts` |
| `DISCOVERY_MAX_FEATURE_SAMPLE` | 50 | `MAX_FEATURE_SAMPLE` in `discover.ts` |
| `DISCOVERY_PROXIMITY_RADIUS_M` | 500 | `PROXIMITY_RADIUS_M` in `discover.ts` |
| `CONFLICT_BUFFER_M` | 2 | Inline `2` in `intelligence.ts` |
| `GEOCODER_ZOOM` | 18 | Inline `18` in `map.ts` |

### P2 — Overpass Deduplication

`infrastructure.ts` now imports `queryOverpass()` from `osm.ts` instead of maintaining its own `queryOverpassNodes()` with duplicate `OverpassNodeResult` interface. Removed ~30 lines of duplicated query/parse logic.

### P2 — Dead Code & Debris Removal

| Item | Action |
|------|--------|
| `src/leaflet-augment.d.ts` | **Deleted** — pre-ECS `_fpMeta`/`_fpClickBound`/`_fpEntityId` augmentation, zero references |
| `ShapeMeta` interface | **Removed** from `types/shape.ts` — replaced by ECS `MetaComponent` |
| `hexColor` alias | **Removed** from `types/brands.ts` — all callers use `hexColorUnchecked` |
| `extractCoords` re-export | **Removed** from `core/renderer.ts` — callers import from `core/geometry.ts` directly |
| `getLayerGroup()` | **Removed** from `core/renderer.ts` — zero callers |
| `getLastSnapInfo()` | **Removed** from `client/snap.ts` — zero callers |
| `setContourInterval()` | **Removed** from `client/terrain.ts` — no UI wiring |
| `computeElevationProfile()` | **Removed** from `client/terrain.ts` — zero callers |
| `formatProximityHtml()` | **Un-exported** in `intelligence.ts` — internal only |
| `detectConflicts()` | **Un-exported** in `intelligence.ts` — internal only |
| `disableSource()` | **Un-exported** in `datasources.ts` — internal only |
| Overstep comment | Fixed `core/primal.ts` — "inspired by ecoPrimals gen3" → "for footPrint" |
| Drawing catch comments | Fixed `drawing.ts` — `/* removed */` → `/* layer may already be gone */` |
| `dist/`, `coverage/` | Cleaned local build artifacts |

### Documentation Updates

| File | Change |
|------|--------|
| `README.md` | Fixed constraint list (7 active: fixed-distance, parallel, perpendicular, horizontal, vertical, coincident, point-on-line + 3 stubs) |
| `specs/PETALTONGUE_VISUAL_TARGETS.md` | Fixed source count (8 modules, 15 sources), removed `_fpMeta` reference, removed primal name overstep |
| `specs/RUSTSCRIPT.md` | Marked README/LICENSE steps as done; updated deployment path description |

### Test Updates

| File | Change |
|------|--------|
| `client/sources/osm.test.ts` | Refactored to import real `osmToGeoJSON` instead of maintaining local copy; added relation→MultiPolygon test (174 total tests) |

---

## Validation

| Check | Result |
|-------|--------|
| `tsc --noEmit` | Clean |
| `npm test` | 19 files, 174 tests passing |
| `vite build` | Clean (89.7 kB app, 314 kB turf, 427 kB leaflet) |
| TODO/FIXME/HACK scan | 0 in non-test source |
| Dead file scan | 0 unreachable `.ts` files (excluding `rustscript/mod.ts` npm barrel) |

---

## Upstream Gaps for Primal Teams

| Team | Gap | Priority |
|------|-----|----------|
| **songBird** | `PROXY_PATH` drawbridge wiring — footPrint client uses `/ext` proxy; needs drawbridge route | P1 |
| **nestGate** | `PROJECTS_PATH` CAS wiring — project CRUD needs CAS persistence | P1 |
| **petalTongue** | `WS_PATH` agent bridge — WebSocket command protocol needs bridge | P1 |
| **cellMembrane** | Caddy blocks for footPrint API endpoints | P2 |
| **sporeGate** | `footprint-drawbridge-live` E2E scenario | P2 |
| **primalSpring** | `@protokarya` npm org setup for RustScript publish | P2 |
