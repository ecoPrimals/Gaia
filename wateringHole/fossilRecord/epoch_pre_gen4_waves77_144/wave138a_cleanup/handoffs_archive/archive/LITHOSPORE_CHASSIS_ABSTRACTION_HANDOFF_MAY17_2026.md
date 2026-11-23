<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# lithoSpore — Chassis Abstraction Evolution Handoff

**Date**: 2026-05-17 PM
**From**: lithoSpore workstream (gardens/lithoSpore)
**For**: All primal teams, spring teams, projectNUCLEUS, projectFOUNDATION
**Status**: Active

---

## Summary

lithoSpore's internal architecture has been systematically decoupled from
the LTEE instance. `litho-core` (11 modules) is now 100% domain-agnostic.
The chassis can now spawn non-LTEE guideStone artifacts (e.g., Chuna lattice
QCD, Bazavov pharmacometrics) without forking.

This handoff documents:
- What changed and why
- What it means for primal/spring teams authoring new guideStone instances
- NUCLEUS composition patterns for multi-instance orchestration
- neuralAPI/biomeOS atomic instantiation implications

---

## 1. What Changed (Architecture)

### Before: Tight LTEE Coupling

Six CLI files (validate, parity, ops, chaos, deploy_test, visualize) each
maintained their own copy of `LTEE_MODULES`, `MODULE_DISPATCH`, and
`LTEE_NOTEBOOKS` constants. Module discovery, dispatch, and name matching
were hardcoded to `ltee-*` binary names. `.biomeos-spore` was a static
template. Braid accession expectations were compiled in. `litho-core`
contained LTEE-specific viz adapters.

### After: Scope-Driven Module Registry

| Change | Detail |
|--------|--------|
| `scope.toml` `[[module]]` entries | Each module specifies name, binary, data_dir, expected, tier1_notebook |
| `registry.rs` centralization | Single module for load_module_table, dispatch_module, module_name_matches |
| Dynamic `.biomeos-spore` | Generated from scope.toml identity fields during `litho assemble` |
| Dynamic braid accessions | Derived from `data.toml` `sra_accession` fields at runtime |
| Parameterized paths | `guidestone.targets_file`, `guidestone.graph_file` in scope.toml |
| `derive_logical_name()` | Strips `ltee-`, `milc-`, `lattice-` prefixes generically |
| `viz/` isolation | Moved from `litho-core` to `ltee-cli` (instance layer) |
| Test fixture isolation | LTEE graph/registry fixtures in `tests/fixtures/`, not source |

### litho-core Is 100% Chassis

`litho-core` contains 11 public modules. None reference LTEE, breseq,
fitness, mutations, or any other domain concept. All domain knowledge
lives in:
- `scope.toml` + `data.toml` (configuration)
- `ltee-*/src/lib.rs` (module implementations)
- `ltee-cli/src/registry.rs` (dispatch table)
- `ltee-cli/src/viz/` (visualization adapters)

---

## 2. What This Means for New GuideStone Instances

### Creating a Chuna GuideStone (Example)

A hypothetical lattice QCD guideStone for the Chuna collaboration:

1. **Write `artifact/scope.toml`**:
```toml
[guidestone]
name = "chuna-guidestone"
version = "0.1.0"
target = "x86_64-unknown-linux-musl"
targets_file = "data/targets/chuna_validation_targets.toml"
graph_file = "graphs/chuna_guidestone.toml"

[[module]]
name = "wilson_flow"
binary = "milc-wilson-flow"
data_dir = "artifact/data/chuna_2024"
expected = "validation/expected/module1_wilson.json"
tier1_notebook = "notebooks/module1_wilson/wilson_flow.py"

[[module]]
name = "fermion_force"
binary = "milc-fermion-force"
data_dir = "artifact/data/fermion_configs"
expected = "validation/expected/module2_fermion.json"
```

2. **Write `artifact/data.toml`** with dataset manifests and BLAKE3 hashes.

3. **Implement module crates** exposing `run_validation()`.

4. **Add Cargo workspace members** and deps to `ltee-cli/Cargo.toml`.

5. **Run `litho assemble`** — chassis handles everything: scope parsing,
   `.biomeos-spore` generation, data staging, binary embedding, provenance.

