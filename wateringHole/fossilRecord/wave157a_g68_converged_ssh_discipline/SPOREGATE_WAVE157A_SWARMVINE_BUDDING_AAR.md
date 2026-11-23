# AAR: Wave 157a — swarmVine v0.1.0 Budding (Primal #16)

**Date**: Aug 8, 2026 11:50 | **Gate**: sporeGate | **Author**: eastGate overwatch

---

## SESSION SCOPE

Budded a new primal: **swarmVine** — epidemic gossip engine for capability, data, and compute propagation across the Tower Atomic mesh. Companion of skunkBat. Scaffolded via sourDough, implemented core gossip engine, validated, built musl binary, staged to depot, pushed to golgi and Forgejo.

---

## WHAT WE EXECUTED

### 1. Concept Discovery — swarmVine identified

User recalled a concept/primal named "swarmVine" from the whitePaper archives related to gossip protocols. Deep search of `infra/whitePaper/` confirmed the name was never committed — it was a remembered concept.

**What already existed**: songBird's `mesh.capabilities_announce` (push gossip), reachability gossip, BirdSong encrypted beacons, topology graph with gossip-inferred edges.

**What was missing**: gossip as a dedicated concern separated from songBird's transport layer, and gossip at the Data and Compute layers (not just Tower/capabilities).

**Architectural decision**: New primal (not just composition) — songBird is the largest Tower primal and already overloaded with transport + discovery + gossip. Extracting gossip gives it its own evolution path, test surface, and clean composition boundary with skunkBat.

### 2. sourDough Scaffold — budded from DNA

```bash
sourdough scaffold new-primal swarmVine "Epidemic gossip engine for capability, data, and compute propagation across the Tower Atomic mesh" --output ../swarmVine
```

Scaffold generated 31 files: workspace Cargo.toml, `swarmvine-core` crate (lifecycle, health, transport, riboCipher, G65 negotiation, G68 substrate), `swarmvine-server` crate (dual-protocol JSON-RPC + tarpc, method gate, Neural API announce), CI workflows, deny.toml, capability registry.

**Key design constraint**: Scaffold independence — generated primal has zero `sourdough-core` dependency. All DNA is inlined. Wire format is the contract.

### 3. Core Gossip Engine — three domains implemented

Added `gossip.rs` to `swarmvine-core` with:

| Component | Purpose |
|-----------|---------|
| `GossipTopic` enum | `Tower`, `Data`, `Compute` — three gossip domains |
| `GossipEntry` struct | Topic + key + payload + origin gate + nonce + TTL + version + timestamps |
| `GossipEngine` | In-memory store, nonce dedup, TTL eviction, version conflict resolution, forward queue |
| `IngestResult` enum | `Accepted`, `Duplicate`, `Expired`, `Rejected`, `AtCapacity` |
| `PeerStats` | Per-peer exchange tracking (received, sent, rejected, last exchange) |
| `GossipStats` | Aggregate stats (entries per topic, nonce history, peer count, totals) |

**Gossip protocol**:
1. Entry arrives → check nonce (dedup) → check TTL → validate key format
2. Compare version with existing entry (higher wins)
3. Store in topic table → add nonce to history → queue for forwarding
4. Periodic eviction of expired entries (default 10 min TTL)
5. Forward to all mesh peers with decremented TTL (epidemic spread)

**Three domains**:
- **Tower**: `capability.advertise:gate:primal`, `topology.reachability:gate`, `endpoint.alive:gate`
- **Data**: `cas.have:gate` (bloom filter), `braid.head:gate`, `depot.manifest:gate`, `content.fresh:gate`
- **Compute**: `compute.capacity:gate`, `build.queue:gate`, `inference.bandwidth:gate`

### 4. JSON-RPC Dispatch — 11 methods

| Method | Direction | Description |
|--------|-----------|-------------|
| `gossip.spread` | peer → swarmVine | Receive gossip entries (single or batch) |
| `gossip.inject` | local primal → swarmVine | Create new locally-originated entry |
| `gossip.query` | local primal → swarmVine | Query table by topic + key prefix |
| `gossip.status` | any → swarmVine | Gossip table stats |
| `gossip.peers` | any → swarmVine | Per-peer exchange stats |
| `health.liveness` | any → swarmVine | Standard liveness probe |
| `health.readiness` | any → swarmVine | Readiness + capabilities |
| `health.check` | any → swarmVine | Full health + node_id |
| `capabilities.list` | any → swarmVine | IPC surface + gossip domains |
| `btsp.negotiate` | any → swarmVine | BTSP null cipher fallback |
| `primal.announce` | any → swarmVine | Neural API self-announce |

### 5. Tests — 33/33 passing

| Suite | Tests | Coverage |
|-------|-------|----------|
| `swarmvine-core` gossip engine | 12 | inject/query, prefix filter, nonce dedup, expiry, version conflict, forward queue, eviction, peer stats, stats aggregate |
| `swarmvine-core` lifecycle | 3 | lifecycle, health, engine access |
| `swarmvine-server` dispatch | 17 | liveness, capabilities (gossip domains), unknown method, parse error, BTSP, gossip inject+query, status, peers, spread |
| `swarmvine-server` method gate | 12 | permissive/enforcing, classify public/protected, token allowlist, serde |

### 6. sourDough Validation — all pass

