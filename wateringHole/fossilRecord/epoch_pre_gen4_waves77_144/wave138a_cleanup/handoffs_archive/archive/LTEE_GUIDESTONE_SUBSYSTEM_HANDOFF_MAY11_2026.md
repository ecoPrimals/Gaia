<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# LTEE GuideStone Subsystem Handoff

**Date**: May 11, 2026 (reconstructed May 13 from ecosystem state + TARGETED_GUIDESTONE_STANDARD)
**From**: primalSpring (coordination)
**To**: lithoSpore / Foundation / spring teams
**Status**: Active

---

## Summary

The LTEE (Long-Term Evolution Experiment) GuideStone is the first Targeted
GuideStone artifact — a self-contained, portable composition that proves
LTEE scientific claims using sovereign Rust+GPU compute from the ecoPrimals
stack. This handoff documents the subsystem architecture, module assignments,
and spring-paper mapping.

---

## Architecture

Three-tier execution model per the Targeted GuideStone Standard:

| Tier | Role | Implementation |
|------|------|----------------|
| Tier 1 | Python baseline | lithoSpore `expected/` JSON + Python notebooks |
| Tier 2 | Rust CPU validation | Spring validation binaries via barraCuda CPU |
| Tier 3 | GPU sovereign dispatch | barraCuda GPU via toadStool + coralReef |

## Science Modules (7)

| Module | Paper | Spring Owner | Tier Status (May 13) |
|--------|-------|-------------|---------------------|
| 1 — `ltee-fitness` | Wiser 2013 (power-law fitness) | groundSpring (B2) | **Tier 2 LIVE** |
| 2 — `ltee-mutations` | Barrick 2009 (mutation accumulation) | groundSpring (B1) | **Tier 2 LIVE** |
| 3 — `ltee-genomics` | Tenaillon 2016 (mutation accumulation) | wetSpring (B7) | **Tier 2 COMPLETE** |
| 4 — `ltee-metabolism` | Anderson 2004 (fitness landscapes) | hotSpring (B2) | Tier 1 STARTED |
| 5 — `ltee-evolution` | Barrick 2009 (mutation dynamics) | neuralSpring (B1) | Tier 1 STARTED |
| 6 — `ltee-proteomics` | (queue — protein abundance) | healthSpring | Not started |
| 7 — `ltee-ecology` | (queue — community dynamics) | ludoSpring | Not started |

## Data Sources

All datasets from public repositories with documented accession numbers:

| Dataset | Source | Accession | Status |
|---------|--------|-----------|--------|
| Wiser 2013 fitness data | Dryad | `fitness_data.csv` | Fetched, BLAKE3 hashed |
| Barrick 2009 mutations | NCBI/Dryad | `mutation_parameters.json` | Fetched, BLAKE3 hashed |
| Tenaillon 2016 genomes | NCBI SRA | 264 genomes | Fetched by wetSpring |

## Ecosystem Integration

- **lithoSpore**: Module host. 6/7 modules at Tier 2 LIVE (May 13). ecoBin compliant.
  `litho-core` shared libraries extracted (`discovery`, `harness`, `stats`).
- **Foundation**: Workload execution. 10/10 threads active.
  CI thread-index validation fixed. Schemas updated.
- **plasmidBin**: Binary depot for cross-arch ecoBin builds. Idempotent harvest
  with post-harvest validation. Checksum desync resolved.
- **primalSpring**: Composition validation. 414-method registry, wire routing
  fixed (security.audit_log→defense, crypto base64 encoding).

## Spring-Paper Assignments (36 total across 6 springs)

The full paper queue is tracked in `primalSpring/docs/PRIMAL_GAPS.md` under
per-spring LTEE sections. The assignment model follows niche specialization:

- **groundSpring**: Foundational fitness/mutation papers (direct LTEE core)
- **wetSpring**: Genomic-scale analyses (sequence data, mutation accumulation)
- **hotSpring**: Thermodynamic/metabolic fitness landscapes
- **neuralSpring**: Evolutionary dynamics modeling (ML-adjacent)
- **healthSpring**: Proteomics and cellular composition
- **ludoSpring**: Community dynamics and game-theoretic evolution

## Remaining Work

1. Modules 4-7 need Tier 1 Python baselines completed
2. Module 3 at Tier 2 — needs Tier 3 GPU promotion path
3. `liveSpore.json` deployment tracking not yet wired
4. Provenance chain (braid references) needs sweetGrass integration
5. Cross-arch ecoBin bundle not yet composed (pending full Tier 2 coverage)

## References

- Standard: `TARGETED_GUIDESTONE_STANDARD.md`
- lithoSpore deep debt: `handoffs/CATHEDRAL_DEEP_DEBT_AUDIT_MAY13_2026.md`
- Foundation execution: `handoffs/PROJECTNUCLEUS_SHADOW_RUN_EXECUTION_MAY13_2026.md`
- Per-spring LTEE gaps: `primalSpring/docs/PRIMAL_GAPS.md`
