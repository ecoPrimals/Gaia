# projectFOUNDATION Deep Debt Evolution Handoff

**Date**: May 16, 2026
**From**: projectFOUNDATION workstream
**To**: primalSpring audit, upstream primal teams
**Status**: Complete — ready for upstream review

## Summary

Comprehensive deep debt resolution, mock elimination, security hardening,
pipeline evolution, and documentation cleanup across the entire
projectFOUNDATION repository. All changes target production correctness,
ecosystem standards compliance, and primal self-knowledge principles.

## What Was Done

### 1. Self-Validating Mock Elimination

Two workloads (`enviro-qs-validation`, `anderson-math-validation`) were
comparing hardcoded constants to themselves — always passing, zero
actual validation. Both now delegate to real `groundSpring` validation
binaries with `[skip]` when binaries aren't built.

**Files changed:**
- `workloads/thread04_enviro/enviro-qs-validation.toml` — rewired to `validate_all --filter anderson_qs`
- `workloads/thread07_anderson/anderson-math-validation.toml` — rewired to `validate_all --filter anderson`

### 2. Pipeline Hardening (foundation_validate.sh)

| Phase | Change |
|-------|--------|
| Phase 4 | Now manifest-driven: reads `data/sources/*.toml` to match fetched files by accession before falling back to glob-all |
| Phase 6 | Target comparison already fixed in prior pass (expected_value, tolerance/tolerance_pct) |
| Phase 7 | All three provenance RPCs (dag.session.complete, entry.append, braid.create) now validate responses; empty/error produces `[WARN]` + `PROVENANCE_WARN` counter |
| Reporting | `[SKIP]` counted alongside `[OK]`/`[FAIL]` throughout pipeline and report |
| Discovery | Tracks `DISCOVERY_FALLBACK_COUNT`; warns when ports resolve via hardcoded defaults instead of discovery socket |

### 3. Script Modularization

`foundation_validate.sh` refactored from 699 → 535 lines:
- `deploy/lib/primal_ipc.sh` (92 lines) — discovery, RPC clients, BLAKE3, byte-array conversion
- `deploy/lib/target_compare.sh` (92 lines) — Phase 6 target comparison logic

All modules pass `bash -n` syntax check.

### 4. Security Isolation Hardening

All 15 workloads using `isolation_level = "None"` upgraded to `"Standard"` with
`trusted_directories`. Zero `None` isolation remaining in any workload TOML.

**Files changed (15):**
- `workloads/thread02_plasma/hs-sarkas-md.toml`
- `workloads/hotspring/hs-chuna-validation.toml`
- `workloads/hotspring/hs-sarkas-md-validation.toml`
- `workloads/groundspring/gs-python-baselines.toml`
- `workloads/groundspring/gs-bench-gpu.toml`
- `workloads/groundspring/gs-guidestone.toml`
- `workloads/groundspring/gs-validate-all.toml`
- `workloads/thread06_ag/airspring-atlas-pipeline.toml`
- `workloads/thread06_ag/airspring-et0-methods.toml`
- `workloads/thread06_ag/airspring-full-suite.toml`
- `workloads/thread06_ag/airspring-soil-physics.toml`
- `workloads/thread06_ag/airspring-water-balance.toml`
- `workloads/thread06_ag/airspring-et0-fao56.toml`
- `workloads/thread07_anderson/litho-anderson-integration.toml`
- `workloads/thread04_enviro/litho-breseq-integration.toml`

### 5. Gate Naming Consistency

33 occurrences of `ironGate` normalized to `irongate` across 11 files.
CI now enforces consistent lowercase naming.

### 6. Target Schema Unification

- Thread 9 gaming targets migrated from string-form to numeric `expected_value`/`tolerance`
- Stale `total_targets` in `thread01_wcm_targets.toml` corrected (24 → 27)
- All 184 targets across 11 files validated against schema

### 7. CI Pipeline Expansion