| Validator | Result | Details |
|-----------|--------|---------|
| `validate primal` | PASS | Cargo.toml, specs/, crates/, README, PrimalLifecycle, PrimalHealth |
| `validate transport` | PASS (warnings) | Transport injection detected, no silicon deism, standard self-binding warnings |
| `validate ribocipher` | **FULL** | All 3 signal bytes (0xEC/0xED/0xEE), first-byte detection, legacy deprecation |
| `validate neural-api` | **FULL** | primal.announce, ipc.register, capabilities, signal_tiers, cost/latency hints |

### 7. Musl Build — 2.4 MB

```
-rwxrwxr-x  2.4M  swarmvine
ELF 64-bit LSB pie executable, x86-64, static-pie linked, stripped
```

### 8. Depot + Golgi Push

- Staged to `infra/plasmidBin/primals/x86_64-unknown-linux-musl/swarmvine`
- Pushed to golgi: `depot-push: golgi musl sync OK (18 binaries)`
- Depot now has 18 binaries (was 17)

### 9. Forgejo Repo Created

- Created `ecoPrimals/swarmVine` on Forgejo via API (golgiAdmin token, then deleted)
- Pushed `master` branch: `8f5fa89` — 31 files, 5058 insertions
- Remote: `ssh://git@git.primals.eco:2222/ecoPrimals/swarmVine.git`
- GitHub mirror: `git@github.com:ecoPrimals/swarmVine.git` (added as `github` remote)
- Forgejo is origin (sovereign), GitHub is mirror (K-derm)

---

## WHAT WORKS

| Aspect | Status |
|--------|--------|
| Scaffold | sourDough budding works perfectly — full DNA at birth |
| Gossip engine | 3-domain epidemic gossip with dedup, TTL, version resolution |
| Wire standard | riboCipher FULL, Neural API FULL, G65 negotiation ready |
| Binary | 2.4 MB musl static, depot + golgi |
| Source | Forgejo + GitHub mirror |
| Tests | 33/33 |

## WHAT NEEDS EVOLUTION

| Gap | Owner | Priority |
|-----|-------|----------|
| Cross-gate propagation via songBird mesh | swarmVine + songBird teams | P1 |
| skunkBat pre-accept validation (vine-bat loop) | skunkBat team | P2 |
| songBird gossip migration (`mesh.capabilities_announce` → swarmVine) | songBird team | P2 |
| Data gossip injection (nestGate/loamSpine → `gossip.inject`) | nestGate + loamSpine teams | P3 |
| Compute gossip injection (toadStool/coralReef → `gossip.inject`) | toadStool + coralReef teams | P3 |
| biomeOS composition graph (`gossip_propagation.toml`) | biomeOS team | P3 |
| NUCLEUS deployment to all gates | overwatch | P1 |
| `gossip.subscribe` streaming method | swarmVine team | P3 |
| Bloom filter for CAS `have` sets | swarmVine team | P4 |
| Periodic epidemic sweep (pull from peers on timer) | swarmVine team | P3 |

## TIMELINE

| Time | Action |
|------|--------|
| 11:37 | User identifies swarmVine concept for gossip |
| 11:38 | Deep search confirms name never committed, gossip substrate in songBird |
| 11:40 | Decision: new primal (not composition) — three-domain gossip engine |
| 11:42 | sourDough scaffold: `scaffold new-primal swarmVine` |
| 11:43 | Core gossip engine implemented (gossip.rs, 350 lines) |
| 11:44 | Dispatch updated with 6 gossip methods |
| 11:45 | 33/33 tests passing, musl release built (2.4 MB) |
| 11:46 | sourDough validation: primal PASS, riboCipher FULL, Neural API FULL |
| 11:47 | Staged to depot, pushed to golgi (18/18 binaries) |
| 11:49 | Blurb updated, pushed to wateringHole |
| 11:50 | Forgejo repo created, code pushed, GitHub mirror added |

**Total**: ~13 minutes from concept to deployed binary in depot.

---

## DESIGN DECISIONS

### Why a new primal (not a composition)?

songBird already handles transport, discovery, relay, federation, STUN, ACME, mesh topology, AND gossip. Adding Data and Compute gossip domains to songBird would increase its already-largest surface area.

swarmVine gives gossip:
- Its own evolution path (independent of transport changes)
- Its own test surface (gossip-specific scenarios without mesh transport complexity)
- A clean composition boundary with skunkBat (vine spreads, bat validates)
- The ability to serve non-Tower domains (Data, Compute)

### Why three domains?

"Gossip happens at data and compute as well." The ecosystem needs propagation of:
1. **What can I do?** → Tower gossip (capabilities)
2. **What do I have?** → Data gossip (CAS, braids, depot)
3. **What can I run?** → Compute gossip (GPU, CPU, build capacity)

songBird only ever handled #1. swarmVine handles all three with a unified protocol.

### vine-bat loop

skunkBat is swarmVine's companion:
- swarmVine receives → optionally delegates to skunkBat for challenge-verify → stores/forwards
- skunkBat validates origin lineage (via bearDog), detects gossip-bomb patterns, rate-limits suspicious origins
- This mirrors the biological metaphor: vine spreads nutrients, immune system validates

---

*swarmVine v0.1.0 — primal #16. Epidemic gossip for Tower + Data + Compute. sourDough scaffold → 33 tests → riboCipher FULL → Neural API FULL → 2.4 MB musl → depot → golgi → Forgejo. 13 minutes from concept to binary. Vine spreads, bat validates.*
