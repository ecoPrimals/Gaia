# primalSpring Phase 32 — Atomic Model Evolution Handoff

**Date**: May 12, 2026
**Owner**: primalSpring (L2 stadial gate)
**Scope**: Tower atomic promotion of skunkBat + Nest reconciliation with provenance trio

---

## Summary

Phase 32 evolves the NUCLEUS atomic model to reflect the ecosystem's actual
composition patterns. Two structural drifts are resolved:

1. **skunkBat promoted to Tower** — defense is integral to the trust boundary,
   not an overlay. Every higher atomic inherits defense.
2. **Nest reconciled with graph fragments** — the Rust `AtomicType::Nest`
   now matches `nest_atomic.toml` (provenance trio, not Squirrel + ai).

## Changes

### Rust Code (`ecoPrimal/src/coordination/mod.rs`)

| AtomicType | Before | After |
|-----------|--------|-------|
| `Tower` | bearDog, songbird (2) | bearDog, songbird, **skunkBat** (3) |
| `Tower` capabilities | security, discovery | security, discovery, **defense** |
| `Node` | 5 primals | **6** primals (Tower 3 + compute trio) |
| `Node` capabilities | 5 caps | **6** caps (+ defense) |
| `Nest` | bearDog, songbird, nestGate, squirrel (4) | bearDog, songbird, **skunkBat**, nestGate, **rhizoCrypt, loamSpine, sweetGrass** (7) |
| `Nest` capabilities | security, discovery, storage, ai | security, discovery, **defense**, storage, **dag, ledger, attribution** |

602 library tests pass (all 30 coordination tests updated).

### Graph Fragments (v3.0.0)

All fragments updated: `tower_atomic.toml`, `node_atomic.toml`,
`nest_atomic.toml`, `nucleus.toml`. Node counts and ordering updated.

### Deployment Matrix

`config/deployment_matrix.toml` atomics updated for all tiers.

### New Documentation

- `docs/TEMPORAL_ECOSYSTEM_REVIEW_MAY12_2026.md` — full ecosystem temporal review
- `docs/LIVE_SCIENCE_API.md` — Tier 2 wire contract (toadstool.validate, list_workloads)
- `INTERSTADIAL_EXIT_CRITERIA.md` — Shadow Run Readiness Tracker added

### Updated Documentation

- `docs/PRIMAL_GAPS.md` — Wave 10 section, Wave 8 upstream progress
- `docs/CROSS_SPRING_PARITY_SCORECARD.md` — Phase 32 composition gap sweep,
  neuralSpring Nest decision, healthSpring BTSP coordination, foundation thread mapping
- `docs/COMPUTE_TRIO_EVOLUTION.md` — atomic table updated
- `graphs/fragments/README.md` — Tower 3-primal, counts updated
- `README.md` — header test counts, graph tables updated
- `CONTEXT.md` — status section updated for Phase 32

## Downstream Impact

Springs that compose Tower (all of them) now implicitly include skunkBat.
Deploy graphs that reference `tower_atomic` inherit the 3-primal definition.

**No spring code changes required** — skunkBat is `required = true` in the
fragment but already present in all 8 springs' deploy graphs (Wave 3 wiring).

## Next Steps

1. **toadStool Phase C** — highest-leverage upstream work (coral-driver absorption)
2. **Songbird `capability.resolve`** — unblocks name-based discovery debt
3. **Shadow runs** — BearDog TLS + lithoSpore Tier 1 startable in parallel
