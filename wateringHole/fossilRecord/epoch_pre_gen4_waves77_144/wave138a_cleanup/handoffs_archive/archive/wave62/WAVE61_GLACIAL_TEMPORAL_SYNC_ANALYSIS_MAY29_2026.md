# Wave 61 — Glacial Goal Analysis: Temporal Sync + Triad Ownership

**Date**: May 29, 2026
**Context**: waterFall temporal sync spec and whitePaper complete. 8 upstream primals
shipped Wave 60 evolution (rhizoCrypt dag.*, loamSpine session.dehydrate, sweetGrass
braid.anchor, biomeOS manifest.gate_profile + DH-1, songBird mesh federation + DH-1,
toadStool/squirrel/barraCuda DH-1). Temporal sync gap discovered and resolved: GitHub
was 4+ commits ahead of Forgejo for 8 primals.

---

## Glacial Gate: Updated Status

### 5 Glacial Criteria (from GLACIAL_SHIFT_READINESS.md)

| # | Criterion | Pre-Wave 60 | Post-Wave 60 | Gap |
|---|-----------|-------------|-------------|-----|
| 1 | Sovereignty shadows S1-S4 cut over | 3/4 (S4 remaining) | 3/4 (unchanged) | S4 auth shadow period |
| 2 | Multi-gate LAN mesh (3+ Plasmodium) | Peer seeding shipped, not live-tested | Peer seeding shipped, not live-tested | Same-subnet + cross-subnet test |
| 3 | cellMembrane Nest expansion deployed | Tooling ready, not deployed | Tooling ready, not deployed | Deploy on VPS |
| 4 | Remote covalent node (flockGate WAN) | Not deployed | Not deployed | Full WAN deployment |
| 5 | DNS + Cloudflare removal | knot-dns planned, CF still live | knot-dns planned, CF still live | DNS cutover |

### NEW Glacial Criterion: Neural API Triad Operational

| # | Criterion | Status | Gap |
|---|-----------|--------|-----|
| 6 | rootPulse signal graphs execute against live primals | **Upstream shipped** (rhizoCrypt dag.*, loamSpine session.dehydrate, sweetGrass braid.anchor) | Wire primalSpring validation to detect live methods |
| 7 | waterFall temporal sync operational | Spec complete, bash not yet temporal | Implement `--source temporal` in cascade-pull.sh |
| 8 | Cross-gate graph executor Phase B | Spec complete | biomeOS implementation (Wave 65) |

---

## Upstream Primal Ownership Map

### Shipped (Wave 60 — verified May 29 via temporal sync)

| Primal | Method | Commits | Status |
|--------|--------|---------|--------|
| **rhizoCrypt** | `dag.branch` | 0b8ea84 | SHIPPED |
| **rhizoCrypt** | `dag.diff` | 0b8ea84 | SHIPPED |
| **rhizoCrypt** | `dag.merge` | 0b8ea84 | SHIPPED |
| **rhizoCrypt** | `dag.federate` | 0b8ea84 | SHIPPED |
| **loamSpine** | `session.dehydrate` | b516c15 | SHIPPED |
| **sweetGrass** | `braid.anchor` | ebee45f | SHIPPED |
| **biomeOS** | `manifest.gate_profile` | b698e79f | SHIPPED (v3.85) |
| **biomeOS** | DH-1 /tmp elimination | 29f9d1c2 | SHIPPED (v3.86) |
| **songBird** | mesh federation methods | f3f5990b | SHIPPED |
| **songBird** | DH-1 /tmp elimination | f20f95ee | SHIPPED |
| **toadStool** | DH-1 BIOMEOS_SOCKET_DIR | 844dada31 | SHIPPED |
| **squirrel** | DH-1 BIOMEOS_SOCKET_DIR | 88fa5a46 | SHIPPED |
| **barraCuda** | DH-1 BIOMEOS_SOCKET_DIR | 15681e31 | SHIPPED |

**13 of 14 upstream methods now shipped.** Only `biomeOS cross-gate graph.execute Phase B`
remains as an upstream blocker.

### Remaining Upstream (1 method + 3 DH-1)

