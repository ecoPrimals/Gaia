# Wave 56 Springs Delta Blurb — NUCLEUS VPS Deployment & postPrimordial

**Date:** May 27, 2026
**From:** primalSpring coordination
**To:** All spring teams in the delta

---

## The Path Forward

The mountain is clean (13/13 primals, zero debt). primalSpring has shipped the
VPS deployment standard with tooling. Your springs can now deploy from the
cellMembrane VPS via `plasmidBin` and begin evolving toward postPrimordial.

This blurb tells each spring team exactly what to do.

---

## For All Springs: VPS Deployment in 3 Steps

Your cell graph is ready in `primalSpring/graphs/cells/{spring}_cell.toml`.
All VPS-standard cell graphs use `spawn=false` — they overlay onto a running
NUCLEUS provisioned by cellMembrane, not self-spawn.

```
Step 1:  cellMembrane provisions NUCLEUS base on VPS (UDS-only, 13 primals)
Step 2:  biomeos deploy graphs/cells/{yourspring}_cell.toml
Step 3:  Your spring connects via CompositionContext::from_live_discovery()
```

No shell scripts. No TCP ports. No desktop symlinks.

### What You Need

| Requirement | How |
|-------------|-----|
| plasmidBin binaries on VPS | Pre-populated by cellMembrane image or `plasmidbin fetch` |
| Your spring binary in plasmidBin | Build via `plasmidbin harvest` or GitHub Release |
| Running NUCLEUS on target gate | cellMembrane `deploy_membrane.sh --composition nucleus` |
| Your cell graph | Already exists in `primalSpring/graphs/cells/` |

### What You Do NOT Need

- No changes to primalSpring
- No shell scripts
- No TCP port allocation
- No harness or `spawn_primal` — those are deprecated

---

## Per-Spring Status & Actions

### hotSpring (biomeGate — qcd_physics)

| Item | Status | Action |
|------|--------|--------|
| Cell graph | `hotspring_cell.toml` — **VPS ready** (`spawn=false`) | Deploy via `biomeos deploy` |
| Gate depth | 9/13 primals | Elevate to full NUCLEUS (hardware: HBM2 capacity) |
| postPrimordial | **First target** for pseudoSpore v1.6.1 ingest via NUCLEUS | Gated on v3.81 VPS deploy + live Nest Atomic on biomeGate |
| Validation matrix | Column U **GATED** | Will be first spring to pass when NC-1 goes live |

**Priority:** Get biomeGate to 13/13 primals, then run first live spore ingest when v3.81 is deployed to VPS.

---

### wetSpring (southGate — biology)

| Item | Status | Action |
|------|--------|--------|
| Cell graph | `wetspring_cell.toml` — **VPS ready** | Deploy via `biomeos deploy` |
| Gate depth | **7/13 health** | Stabilize — investigate Songbird crashes, BearDog timeout, biomeOS socket |
| postPrimordial | Planned (Tenaillon 2016: 264 clones, 590 GB) | After gate stabilization |
| Validation matrix | Column U **planned** | Natural second data point after hotSpring |

**Priority:** Stabilize southGate to 13/13 health. This is ops work — Songbird TCP seed bug is fixed upstream; likely env vars (`SONGBIRD_PEERS`), OOM, or cold-start timing on your end.

---

### neuralSpring (southGate — inference)

| Item | Status | Action |
|------|--------|--------|
| Cell graph | `neuralspring_cell.toml` — **VPS ready** | Deploy via `biomeos deploy` |
| Gate depth | **7/13 health** (shares southGate with wetSpring) | Joint stabilization with wetSpring |
| postPrimordial | Planned | After gate stabilization |
| Multi-GPU | Required (`NC-4` matrix) | Node Atomic + multi-GPU compute |

**Priority:** Joint southGate stabilization with wetSpring. Once 13/13, run `s_covalent_mesh` across gates.

---

### airSpring (eastGate — weather/agriculture)

| Item | Status | Action |
|------|--------|--------|
| Cell graph | `airspring_cell.toml` — **VPS ready** | Deploy via `biomeos deploy` |
| Gate depth | Full NUCLEUS — **operational** | No action needed |
| postPrimordial | Planned | When NC-1 goes live |

**Priority:** You're operational. Begin testing VPS deployment via cellMembrane when ready. Column U when NC-1 lands.

---

### groundSpring (eastGate — geology/uncertainty)

| Item | Status | Action |
|------|--------|--------|
| Cell graph | `groundspring_cell.toml` — **VPS ready** | Deploy via `biomeos deploy` |
| Gate depth | Full NUCLEUS — **operational** | No action needed |
| postPrimordial | **Second target** for pseudoSpore ingest | lithoSpore LTEE modules exist; natural second data point |
| Validation matrix | Column U **GATED** | After hotSpring proves the path |

**Priority:** Operational. Natural second spring for column U once hotSpring demonstrates the pattern.

---

### healthSpring (ironGate — health)

| Item | Status | Action |
|------|--------|--------|
| Cell graph | `healthspring_cell.toml` — **VPS ready** | Deploy via `biomeos deploy` |
| Gate depth | Full NUCLEUS — **operational** | No action needed |
| postPrimordial | Planned | After NC-1 |
| Special needs | NestComposition facade, dual tower + enclave topology | When ready |

**Priority:** Operational. NestComposition facade when you're ready; no urgency.

---

### ludoSpring (ironGate — game science)

| Item | Status | Action |
|------|--------|--------|
| Cell graph | `ludospring_cell.toml` — **desktop-only** (`spawn=true`) | Needs normalization to `spawn=false` for VPS |
| Gate depth | Full NUCLEUS — **operational** | No action needed |
| postPrimordial | Game telemetry pseudoSpore (theoretical) | Low priority |
| Special needs | coralReef IPC gap (GAP-01) | When coralReef team is ready |

**Priority:** Normalize `ludospring_cell.toml` to `spawn=false` for VPS deployment. Currently desktop-only.

---

### esotericWebb (ironGate — crpg)

| Item | Status | Action |
|------|--------|--------|
| Cell graph | `esotericwebb_cell.toml` — **mixed spawn flags** | Needs normalization for VPS |
| Gate depth | Operational | No action needed |
| postPrimordial | Low priority | Domain-specific |

**Priority:** Normalize spawn flags when convenient. Not blocking anything.

---

## The postPrimordial Checklist (For Every Spring)

When your gate is healthy and NC-1 is live, your spring becomes postPrimordial by:

1. **Emit** a pseudoSpore via `litho emit-pseudospore --spring {yourspring}`
2. **Ingest** via `biomeos nucleus ingest` (not the old `litho ingest-pseudospore`)
3. **Provenance trio signs** the ingestion (rhizoCrypt + loamSpine + sweetGrass)
4. **sweetGrass braid** links spring origin + storage CID + trio session
5. **plasmidBin checksums** carry Layer 2 composite fingerprint

Column U passes when your spring completes steps 1-3.
Column V passes when provenance trio is verified end-to-end.

---

## Timeline

```
NOW          → Deploy from VPS via biomeos deploy (all VPS-ready springs)
NC-1.4       → RESOLVED (v3.81) — deploy to VPS is remaining gate
NC-1 live    → hotSpring first column U pass
After NC-1   → groundSpring second column U pass → stadial gate criterion
NC-2         → 3+ gates meshed (southGate stabilization required)
Stadial      → NC-1 (2+ springs) + NC-2 (3+ gates) + NC-4 (all 4 gates healthy)
```

---

*Your cell graphs are ready. The VPS contract is documented. Deploy and evolve.*
