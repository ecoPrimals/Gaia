# CATHEDRAL Workstream Split

**Date**: 2026-05-16
**From**: CATHEDRAL (lithoSpore + projectFOUNDATION)
**For**: primalPing, upstream primal teams, spring teams

## Summary

CATHEDRAL splits into two focused workstreams with separate cadences.
lithoSpore proved the verification pattern with LTEE as the first
instance. The chassis is now being abstracted so future guideStone-grade
artifacts reuse the same engine with different scope and data.

## Terminology

- **guideStone** — a verification grade, not a product name. Any
  artifact that meets the Targeted GuideStone Standard earns this
  classification.
- **lithoSpore** — the verification chassis. A reusable binary pattern
  (scope engine + fetch + validate + assemble + provenance journal).
  LTEE is the first lithoSpore instance. Future instances (physics,
  measurement science, nuclear, etc.) use the same chassis with
  different `scope.toml` and data.
- **projectFOUNDATION** — the scientific knowledge layer. Declares what
  data exists, what results to expect, and how threads connect. Seeds
  new lithoSpore instances by delivering mature thread packages.

## The Two Workstreams

### lithoSpore Workstream

**Owns**: `lithoSpore`, `benchScale`, `agentReagents`

**Focus**:
- Abstract the chassis from LTEE-specific coupling into domain-agnostic
  patterns, using LTEE as the validation instance that proves the
  abstraction didn't break anything
- Stadial hardening: v1.0 tag, crates.io publish, external USB validation
- guideStone grade certification for new instances
- Deployment test infrastructure (benchScale VM orchestration, agentReagents
  image provisioning)

**Current state** (as of split):
- 7/7 LTEE modules PASS Tier 2 (75/75 checks)
- Deployment-validated: musl-static on Ubuntu/Alpine/Fedora/Debian,
  Windows cross-compilation via Wine 11
- Bash-to-Rust elevation complete (all scripts replaced)
- `litho-core` already domain-agnostic: `harness.rs`, `spore.rs`,
  `discovery.rs`, `stats.rs`, `tolerance.rs`
- LTEE coupling remaining in: `validate.rs` (hardcoded `LIVE_MODULES`),
  `fetch.rs` (module-specific fallback), `assemble.rs` (hardcoded binary
  list)

**Abstraction target**: `validate.rs`, `fetch.rs`, and `assemble.rs`
become scope-driven (read from `scope.toml` + `data.toml` at runtime).
`MODULE_DISPATCH` stays compiled (in-process dispatch requires function
pointers). The `ltee-*` crates remain as the first module set.

### projectFOUNDATION Workstream

**Owns**: `projectFOUNDATION`

**Focus**:
- Knowledge layer maintenance: thread validation, data anchoring,
  expression documents
- Unblock Thread 1 WCM (rhizoCrypt session RPC + toadStool
  working-directory trust)
- Seed new lithoSpore instances by delivering mature thread packages
- `foundation_validate.sh` pipeline evolution (eventual Rust elevation)

**Current state** (as of split):
- 10 threads defined, all with expression docs + source/target TOMLs
- Threads 2, 6, 7: full PASS runs with provenance
- Thread 1: attempted, 0/24, upstream-blocked
- Thread 4: litho integration workloads wired, no dated validation run
- Threads 3, 5, 8, 9, 10: documented, not validated

## Handoff Contract

projectFOUNDATION delivers a **mature thread package**:

1. Expression document (`expressions/*.md`)
2. Data source TOMLs (`data/sources/thread*_*.toml`)
3. Validation target TOMLs (`data/targets/thread*_*_targets.toml`)
4. toadStool workloads (`workloads/thread*_*/`)
5. At least one validated run with provenance (`validation/<thread>-<date>/`)

lithoSpore accepts a mature thread as a new instance:

1. Author `scope.toml` scoped to the thread's springs and datasets
2. Populate `data.toml` with the thread's data sources
3. Wire module crates that implement `run_validation(data_dir, expected, max_tier)`
4. Provide `validation/expected/*.json` golden outputs
5. `litho assemble` + `litho validate` produce a guideStone-grade artifact

## Thread Maturity for Next Instance

| Thread | Status | guideStone Readiness |
|--------|--------|---------------------|
| 2 — Plasma | 12/12 PASS | Ready (already in LTEE scope) |
| 6 — Agriculture | 36/36 PASS, 6 workloads | Strongest next-instance candidate |
| 7 — Anderson | 18/18 PASS | Ready (already in LTEE scope) |
| 1 — WCM | 0/24, upstream-blocked | Needs rhizoCrypt/toadStool unblock |
| 4 — Enviro | litho anchored | Needs dated validation run |
| 3, 5, 8, 9, 10 | Documented only | Needs workloads + validation |

Thread 6 (agriculture/measurement science) is the immediate candidate
for the second lithoSpore instance once the chassis abstraction lands.

## What "Split" Means

Separate commit/review/deploy cadences. lithoSpore enters its
stabilization phase (abstract, harden, tag). projectFOUNDATION continues
as a living knowledge layer. New lithoSpore instances start as
`scope.toml` files and grow toward guideStone grade independently.

The split is about focus, not separation. Both workstreams share
`litho-core` as the engine and wateringHole standards as the contract.
