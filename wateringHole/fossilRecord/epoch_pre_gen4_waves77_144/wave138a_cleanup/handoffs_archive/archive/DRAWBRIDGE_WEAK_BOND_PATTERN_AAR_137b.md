# Drawbridge Weak Bond Pattern — AAR Wave 137b

**Date**: Jul 13, 2026 | **From**: flockGate overwatch | **Classification**: Architectural Pattern AAR

---

## Origin

footPrint is an external TypeScript project undergoing **genetic transformation** — being incorporated into the primal ecosystem and evolved toward sovereign Rust standards. During the FP-API wiring analysis, we identified that footPrint's GIS proxy (`/api/proxy?url=<target>`) is not a proxy at all — it's the **embryonic form of a drawbridge weak bond**.

This AAR documents the pattern as a platform capability for all teams, not a footPrint-specific solution.

---

## 1. The Pattern: Drawbridge Weak Bonds

### What is a Weak Bond?

In the primal bond taxonomy:
- **Covalent bonds** — between gates on the same LAN. High trust, low latency, shared keys.
- **Ionic bonds** — between primals on the same gate. UDS sockets, riboCipher authenticated.
- **Weak bonds** — between the organism and external data sources. Low trust, breakable, reconnectable. The drawbridge mediates all weak bonds.

A **weak bond** is a managed, monitored connection from the sovereign mesh to an external service. It flows through songBird's drawbridge — the outer membrane's ion channel.

### K-Derm Analogy

```
Extracellular space     = the internet, external APIs, public data
Outer membrane          = Caddy + songBird drawbridge
Ion channels (pores)    = weak bonds — selective, gated, observable
Periplasm               = golgi relay, data arrives here first
Plasma membrane         = nftables/firewall
Cytoplasm               = NUCLEUS primals, UDS IPC
```

Weak bonds are the outer membrane pores. Each pore has:
- **Selectivity filter** — allowlist (which hosts, which paths)
- **Gating** — health check, rate limit, circuit breaker
- **Conductance** — cache policy (how much data flows per unit time)
- **Inactivation** — bond decay when the endpoint goes offline

---

## 2. Trust Tiers

Not all external data is equal. A USGS elevation service and a random API have different trust profiles. The drawbridge assigns trust tiers to weak bonds:

| Tier | Trust | Examples | Cache | Bond Behavior |
|------|-------|----------|-------|---------------|
| **scientific** | HIGH | NCBI PubChem, USGS EPQS, FEMA NFHL, NRCS soils | Long (30d) | Alert on failure, retry with backoff |
| **community** | MEDIUM | OpenStreetMap Overpass, Nominatim geocoder | Moderate (3d) | Warn on failure, expect occasional downtime |
| **commercial** | MEDIUM | Esri ArcGIS, Mapbox | Variable | ToS-aware rate limits, key rotation |
| **municipal** | LOW | City/state GIS portals (East Lansing, Michigan) | Short (1d) | Expect fragility, degrade gracefully |
| **untrusted** | NONE | Arbitrary web, social media, scraping | Never persist | Ephemeral only, quarantine responses |

Teams mark their external data sources by tier. The drawbridge enforces the tier's bond characteristics automatically.

---

## 3. Bond Registry

Teams declare weak bonds in a shared manifest. The drawbridge owns the connections.

### Proposed: `drawbridge_bonds.toml`

