# ironGate Wave 157k POST-PANDEMIC EVOLUTION AAR

**Date**: 2026-08-12 | **Wave**: 157k | **Gate**: ironGate (10.13.37.10)
**Operator**: ironGate hardware overwatch
**Posture**: INNER MEMBRANE LIVE. 0/0/0.

---

## SUMMARY

Full cascade from golgiBody Forgejo absorbed Wave 157k rationalized ownership, MeshRelay completion, Nest Atomic Neural API, and G72 Tier-2 evolution across 15 repositories. 7 depot binaries replaced (targeted redeploy). **13/13 services active. 2 gossip peers (westGate + eastGate). 594 entries ingested. Vine-bat OPERATIONAL. Mesh relay enabled.**

---

## RATIONALIZED OWNERSHIP — ironGate

Per Wave 157k canonical gate × team matrix, ironGate now owns:

| Code Team | Role |
|-----------|------|
| **bearDog** | Trust + signing |
| **songBird** | Network orchestration |
| **skunkBat** | Security membrane |
| **swarmVine** | Gossip mesh |
| **bingoCube** | (parked) |
| **petalTongue** | Visualization |
| **esotericWebb** | Web interface |
| **footPrint** | (new: from flockGate) |
| **tideGlass** | (new: from flockGate) |
| + 4 parked springs | airSpring, groundSpring, healthSpring, ludoSpring |

ironGate role: **Primal workhorse, 14TB NFT braid, primary Linux builder.**

---

## CASCADE

15 repositories pulled with new commits:

