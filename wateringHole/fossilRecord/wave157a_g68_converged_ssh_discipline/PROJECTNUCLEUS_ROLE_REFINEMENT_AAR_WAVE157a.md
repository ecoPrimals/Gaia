# projectNUCLEUS Role Refinement — AAR

**Date**: 2026-08-08 | **Wave**: 157a | **Gate**: ironGate code team
**Classification**: Architectural refinement — scope reduction

---

## Summary

projectNUCLEUS scope refined from 5 concerns to 3. Historical residue from
the atomics evolution phase (gen3→gen4, ~May 2026) identified and marked for
handoff to upstream owners. README updated. Handoff tracking documents placed
in each affected directory.

## What Changed

### Refined Scope (3 concerns, down from 5)

1. **Gate deployment** — `nucleus-deploy` CLI (CORE, no replacement exists)
2. **Security validation** — `darkforest` adversarial auditor (CORE)
3. **Tunnel sovereignty** — `tunnelKeeper` CF→Songbird transition (TRANSITIONAL)

### What Was Removed from Active Scope

| Component | Classification | Target Owner | Action Taken |
|-----------|---------------|--------------|-------------|
| `workloads/` (43 TOMLs, 8 springs) | PENDING HANDOFF | Spring repos / primalSpring | `workloads/HANDOFF.md` filed |
| `docs/BONDING_MODELS.md` | PENDING HANDOFF | wateringHole foundations | `docs/HANDOFF.md` filed |
| `docs/FAMILY_HPC_MODEL.md` | PENDING HANDOFF | wateringHole foundations | `docs/HANDOFF.md` filed |
| `whitePaper/baseCamp/` | PENDING HANDOFF | primalSpring docs | `whitePaper/HANDOFF.md` filed |
| `notebooks/` template | PENDING HANDOFF | primalSpring notebooks | `notebooks/HANDOFF.md` filed |
| `deploy/pappuscast/` + `observer_server.py` | DEPRECATED | sporePrint / biomeOS | `pappuscast/DEPRECATED.md` filed |
| `deploy/legacy/` (16 bash scripts) | FOSSILIZED | fossilRecord | `legacy/FOSSILIZED.md` filed |

### Specs Audit (23 documents)

- **15 KEEP**: NUCLEUS-specific operational docs (validation results, baselines, security)
- **5 MIGRATE**: Normative ecosystem standards → wateringHole (`TRANSPORT_MATRIX`, `COMPOSITION_CONTRACT`, `EXECUTION_MODEL`, `PROVENANCE_CONTRACT`, `INVISIBILITY_STANDARD`)
- **3 FOSSILIZE**: Completed snapshots (`DARKFOREST_OUTER_MEMBRANE_REPORT`, `COMPLETE_DEPENDENCY_INVENTORY`, specs README update)

Full classification in `specs/AUDIT.md`.

### Transitional Components

| Component | Condition for Archive |
|-----------|----------------------|
| `tunnelKeeper` | Songbird cutover complete (H2-16 per `TUNNEL_EVOLUTION.md`) |
| `nucleus-primals` registry | Converged with primalSpring upstream or auto-generated |
| `nucleus_config.sh` | Converged with nucleus-primals Rust registry |

## Overwatch Action Required

### Phase 2 — Cross-Repo Migrations (overwatch coordination)

1. **Spring repo maintainers**: Absorb workload TOMLs from `projectNUCLEUS/workloads/`
2. **wateringHole**: Accept 5 normative specs + 2 architectural model docs
3. **primalSpring**: Accept `baseCamp/` validation methodology + notebook template
4. **fossilRecord**: Accept `deploy/legacy/` archive
5. **sporePrint**: Confirm observer surface absorption (replaces pappusCast)

### Tier 3 — Primal Wire Evolution (overwatch tasking)

These require federation maturity and are longer-term:

- `nucleus-deploy` direct spawn → converge to `--graph-deploy` default (biomeOS `composition.deploy`)
- SSH-based remote probes → songBird federation RPC (as coverage expands)
- `tunnelKeeper` CF ops → archive after Songbird cutover

## Files Modified in projectNUCLEUS

| File | Change |
|------|--------|
| `README.md` | Refined scope, handoff status table, deprecated pappusCast section, updated wave stamp |
| `workloads/HANDOFF.md` | NEW — migration targets for 43 spring workload TOMLs |
| `docs/HANDOFF.md` | NEW — architectural models → wateringHole tracking |
| `whitePaper/HANDOFF.md` | NEW — baseCamp → primalSpring tracking |
| `notebooks/HANDOFF.md` | NEW — template → primalSpring tracking |
| `deploy/pappuscast/DEPRECATED.md` | NEW — deprecation notice + migration path |
| `deploy/legacy/FOSSILIZED.md` | NEW — fossilization notice + replacement mapping |
| `specs/AUDIT.md` | NEW — 23-spec classification (15 keep, 5 migrate, 3 fossilize) |

## What projectNUCLEUS Focuses On Now

1. **Stop evolving** pappusCast, observer Python, workload TOMLs, bonding docs
2. **Focus evolution on** nucleus-deploy ops, darkforest coverage, graph-deploy convergence
3. **Contribute upstream** — nucleus-primals drift fixes → primalSpring, normative specs → wateringHole
4. **Track tunnel cutover** — tunnelKeeper stays but shrinks as Songbird matures

---

*Filed by ironGate code team. Wave 157a role refinement — from 5 concerns to 3.*
