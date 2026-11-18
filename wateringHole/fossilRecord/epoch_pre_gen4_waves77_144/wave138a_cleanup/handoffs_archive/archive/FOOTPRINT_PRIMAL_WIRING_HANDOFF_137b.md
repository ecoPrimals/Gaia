# footPrint Primal Wiring Handoff — Wave 137b

**Date**: 2026-07-13
**Gate**: flockGate
**Type**: Deployment Wiring Handoff
**Scope**: footPrint client-side abstraction complete — ready for primal backend wiring

---

## Summary

All client-side HTTP and WebSocket calls now go through a single API
abstraction layer (`src/client/api.ts`). Backend paths are configurable
via three constants in `src/constants.ts`. Deployment teams rewire by
changing these constants and deploying the corresponding primal services.

The Express server is a **standalone fallback** — it handles both `/api/proxy`
and `/ext` paths identically. In production composition, primals replace it
entirely.

## API Abstraction Layer

### Constants (`src/constants.ts`)

```
PROXY_PATH    = '/ext'          → songBird drawbridge
PROJECTS_PATH = '/api/projects' → nestGate CAS
WS_PATH       = '/ws'           → agent bridge
```

### Module (`src/client/api.ts`)

| Function | What | Used by |
|----------|------|---------|
| `proxyUrl(url)` | Builds `${PROXY_PATH}?url=${encode(url)}` | usgs.ts |
| `proxyGet<T>(url)` | GET through proxy, returns parsed JSON | fema, zoning, michigan, map (geocoder) |
| `proxyPost<T>(url, body)` | POST through proxy | osm, infrastructure |
| `listProjects()` | GET `${PROJECTS_PATH}` | storage.ts |
| `loadProject(name)` | GET `${PROJECTS_PATH}/${name}` | storage.ts |
| `saveProject(name, data)` | POST `${PROJECTS_PATH}/${name}` | storage.ts |
| `deleteProject(name)` | DELETE `${PROJECTS_PATH}/${name}` | storage.ts |
| `agentWsUrl()` | Builds `ws(s)://${host}${WS_PATH}` | agent-bridge.ts |

### No More Raw Fetch

Zero client-side files import `PROXY_PATH` directly or make raw `fetch()` calls
to Express endpoints. All backend communication is routed through `api.ts`.

---

## Wiring Instructions per Primal

### songBird — External Data Proxy

**What**: All external GIS data fetches (Overpass, FEMA, USGS, ArcGIS, Nominatim)
go through `PROXY_PATH` (`/ext`).

**Wire**:
1. songBird drawbridge accepts `GET /ext?url=<encoded>` and `POST /ext?url=<encoded>`
2. Host allowlist (10 hosts, defined in `src/constants.ts` `ALLOWED_HOSTS`):
   - `overpass-api.de`, `hazards.fema.gov`, `services1.arcgis.com`,
     `services2.arcgis.com`, `nominatim.openstreetmap.org`, `epqs.nationalmap.gov`,
     `sdmdataaccess.sc.egov.usda.gov`, `gisagocss.state.mi.us`,
     `gisp.mcgi.state.mi.us`, `gis2.cityofeastlansing.com`
3. Cache TTL strategy (replicate from Express `ttlForUrl()`):
   - `overpass` → 3 days
   - `fema.gov` → 1 day
   - `epqs.nationalmap.gov` → 30 days
   - `sdmdataaccess` → 90 days
   - default → 7 days
4. POST proxy: body is `application/x-www-form-urlencoded` (Overpass QL queries)
5. User-Agent: `FootPrint-HomePlanner/2.0`

**Verify**: Load map, toggle "Buildings" data source — Overpass POST goes through
songBird. Toggle "Flood Zones" — FEMA ArcGIS GET goes through songBird.

### nestGate — Project Persistence

**What**: Project save/load/delete via `PROJECTS_PATH` (`/api/projects`).

**Wire**:
1. `GET /api/projects` → list project names (returns `string[]`)
2. `GET /api/projects/:name` → load project (returns `ProjectFile`)
3. `POST /api/projects/:name` → save project (body: `ProjectFile`, returns `SaveResponse`)
4. `DELETE /api/projects/:name` → delete project (returns `DeleteResponse`)

**Types** (`src/types/project.ts`):

```typescript
interface ProjectFile {
  readonly name: string;
  readonly savedAt: string;       // ISO 8601
  readonly layers: SerializedLayers;
}

interface SaveResponse { readonly saved: string; }
interface DeleteResponse { readonly deleted: string; }
interface ErrorResponse { readonly error: string; readonly detail?: string; }
```

