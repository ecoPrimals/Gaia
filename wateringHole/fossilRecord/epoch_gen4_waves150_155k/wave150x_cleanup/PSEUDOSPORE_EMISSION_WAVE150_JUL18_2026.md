# pseudoSpore Emission — Wave 150 (Jul 18, 2026)

**Team:** lithoSpore/pseudoSpore on ironGate
**Action:** First ecosystem-wide pseudoSpore emission from all 7 science springs

## Emission Summary

| Spring | Artifact | Tarball | Files | BLAKE3 |
|--------|----------|---------|-------|--------|
| hotSpring | CompChem-GuideStone v1.6.1 | (pre-existing) | — | — |
| groundSpring | LTEE-Measurement v1.0.0 | **279 KB** | 252 | `b130f321...` |
| airSpring | Agricultural-Meteorology v1.0.0 | **568 KB** | 278 | `acaf7f30...` |
| healthSpring | Clinical-PKPD v1.0.0 | **375 KB** | 374 | `38983ea6...` |
| neuralSpring | ML-Surrogates v1.0.0 | **16 MB** | 256 | `34b53568...` |
| wetSpring | Life-Science-Analytics v1.0.0 | **782 KB** | 180 | `a600c5f2...` |
| ludoSpring | Game-Science v1.0.0 | **61 KB** | 50 | `07374084...` |

**Total registry entries:** 7 (1 COMPLETE, 6 PENDING module validation)
**All tarballs email-safe** except neuralSpring (16 MB — SRA-style manifest needed for model weights).

## Audit Results (all 6 new spores)

All pass with MEDIUM recommendations:
- **DATA-MISSING**: No raw `data/` directory (benchmark outputs only, not zero-trust verifiable)
- **PROVENANCE-GAPS**: `ferment_transcript.json` has empty `dag_session_id` (needs sweetGrass braid)

No HIGH findings. No integrity failures.

## Old Patterns Found During Emission

### P0 — Fix Before v2.0 Promotion

1. **Bash orchestration everywhere**: hotSpring has **114 .sh files**, airSpring has `run_all_baselines.sh` at root, healthSpring `control/run_all.sh`, groundSpring 6 scripts. These should evolve to UniBin scenarios or Rust validators.

2. **Broken workspaces**: groundSpring `cargo test` fails (missing `primalTools/bingoCube/nautilus` path dependency). ludoSpring requires rustc 1.92 vs toolchain 1.87. Cannot run module validation until fixed.

3. **Duplicate/stale profiles**: groundSpring has root `domain_profile.toml` (measurement-uncertainty) AND `validation/domain_profile.toml` (LTEE-specific). Only root profile should exist; stale one causes confusion.

### P1 — Evolve This Quarter

4. **No root `scope.toml` in any spring**: All springs lack `scope.toml` at their root. The emit pipeline generates one in the pseudoSpore, but the spring itself has no self-describing artifact manifest. Each spring should have `scope.toml` as the canonical "what I produce" declaration.

5. **Python baselines not connected to emission**: 29 groundSpring baselines + airSpring/healthSpring golden values exist as standalone benchmark JSON files. No automated "run baseline → compare → populate validation.json" pipeline exists in-spring. Each spring needs a `validate` entry point that materializes module results.

6. **External pseudoSpore tarballs**: hotSpring v1.5/v1.6/v1.7.0 are documented but live outside the repo (Discord/cellMembrane). Need canonical archive location in fossilRecord or a content-addressed registry URI.

7. **FASTQ data scoping**: wetSpring has 5.2 GB of FASTQ in `data/paper_proxy/`. The pseudoSpore emission correctly excluded this, but there's no SRA accession manifest for lazy-fetch. Needs `data_manifest.toml` with accession IDs.

### P2 — Technical Debt, Low Urgency

8. **`Makefile`/`justfile` in neuralSpring**: Should evolve to Rust-native orchestration.

9. **`composition_nucleus.sh` in fossilRecord**: wetSpring, neuralSpring, ludoSpring all have this fossil. Harmless but should be documented as historical.

10. **Test count discrepancies**: README vs sporeprint vs actual `cargo test` counts diverge across springs. Each spring needs a CI gate that updates its test count in domain_profile.toml.

11. **No `index_map.toml`**: Translation mapping (domain concept → computation module) is disabled in all profiles. When enabled, it would allow cross-spring correlation analysis (e.g., both groundSpring and airSpring validate FAO-56 ET₀).

## Infrastructure Changes

- `pseudospores/registry.toml`: Updated from 1 → 7 entries
- `ingest_pseudospore::tests::existing_registry_toml_parses`: Evolved from hardcoded `== 1` to `>= 1` with named lookup (was a test fragility pattern — old pattern #10-style)
- All tests pass, 0 clippy warnings

## Next Steps

1. **Spring teams populate `validation.json`**: Each PENDING spore needs module validation results from its spring's validator
2. **groundSpring team fixes `bingoCube/nautilus`** dependency to unblock `cargo test`
3. **sporePrint gallery pages** for all 7 pseudoSpores (P1)
4. **Upstream cascade** for overwatch audit
