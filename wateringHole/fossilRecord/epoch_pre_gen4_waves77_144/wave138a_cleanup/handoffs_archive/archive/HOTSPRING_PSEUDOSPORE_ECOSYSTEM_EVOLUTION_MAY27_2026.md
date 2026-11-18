# hotSpring Handoff: pseudoSpore Ecosystem Evolution — Ownership Matrix & Dispersal Architecture

**Date:** 2026-05-27
**From:** hotSpring (biomeGate)
**To:** primalSpring, lithoSpore, biomeOS
**Context:** [Spore Ecosystem Evolution](56713e5b-805e-4759-aa4a-feee796f4b22)

---

## Summary

Completed the 7-phase pseudoSpore Ecosystem Evolution Plan. This decomposes spore
concerns into a three-way ownership split (springs → lithoSpore envelope → biomeOS
NUCLEUS gateway), unifies the `liveSpore.json` schema, extracts a shared
`pseudospore-core` crate, generalizes `litho emit-pseudospore` for any domain, and
scaffolds `biomeos nucleus ingest/emit` as the future NUCLEUS gateway.

The CompChem pseudoSpore artifact is now at **v1.6.1** — 8 modules (01–06 science,
07 PLUMED-NEST aggregate, 08 exploration roadmap), full-data self-contained tarball,
unified `{envelope, validations}` liveSpore.json schema.

---

## What Was Done

### Phase 1: Ownership Documentation
- **NEW**: `infra/wateringHole/SPORE_OWNERSHIP_MATRIX.md` — three-way split formalized
  (Domain Science ↔ Spore Envelope ↔ NUCLEUS Gateway)
- **UPDATED**: `infra/wateringHole/GLOSSARY.md` — NUCLEUS Gateway, pseudospore-core,
  Spore Ownership Matrix defined
- **UPDATED**: `infra/wateringHole/PRIMAL_REGISTRY.md` — biomeOS entry updated with
  gateway role

### Phase 2: Unified liveSpore.json Schema
- Canonical schema: `{"envelope": {...}, "validations": [...]}`
- Updated in: `PSEUDOSPORE_STANDARD.md`, `litho emit-pseudospore`, `litho audit`,
  `nest-validate guidestone emit`
- Legacy migration logic handles append-only array and hotSpring object formats

### Phase 3: pseudospore-core Crate Extraction
- **NEW**: `gardens/lithoSpore/crates/pseudospore-core/` — 10 `pub mod` (9 API + `error`):
  `blake3_manifest`, `braid_envelope`, `domain_profile`, `envelope`, `error`, `livespore`, `receipts`, `scope`, `tarball`, `validation`
- Workspace member added to `gardens/lithoSpore/Cargo.toml`
- `cargo check` passes

### Phase 4: nest-validate Slimming
- Envelope operations (`guidestone verify`, `guidestone refresh`) now delegate to
  `litho` CLI via `delegate_to_litho` helper
- Domain science operations remain local to hotSpring
- Dead `ingest_targets` placeholder removed from `targets.rs`

### Phase 5: NUCLEUS Gateway Scaffold
- **NEW**: `primals/biomeOS/crates/biomeos-cli/src/commands/nucleus_ingest.rs` —
  `handle_nucleus_ingest` + `handle_nucleus_emit` (stub)
- **UPDATED**: `primals/biomeOS/specs/BIOMEOS_NUCLEUS_EVOLUTION.md`

### Phase 6: Domain-Agnostic Emission
- `litho emit-pseudospore` accepts `--spring` and `--domain-profile` flags
- Removed hardcoded LTEE/CompChem assumptions (forcefield, paper DOI, xylose-specific
  module naming)

### Phase 7: primalSpring Certification
- **NEW**: `springs/primalSpring/experiments/exp115_nest_ingest_pseudospore/README.md`
- **UPDATED**: `s_nest_atomic.rs` — Phase 4 (Spore Gateway) structural checks
- **UPDATED**: `specs/CROSS_SPRING_EVOLUTION.md` — pseudoSpore Ecosystem Convergence section
- **UPDATED**: `specs/NUCLEUS_VALIDATION_MATRIX.md` — columns U/V/W for spore gateway

### Root Documentation Cleanup
- `README.md` — v1.5.0 → v1.6.1, 5 modules → 8 modules, Quick Start path updated
- `specs/README.md` — version bump + CAZyme FEL status expanded
- `whitePaper/README.md` — version bump + module count + schema note
- `docs/PRIMAL_GAPS.md` — audit date + ecosystem evolution note
- `docs/LITHOSPORE_PROMOTION.md` — marked superseded by ecosystem evolution

### Debris Cleaned
- Dead `ingest_targets` TODO stub removed from `nest-validate/src/targets.rs`
- v1.5.0 artifact retained on disk for provenance (data.toml refresh in-flight)

---

## Five-Repo Touch Points

| Repo | Changes |
|------|---------|
| **hotSpring** | nest-validate delegation, root doc updates, debris cleanup |
| **lithoSpore** | pseudospore-core crate, emit/audit generalization, PSEUDOSPORE_STANDARD |
| **biomeOS** | nucleus_ingest scaffold, BIOMEOS_NUCLEUS_EVOLUTION spec |
| **primalSpring** | exp115, s_nest_atomic Phase 4, CROSS_SPRING_EVOLUTION, NUCLEUS_VALIDATION_MATRIX |
| **wateringHole** | SPORE_OWNERSHIP_MATRIX, GLOSSARY, PRIMAL_REGISTRY |

---

## Downstream Expectations

### For primalSpring
1. **Audit**: Run structural validation — exp115 checks should pass (existence of
   ownership matrix, pseudospore-core, nucleus_ingest module)
2. **Nest Atomic abstraction**: Abstract `nest ingest` + `validate` into `Nest Atomic`
   and Neural API, enabling hotSpring to clean transitional `litho ingest-pseudospore`
   shell-out for full postPrimordial compliance
3. **NUCLEUS_VALIDATION_MATRIX columns U/V/W**: Live gateway experiments pending
   biomeOS southGate health

### For biomeOS
1. Wire `nucleus ingest` subcommand into top-level CLI argument parser
2. Implement `nucleus emit` (currently stub)
3. Adopt `pseudospore-core` as dependency for NestGate operations

### For lithoSpore
1. ~~Wire `ltee-cli` to depend on `pseudospore-core` (currently parallel implementations)~~ **COMPLETE** (NC-1.3, May 27)
2. ~~Validate domain-agnostic emission against a second spring~~ **COMPLETE** — groundSpring emits identical envelope structure (column W validated, May 27)

---

## Untracked Data (Not Committed — Working Data)

| Path | Status |
|------|--------|
| `control/gromacs_fel/guidestone_refresh/*/fes_*.dat` | Refreshed FES outputs — already promoted into v1.5.0 modules |
| `control/plumed_nest/target_02_chignolin_opes/COLVAR*` | PLUMED simulation outputs — gitignore candidates |
| `control/plumed_nest/target_02_chignolin_opes/Kernels*.data` | OPES kernel data — gitignore candidates |
| `pseudoSpore_*_v1.6.1.tar.gz` | Distribution tarball — intentional release artifact |
