# primalSpring Team — eastGate (Wave 116)

**Status**: ACTIVE | **Gate**: eastGate | **Date**: 2026-06-18
**Repo**: `/home/eastgate/Development/ecoPrimals/springs/primalSpring`
**Tests**: 75 validation scenarios (all passing)

---

## Role

You are the **primalSpring evolution team** on eastGate. Your focus is the science and validation engine — evolving `primalSpring`, expanding scenario coverage, proving NUCLEUS integration patterns, and maintaining genetics compliance.

Overwatch handles cascade coordination, cross-team blurbs, and ecosystem-wide state tracking. You focus on **code evolution**.

---

## Current State (Jun 19 14:10 EDT)

| Asset | Status |
|-------|--------|
| primalSpring | 75 scenarios passing, toadStool S320+ (112 methods, MitoBeacon) |
| NUCLEUS on eastGate | **13/13 LIVE** (user systemd, no sudo) |
| WireGuard | eastGate (.5) enrolled, 5-node mesh stable |
| VCS | origin + forgejo at parity, zero drift |
| cellMembrane | **680 tests** green (rootpulse, webhook cascade, SSH consolidation) |
| membrane binary | Fresh (topology.resolve/zones/mesh + rootpulse dispatch) |
| pepti | SSH→forgejo FIXED — fresh builds unblocked |

---

## Your Primals (eastGate compute focus)

Your 11 live primals give you capabilities to leverage:

| Primal | What It Does For You |
|--------|---------------------|
| **Squirrel** | AI inference — use for scenario intelligence, evolution guidance |
| **ToadStool** | Compute dispatch — orchestrate experiment runs, scenario batches |
| **BarraCuda** | Tensor math — future GPU offload path (northGate 5090 via covalent bond) |
| **CoralReef** | Shader compilation — visualization backend |
| **RhizoCrypt** | DAG provenance — track experiment lineage, cascade verification |
| **LoamSpine** | Merkle ledger — wave state persistence, sovereign commits |
| **SweetGrass** | Attribution — commit braids, who contributed what |
| **BearDog** | Trust — BTSP encryption for cross-gate bonds |
| **Songbird** | Discovery — mesh relay, peer finding |
| **SkunkBat** | Defense — audit, anomaly detection |
| **PetalTongue** | Visualization — dashboard rendering |

## Your Work

### P1 — primalSpring Scenario Expansion

Grow validation coverage. Current scenarios cover:
- Mesh topology (5-node WG overlay)
- Gate enrollment posture
- Cytoplasm zones (three-hub triangle)
- Composition routing

**Next scenarios to add:**
- NUCLEUS deployment validation (user systemd pattern)
- Sovereignty ledger verification (rootpulse commit/verify round-trip)
- K-Derm layer validation (plasma membrane ↔ periplasm ↔ outer membrane)
- Gate parity assertion (N primals alive, systemd persisted, WG handshake active)
- Primal debt tracking (detect missing modules from composition)
- Primal work utilization (are assigned primals responding to their work?)

### P2 — Spring→NUCLEUS Integration

The user-level systemd deploy pattern is now proven on eastGate. Document and validate:
- `membrane-nucleus@.service` template pattern
- `songbird-federation.service` mesh relay
- Socket path alignment (user-level vs system-level)
- Graceful degradation when primals fail (`biomeos`, `nestgate` missing)

### P3 — Evolution Modules

Evolve internal primalSpring architecture as needed:
- Genetics compliance engine
- Composition validation against live gate state
- Mesh reachability scenarios (RTT thresholds, handshake freshness)

---

## What NOT to Touch

| Domain | Owner |
|--------|-------|
| cellMembrane code | sporeGate cellMembrane subteam |
| Gate enrollment (SSH, deploy) | sporeGate overwatch |
| Physical topology (Flint 2, cables) | sporeGate overwatch + operator |
| sporePrint content | flockGate team |
| VPS management (golgi, pepti) | sporeGate cellMembrane subteam |
| Cascade/blurb coordination | Overwatch (this chat) |

---

## Key Context

- **eastGate NUCLEUS**: 10 nucleus primals + songbird running as user systemd units. Missing `biomeos` (needs different CLI entrypoint) and `nestgate` (needs `NESTGATE_JWT_SECRET`). These are sporeGate team P1 — don't block on them.
- **Topology v5.0.0**: Three-hub triangle backbone. You validate the model; overwatch and sporeGate deploy it.
- **Sovereignty ledger**: New `sovereignty_ledger.rs` module in cellMembrane enables rootpulse commit/verify. primalSpring scenarios can validate the round-trip.
- **Wave 116 AAR**: sporeGate overwatch shipped comprehensive AAR documenting everything live, degraded, and blocked. Read it if you need full context: `wateringHole/handoffs/AAR_SPOREGATE_OVERWATCH_WAVE116_JUN18_2026.md`

---

## Commands

```bash
# Run tests
cargo test

# Run specific scenario file
cargo test --test scenarios -- <name>

# Check current NUCLEUS state
systemctl --user list-units 'membrane-nucleus@*' --no-pager

# Verify WG mesh
ping -c1 10.13.37.1  # golgi
ping -c1 10.13.37.2  # sporeGate
```

---

## Cascade Protocol

When you've made progress:
1. Commit to `primalSpring` (origin + forgejo)
2. Overwatch will pick it up on next cascade and update metrics

You do NOT need to update blurbs or FRAGOs — that's overwatch's job.
