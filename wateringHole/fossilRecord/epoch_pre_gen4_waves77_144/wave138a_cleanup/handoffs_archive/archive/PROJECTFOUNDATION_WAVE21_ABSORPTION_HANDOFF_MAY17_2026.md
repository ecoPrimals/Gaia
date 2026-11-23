# projectFOUNDATION — Wave 21 Absorption Handoff

**Date**: May 17, 2026
**From**: projectFOUNDATION (sporeGarden/gardens)
**To**: primalSpring (audit response), all primal teams, all springs
**Context**: Absorption of primalSpring Wave 21 audit "Garden Product
Evolution — Primal Composition Patterns" into projectFOUNDATION.

---

## What Was Absorbed

### 1. Canonical Schema Resolution

Marked `primal.list` and `capability.list` canonical schemas as SHIPPED
in `COMPOSITION_GAPS.md`. UB-1 through UB-4 upstream blockers are resolved.
Wave 20 resolutions section added with full status table.

**Files changed**: `validation/COMPOSITION_GAPS.md`

### 2. Method Stability Tier Awareness

Added stability tier documentation to `workloads/README.md` covering
`stable`, `evolving`, and `internal` tiers with consumer guidance.
Updated key workloads (Thread 5 LTEE, Thread 10 Provenance) with
`method_stability = "all_stable"` and explicit `methods_consumed` lists.

**Files changed**: `workloads/README.md`, `workloads/thread05_ltee/litho-ltee-mutations.toml`,
`workloads/thread05_ltee/litho-ltee-fitness.toml`,
`workloads/thread10_provenance/primalspring-validation.toml`

### 3. Degradation Behavior Documentation

Created `docs/DEGRADATION_BEHAVIOR.md` documenting the full pipeline
degradation matrix — what happens when each primal is unreachable,
per pipeline phase. Documents the ecosystem invariant: "Science is
never gated behind primal availability."

Added degradation state section to `foundation_validate.sh` report
output, including discovery fallback count, provenance warnings, and
trio state classification (full / dag_spine / dag_only / standalone).

Added `[degradation]` section to `provenance.toml` export.

**Files changed**: `docs/DEGRADATION_BEHAVIOR.md` (new),
`deploy/foundation_validate.sh`

### 4. Trio Partial Completion Semantics

Documented partial trio completion policy in `COMPOSITION_GAPS.md`,
referencing `wateringHole/PROVENANCE_TRIO_INTEGRATION_GUIDE.md`.
The four valid states (Full, DAG+spine, DAG only, Standalone) are
now explicit. "No rollback on partial" is the documented rule.

Updated `PROVENANCE_FOLDER_CONVENTION.md` with partial trio section.

**Files changed**: `validation/COMPOSITION_GAPS.md`,
`validation/PROVENANCE_FOLDER_CONVENTION.md`

### 5. Thread 5 Braid Evidence Preparation

Created `validation/wetSpring/braids/` directory with `README.md`
documenting the ferment transcript wire format, expected braids
(Barrick 2009, Tenaillon 2016), and integration path.

Updated Thread 5 LTEE targets:
- Added `braid_pending = true` to all 4 B7 Tenaillon targets
- Added `braid_evidence_source` to `litho-ltee-mutations` workload
- Added upstream metadata (`upstream_spring`, `upstream_status`) to
  target file header

When wetSpring completes Barrick 2009 (4/7 clones remaining), braid
JSON flows to `validation/wetSpring/braids/` and upgrades Thread 5
from "trust the published numbers" to "verify the computation chain."

**Files changed**: `validation/wetSpring/braids/README.md` (new),
`data/targets/thread05_ltee_targets.toml`,
`workloads/thread05_ltee/litho-ltee-mutations.toml`

### 6. Benchmark Formalization as Parity Proofs

Updated `benchmarks/barracuda_cpu_parity/README.md` to frame the
6 CPU parity baselines as formal Tier 1→2 parity proofs per the
ecosystem validation tier model. References
`primalSpring/docs/VALIDATION_TIERS.md` for the three-layer proof
structure.

**Files changed**: `benchmarks/barracuda_cpu_parity/README.md`

### 7. BLAKE3 Backfill Gap Documentation

Created `data/sources/BLAKE3_BACKFILL_STATUS.md` documenting the
current state: all 165 sources across 11 TOMLs have empty blake3
fields. Documents the backfill process and priority (Medium — doesn't
block validation but adds integrity).

**Files changed**: `data/sources/BLAKE3_BACKFILL_STATUS.md` (new)

### 8. Documentation Updates

- `README.md`: Updated generation tag, added ferment braid and
  degradation doc to repo structure
- `validation/README.md`: Added braids subfolder to directory
  convention, updated Thread 5 status with braid evidence note
- `validation/handbacks/UPSTREAM_AUDIT_PREP_MAY15_2026.md`: Updated
  validation state header to Wave 21, updated Thread 5 status,
  added Wave 20 resolution notes
- `validation/handbacks/DEEP_AUDIT_FINDINGS_MAY16_2026.md`: Added
  Wave 21 absorption context

---

## What Remains Open

| Item | Owner | Priority | Note |
|------|-------|----------|------|
| BLAKE3 backfill (165 sources) | projectFOUNDATION | Medium | Requires fetch infrastructure on networked gate |
| Thread 5 B7 validation (4 targets) | wetSpring | High | Barrick 2009 breseq: 4/7 clones remaining |
| Tenaillon 2016 pipeline (~200 GB) | wetSpring | Medium | Queued after Barrick 2009 |
| Thread 1 WCM (0/27 targets) | CATHEDRAL | Medium | RPC stack unreachable — degraded, not broken |
| Thread 3 Immunology (0/15) | healthSpring | Medium | Expression ready, spring validation needed |
| Thread 4 Env Genomics (0/13) | wetSpring, airSpring | Medium | Expression ready, spring validation needed |
| Thread 8 Health (0/9) | healthSpring | Medium | Expression ready, spring expanding |
| ParityReport JSON schema adoption | lithoSpore → projectFOUNDATION | Low | Formalize parity output consumption |
| `method_stability` across all 29 workloads | projectFOUNDATION | Low | 3 done; convention documented; remainder trivial |

---

## Ecosystem Posture (projectFOUNDATION)

| Metric | Value |
|--------|-------|
| Total targets | 184 |
| Validated targets | 146 (79.3%) |
| Active threads | 9/10 (Thread 4 sole remaining inactive) |
| Workloads | 29 (all Standard isolation, trusted_directories) |
| CPU parity baselines | 6 (32 test cases) — formalized as Tier 1→2 proofs |
| Provenance folders | Spring-oriented + braids/ convention |
| CI gates | 11 (shellcheck, TOML syntax, schema, integrity, naming, parity, graph, target reconciliation) |
| BLAKE3 backfill | 0/165 (documented, Medium priority) |
| Upstream blockers absorbed | UB-1 through UB-4 SHIPPED, Wave 20 canonical schemas RESOLVED |
| Stability tier awareness | Documented + 3 key workloads annotated |
| Degradation behavior | Documented (per ecosystem standard) |
| Trio partial completion | Documented and handled in pipeline |
| Braid evidence readiness | Thread 5 prepared for wetSpring ferment transcripts |
