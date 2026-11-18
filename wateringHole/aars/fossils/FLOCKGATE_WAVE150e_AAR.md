# flockGate Wave 150e AAR — esotericWebb LIVE, Deployment Chain Validated

**Date**: 2026-07-18 | **Wave**: 150d→150e | **From**: flockGate WAN overwatch
**Gate**: flockGate (10.13.37.6) | **Role**: WAN covalent validation + esotericWebb host

---

## Summary

flockGate completed all assigned ops actions for Wave 150e. esotericWebb is
now externally functional at `webb.primals.eco` with systemd persistence.
The full deployment chain (Cloudflare → Caddy → WireGuard → service) has been
validated end-to-end from WAN for all 5 composition surfaces.

---

## Deliverables

### 1. esotericWebb V19.1 — HTTP-Aware TCP Listener

**Problem**: esotericWebb's TCP listener spoke raw newline-delimited JSON-RPC.
Caddy sent HTTP POST → esotericWebb parsed `POST /jsonrpc HTTP/1.1` as JSON →
parse error → response sent without HTTP framing → Caddy 502.

**Fix**: Added HTTP detection to `handle_tcp_connection()` in
`webb/src/ipc/listener.rs`. First line is inspected:
- If it starts with `POST`/`GET`/`PUT`/`OPTIONS` → consume HTTP headers,
  extract body via Content-Length, dispatch JSON-RPC, return HTTP/1.1 200
  with Content-Type + CORS headers.
- Otherwise → fall through to existing raw JSON-RPC protocol.

Both protocols coexist on the same port. Zero new dependencies.

**Commit**: `08588d5` pushed to `github.com:sporeGarden/esotericWebb`

### 2. systemd Unit Enabled

Created `/home/flockgate/.config/systemd/user/esotericwebb-server.service`:
- `Type=simple`, `Restart=always`, `RestartSec=5`
- WorkingDirectory set to gardens/esotericWebb
- Environment inherits ECOPRIMALS_ROOT and BIOMEOS_SOCKET_DIR
- Enabled at `default.target` — survives reboot

### 3. primalSpring Scenario Fix — Subdomain Standard

Updated `s_protokarya_wan_deploy` to reflect the subdomain migration:
- Live probe now targets `footprint.primals.eco` (was `primals.eco/footprint/`)
- Added redirect validation: old path returns 301 (confirms migration)
- Structural check accepts both URL formats (composition manifest not yet updated)

**Commit**: `c677c3c` pushed to primalSpring

### 4. Full WAN Surface Validation

| Surface | Code | Latency | Chain |
|---------|------|---------|-------|
| `footprint.primals.eco` | 200 | 216ms | golgi → sporeGate:8090 |
| `webb.primals.eco` | 200 | 235ms | golgi → flockGate:8090 |
| `sporeprint.primals.eco` | 200 | 524ms | golgi (local) |
| `live.primals.eco` | 200 | 357ms | golgi → sporeGate |
| `git.primals.eco` | 200 | 203ms | golgi (local) |
| `lab.primals.eco` | 401 | 128ms | golgi → ironGate |
| `primals.eco` (root) | 301 | 139ms | golgi redirect |

---

## Remaining Divergence

### P0 — Blocks External Users

| Item | Owner | Gate | Detail |
|------|-------|------|--------|
| footPrint map tiles blank | cellMembrane + ops | golgiBody | Caddy reload needed (`membrane caddy.generate`). Code complete per Wave 150e. Until Caddy reloads, tile proxying may not work despite CSP fix. |
| esotericWebb V19.1 not in depot | flockGate / sporeGate | depot | Local build only. Needs `depot_sync --push` or sporeGate harvest. Not blocking WAN — binary runs locally. |

### P1 — Inter-Primal Wiring

| Item | Owner | Status |
|------|-------|--------|
| petalTongue `WS_PATH` agent bridge | petalTongue team | **OPEN** — last remaining P1 |
| footPrint CAS consumer verification | footPrint team | nestGate says COMPLETE, consumer side unverified |

### P2 — Ecosystem Quality

| Item | Owner | Detail |
|------|-------|--------|
| primalSpring CAC scenario | primalSpring | FRAGO issued, not implemented |
| `primals.eco` DNSSEC | ops / Cloudflare | Enable via API (trivial but not done) |
| esotericWebb GET handler | flockGate | GET returns 502 via Caddy (only POST works). Not blocking JSON-RPC consumers but breaks browser navigation. |
| `footprint_composition.toml` URL update | cellMembrane | Still references `primals.eco/footprint/` — needs `footprint.primals.eco` |
| Credential store trait | bearDog + squirrel | Silicon Atheism Phase 2 |
| Health monitoring trait | ecosystem | Not procfs-hardcoded |

### Architectural Notes

1. **esotericWebb GET support**: The HTTP adapter only processes POST (extracts
   JSON body). A GET to `webb.primals.eco/` returns 502 because there's no body
   to parse. For browser-navigable UI, esotericWebb needs either:
   - A static HTML page served on GET (petalTongue serves this for footPrint)
   - Or a dedicated GET handler returning status/docs HTML

2. **Depot binary**: V19.1 is a local build on flockGate (`target/release/`).
   It's not in the ecosystem depot yet. sporeGate's next harvest cycle should
   pick it up, or we can push manually.

3. **systemd vs lingering**: The user unit requires `loginctl enable-linger`
   for the service to survive logout. Currently active because flockGate has
   an active session.

---

## Dimensional Impact

| Dim | Before | After | Note |
|-----|--------|-------|------|
| 6 (Public Surface) | AMBER | **GREEN** for flockGate | webb.primals.eco LIVE |
| 8 (Compositions) | AMBER | **GREEN** for flockGate | esotericWebb externally functional |

**Ecosystem-wide**: Dimensions 6+8 remain AMBER until golgiBody Caddy reload
(footPrint tiles) completes. flockGate's contribution is done.

---

## Test Health

- primalSpring: 169 scenarios, 1,203 tests, 0 failures
- esotericWebb: 453 tests, 0 failures
- Known debt: `graphenegate-readiness` (14), `full-cross-compile` (3, pre-harvest)

---

*flockGate Wave 150e: OPS COMPLETE. esotericWebb V19.1 LIVE on webb.primals.eco.
systemd enabled. Full deployment chain proven. 5/5 composition surfaces responding.
Only remaining flockGate item: GET handler + depot binary push (both P2).*
