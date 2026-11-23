# Wave 55b: PostPrimordial Checkpoint — primalSpring

**Date**: May 27, 2026
**Author**: primalSpring / eastGate
**Scope**: Local debt resolution + metrics alignment + wateringHole update

---

## Summary

Wave 55b closes the local debt sweep within primalSpring before the next wave
cycle. All code, documentation, and validation artifacts are now aligned to
postPrimordial canonical metrics.

## Canonical Metrics (as of Wave 55b)

| Metric | Value |
|--------|-------|
| Registered methods | **460** (+2 nucleus.ingest_spore, nucleus.emit_spore) |
| Signal graphs | **15** (+1 nest_ingest_spore) |
| Validation scenarios | **56** (10 tracks, 3 tiers) |
| Experiments | **93** (21 tracks) |
| Deploy graphs | **96** (81 deploy + 15 signal) |
| Lib tests | **813** (797 pass, 16 live-tier) |
| Clippy warnings | **0** (pedantic + nursery) |
| Runtime deps | **16** |

## Code Changes

1. **Signal dispatch parity**: `s_signal_dispatch_parity.rs` expanded 14→15
   signals. `nest.ingest_spore` added to both SIGNALS table and SIGNAL_GRAPHS
   test table. Full dispatch + structural parity across all 15 graphs.

2. **PostPrimordial path cleanup**: `biomeos-cli` → `biomeos/src/modes/` path
   refs updated. exp114 hardcoded `/run/user/1000` replaced with
   `tolerances::biomeos_socket_dir()`. `neural_dispatch` threshold 458→460.

3. **Lint hygiene**: All remaining `#[allow(clippy::...)]` in production code
   migrated to `#[expect(..., reason)]` (s_tower_cns, harness/mod.rs).

4. **Catalog**: `experiment_catalog.json` regenerated (93 experiments,
   postprimordial_glacial track added: exp112-115).

## Documentation Sweep

Updated 15+ docs to canonical metrics (460/15/56/93/96/813):
- README, CONTEXT, PRIMAL_GAPS, DOWNSTREAM_PATTERN_GUIDE
- CROSS_SPRING_PARITY_SCORECARD, VALIDATION_TIERS
- CROSS_SPRING_EVOLUTION, NUCLEUS_VALIDATION_MATRIX
- SOVEREIGNTY_INFRASTRUCTURE_STATUS, COMPUTE_TRIO_EVOLUTION
- experiments README, DOWNSTREAM_PATTERN_GUIDE signal inventory

## wateringHole Updates

- TEMPORAL_ECOLOGICAL_REVIEW: metrics updated, phase→Wave 55b
- PRIMAL_REGISTRY: updated to Wave 55b metrics + niche climate status
- GLACIAL_SHIFT_READINESS: primalSpring metrics updated

## Niche Climate Status (unchanged from absorption)

| Gate | Status |
|------|--------|
| NC-1 Spore Gateway | **COMPLETE** — biomeOS v3.81 code done, deploy pending |
| NC-2 Multi-Gate Mesh | **IN PROGRESS** — Songbird TCP fix, cellMembrane knot-dns |
| NC-3 cellMembrane Sovereignty | **CONSUMED** — 95.8% coverage, typed errors |
| NC-4 Spring NUCLEUS Depth | **ADVANCING** — 166 tests, wire-native discovery |
| NC-5 Stadial Gate | **UNBLOCKED** — gated on v3.81 VPS deploy + column U |

## Remaining Known Gaps

- ~~biomeOS NC-1.4: swap to `pseudospore-core` for canonical validation~~ **RESOLVED v3.81**
- biomeOS emit pipeline: unpack content from receipt
- Live gate deployments: ops coordination for ironGate/southGate
- `capability_registry.toml` at 1034 lines (config file, not code — accepted)
- Fossil docs (sporeprint, whitePaper, CHANGELOG history) retain historical metrics

## Next Steps

- Wave 56+: absorb next ecosystem evolution cycle
- NC-1 completion: biomeOS `pseudospore-core` swap
- Gate deployment coordination: cellMembrane ironGate, neuralSpring southGate
- Stadial gate readiness assessment