| Category | Repos Updated |
|----------|---------------|
| **primals/** | barraCuda, bearDog, biomeOS, petalTongue, songBird, sourDough, squirrel, swarmVine, toadStool |
| **gardens/** | cellMembrane |
| **springs/** | hotSpring, primalSpring |
| **infra/** | wateringHole |

Key landed changes:
- **songBird**: `gossip.subscribe` completes MeshRelay surface (relay/inject/spread/subscribe); cross-gate federation forwarding via `gossip.spread`
- **bearDog**: gossip LIVE — protocol alignment + socket resolution fix; G72 Tier-2 url excision (-32 crates); darwin ios.rs fix
- **biomeOS**: Nest Atomic Neural API + riboCipher transport fix; deploy→gossip→verify pipeline wired into `composition.orchestrate`
- **swarmVine**: cascade domain types (CascadeNotification, CascadeResult, DepotFreshness); GossipTopic::FromStr; GATE_ID warning + peer discovery diagnostics
- **barraCuda**: Node-Atomic silicon AAR; multi-pass reduction + HMC correctness (ΔH 73000→0.97)
- **petalTongue**: peptidoglycan per-arch BLAKE3SUMS; nestgate.io depot/provenance routes
- **sourDough**: cross-platform service template module (systemd + launchd)
- **cellMembrane**: peer registry LAN IPs for ironGate/southGate/strandGate; sovereign defense fail2ban wiring
- **primalSpring**: lifecycle executor deploy→gossip→verify pipeline
- **squirrel**: darwin build fix
- **toadStool**: silicon ledger + idle-aware routing (Node-Atomic AAR)

---

## DEPOT REDEPLOY

7 changed binaries replaced (targeted, not full fleet):

| Binary | Change |
|--------|--------|
| biomeos | Nest Atomic Neural API + deploy→gossip→verify |
| songbird | MeshRelay complete (gossip.subscribe/relay/spread) |
| barracuda | Node-Atomic silicon + HMC correctness |
| beardog | Gossip LIVE + G72 Tier-2 (-32 crates) |
| petaltongue | Per-arch BLAKE3SUMS + nestgate.io routes |
| squirrel | Darwin build fix |
| toadstool | Silicon ledger + idle-aware routing |

8 unchanged binaries retained from 157i: coralreef, loamspine, nestgate, rhizocrypt, skunkbat, sourdough, sweetgrass, swarmvine.

---

## SERVICE STATUS

| Metric | Value |
|--------|-------|
| Services | **13/13 active** |
| Capabilities | **166 across 8 registered primals** |
| Registered services | 18 (including TARPC virtual endpoints) |
| Dispatch latency | **9ms** (gossip.inject resolve) |
| TCP 7800 | **LISTENING** |
| Mesh relay | **ENABLED** (1 reachable peer, relay active) |

Capability breakdown:
- rhizocrypt: 40, squirrel: 39, loamspine: 37, skunkbat: 31
- nestgate: 7, coralreef: 6, petaltongue: 3, beardog: 3

Note: skunkBat registration script expanded from 5→31 capabilities to match self-registration set. Eliminates first-registration-wins race condition.

---

## GOSSIP MESH

| Metric | 157i | 157k |
|--------|------|------|
| Peers | 2 | **2** (stable) |
| Entries ingested | 1 | **594** |
| Entries sent/peer | 1 | **594** |
| Tower entries | 1 | **8** |
| Compute entries | 0 | **1** |
| Nonce history | 1 | **594** |

Peer table:

| Peer | Address | Entries Sent | Status |
|------|---------|-------------|--------|
| westGate | 192.168.4.149:7800 | 594 | ACTIVE |
| eastGate | 10.13.37.5:7800 | 594 | ACTIVE |

Cross-gate TCP 7800 reachability:

| Gate | Status |
|------|--------|
| westGate (192.168.4.149) | REACHABLE |
| eastGate (10.13.37.5) | REACHABLE |
| southGate (10.13.37.7) | **REACHABLE** (new since 157i!) |
| sporeGate (10.13.37.1) | UNREACHABLE |
| strandGate (10.13.37.3) | UNREACHABLE |
| graftGate (10.13.37.13) | UNREACHABLE |

---

## BLOCKER #3 — songBird --node-id

**Finding**: `mesh.status` correctly reports `"node_id":"ironGate"` (sourced from GATE_ID env var). The `identity` endpoint reports `"primal":"songbird"` (correct — that is the primal name, not the gate ID). The issue is that no `--node-id` CLI flag exists in the binary.

**Action**: songBird code team (now ironGate-owned) should add `--node-id` CLI flag so gate identity can be set at startup rather than solely via env var. Not blocking — mesh identity is correct.

---

## DELTA FROM WAVE 157i

| Metric | 157i | 157k | Change |
|--------|------|------|--------|
| Wave | 157i | 157k | +2 waves |
| Services | 13/13 | 13/13 | STABLE |
| Capabilities | 166 | 166 | STABLE (registration script fixed) |
| Dispatch | 2ms | 9ms | +7ms (cold resolve) |
| Gossip peers | 2 | 2 | STABLE |
| Gossip entries | 1 | 594 | +593 (mesh active) |
| Vine-bat | OPERATIONAL | OPERATIONAL | STABLE |
| P0/P1/P2 | 0/0/1 | 0/0/0 | **ALL CLEAR** |
| southGate TCP | UNTESTED | REACHABLE | NEW |
| MeshRelay | MISSING | **ENABLED** | SHIPPED |
| Mesh relay peers | 0 | 1 | +1 |

---

## OPEN ITEMS

| Priority | Item | Owner |
|----------|------|-------|
| — | songBird `--node-id` CLI flag (blocker #3) | songBird code team (ironGate) |
| — | ~~skunkBat registration ordering~~ **FIXED** (script expanded 5→31 caps) | ironGate ops |
| — | sporeGate TCP 7800 unreachable | sporeGate ops |
| — | strandGate TCP 7800 unreachable | strandGate ops |
| — | graftGate TCP 7800 unreachable | graftGate (pending enmeshment) |
| — | toadStool service disabled (`biome.yaml` required) | toadStool code team (strandGate) |
| — | sourDough has no systemd service template | sourDough code team (graftGate) |
| — | hotSpring gossip: 0/10 events (scaffold) | hotSpring code team (strandGate) |
| — | nestGate runs TCP-only, no UDS socket | nestGate code team (westGate) |

---

*ironGate Wave 157k — POST-PANDEMIC EVOLUTION. 15-repo cascade. 7 targeted depot binaries deployed. 13/13 services. 166 capabilities (skunkBat registration fix). 2 gossip peers, 594 entries. MeshRelay ENABLED. southGate reachable. 0/0/0. Rationalized ownership absorbed.*
