# Ecosystem Tightening Blurb — Wave 49

**Date**: May 25, 2026
**From**: primalSpring (eastGate / ironGate)
**To**: All 13 primals + springs
**Status**: Post-primordial — plasmidBin-only deployment enforced

---

## 1. Showcase Fossilization Directive

Eight primals have `showcase/` directories containing old atomic/NUCLEUS evolution
code that powered the journey from prokaryotic to post-primordial. That evolution
is complete. These directories now risk confusing new contributors and cluttering
the active codebase.

**Affected primals** (alphabetical):

| Primal | `showcase/` contents | Action |
|--------|---------------------|--------|
| barraCuda | Atomic composition demos, old bonding examples | Fossilize |
| bearDog | Security harness showcases, ACME proto demos | Fossilize |
| loamSpine | Soil analysis pipeline demos, old NestGate IPC | Fossilize |
| petalTongue | Neural API proto experiments, MCP tool demos | Fossilize |
| rhizoCrypt | Crypto primitive showcases, key rotation demos | Fossilize |
| skunkBat | Audio pipeline showcases, old spawn patterns | Fossilize |
| sweetGrass | Graph analysis demos, broken wateringHole refs | Fossilize + fix refs |
| toadStool | Registry showcases, old deploy pattern demos | Fossilize |

**Steps per primal**:

1. Archive `showcase/` contents to `ecoPrimals/fossilRecord/primals/<primalName>/showcase_wave49/`
2. Replace `showcase/` with a single `README.md` pointing to the fossil record location
3. Fix any broken path references (notably sweetGrass `showcase/` references a non-existent local `wateringHole/`)
4. Commit with message: `fossilize showcase/ — Wave 49 ecosystem tightening`

Primals without `showcase/` directories: no action needed.

---

## 2. wateringHole Consolidation Policy

**15 separate `wateringHole/` trees** exist across the ecosystem. This creates
confusion about which handoffs are authoritative and risks stale documentation
diverging from the central hub.

### Two-tier model (effective Wave 49):

| Tier | Location | Role |
|------|----------|------|
| **Hub** | `infra/wateringHole/` | Ecosystem-wide canonical handoffs, blurbs, and coordination docs. All cross-primal communication goes here. |
| **Spring coordination** | `primalSpring/wateringHole/` | Spring standards (METHOD_GATE, DEPLOYMENT_BEHAVIOR, etc.). Authoritative for spring coordination patterns. |
| **Per-repo local** | `<repo>/wateringHole/` or `<repo>/infra/wateringHole/` | Team-local fossil record only. Active handoffs MUST mirror to central `infra/wateringHole/handoffs/`. |

### Specific cleanup targets:

| Repo | `wateringHole/` path | Issue | Action |
|------|---------------------|-------|--------|
| agentReagents | `wateringHole/` | Stale since Mar 28 | Fold active content into repo README, archive remainder |
| benchScale | `wateringHole/` | Stale since Mar 28 | Fold active content into repo README, archive remainder |
| loamSpine | `infra/wateringHole/` | 13 handoffs, never mirrored to central | Mirror active handoffs to `infra/wateringHole/handoffs/`, archive local copies |
| toadStool | `infra/wateringHole/` | 36 handoffs, never mirrored | Mirror active handoffs to central, archive local copies |
| esotericWebb | `wateringHole/` | V3–V9 not archived per own policy | Archive per stated policy, retain only current |
| projectNUCLEUS | `infra/wateringHole/` | Stale since May 16 | Archive all; project NUCLEUS coordination now in central hub |
| neuralSpring | `infra/wateringHole/` | Wave 49 handoff duplicates central | Remove duplicate, reference central `infra/wateringHole/handoffs/` instead |

### Per-repo action:

1. Identify any active (non-superseded) handoffs in your local `wateringHole/`
2. Mirror them to `infra/wateringHole/handoffs/` with proper naming
3. Replace your local `wateringHole/` content with a `README.md` pointing to central
4. Archive old local handoffs to `fossilRecord/` if historically significant

---

## 3. Old Deployment Pattern Cut List

The post-primordial mandate (Wave 49) requires that all NUCLEUS primal binaries
come exclusively from `plasmidBin`. The following stale patterns still exist in
upstream repos and should be removed:

| Repo | File | Pattern | Action |
|------|------|---------|--------|
| neuralSpring | `tools/composition_nucleus.sh:396` | petalTongue `target/release/` fallback | Remove fallback; require plasmidBin-only |
| hotSpring | `scripts/validate-primal-proof.sh` | `target/release/hotspring_unibin` reference | Update to `plasmidBin/primals/hotspring` |
| Various springs | Assorted scripts | `target/release/` for spring-own UniBin | **Acceptable** for spring cell binaries (not primals). Document clearly. |

**Key distinction**: `target/release/` references for **primal** binaries (bearDog,
Songbird, toadStool, etc.) must be replaced with `plasmidBin/primals/` discovery.
`target/release/` references for **spring cell binaries** (the spring's own binary)
are acceptable — springs build and manage their own cell binaries independently.

See `primalSpring/wateringHole/PLASMIDBIN_DEPOT_PATTERN.md` for the canonical
discovery pattern and the "Spring Cell Binaries" section.

---

## 4. Broken Reference Fixes

| Repo | Issue | Fix |
|------|-------|-----|
| sweetGrass | `showcase/` references non-existent local `wateringHole/` | Fix paths or remove during fossilization |
| barraCuda | Stale `wateringHole/` cross-references in showcase | Fix paths or remove during fossilization |

---

## Verification Checklist

After completing your primal's tightening:

- [ ] No `showcase/` directory remains (or contains only a README pointer)
- [ ] Local `wateringHole/` active handoffs mirrored to `infra/wateringHole/handoffs/`
- [ ] No `which <primal>` or `target/release/<primal>` patterns for NUCLEUS primals in scripts
- [ ] All script binary discovery uses `plasmidBin/primals/` pattern
- [ ] Commit references Wave 49 ecosystem tightening

---

## Timeline

This is not urgent — primals should integrate these changes during their next
natural wave. The post-primordial deployment policy (plasmidBin-only) is already
enforced in `primalSpring` tooling; this blurb extends the tightening to the
broader ecosystem.

**Priority order**:
1. Old deployment patterns (security/correctness — prevents wrong binary execution)
2. wateringHole consolidation (prevents stale handoff confusion)
3. Showcase fossilization (cleanup — lowest urgency)
