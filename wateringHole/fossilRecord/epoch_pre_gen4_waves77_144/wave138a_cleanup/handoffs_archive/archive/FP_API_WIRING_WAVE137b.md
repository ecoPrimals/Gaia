# FP-API Wiring — Wave 137b

**Date**: Jul 13, 2026 | **Owner**: flockGate + songBird | **Status**: SUPERSEDED by DRAWBRIDGE_WEAK_BOND_PATTERN_AAR_137b.md

> **Note**: The CSP-expansion approach below is superseded. The correct pattern is drawbridge weak bonds — see `DRAWBRIDGE_WEAK_BOND_PATTERN_AAR_137b.md`. The SPA should never fetch directly from external services.

---

## Problem

footPrint's GIS proxy (`/api/proxy?url=<target>`) runs in Express during dev. In production (`primals.eco/footprint/`), the SPA is static — no Node.js server runs. The 10 external GIS services need to be reachable from the browser.

## Current State

### Caddy Config (golgi, provision-golgi.sh line 173)

```caddy
handle_path /footprint/* {
    root * /opt/ecoPrimals/compositions/footprint/dist/client
    header Content-Security-Policy "default-src 'self'; script-src ... ; connect-src 'self' https://*.openstreetmap.org https://hazards.fema.gov https://epqs.nationalmap.gov https://*.arcgis.com; ..."
    try_files {path} /index.html
    file_server
}
```

### CSP Gap

Current `connect-src` allows 4 of 10 hosts. Missing 6:

| Host | In CSP? | CORS? |
|------|---------|-------|
| overpass-api.de | NO | YES (sends `Access-Control-Allow-Origin: *`) |
| hazards.fema.gov | YES | Partial (CORS on REST endpoints) |
| nominatim.openstreetmap.org | YES (via wildcard) | YES |
| epqs.nationalmap.gov | YES | YES |
| sdmdataaccess.sc.egov.usda.gov | NO | NO (WMS, no CORS) |
| gisagocss.state.mi.us | NO | Unlikely (state GIS) |
| gisp.mcgi.state.mi.us | NO | Unlikely (state GIS) |
| gis2.cityofeastlansing.com | NO | Unlikely (municipal) |
| services1.arcgis.com | YES (via wildcard) | YES |
| services2.arcgis.com | YES (via wildcard) | YES |

**6 hosts with CORS** → SPA can fetch directly (no proxy needed)
**4 hosts without CORS** → proxy required (state/municipal GIS services)

---

## Resolution: Two-Phase Approach

### Phase A — CSP Expansion + Direct Fetch (IMMEDIATE)

Expand CSP to allow all 10 hosts. The SPA client fetches directly from services that support CORS. This handles 6/10 hosts immediately.

**Caddy config change** (golgi, replace footPrint `connect-src`):

```caddy
header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.tile.openstreetmap.org https://*.arcgis.com; font-src 'self'; connect-src 'self' https://*.openstreetmap.org https://overpass-api.de https://hazards.fema.gov https://epqs.nationalmap.gov https://*.arcgis.com https://sdmdataaccess.sc.egov.usda.gov https://gisagocss.state.mi.us https://gisp.mcgi.state.mi.us https://gis2.cityofeastlansing.com; frame-ancestors 'none'"
```

**Client-side change** (footPrint SPA): For CORS-enabled services, call directly without going through `/api/proxy`. Add a `canFetchDirect(url)` check:

```typescript
const CORS_HOSTS = [
  'overpass-api.de',
  'nominatim.openstreetmap.org',
  'epqs.nationalmap.gov',
  'services1.arcgis.com',
  'services2.arcgis.com',
  'hazards.fema.gov',
];

function canFetchDirect(url: string): boolean {
  const parsed = new URL(url);
  return CORS_HOSTS.some(h => parsed.hostname.endsWith(h));
}
```

### Phase B — songBird Drawbridge Proxy (after SOCKET-DIR-UNIFY)

For the 4 non-CORS hosts (state/municipal GIS), route through songBird's `http.request`:

**Caddy addition** (insert BEFORE the static file handler):

```caddy
handle_path /footprint/api/proxy {
    reverse_proxy 10.13.37.2:7780 {
        header_up Host {host}
        header_up X-Forwarded-For {remote_host}
        header_up X-FP-Target-URL {query.url}
    }
}
```

**songBird drawbridge route**: A new route handler that:
1. Reads `X-FP-Target-URL` header
2. Validates against the 10-host allowlist
3. Calls `http.request` internally
4. Returns the response

**Prerequisite**: SOCKET-DIR-UNIFY must resolve first — songBird needs TLS delegation to work for HTTPS targets. Current error: `Failed to connect to security provider at /var/run/biomeos/neural-api.sock`.

---

## Effort Estimate

| Phase | What | Effort | Blocks on |
|-------|------|--------|-----------|
| A | CSP expand + client direct-fetch | 1-2hr | Nothing (ship now) |
| B | songBird drawbridge proxy | 2-4hr | SOCKET-DIR-UNIFY |

## Validation

`s_fp_api_proxy` scenario (#142) already validates:
- Allowlist alignment (10/10 hosts)
- Proxy route structure (GET+POST)
- Cache strategy (SHA-256 keys, TTL per domain)
- songBird `http.request` availability

**New check needed** (Phase B): Add TLS delegation probe to live phase.

---

## Deployment Sequence

```
1. Phase A: Update Caddy CSP on golgi                    ← golgi team
2. Phase A: Patch footPrint client with canFetchDirect() ← flockGate
3. Phase A: Deploy SPA to golgi                          ← sporeGate
4. Verify: 6 CORS hosts fetch directly from NYC          ← flockGate WAN
5. Phase B: SOCKET-DIR-UNIFY resolves                    ← biomeOS
6. Phase B: songBird drawbridge proxy handler            ← songBird
7. Phase B: Caddy route for /footprint/api/proxy         ← golgi team
8. Verify: 4 non-CORS hosts proxy through drawbridge     ← flockGate WAN
```

---

*FP-API: 60% of GIS services work with direct fetch (CSP expansion). Remaining 40% need songBird HTTPS proxy (blocked on SOCKET-DIR-UNIFY). Phase A is shippable immediately.*
