# primalSpring Wave 139a — Upstream Handoff

**Date**: 2026-07-14 | **Wave**: 139a | **From**: eastGate primalSpring overwatch
**Posture**: 156 SCENARIOS ACTIVE. 1,174 tests. 1 known-debt (graphenegate-readiness:1).

---

## What Happened

Wave 139a cascaded from VPS with zero code debt. primalSpring on eastGate:
1. Re-enabled 22 scenarios (VPS health restore had re-commented them)
2. Cleared 2 debt items — `cascade-provenance-match` (0 fail) and `bootstrap-readiness` (0 fail)
3. Added 2 new scenarios targeting 139a scope
4. Resolved merge conflicts with upstream's `s_drawbridge_bond_registry` addition

## Changes

| What | Detail |
|------|--------|
| Re-enabled 22 scenarios | All compile and pass on eastGate |
| New: `s_depot_layout_compliance` | Validates plasmidBin standard: 13/13 NUCLEUS primals, musl-static, checksums, provenance verify |
| New: `s_soundstage_ceremony_observation` | Validates soundStage↔FIDO2 ceremony integration — channels, sessions, comparator, quality gates, NAPI routing |
| Debt cleared | `cascade-provenance-match` (was 2→0), `bootstrap-readiness` (was 1→0) |
| `EXPECTED_SCENARIO_COUNT` | 143 → 156 |
| `KNOWN_DEBT` | Only `graphenegate-readiness:1` remains |
| Integrated upstream | `s_drawbridge_bond_registry` from parallel session |

## New Scenarios Detail

### `s_depot_layout_compliance` (Track: Sovereignty)

Validates the divergence exposed in Wave 139a blurb (genomeBin 6/14 primals, dynamically linked):
- Phase 1: 13/13 NUCLEUS primal coverage in registry
- Phase 2: Manifest structure (versioning, architecture targeting)
- Phase 3: Static linkage enforcement (musl-static, reject dynamic)
- Phase 4: Trust artifacts (checksums, provenance verify, BLAKE3, Ed25519)
- Phase 5: Architecture completeness (x86_64 + aarch64)

### `s_soundstage_ceremony_observation` (Track: Security)

Bridges the soundStage transparency concept with the FIDO2 ceremony path:
- Phase 1: Channel per anchor type (FIDO2, StrongBox, Audio, OS)
- Phase 2: Session captures full ceremony (request/response/contribution)
- Phase 3: LiveCapture thread-safe observation (Arc<Mutex>)
- Phase 4: Comparator proves key independence across sessions
- Phase 5: Quality gates reject single-source and degenerate entropy
- Phase 6: Neural API routing for ceremony methods (beardog.fido2.*, genetic.ceremony_*)

## Metrics

| Metric | Value |
|--------|-------|
| Scenarios | 156 |
| Tests | 1,174 |
| Failures | 0 |
| Known debt | 1 (graphenegate-readiness: deploy script) |
| soundStage unit tests | 16 |
| Total soundStage tests | 16 (unit) + scenario integration |

## Upstream Gaps for 139a Scope

| Priority | Gap | Owner |
|----------|-----|-------|
| P1 | SoloKey GetAssertion live tap test | bearDog hardware team |
| P1 | Wire soundStage capture into bearDog ceremony IPC | bearDog team |
| P2 | Depot full harvest — build all 13 primals musl-static on sporeGate | cellMembrane + sporeGate |
| P2 | northGate mesh enrollment (Windows songBird cross-compile) | songBird team |
| P2 | Browser UI for live soundStage observation | sporePrint / esotericWebb |
| P3 | Cascade push fix for non-bare repos | cellMembrane |

---

**Status**: PUSHED. 156 scenarios / 1,174 tests / zero failures. soundStage now proven
at both unit level (16 tests) and scenario integration level. Depot layout compliance
validates the P2 divergence structurally.
