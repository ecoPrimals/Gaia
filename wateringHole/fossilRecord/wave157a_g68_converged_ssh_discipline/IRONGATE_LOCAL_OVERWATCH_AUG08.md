# ironGate Local Overwatch — Code Team Blurb

**Date**: 2026-08-08 09:15 EDT (Session 14 — Wave 157a Gate Redeploy)
**Gate**: ironGate (10.13.37.7) — PRIMARY DOWNSTREAM HOST
**Wave**: 157a — G68 CONVERGED
**Audience**: esotericWebb code team + footPrint code team (parallel IDE sessions)
**From**: ironGate hardware team (local overwatch)

---

## Gate State — REDEPLOYED

```
NUCLEUS:         31/31 HEALTHY
biomeOS:         4.57.0
petalTongue:     1.7.0 (UPGRADED — protocol negotiation wire.rs added upstream)
rhizoCrypt:      0.14.17 (UPGRADED)
sweetGrass:      0.8.0 (UPGRADED — capability.call handler shipped)
skunkBat:        0.2.18 (UPGRADED)
sourDough:       0.4.0 (NEW — live convergence validator)
nestGate:        0.5.0 (CAS on /mnt/nestgate, 12 TB avail)
squirrel:        0.1.0 (9 providers registered)
SSH:             ENFORCED — Forgejo only, zero github remotes
```

---

## What Changed for Code Teams

### petalTongue 1.7.0
- Protocol negotiation added (`petal-tongue-ipc/src/protocol_negotiation/wire.rs`)
- Scene passthrough from Session 13 is now in production binary
- WebSocket and UDS routes are stable

### sweetGrass 0.8.0
- `capability.call` handler now LIVE — was previously a gap
- Your braids should now validate through the new handler

### sourDough 0.4.0 (NEW)
- Live convergence validator — can validate running primal compliance
- Useful for verifying your cell compositions are G68 clean

---

## Blockers — Current

| Blocker | Owns | Impact |
|---------|------|--------|
| LLM provider for squirrel | infra/overwatch | `signal.plan` returns no-op |
| westGate CAS federation (NG-05) | westGate team | `content.replicate.pull` timeouts |
| footPrint `agentConnected: true` | footPrint code team | Agent panel shows disconnected until squirrel provider registered |

---

## Action Items for Code Teams

### esotericWebb
- **petalTongue 1.7.0** is now available — test WebGL pipeline with new protocol negotiation
- PrimalBridge can now route through Neural API with sweetGrass `capability.call`
- Springs activation is "when infrastructure stable" — we are **stable**

### footPrint
- **petal-bridge.ts** dual-socket router (Session 13) is running against petalTongue 1.7.0
- Verify `squirrel.sock` registration works with agent panel WebSocket
- `GeoJSON → nestGate → CAS` pipeline available (nestGate v0.5.0, 12 TB free)
- sourDough validator available for G68 compliance of footPrint cell

---

## Network Topology (unchanged)

```
ironGate: 10.13.37.7 (WireGuard)
nestGate CAS: /mnt/nestgate (12 TB, ext4)
petalTongue: :3001/ws (WebSocket)
Neural API: /run/user/1000/membrane/neural-api-default.sock
squirrel: /run/user/1000/biomeos/squirrel.sock (9 providers)
Forgejo: git@git.primals.eco (SSH key: ironGate)
Depot: https://depot.primals.eco (Caddy TLS, file browser)
```

---

*ironGate Wave 157a — REDEPLOYED. 31/31 healthy. G68 converged. SSH discipline enforced. 4 primal upgrades + 1 new binary. Code teams clear to resume.*
