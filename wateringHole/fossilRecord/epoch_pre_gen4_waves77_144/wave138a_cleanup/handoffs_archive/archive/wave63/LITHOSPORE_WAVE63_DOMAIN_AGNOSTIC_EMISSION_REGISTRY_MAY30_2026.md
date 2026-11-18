# lithoSpore Wave 63 — Domain-Agnostic Emission + Registry Evolution

**Date**: May 30, 2026
**From**: lithoSpore team
**To**: primalSpring coordination, projectFOUNDATION, sporePrint teams
**Context**: Wave 63 sporeGarden Products audit response

---

## Summary

lithoSpore's emit pipeline and registry ingest have been evolved for
multi-spring domain-agnostic operation. Comp-chem defaults (GROMACS, PLUMED,
carbohydrate ring atoms) are now gated behind profile detection. Registry
ingest uses structured TOML I/O with version-aware upsert, status derivation,
and meta counter maintenance.

**199 tests**, zero clippy warnings, `#![forbid(unsafe_code)]`.

---

## Changes

### 1. Profile-Gated Environment Probing (`environment.rs`)

**Before**: Always probed `gmx` and `plumed` regardless of domain profile.
**After**: Profile-driven tool detection. When a profile declares `tools`,
only those tools are probed. No-profile mode retains comp-chem defaults for
backward compatibility with existing hotSpring emissions.

### 2. Domain-Agnostic README Generation (`scripts.rs`)

**Before**: Hardcoded FEL plots, GROMACS MDP, PLUMED HILLS, xylanase crystal
structure, Cremer-Pople collective variables in all generated READMEs.
**After**: README template branches on profile domain:
- Comp-chem profiles (tools include gromacs/plumed/lammps): MD-specific
  Quick Start, File Inventory, and module table with CV/Time columns
- Non-comp-chem profiles: generic descriptions, dataset-oriented module table
- Translation rows (index_map, TRANSLATE.md) only shown when translation
  is enabled in the profile

### 3. Profile-Gated Module Metadata (`scope.rs`)

**Before**: `infer_module_metadata` assumed all modules were MD simulations
with "collective variables".
**After**: Returns domain-appropriate labels based on profile tools.
Non-MD profiles get generic "dataset" / profile ID labels.

### 4. Removed Carbohydrate Fallback (`index_map.rs`)

**Before**: When no entity groups provided, fell back to hardcoded carbohydrate
ring atom names (C1-C5, O5) and sugar residue filters (XYS, BXYL, etc.).
**After**: Translation requires explicit entity groups from a domain profile.
No profile → no index_map generated. Dead code (`default_atom_names`,
`default_residue_filters`) removed.

### 5. Structured Registry Ingest (`ingest_pseudospore.rs`)

**Before**: Append-only string concatenation. Name-only dedup (version bumps
skipped). No `status` field. `[meta].last_updated` and `total_ingested`
never updated. Write errors silently ignored.
**After**:
- Proper `Registry` / `RegistryEntry` serde types with structured TOML parse
- Version-aware upsert: `(name, version)` match for update, else insert
- `status` derived from validation: COMPLETE / PARTIAL / PENDING
- `[meta].last_updated` and `total_ingested` auto-maintained
- `spring` falls back to scope origin when ferment transcript is absent
- Write errors propagated (not silently swallowed)
- Header comment preserved across writes
- 4 new tests: insert, upsert-same-version, append-new-version, existing
  registry.toml parse

### 6. Registry Schema Fix (`pseudospores/registry.toml`)

- `total_ingested` corrected from `0` to `1`
- `spring` normalized from `springs/hotSpring` to `hotSpring`
- Schema now matches canonical `Registry` struct

---

## Test Metrics

| Metric | Before | After |
|--------|--------|-------|
| Total tests | 192 | 199 |
| ltee-cli unit tests | 31 | 36 |
| Registry tests | 0 | 4 |
| Domain synthesis tests | 0 | 2 |
| Clippy warnings | 0 | 0 |

---

## Multi-Spring Emission Readiness

| Component | Status |
|-----------|--------|
| `--spring` flag | Agnostic (free string) |
| `DomainProfile` parser | Any TOML with `[profile]` section |
| Environment probing | Profile-gated |
| README generation | Profile-gated |
| Index map generation | Profile-required (no comp-chem fallback) |
| Figures generation | Profile-gated (`[figures] enabled`) |
| Module metadata | Profile-aware labels |
| Registry ingest | Version-aware upsert with status |

**Ready for**: `litho emit-pseudospore --spring healthSpring --domain-profile <path>`
once healthSpring's `domain_profile.toml` is synced locally.

**Schema note for upstream springs**: wetSpring and groundSpring profiles use
`[[translation.entity_groups]]`, `[[derivation.pipeline]]`, and
`[[audit.checks]]` conventions. lithoSpore's parser expects
`[[translation.entity_group]]`, `[[derivation.contract]]`, and `[audit]`
boolean flags. The emit pipeline degrades gracefully (copies profile, generates
envelope, skips rich domain logic), but full domain-aware audit/promote
requires schema alignment. This is a coordination item for Wave 64.

---

## Wave 63 lithoSpore Immediate Work — Status

| Task | Priority | Status |
|------|----------|--------|
| Multi-spring emission (domain-agnostic gating) | **HIGH** | **DONE** — pipeline ready for any spring |
| Registry automation (structured upsert) | LOW | **DONE** — status, meta, version-aware |
| Remote fetch subcommand | MEDIUM | **DONE** — `litho fetch-pseudospore --url <url>` with `--ingest` chain |
| Domain knowledge extraction | — | **DONE** — LTEE synthesis moved from chassis to domain crates |

### 7. Remote Fetch Subcommand (`fetch_pseudospore.rs`)

New `litho fetch-pseudospore --url <url>` subcommand. Downloads a tarball
from a hosted gallery (HTTP/HTTPS), extracts and validates the pseudoSpore
envelope, and optionally chains into `ingest-pseudospore` with `--ingest`.
Uses existing `ureq`/`tar`/`flate2` workspace deps — no new externals.

### 8. Domain Knowledge Extraction (`fetch.rs` → domain crates)

LTEE-specific data synthesis functions (`generate_fitness_csv`,
`generate_mutation_params`) moved from the chassis `fetch.rs` pipeline
into their domain crates as `synthesize_from_expected()`. Domain
constants (`POPULATION_SIZE = 500_000`, `GENOMIC_MUTATION_RATE = 8.9e-4`,
`GENERATIONS_OBSERVED = 20_000`) centralized as named constants in
`ltee-mutations`. `fetch.rs` now delegates to domain crate APIs — no
hardcoded LTEE constants remain in the chassis pipeline.

---

## Upstream Notes

- **projectFOUNDATION**: lithoSpore's `registry.toml` is now machine-parseable
  with proper serde types. Foundation's planned "pseudoSpore library management"
  can deserialize it directly to generate gallery pages.
- **sporePrint**: The registry schema includes `status`, `modules_pass`,
  `modules_total`, `spring`, and `date` — sufficient for gallery template
  population without additional API.
- **healthSpring**: Profile documented as shipped (commit `a35cc6d`) but not
  present in local workspace. Sync needed before running emission test.
