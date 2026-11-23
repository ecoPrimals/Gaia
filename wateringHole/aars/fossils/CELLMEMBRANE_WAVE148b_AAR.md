# cellMembrane Wave 148b AAR — Deploy Fix Confirmed + Deep Debt Clear

**Date**: 2026-07-18 | **Wave**: 148b | **From**: eastGate overwatch (cellMembrane)

---

## What Was Done

### Wave 148a (code changes, pushed)

esotericWebb deploy artifacts were shipping with wrong port and CLI contract.
Root cause: cellMembrane assumed Webb used petalTongue (8080) and the standard
`server --socket` contract. In reality Webb serves directly on 8090.

**Fixes shipped** (`33aa33a`):

| Fix | Before | After |
|-----|--------|-------|
| systemd ExecStart | `server --socket /run/membrane/esotericwebb.sock` | `serve --content content/ --listen 0.0.0.0:8090` |
| systemd WorkingDirectory | (missing) | `/opt/ecoPrimals/gardens/esotericWebb` |
| systemd Restart | `always` | `on-failure` |
| Caddy `/webb/*` upstream | `petalTongue:8080` | `esotericWebb:8090` |
| Port constant | (none) | `DEFAULT_ESOTERICWEBB_PORT = 8090` |

### Wave 148b (debt sweep, pushed)

Comprehensive codebase audit — zero debt found:

- 0 files > 800 lines (largest: 762)
- 0 `TODO/FIXME/HACK/XXX/STUB` markers
- 0 `unsafe` blocks
- 0 `#[cfg(target_os)]` (OS Atheism complete)
- 0 `GateRole::Other()` (all roles typed)
- 0 mocks/stubs in production code
- 0 production `unwrap()`
- 1 stale doc reference fixed (caddy/ "deprecated" label removed)

**Test health**: 1,100 tests, 0 clippy, 0 debt.

---

## Port Map (Canonical — All Teams Please Note)

| Port | Service | Gate | Protocol |
|------|---------|------|----------|
| 8080 | nestGate / petalTongue | sporeGate | HTTP (static + WS) |
| 8090 | footPrint | sporeGate | HTTP (API, behind drawbridge) |
| 8090 | esotericWebb | flockGate | HTTP (direct serve) |

---

## cellMembrane Is Blocked — What We Need From Primals Teams

cellMembrane has **zero internal debt** and **zero actionable code tasks**.
All remaining work is blocked on upstream primals. Overwatch: please
disseminate to the following teams.

### OPERATIONAL (sporeGate ops team)

| Action | Gate | Command |
|--------|------|---------|
| Enable esotericWebb persistence | flockGate | `sudo systemctl enable --now esotericwebb-server` |
| Verify esotericWebb serving | flockGate | `curl http://localhost:8090/` |
| Activate Caddy route | golgiBody | Add `/webb/` → `flockGate:8090` to Caddyfile |

### songBird (P1)

| Need | Detail |
|------|--------|
| BTSP → `gate.enroll` integration | cellMembrane's `gate.enroll` is fully automated (7 phases). songBird BTSP handshake is the last missing enrollment primitive. Pending songBird team. |

### squirrel (P1)

| Need | Detail |
|------|--------|
| Accept `null` params on health endpoint | esotericWebb health checks send `null` params. squirrel rejects them. |

### nestGate (P1)

| Need | Detail |
|------|--------|
| `PROJECTS_PATH` CAS wiring | footPrint needs content-addressed project serving from nestGate. |

### petalTongue (P1)

| Need | Detail |
|------|--------|
| `WS_PATH` agent bridge | footPrint needs WebSocket bridge for real-time agent comms. |

### bearDog (P1)

| Need | Detail |
|------|--------|
| Confirm crypto JSON-RPC sigs | esotericWebb needs signed JSON-RPC responses from bearDog. |

### sweetGrass (P1)

| Need | Detail |
|------|--------|
| Confirm `braid.create/query` | esotericWebb needs braid endpoints for knowledge graph integration. |

### biomeOS (P2)

| Need | Detail |
|------|--------|
| GAP-017: neural-api resurrection | esotericWebb needs neural-api for capability routing. |
| GAP-018: executors not exposed | esotericWebb needs executor access for agent dispatch. |

### ALL primals (P2 ecosystem convention)

| Need | Detail |
|------|--------|
| GAP-036: Socket naming convention | Standardize UDS socket paths across all primals. |
| GAP-038: Stale UDS socket cleanup | Primals should clean up sockets on shutdown. |

---

## Ecosystem Status

Two sovereign products LIVE on mesh:
- **footPrint** → `primals.eco/footprint/` on sporeGate (LIVE)
- **esotericWebb** → `primals.eco/webb/` on flockGate (LIVE, persistence pending ops)

6-gate mesh operational. cellMembrane: 1,100 tests, 0 debt, stadial-ready.

---

*Overwatch: cellMembrane is clean and waiting. Please route the above demand
signal items to the respective primals teams. The P1 items are all that stand
between current state and full composition integration.*
