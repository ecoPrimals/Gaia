# Wave 59 — Remaining Work to Stadial Entry

**Date:** May 28, 2026 (P0 resolved — NUCLEUS on VPS)
**From:** primalSpring coordination
**To:** All teams

---

## Ecosystem State

**P0 RESOLVED.** cellMembrane deployed NUCLEUS to VPS — 13/13 primals active
on UDS sockets, 57s deploy, zero new firewall ports. Spring overlay test
validated (hotSpring cell graph 14 nodes parsed). biomeOS `graph.execute`
gated on v0.2. bearDog refreshed PRIMAL_CONTRACTS (127→223 methods),
NC-3.5 `auth.issue_session` scope resolved. lithoSpore wired derivation
anchoring (GUIDESTONE-GRADE items 11-14, 192 tests).

**Strategy shift:** Delay all springs except wet/neuralSpring. southGate
becomes the concentrated pattern node — stabilize it to 13/13, prove the
membrane-to-spring patterns, then hand off to other springs. This tightens
the wave focus.

---

## What's Done (no further action needed)

| Item | Owner | Wave |
|------|-------|------|
| **NUCLEUS deployed to VPS (P0)** | **cellMembrane** | **59** |
| Spring overlay graph validated (hotSpring cell) | cellMembrane | 59 |
| NUCLEUS composition typed (175 tests, 17 services) | cellMembrane | 59 |
| NC-1 code: `biomeos-pseudospore` + emit materialization | biomeOS | 57 |
| biomeOS env centralization: `env_config` module (90+ literals) | biomeOS | 58b |
| VPS deployment standard: `--uds-only`, TransportMode, spring overlays | cellMembrane | 56 |
| cellMembrane deep debt: 95.8% coverage, typed errors, licensing | cellMembrane | 57 |
| Deploy scripts: all 13 primal `--uds-only` + socket health | projectNUCLEUS | 58 |
| projectNUCLEUS: async-correct, wire-native discovery, 166 tests | projectNUCLEUS | 58 |
| projectFOUNDATION: Rust elevation Phase B (5 crates) | projectFOUNDATION | 58b |
| lithoSpore: derivation anchoring (GUIDESTONE-GRADE 11-14), 192 tests | lithoSpore | 59 |
| bearDog: PRIMAL_CONTRACTS v4.0 (223 methods), NC-3.5 scope resolved | bearDog | 118 |
| Env var centralization (8 primals pushed by primalSpring) | primalSpring coord | 57b |
| bearDog: `env_keys.rs` (290 constants), orphan purge (21 files) | bearDog | 117b |
| songbird: `songbird-process-env` full adoption, 146 `#[expect` | songbird | 58 |
| squirrel: 316 env constants, self-identity eliminated, 5,417L purge | squirrel | 58 |
| primalSpring: dispatch telemetry, doc alignment, glacial review | primalSpring | 58b-59 |
| Port SSOT reconciliation | cellMembrane + primalSpring | 56 |
| Wire-native newline JSON-RPC discovery | projectNUCLEUS | 58 |

---

## What Remains — Ordered by Critical Path

### P0b: biomeOS Orchestration (blocks column U)

| Action | Owner | Blocker |
|--------|-------|---------|
| biomeOS `graph.execute` over UDS (currently v0.1.0, parse-only) | biomeOS | Code evolution (v0.2) |
| `FAMILY_ID` in `tower.env` (biomeOS runs standalone mode without it) | cellMembrane ops | Config update |
| toadStool `--socket /run/membrane/toadstool.sock` (currently `/tmp/`) | toadStool | Env debt |

### P1: southGate as Pattern Node (concentrated focus)

| Action | Owner | Blocker |
|--------|-------|---------|
| southGate redeploy from fresh plasmidBin (7→13/13 health) | wetSpring/neuralSpring ops | Primal binaries + SONGBIRD_PEERS |
| wet/neuralSpring membrane patterns proven on southGate | wetSpring + neuralSpring | southGate 13/13 |
| Live `s_covalent_mesh` eastGate ↔ ironGate ↔ southGate | primalSpring | southGate health |
| Pattern documentation for other springs | primalSpring | Patterns proven |

### P2: Gate Stabilization (stadial NC-2/NC-4)

| Action | Owner | Blocker |
|--------|-------|---------|
| biomeGate 9→13/13 primals | hotSpring ops | Primal binaries |
| Dark Forest re-audit with 13 primals on VPS | cellMembrane | Post-deploy |
| Provenance pipeline re-validation (was 10/10 with 7) | cellMembrane | Post-deploy |

### P3: Column U Emissions (after patterns proven)

| Action | Owner | Blocker |
|--------|-------|---------|
| wet/neuralSpring column U on southGate (first emission) | wetSpring + neuralSpring | P1 |
| hotSpring column U on biomeGate (second emission) | hotSpring | P2 + biomeOS v0.2 |
| Remaining springs column U (pattern handoff) | spring teams | P1 patterns |

### P4: Sovereignty Completion (progressive)

| Action | Owner | Blocker |
|--------|-------|---------|
| NS registrar cutover (NC-3.3) | cellMembrane + registrar | External |
| Forgejo releases (NC-3.4) | cellMembrane + plasmidBin | Forgejo config |
| ~~sporePrint living content (NC-3.5)~~ | ~~cellMembrane + petalTongue~~ | **UNBLOCKED** (bearDog W118) |

### P5: Remaining Primal Debt (non-blocking)

| Primal | Status | Remaining |
|--------|--------|-----------|
| squirrel | **IN PROGRESS** | ~93 files raw `std::env::var`. SDK config layer next. |
| toadStool | **PENDING** | ~200 env sites + socket path debt (VPS `--socket` flag) |

---

## VPS Observations (from cellMembrane Experiment 001)

| Finding | Impact | Fix Owner |
|---------|--------|-----------|
| toadStool binds `/tmp/biomeos/` not `/run/membrane/` | Socket discovery fragmented | toadStool (env debt) |
| biomeOS `graph.execute` not implemented v0.1.0 | Spring overlays parse but don't orchestrate | biomeOS |
| `FAMILY_ID` not in `tower.env` | biomeOS runs standalone, not family mode | cellMembrane ops |
| coralReef stderr on `--version` | Cosmetic only | coralReef |
| `nucleus_launcher` not in releases | Preferred deploy path unavailable | plasmidBin |

---

## Stadial Entry Criteria (updated)

```
NC-1: 2+ springs pass column U        → GATED on P0b + P1/P3
NC-2: 3+ gates meshed                  → GATED on P1 (southGate focus)
NC-4: all 4 named gates healthy        → GATED on P1 + P2
NC-3: partial satisfaction sufficient   → ADVANCING (NC-3.5 unblocked)
NC-5: progressive after column U       → UNBLOCKED (derivation anchoring wired)
```

**Critical path shifted**: ~~P0 deploy~~ → **P0b orchestration** (biomeOS `graph.execute`) →
**P1 southGate pattern node** (wet/neuralSpring) → P3 emissions → stadial candidate.

---

*Wave 59. NUCLEUS on VPS. Focus the wave. Prove the patterns on southGate.*
