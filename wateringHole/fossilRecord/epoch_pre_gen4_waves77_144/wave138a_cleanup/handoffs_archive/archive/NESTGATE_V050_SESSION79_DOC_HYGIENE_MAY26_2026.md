# NestGate v0.5.0 — Session 79: Documentation Hygiene

**Date**: 2026-05-26  
**Session**: 79  
**Wave**: 53 (continuation)

---

## Summary

Comprehensive documentation sweep across NestGate root docs, crate READMEs, and
infra references. All active documentation synchronized to Session 78 metrics
(12,467+ tests, 83.61% coverage, v0.5.0).

## Changes

### Root Docs Updated (9 files)

- `README.md` — Session 78 metrics, 12,467+ tests, 83.61% coverage
- `STATUS.md` — Quick Metrics block refreshed; measured date May 26, 2026
- `CONTEXT.md` — Added test/coverage rows to facts table
- `START_HERE.md` — Session 78 metrics
- `QUICK_REFERENCE.md` — Session 78 metrics
- `QUICK_START.md` — Session 78 build status
- `CONTRIBUTING.md` — Session 78 metrics, footer date
- `DOCUMENTATION_INDEX.md` — Session 78 date
- `CAPABILITY_MAPPINGS.md` — Session 78 date

### Crate README Fixes (2 files)

- `nestgate-core/README.md` — `0.1.0` → `0.5.0` in dependency example
- `nestgate-api/README.md` — `0.1.0` → `0.5.0` in JSON version field

### Broken Link Fixes (2 files)

- `docs/guides/ENVIRONMENT_VARIABLES.md` — removed dead links to
  `../config/README.md` and `../deployment/README.md`
- `docs/API_COLLABORATIVE_INTELLIGENCE.md` — removed dead link to
  `COLLABORATIVE_INTELLIGENCE_TRACKER.md`, fixed biomeOS quick start path

### Debris Cleaned (2 files)

- `benches/README.md` — replaced emoji-heavy DashMap migration README with
  concise legacy-reference note
- `code/crates/nestgate-config/src/constants/MIGRATION_GUIDE.md` — corrected
  stale "188 deprecated markers" claim (markers were cleaned in Session 43w)

### Infra Docs Updated (3 files)

- `wateringHole/GLACIAL_SHIFT_WAVE_PLAN.md` — NestGate version unify marked
  RESOLVED
- `wateringHole/handoffs/WAVE53_PRIMAL_MOUNTAINS_MAY26_2026.md` — NestGate
  section updated from CRITICAL to RESOLVED
- `plasmidBin/README.md` — NestGate version `0.1.0` → `0.5.0` in binary table

## Audit Results (No Action Needed)

- `.env.test` — test config only (no secrets); intentionally committed
- `scripts/setup-test-substrate.sh` — legitimate host-specific ZFS test setup
- 22 fossil-bannered docs in `docs/` — correctly marked as historical records
- All `CHANGELOG.md` historical version references — intentional fossil context
- `Cargo.lock` in `.gitignore` — workspace policy (library crate convention)

## Open Items

- Coverage push to 90% target (ongoing across waves)
- VPS Nest expansion (Wave 54)
