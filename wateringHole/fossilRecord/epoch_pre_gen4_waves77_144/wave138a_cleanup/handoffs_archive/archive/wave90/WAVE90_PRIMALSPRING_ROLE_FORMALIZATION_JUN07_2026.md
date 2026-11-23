# Wave 90: primalSpring Role Formalization

**Date**: 2026-06-07
**From**: eastGate overwatch
**To**: cellMembrane, projectNUCLEUS, all teams

---

## Summary

primalSpring's identity has been formalized as the **composition experimentation
laboratory**. The three-tier deployment chain is now the canonical model:

| Tier | Component | Responsibility |
|------|-----------|----------------|
| 1 | primalSpring | Experiment, validate, certify composition patterns |
| 2 | cellMembrane | Deploy validated patterns, manage plasmidBin depot, VPS ops |
| 3 | projectNUCLEUS | Package patterns as polished agnostic deployment product |

## What Changed

### Documentation
- `CONTEXT.md` — explicit ownership boundaries, three-tier consumption model
- `README.md` — cleaned stale references (scripts, tools, counts), reflects
  post-deep-debt-sprint reality (5 lab scripts, 1 deprecated tool, 931 tests)
- Module doc headers — `launcher/`, `deploy/`, `harness/`, `nucleus_launcher`
  all carry explicit ownership notes

### Downstream Consumption
- `specs/DOWNSTREAM_CONSUMPTION.md` — defines what projectNUCLEUS depends on:
  library crate (`composition`, `coordination`, `certification`, `deploy`, etc.),
  graph artifacts (`cells/`, `fragments/`, `compositions/`), config schema
  (`capability_registry.toml`, `primal_launch_profiles.toml`), and certification
  as quality gate (`primalspring certify --bare` is a hard gate)

### Handoffs and FRAGOs
- Wave 89 handoffs fossilized to `archive/wave89/`
- GLACIAL_SHIFT_READINESS.md updated with three-tier model, all P1 deployment
  blockers marked RESOLVED, critical path updated
- wave84-temporal-inner-membrane-adoption FRAGO updated with Wave 90 three-tier
  formalization

## For cellMembrane Team

primalSpring role formalized — deployment patterns validated, ready for
projectNUCLEUS downstream absorption. cellMembrane continues to own:
- plasmidBin depot (harvest, refresh, trigger)
- VPS deployment (systemd units, Caddy, membrane ops)
- Binary evolution pipeline

The `specs/DOWNSTREAM_CONSUMPTION.md` in primalSpring defines the stable
interface contract. projectNUCLEUS consumes the composition library and
certification engine from primalSpring; cellMembrane deploys the results.

## For projectNUCLEUS Team

Your consumption surface is now documented in `primalSpring/specs/DOWNSTREAM_CONSUMPTION.md`.
Key items:
- Depend on `primalspring` crate for composition validation, coordination types, certification
- Run `primalspring certify --bare` as a **hard gate** in CI
- Own your routing config instances, workload TOMLs, deploy automation, UX polish
- File gaps back to primalSpring's `docs/PRIMAL_GAPS.md` when integration reveals issues
