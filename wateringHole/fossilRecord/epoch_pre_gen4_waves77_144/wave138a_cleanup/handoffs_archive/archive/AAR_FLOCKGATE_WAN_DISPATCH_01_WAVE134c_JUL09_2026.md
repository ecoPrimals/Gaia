# AAR: WAN-DISPATCH-01 Validation — Wave 134c

**Date**: 2026-07-09 13:06 UTC | **Gate**: flockGate | **Wave**: 134c
**Classification**: WAN mesh validation — cross-gate HTTP dispatch through drawbridge

---

## Executive Summary

WAN-DISPATCH-01 is **PASS at the transport layer**. The full chain
`flockGate → WireGuard → sporeGate songBird drawbridge → ironGate JupyterHub`
returns `{"version": "5.4.5"}` consistently (10/10 HTTP 200, p50=142ms).

Two protocol-layer gaps remain:
1. `capability.call("jupyter")` — no provider advertised (sporeGate env config needed)
2. songBird `http.request` — path-handling bug at drawbridge (404 vs curl's 200)

---

## Findings

### P1: HTTP Data Path — PROVEN

| Metric | Value |
|--------|-------|
| Success rate | 10/10 (100%) |
| Response body | `{"version": "5.4.5"}` |
| HTTP status | 200 |
| p50 RTT | 142ms |
| p95 RTT | 152ms |
| p99 RTT | 152ms |
| min/max | 136ms / 152ms |
| ICMP baseline | 69ms (single WG hop) |
| Explanation | HTTP RTT ≈ 2x ICMP (TCP handshake + HTTP request/response = 2 round trips) |

**Golgi relay path** (lab.primals.eco → Caddy → sporeGate → ironGate):
- p50: 207ms | cold (TLS handshake): 266ms | warm: ~200ms

### P2: capability.call Protocol — FAIL (Configuration Gap)

```
Request:  {"method":"capability.call","params":{"capability":"jupyter","operation":"GET /hub/api"}}
Response: {"error":{"code":-32603,"message":"No local or remote provider found for capability 'jupyter'"}}
```

**Root cause**: sporeGate's songBird is not running with `SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter`.
The drawbridge IS routing HTTP correctly (curl to :7780/hub/api → 200), but the capability
auto-advertisement feature (committed in e5941eeb) requires the env var to trigger
`announce_drawbridge_capabilities()` at startup.

**Fix**: Add to sporeGate's songBird systemd unit or environment:
```
Environment=SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter
```
Then restart songBird. The mesh peers will receive `mesh.capabilities_announce` and
`capability.call("jupyter")` will route correctly.

### P3: songBird http.request — Path-Handling Bug (Minor)

| Client | URL | Result |
|--------|-----|--------|
| `curl` (direct TCP) | `http://10.13.37.2:7780/hub/api` | HTTP 200, `{"version":"5.4.5"}` |
| songBird `http.request` (same URL, same headers) | `http://10.13.37.2:7780/hub/api` | HTTP 404, JupyterHub HTML page |

Both reach JupyterHub (verified by response headers including `x-jupyterhub-version`,
`set-cookie` with `/hub/` path, JupyterHub-specific CSP). But songBird's HTTP client
causes JupyterHub to return 404 while curl gets the API JSON.

**Hypothesis**: songBird's internal HTTP client (`reqwest`/`hyper`) may be:
- Normalizing the URL path differently before TCP write
- Using HTTP/2 upgrade that the drawbridge handles differently
- Adding a header that triggers different drawbridge routing behavior
- Or: the drawbridge double-routes when request comes from another songBird instance

**Impact**: Low. The transport is proven. This is a songBird HTTP client interop issue
with its own drawbridge proxy. Direct TCP (curl) works perfectly.

**Suggested investigation**: Compare raw TCP payloads (`tcpdump` on sporeGate port 7780)
between a curl request and a songBird `http.request` to identify the divergence.

---

## Actions Completed

1. **Deployed fresh songBird 0.2.1** from golgi depot onto flockGate (replaced stale Jun 11 binary)
2. **Mesh re-initialized** — 2 peers connected (golgi 10.13.37.1, sporeGate 10.13.37.2)
3. **Full latency characterization** — 10 samples direct WG, 5 samples golgi relay
4. **Updated heads/flockGate.toml** with PASS status and full metrics
5. **primalSpring at 128 scenarios / 1101 tests / 0 fail** (includes composition profiles)

---

## Remaining Items for Upstream

### sporeGate Team (P1 — unblocks capability.call FULL PASS)

```bash
# Add to songBird environment on sporeGate:
sudo systemctl edit songbird
# Add:
# [Service]
# Environment=SONGBIRD_DRAWBRIDGE_ROUTES=/hub=jupyter
sudo systemctl restart songbird
```

After this, flockGate's `capability.call("jupyter")` should resolve via mesh peer discovery.
The auto-advertisement flow: startup → read env → `provided_capabilities()` → 
`announce_drawbridge_capabilities()` → `mesh.capabilities_announce` to all peers.

### songBird Code Team (P2 — http.request path bug)

The `http.request` method returns 404 from JupyterHub when curl to the same URL returns 200.
Both send identical headers (verified). The issue is below the HTTP header level.

**Reproduce on sporeGate**:
```bash
# This works:
curl http://localhost:7780/hub/api
# Does this also 404?
socat - UNIX-CONNECT:/run/songbird.sock <<'EOF'
{"jsonrpc":"2.0","id":1,"method":"http.get","params":{"url":"http://localhost:7780/hub/api"}}
EOF
```

If it also 404s locally on sporeGate, the issue is in songBird's HTTP client path
serialization. If it works locally, the issue is in how the remote peer relays the request.

### eastGate Overwatch

- ironGate cascade refresh (5+ days stale) — needs SSH access
- Wave 134c integration: composition profiles validated in primalSpring (scenario 128)
- All 7 stadial criteria CLEAR — WAN-DISPATCH-01 transport proven

---

## Metrics Snapshot

```
flockGate mesh (post-redeploy):
  songBird version: 0.2.1 (from golgi depot, 23MB)
  uptime: fresh (redeployed 09:42 EDT)
  peers: 2 (golgi, sporeGate)
  WireGuard: UP, ICMP 69ms to sporeGate
  
primalSpring:
  scenarios: 128 (new: s_composition_profiles)
  tests: 1101
  failures: 0
  suite: GREEN

WAN-DISPATCH-01:
  HTTP transport: PASS (10/10, 142ms p50)
  capability.call: FAIL (env config needed on sporeGate)
  Target: FULL PASS after sporeGate sets SONGBIRD_DRAWBRIDGE_ROUTES
```

---

*AAR authored by flockGate WAN mesh validation team. Patterns: fractal deployment
from pepti depot (binary redeploy via curl from membrane.primals.eco/depot/), mesh
re-initialization with known peers, latency characterization methodology (10 sequential
samples, sorted percentile calculation). Disseminate to sporeGate + songBird teams.*