New CI gates added to `.github/workflows/ci.yml`:
- Target TOML schema validation (numeric types, required keys)
- Workload integrity check (metadata completeness, isolation level)
- Gate naming consistency enforcement
- Python 3.10+ compatibility via `tomli` fallback

### 8. Benchmark Infrastructure

- Added `benchmarks/barracuda_cpu_parity/requirements.txt` (numpy, scipy)
- Fixed README (removed false `pytest` claim, corrected tolerance table)
- All 3 Python baselines now emit provenance headers (timestamp, Python/NumPy version, platform, git commit)

### 9. Workload Metadata Completion

6 thread06_ag workloads missing `thread`/`thread_name` metadata now have `thread = "06"`.
29 workloads total, zero schema errors, zero `None` isolation.

### 10. Documentation Cleanup

- Root `README.md`: updated target count (184), added deploy/lib/, benchmarks/ to repo structure
- `specs/FOUNDATION_VALIDATE_ELEVATION_REVIEW.md`: corrected stale line count (607 → 535 + libs)
- `validation/handbacks/SECURITY_HANDBACK_MAY06_2026.md`: fixed stale `graphs/compositions/` path, clarified primalSpring CHECKSUMS reference
- `workloads/README.md`: updated directory listing for all 10 thread dirs, updated isolation example

## Validation Results

```
TOML syntax:     All valid (0 errors)
Bash syntax:     All 5 scripts pass bash -n
Target schema:   184 targets / 11 files / 0 errors
Workload check:  29 workloads / 0 errors / 0 None isolation
Gate naming:     Consistent (only CI check file references ironGate)
TODO/FIXME:      Zero occurrences in non-archive code
Empty files:     None found
Temp debris:     None found
Files >800L:     None (largest: LICENSE at 661)
```

## Upstream Review Notes for primalSpring

### Gaps Found for Upstream Primal Teams

1. **rhizoCrypt**: `dag.session.create` response structure not documented in
   primalSpring — we infer `result.session_id` from observed behavior.
   Needs: API schema in primalSpring docs.

2. **loamSpine**: `entry.append` with `SessionCommit` entry type — response
   format undocumented. Pipeline now validates response but can't distinguish
   partial success from full commit without schema.

3. **sweetGrass**: `braid.create` returns `result.urn` — format not documented
   (is it always a URN? can it be an ID?). Pipeline handles both.

4. **toadStool**: `trusted_directories` interaction with `working_dir` needs
   explicit documentation. We set both `trusted_directories` and `working_dir`
   in all workloads but the precedence rules aren't documented.

5. **Discovery socket**: `capability.resolve` — no documentation on response
   schema or error cases. Pipeline falls back to environment/defaults.

6. **NestGate**: `storage.store` value format is ad-hoc (`"blake3:$hash size:$size"`).
   Needs: structured value schema or dedicated metadata fields.

### What primalSpring Should Audit

- All 29 workload TOMLs now use `isolation_level = "Standard"` — verify
  toadStool honors `trusted_directories` correctly for this level
- Phase 7 provenance chain now validates RPC responses — coordinate on
  expected response schemas for the trio
- Self-validating workloads eliminated — groundSpring `validate_all` binary
  is now the real dependency for Thread 4 and Thread 7 validation

## Files Changed (Summary)

| Category | Count | Key files |
|----------|-------|-----------|
| Workload TOMLs | 23 | All under `workloads/` |
| Deploy scripts | 3 | `foundation_validate.sh`, new `lib/primal_ipc.sh`, `lib/target_compare.sh` |
| Target TOMLs | 2 | `thread09_gaming_targets.toml`, `thread01_wcm_targets.toml` |
| CI | 1 | `.github/workflows/ci.yml` |
| Benchmarks | 4 | 3 Python scripts + `requirements.txt` |
| Documentation | 6 | README.md, workloads/README.md, benchmarks README, elevation review, security handback, deploy README |
| Handoff | 1 | This file |