**CAS migration**: Content-address by `sha256(JSON.stringify(layers))`. The `name`
field is user-facing; the content hash is the storage key. `savedAt` timestamp
maps to rootPulse event time.

**Verify**: Save a project, reload page, load project — data round-trips through
nestGate CAS.

### petalTongue — Static SPA Serving

**What**: Serve `dist/client/` from Axum static file server.

**Files**:
- `dist/client/index.html` — SPA entry point (4.1 kB)
- `dist/client/assets/index-*.js` — app bundle (89.6 kB gzip: 28.8 kB)
- `dist/client/assets/vendor-turf-*.js` — Turf.js (306.9 kB gzip: 72.0 kB)
- `dist/client/assets/vendor-leaflet-*.js` — Leaflet + Geoman (427.1 kB gzip: 117.8 kB)
- `dist/client/assets/index-*.css` — styles (40.3 kB)
- `dist/client/css/` — static CSS from `public/css/`

**Caddy** (current production at `primals.eco/footprint/`):
```
handle_path /footprint/* {
    root * /path/to/footPrint/dist/client
    file_server
}
```

**Axum**: Serve `dist/client/` at root, fallback `index.html` for SPA routes.

### Agent Bridge — WebSocket

**What**: `WS_PATH` (`/ws`) carries agent state sync and commands.

**Wire**: Caddy/reverse proxy must support WebSocket upgrade at `/ws`.
Protocol: JSON messages with `type` discriminator. See `src/agent/protocol.ts`
for full message schema.

---

## Bugs Fixed in This Pass

| Bug | Fix |
|-----|-----|
| **Zoning double `/query`** — `ZONING_URL` ended with `/query`, code appended `/query?` again → `…/0/query/query?…` | `ZONING_URL` now ends at `/0`; code correctly appends `/query?` |
| **Nominatim CORS** — geocoder fetched directly from browser, bypassing proxy → CORS failures in some deployments | Nominatim now routes through `proxyGet()` like all other sources |
| **Express `/ext` 404** — production Express didn't handle `/ext`, only `/api/proxy` → data sources broken without songBird | Express now registers both `/api/proxy` and `/ext` using same handler |

## Verification

| Check | Result |
|-------|--------|
| `tsc --noEmit` | **0 errors** |
| `vitest run` | **58/58 tests pass** (12 new API tests) |
| `vite build` | **Clean, 1.33s, 3 optimized chunks** |
| Raw `fetch()` in client (excl. api.ts) | **0** |
| Direct `PROXY_PATH` imports in client (excl. api.ts) | **0** |

## Files Changed

### New files (2)
- `src/client/api.ts` — backend abstraction layer
- `src/client/api.test.ts` — 12 tests for proxy, projects, and WebSocket URL

### Modified files (11)
- `src/constants.ts` — added `PROJECTS_PATH`, `WS_PATH`; fixed `ZONING_URL`
- `src/server.ts` — extracted proxy handlers; registered `/ext` routes
- `src/client/storage.ts` — uses API layer instead of raw fetch
- `src/client/agent-bridge.ts` — uses `agentWsUrl()` from API layer
- `src/client/map.ts` — geocoder uses `proxyGet()` instead of direct fetch
- `src/client/sources/osm.ts` — uses `proxyPost()`
- `src/client/sources/infrastructure.ts` — uses `proxyPost()`
- `src/client/sources/fema.ts` — uses `proxyGet()`
- `src/client/sources/zoning.ts` — uses `proxyGet()`; zoning URL fix
- `src/client/sources/michigan.ts` — uses `proxyGet()`
- `src/client/sources/usgs.ts` — uses `proxyUrl()`

---

## Composition Wiring Summary

```
                     ┌─────────────────────────┐
                     │     Browser SPA          │
                     │  (dist/client/ assets)   │
                     └────┬─────┬─────┬────────┘
                          │     │     │
                   /ext   │     │     │ /ws
            (proxy)│      │     │     │(agent)
                   ▼      │     ▼     ▼
              songBird    │  nestGate  agent bridge
              drawbridge  │  CAS       (WebSocket)
                          │
                    /api/projects
                    (persistence)
```

The Express server becomes unnecessary once all three primals are wired.
`src/server.ts` remains as the standalone fallback for local development
without the full primal stack.

---

*flockGate — footPrint primal wiring handoff complete. API abstraction layer
in place. 3 bugs fixed. 58 tests pass. Deployment teams: pick up your section
and wire. Express server is now optional.*
