# projectNUCLEUS Deep Debt Resolution — May 13, 2026

**Date**: May 13, 2026
**From**: projectNUCLEUS (sporeGarden)
**For**: primalSpring, all primal teams, spring teams
**Scope**: Hardcoded path elimination, documentation reconciliation, upstream
drift flagging across projectNUCLEUS + foundation + lithoSpore

---

## What Shipped

### Hardcoded Path Elimination (zero remaining)

| Category | Count | What Changed |
|----------|------:|-------------|
| Workload TOMLs | 7 | `${SPRINGS_ROOT:-/home/eastgate/...}` fallbacks removed — now bare `$SPRINGS_ROOT` matching all other workloads |
| Deploy scripts | 1 | `deploy_songbird_relay.sh` `SONGBIRD_SRC` evolved from `/home/irongate/...` to `${ECOPRIMALS_ROOT}` pattern |
| Display strings | 2 | `external_validation.sh` "ironGate" references evolved to gate-agnostic "Gate" |

**Result**: Zero hardcoded developer paths remain in workloads or deploy scripts.

### Documentation Reconciliation

| Item | Before | After |
|------|--------|-------|
| foundation `specs/EVOLUTION_GAPS.md` | 194-line stale copy (May 09) contradicting NUCLEUS canonical (May 11) on H2-05, H2-12, H2-14 | Cross-reference to NUCLEUS canonical copy |
| lithoSpore README | "2/7 MODULES PASS" | "4/7 MODULES PASS (28/28 checks)" — reflects B7 Tenaillon + B2 Anderson |
| lithoSpore `UPSTREAM_GAPS.md` | "2/7 modules live" with modules 6+7 listed as Scaffold | Modules 6+7 updated to "Tier 2 PASS" with check counts |
| foundation `FOUNDATION_PRIMER.md` | "12,510+ quantitative checks" | "13,100+" |
| foundation `THE_UNIFIED_LINEAGE.md` | "12,510+ quantitative checks" | "13,100+" |
| benchScale `songbird_nat_parity.sh` | "stub until Songbird NAT is implemented" | Points to `deploy_songbird_relay.sh` (Wave 202) |

### Upstream Flag: barraCuda Registry Count Drift

`crates/barracuda-core/src/ipc/methods_tests/registry_tests.rs` asserts
`REGISTERED_METHODS.len() == 71` but `methods/mod.rs` contains 72 entries
after Sprint 58 added `precision.route`.

**Action for barraCuda team**: Update assertion to 72 or derive expected count
from the slice to prevent future drift. Documented in
`projectNUCLEUS/validation/PRIMAL_DEEP_DEBT_HANDBACK.md` addendum.

---

## Scope of Changes

| Repo | Files Changed | Nature |
|------|--------------|--------|
| projectNUCLEUS | 11 | Workload TOMLs (7), deploy script (1), external_validation.sh (1), EVOLUTION_GAPS.md changelog (1), PRIMAL_DEEP_DEBT_HANDBACK.md (1) |
| foundation | 3 | EVOLUTION_GAPS.md (replaced), FOUNDATION_PRIMER.md (count fix), THE_UNIFIED_LINEAGE.md (count fix) |
| lithoSpore | 2 | README.md (module counts), UPSTREAM_GAPS.md (module statuses + counts) |

---

## What This Means for Teams

- **primalSpring**: No action needed. Zero drift items flagged against springs.
- **barraCuda**: Registry test assertion needs 71→72 bump (Sprint 58 `precision.route`).
- **All primals**: Workload TOMLs now require `$SPRINGS_ROOT` to be set (no fallback). Ensure your gate environment exports this variable.
- **Spring teams**: lithoSpore upstream gap tracker now correctly reflects 4/7 modules PASS. neuralSpring B3/B4/B6 remain the critical path for modules 3-5.
