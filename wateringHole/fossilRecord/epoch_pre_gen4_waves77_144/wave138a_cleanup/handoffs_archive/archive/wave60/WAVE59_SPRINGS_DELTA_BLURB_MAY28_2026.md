# Wave 59b Springs Delta Blurb — southGate Focus

**Date:** May 28, 2026
**From:** primalSpring coordination
**To:** wet/neuralSpring (active), all other springs (delayed)

---

## P0 RESOLVED. NUCLEUS is live on VPS.

13/13 primals on UDS sockets. Spring overlay validated. The infrastructure
works. Now we prove the patterns.

---

## Strategy: Concentrate on southGate

**All springs delayed except wet/neuralSpring.** southGate is the pattern
node. We stabilize it, prove the membrane-to-spring connection, document
the patterns, then hand off to all other springs.

This means: hotSpring, groundSpring, airSpring, healthSpring — **no action
needed this wave**. Prepare column U artifacts at your own pace. We'll come
to you with proven patterns.

---

## wet/neuralSpring — Your Sprint

### Phase 1: southGate Stabilization

| Task | Status |
|------|--------|
| Fresh plasmidBin redeploy (13 primals) | NEEDED (currently 7/13 health) |
| SONGBIRD_PEERS config for mesh seeding | NEEDED |
| All 13 primals responding on southGate | TARGET |

### Phase 2: Membrane Connection Patterns

| Task | Status |
|------|--------|
| `CompositionContext::from_live_discovery()` against live VPS sockets | PROVE |
| UDS discovery path (tiers 2-4) working from spring runtime | PROVE |
| `health.liveness` round-trip through Neural API | PROVE |
| Dispatch telemetry flowing (JSON-lines for routing data) | PROVE |

### Phase 3: Column U (first emission)

| Task | Status |
|------|--------|
| Cell graph exists with `vps_standard = true` | CHECK |
| `domain_profile.toml` prepared for lithoSpore | PREPARE |
| Binary in plasmidBin depot | CHECK |
| `biomeos nucleus ingest` through NUCLEUS path | GATED on biomeOS v0.2 |

### What You Document for Other Springs

After proving phases 1-2, document:
1. How spring runtime discovers VPS NUCLEUS primals
2. UDS socket paths and discovery tiers that work
3. Any env vars or config needed
4. Failure modes and workarounds
5. Telemetry expectations

This becomes the **Spring Membrane Connection Playbook** for all other springs.

---

## Other Springs — Status (delayed, no action needed)

| Spring | Gate | Column U | Wait For |
|--------|------|----------|----------|
| hotSpring | biomeGate | P3 (after patterns) | biomeGate 13/13 + biomeOS v0.2 |
| groundSpring | eastGate | P3 (after patterns) | Pattern playbook |
| airSpring | eastGate | P3 (after patterns) | Pattern playbook |
| healthSpring | ironGate | P3 (after patterns) | Pattern playbook |
| ludoSpring | desktop-only | N/A | Not on VPS path |

---

## Timeline

```
NOW    → southGate fresh redeploy + stabilization
THEN   → wet/neuralSpring membrane patterns proven
THEN   → Spring Membrane Connection Playbook documented
THEN   → hotSpring + groundSpring column U (pattern handoff)
TARGET → Stadial: NC-1(2+) + NC-2(3+) + NC-4(all 4 gates)
```

---

*Wave 59b. NUCLEUS live. southGate is your node. Prove the path.*
