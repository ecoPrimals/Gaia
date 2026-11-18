# Wave 58 Springs Delta Blurb — Deploy & Emit

**Date:** May 28, 2026
**From:** primalSpring coordination
**To:** All spring teams

---

## Ecosystem Ready. Awaiting v3.84 Deploy.

cellMembrane: 95.8% coverage, typed errors, VPS standard live.
projectNUCLEUS: 166 tests, async-correct, wire-native discovery.
primalSpring: 797 tests, zero debt, env vars centralized across 8 primals.

**The only blocker for spring emissions is biomeOS v3.84 on VPS.**

---

## VPS Deployment — 3 Steps

```
1. cellMembrane deploys NUCLEUS base (13 primals, UDS-only)
   → deploy_membrane.sh --composition nucleus --uds-only

2. cellMembrane deploys your spring overlay
   → deploy_membrane.sh spring-overlay root@<ip> --cell <yourspring>

3. Your spring runtime discovers primals via UDS
   → CompositionContext::from_live_discovery()
```

Cell graphs: `graphs/cells/<yourspring>_cell.toml` in primalSpring.
All 6 spring cells: `vps_standard = true`, `spawn = false`.

---

## Per-Spring Priorities

| Spring | Gate | Priority | Status |
|--------|------|----------|--------|
| **hotSpring** | biomeGate (Nest Atomic) | **P0 — first emitter** | GATED on v3.84 deploy |
| **groundSpring** | eastGate (Full NUCLEUS) | **P1 — second emitter** | GATED on first pass |
| wetSpring | southGate (Node Atomic) | P2 | GATED on southGate 13/13 |
| neuralSpring | southGate (Node Atomic) | P2 | GATED on southGate 13/13 |
| airSpring | eastGate (Full NUCLEUS) | P3 | Ready after first 2 emissions |
| healthSpring | ironGate (Full NUCLEUS) | P3 | Ready after first 2 emissions |
| ludoSpring | ironGate (desktop-only) | — | Not on VPS path |

---

## Column U Checklist

- [ ] Cell graph exists with `vps_standard = true`
- [ ] `domain_profile.toml` prepared for lithoSpore emission
- [ ] `source_dir` content ready for pseudoSpore packaging
- [ ] `CompositionContext::from_live_discovery()` tested locally
- [ ] `health.liveness` responds correctly
- [ ] Binary in plasmidBin depot (`plasmidbin harvest`)

---

## Timeline

```
NOW    → biomeOS v3.84 VPS deploy (cellMembrane)
THEN   → hotSpring column U (first emission)
THEN   → groundSpring column U (NC-5 universality)
THEN   → lithoSpore postPrimordial (pipeline proven)
TARGET → Stadial: NC-1(2+) + NC-2(3+) + NC-4(all 4 gates)
```

---

*Wave 58. Infrastructure converged. Springs: prepare to emit.*
