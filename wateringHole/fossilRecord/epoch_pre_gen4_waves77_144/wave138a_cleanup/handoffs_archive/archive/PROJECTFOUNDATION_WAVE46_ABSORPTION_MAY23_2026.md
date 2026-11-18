# projectFOUNDATION — Wave 46 Absorption Handoff

**Date**: May 23, 2026
**From**: projectFOUNDATION
**To**: primalSpring (coordination), upstream primal/spring teams
**primalSpring version**: v0.9.27 (458 methods, 784 tests, 49 scenarios)
**Foundation commits**: `b0a0c62` (Wave 29), this wave

## Context

primalSpring Wave 46 cleared the primal and spring layers to zero gate debt.
projectFOUNDATION absorbs Wave 46 patterns (typed errors, env_keys, signal
dispatch, deploy graph alignment) and resolves remaining local bash debt
in preparation for Rust elevation (Phase B of the elevation review).

## Resolved Items

### 1. Trio-State Deduplication

Three inline trio-state computations (report MD, provenance.toml, results.json)
replaced with `compute_trio_state()` and `trio_state_label()` in `json_rpc.sh`.
Single source of truth, called once in Phase 8.

### 2. Typed Primal Health Checks

`grep -qw` on `REQUIRED_PRIMALS` string replaced with bash array membership
via `is_required_primal()`. Last grep-on-variable pattern eliminated.

### 3. Dead State Cleanup

`declare -A REGISTERED_FILES` — written but never read — removed. Phase 4
registration is manifest-only (catch-all sweep removed in Wave 29).

### 4. Library Consolidation

`fetch_sources.sh` now sources `primal_ipc.sh` for discovery and hashing.
Duplicate `rpc_nestgate()` replaced with conditional fallback (only defined
if `primal_ipc.sh` not sourced). Single `blake3_hash` with Python fallback
retained in fetch for standalone use; canonical `b3sum`-only version in
`primal_ipc.sh` for validation pipeline.

### 5. Spring Folder Mapping Evolution

Hardcoded `case` block for spring → folder routing replaced with
`resolve_workload_spring()` that reads workload TOML metadata
(`provenance.upstream_spring`, `metadata.spring_upstream`), falling back
to prefix matching only for spring-named workloads.

### 6. Deploy Graph Alignment (Wave 46)

`foundation_validation.toml` updated to align with primalSpring patterns:
- `fallback = "skip"` on optional nodes (coralreef, petaltongue, squirrel)
- Dependency ordering: loamSpine → rhizoCrypt, sweetGrass → loamSpine
- Graph README documents intentional delta vs canonical (skunkbat defense
  layer, by_capability string drift, signal graph absence)

### 7. Metrics Sync (458 methods, 49 scenarios)

Updated `validation/COMPOSITION_GAPS.md` from 445 → 458 methods,
referencing primalSpring v0.9.27 and 49 scenarios.

### 8. Elevation Review Updated for Wave 46

`specs/FOUNDATION_VALIDATE_ELEVATION_REVIEW.md` updated:
- Phase B marked as unblocked by Wave 46
- Wave 46 API table added (CompositionContext, env_keys, DispatchError,
  PhasedIpcError, primal.announce, signal dispatch)
- LOC updated (660 + 435 lib = 1,095 sourced)

## Current Pipeline Metrics

| Metric | Value |
|--------|------:|
| `foundation_validate.sh` LOC | 660 |
| Sourced lib LOC | 435 (4 files) |
| Total deploy shell LOC | 1,746 |
| Workloads | 29 |
| Validation targets | 184 |
| Data sources | 165 (10 BLAKE3-anchored) |
| CI gates | 17 |
| CPU parity benchmarks | 6 |
| sporePrint content | Tier 2 (validation-summary.md) |

## Elevation Status

| Phase | Status | Blocker |
|-------|--------|---------|
| A (bash fixes) | **COMPLETE** | — |
| B (foundation-core + foundation-ipc) | **UNBLOCKED** | None — CompositionContext, env_keys, typed errors available |
| C (foundation validate UniBin) | Pending Phase B | — |
| D (foundation fetch UniBin) | Pending Phase C | — |

## Thread 1 WCM (FN-1)

10/25 sources BLAKE3-anchored. 15 unfetchable (private/manual). CI gates
enforce ≥10 non-regression. No change this wave — data integrity is stable.

## What's NOT Changed

- No Rust code yet — Phase B is the next sprint, not this wave
- `fetch_sources.sh` still has Python fallback blake3 (justified — standalone use)
- Phase 4 still uses `find` for accession matching (Rust elevation target)
- RPC failures still swallowed with `|| true` (documented degradation behavior)
- Signal graphs not adopted (bash cannot use CompositionContext)
