# footPrint Deep Evolution — Wave 143c

**Date:** 2026-07-16
**Scope:** Server validation hardening, dead code removal, constants centralization, test coverage expansion

---

## Summary

Fourth wave of deep evolution completing the remaining P0–P2 items from the footPrint audit. This wave focused on wiring the runtime agent protocol validators into the server REST endpoint (closing the validation gap), deleting the dead `agent-primal.ts` module, centralizing 17 remaining hardcoded values (discovery scoring, grid/snap defaults, Overpass timeout, UI timing), removing all dead exports, and expanding test coverage from 206 to 226 tests.

---

## Changes

### P0 — Server Validation Hardening

| Item | Action | Files |
|------|--------|-------|
| **Agent REST validation** | `POST /api/agent/command` now uses `parseCommandPayload()` runtime validator (created in 143b but unused). Rejects unknown actions with structured `ErrorResponse`. Eliminated `as unknown as Record<string, unknown>` cast | `server.ts` |
| **WS_PATH config drift** | `agent/server-bridge.ts` used hardcoded `'/ws'` instead of `WS_PATH` constant. Now imports and uses `WS_PATH` | `agent/server-bridge.ts` |

### P1 — Dead Code Removal

| Item | Action |
|------|--------|
| `core/agent-primal.ts` | **Deleted** — zero production imports after `registerAgentPrimal()` was removed from `app.ts` in 143b. Was a dead duplicate of the live command path in `client/agent-bridge.ts` |
| `getSource()` | **Removed** from `client/datasources.ts` — defined but never called |
| `setGridSpacing()` | **Removed** from `client/grid.ts` — no UI wiring, never called |
| `setGridSnap()` | **Removed** from `client/snap.ts` — no UI wiring, never called |
| `GRID_SPACINGS_FT` | **Removed** from `types/snap.ts` — zero importers |

### P1 — Constants Centralization

17 new constants added to `src/constants.ts`:

| Constant | Value | Replaces |
|----------|-------|----------|
| `DISCOVERY_COUNT_WEIGHT` | 0.3 | Inline in `discover.ts` |
| `DISCOVERY_PROXIMITY_WEIGHT` | 0.4 | Inline in `discover.ts` |
| `DISCOVERY_CATEGORY_WEIGHT` | 0.3 | Inline in `discover.ts` |
| `DISCOVERY_DEFAULT_BOOST` | 0.5 | Inline in `discover.ts` |
| `DISCOVERY_COUNT_DIVISOR` | 20 | Inline in `discover.ts` |
| `DISCOVERY_NO_DATA_DISTANCE` | 999 | Inline in `discover.ts` |
| `PROXIMITY_UI_LIMIT` | 8 | Inline in `intelligence.ts` |
| `DEFAULT_GRID_SPACING_FT` | 10 | Inline in `grid.ts` |
| `GRID_MIN_ZOOM` | 17 | `MIN_ZOOM` in `grid.ts` |
| `GRID_COLOR` | `#4FC3F7` | Inline in `grid.ts` |
| `GRID_MAX_LINES` | 500 | Inline in `grid.ts` |
| `DEFAULT_SNAP_DISTANCE` | 20 | Inline in `types/snap.ts` |
| `METERS_PER_FOOT` | 0.3048 | Inline in `types/snap.ts` |
| `GEOCODER_ERROR_FLASH_MS` | 1500 | Inline in `map.ts` |
| `SERVER_PORT` | 3000 | Inline in `server.ts` |
| `OVERPASS_TIMEOUT_S` wiring | (existing) | 9 hardcoded `[timeout:25]` strings in `osm.ts` + `infrastructure.ts` now use `${OVERPASS_TIMEOUT_S}` |

### P2 — Test Coverage Expansion (206 → 226)

| File | Tests | Coverage |
|------|-------|----------|
| `core/entity.test.ts` (new) | 4 | `createEntity` structure, unique IDs, parent wiring, all entity kinds |
| `client/intelligence.test.ts` (new) | 12 | `compassDir` — all 8 cardinal/intercardinal directions, negative/overflow bearings, rounding boundaries |
| `client/geojson.test.ts` (new) | 4 | `layerToFeature` — polygon, polyline, circle marker extraction, null on missing `toGeoJSON` |

### Documentation Updates

| File | Change |
|------|--------|
| `README.md` | Added runtime validation note to architecture diagram |
| `specs/PETALTONGUE_VISUAL_TARGETS.md` | Fixed module count: 12 → 11 |
| `specs/CONSTRAINT_MATRIX.md` | Fixed module count: 12 → 11 |

---

## Validation

| Check | Result |
|-------|--------|
| `tsc --noEmit` | Clean |
| `npm test` | 25 files, 226 tests passing |
| `vite build` | Clean (86.76 kB app, 314 kB turf, 427 kB leaflet) |
| TODO/FIXME/HACK scan | 0 in source |
| Dead export scan | 0 unused exports remaining |
| Stale reference scan | 0 references to deleted files (`agent-primal`, `leaflet-augment`, `spatial.ts`, `types/index`) |

---

## Codebase State

| Metric | Value |
|--------|-------|
| Production source files | 53 |
| Test files | 25 |
| Total source lines | ~9,800 |
| Test count | 226 |
| Constants centralized | ~60 (in `constants.ts`) |
| `as` casts remaining | ~120 (mostly Leaflet/GeoJSON/Turf boundary casts) |
| Largest file | `core/constraints.ts` (460L) |

---

## Upstream Gaps for Primal Teams

| Team | Gap | Priority | Status |
|------|-----|----------|--------|
| **songBird** | `PROXY_PATH` drawbridge wiring — footPrint client uses `/ext` proxy; needs drawbridge route | P2 | Blocked on songBird |
| **nestGate** | `PROJECTS_PATH` CAS wiring — project CRUD needs CAS persistence | P2 | Blocked on nestGate |
| **petalTongue** | `WS_PATH` agent bridge — WebSocket command protocol needs bridge | P2 | Blocked on petalTongue |
| **primalSpring** | `@protokarya` npm org setup for RustScript publish | P2 | Blocked on npm org |
