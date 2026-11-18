# hotSpring Handoff — CAZyme FEL Biomolecular MD Evolution

**Date:** May 25, 2026 (updated from May 24)
**From:** hotSpring
**To:** primalSpring (audit), Alistaire (domain validation), barraCuda (shader evolution), ludoSpring/petalTongue (visualization)
**Experiment:** 220
**Status:** Tier 0 COMPLETE — handoff-ready pseudoSpore v1.1.1, lithoSpore v2.1.0

---

## Summary

hotSpring has completed a full CAZyme conformational Free Energy Landscape (FEL)
validation pipeline for PDB 2D24 (GH10 xylanase, β-D-xylopyranose substrate).
The work extends the validated plasma MD stack (Exp 001–219) into biomolecular
enhanced sampling, establishing GROMACS+PLUMED as the industry control target.

**Collaborators:**
- Alistaire — domain expert (CAZyme biochemistry, QM/MM, metadynamics)
- Mark — NSF HPC access (Texas A&M ACES, A100 GPUs)

**Scientific goal:** Validate free energy landscapes for carbohydrate puckering
in enzyme active sites. Enzyme-bound xylose shows 1-5 kJ/mol barrier reduction
vs free xylose across all conformational transitions.

---

## What Was Delivered

### pseudoSpore v1.1.1 (`~/Desktop/pseudoSpore_hotSpring-CAZyme-FEL_v1.1.1.tar.gz`)

5-module validation artifact:

| Module | System | CV | Status |
|--------|--------|-----|--------|
| xylose-puckering-fel | Free β-D-xylose in water | Cremer-Pople θ (1D) | PASS |
| enzyme-bound-puckering | GH10 -1 subsite | Cremer-Pople θ (1D) | PASS |
| free-xylose-2d | Free β-D-xylose in water | Cremer-Pople qx/qy (2D) | PASS |
| enzyme-bound-2d | GH10 -1 subsite | Cremer-Pople qx/qy (2D) | PASS |
| ala-dipeptide-fel | Alanine dipeptide (control) | Ramachandran φ/ψ | PASS |

### lithoSpore v2.1.0

Full deployment chassis with:
- Stripped `litho` + `cazyme-fel` binaries (5.9 MB + 3.7 MB)
- Python Tier 1 validator (`tier1_validator.py`)
- Auto-generated RELEASE.md from provenance braids
- Self-auditing: `litho audit --path proof/ --verbose` → 10/10 PASS

### Automation Pipeline (lithoSpore CLI)

| Command | Function |
|---------|----------|
| `litho emit-pseudospore` | Assembles artifact from source — auto-figures, PDB serial extraction, BLAKE3 sealing |
| `litho audit` | 10-check pre-handoff validation (integrity, config fidelity, topology cross-ref, derivation, figures, versions, provenance, MDP headers) |
| `litho promote` | pseudoSpore → lithoSpore chassis (stripped binaries, env capture, RELEASE.md) |
| `litho translate-config` | Domain↔computation index translation for PLUMED configs |
| `litho ingest-pseudospore` | Validates incoming pseudoSpore artifacts |

---

## Key Science Results

- **Free xylose**: Global minimum at θ≈5° (⁴C₁ chair). Barrier to ¹C₄ ~25 kJ/mol.
- **Enzyme-bound**: All barriers reduced 1-5 kJ/mol. Active site pre-organizes for catalytic itinerary.
- **2D landscapes**: qx/qy maps show conformational pathway differences between free/bound states.
- **Alanine dipeptide**: Control system validates metadynamics setup (known φ/ψ landscape).

---

## What's Needed from Ecosystem

### Alistaire (domain validation)

- Review pseudoSpore v1.1.1 — all data, configs, index translations included
- Confirm Cremer-Pople atom ordering (C1-C2-C3-C4-C5-O5) and PDB serial assignments
- Validate scientific interpretation against Iglesias-Fernández 2015

### barraCuda (primal evolution — Phase 1+)

4 new WGSL shaders for bonded force field terms:
- `harmonic_bond.wgsl` — V(r) = ½k(r - r₀)²
- `harmonic_angle.wgsl` — V(θ) = ½k(θ - θ₀)²
- `dihedral_torsion.wgsl` — V(φ) = Σ kₙ(1 + cos(nφ - δₙ))
- `improper_dihedral.wgsl` — V(ψ) = ½k(ψ - ψ₀)²

### ludoSpring / petalTongue (visualization)

FEL visualization — 2D heatmap, 3D surface, CV trajectory overlay, convergence diagnostics.

---

## Compute Tier Strategy

| Tier | Hardware | Role |
|------|----------|------|
| Local dev | strandGate RTX 3090 | GROMACS control + barraCuda dev |
| biomeGate | 2× Titan V + RTX 5060 | Sovereign dispatch production |
| HPC | ACES A100 (NSF) | Scale validation with Alistaire |

---

## Phase Status

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | GROMACS+PLUMED industry control (5 modules) | **✅ COMPLETE** |
| 1 | barraCuda bonded FF shaders | Pending |
| 2 | hotSpring topology reader + MD loop | Pending |
| 3 | Metadynamics bias layer | Pending |
| 4 | Parity validation (barraCuda FEL ≈ GROMACS FEL) | Pending |

---

## Audit History

| Version | Audit Result | Key Changes |
|---------|-------------|-------------|
| v0.6.0 | FAIL — lyxose structure, wrong indices | Initial prototype |
| v0.7.0 | PASS with 3 recommendations | Alistaire review incorporated |
| v0.8.0 | PASS — overnight campaign | 5 modules, 2D FELs added |
| v0.9.0 | PASS — 9 findings | index_map.toml, translate-config |
| v1.0.0 | PASS — 7 observations (cosmetic) | Full automation pipeline |
| v1.1.0 | PASS — 4 observations (cosmetic) | Fossilize + rebuild from CLI |
| v1.1.1 | **10/10 PASS — zero findings** | Visual evidence, tier1 validator, --help |

---

## Key References

- Iglesias-Fernández et al. (2015) ACS Catal. — GH10 xylanase conformational itinerary
- Ardèvol & Rovira (2015) JACS — CAZyme catalytic itinerary (Fig. 10)
- Alonso-Gil (2019) thesis — QM/MM equations (Ch. 2.2–2.4)
- PDB 2D24 — GH10 xylanase crystal structure with bound xylose
- GROMOS 45a4 / CHARMM36 force fields
- Wei-Tse Hsu — GROMACS enhanced sampling tutorials

---

## Gaps

| Gap | Description | Severity |
|-----|-------------|----------|
| GAP-HS-111 | Bonded FF terms + topology reader + metadynamics (barraCuda Phase 1) | Medium |
| GAP-HS-112 | petalTongue FEL visualization evolution | Low |
