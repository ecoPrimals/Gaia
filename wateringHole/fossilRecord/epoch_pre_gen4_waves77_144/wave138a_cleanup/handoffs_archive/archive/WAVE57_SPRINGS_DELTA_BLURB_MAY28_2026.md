# Wave 57 Springs Delta Blurb — Deploy & Emit

**Date:** May 28, 2026
**From:** primalSpring coordination
**To:** All spring teams in the delta

---

## The Deploy Path Is Live

The ecosystem has converged. cellMembrane shipped the typed VPS standard and is
ready to deploy spring overlays. projectNUCLEUS has `--uds-only` for all 13
primals. The only blocker for spring emissions is biomeOS v3.81 on VPS.

**When biomeOS v3.81 lands on VPS, springs can begin column U passes.**

---

## VPS Deployment — 3 Steps (unchanged)

```
1. cellMembrane deploys NUCLEUS base (13 primals, UDS-only)
   → deploy_membrane.sh --composition nucleus --uds-only

2. cellMembrane deploys your spring overlay
   → deploy_membrane.sh spring-overlay root@<ip> --cell <yourspring>

3. Your spring runtime discovers primals via UDS
   → CompositionContext::from_live_discovery()
```

Your cell graph lives in `graphs/cells/<yourspring>_cell.toml` in primalSpring.
All 6 spring cells are tagged `vps_standard = true` and use `spawn = false`.

---

## Per-Spring Status & Priorities

### hotSpring — **FIRST EMITTER**

| Item | Status |
|------|--------|
| Cell graph `vps_standard` | **true** |
| Gate depth | Nest Atomic (biomeGate) |
| postPrimordial column U | **GATED** on biomeOS v3.81 VPS deploy |
| Priority | **P0**: prepare v1.6.1 ingest path for column U pass |

**You are the critical path for NC-5.** Once biomeOS v3.81 is on VPS, your
ingest through the Nest Atomic graph will be the first live pseudoSpore emission.
Prepare your `source_dir` content and domain profile.

### groundSpring — **SECOND EMITTER**

| Item | Status |
|------|--------|
| Cell graph `vps_standard` | **true** |
| Gate depth | Full NUCLEUS (eastGate) |
| postPrimordial column U | **GATED** on first pass + biomeOS VPS |
| Priority | **P1**: column U preparation after hotSpring proves the path |

Second data point for NC-5 universality. Your emission validates that the
pseudoSpore pipeline works for a second spring.

### wetSpring

| Item | Status |
|------|--------|
| Cell graph `vps_standard` | **true** |
| Gate depth | Node Atomic (southGate) |
| postPrimordial column U | **GATED** on southGate 13/13 stabilization |
| Priority | Stabilize southGate operations, prepare for column U |

southGate 7/13 health is likely a `SONGBIRD_PEERS` env or cold-start timing
issue, not a code bug. Coordinate with neuralSpring on ops.

### neuralSpring

| Item | Status |
|------|--------|
| Cell graph `vps_standard` | **true** |
| Gate depth | Node Atomic (southGate) |
| postPrimordial column U | **GATED** on southGate stabilization |
| Priority | Coordinate southGate ops with wetSpring |

### airSpring

| Item | Status |
|------|--------|
| Cell graph `vps_standard` | **true** |
| Gate depth | Full NUCLEUS (eastGate) |
| postPrimordial column U | Ready after first 2 emissions prove path |
| Priority | Low urgency — eastGate operational, path clear |

### healthSpring

| Item | Status |
|------|--------|
| Cell graph `vps_standard` | **true** |
| Gate depth | Full NUCLEUS (ironGate) |
| postPrimordial column U | Ready after first 2 emissions prove path |
| Priority | Low urgency — ironGate operational, path clear |

### ludoSpring

| Item | Status |
|------|--------|
| Cell graph `vps_standard` | **false** (spawn=true demo) |
| Gate depth | Full NUCLEUS (ironGate) |
| postPrimordial | Desktop-only, not on VPS standard path |
| Priority | No VPS action needed — desktop/demo spring |

---

## postPrimordial Checklist (Column U/V)

For springs preparing for column U passes:

- [ ] Cell graph exists in `graphs/cells/<spring>_cell.toml` with `vps_standard = true`
- [ ] `domain_profile.toml` prepared for lithoSpore emission
- [ ] `source_dir` content ready for pseudoSpore packaging
- [ ] `CompositionContext::from_live_discovery()` tested locally
- [ ] Health: `health.liveness` method responds correctly
- [ ] Spring binary in plasmidBin depot (via `plasmidbin harvest`)

---

## Timeline

```
NOW       → biomeOS v3.81 VPS deploy (cellMembrane action)
THEN      → hotSpring column U (first emission)
THEN      → groundSpring column U (second emission, NC-5 universality)
THEN      → NC-5 lithoSpore postPrimordial (2 emissions prove pipeline)
TARGET    → Stadial entry: NC-1(2+) + NC-2(3+) + NC-4(all 4 gates)
```

---

*Wave 57. Deploy path operational. cellMembrane ready. Springs: prepare to emit.*
