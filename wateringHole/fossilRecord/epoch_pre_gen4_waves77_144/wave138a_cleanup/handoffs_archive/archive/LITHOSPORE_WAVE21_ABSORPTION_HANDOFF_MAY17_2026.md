<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# lithoSpore — Wave 21 Absorption Handoff

**Date**: 2026-05-17 PM
**From**: lithoSpore workstream (gardens/lithoSpore)
**For**: primalSpring audit, projectFOUNDATION, projectNUCLEUS, all spring/primal teams
**Context**: Absorbing Wave 21 garden evolution guidance from primalSpring

---

## Summary

lithoSpore absorbed the Wave 21 audit's lithoSpore-specific guidance.
All items addressed in code and documentation. 125 tests pass, zero
clippy warnings.

---

## What Was Absorbed

### 1. Wave 20 Canonical Schemas — ABSORBED

- `query_capabilities()` already conforms to `{ capabilities, count, primal }` envelope
- Added `PrimalListResponse` struct for `primal.list` canonical `{ primals, count }` shape
- Added `query_primal_list()` function using the canonical envelope
- 2 new unit tests validating Wave 20 envelope parsing

### 2. Method Stability Tiers — ABSORBED

`config/capability_registry.toml` updated:
- Header documents stability tier definitions (stable/evolving/internal)
- Every domain section annotated with `stability = "..."`:
  - `stable`: health, lifecycle, capabilities, discovery, ipc, visualization,
    dag, spine, braid, storage, crypto
  - `evolving`: compute (toadStool dispatch — may change with GPU evolution)
  - `internal`: test_fixtures
- Registry count updated from 451 (Wave 18) to 452 (Wave 20)
- Added `primal.list` to lifecycle methods

### 3. Degradation Behavior — DOCUMENTED

New `docs/DEGRADATION_BEHAVIOR.md`:
- Per-primal degradation matrix (9 primals × reachable/unreachable behavior)
- Discovery chain degradation sequence
- Provenance trio partial completion table aligned with
  `PROVENANCE_TRIO_INTEGRATION_GUIDE.md`
- Code references for all degradation paths

### 4. Partial Provenance — EVOLVED

`provenance.rs` `try_record_tier3()` rewritten:
- DAG is the only required primal (minimum for Tier 3)
- Spine and braid phases degrade gracefully with empty IDs
- `primals_reached` accurately tracks which primals responded
- Aligns with the ecosystem transaction semantics table:
  Full, DAG+spine, DAG-only, None — all valid states

### 5. ParityReport Standard — PUBLISHED

New `specs/PARITY_REPORT_SCHEMA.md`:
- Complete JSON schema with field definitions
- Parity status rules (MATCH/DIVERGENCE/SKIPPED)
- Rust type definitions for ecosystem consumers
- Adoption guide for other products (projectFOUNDATION barraCuda, airSpring)

### 6. Braid Ingestion Path — PREPARED

- Created `provenance/braids/` directory with `.gitkeep`
- `provenance/README.md` documents wire format and current state
- Standalone braids (empty trio IDs) accepted as structurally valid
- Ready to receive wetSpring Exp381 Barrick 2009 braids when 7/7 clones complete

### 7. Ecosystem Version Refs — UPDATED

- README: ecosystem posture section (452 methods, 9,539+ spring tests, Wave 21 context)
- capability_registry.toml: Wave 20 alignment
- Test count: 117 → 125 across all docs (post-chassis-abstraction evolution)

---

## Current State

| Metric | Value |
|--------|-------|
| Science checks | 75/75 |
| Unit/integration tests | 125 |
| Chaos tests | 10 |
| CLI subcommands | 15 |
| Clippy | Zero warnings |
| Stability tiers | All methods annotated |
| Degradation doc | Complete per-primal matrix |
| ParityReport schema | Published |
| Partial provenance | DAG-only valid, spine/braid optional |
| Braid ingestion | Directory ready, awaiting wetSpring Exp381 |

---

## What's NOT Addressed (Out of Scope for This Pass)

| Item | Status | Blocked By |
|------|--------|------------|
| Absorb wetSpring Exp381 braids | Awaiting 7/7 clones | wetSpring computation |
| cellMembrane geo-delocalized coordination | Future | cellMembrane Phase 1 Tower |
| Exercise `query_capabilities()` from CLI | Wired, not called from flow | Integration test opportunity |
| Exercise `query_primal_list()` from CLI | Wired, not called from flow | Integration test opportunity |

---

## Cross-References

- `LITHOSPORE_PRIMAL_SPRING_EVOLUTION_HANDOFF_MAY17_2026.md` — primal evolution requests
- `LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md` — braid contract
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — partial completion semantics
- `lithoSpore/specs/PARITY_REPORT_SCHEMA.md` — ecosystem parity standard
- `lithoSpore/docs/DEGRADATION_BEHAVIOR.md` — per-primal degradation matrix
