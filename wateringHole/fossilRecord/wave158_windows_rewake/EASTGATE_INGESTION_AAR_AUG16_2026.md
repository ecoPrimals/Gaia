# AAR: eastGate Enmeshment + Ingestion — Aug 16, 2026

**Gate**: eastGate
**Wave**: 157k Enmeshment + Ingestion
**Teams**: biomeOS, primalSpring
**Outcome**: exp125 VALIDATED (23/24). rootPulse 6/6 graphs REGISTERED. D12/D13 + content.put confirmed CLOSED. Fork storm remediated.

---

## Actions Taken

### 1. exp125 bonsai-bt — Live NUCLEUS Validation

Ran exp125 against eastGate's live 14/14 NUCLEUS. Results:

- **23/24 PASS** (matches blurb expectation)
- **Tree 1** (reactive health): Sequence over capability domains — PASS (tree executed)
- **Tree 2** (compute fallback): Select first-success-wins — PASS
- **Tree 3** (provenance pipeline): hash→store→DAG→sign — PASS
- **Tree 4** (serialization): 550B JSON, BLAKE3, equality preserved — PASS
- **Tree 5** (memoryless reactive): Re-evaluate each tick — PASS

**1 expected failure**: `has_capability("crypto")` returns false because `CompositionContext::from_live_discovery_with_fallback()` can't find biomeOS's neural API socket via the standard discovery path. Root cause: socket naming mismatch — biomeOS uses `biomeos-neural.sock` but discovery looks for `neural-api-{family}.sock`. This is a known discovery gap (not a bonsai-bt issue).

**Finding for Phase 1**: EcoAction semantics validated. Trees compose cleanly over Neural API domains without referencing primal names. The bonsai-bt 0.13 API integrates directly with primalSpring's composition types.

### 2. rootPulse Graph Execution (Item #10, P2)

**Status**: DONE — all 6 rootPulse graphs now registered in biomeOS composition pattern registry.

Before: Only `rootpulse_commit` was in `CompositionPatternRegistry::with_canonical_patterns()`.
After: All 6 graphs registered with correct method sequences, primal lists, and graph file paths:

| Graph | Methods | Primals |
|-------|---------|---------|
| `rootpulse_commit` | crypto.sign, dag.event.append, braid.anchor, spine.commit | bearDog, rhizoCrypt, sweetGrass, loamSpine |
| `rootpulse_harvest` | crypto.sign, content.put, spine.commit, braid.attribute | bearDog, nestGate, loamSpine, sweetGrass |
| `rootpulse_branch` | dag.session.create, spine.create, braid.attribute | rhizoCrypt, loamSpine, sweetGrass |
| `rootpulse_merge` | dag.dehydration.trigger, crypto.sign, spine.commit, braid.attribute | rhizoCrypt, bearDog, loamSpine, sweetGrass |
| `rootpulse_diff` | spine.get, dag.merkle.root | loamSpine, rhizoCrypt |
| `rootpulse_federate` | discovery.peers, spine.get, content.get, dag.event.append, spine.commit | songBird, loamSpine, nestGate, rhizoCrypt |

biomeOS 1,608 tests pass. `graph.list` will now expose all rootPulse graphs.

### 3. Fork Storm Remediation (Carryover)

Confirmed: stale `~/.local/bin/` primal binaries were removed on Aug 14. No recurrence observed. 14/14 primals healthy from plasmidBin depot, biomeOS alive (2.5+ days uptime).

---

## Commits Pushed

| Repo | Commit | Description |
|------|--------|-------------|
| **biomeOS** | `af1dc9d3` | Register all 6 rootPulse graphs in composition pattern registry |
| **primalSpring** | `8f235850` | Wave 157k enmeshment + ingestion: bonsai-bt exp125, rootPulse 6/6 |

---

## Remaining eastGate Items

| # | Item | Status |
|---|------|--------|
| exp125 live discovery gap | Socket naming mismatch — known, not blocking Phase 1 | P4 |
| bonsai-bt Phase 1 scaffold | sourDough scaffold + EcoAction/EcoBlackboard + provenance | NEXT (downstream) |
| Graph visualization spec | Shared with ironGate (petalTongue) — spec filed | WAITING |

---

*eastGate posture: ACTIVE (exp125 validated, rootPulse registered). Ingesting bonsai-bt. 0/0/0.*
