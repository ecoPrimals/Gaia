# Composition Routing Standard

**Authority**: Overwatch + Ecosystem Convention
**Status**: Active (Wave 155h — reviewed, content current)
**Date**: 2026-07-29
**Prerequisites**: `../operations/GATEHOUSE_DARKFOREST_STANDARD.md`, `../foundations/DIDERM_DOMAIN_ARCHITECTURE.md`

---

## Purpose

This standard defines how live compositions (protoKarya projects and
other deployed products) register with the sovereign routing
infrastructure, ingest external data, and expose capabilities to
the mesh.

Every composition that wants a `*.primals.eco` subdomain or mesh
capability registration MUST follow this standard.

---

## Requirements

### 1. Subdomain Registration

Compositions receive subdomains through the `*.primals.eco` wildcard
DNS. No Cloudflare changes are needed. Only a Caddy server block
on golgi is required.

**Standard**: `prefix.primals.eco` subdomain is the REQUIRED pattern
for all live compositions. Path-based routing on the root domain
(`primals.eco/path/`) is NOT standard and MUST NOT be used for new
compositions. The root domain is reserved for sporePrint content.

**Rule**: Add a Caddy block to `provision/provision-golgi.sh` with
the `security_headers` import. The wildcard catch-all block returns
404 for unclaimed subdomains.

```caddy
myproject.primals.eco {
    import security_headers
    reverse_proxy MESH_IP:PORT
}
```

Upstream MUST be the WireGuard mesh IP of the gate running the
service (`10.13.37.x:PORT`), not `localhost`. Caddy on golgiBody
proxies over the WireGuard mesh to the target gate.

### Root Domain Redirect

