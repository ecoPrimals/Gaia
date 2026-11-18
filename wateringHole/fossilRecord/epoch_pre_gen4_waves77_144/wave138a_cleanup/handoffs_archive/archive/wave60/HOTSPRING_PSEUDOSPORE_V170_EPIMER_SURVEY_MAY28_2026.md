# hotSpring: pseudoSpore v1.7.0 — Epimer Survey + Mechanistic Comparison

**Date**: 2026-05-28
**From**: hotSpring (Exp 220 — CAZyme FEL Biomolecular MD)
**Artifact**: `pseudoSpore_hotSpring-CompChem-GuideStone_v1.7.0.tar.gz` (843 MB)
**Status**: Shipped (Desktop tarball ready for Discord)

## Summary

pseudoSpore v1.7.0 is the second major science artifact from hotSpring's CAZyme FEL
campaign. It evolves v1.6.1 (the baseline 6-module FEL handoff) into a comprehensive
22-module survey covering:

- **4 free sugar epimer baselines** (lyxose, glucose, mannose, galactose)
- **2 GH10 subsite analyses** (-2 and +1 subsites of PDB 2D24)
- **GH11 inverting xylanase** (PDB 1XYN, -1 subsite — mechanistic comparison)

Lineage: `v1.5.0 → v1.6.0 → v1.6.1 → v1.7.0` (immutable evolution chain).

## New Science (Modules 09-16)

| Module | System | Simulation | Key Result |
|--------|--------|-----------|------------|
| 09 | Free lyxose 1D+2D | 10+20 ns | C2 epimer of xylose baseline |
| 10 | Free glucose 1D+2D | 10+20 ns | Hexose comparison |
| 11 | Free mannose 1D+2D | 10+20 ns | Hexose comparison |
| 12 | Free galactose 1D+2D | 10+20 ns | Hexose comparison |
| 13 | GH10 -2 subsite 1D+2D | 10+20 ns | Subsite distortion propagation |
| 14 | GH10 +1 subsite 1D+2D | 10+20 ns | Subsite distortion propagation |
| 15 | GH11 -1 subsite 1D | 10 ns | Inverting vs retaining comparison |
| 16 | GH11 -1 subsite 2D | 20 ns | Inverting vs retaining comparison |

**Total new simulation time**: ~420 ns
**All simulations**: CHARMM36-jul2022 + PLUMED 2.10 + GROMACS 2026.0

## Validation

- **185/187 checks PASS** (2 pre-existing cross-landscape warnings from v1.6.1)
- **162 BLAKE3 files** verified
- **47 cross-check fields** verified (pipeline-derived metadata, 0 mismatches)
- All 18 FEL parity checks: 0.00 kJ/mol RMSD (self-consistent)

## Infrastructure Changes

### nest-validate (main.rs)
- `guidestone_finalize`: systems array expanded from 4 to 18 entries
- `guidestone_validate`: parity_modules expanded from 4 to 18 entries
- `guidestone_run_pipeline`: systems array expanded from 4 to 18 entries
- Module population map expanded to 17 entries (includes all new modules)
- Graceful skip for missing systems (WARN instead of exit)

### New Files
- 14 `target.toml` files in pseudoSpore modules (09-16)
- 12 PLUMED config templates in `configs/` directory
- 4 sugar PDB structures in `structures/`
- GH11 structures: `1XYN.pdb`, `xylose_gh11_m1.pdb`, `complex_gh11.pdb`

### Build Scripts (control/gromacs_fel/)
- `build_sugars.py`: RDKit conformer generation with CHARMM36 RTP atom naming
- `run_epimer_pipeline.sh`: Full EM→NVT→NPT equilibration for 4 epimers
- `run_epimer_metad.sh`: 1D+2D metadynamics for all 4 epimers
- `build_subsite_systems_v3.sh`: Independent -2/+1 subsite system assembly
- `build_gh11_system.sh`: 1XYN + xylose system build with structural placement

## Downstream Expectations

### primalSpring
- Audit v1.7.0 artifact for pseudoSpore 2.0 NUCLEUS elevation
- nest-validate ownership split (domain science vs envelope vs gateway)
- provenance_trio integration pending (rhizoCrypt/loamSpine/sweetGrass)

### Alistaire / ABG
- v1.7.0 provides the mechanistic comparison dataset for GH10 vs GH11
- Epimer survey enables cross-sugar FEL comparison (xylose vs lyxose/glucose/mannose/galactose)
- AutoDock Vina docking ↔ FEL correlation now has expanded reference data

### biomeOS
- `biomeos nucleus ingest` pathway documented in DEPLOY.md
- provenance_trio_status remains "pending" until primalSpring elevates

## Provenance

```
braid_id: urn:braid:hotspring-compchem-guidestone-v1.7.0
parent:   urn:braid:hotspring-compchem-guidestone-v1.6.1
era:      pipeline_derived (era 2)
target:   nucleus_nest_deploy (era 3, v2.0+)
```
