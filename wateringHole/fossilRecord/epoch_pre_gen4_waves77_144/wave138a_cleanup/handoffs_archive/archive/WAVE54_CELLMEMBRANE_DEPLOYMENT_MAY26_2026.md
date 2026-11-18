# Wave 54 — cellMembrane + Deployment Handoff

**Date**: 2026-05-26  
**From**: primalSpring (coordination)  
**To**: cellMembrane team, gate operators, primal teams with deployment items  
**Context**: PostPrimordial complete. Primal mountain debt clearing in Wave 53.
This handoff prepares cellMembrane and gate operators for Wave 54 deployment
stabilization. Glacial shift wave plan at `wateringHole/GLACIAL_SHIFT_WAVE_PLAN.md`.

---

## Upstream Status: CLEAR

- plasmidBin pipeline: `validate` 100/100, `doctor` 35/35, all 14 binaries
  checksummed. `fetch --all --force` pulls complete NUCLEUS.
- K-Derm topology + bonding model standards published to wateringHole.
- primalSpring v0.9.30: 92 experiments, 175/193 certify, zero debt.
- sourDough v0.3.0 harvested and verified.

---

## Garden Guidance

### cellMembrane (CRITICAL — owns 3 glacial blockers)

Phase 1 (Tower) operational on VPS. Channel 2 TURN/RustDesk LIVE, Channel 3
TLS LIVE. `cellmembrane-types` v0.1.0, 80 tests. Wave 51 deep-debt clean.

#### Action items:

1. **2nd CI runner on eastGate** (HIGH — eliminates ironGate SPOF)
   - Workflow configs already default to `self-hosted, linux, x86_64`
   - Deploy `actions-runner` on eastGate alongside existing ironGate runner

2. **VPS Nest expansion** (GLACIAL BLOCKER 1)
   - Deploy Nest primals on `membrane-relay` VPS ([RELAY_PUBLIC]):
     rhizoCrypt, loamSpine, sweetGrass, NestGate
   - Use `plasmidbin fetch --all --force` on VPS, then start Nest primals
   - Transforms VPS from Tower-only to Tower+Nest (provenance + storage on outer membrane)
   - Reconcile with projectNUCLEUS README which claims Nest Atomic LIVE —
     glacial-shift tracker still lists Nest as not deployed

3. **Sovereign DNS** (GLACIAL BLOCKER 2)
   - Deploy knot-dns on VPS (Channel 1)
   - Replace Cloudflare DNS delegation for `primals.eco` zone
   - DNS sovereignty milestone

4. **K-Derm wire contract** (NEW — primalSpring integration)
   - Publish to `wateringHole/`:
     - `membrane.toml` canonical schema
     - Layer placement per primal (which K-Derm layer each primal occupies)
     - `BoundaryPolicy` set (what crosses each layer boundary)
     - Channel protein definitions
   - primalSpring will consume `cellmembrane-types` (`EnvelopeTopology`,
     `BondType`, `ChannelProtein`) and add `s_kderm_boundary` scenario

5. **S1 TLS shadow prep** (after DNS)
   - Cloudflare → sovereign TLS via Caddy (S1 cutover)
   - Can begin once DNS is sovereign

### projectNUCLEUS (IMPORTANT — gate coordination)

Sovereignty evolution active. 13/13 primals zero debt, 8/8 springs Tier 4.
55 Rust tests, shadow orchestrator 6/6 PASS.

- **Gate coordination**: assist SouthGate + BiomeGate redeploy (see operator
  items below)
- **Horizon 2 cutovers**: BearDog TLS 7-day parity (H2-12), DNS NS cutover
  (H2-17/18) — align with cellMembrane sovereign DNS
- **Forgejo Actions**: deploy Forgejo on ironGate as shadow CI (H3-03), then
  invert to Forgejo-primary

### projectFOUNDATION (LOW — background)

gen4 soil layer. Deep debt pass complete. Thread validation partial.

- **BLAKE3 backfill**: 155 sources pending fetch — continue as data becomes available
- **Thread 1 WCM**: 0/27 validated — incremental work, not blocking
- No Wave 54 deployment dependencies; continue at current pace

### esotericWebb (FYI — spring-side Wave 55)

V10, 357 tests, 91% coverage. 12 open evolution gaps.

- 6 `game.*` methods for ludoSpring integration are Wave 55 items
- BearDog crypto bridge gap (GAP-015) resolves after BearDog TCP drop
- No Wave 54 action needed

### lithoSpore (FYI — field deployment)

v0.1.0, 7/7 modules PASS. 4 USBs deployed to Barrick Lab.

- **Tier 3 provenance**: wired but needs live NUCLEUS at runtime — benefits
  from VPS Nest expansion
- Songbird TURN client library + TURN-relayed RPC: blocked on Songbird, not
  cellMembrane
- No Wave 54 action needed; benefits passively from gate stabilization

### blueFish (NO ACTION)

Placeholder repo. Product not started. No Wave 54 dependencies.

---

## Per-Primal Deployment Guidance

### songbird (after Wave 53 fix)

- SouthGate: confirm Songbird process stability after crash investigation
- BiomeGate: restart with `SONGBIRD_FEDERATION_PORT=7700` + `SONGBIRD_PEERS=192.168.1.144:7700`
- Validate federation handshake with eastGate mesh

### bearDog (TCP drop prototype)

- **Test NUCLEUS**: run BearDog UDS-only (no TCP 9900/9101)
- Verify all crypto capabilities reachable via domain sockets
- If successful, this validates the Tower CNS convergence path (exp114)

### biomeOS (cephalization prep)

- primalSpring will prototype primal-scoped socket directories (exp113):
  `biomeos/beardog/crypto.sock` instead of `biomeos/crypto.sock`
- Backward compat via symlinks
- Phase A: beardog/ (5 sockets) + barracuda/ (5 sockets)
- biomeOS Neural API will need primal-scoped socket discovery in a future
  wave — no action needed now, primalSpring validates routing first

### NestGate (VPS deployment)

- Will be deployed to VPS as part of cellMembrane Nest expansion
- Verify version alignment resolved in Wave 53 before VPS deploy

### rhizoCrypt, loamSpine, sweetGrass (VPS deployment)

- Will be deployed to VPS as Nest primals
- No code changes needed — `plasmidbin fetch` delivers current binaries
- Verify health via `plasmidbin doctor` after VPS deployment

### All others (NO ACTION)

toadStool, coralReef, barraCuda, petalTongue, squirrel, skunkBat, sourDough,
bingoCube — no Wave 54 deployment items. Continue normal evolution.

---

## Gate Operator Guidance

### SouthGate (after Wave 53 Songbird fix)

Fresh NUCLEUS redeploy:
```
plasmidbin fetch --all --force
plasmidbin launch
```
Target: 13/13 primals, all sockets healthy.
Verify: `SONGBIRD_PEERS=192.168.1.144:7700` (eastGate mesh seed).

### BiomeGate

Restart Songbird with federation:
```
SONGBIRD_FEDERATION_PORT=7700 SONGBIRD_PEERS=192.168.1.144:7700 \
  plasmidbin start songbird
```
Push from 6–9 primals to full 13/13. Verify federation handshake
with eastGate.

### eastGate (reference — no action)

13/13 primals, 19/19 sockets, doctor 35/35. Reference deployment.
Accept 2nd CI runner from cellMembrane.

### ironGate (no action)

Operational. Continue as primary CI gate.

---

## Timeline

Wave 54 begins after Wave 53 primal mountain work completes (SouthGate
stability is the gate). Estimated: 1–2 sprints.

Respond with status ack to `wateringHole/handoffs/`.
