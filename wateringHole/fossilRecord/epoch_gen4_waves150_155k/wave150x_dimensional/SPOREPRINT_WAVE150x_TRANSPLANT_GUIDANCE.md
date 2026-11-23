# sporePrint Transplant Guidance — Wave 150x

**Date**: Jul 24, 2026 | **Wave**: 150x | **From**: eastGate overwatch
**To**: sporePrint team (sporeGate)
**Priority**: P2 — publish after Tower Atomic wave stabilizes

---

## Mission

Update `primals.eco` to reflect the current ecosystem state. The site has 311
pages but several sections are stale (pre-150). The ecosystem has evolved
significantly: Tower Atomic proven, 6 exploration domains LIVE, crash-loop
self-recovery shipped, 196 validation scenarios, sovereign CI pipeline.

---

## What's New Since Last Publish (Wave 150p)

### Tower Atomic (the headline)

Tower Atomic (bearDog + songBird + skunkBat) has PROVEN WireGuard parity
and EXCEEDS on throughput:

| Metric | Tower | WireGuard | Verdict |
|--------|-------|-----------|---------|
| LAN throughput | 6.49 Gbps | 4.16 Gbps | **Tower 1.56x** |
| WAN throughput | 14.40 Mbps | 13.00 Mbps | **Tower 1.11x** |
| LAN latency | 0.72ms | 0.62ms | Parity |
| Jitter | Sub-ms | Multi-ms | **Tower wins** |

6 exploration domains ALL PROVEN LIVE:
1. Capability-aware routing — per-provider dispatch
2. Multi-stack routing — 6 traffic classes → 5 stacks
3. Large data transfer — content-addressed via nestGate CAS
4. Secure compute mesh — per-session BTSP keys + attestation
5. Distributed compute — 4-node targeted dispatch
6. Edge/SFF profile — 30MB RSS, 39MB total stack

### Topology

```
eastGate (.5)    — 1G MikroTik — code hub
sporeGate (.2)   — 1G MikroTik — build authority, HPC interface
flockGate (.6)   — WAN — Tower primal teams
golgiBody (.1)   — WAN hub — TURN relay, depot, Forgejo
northGate (.8)   — Windows 11, RTX 5090
grapheneGate     — Tower LIVE (HSM testing)
10G backbone     — between houses, large compute
```

Friends and family gates use R45 topology — Tower handles mixed routing.

### Sovereign Systems Shipped

- Sovereign CI pipeline (Forgejo → sporeGate build → depot → all gates)
- Crash-loop breaker + systemd hardening (29,081-restart divergence → self-recovery)
- DNSSEC on all 3 domains
- 196 primalSpring validation scenarios (7 stress + 7 pen test)
- biomeOS chimera design (Tower collapse into single process)

### Metrics Update for `config.toml`

| Metric | Old (150q) | Current (150x) |
|--------|-----------|----------------|
| Scenarios | 182 | **196** |
| Known debt | ~42 | **30** |
| Gate mesh | 5 + northGate | 5 + northGate + grapheneGate Tower |
| Shadow runs | 0 | **213 benchmark files** |

---

## Pages to Create/Update

### New Pages

| Page | Section | Content Source |
|------|---------|---------------|
| `tower_atomic.md` | `products/` or `architecture/` | Tower Atomic convergence, benchmark data, exploration domains |
| `sovereign_ci.md` | `architecture/` | Depot pipeline, Forgejo hooks, build authority model |
| `mesh_topology.md` | `architecture/` | Gate topology diagram, 10G/1G mix, enrollment |

### Pages to Update

| Page | What Changed |
|------|-------------|
| `architecture/deployment.md` | Add sovereign CI, crash-loop breaker, systemd hardening |
| `architecture/nucleus.md` | Tower Atomic as electron shell, Node/Nest atomic types |
| `products/` index | Add Tower Atomic, update metrics |
| `config.toml` entity registry | Update LOC, tests, capabilities for bearDog, songBird, skunkBat, cellMembrane |

### Pages NOT to Create (yet)

- rootPulse (P3 — not started)
- Node Atomic / Nest Atomic (depends on chimera)
- Chimera design (internal analysis, not public yet)

---

## Key Files to Read

1. `infra/wateringHole/analysis/TOWER_ATOMIC_DATA_ANALYSIS_150w.md` — honest data
2. `infra/wateringHole/analysis/TOWER_ATOMIC_COMPOSITION_MAP.md` — UDS interaction map
3. `primals/songBird/infra/wateringHole/TOWER_ATOMIC_CONVERGENCE.md` — full convergence doc
4. `infra/wateringHole/aars/FLOCKGATE_WAVE150w_SHADOW_DEPLOY_AAR.md` — 6/6 domains evidence
5. `infra/wateringHole/aars/PRIMALSPRING_EASTGATE_AAR_150x.md` — benchmark data

---

## Publishing Pipeline

Use existing Tier 2 flow:
1. Create content in `infra/sporePrint/content/`
2. Update `config.toml` entity registry metrics
3. Build locally: `cd infra/sporePrint && zola build`
4. Push to Forgejo — sovereign CI deploys to golgiBody

---

*sporePrint team: the ecosystem has evolved significantly since 150p. Tower
Atomic is the headline — proven to exceed WireGuard. Update the public face
to reflect our current posture. Focus on architecture and products sections.*