No changes to `litho-core`. No changes to the harness, tolerance, discovery,
provenance, scope, or manifest modules.

---

## 3. NUCLEUS Composition Patterns

### Single-Instance Composition (Current)

```
NUCLEUS
  └── litho-validate-tier3 (workload)
        └── ltee_guidestone.toml (graph)
              ├── beardog (crypto)
              ├── rhizocrypt (dag)
              ├── loamspine (spine)
              └── sweetgrass (braid)
```

### Multi-Instance Composition (Future)

```
NUCLEUS
  ├── litho-validate-ltee-tier3
  │     └── ltee_guidestone.toml
  ├── litho-validate-chuna-tier3
  │     └── chuna_guidestone.toml
  └── litho-parity-cross-instance
        └── parity across both instances
```

Each instance gets its own graph, workload, and `scope.toml`. The chassis
plumbing (discovery, provenance, braid ingestion) is shared. NUCLEUS
orchestrates them as independent workloads that share the same trio.

### Atomic Instantiation via neuralAPI

The USB artifact is a ColdSpore → LiveSpore → lithoSpore lifecycle.
biomeOS can atomically instantiate it:

1. `spore.discover` — find lithoSpore artifacts on attached media
2. `spore.validate` — run `litho self-test` for integrity
3. `spore.instantiate` — provision into VM cell with UDS connectivity
4. `primal.announce` — register with biomeOS at Tier 3 startup

The `.biomeos-spore` manifest (now generated from scope.toml) provides
identity, capabilities, and entry points for biomeOS to discover.

**Request to biomeOS**: Define the `spore.instantiate` signal/command.
Currently manual (cloud-init YAML + `litho grow --vm`).

---

## 4. Implications for Upstream Springs

### Braid Handoff Is Instance-Agnostic

The ferment transcript pattern works for any instance:
- Spring processes raw data → records provenance → hands braid
- lithoSpore stores braid in `provenance/braids/` per instance
- `data.toml` references `upstream_braid`, `upstream_spring`, `upstream_dag_session`
- `litho validate` checks SRA accessions from `data.toml` at runtime

Springs don't need to know about the chassis abstraction — they hand
braids to a dataset, not to the chassis.

### Summary Stats Contract

Springs producing summary statistics for a guideStone must match the
published paper's claims within the tolerances defined in
`artifact/tolerances.toml`. This contract is per-instance — each
instance defines its own tolerance bands.

---

## 5. What Primal Teams Should Absorb

| Item | Team | Priority |
|------|------|----------|
| `.biomeos-spore` is now dynamic JSON from scope.toml | biomeOS | INFO |
| `derive_logical_name()` strips `milc-`, `lattice-` in addition to `ltee-` | All | INFO |
| `scope.toml` `[[module]]` is the module registry standard | projectFOUNDATION | MEDIUM |
| `registry.rs` pattern: scope-primary, compiled-fallback | All gardens | INFO |
| Multi-instance NUCLEUS composition is architecturally ready | projectNUCLEUS | MEDIUM |
| `spore.instantiate` signal needed for automated provisioning | biomeOS | LOW |

---

## 6. Current State (Post-Abstraction)

| Metric | Value |
|--------|-------|
| litho-core modules | 11 (100% chassis — zero domain code) |
| Science modules | 7/7 PASS (Tier 2 Rust) |
| Science checks | 75/75 |
| Unit/integration tests | 125 |
| Chassis coupling points resolved | 10/12 (remaining: crate naming, feature flags) |
| CLI subcommands | 15 |
| Clippy | Zero warnings |
| Unsafe code | `#![forbid(unsafe_code)]` workspace-wide |

---

## Cross-References

- `LITHOSPORE_PRIMAL_SPRING_EVOLUTION_HANDOFF_MAY17_2026.md` — primal evolution requests
- `LITHOSPORE_FERMENT_TRANSCRIPT_BRAID_HANDOFF_MAY17_2026.md` — upstream braid contract
- `LITHOSPORE_WAVE21_ABSORPTION_HANDOFF_MAY17_2026.md` — Wave 21 absorption
- `lithoSpore/docs/ARCHITECTURE.md` — chassis evolution roadmap
- `lithoSpore/specs/MODULES.md` — coupling inventory
- `lithoSpore/artifact/scope.toml` — LTEE scope definition with `[[module]]` entries
