# footPrint Deep Evolution — Wave 145b

**Date:** 2026-07-17
**Scope:** Protocol security hardening, store type safety, serialize/deserialize validation, Leaflet cast elimination, exhaustive switching

---

## Summary

Final frontier deep debt cleanup. This wave hardens the two highest-risk untrusted-input boundaries (WebSocket protocol + project file deserialization), restructures the ECS store's internal type model, and eliminates cast-and-pray patterns across Leaflet integration layers. After this wave, only 4 `as unknown` casts remain in production — all at JSON parse boundaries backed by thorough runtime validation.

---

## Changes

### P0 — Protocol Security (highest impact)

| Item | Action | Files |
|------|--------|-------|
| **Deep wire message validation** | `parseWireMessage` now validates per-variant required fields: `state-sync` checks `entities` array with per-entity `id`/`kind` validation, `command` validates `id` + nested payload, `command-result` checks `id`/`ok`, messages check `text`/`timestamp`, `agent-action` checks `description`/`timestamp` | `agent/protocol.ts` |
| **Deep command payload validation** | `parseCommandPayload` validates per-action fields: `add-entity` requires valid `kind` ∈ `ENTITY_KINDS`, `remove-entity`/`update-component`/`move-geometry` require `entityId`, `update-component` requires valid `componentKey` + non-undefined `value`, `move-geometry` requires numeric `deltaLng`/`deltaLat` | `agent/protocol.ts` |
| **Component value validation** | Added `isValidComponentValue(key, value)` — runtime shape validator per component key (geometry, style, meta, layer, dimension, constraint, elevation). Used in agent-bridge before store mutation | `core/entity.ts`, `client/agent-bridge.ts` |
| **Exhaustive command handling** | Added `never` exhaustiveness check on `default` switch branch in `handleCommand` — TypeScript now proves all `CommandPayload` variants are handled | `client/agent-bridge.ts` |
| **Server request validation** | Refactored `/api/agent/messages` validation from `req.body as { text }` to explicit unknown-first validation. Fixed `/api/agent/command` entityId extraction using discriminated union narrowing instead of generic cast | `server.ts` |

### P0 — Store Type Safety

| Item | Action | Files |
|------|--------|-------|
| **MutableEntity internal storage** | Store now uses `Map<EntityId, MutableEntity>` internally, exposing `ReadonlyEntity` only at the `get()` boundary. Eliminates 3 mutation casts (`entity as { components: ComponentMap }`) and the double-cast `as unknown as ReadonlyEntity` in `get()` | `core/store.ts` |

### P1 — Serialization Validation

| Item | Action | Files |
|------|--------|-------|
| **Typed serialize builder** | Replaced `Record<string, unknown>` property bag with typed `SerializedShapeProps` construction. Added `_entityId` to the interface for serialize/deserialize symmetry | `client/layers.ts`, `types/shape.ts` |
| **`parseSerializedShapeProps`** | Runtime validator for project file deserialization — validates all field types (`label`, `notes`, `status`, `color`, `createdAt`, `layerId`, `_entityId`, `_shapeType`, `_radius`) with `exactOptionalPropertyTypes` compliance | `types/shape.ts` |
| **EntityId brand erasure** | `layerEntityId as string` → `String(layerEntityId)` | `client/layers.ts` |

### P1 — Leaflet Cast Elimination

| Item | Action | Files |
|------|--------|-------|
| **`instanceof L.Path`** | Replaced 5× `'setStyle' in layer` / `'bindPopup' in layer` + cast patterns with `instanceof L.Path` — TypeScript narrows automatically | `client/drawing.ts` (3), `client/datasources.ts` (1), `core/renderer.ts` (1) |
| **`instanceof L.LatLng`** | Added runtime guards for Geoman `pm:snap` and `pm:vertexadded` events — validates `latlng` presence and type before use, replacing double-casts through `unknown` | `client/snap.ts`, `client/dimensions.ts` |
| **TS `in` narrowing** | `measurement.ts` `preventDefault` — eliminated cast by leveraging TS 4.9+ `in` operator narrowing | `client/measurement.ts` |
| **`String()` for brand erasure** | `style.color as string` → `String(style.color)` in renderer | `core/renderer.ts` |

### P2 — Remaining Cast Analysis

| Item | Action | Files |
|------|--------|-------|
| **`discover.ts` entityId** | Replaced inline `entityId as EntityId` brand cast with `entityIdFrom()` import | `client/discover.ts` |
| **`discover.ts` GeoJSON** | Kept `structuredClone(geo.geojson) as GeoJSON.Geometry` — necessary at readonly→mutable boundary (TS preserves readonly in structuredClone return type) | `client/discover.ts` |
| **Server project validation** | Refactored from 3 repeated `(body as {…})` casts to single `Record<string, unknown>` with field-level checks | `server.ts` |

### Test Updates

| File | Change |
|------|--------|
| `agent/protocol.test.ts` | Updated to reflect deep validation: tests now provide valid per-variant fields. Added 2 new negative test cases (reject messages/payloads with valid discriminant but missing required fields). **228 total tests, 25 files** |

---

## Validation

| Check | Result |
|-------|--------|
| `tsc --noEmit` | Clean |
| `npm test` | 25 files, 228 tests passing |
| `vite build` | Clean (90.3 kB app, 314 kB turf, 427 kB leaflet) |
| TODO/FIXME/HACK scan | 0 in non-test source |
| `as unknown` remaining | 4 total (JSON.parse boundary + protocol validators backed by deep validation) |
| Files >800 lines | 0 (largest: constraints.ts at 460) |

---

## Remaining Cast Inventory (production src/, excluding test + rustscript/)

| Category | Count | Nature |
|----------|-------|--------|
| **JSON parse boundaries** | 6 | `resp.json() as T`, `JSON.parse(data) as unknown` — inherent to fetch/JSON APIs |
| **GeoJSON geometry narrowing** | ~12 | `Feature` → `Feature<Polygon>` for Turf.js API calls — inherent to Turf's specific-geometry params |
| **Leaflet union narrowing** | ~4 | `getLatLngs()` returns `LatLng[] | LatLng[][]` union; `src.layer as L.GeoJSON` — inherent to Leaflet type system |
| **Brand constructors** | ~8 | `brands.ts` validated/unchecked constructors — by design |
| **Protocol validators** | 2 | `raw as unknown as AgentWireMessage` — backed by deep per-variant validation |
| **`as const`** | ~4 | Safe TypeScript const assertions |

All remaining casts are at library/parse trust boundaries or are brand constructors by design. No unvalidated `as unknown` casts remain.

---

## Upstream Gaps for Primal Teams (unchanged)

| Team | Gap | Priority |
|------|-----|----------|
| **songBird** | `PROXY_PATH` drawbridge wiring — footPrint client uses `/ext` proxy; needs drawbridge route | P1 |
| **nestGate** | `PROJECTS_PATH` CAS wiring — project CRUD needs CAS persistence | P1 |
| **petalTongue** | `WS_PATH` agent bridge — WebSocket command protocol needs bridge | P1 |
| **cellMembrane** | Caddy blocks for footPrint API endpoints | P2 |
| **sporeGate** | `footprint-drawbridge-live` E2E scenario | P2 |
| **primalSpring** | `@protokarya` npm org setup for RustScript publish | P2 |
