# Wave 63 — River Delta: Springs + syntheticChemistry Temporal Sync

**Date**: May 30, 2026
**From**: primalSpring coordination (eastGate)
**To**: All spring teams (syntheticChemistry org)
**Phase**: River delta — springs onboard temporal sync, clear remaining debt

---

## Summary

Mountain primals are at zero debt. The river delta is where springs flow into the
ecosystem mesh. All 8 springs are in the `syntheticChemistry` GitHub org and currently
sync as **trailing mirrors** on Forgejo. This handoff brings each spring onto the
temporal sync, identifies remaining debt per spring, and advances the pseudoSpore
release pipeline.

All 11 syntheticChemistry Forgejo repos are currently **pull mirrors**. None are
bidirectional yet.

---

## Delta-Wide Actions (all springs)

### 1. Temporal Sync Tooling

Each spring needs the updated wateringHole for temporal sync support:

```bash
cd /path/to/ecoPrimals/infra/wateringHole
git pull origin main

# Verify cascade-pull.sh has --source temporal
./scripts/cascade-pull.sh --help | grep temporal
```

### 2. CONTEXT.md Drift

Three springs have dirty `CONTEXT.md` files (uncommitted local edits):
- **groundSpring**
- **ludoSpring**
- **neuralSpring**

Each team: review, commit, and push CONTEXT.md updates or discard if stale.

### 3. composition_nucleus.sh Debt

Three springs still have **active** `composition_nucleus.sh` bash scripts in `tools/`:
- **ludoSpring** (`tools/composition_nucleus.sh`)
- **neuralSpring** (`tools/composition_nucleus.sh`)
- **wetSpring** (`tools/composition_nucleus.sh`)

healthSpring and primalSpring already fossilized theirs. These scripts should be:
- Reviewed for relevance — if still used, they stay but should eventually evolve to Rust
- If superseded by `plasmidbin launch`, fossilize to `fossilRecord/`

### 4. pseudoSpore Domain Profiles

No spring has a `domain_profile.toml` yet. hotSpring's CompChem pseudoSpore (v1.6.1)
is the reference implementation. Each spring needs:

1. Write `domain_profile.toml` describing science modules
2. Run `litho emit-pseudospore --spring <name> --domain-profile ./domain_profile.toml`
3. Validate with `litho audit`
4. Promote to sporePrint

---

## Per-Spring Blurbs

### wetSpring (southGate) — Biology / Breseq / LTEE

**Last commit**: `67a856d` — Wave 60 stabilization, clippy zero warnings
**Gate**: southGate (pending NUCLEUS redeploy)
**Forgejo**: `syntheticChemistry/wetSpring` — pull mirror

**Status**: Clean. Zero clippy warnings. Cast safety hardened.

**Wave 63 tasks**:
- [ ] PG-02 / PG-04 live verification — needs stable southGate NUCLEUS
- [ ] pseudoSpore: Ferment transcript spore (Barrick 2009 SEALED, Tenaillon 2016 in-flight). Data exists, needs `domain_profile.toml`
- [ ] Review `tools/composition_nucleus.sh` — fossilize if plasmidbin-launched
- [ ] Temporal sync: once Forgejo mirror is converted to bidirectional, push from southGate

**Blocked by**: SouthGate NUCLEUS redeploy (ops, not code)

---

### neuralSpring (southGate) — ML / Structure Prediction

**Last commit**: `5b4fcc0` — Wave 55 southGate redeploy, loamSpine Tokio fix
**Gate**: southGate
**Forgejo**: `syntheticChemistry/neuralSpring` — pull mirror

**Known debt**:
- `scripts/validate_clean_machine.sh:96` — hardcoded `target/release/` primal paths
- `scripts/visualize.sh:54,68,75` — hardcoded `target/release/` binary paths
- `tools/composition_nucleus.sh` — active bash script, not fossilized
- Dirty `CONTEXT.md`

**Wave 63 tasks**:
- [ ] Fix `target/release/` hardcodes in `validate_clean_machine.sh` and `visualize.sh` — use `plasmidbin` paths or `which` discovery
- [ ] Review `tools/composition_nucleus.sh` — fossilize if plasmidbin-launched
- [ ] Commit CONTEXT.md updates
- [ ] Resolve loamSpine Tokio double-runtime crash workaround
- [ ] Squirrel provider registration
- [ ] pseudoSpore: Inference benchmark spore — needs `domain_profile.toml`

**Blocked by**: SouthGate NUCLEUS redeploy, loamSpine upstream Tokio bug

---

### hotSpring (biomeGate) — GPU Compute / CompChem

**Last commit**: `0b38ec5` — GAP-HS-109 resolved, DH-1 fixes documented
**Gate**: biomeGate (pending federation fix)
**Forgejo**: `syntheticChemistry/hotSpring` — pull mirror

**Status**: pseudoSpore DONE (v1.6.1, reference implementation).

