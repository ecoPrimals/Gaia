# footPrint Overwatch AAR — Wave 147e

**Date**: Jul 17, 2026 | **From**: eastGate overwatch
**Scope**: Deep debt evolution waves 145a–147e — cast elimination, protocol
security, solver extraction, route wiring, test expansion

---

## What Happened

Four footPrint commits across waves 145a–147e, driven by continuous deep debt
cleanup, overstep elimination, and evolution toward primal composition readiness.

### Commit 1: `e91776d` — server validation, source property typing (wave 145a)

| Dimension | Change |
|-----------|--------|
| Server security | Runtime validation for POST /api/projects body — no unchecked `as ProjectFile` |
| Source typing | `femaProps`, `zoningProps`, `MichiganRoadProperties` helpers — eliminate generic `Record<string, unknown>` |
| Cast elimination | `toLngLat` exported from geometry.ts, `instanceof L.Marker`/`L.Polyline` in snap.ts |

### Commit 2: `5b185a0` — protocol security hardening (wave 145b)

| Dimension | Change |
|-----------|--------|
| Protocol | `parseWireMessage` + `parseCommandPayload` deep per-variant field validation |
| Store | Internal `MutableEntity` — eliminates mutation casts in `EntityStore` |
| Serialization | `parseSerializedShapeProps` runtime validator, `exactOptionalPropertyTypes`-safe |
| Cast patterns | `instanceof L.Path` replaces `'setStyle' in obj` in drawing/datasources/renderer |
| Exhaustiveness | `never` check on `handleCommand` default branch |
| API hygiene | `isValidComponentValue` runtime guard for update-component payloads |

### Commit 3: `de64053` — server security, constants consolidation (wave 147c)

| Dimension | Change |
|-----------|--------|
| Server security | `sanitizeProjectName` path traversal guard on GET/DELETE project routes |
| Constants | `APP_VERSION`, `SNAP_GRID_MAX_POINTS`, `SNAP_SOURCE_LABEL_RADIUS_M`, `DISCOVERY_AUTO_ENABLE_IDS`, `CONFLICT_UTILITY_SOURCE_IDS`, `ELEVATION_SAMPLE_CAP` |
| Route wiring | `PROJECTS_PATH`, `PROXY_PATH` wired in server.ts |
| API hygiene | Un-exported `bindShapeClick`, `CategoryBoost`, `StoreEventType`; removed orphan `ElevationProfile` |
| Tests | +15 (history.ts 10 tests, reactive.ts 5 tests) |

### Commit 4: `2e5b68f` — solver extraction, full route wiring (wave 147e)

| Dimension | Change |
|-----------|--------|
| Architecture | Gauss-Newton solver engine extracted to `src/core/solver.ts` (251L) — pure math, zero ECS dependency |
| File sizes | `constraints.ts` 460L → 235L; `solver.ts` 251L. No file > 400L |
| Route wiring | `AGENT_PATH`, `CACHE_PATH`, `HEALTH_PATH` constants — all 6 server routes configurable |
| Tests | +23 solver tests (error functions, linear system, GN convergence) |
| Bugfix | `reactive.test.ts` `exactOptionalPropertyTypes` compliance |

---

## Current Posture

| Metric | Value |
|--------|-------|
| Tests | **266** (28 test files) |
| tsc | **clean** (strict, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`) |
| vite build | **clean** |
| Debt markers | **0** |
| Largest file | `terrain.ts` (397L) — all files < 400L |
| Production LOC | 8,685 |
| Test LOC | 2,635 |
| `as unknown` casts | 0 remaining in production code |
| Route constants | 6/6 (PROJECTS_PATH, PROXY_PATH, AGENT_PATH, WS_PATH, CACHE_PATH, HEALTH_PATH) |

---

## Composition Wiring Status

All server routes are single-point-of-configuration via `src/constants.ts`:

| Endpoint | Constant | Absorbing Primal | Status |
|----------|----------|-----------------|--------|
| `/api/projects/*` | `PROJECTS_PATH` | nestGate (CAS) | PLANNED |
| `/ext` | `PROXY_PATH` | songBird (drawbridge) | **BLOCKS LIVE** |
| `/api/agent/*` | `AGENT_PATH` | petalTongue | PLANNED |
| `/ws` | `WS_PATH` | petalTongue | PLANNED |
| `/api/cache` | `CACHE_PATH` | songBird | PLANNED |
| `/api/health` | `HEALTH_PATH` | monitoring | PLANNED |

---

## What Remains (footPrint-internal)

| Item | Priority | Notes |
|------|----------|-------|
| Client-side test coverage (terrain, layers, drawing) | P2 | DOM-dependent — needs jsdom or Leaflet mocks |
| `terrain.ts` (397L) — near threshold | P3 | Naturally cohesive; split not warranted yet |
| Snap grid visualization | P3 | UI feature, not debt |

**No P0 or P1 internal items remain.** footPrint's critical path is now
entirely upstream:

1. **sporeGate**: NUCLEUS service unit deploy (cellMembrane)
2. **songBird**: Drawbridge route for `/ext` proxy
3. **cellMembrane**: Caddy blocks (SHIPPED — awaiting deploy)

---

## Upstream Demand Signal (unchanged from 147c)

| Gap | Owner | Priority |
|-----|-------|----------|
| `PROXY_PATH` drawbridge wiring | songBird | **P0** — blocks live |
| NUCLEUS service unit on sporeGate | cellMembrane | **P0** — blocks live |
| `PROJECTS_PATH` CAS wiring | nestGate | P1 |
| `WS_PATH` agent bridge | petalTongue | P1 |
| `@protokarya` npm org for RustScript publish | primalSpring | P2 |

---

*footPrint internal evolution is complete for this phase. 266 tests, 0 debt,
all routes configurable, solver extracted, no casts remaining. Overwatch
handoff to upstream primal teams for composition deploy.*
