# footPrint Wave 142b — XSS Hardening + Test Coverage Expansion

**Date**: 2026-07-16 | **Wave**: 142b | **Commit**: `8389118`

## Summary

Deep evolution pass completing XSS hardening across all data source popups,
migrating deprecated `hexColor` API, deduplicating remaining magic numbers,
hardening the server proxy, and expanding test coverage by 77%.

## Changes

### P0 — XSS Hardening (complete)

All `innerHTML` interpolations of external data now wrapped with `escHtml()`:

| File | Surface |
|------|---------|
| `intelligence.ts` | `sourceName` in proximity panel |
| `sources/osm.ts` | Building name/addr, power voltage/operator, pipeline substance, fence material, water name |
| `sources/infrastructure.ts` | Manhole type/utility, hydrant type/diameter, streetlight type, pole operator/material |
| `sources/fema.ts` | Flood zone code, subtype |
| `sources/zoning.ts` | Zone code, description |

### P1 — hexColor Migration (23 call sites, 9 files)

All `hexColor()` calls migrated to `hexColorUnchecked()`. Deserialization paths
(`layers.ts:deserializeLayers`) now validate through `parseHexColor` with fallback,
preventing invalid color brands from persisted project data.

### P1 — Magic Number Deduplication

| Constant | File | Before |
|----------|------|--------|
| `DISCOVERY_DEBOUNCE_MS` | discover.ts | inline `800` |
| `FEET_PER_MILE` | dimensions.ts | inline `5280` |
| `AGENT_RECONNECT_MS` | agent-bridge.ts | inline `1000` |
| `SOLVER_SATISFIED_THRESHOLD` | constraints.ts | `SOLVER_TOLERANCE * 100` |
| `SOLVER_DIST_EPSILON` | constraints.ts | inline `1e-12` |
| `SOLVER_PIVOT_EPSILON` | constraints.ts | inline `1e-15` |

### P2 — Server Proxy Hardening

- **Content-Type validation**: Rejects non-JSON upstream responses before caching
  (prevents cache poisoning from HTML error pages)
- **X-Cache headers**: `HIT` / `MISS` on every proxy response for debugging

### P1 — Test Coverage Expansion

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `core/geometry.test.ts` | 15 | extractCoords/rebuildGeometry for all 7 GeoJSON types |
| `core/store.test.ts` | 22 | CRUD, queries, event batching, borrow rules, serialize |
| `core/commands.test.ts` | 14 | Add/Remove/Update/Move/Batch with undo/redo |
| `core/constraints.test.ts` | 7 | Gauss-Newton solver: horizontal, vertical, distance, coincident |
| `client/terrain.test.ts` | 11 | Contour generation, slope/aspect (Horn's method) |
| `client/sources/osm.test.ts` | 8 | Overpass response parsing: node/way/polygon detection |

**Total**: 98 → 173 tests (+77%)

## Validation

- `tsc --noEmit`: clean
- `vitest run`: 19 files, 173 tests, 0 failures
- `vite build`: clean (90 KB app + 315 KB turf + 427 KB leaflet)

## Remaining footPrint Work (blocked on other primals)

| Item | Blocker |
|------|---------|
| `PROXY_PATH` → songBird drawbridge | songBird team |
| `PROJECTS_PATH` → nestGate CAS | nestGate team |
| `WS_PATH` → petalTongue agent bridge | petalTongue team |
| `@protokarya/rustscript` npm publish | npm org setup |
| Caddy blocks for footPrint | cellMembrane team |