```toml
# drawbridge_bonds.toml — Weak bond registry for external data sources
#
# Teams declare external data dependencies here. songBird drawbridge
# manages the bonds: allowlist, cache, health monitoring, rate limits.
# Multiple consumers share a single bond (one fetch, shared cache).

[meta]
schema_version = 1
description = "Ecosystem weak bond registry — external data source connections"

# ── Scientific tier ───────────────────────────────────────────

[bonds.usgs_elevation]
tier = "scientific"
host = "epqs.nationalmap.gov"
paths = ["/v1/json"]
methods = ["GET"]
cache_days = 30
consumers = ["footPrint"]
description = "USGS Elevation Point Query Service"

[bonds.fema_flood]
tier = "scientific"
host = "hazards.fema.gov"
paths = ["/gis/nfhl/rest/services/"]
methods = ["GET"]
cache_days = 1
consumers = ["footPrint"]
description = "FEMA National Flood Hazard Layer"

[bonds.nrcs_soils]
tier = "scientific"
host = "sdmdataaccess.sc.egov.usda.gov"
paths = ["/Spatial/SDM.wms"]
methods = ["GET"]
cache_days = 90
consumers = ["footPrint"]
description = "NRCS Soil Data Access (WMS)"

[bonds.ncbi_pubchem]
tier = "scientific"
host = "ncbi.nlm.nih.gov"
paths = ["/pccompound", "/pug/pug.cgi"]
methods = ["GET", "POST"]
cache_days = 30
consumers = ["squirrel", "neuralSpring"]
description = "NCBI PubChem compound database"

# ── Community tier ────────────────────────────────────────────

[bonds.osm_overpass]
tier = "community"
host = "overpass-api.de"
paths = ["/api/interpreter"]
methods = ["POST"]
cache_days = 3
rate_rpm = 30
consumers = ["footPrint"]
description = "OpenStreetMap Overpass API (building footprints, roads)"

[bonds.osm_nominatim]
tier = "community"
host = "nominatim.openstreetmap.org"
paths = ["/search"]
methods = ["GET"]
cache_days = 7
rate_rpm = 60
consumers = ["footPrint"]
description = "OSM Nominatim geocoder (address → coordinates)"

# ── Commercial tier ───────────────────────────────────────────

[bonds.arcgis_hosted]
tier = "commercial"
hosts = ["services1.arcgis.com", "services2.arcgis.com"]
methods = ["GET"]
cache_days = 7
rate_rpm = 120
consumers = ["footPrint"]
description = "Esri ArcGIS hosted feature layers"

# ── Municipal tier ────────────────────────────────────────────

[bonds.mi_framework]
tier = "municipal"
host = "gisagocss.state.mi.us"
paths = ["/arcgis/rest/services/"]
methods = ["GET"]
cache_days = 1
fragile = true
consumers = ["footPrint"]
description = "Michigan Geographic Framework (parcels, boundaries)"

[bonds.mi_gis_portal]
tier = "municipal"
host = "gisp.mcgi.state.mi.us"
methods = ["GET"]
cache_days = 1
fragile = true
consumers = ["footPrint"]
description = "Michigan GIS portal"

[bonds.el_zoning]
tier = "municipal"
host = "gis2.cityofeastlansing.com"
paths = ["/arcgis/rest/services/ZoningDistricts/"]
methods = ["GET"]
cache_days = 1
fragile = true
consumers = ["footPrint"]
description = "City of East Lansing zoning districts"
```

### Key Properties

**Shared bonds**: If squirrel and neuralSpring both need PubChem, they declare the same bond. One cache, one health monitor, one rate limiter. No duplicate fetches.

**Team autonomy**: Any primal or spring team can add a bond by declaring it in the registry. The drawbridge enforces the tier's characteristics.

**Observable**: Every request through a weak bond is visible to skunkBat. Bond health metrics (latency, failure rate, cache hit ratio) feed into the threat detection baseline.

---

## 4. Genetic Transformation: footPrint as First Protist

footPrint is the first external project being absorbed into the ecosystem. The transformation stages:

```
External project (TypeScript/Express)
    │
    ▼
Stage 1: CLONED — source in protists/footPrint, builds with npm
    │                                                          ← WE ARE HERE
    ▼
Stage 2: DEPLOYED — SPA live at primals.eco/footprint/ (Caddy serves static)
    │               Express server disappears in production     ← DONE
    ▼
Stage 3: BONDS DECLARED — GIS proxy → drawbridge weak bonds
    │                      Express proxy logic → bond registry  ← THIS AAR
    ▼
Stage 4: PERSISTENCE ABSORBED — Express CRUD → nestGate CAS
    │                                                          ← FP-PERSIST DONE
    ▼
Stage 5: FRONTEND EVOLVED — TypeScript SPA → petalTongue parity
    │                        12 visual capability areas         ← TOPO-VIS ACTIVE
    ▼
Stage 6: PURE RUST — all footPrint capabilities expressed as primals
    │                 TypeScript is scaffolding, Rust is structure
    ▼
Absorbed: footPrint is a composition of primals, not a project
```

At each stage, the external project's capabilities get expressed through sovereign primal patterns. The Express proxy becomes drawbridge bonds. The Express CRUD becomes nestGate CAS. The React frontend becomes petalTongue visual targets. The TypeScript dissolves as the Rust primals grow.

