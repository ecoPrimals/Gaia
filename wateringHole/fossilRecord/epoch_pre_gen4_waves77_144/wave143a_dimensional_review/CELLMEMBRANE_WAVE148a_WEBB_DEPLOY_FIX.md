# cellMembrane Wave 148a AAR — esotericWebb Deploy Fix

**Date**: 2026-07-18 | **Wave**: 148a | **From**: eastGate overwatch (cellMembrane)
**Scope**: esotericWebb port + systemd unit + Caddy routing correction

---

## What Happened

esotericWebb shipped its binary and went LIVE on flockGate:8090. The upstream
AAR revealed that cellMembrane's shipped deploy artifacts (Wave 147e) had 3
bugs — all caused by a port confusion between nestGate/petalTongue (8080) and
esotericWebb (8090), plus an incorrect CLI contract assumption.

## Root Cause

cellMembrane assumed esotericWebb used the standard NUCLEUS `server --socket`
contract and routed through petalTongue on port 8080. In reality, esotericWebb
uses `serve --content content/ --listen 0.0.0.0:8090` — a direct HTTP server
on its own port, not behind petalTongue.

## What Was Fixed (cellMembrane `33aa33a`)

| Fix | Detail |
|-----|--------|
| **systemd unit** | ExecStart: `server --socket` → `serve --content content/ --listen 0.0.0.0:8090` |
| **systemd unit** | Added `WorkingDirectory=/opt/ecoPrimals/gardens/esotericWebb` (so `--content content/` resolves) |
| **systemd unit** | `Restart=always` → `Restart=on-failure` per upstream spec |
| **Caddy generation** | `/webb/*` upstream: `petalTongue:8080` → `esotericWebb:8090` |
| **Typed constant** | `DEFAULT_ESOTERICWEBB_PORT = 8090` added to constants |

## Port Map (Clarified)

| Port | Service | Gate | Notes |
|------|---------|------|-------|
| 8080 | nestGate / petalTongue | sporeGate | Static content, WS bridge |
| 8090 | footPrint | sporeGate | footPrint API (behind drawbridge) |
| 8090 | esotericWebb | flockGate | Direct HTTP server |

## Test Health

1,100 tests passing. 0 clippy warnings. 0 debt markers.

---

## Action Items for Primals Teams

### sporeGate ops (DEPLOY — operational, not code)
- [ ] `sudo systemctl enable --now esotericwebb-server` on flockGate
- [ ] Verify `curl http://localhost:8090/` returns esotericWebb content
- [ ] Activate Caddy route on golgiBody: `/webb/` → `flockGate:8090`

### esotericWebb — no action needed
Binary in depot, Forgejo synced, LIVE. cellMembrane artifacts now match.

### squirrel (P1)
- [ ] Accept `null` params on health endpoint (blocks esotericWebb health checks)

### nestGate (P1)
- [ ] `PROJECTS_PATH` CAS wiring for footPrint

### petalTongue (P1)
- [ ] `WS_PATH` agent bridge for footPrint

### bearDog (P1)
- [ ] Confirm crypto JSON-RPC signatures for esotericWebb

### sweetGrass (P1)
- [ ] Confirm `braid.create/query` endpoints for esotericWebb

### songBird (P1)
- [ ] BTSP → cellMembrane `gate.enroll` integration (pending)

### biomeOS (P2)
- [ ] GAP-017: neural-api resurrection
- [ ] GAP-018: executors not exposed

### ALL primals (P2 ecosystem convention)
- [ ] GAP-036: Socket naming convention
- [ ] GAP-038: Stale UDS socket cleanup

---

## Ecosystem Status After 148a

Two composition products now serving on sovereign mesh:
- **footPrint** → `primals.eco/footprint/` on sporeGate (LIVE)
- **esotericWebb** → `primals.eco/webb/` on flockGate (LIVE, persistence pending ops)

6-gate mesh operational. 1,100 cellMembrane tests. All primals at 0 debt.

---

*Pushed to Forgejo. Overwatch: disseminate to primals teams per action items above.*
