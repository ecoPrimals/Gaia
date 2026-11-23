# AAR: flockGate WAN Overwatch — Wave 137a

**Date**: 2026-07-12 14:50 EDT  
**Author**: flockGate overwatch  
**Wave**: 137a  
**Gate**: flockGate (NYC, WAN mesh endpoint)

---

## Executive Summary

Wave 137a sync and WAN validation from flockGate. primalSpring at v0.9.36 parity (136 scenarios, 1,106 tests, 0 failures). FP-DEPLOY confirmed LIVE from WAN. Deep mesh probe refined: 3-cause topology gap fully characterized. New scenario `s_federation_wan_readiness` landed. footPrint API surface mapped for FP-API Phase 2 work.

---

## 1. Deliverables

| Item | SHA | Status |
|------|-----|--------|
| primalSpring sync | `5b424f7` | GREEN — 136 scenarios, 1,106 tests, 0 fail |
| s_federation_wan_readiness (#133→#136 after rebase) | `a2f1950` | Landed upstream, complementary to `s_mesh_federation_readiness` |
| s_cascade_provenance_match fix | `fb03030` | Merged upstream — checksums parser handles nested arch tables |
| heads/flockGate.toml | `8b46c91c` | Pushed — v0.9.36 parity + FP-DEPLOY confirmed |
| AAR update (136b) | `2bd7e5e9` | Pushed — 3-cause analysis, HTTP workaround proven |

---

## 2. FP-DEPLOY WAN Confirmation

First live composition on sovereign infrastructure, confirmed from WAN (NYC → Cloudflare → golgi):

| Metric | Value |
|--------|-------|
| URL | `https://primals.eco/footprint/` |
| Status | 200 OK |
| Size | 4,154 bytes |
| Latency | 114ms (NYC → golgi) |
| CSP | Custom: `self` + OSM tiles + FEMA + USGS + ArcGIS allowlist |
| X-Frame-Options | DENY |
| Server | Caddy (via Cloudflare H2) |

The CSP correctly allows connect-src to the GIS services the SPA needs while denying everything else. This is proper composition-specific hardening beyond the default sporePrint CSP.

---

## 3. Mesh Topology — Full Characterization

### 3.1 Federation Port Reachability (from flockGate)

| Peer | Address | Port 7700 | Protocol | Status |
|------|---------|-----------|----------|--------|
| golgi | 10.13.37.1 | TCP | — | **UNREACHABLE** (bound to public IP [RELAY_PUBLIC] only) |
| sporeGate | 10.13.37.2 | HTTP `/jsonrpc` | JSON-RPC 2.0 | **REACHABLE** (3 peers, v0.2.1) |
| eastGate | 10.13.37.5 | HTTP `/jsonrpc` | JSON-RPC 2.0 | **REACHABLE** (1 peer: golgi) |
| ironGate | 10.13.37.7 | TCP | — | **UNREACHABLE** (no listener) |

### 3.2 sporeGate Mesh State (observed via HTTP)

```json
{
  "online": 3,
  "peers": [
    {"address": "[RELAY_PUBLIC]:7700", "node_id": "peer-[RELAY_PUBLIC]", "reachable": true},
    {"address": "192.168.4.237:7700", "node_id": "peer-192.168.4.237", "reachable": true},
    {"address": "10.13.37.0:8080", "node_id": "wg-A2fvz3cz", "reachable": true}
  ]
}
```

sporeGate's mesh is live with golgi (public IP), eastGate (LAN), and a WG drawbridge peer.

### 3.3 Three Compound Blockers

| # | Blocker | Detail | Owner |
|---|---------|--------|-------|
| 1 | **golgi WG bind** | songBird federation on golgi listens on [RELAY_PUBLIC]:7700 but NOT 10.13.37.1:7700. flockGate's WG overlay routes to 10.13.37.x — so golgi is unreachable as a federation endpoint from WAN gates. | golgi/sporeGate |
| 2 | **UDS ↔ HTTP protocol mismatch** | flockGate's local songBird (UDS socket) calls `peer.connect` → TCP connects at 70ms, state="connected" — but `mesh.peers` remains empty. The remote federation serves HTTP JSON-RPC at `/jsonrpc`; the UDS mesh engine expects a different wire protocol for peer registration. | songBird team |
| 3 | **Missing DRAWBRIDGE_ROUTES** | `discover_capabilities` on sporeGate returns only songBird built-ins (http.*, relay.*, mesh.*, crypto.*). No `jupyter` capability advertised. `capability.call("jupyter")` fails with "No local or remote provider". | sporeGate |

### 3.4 Capability Call Failure Chain

```
flockGate UDS: capability.call("jupyter")
  → "No local provider for 'jupyter' and no reachable mesh peers for remote dispatch"
  → Root cause: 0 peers in UDS mesh engine (blocker #2)

sporeGate HTTP: capability.call("jupyter")  
  → "No local or remote provider found for capability 'jupyter' (tried 3 mesh peers via TCP and TURN relay; last error: HTTP request to http://10.13.37.0:8080/jsonrpc failed: client error (Connect))"
  → Root cause: jupyter not advertised (blocker #3), ironGate not in peer list
```

### 3.5 Proven Workaround

Direct HTTP JSON-RPC to sporeGate's federation works from flockGate:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"mesh.peers","id":1}' \
  http://10.13.37.2:7700/jsonrpc
```

This bypasses the local UDS mesh engine entirely. Latency: ~220ms.

---

## 4. Outer Membrane Posture (from WAN)

| Endpoint | Status | Latency | Notes |
|----------|--------|---------|-------|
| `primals.eco/footprint/` | 200 | 114ms | FP-DEPLOY live, custom CSP |
| `membrane.primals.eco/depot/` | 200 | 184ms | Pepti depot healthy |
| `lab.primals.eco/` | 401 | 153ms | basicauth EXP-06 confirmed |
| `primals.eco/index.html` | 200 | 126ms | sporePrint serving |
| WireGuard → golgi ICMP | 0% loss | 31ms | Overlay healthy |

All security headers present where expected (CSP, X-Frame-Options DENY).

---

## 5. Latency Baseline

| Path | p50 | Method |
|------|-----|--------|
| flockGate → primals.eco (HTTPS via CF) | 126ms | curl |
| flockGate → membrane.primals.eco (HTTPS via CF) | 184ms | curl |
| flockGate → primals.eco/footprint/ (HTTPS) | 114ms | curl |
| flockGate → golgi WG ICMP | 31ms | ping -c3 |
| flockGate → sporeGate federation HTTP | 220ms | curl JSON-RPC |
| flockGate → sporeGate peer.connect TCP | 70ms | songBird UDS |

---

## 6. footPrint API Surface Mapping (FP-API Preparation)

The Express server (to be absorbed by primals) has these endpoints:

| Endpoint | Method | Primal Target | Notes |
|----------|--------|---------------|-------|
| `/api/proxy?url=<target>` | GET | songBird drawbridge | 10-host allowlist (OSM, FEMA, USGS, ArcGIS, Nominatim, NRCS, MI GIS). Caching (1-90 day TTLs). Drawbridge has allowlist landed (`87b7779`). |
| `/api/proxy?url=<target>` | POST | songBird drawbridge | Same as above, for Overpass API queries (POST body). |
| `/api/projects` | GET | nestGate CAS | List all projects |
| `/api/projects/:name` | GET/POST/DELETE | nestGate CAS | CRUD for project data (JSON). Replace with content-addressed, rootPulse-traced persistence. |
| `/api/cache` | DELETE | local (optional) | Clear proxy cache — may become irrelevant with drawbridge caching |
| `/api/agent/status` | GET | primal health | Returns `{ agent: "none" }` — maps to `health.liveness` |

### Alignment Gap

footPrint client uses **query-parameter** style: `GET /api/proxy?url=https://hazards.fema.gov/...`

songBird drawbridge uses **path-based** routing: `/hazards.fema.gov/gis/nfhl/rest/...`

Resolution options:
1. **Client-side**: Update footPrint client to use drawbridge path format
2. **Drawbridge-side**: songBird adds `?url=` query-param adapter
3. **Caddy rewrite**: `rewrite /api/proxy?url={uri.query.url} /drawbridge/{uri.query.url}`

Option 1 is cleanest (no runtime translation). Option 3 is fastest to deploy.

---

## 7. primalSpring Evolution

| Scenario | SHA | What It Validates |
|----------|-----|-------------------|
| `s_federation_wan_readiness` | `a2f1950` | Live TCP probe to port 7700 on all WAN peers — catches topology gaps |
| `s_cascade_provenance_match` fix | `fb03030` | Fixed checksums parser (nested arch-keyed TOML tables) |

Both merged upstream. Additionally, upstream landed:
- `s_mesh_federation_readiness` — structural prerequisites for federation
- `s_live_composition_deploy` — FP-DEPLOY SPA readiness + drawbridge alignment
- `s_pure_rust_crypto_audit` — ecosystem-wide pure Rust crypto compliance

Suite: 136 scenarios, 1,106 tests, 0 failures. Env requires `ECOPRIMALS_ROOT` + `ECOPRIMALS_PLASMID_BIN` for full depot validation.

---

## 8. Open Items (flockGate ownership)

| ID | Item | Status | Next |
|----|------|--------|------|
| FLOCKGATE-MESH | 0 UDS mesh peers | **BLOCKED** | Awaiting golgi WG bind + songBird protocol fix |
| FP-API | Wire Express proxy to drawbridge | **PENDING** | Phase 2 — map `?url=` to path-based routing |
| FP-PERSIST | Wire Express CRUD to nestGate CAS | **PENDING** | Phase 2 — nestGate team owns implementation |
| FP-PARITY | petalTongue visual parity | **TRACKING** | 12 VT areas defined, petalTongue team owns |

---

## 9. Recommendations for Upstream

1. **FLOCKGATE-MESH**: The golgi WG bind is trivial (`--bind-address 0.0.0.0` or add `10.13.37.1` to listen addresses). The UDS ↔ HTTP protocol gap is architectural — may need a `mesh.add_peer` RPC that accepts HTTP federation endpoints, or the songBird binary needs a flag to use HTTP federation client mode.

2. **FP-API alignment**: Recommend Caddy rewrite as Phase 1 quickfix, then client-side migration to drawbridge paths. The 10-host allowlist is already in songBird (`87b7779`).

3. **Neural API + mesh**: Once NAPI-START and NAPI-PERMS are resolved on sporeGate, the `capability.call` routing through Neural API should subsume the current songBird-only dispatch. This may make the UDS/HTTP protocol mismatch less critical (Neural API uses its own routing layer).

---

## Summary

flockGate is at full 137a parity. FP-DEPLOY confirmed live from WAN — first composition on sovereign infrastructure. Mesh topology fully mapped with proven HTTP workaround. Three compound blockers documented for capability.call (golgi bind, protocol mismatch, missing routes). footPrint API surface mapped for Phase 2 absorption. No action required from flockGate until upstream resolves mesh infra items.

**Next probe trigger**: NAPI-START resolution OR golgi 7700 bind fix notification.
