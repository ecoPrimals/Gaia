# Deployment Signaling Evolution — biomeOS + swarmVine

**Date**: Aug 12, 2026 | **Wave**: 157k | **From**: overwatch (eastGate)
**To**: biomeOS team (eastGate), swarmVine team (ironGate), primalSpring (eastGate)
**Status**: SPEC — evolution track for next subwave

---

## Problem

When graftGate deployed Full NUCLEUS via `biomeos nucleus start --mode full`, it found **10 divergences** (D1-D10: socket path limits, binary name mismatch, keychain access, security provider handshake, resurrection loops, PATH inheritance, etc). These divergences were discovered by a human operator and reported via an AAR document pushed to wateringHole.

**There is no automated deployment feedback channel.** biomeOS can deploy→verify internally, but cannot emit structured deployment events to the gossip mesh for fleet-wide convergence. When a gate deploys and encounters divergences, other gates and overwatch have no way to know until a human writes an AAR.

## Current State

### What exists (swarmVine gossip):
- `GossipTopic::Tower` — capability ads, topology, reachability
- `GossipTopic::Data` — CAS availability, braid HEADs, depot manifests
- `GossipTopic::Compute` — resource capacity, build queues
- Domain types: `CascadeNotification`, `CascadeResult`, `DepotFreshness`
- Events: `endpoint.alive` (self-inject on startup)

### What exists (biomeOS):
- `composition.orchestrate` — deploy→gossip→verify pipeline
- `resurrection.rs` — health monitoring with rapid-restart detection
- `nucleus start --mode full` — sequential primal launch with health checks
- Capability auto-discovery after deployment

### What's missing:
- No `deploy.result` gossip event — gates can't signal deployment outcomes
- No `deploy.divergence` gossip event — divergences aren't propagated
- No way for primalSpring or overwatch to aggregate deployment health across gates
- biomeOS `composition.orchestrate` doesn't emit gossip after deploy/verify phases

## Proposed Evolution

### Phase 1: biomeOS deploy events → swarmVine gossip

biomeOS emits structured gossip entries after each deployment phase:

```
deploy.result:<gate>  → Tower topic
{
    "gate": "graftGate",
    "wave": "157k",
    "status": "partial",            // "success" | "partial" | "failed"
    "primals_launched": 13,
    "primals_failed": 0,
    "capabilities_active": 21,
    "divergences": [
        {"id": "D2", "primal": "barraCuda", "detail": "binary name mismatch"},
        {"id": "D6", "primal": "biomeOS", "detail": "security capability resurrection loop"}
    ],
    "timestamp": "2026-08-12T13:21:00Z"
}
```

Implementation path:
1. biomeOS: after `composition.orchestrate` completes, call `gossip.inject` via local swarmVine UDS
2. swarmVine: no changes needed — `GossipTopic::Tower` already supports arbitrary key prefixes
3. Key format: `deploy.result:<gate_id>` (matches existing `endpoint.alive:<gate_id>` pattern)

### Phase 2: Divergence convergence loop

When a gate reports divergences, code teams can:
1. Query `gossip.query("tower", "deploy.result:")` to see all gates' deployment status
2. Fix the divergence in their primal
3. Push fix → depot rebuild → cascade → gate redeploys → new `deploy.result` with divergence resolved

primalSpring can aggregate `deploy.result` entries across gates to produce a fleet-wide deployment health view.

### Phase 3: cellMembrane sovereignty validation

cellMembrane validates deployment integrity at the sovereignty boundary:
- Verify deployed binary hashes against depot manifest
- Confirm capability domains match expected composition profile
- Emit `deploy.validated:<gate>` after sovereignty check passes

### Phase 4: Topology-aware deployment (sporeGate)

sporeGate topology integrates deployment status into cascade decisions:
- Skip cascade to gates with active divergences
- Prioritize depot rebuild when multiple gates report the same divergence
- NanoWire retirement accelerated by deployment gossip (mesh-native `deploy.result` replaces SSH-based status checks)

## Interaction Model

```
biomeOS (composition.orchestrate)
    ↓ deploys primals, detects divergences
    ↓ emits deploy.result via swarmVine gossip.inject
        → swarmVine spreads to mesh peers
            → primalSpring aggregates fleet status
            → overwatch sees deployment health dashboard
            → code teams see their divergences
    ↓ code teams fix + push
        → depot rebuild → cascade → redeploy
            → new deploy.result (divergences resolved)
                → convergence achieved
```

## Implementation Estimate

| Phase | Owner | Scope | Depends On |
|-------|-------|-------|------------|
| 1 | biomeOS (eastGate) | Add `gossip.inject` call after `composition.orchestrate` | swarmVine UDS available on deployment gate |
| 2 | primalSpring (eastGate) | Aggregate `deploy.result` entries | Phase 1 |
| 3 | cellMembrane (sporeGate) | Sovereignty validation → gossip | Phase 1, bearDog signing |
| 4 | sporeGate topology | Topology-aware cascade | Phase 2 |

Phase 1 is the immediate target — it closes the feedback gap with minimal changes to existing code.

## Evidence

- graftGate NUCLEUS AAR: 10 divergences found by human, reported via document
- southGate canary: 4 bugs found by human, reported via AAR
- Both required overwatch to manually cross-reference repo HEADs to determine fix status
- With deployment gossip, the canary findings would propagate automatically

---

*Deployment signaling is the pheromone trail that closes the ant colony convergence loop (ref: whitePaper subGen/SWARMVINE_ANT_COLONY_NUCLEUS_ATOMICS.md). Without it, the colony forages blind.*

---
*FOSSILIZED Wave 157k interstadial (Aug 14, 2026). Content absorbed into ortho/blurb or implemented in code.*