**Other teams can follow this same path.** Any external project — a Python ML pipeline, a Go microservice, a data analysis notebook — can be genetically transformed by:
1. Clone into the ecosystem
2. Deploy via composition (Caddy/petalTongue serves the frontend)
3. Declare external dependencies as drawbridge weak bonds
4. Migrate persistence to nestGate/rhizoCrypt
5. Evolve frontend through petalTongue
6. Express all logic through Rust primals

---

## 5. How Teams Use Weak Bonds

### Declaring a Bond (any team)

Add an entry to `drawbridge_bonds.toml`:

```toml
[bonds.my_data_source]
tier = "scientific"
host = "api.example.gov"
paths = ["/v2/data"]
methods = ["GET"]
cache_days = 7
consumers = ["myPrimal"]
description = "Example government data API"
```

### Consuming a Bond (in Rust)

```rust
// In a primal's capability handler:
let response = capability_call("drawbridge.fetch", json!({
    "bond": "fema_flood",
    "path": "/gis/nfhl/rest/services/public/NFHL/MapServer/identify",
    "params": { "geometry": "-84.55,42.71", "sr": "4326" }
})).await?;

// The drawbridge handles: allowlist, cache, rate limit, health, retry
```

### Consuming a Bond (in SPA client)

```typescript
// footPrint client calls through the drawbridge, never direct:
const data = await fetch('/api/drawbridge/fema_flood?' + params);

// Caddy routes /api/drawbridge/* → songBird drawbridge
// songBird resolves the bond, enforces policy, returns cached or fresh data
```

### Monitoring (skunkBat)

```
bond:fema_flood        latency_p50=120ms  cache_hit_ratio=0.87  failures_24h=0
bond:osm_overpass      latency_p50=340ms  cache_hit_ratio=0.62  failures_24h=2
bond:el_zoning         latency_p50=890ms  cache_hit_ratio=0.95  failures_24h=8  FRAGILE
bond:ncbi_pubchem      latency_p50=200ms  cache_hit_ratio=0.91  failures_24h=0
```

---

## 6. Implementation Path

| Phase | What | Owner | Effort |
|-------|------|-------|--------|
| 1 | Create `drawbridge_bonds.toml` with footPrint's 10 bonds | flockGate | 1hr |
| 2 | songBird: `drawbridge.fetch` method reads bond registry | songBird | 4-8hr |
| 3 | songBird: per-bond cache (SHA-256 key, TTL from registry) | songBird | 2hr |
| 4 | songBird: health monitor per bond (background probe) | songBird | 2hr |
| 5 | Caddy: route `/api/drawbridge/*` → songBird | golgi | 30min |
| 6 | footPrint client: replace `/api/proxy` → `/api/drawbridge/{bond}` | flockGate | 2hr |
| 7 | skunkBat: bond metrics ingestion | skunkBat | 2hr |
| 8 | primalSpring: `s_drawbridge_bonds` validation scenario | flockGate | 2hr |

**Prerequisite**: SOCKET-DIR-UNIFY (songBird needs TLS delegation for HTTPS targets). Phase 1-2 can be designed now; Phase 3+ needs the socket fix.

---

## 7. Validation

The existing `s_fp_api_proxy` scenario (#142) validates the embryonic form. A new scenario `s_drawbridge_bonds` should validate:

- Bond registry parses and all entries have required fields
- Trust tiers are valid (scientific/community/commercial/municipal/untrusted)
- Every bond has at least one consumer
- No duplicate host+path entries
- Cache TTLs are within tier bounds
- Live phase: probe each bond endpoint for health

---

## 8. Recommendations

1. **Create `config/drawbridge_bonds.toml`** in primalSpring config alongside ecosystem_manifest.toml. footPrint's 10 GIS services are the seed entries.

2. **Retire the CSP-expansion approach.** The SPA should never fetch directly from external services. All external traffic flows through drawbridge bonds — single control point, single monitoring surface.

3. **Evolve `s_fp_api_proxy`** into `s_drawbridge_bonds` once the registry exists. The current scenario validates the embryonic pattern; the evolved scenario validates the platform capability.

4. **Document the genetic transformation pattern** so other teams absorbing external projects know the stages: clone → deploy → declare bonds → migrate persistence → evolve frontend → pure Rust.

---

*footPrint's GIS proxy isn't a workaround — it's the first weak bond. The drawbridge weak bond registry turns an ad-hoc proxy into a platform capability that any team can use for any external data source. The trust tiers (scientific → community → commercial → municipal → untrusted) let the organism maintain selective permeability to the extracellular space while keeping all external traffic observable and managed.*