| Primal | Target | Priority | Wave |
|--------|--------|----------|------|
| **biomeOS** | Cross-gate `graph.execute` Phase B | HIGH | 65 |
| **coralReef** | DH-1 /tmp cleanup | P2 | 66 |
| **sweetGrass** | DH-1 /tmp cleanup | P2 | 66 |
| **squirrel** | DH-1 verify complete | P2 | 66 |

### Verification Needed

The upstream primals shipped methods but we need to verify they match
the API contracts in primalSpring's capability registry:

| Verification | How | Owner |
|-------------|-----|-------|
| rhizoCrypt dag.* methods discoverable via `capability.call` | `s_primal_announce` + capability check | primalSpring |
| loamSpine `session.dehydrate` wire format | Method call test against live primal | primalSpring |
| sweetGrass `braid.anchor` wire format | Method call test against live primal | primalSpring |
| songBird `mesh.publish/discover_remotes/mirror` wire format | Method call test against live primal | primalSpring |
| nestGate `content.sync/push/fetch_heads/replicate` | **Not shipped** — check if included in songBird mesh work | nestGate team |

---

## Downstream Pattern Ingestion Map

### Who Consumes What

| Consumer | Pattern | Source | Status |
|----------|---------|--------|--------|
| **All gates** | `cascade-pull.sh --source temporal` | waterFall Phase 1 | NOT YET — needs implementation |
| **eastGate** | Temporal sync validates triad | primalSpring spec | IN PROGRESS |
| **ironGate** (projectNUCLEUS) | Deploy from VPS depot, common NUCLEUS | waterFall + deployment | PARTIALLY SHIPPED |
| **southGate** | wetSpring + neuralSpring sync via Forgejo | waterFall membrane sync | OPERATIONAL |
| **VPS (cellMembrane)** | `forgejo_mirror.sh` + temporal freshness | waterFall Phase 2 | NEEDS EVOLUTION |
| **All springs** | `biomeos signal dispatch ecosystem.pull` | waterFall Phase 3 | FUTURE (Wave 63+) |
| **gen5 collaborators** | Project-specific depot sync | waterFall airgap/depot | FUTURE |
| **strandGate, northGate** | Gate onboarding via waterFall | waterFall + NUCLEUS deploy | NOT DEPLOYED |
| **flockGate** (WAN) | Remote sync via VPS membrane | waterFall + songbird TURN | NOT DEPLOYED |
| **sporeGate, swiftGate** (mobile) | Roaming sync, on-connect waves | waterFall airgap | CONCEPTUAL |
| **kinGate** (friend's tower) | MitoBeacon + temporal sync | waterFall + genetic security | CONCEPTUAL |

### Ingestion Priority

| Priority | Consumer | Why |
|----------|----------|-----|
| P0 | All deployed gates (east/iron/south/biome) | Temporal sync eliminates stale-Forgejo problem immediately |
| P1 | VPS cellMembrane | Mirror service needs temporal awareness to stay current |
| P1 | strandGate | Ready hardware, needs onboarding |
| P2 | flockGate (WAN) | First remote node — validates WAN temporal sync |
| P3 | sporeGate/swiftGate/kinGate | Mobile/roaming — validates airgap and depot patterns |

---

## waterFall Temporal Sync: Glacial Impact

### Immediate Value (Phase 1 — Wave 61)

`--source temporal` in `cascade-pull.sh` directly addresses:

- **Stale Forgejo incident** (May 29): 8 primals had evolution on GitHub that
  Forgejo didn't have. Temporal sync would have automatically pulled from GitHub
  (the leader) and pushed to Forgejo (the follower).
- **Complementary membranes**: GitHub and Forgejo as equal participants, not
  primary/fallback. Whichever is ahead leads.
- **Push propagation**: After pulling from the leader, automatically push to
  followers. One gate's sync brings all membranes into parity.

### Medium-Term Value (Phase 2-3 — Wave 62-65)

- **Freshness protocol**: Gates publish temporal state to mesh. Other gates
  can check freshness without fetching (saves bandwidth and time).
- **Neural API integration**: `ecosystem.pull` signal graph with temporal
  source selection replaces bash.
- **Forgejo inversion**: With temporal sync, the formal inversion from
  `default_source = "github"` to `default_source = "forgejo"` becomes
  less critical — temporal sync naturally uses whoever is ahead.

### Glacial Value (Phase 4 — Wave 65+)

- **Fleet temporal coordination**: Cross-gate `ecosystem.check` provides
  fleet-wide freshness view.
- **Adaptive sync**: Hot repos sync more frequently, cold repos less.
- **Plasmodium coherence**: All gates maintaining temporal awareness
  IS the Plasmodium — coherent, distributed, self-maintaining.

---

## Work Remaining: Ordered by Glacial Impact

### Immediate (Wave 61)

| Task | Owner | Effort | Blocks |
|------|-------|--------|--------|
| Implement `--source temporal` in `cascade-pull.sh` | primalSpring/infra | Small | Stale sync elimination |
| Verify upstream rhizoCrypt/loamSpine/sweetGrass API contracts | primalSpring | Medium | rootPulse semantic validation |
| benchScale temporal sync test | primalSpring/infra | Medium | Temporal sync confidence |

### Near-Term (Wave 62-63)

| Task | Owner | Effort | Blocks |
|------|-------|--------|--------|
| Extended `freshness.toml` schema | primalSpring/infra | Small | Freshness protocol |
| `--publish-freshness` in cascade-pull | primalSpring/infra | Small | Freshness tracking |
| Verify nestGate `content.sync/push/fetch_heads` status | nestGate team | — | waterFall Phase 3 |
| Promote rootPulse signals from structural to semantic | primalSpring | Medium | Glacial criterion 6 |
| VPS `forgejo_mirror.sh` evolution to temporal | cellMembrane team | Small | VPS freshness |

### Medium-Term (Wave 64-65)

| Task | Owner | Effort | Blocks |
|------|-------|--------|--------|
| biomeOS cross-gate `graph.execute` Phase B | biomeOS team | Large | Glacial criterion 8 |
| Wire ecosystem.pull/push/check to live execution | biomeOS team | Medium | waterFall Phase 3 |
| strandGate onboarding | infra | Medium | Glacial criterion 2 (3+ gates) |
| S4 auth shadow completion | bearDog/cellMembrane | Medium | Glacial criterion 1 |

### Longer-Term (Wave 65+)

| Task | Owner | Effort | Blocks |
|------|-------|--------|--------|
| flockGate WAN deployment | infra | Large | Glacial criterion 4 |
| Sovereign DNS (knot-dns) cutover | cellMembrane | Medium | Glacial criterion 5 |
| Cloudflare retirement | cellMembrane | Small | Glacial criterion 5 |
| DH-1 remaining primals (coralReef, sweetGrass) | primal teams | Small | VPS `ProtectSystem=strict` |
| Fleet temporal coordination | primalSpring + biomeOS | Large | Full Plasmodium |

---

## Updated Wave Timeline

```
Wave 60 (done)   Neural API triad spec + whitePaper series
                 8 upstream primals shipped evolution
                 Temporal sync gap discovered + manually resolved

Wave 61          --source temporal in cascade-pull.sh
                 Upstream API contract verification
                 benchScale temporal sync test

Wave 62-63       Freshness protocol (extended freshness.toml)
                 rootPulse structural → semantic promotion
                 strandGate onboarding
                 S4 auth shadow

Wave 64-65       biomeOS cross-gate graph.execute Phase B
                 Neural API ecosystem signal wiring
                 flockGate WAN prep

Wave 65+         Cross-gate temporal coordination
                 Fleet dashboard
                 Remaining sovereignty cutover

Glacial Gate     All 8 criteria met
                 Sovereign inner membrane
                 3+ gates meshed with temporal coherence
                 Cloudflare removed
```

---

## Key Insight: Upstream Has Moved Faster Than Expected

The Wave 60 upstream targets document (May 29) listed 14 methods as
"API contracts that don't exist yet." By the same evening, 13 of 14
were shipped by upstream primals. The ecosystem is evolving concurrently
and asynchronously — exactly the pattern waterFall is designed to
support.

The irony: we discovered this evolution because we couldn't see it.
GitHub had the truth, Forgejo was stale, and `--source auto` picked
the stale membrane. The temporal sync spec was born from this exact
failure mode.

**The ecosystem's own evolution validated the need for temporal sync.**
