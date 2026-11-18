# primalSpring Wave 75 — Evolution Sprint Handoff

**Date**: 2026-06-03  
**Author**: eastGate — primalSpring evolution  
**Status**: Complete  
**Version**: 0.9.31  
**Tests**: 851 lib + 10 integration + 18 doc = 879 total (zero failures)

---

## Delivered

### Cross-Gate Trust Validation (P0)

- **s_covalent_mesh 6-phase trust** — Phase 4 (Security: BTSP token
  issue/verify/cross-gate/forged/scopes), Phase 5 (Content: BLAKE3
  put/get/replicate), Phase 6 (Dark Forest: port isolation, UDS-only,
  reversibility).
- **Gen5 paper COVALENT_MESH_TRUST_VALIDATION.md** — Phases 3-6 IMPLEMENTED.
- **LiveMeshConfig** — validation infrastructure for live cross-gate testing
  (env parsing, connectivity checks, authenticated call builders, BTSP readiness).

### Evolution Sprint

- **s_covalent_mesh refactored** — 909L→346L. Trust phases extracted to
  `covalent_mesh_trust.rs` (smart domain split, not arbitrary).
- **Identity-mode retired** — last production use of deprecated
  `required_primals()` removed from handlers.
- **Orchestrator fallback removed** — `ordered_primals()` proven resolves
  all capabilities via new `all_caps_resolve_to_primals` test.
- **MeshTopology wired into CompositionContext** — `set_mesh()`, `mesh()`,
  `resolve_cross_gate()` for Layer 3 cross-gate resolution.
- **Handlers elevated to Tier 1** — all use `CompositionContext::discover()`
  (full Songbird escalation).
- **Handler consolidation** — `validate_composition_by_capability` delegates
  to `validate_composition`. `handle_probe_primal` accepts `capability` param.
- **Perceptron pipeline** — telemetry→extraction→ml.mlp_train→weights.
- **Plasmodium evolved** — 3-gate ironGate routing + MeshTopology composition.

### Quality Bar

| Metric | Value |
|--------|-------|
| Tests | 851 lib + 10 integration + 18 doc |
| Clippy | Zero warnings (pedantic + nursery) |
| Unsafe | Zero (forbid on all crate roots) |
| Files >800L | Zero |
| `#[allow]` | Zero in production |
| Mocks in prod | Zero |
| C deps | Zero |
| Runtime deps | 16 (pure Rust) |

---

## Deprecated Surface (remaining — harness only)

| Item | Status | Removal Gate |
|------|--------|--------------|
| `AtomicHarness` / `RunningAtomic` | Deprecated 0.9.25 | Integration tests migrate to ecoBin |
| `CompositionContext::from_running` | Bridge only | Removed with harness |
| `required_primals()` | Deprecated 0.9.31 | Tests + harness only consumers now |
| `substrate_primal()` | Deprecated 0.9.31 | Tests only |
| `spawn_primal` / `spawn_biomeos` | Deprecated 0.9.25 | Harness only |
| `from_live_discovery_with_fallback` | Valid but inferior | Constructor only; zero callers |

---

## Upstream Gaps (primalSpring perspective)

### P0 — Blocks Live Cross-Gate Validation

| Gap | Owner | Status |
|-----|-------|--------|
| Capability propagation in `discovery.peers` | Songbird | FRAGO active (w76) |

### P1 — Blocks Full Trust Loop

| Gap | Owner | Status |
|-----|-------|--------|
| `verification_source` param in `auth.verify_ionic` | bearDog | Expected w135+ |
| `content.stat` for reversibility validation | NestGate | Expected s90+ |

### P2 — Nice to Have

| Gap | Owner | Status |
|-----|-------|--------|
| `compute.dispatch.submit` trust model | toadStool | In progress (S286) |
| `bonding.status` routing gap | biomeOS | Open |

---

## Next Wave Priorities

1. **Live cross-gate validation** — When Songbird ships capability propagation,
   run `s_covalent_mesh` Phase 3 live and validate end-to-end `capability.call`.
2. **3-gate plasmodium** — ironGate added to SONGBIRD_PEERS, verify 3-way routing.
3. **Perceptron weights deployment** — Run pipeline against real
   `dispatch_telemetry.jsonl`, deploy `.bin` to biomeOS `XDG_DATA_HOME`.
4. **Harness retirement prep** — Migrate integration tests from `AtomicHarness`
   to ecoBin + `CompositionContext::discover()`.