**Wave 63 tasks**:
- [ ] BiomeGate: restart Songbird with `SONGBIRD_FEDERATION_PORT=7700` + `SONGBIRD_PEERS`
- [ ] Ionic cross-family GPU lease prototype (GAP-HS-005: `crypto.sign_contract`)
- [ ] Temporal sync validation after biomeGate comes online

**Blocked by**: BiomeGate Songbird federation restart

---

### healthSpring (ironGate) — Clinical / PK-PD

**Last commit**: `038777c` — 31 unit tests added, test count 1021→1052
**Gate**: ironGate (operational)
**Forgejo**: `syntheticChemistry/healthSpring` — pull mirror

**Status**: Clean. composition_nucleus.sh already fossilized.

**Wave 63 tasks**:
- [ ] BTSP `btsp.capabilities` probe pattern implementation
- [ ] pseudoSpore: Drug interaction model spore (PBPK curves + PD responses) — needs `domain_profile.toml`
- [ ] Temporal sync: pull from temporal leaders via updated cascade-pull.sh

---

### ludoSpring (ironGate) — Game Science

**Last commit**: `3f9dff7` — Wave 50 sync, all stale refs updated
**Gate**: ironGate (operational)
**Forgejo**: `syntheticChemistry/ludoSpring` — pull mirror

**Known debt**:
- Dirty `CONTEXT.md`
- `tools/composition_nucleus.sh` — active, not fossilized

**Wave 63 tasks**:
- [ ] 6 `game.*` methods for esotericWebb integration
- [ ] Review `tools/composition_nucleus.sh` — fossilize if plasmidbin-launched
- [ ] Commit CONTEXT.md updates
- [ ] pseudoSpore: Game telemetry spore (Fitts, WFC, engagement models) — needs `domain_profile.toml`

---

### airSpring (eastGate) — Agriculture / Atmospheric / ADS-B

**Last commit**: `bf9084c` — test count sweep 1057→1061, total 1442→1446
**Gate**: eastGate (operational)
**Forgejo**: `syntheticChemistry/airSpring` — pull mirror

**Status**: Clean.

**Wave 63 tasks**:
- [ ] AG-006 coralReef shader compile integration
- [ ] pseudoSpore: Soil dynamics spore (ET₀, diversity indices) — needs `domain_profile.toml`

---

### groundSpring (eastGate) — Geospatial / Measurement

**Last commit**: `a6dc8a0` — domain_profile.toml for lithoSpore LTEE emission
**Gate**: eastGate (operational)
**Forgejo**: `syntheticChemistry/groundSpring` — pull mirror

**Known debt**:
- Dirty `CONTEXT.md`

**Wave 63 tasks**:
- [ ] Squirrel composition integration
- [ ] Commit CONTEXT.md updates
- [ ] pseudoSpore: Uncertainty quantification spore (calibration datasets) — needs `domain_profile.toml`

---

### primalSpring (eastGate) — Coordination / Validation

**Last commit**: `62cb663` — waterFall temporal sync specification
**Gate**: eastGate (operational)
**Forgejo**: `syntheticChemistry/primalSpring` — pull mirror

**Status**: Clean. composition_nucleus.sh fossilized. 92 experiments, 56 scenarios.

**Wave 63 tasks**:
- [ ] Cross-gate `discovery.peers` smoke test (same-subnet: eastGate ↔ ironGate)
- [ ] Cross-gate `capability.call` smoke test (`s_covalent_mesh`)
- [ ] `exp115_nest_ingest_pseudospore` validation as springs emit spores
- [ ] Wire primalSpring validation to detect live upstream Neural API methods

---

## Forgejo Mirror Conversion Priority

syntheticChemistry repos to convert from pull mirror to bidirectional (by priority):

| Priority | Repo | Reason |
|----------|------|--------|
| 1 | primalSpring | Coordination spring, high sync priority |
| 2 | wetSpring | southGate primary, high sync priority |
| 3 | neuralSpring | southGate, high sync priority |
| 4 | hotSpring | biomeGate primary |
| 5-8 | airSpring, groundSpring, healthSpring, ludoSpring | Lower priority, pull-only gates |
| 9-11 | agentReagents, benchScale, rustChip | Tools, low priority |

Conversion is done via `membrane` CLI:
```bash
membrane repo.delete syntheticChemistry/<name>
membrane repo.create syntheticChemistry/<name>
git push forgejo main --force
```

---

## Success Criteria

- [ ] All 3 dirty CONTEXT.md files committed and pushed
- [ ] neuralSpring `target/release/` hardcodes fixed
- [ ] 3 active `composition_nucleus.sh` reviewed (fossilized or justified)
- [ ] At least 1 spring pseudoSpore emitted (wetSpring is closest: data exists)
- [ ] primalSpring + wetSpring + neuralSpring Forgejo repos converted to bidirectional
- [ ] SouthGate NUCLEUS redeployed (unblocks wetSpring + neuralSpring)
