# ironGate Session 15 — Wave 157a swarmVine Deploy + Seam Verified

**Date**: 2026-08-08 20:35 EDT
**Gate**: ironGate (10.13.37.7)
**Wave**: 157a — N2-N5 VERIFIED
**From**: ironGate hardware team
**To**: eastGate overwatch

---

## Summary

swarmVine deployed to ironGate NUCLEUS (primal #16). songBird gossip seam verified (ipc.register → gossip.inject → swarmVine epidemic table). Systemd services unified to /usr/local/bin with GATE_ID env. Double-launch prevention hardened.

---

## Execution

### 1. Cascade

Absorbed: biomeOS riboCipher auto-detect (+208 LOC), songBird gossip seam (`af0d8fa8`), toadStool S370/S371, cellMembrane transport unification, primalSpring exp121.

### 2. swarmVine Deployed

- Cloned from Forgejo (`ecoPrimals/swarmVine`)
- Built from source: `cargo build --release` (20.9s, 30 warnings — all unused)
- Installed to `/usr/local/bin/swarmvine`
- Created `membrane-nucleus@swarmvine.service` (systemd user, boot-persistent)
- Config: `--gate-id ironGate --gossip-port 7800`, `SWARMVINE_PEERS=192.168.4.149:7800`
- Sockets: `/run/user/1000/biomeos/swarmvine.sock` + `.tarpc.sock`
- Health: Healthy, `gossip.inject` and `gossip.query` working

### 3. songBird Gossip Seam — VERIFIED

- Rebuilt songBird from source (includes `6b580cf0` seam + `af0d8fa8` fix)
- **Root cause of initial failure**: systemd service was running old depot binary (19 MB) without seam code. New binary is 24 MB (with seam).
- After installing correct binary, tested:
  - `ipc.register` with capabilities → songBird fires `gossip.inject` to swarmVine
  - Confirmed: `capability.advertise:ironGate:seam-proof` entry appeared in gossip table
  - `capability.advertise:ironGate:nestgate` and `petaltongue` also propagated
- Auto-discovered primals (loamspine, rhizocrypt, sweetgrass) use internal registry, not `ipc.register` path — so no gossip injection for those (by design)

### 4. Service Unification — Double-Launch Prevention

- All services now use `/usr/local/bin/` (unified with depot)
- Added `Environment=GATE_ID=ironGate` to all 14 services
- Added `NESTGATE_JWT_SECRET` to nestgate service
- Operator instruction: NEVER `nohup` manually — use `systemctl --user restart`

---

## Final State

```
NUCLEUS services:  14 active (13 original + swarmVine)
Sockets:           29
RSS:               92 MB total
Load:              1.94 (32 cores)
swarmVine:         LIVE (gossip inject + query + epidemic sweep)
songBird seam:     VERIFIED (ipc.register → gossip.inject)
Gossip entries:    4 (nestgate, petaltongue, seam-proof, healthcheck)
Binary path:       ALL /usr/local/bin/ (unified)
GATE_ID:           Set on all services
```

---

## Gaps Identified

| Gap | Impact | Owner |
|-----|--------|-------|
| Depot binary doesn't include gossip seam yet | songBird on depot is pre-seam (19 MB vs 24 MB rebuilt) | sporeGate depot rebuild |
| beardog registers as "beardog-tunnel" (identity mismatch) | Can't register beardog via script | beardog team (identity.get response) |
| Auto-discovered primals skip gossip seam | loamspine/rhizocrypt/sweetgrass not in gossip table | songBird team (consider auto-discovery → gossip path) |
| westGate swarmVine not confirmed running | Can't test epidemic spread cross-gate | westGate team |
