# footPrint Composition — flockGate Spin-Up (Wave 136b)

**Date**: 2026-07-11
**Gate**: flockGate
**Scope**: Clone, install, verify dev server, audit composition surface.

---

## Delivered

| Step | Status | Detail |
|------|--------|--------|
| Clone | DONE | `protists/footPrint` from `git@github.com:protoKarya/footPrint.git` (4 commits, HEAD `dd82281`) |
| Node.js toolchain | DONE | fnm → Node v24.18.0 LTS, npm 11.16.0 |
| `npm install` | DONE | 276 packages installed (11 audit vulnerabilities — inherited from upstream deps, not blocking) |
| Vite dev server | PASS | `http://localhost:5173/` → 200, Leaflet/Geoman/Turf.js SPA loads |
| Express backend | PASS | `http://localhost:3000` → WebSocket agent bridge + REST API active |
| Dual-server concurrency | PASS | `npm run dev` runs both via `concurrently`, Vite proxies `/api` to Express |

## Codebase Audit — Composition Surface

### What the Express server does (to be absorbed by primals)

| Express endpoint | What it does | Absorbing primal |
|-----------------|--------------|-----------------|
| `GET/POST/DELETE /api/projects/:name` | Project CRUD — JSON files in `projects/` | **nestGate** CAS (content-addressed, rootPulse-traced) |
| `GET/POST /api/proxy?url=` | Proxied external data fetch with host allowlist + disk cache | **songBird** drawbridge routing |
| `DELETE /api/cache` | Clear disk cache | songBird cache management |
| `GET /api/agent/status` | Agent bridge status | Overwatch coordination (nestGate) |
| `GET /api/agent/state` | ECS shadow state snapshot | nestGate CAS live subscription |
| `POST /api/agent/command` | Send command to browser agent | nestGate JSON-RPC `coord.command` |
| `GET/POST /api/agent/messages` | Agent ↔ user message bus | nestGate coordination backend |
| WebSocket `/ws` | Real-time shadow state sync | petalTongue Axum WebSocket |

### Host allowlist (songBird drawbridge will enforce)

```
overpass-api.de, hazards.fema.gov, services1.arcgis.com,
services2.arcgis.com, nominatim.openstreetmap.org,
epqs.nationalmap.gov, sdmdataaccess.sc.egov.usda.gov,
gisagocss.state.mi.us, gisp.mcgi.state.mi.us,
gis2.cityofeastlansing.com
```

### Browser frontend (stays as-is, primals serve it)

- **Map engine**: Leaflet 1.9.4 + ESRI satellite + OSM street tiles
- **Drawing**: Leaflet-Geoman 2.19 (polygon, polyline, rect, circle, marker)
- **Spatial compute**: Turf.js 7.x (geodesic measurement, conflict detection, proximity)
- **ECS**: Full entity-component-system with command/undo, constraint solver (Gauss-Newton)
- **Data sources**: 8 overlays (OSM/Overpass, Regrid parcels, FEMA flood, zoning, USGS elevation, NRCS soils, MI GIS, infrastructure)
- **RustScript**: 12 Rust safety modules in TypeScript (Result, Option, Owned, RefCell, Iter, Cow, Channel, Vec, Newtype, exhaustive match)

### Architecture snapshot

```
Browser (Leaflet + Geoman + Turf.js + RustScript ECS)
    │
    ├── Vite dev server (:5173)  ──proxy──→  Express (:3000)
    │                                            │
    │                                  ┌─────────┴──────────┐
    │                                  │                     │
    │                         Project CRUD           Data source proxy
    │                         (JSON files)           (allowlisted hosts)
    │                                                    │
    │                                         ┌──────────┼──────────┐
    │                                     Overpass   FEMA    USGS  ...
    │
    └── WebSocket /ws (agent bridge — ECS shadow state)
```

**Target architecture** (Express disappears):

```
Browser (same frontend, same JS)
    │
    └── petalTongue Axum (:8080)
            │
            ├── Static file server (serves Leaflet frontend)
            ├── WebSocket (ECS shadow state → nestGate CAS subscription)
            ├── /api/projects/* → nestGate CAS JSON-RPC
            ├── /api/proxy/* → songBird drawbridge (same allowlist)
            └── Auth → bearDog TLS termination
```

## Visual Target Spec

12 visual target areas defined in `specs/PETALTONGUE_VISUAL_TARGETS.md`:
VT-1 Map Engine, VT-2 Drawing Tools, VT-3 Layer System, VT-4 Data Source Overlays,
VT-5 Measurement, VT-6 Constraint Solver, VT-7 Intelligence Layer, VT-8 Project
Persistence, VT-9 Snap & Grid, VT-10 Status Bar, VT-11 UI Theme, VT-12 Agent Bridge.

## Next Steps

1. petalTongue: Begin VT-1/VT-2 parity (serve Leaflet frontend from Axum static files)
2. nestGate: Map `ProjectFile` JSON schema to CAS family structure
3. songBird: Add footPrint allowlist hosts to drawbridge routing config
4. skunkBat (SKUNY-INGEST): Map Caddy JSON access logs to `baseline.observe` format
5. flockGate: Coordinate composition wiring as teams deliver endpoints

---

*flockGate — footPrint composition spun up. Dev server verified. Express surface mapped for primal absorption. Browser frontend is the product; primals are the backend.*
