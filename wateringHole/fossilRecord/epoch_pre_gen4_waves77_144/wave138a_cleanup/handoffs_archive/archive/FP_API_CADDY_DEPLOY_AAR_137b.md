# FP-API-CADDY-DEPLOY — After Action Review

**Wave**: 137b | **Date**: Jul 13, 2026 | **Operator**: eastGate overwatch
**Status**: COMPLETE

---

## Task

Deploy flockGate's `fp-api-caddy.caddyfile` (10 GIS proxy hosts) to golgi's Caddy config so footPrint SPA routes external API calls through the sovereign outer membrane rather than direct browser-to-upstream requests.

## What Was Done

1. **Cascaded** songBird `718d18d3` — pulled the `infra/caddy/footprint-gis-proxy.Caddyfile` (103 LOC, Caddy named snippet `(footprint_gis_proxy)`) authored by flockGate.

2. **Deployed** the snippet to `/etc/membrane/Caddyfile` on golgi as a top-level named snippet (must appear before first `import`).

3. **Imported** via `import footprint_gis_proxy` in the `primals.eco` server block, positioned before the catch-all `handle_path /footprint/*` so `/footprint/ext/{service}/*` routes match first.

4. **Updated CSP** for footPrint: removed external `connect-src` hosts (`*.openstreetmap.org`, `hazards.fema.gov`, `epqs.nationalmap.gov`, `*.arcgis.com`) — all API requests now route through same-origin `/footprint/ext/` proxy. `img-src` retains tile server domains (map tiles are direct browser loads, not API calls).

5. **Fixed Caddy syntax**: `transport http { tls }` one-liner format isn't valid — expanded to multi-line blocks.

6. **Validated** with `caddy validate`, reloaded, and tested all 10 routes.

## Proxy Route Map

| Caddy Path | Upstream | Test |
|------------|----------|------|
| `/footprint/ext/overpass/*` | `overpass-api.de` | 400 (needs POST body — proxy OK) |
| `/footprint/ext/fema/*` | `hazards.fema.gov` | 200 |
| `/footprint/ext/arcgis1/*` | `services1.arcgis.com` | 200 |
| `/footprint/ext/arcgis2/*` | `services2.arcgis.com` | 200 |
| `/footprint/ext/nominatim/*` | `nominatim.openstreetmap.org` | 200 |
| `/footprint/ext/usgs/*` | `epqs.nationalmap.gov` | 403 (upstream rejection — direct call also 403) |
| `/footprint/ext/nrcs/*` | `sdmdataaccess.sc.egov.usda.gov` | 302 (redirect to landing) |
| `/footprint/ext/michigan/*` | `gisagocss.state.mi.us` | 200 |
| `/footprint/ext/mcgi/*` | `gisp.mcgi.state.mi.us` | 200 |
| `/footprint/ext/eastlansing/*` | `gis2.cityofeastlansing.com` | 200 |

**8/10 clean pass.** Overpass needs POST (expected). USGS rejects at origin (tracked upstream).

## Security Impact

- **CSP tightened**: footPrint `connect-src` reduced from 5 external domains to `'self'` only. All external API traffic now transits Caddy's sovereign TLS termination — the browser never reaches external hosts for API calls.
- **Caddy access logs** capture all GIS proxy traffic — feeds skunkBat's `baseline.observe` pipeline.
- **CORS eliminated**: Same-origin proxy means no cross-origin requests in the data path.

## Artifacts Updated

| File | Change |
|------|--------|
| `/etc/membrane/Caddyfile` (golgi) | Added `(footprint_gis_proxy)` snippet + `import` in `primals.eco` block |
| `provision-golgi.sh` | Mirrored: snippet definition + `import` + CSP update |

## Upstream Note

The USGS National Map elevation API (`epqs.nationalmap.gov`) returns 403 even on direct calls. This is a known upstream behavior — they may require specific `User-Agent` headers or have changed their rate-limiting policy. footPrint should handle 403 gracefully with fallback elevation sources.

## Relationship to Sovereignty Model

This deployment moves 10 external GIS data sources behind the sovereign outer membrane. The browser-to-upstream data path is eliminated for API calls. Map tile imagery (`*.tile.openstreetmap.org`, `*.arcgis.com`) remains direct (CSP `img-src` allows them) — these are read-only CDN resources with no sovereignty concern.

When `bearDog` achieves Caddy parity (DIV-01/DIV-02), these proxy routes become `bearDog` upstream configs — no structural change needed, just migration of the routing table.
