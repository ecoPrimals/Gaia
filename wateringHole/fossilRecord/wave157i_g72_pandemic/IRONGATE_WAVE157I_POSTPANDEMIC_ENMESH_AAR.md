# ironGate Wave 157i POST-PANDEMIC ENMESHMENT AAR

**Date**: 2026-08-11 | **Wave**: 157i | **Gate**: ironGate (10.13.37.10)
**Operator**: ironGate hardware overwatch

---

## SUMMARY

Full cascade from golgiBody Forgejo (git.primals.eco) absorbed Wave 157i G72 Tier-1 dependency pandemic cleanup, gossip injection expansion, nestGate S147/S148, and depot-rebuilt binaries across 26 repositories. All 15 depot binaries replaced with G72-trimmed versions. **13/13 services active. 2 gossip peers converged (westGate + eastGate). Vine-bat OPERATIONAL.**

---

## CASCADE

26 repositories pulled with new commits:

| Category | Repos Updated |
|----------|---------------|
| **primals/** | barraCuda, bearDog, biomeOS, coralReef, loamSpine, petalTongue, rhizoCrypt, songBird, sourDough, squirrel, swarmVine, sweetGrass, toadStool |
| **gardens/** | cellMembrane |
| **springs/** | hotSpring, primalSpring, tideGlass, wetSpring |
| **infra/** | fossilRecord, plasmidBin, sporePrint, wateringHole, whitePaper |

Key landed changes:
- **G72 Tier-1 complete**: ~155+ crates shed fleet-wide (11/11 teams)
- **bearDog**: 41 dead deps removed, `tokio["full"]` eliminated
- **petalTongue**: telemetry crate removed, runtime peer discovery
- **nestGate S147/S148**: nestgate-nas dropped, steam feature removed, shared state consolidation
- **barraCuda**: 22/22 gossip events (full spec coverage)
- **wetSpring**: 4/4 gossip events wired
- **sweetGrass**: `braid.verify` behavioral tests (P2 CLOSED)
- **hotSpring**: pseudoSpore E2E pipeline shipped
- **darwinGate→graftGate**: rename across sporePrint, whitePaper, cellMembrane, primalSpring

---

## DEPOT REDEPLOY

15 depot binaries pulled from `depot.primals.eco` and replaced in `/usr/local/bin/`:

| Binary | 157i | Previous | Delta |
|--------|------|----------|-------|
| beardog | 12M | 8.3M | +2.9M (new features) |
| nestgate | 8.5M | 9.1M | -0.6M (crate surgery) |
| petaltongue | 29M | 34M | -5M (telemetry excised) |
| biomeos | 17M | 17M | +213K |
| swarmvine | 2.6M | 2.5M | +29K |
| barracuda | 8.8M | 8.8M | +45K |
| coralreef | 9.1M | 9.1M | +32K |
| loamspine | 5.0M | 5.0M | +37K |
| rhizocrypt | 7.9M | 7.8M | +41K |
| sweetgrass | 8.6M | 8.6M | +24K |
| skunkbat | 3.3M | 3.3M | ~0 |
| songbird | 19M | 19M | ~0 |
| squirrel | 8.7M | 8.7M | ~0 |
| sourdough | 3.4M | 3.4M | ~0 |
| toadstool | 13M | 14M | -1M |

Feature verification via strings:
- sweetGrass: `braid.verify` CONFIRMED in binary
- barraCuda: `gossip: injected precision.route`, `gossip: injected health.degraded` CONFIRMED
- swarmVine: vine-bat dispatch with `SWARMVINE_SKUNKBAT_SOCK` CONFIRMED
- nestGate: version 0.5.0

---

## SERVICE STATUS

| Metric | Value |
|--------|-------|
| Services | **13/13 active** |
| Capabilities | **166 across 8 registered primals** |
| Registered primals | 18 (including TARPC virtual endpoints) |
| Dispatch latency | **2ms** |
| TCP 7800 | **LISTENING** (pid swarmvine) |

Capability breakdown:
- rhizocrypt: 40
- squirrel: 39
- loamspine: 37
- skunkbat: 31
- nestgate: 7
- coralreef: 6
- petaltongue: 3
- beardog: 3

---

## GOSSIP MESH — ironGate NOW PEERED

**Previous state (Wave 157g)**: listening, 0 peers
**Current state (Wave 157i)**: **2 peers converged**

| Peer | Address | Entries Sent | Status |
|------|---------|-------------|--------|
| westGate | 192.168.4.149:7800 | 1 | ACTIVE |
| eastGate | 10.13.37.5:7800 | 1 | ACTIVE |
| sporeGate | 10.13.37.1:7800 | — | REFUSED |

Gossip status:
- tower_entries: 1
- total_ingested: 1
- peer_count: 2
- vine-bat: OPERATIONAL (preaccept via skunkBat)

`gossip.inject` (tower topic): ingested successfully, vine-bat preaccept active.
`gossip.spread`: correctly rejected duplicate nonce.

---

## CROSS-GATE TCP REACHABILITY

| Gate | Address | Status |
|------|---------|--------|
| westGate | 192.168.4.149:7800 | REACHABLE |
| eastGate | 10.13.37.5:7800 | REACHABLE |
| sporeGate | 10.13.37.1:7800 | REFUSED |
| ironGate | 0.0.0.0:7800 | LISTENING |

---

## OPEN ITEMS

| Priority | Item | Owner |
|----------|------|-------|
| P2 | petalTongue port remaining | petalTongue code team |
| — | MeshRelay needed for blueGate + southGate peering | songBird code team |
| — | nestGate runs on TCP (127.0.0.1:8083/8091), no UDS socket | nestGate code team |
| — | sweetGrass capabilities not surfaced in songBird registration (riboCipher framing required) | upstream config |
| — | sporeGate TCP 7800 refused — needs depot rebuild or swarmVine startup | sporeGate ops |
| — | toadStool service disabled (CLI requires `biome.yaml`) | toadStool code team |
| — | sourDough has no systemd service template | sourDough code team |
| — | graftGate SSH/WG enrollment blocked on sporeGate | sporeGate topology |
| — | hotSpring gossip: 0/10 events (scaffold only) | hotSpring code team |

---

## DELTA FROM WAVE 157g

| Metric | 157g | 157i | Change |
|--------|------|------|--------|
| Wave | 157g | 157i | +2 waves |
| Services | 13/13 | 13/13 | STABLE |
| Capabilities | 170 | 166 | -4 (G72 consolidation) |
| Dispatch | 16ms | 2ms | **-14ms (8x faster)** |
| Gossip peers | 0 | 2 | **+2 (westGate + eastGate)** |
| Vine-bat | OPERATIONAL | OPERATIONAL | STABLE |
| TCP 7800 | LISTENING | LISTENING | STABLE |
| G72 Tier 1 | in progress | 11/11 COMPLETE | DONE |
| P0/P1/P2 | 0/0/2 | 0/0/1 | braid.verify CLOSED |

---

*ironGate Wave 157i — POST-PANDEMIC ENMESHMENT complete. 26-repo cascade. 15 G72-trimmed binaries deployed. 13/13 services. 2ms dispatch. 2 gossip peers converged. Vine-bat OPERATIONAL. 0/0/1.*
