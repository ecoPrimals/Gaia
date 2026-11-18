# footPrint Deep Debt Cleanup — Wave 140a

**Date**: Jul 15, 2026 | **Wave**: 140a | **From**: flockGate
**Track**: 3 — Live Compositions | **Scope**: P0/P1 debt, dead code, XSS, turf, constants

---

## Summary

Comprehensive deep-debt pass on the footPrint composition target. 1 P0 and 7 P1 findings addressed. Codebase is now type-clean, test-green, and stripped of dead code.

---

## Changes

### P0: Discovery Pipeline Fix

`src/client/discover.ts` was completely dead post-ECS migration. The `pm:create` handler checked `shape._fpMeta` and a hardcoded color `#e74c3c`, but `_fpMeta` was never set after the ECS transition. Drawing creates entities in the store, not Leaflet shapes.

**Fix**: Replaced `pm:create` listener with ECS store event listener. Discovery now fires when a new shape entity is added to the "Property Boundary" layer, matching on `entity.parentId` → layer entity name.

### P1: Vite Dev Proxy

`/ext` in `vite.config.ts` proxied to port 7780 (stale from pre-Express migration). Server runs on 3000. Fixed to target 3000.

### P1: Server Proxy Error Handling

`handleProxyGet` and `handleProxyPost` cached upstream responses without checking `resp.ok`. Error responses (404, 500, etc.) from external GIS APIs were cached as valid data.

**Fix**: Added `resp.ok` guard before caching. Non-200 upstream responses pass through the status code without caching.

### P1: XSS Protection

Created shared `src/client/html.ts` with `escHtml()` utility. Replaced 3 duplicate implementations across the codebase. Added escaping to all unescaped innerHTML interpolation points:

| File | Escaped Data |
|------|-------------|
| `layers.ts` | Layer names, style colors |
| `app.ts` | Data source names, error messages |
| `datasources.ts` | Feature property keys and values |
| `discover.ts` | Source names, source colors |
| `agent-panel.ts` | Agent message text (consolidated) |
| `storage.ts` | Project names (consolidated) |
| `properties.ts` | Shape labels, notes (consolidated) |

### P1: Dead Code Removal

| Removed | Lines | Reason |
|---------|------:|--------|
| `src/core/spatial.ts` (SpatialIndex) | 152 | Zero imports anywhere |
| Duplicate `/api/proxy` routes | 2 | Client uses `/ext` only |
| `getAgentMessageHistory()` | 3 | Never called |
| `getSelectedEntityId()`, `applyLayerStyle()` | 15 | Never imported |
| `getActiveLayerEntityId()`, `getActiveLayerColor()` | 10 | Never imported |
| `getContourInterval()`, `getCachedGrid()`, `clearTerrain()` | 10 | Never imported |
| `addParallel/Perpendicular/Horizontal/VerticalConstraint` | 60 | Never wired to UI |
| `unregisterComputation()`, `runComputation()`, `forceFlush()` | 15 | Never called |
| `src/types/index.ts` (dead barrel) | 42 | Zero imports |
| `ProxyGetQuery` type | 3 | Never used |
| `LayerDef`, `LayerState` types | 12 | Never imported |

### P1: Constants Centralization

Added 13 named constants to `src/constants.ts` and wired them into 12 source files, replacing inline magic numbers:

| Constant | Value | Was in |
|----------|-------|--------|
| `DISCOVERY_DEBOUNCE_MS` | 800 | discover.ts |
| `REACTIVE_DEBOUNCE_MS` | 16 | reactive.ts |
| `AGENT_RECONNECT_MS` | 1000 | agent-bridge.ts |
| `AGENT_RECONNECT_MAX_MS` | 16000 | agent-bridge.ts |
| `AGENT_COMMAND_TIMEOUT_MS` | 10000 | server-bridge.ts |
| `UNDO_HISTORY_LIMIT` | 200 | history.ts |
| `AGENT_LOG_LIMIT` | 200 | agent-panel.ts |
| `TOAST_DURATION_MS` | 2000 | storage.ts |
| `JSON_BODY_LIMIT` | '10mb' | server.ts |
| `SHUTDOWN_GRACE_MS` | 5000 | server.ts |
| `DEFAULT_CONTOUR_INTERVAL_FT` | 5 | terrain.ts |
| `MAX_ELEVATION_CONCURRENT` | 6 | usgs.ts |
| `ELEVATION_THROTTLE_MS` | 50 | usgs.ts |
| `OVERPASS_TIMEOUT_S` | 25 | osm.ts, infrastructure.ts |

Inline `3.28084` replaced with `FEET_PER_METER` in intelligence.ts and terrain.ts.

### P1: Primal Name Scrub

Removed direct primal name references (songBird, nestGate) from production source comments in `api.ts` and `constants.ts`. Comments now reference generic "deployment rewire points" and "backend services". Docs/specs references preserved as fossil record.

### P1: Turf Tree-Shaking

Replaced monolithic `@turf/turf` with 12 individual sub-packages:

```
@turf/area, @turf/distance, @turf/centroid, @turf/midpoint,
@turf/nearest-point-on-line, @turf/buffer, @turf/boolean-intersects,
@turf/line-intersect, @turf/bearing, @turf/polygon-to-line,
@turf/length, @turf/helpers
```

Updated imports in 4 files: `discover.ts`, `measurement.ts`, `intelligence.ts`, `dimensions.ts`. Vite manual chunk config updated accordingly. Module count dropped from 349 → 190.

### Documentation Updates

| Document | Changes |
|----------|---------|
| `README.md` | Fixed constraint count (6→7), turf dep description, added all scripts, fixed proxy path, removed primal names from architecture diagram, added `/footprint/` base path to Quick Start URL |
| `specs/RUSTSCRIPT.md` | Updated module map (removed `newtype.ts`, added `src/types/brands.ts` section), updated package name to `@protoKarya/rustscript`, updated deployment steps to reflect existing stubs |
| `deploy/caddy-footprint-api.snippet` | Added `DELETE /api/cache` route |

---

## Validation

```
Typecheck:  PASS (0 errors)
Build:      PASS (190 modules, 3 chunks)
Tests:      13 files, 98 tests, all passing
```

---

## Remaining P2 Items (Not Blocking)

These are documented for upstream teams:

- Annotation entity kind defined in types but renderer returns `null` (planned feature)
- Dual agent architecture: capability registry (`agent-primal.ts`) unused by REST path
- `hexColor` deprecated alias still has 14+ call sites — gradual migration to `hexColorUnchecked`
- Test coverage: 13 test files cover core/rustscript/api; client layer mostly untested
- East Lansing geographic defaults (`DEFAULT_MAP_CENTER`, `ZONING_URL`) — accept as product context

---

*Wave 140a. footPrint deep debt: 1 P0 + 7 P1 fixes. Discovery pipeline restored, XSS hardened, 300+ lines dead code removed, turf tree-shaken, constants centralized.*
