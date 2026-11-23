# flockGate WAN Overwatch AAR — Wave 137b

**Date**: Jul 13, 2026 | **Gate**: flockGate (NYC) | **Wave**: 137b
**Author**: flockGate overwatch agent | **Classification**: Technical AAR

---

## Executive Summary

**JupyterHub data plane PROVEN end-to-end from WAN.** First successful cross-gate compute access: flockGate (NYC) → WireGuard overlay → sporeGate (MI) → LAN → ironGate JupyterHub v5.4.5. Total RTT: 202ms.

Created `s_fp_api_proxy` validation scenario (#142, 13 checks, all PASS) for footPrint API drawbridge wiring. Identified three remaining blockers for full `capability.call` control plane. primalSpring at 142 scenarios / 1,176 tests / 0 failures / 0 clippy.

---

## 1. Successes

### 1.1 JupyterHub Data Plane — PROVEN

The relay chain works:

```
flockGate (10.13.37.6)
  → WG overlay (62ms)
    → sporeGate (10.13.37.2:7700/jsonrpc)
      → http.request → ironGate (192.168.4.237:8000)
        → JupyterHub v5.4.5 responds: {"version":"5.4.5"}
```

- **Method**: HTTP JSON-RPC `http.request` on sporeGate's federation endpoint
- **Auth**: JupyterHub returns 403 on `/hub/api/users` (credentials required) — confirms auth layer active
- **Latency**: 202ms total WAN RTT (62ms WG hop + 1ms LAN + processing)
- **Significance**: First proof that WAN clients can reach LAN compute services through the sovereign mesh without exposing internal services to the internet

### 1.2 GOLGI-WG-BIND — Confirmed Resolved

golgi now responds on WireGuard address `10.13.37.1:7700`:
- node_id: `membrane-relay`
- 4 overlay peers visible
- version: 0.2.1
- Latency from flockGate: 29ms (WG RTT)

This was a 5-day blocker. Resolved by binding songBird to `0.0.0.0:7700` instead of only the public interface.

### 1.3 FP-API Scenario — s_fp_api_proxy (#142)

New validation scenario validates the footPrint GIS proxy wiring architecture:

| Check | Result |
|-------|--------|
| fpapi:allowlist_count | PASS — 10/10 hosts aligned |
| fpapi:proxy_path_defined | PASS — `/api/proxy` |
| fpapi:user_agent_defined | PASS — `FootPrint-HomePlanner/2.0` |
| fpapi:express_deprecated | PASS — manifest confirms SPA-only |
| fpapi:server_allowlist_validation | PASS — `isHostAllowed()` |
| fpapi:server_cache_layer | PASS — disk cache with TTLs |
| fpapi:post_proxy_support | PASS — Overpass POST body |
| fpapi:manifest_drawbridge_ref | PASS — drawbridge referenced |
| fpapi:cache_ttls_defined | PASS — 4/4 TTL domains |
| fpapi:cache_key_sha256 | PASS — content-addressable |
| fpapi:live:sporegate_reachable | PASS — TCP to 10.13.37.2:7700 |
| fpapi:live:http_request_method | PASS — method in rpc.discover |
| fpapi:live:capability_call_method | PASS — method available |

### 1.4 Local Environment Fully Configured

- `GATE_NAME=flockGate` persisted in `.bashrc`
- `ECOPRIMALS_ROOT` set — 13/13 depot binaries resolve via `discover_binary`
- `ECOPRIMALS_PLASMID_BIN` pointed to triple-specific directory
- All primalSpring tests pass without env-related false positives

### 1.5 primalSpring Evolution

| Metric | Previous | Current |
|--------|----------|---------|
| HEAD | `445826b` | `62a7ad7` |
| Scenarios | 141 | 142 (+1 FP-API) |
| Tests | 1,135 | 1,176 (+41) |
| Failures | 0 | 0 |
| Clippy | 0 | 0 |

---

## 2. Path to Full WAN `capability.call`

The data plane is proven. The control plane (`capability.call`) needs three things:

### 2.1 Blocker: Depot Binary Pre-Fix

**Status**: BLOCKED — waiting for depot rebuild

The pepti depot songBird binary (last-modified Jul 9) does not contain the `0d2895b5` UDS-HTTP fix. Evidence:
- `peer.connect` TCP-connects to sporeGate at 62ms
- `mesh.peers` stays at 0 after connect
- sporeGate's `mesh.peers` shows 3 peers — flockGate is NOT among them
- The fix makes peers register in BeaconMesh after HTTP federation handshake

**Resolution**: Rebuild songBird with `0d2895b5` and publish to `membrane.primals.eco/depot/`. Once deployed locally, flockGate will appear in sporeGate/golgi's peer lists.

### 2.2 Blocker: DRAWBRIDGE-ROUTES Not Advertising

**Status**: BLOCKED — `jupyter` not in capabilities.list

Despite the blurb marking DRAWBRIDGE-ROUTES as resolved, sporeGate's songBird only shows 15 native capabilities:
```
bluetooth.pair, crypto.delegate, ipc.jsonrpc, ipc.tarpc,
network.btsp, network.discovery, network.federation, network.igd,
network.onion, network.quic, network.relay, network.stun,
network.tls, network.tor, nfc.genesis
```

No `jupyter`, no drawbridge-advertised capabilities. HTTP GET to `/hub` returns 404. The `SONGBIRD_DRAWBRIDGE_ROUTES` env var may be set, but capabilities aren't being advertised through `capabilities.list`.

**Impact**: Even with mesh peering fixed, `capability.call jupyter` will fail because no provider advertises `jupyter`.

**Resolution**: Verify `SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter` in songBird systemd unit on sporeGate. If set, investigate why capabilities aren't advertised. May need songBird code fix to register drawbridge routes as capabilities.

### 2.3 Blocker: Stale Peer Ghost

sporeGate's peer list contains a ghost entry: `10.13.37.0:8080` (node_id: `wg-A2fvz3cz`). This is from before the port 8080→7700 fix. `capability.call` wastes time trying to connect to this dead peer.

**Resolution**: `mesh.remove_peer` or songBird restart with clean state on sporeGate.

### 2.4 Resolution Sequence

```
1. Rebuild songBird → depot (includes 0d2895b5)
2. flockGate deploys new binary → mesh.peers > 0
3. Verify DRAWBRIDGE-ROUTES advertises jupyter
4. Clean stale 10.13.37.0:8080 peer from sporeGate
5. capability.call jupyter → SUCCESS
6. WAN-DISPATCH-01 = FULL PASS
```

---

## 3. FP-API Architecture Analysis

### Current State

footPrint's `/api/proxy?url=<target>` runs in Express (dev mode). In production (`primals.eco/footprint/`), the SPA is static — no Node.js server runs.

### TLS Delegation Blocker

songBird's `http.request` fails on all HTTPS URLs:
```
Security provider RPC error: Failed to connect to security provider
at /var/run/biomeos/neural-api.sock: No such file or directory
```

songBird delegates TLS to bearDog via a socket. The socket path is hardcoded to `/var/run/biomeos/neural-api.sock` but on sporeGate the actual socket is at `/run/membrane/neural-api.sock` (SOCKET-DIR-UNIFY gap).

### Resolution Options

| Option | Approach | Effort | Clean? |
|--------|----------|--------|--------|
| A | **Caddy rewrite** — Caddy handles TLS natively, add route for `/footprint/api/proxy` | 2hr | Quickfix |
| B | **SOCKET-DIR-UNIFY** — fix socket path symlinks, songBird http.request works for HTTPS | 2-4hr | Clean |
| C | **Client-side fetch** — SPA calls GIS services directly (CORS-limited) | 4hr | Partial |

**Recommendation**: Option A (Caddy rewrite) as quickfix for immediate FP-API, then Option B lands naturally with SOCKET-DIR-UNIFY debt resolution.

### GIS Service Allowlist (10 hosts)

| Host | Service | Protocol |
|------|---------|----------|
| overpass-api.de | OSM Overpass | HTTPS (POST) |
| hazards.fema.gov | FEMA NFHL flood | HTTPS |
| nominatim.openstreetmap.org | Geocoding | HTTPS |
| epqs.nationalmap.gov | USGS elevation | HTTPS |
| sdmdataaccess.sc.egov.usda.gov | NRCS soils | HTTPS |
| gisagocss.state.mi.us | MI framework | HTTPS |
| gisp.mcgi.state.mi.us | MI GIS portal | HTTPS |
| gis2.cityofeastlansing.com | Zoning | HTTPS |
| services1.arcgis.com | ArcGIS | HTTPS |
| services2.arcgis.com | ArcGIS | HTTPS |

All 10 require HTTPS — confirms Option A (Caddy) is the only immediate path.

---

## 4. Mesh Topology (As Observed from flockGate)

```
                    ┌─────────────────────────────────────┐
                    │  sporeGate (10.13.37.2)             │
                    │  node_id: sporeGate                 │
                    │  3 peers (LAN+public+stale WG)      │
                    │  songBird: v0.2.1, HTTP federation   │
                    │  Neural API: 48 primals             │
         62ms WG    │  HTTPS: BLOCKED (socket path)       │
    flockGate ──────┤                                     │
    (10.13.37.6)    └───────────────┬─────────────────────┘
         │                          │ LAN 1ms
         │                          ▼
         │               ┌─────────────────────┐
         │               │ ironGate (LAN)       │
         │               │ JupyterHub v5.4.5    │
         │               │ port 8000            │
         │               └─────────────────────┘
         │
         │  29ms WG
         └──────────┬─────────────────────────────┐
                    │  golgi (10.13.37.1)          │
                    │  node_id: membrane-relay      │
                    │  4 overlay peers              │
                    │  songBird: v0.2.1             │
                    │  WG-BIND: RESOLVED            │
                    └──────────────────────────────┘
```

---

## 5. Remaining Work (flockGate Perspective)

### Blocked on Upstream

| ID | What | Owner | Blocking |
|----|------|-------|----------|
| DEPOT-REBUILD | Rebuild songBird with 0d2895b5, publish to depot | songBird/pepti | Mesh peering |
| DRAWBRIDGE-CAP | Investigate why drawbridge routes don't appear in capabilities.list | songBird | capability.call |
| STALE-PEER | Remove 10.13.37.0:8080 ghost from sporeGate | sporeGate | capability.call perf |
| SOCKET-DIR-UNIFY | Fix TLS delegation path | biomeOS | songBird HTTPS |

### flockGate Can Action

| ID | What | Effort |
|----|------|--------|
| FP-API-CADDY | Draft Caddy config snippet for GIS proxy route | 1hr |
| SCENARIO-TLS | Add TLS delegation check to s_fp_api_proxy (live phase) | 30min |
| DEPOT-REDEPLOY | Deploy new songBird immediately when depot updates | 15min |

### Validation Readiness

Once DEPOT-REBUILD lands:
1. Deploy binary (15min)
2. `mesh.init` + `peer.connect` → verify `mesh.peers > 0`
3. If DRAWBRIDGE-CAP resolved: `capability.call jupyter` → PASS
4. Mark WAN-DISPATCH-01 = FULL PASS
5. Update primalSpring scenario `s_wan_dispatch_validation` with E2E proof

---

## 6. Metrics

| Measurement | Value | Method |
|-------------|-------|--------|
| WG overlay RTT (golgi) | 31ms | ICMP |
| WG overlay RTT (sporeGate) | 62ms | TCP connect |
| WG overlay RTT (golgi, federation) | 87ms | HTTP JSON-RPC |
| WG overlay RTT (sporeGate, federation) | 207ms | HTTP JSON-RPC |
| JupyterHub relay RTT | 202ms | http.request via sporeGate |
| primals.eco WAN RTT | 114ms | HTTPS from NYC |
| songBird uptime | ~10hr | mesh.status |
| Depot binaries resolving | 13/13 | discover_binary |

---

## 7. Recommendations for Upstream

1. **Priority: Depot rebuild** — The `0d2895b5` fix is committed but not published. Every gate running the old binary is excluded from BeaconMesh. This blocks the entire "bidirectional mesh" claim.

2. **Clarify DRAWBRIDGE-ROUTES status** — The blurb marks it as "confirmed operational" but evidence from the federation endpoint shows no drawbridge capabilities. Either the env var isn't being read, or drawbridge routes don't register as capabilities (design gap).

3. **Clean stale peers** — sporeGate's `10.13.37.0:8080` entry pre-dates the port fix. It causes `capability.call` to waste time on unreachable peers.

4. **FP-API: Caddy path is fastest** — songBird can't do HTTPS until SOCKET-DIR-UNIFY. A 10-line Caddy snippet would make footPrint GIS proxy live today.

---

*Wave 137b: Data plane proven. Control plane blocked on depot rebuild + drawbridge capability advertising. 142 scenarios, 1,176 tests, 0 failures. Full E2E path clear — 3 upstream items gate final validation.*
