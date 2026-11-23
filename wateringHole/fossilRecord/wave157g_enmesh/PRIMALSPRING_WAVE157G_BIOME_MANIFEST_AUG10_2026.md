# primalSpring — Wave 157g: biome.yaml Manifest Consumption

**Date**: Aug 10, 2026 | **Team**: primalSpring (eastGate) | **Wave**: 157g ENMESH

## Summary

primalSpring now consumes toadStool's canonical `biome.yaml` v1 schema for
manifest-driven NUCLEUS composition lifecycle. This is the HIGH-priority
modernization item from Wave 157g.

## Delivered

### 1. biome.yaml Parser + Validator (`composition::manifest`)

New module `ecoPrimal/src/composition/manifest.rs` — 450 LOC Rust:
- `BiomeManifest`, `CompositionGraph`, `CompositionKind`, `CompositionReadiness`
  types compatible with toadStool's `toadstool_core::manifest` v1 schema
- `load_biome_manifest()` — parse + structural validation
- `validate_manifest()` — cross-reference members, detect dependency cycles
- `topological_waves()` / `topological_order()` — Kahn's algorithm for
  wave-parallel startup ordering
- `resolve_compositions()` — priority-sorted composition plans
- `global_start_order()` — deduplicated cross-composition start sequence
- `reconcile_with_live()` — probe live sockets against manifest declarations

### 2. eastGate biome.yaml Manifest

`config/biome-eastgate.yaml` — 14 primals, 3 compositions:
- **tower-atomic** (priority 0): biomeos → {beardog, skunkbat, songbird} → swarmvine
- **nest-atomic** (priority 10): {nestgate, rhizocrypt} → loamspine → sweetgrass
- **node-atomic** (priority 20): toadstool → coralreef → barracuda

With capability declarations, gossip events, source paths, security policy
(crypto_required: true), and federation peers (6 gates).

### 3. nucleus_launcher Wiring

- `--biome <path>` flag for manifest-driven lifecycle
- `reconcile` subcommand for live state reconciliation
- Reports composition readiness per sub-graph

### 4. exp122 — Manifest Composition Lifecycle

Experiment validates end-to-end: parse → structure → ordering → resolution → live reconciliation.
**37/37 PASS** on eastGate:
- 14/14 primals ALIVE
- Tower READY (5/5), Nest READY (4/4), Node READY (3/3)
- biomeos starts first in global order
- All dependency edges respected

### 5. spine.list Routing Gap CLOSED

`spine.list` routes correctly through Neural API → loamSpine (returns `{"count":0,"spine_ids":[]}`).
Last known routing gap is resolved.

## Test Results

| Suite | Result |
|-------|--------|
| `composition::manifest` unit tests | **12/12 PASS** |
| exp122 live validation | **37/37 PASS** |
| Existing workspace tests | **clean** (no regressions) |

## Files Changed

| Path | Change |
|------|--------|
| `ecoPrimal/src/composition/manifest.rs` | **NEW** — biome.yaml parser + lifecycle |
| `ecoPrimal/src/composition/mod.rs` | Added `pub mod manifest` |
| `config/biome-eastgate.yaml` | **NEW** — eastGate manifest |
| `experiments/exp122_manifest_composition_lifecycle/` | **NEW** — lifecycle experiment |
| `ecoPrimal/Cargo.toml` | Added `serde_yaml_ng` dependency |
| `Cargo.toml` | Workspace: added `serde_yaml_ng`, exp122 member |
| `ecoPrimal/src/bin/nucleus_launcher/main.rs` | `--biome` flag + `Reconcile` subcommand |
| `CONTEXT.md` | Updated to Wave 157g |
| `README.md` | Updated to Wave 157g |

## Architecture Note

primalSpring defines its own `BiomeManifest` type rather than depending on
`toadstool-core` directly. This is intentional: toadStool is an upstream primal
with 5 divergent `BiomeManifest` structs being converged. Once toadStool ships
a single canonical crate, primalSpring should re-export from it. The types are
serde-compatible — same YAML parses identically.

## Open Items (from blurb)

| Item | Status | Notes |
|------|--------|-------|
| biome.yaml manifest consumed | **DONE** | This handoff |
| Composition start/stop lifecycle | **PROTOTYPED** | exp122 validates; full executor pending biomeOS `nucleus.start` |
| spine.list routing gap | **CLOSED** | Routes through Neural API to loamSpine |
| 4 divergent BiomeManifest → 1 | **UPSTREAM** | toadStool convergence (their S376+) |
| Composition execution (biomeOS) | **UPSTREAM** | biomeOS must consume manifest for `nucleus.start` |
| swarmVine socket discovery | **UPSTREAM** | biomeOS connects `.tarpc.sock` instead of `.sock` |
| sourDough CI wiring | **UPSTREAM** | sporeGate + sourDough team |
| songBird MeshRelay | **UPSTREAM** | songBird team |

## Downstream Impact

- Other springs can reference `config/biome-eastgate.yaml` as a template for
  their own gate manifests
- `composition::manifest` module is public API — springs can consume it for
  composition lifecycle validation
- `nucleus_launcher reconcile` provides gate health reporting for any manifest