The root domain `primals.eco` redirects to `sporeprint.primals.eco`
(the ecosystem's public face). No compositions serve from the root.

```caddy
primals.eco {
    import security_headers
    redir https://sporeprint.primals.eco{uri} permanent
}
```

### 2. Drawbridge Capability Registration

Compositions that serve capabilities MUST register them via songBird
drawbridge environment variables:

```bash
SONGBIRD_DRAWBRIDGE_ROUTES=/path=capability_name
SONGBIRD_PROXY_ROUTES=capability_name=http://backend:port
```

This auto-registers the capability in the IPC registry and announces
it to mesh peers. Remote gates can `capability.call("capability_name")`
to reach this composition.

### 3. Data Ingestion via Weak Bonds

External data sources enter through drawbridge weak bonds. This is
the ONLY approved path for external data entering the sovereign
interior.

**Ingestion flow**:

```
External API (USGS, NCBI, ArcGIS, etc.)
  → HTTP/HTTPS fetch (weak bond, zero trust)
    → BLAKE3 hash (integrity verification)
      → NestGate CAS store (content-addressed)
        → Loam Certificate mint (provenance attribution)
          → Available as capability across mesh
```

**Requirements**:
- All fetched data MUST be BLAKE3 hashed before storage
- Source attribution MUST be recorded (sweetGrass braid minimum)
- Data MUST land in NestGate CAS, not local filesystem
- Ingestion SHOULD be idempotent (same data = same hash = no duplicate)

### 4. Domain Trust Levels

| Domain | Layer | What Deploys Here |
|--------|-------|-------------------|
| `*.primals.eco` | Intra-membrane (shared ecosystem) | Public compositions, shared data, tools, docs |
| `*.primal.eco` | Inner membrane (personal sovereign) | Private compositions, ceremonies, sovereign data |
| `*.nestgate.io` | Data service point | Federated data gateway, CAS queries, API interactions |

**Rule**: The same composition code can deploy to both domains. The
domain determines the trust level, which determines what data is
accessible and what provenance is required.

### 5. Composition Manifest

Every composition SHOULD have a manifest file declaring its
capabilities, data sources, and primal dependencies:

```toml
[composition]
name = "footPrint"
org = "protoKarya"
subdomain = "footprint.primals.eco"
trust_level = "outer"

[capabilities]
exposed = ["gis.render", "gis.layers", "gis.search"]

[data_sources]
usgs = { type = "weak_bond", url = "https://basemap.nationalmap.gov" }
osm = { type = "weak_bond", url = "https://tile.openstreetmap.org" }

[primals]
required = ["nestGate", "songBird", "petalTongue"]
optional = ["bearDog"]
```

### 6. Security Headers

All compositions served through Caddy MUST import the standard
security headers snippet:

```caddy
(security_headers) {
    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
        -Server
    }
}
```

CSP (Content-Security-Policy) MUST be composition-specific to
allow the external origins the composition needs. Compositions
loading external tiles, scripts, or images (e.g., Esri, OSM) MUST
declare those origins in `img-src`, `script-src`, etc. A missing
CSP allowlist will cause silent failures (blank maps, broken data).

**footPrint CSP example** (tile and data sources):

```caddy
header Content-Security-Policy "default-src 'self'; img-src 'self' https://server.arcgisonline.com https://*.tile.openstreetmap.org https://tiles.arcgis.com; connect-src 'self' https://nominatim.openstreetmap.org https://overpass-api.de https://epqs.nationalmap.gov https://hazards.fema.gov https://sdmdataaccess.sc.egov.usda.gov https://gisagocss.state.mi.us https://gis2.cityofeastlansing.com"
```

---

## Composition Lifecycle

```
1. DESIGN    — Define capabilities, data sources, primal deps
2. DEVELOP   — Build in protoKarya or relevant org
3. REGISTER  — Add Caddy block + drawbridge routes
4. DEPLOY    — Binary to depot, systemd service, mesh announce
5. VALIDATE  — primalSpring scenario confirms capability.call works
6. OPERATE   — Live on *.primals.eco, data flowing, capabilities exposed
7. FEDERATE  — Other compositions consume via capability.call
```

### Adding a Composition (Checklist)

- [ ] Composition code in appropriate org (protoKarya, sporeGarden, etc.)
- [ ] Caddy block in `provision-golgi.sh` with `security_headers`
- [ ] `SONGBIRD_DRAWBRIDGE_ROUTES` and `SONGBIRD_PROXY_ROUTES` configured
- [ ] Data sources documented with ingestion endpoints
- [ ] NestGate CAS wired for content storage (if applicable)
- [ ] primalSpring validation scenario created
- [ ] Security headers verified (`darkforest --scope outer --target subdomain`)
- [ ] Composition manifest TOML created

---

## Deployment Chain

The full path from user to service for `prefix.primals.eco`:

```
User browser
  → DNS: *.primals.eco → golgiBody VPS (Cloudflare wildcard A record)
    → Cloudflare (outer membrane firebreak — DDoS absorber, CDN)
      → Caddy on golgiBody (TLS termination, Host-header routing)
        → reverse_proxy MESH_IP:PORT (over WireGuard to target gate)
          → songBird drawbridge (capability resolution, port solving)
            → Local service (footPrint, esotericWebb, etc.)
```

**songBird's role**: The inner membrane port solver. Drawbridge
listens at `:7780`, maps HTTP paths to capabilities via
`SONGBIRD_DRAWBRIDGE_ROUTES`, resolves capabilities to local
service URLs via `SONGBIRD_PROXY_ROUTES`, and optionally proxies
external "weak bond" APIs through a domain-validated allowlist.

**Production optimization**: For external HTTPS data sources (tiles,
GIS APIs), Caddy handles the proxy directly via imported snippets
from `songBird/infra/caddy/`. This avoids drawbridge overhead for
high-volume tile traffic. Drawbridge handles internal capability
routing and the JSON-RPC bridge.

## Current Compositions (Wave 150c)

| Composition | Subdomain | Gate | Status | Capabilities |
|------------|-----------|------|--------|-------------|
| sporePrint | `sporeprint.primals.eco` | golgiBody | NEEDS MIGRATION (currently on root) | `content.serve` |
| footPrint | `footprint.primals.eco` | sporeGate | DEPLOYED (routing broken) | GIS proxy (10 hosts) |
| esotericWebb | `webb.primals.eco` | flockGate | DEPLOYED (Caddy missing) | `esotericwebb` |
| TOPO-VIS | `live.primals.eco` | sporeGate | LIVE | `topo.visualize` |
| JupyterHub | `lab.primals.eco` | ironGate | LIVE | `jupyter` |
| Forgejo | `git.primals.eco` | golgiBody | LIVE | `forge.serve` |
| Nest Atomic | `membrane.primals.eco` | golgiBody | LIVE | Tower + Nest services |
| tideGlass | `tideglass.primals.eco` | — | PLANNED | GPS reversal screening |
| helixVision | `helix.primals.eco` | — | PLANNED | Expression analysis |

---

## References

- `../operations/GATEHOUSE_DARKFOREST_STANDARD.md` — Bond escalation, drawbridge spec
- `../foundations/DIDERM_DOMAIN_ARCHITECTURE.md` — Domain trust levels, membrane layers
- `../GLOSSARY.md` — Drawbridge, weak bonds, Loam Certificates
- `whitePaper/gen5/foundations/COMPOSITION_ROUTING_PATTERN.md` — Full pattern documentation
- `whitePaper/gen5/foundations/EXTERNAL_SOVEREIGNTY_PATTERN.md` — Collaborator gate routing
- `provision/provision-golgi.sh` — Caddy configuration source of truth

---

## Changelog

| Wave | Change |
|------|--------|
| 138a | Initial: formalized composition routing standard from ad-hoc footPrint and JupyterHub deployments. Wildcard DNS, drawbridge registration, data ingestion via weak bonds, trust levels by domain. |
| 150c | Subdomain standard enforced: `prefix.primals.eco` is REQUIRED. Path-based routing prohibited for new compositions. footPrint corrected to `footprint.primals.eco`. esotericWebb changed from `/webb/` path to `webb.primals.eco` subdomain. CSP requirements strengthened. Deployment chain and songBird role documented. |
| 150d | Root domain redirect: `primals.eco` → `sporeprint.primals.eco`. sporePrint gets own subdomain. Domain terminology refined: `primals.eco` = intra-membrane, `primal.eco` = inner membrane, `nestgate.io` = data service point. |
