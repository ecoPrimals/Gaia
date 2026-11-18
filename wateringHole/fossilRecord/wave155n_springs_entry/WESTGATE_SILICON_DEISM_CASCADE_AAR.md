# AAR: westGate Silicon Deism Cascade — Data Federation at 343 GB

**Date**: Aug 2, 2026 09:17 EDT
**Gate**: westGate
**Wave**: 155n (silicon deism + publication phase)
**Author**: westGate overwatch (agent-assisted)
**biomeOS**: v4.56.0, 13/13 active

---

## TL;DR

Cascade absorbed: biomeGate GPU crankshaft (3 VFIO GPUs, 44-experiment matrix, silicon
deism), strandGate cross-vendor arXiv data (RTX 3090 + RX 6950 XT), whitePaper silicon
deism hardware guide + sovereign identity garden + arXiv multi-vendor tables. westGate
data federation significantly ahead of blurb numbers: **343 GB on ZFS** (blurb shows
71.4 GB — stale from pre-overnight downloads). 22 datasets, 257K+ files, 4,788 CAS
objects. All 3 overnight downloads completed and ingested with full provenance.

---

## Cascade Absorbed

| Repo | Commits | Key |
|------|---------|-----|
| wateringHole | +2 | biomeGate GPU crankshaft AAR, G34/G35 outer membrane spec |
| whitePaper | +4 | Silicon deism hardware guide, sovereign identity garden, arXiv Sections 3.4 multi-vendor |
| hotSpring | +3 | biomeGate revalidation spec, multi-GPU arxiv sweep, production run tuning |
| sporePrint | +1 | Demonstration era AAR, pseudospore hotspring-qcd content |

### biomeGate: Silicon Deism — Diesel Engine Sees All GPUs the Same

Three VFIO-bound GPUs spanning 10 years of NVIDIA silicon:

| GPU | Arch | SM | FP64 Ratio | VFIO Group | Role |
|-----|------|----|-----------|-----------|------|
| RTX 5060 | Ada/Blackwell | 89+ | 1:64 | Host | wgpu compute |
| Titan V | Volta (GV100) | 70 | **1:2** | `/dev/vfio/49` | Sovereign dispatch |
| K80 ×2 | Kepler (GK210) | 37 | **1:3** | `/dev/vfio/{35,36}` | Cross-gen quench |

Key insight: Titan V and K80 have HPC-grade FP64 (1:2 and 1:3 ratios vs consumer 1:64).
biomeGate is the only gate with native f64 silicon for validation — no DF64 polyfill needed.

44-experiment revalidation matrix staged across 6 phases. Exp 231 (K80 cross-gen quench)
is the first-ever hardware run on the replaced K80.

### strandGate: Cross-Vendor arXiv Data

RTX 3090 (NVIDIA SM86) + RX 6950 XT (AMD RDNA2) — same HMC, same physics, different vendors.
arXiv Section 3.4 (multi-vendor) is the last remaining section.

### whitePaper: Silicon Deism Hardware Guide

Comprehensive acquisition guide for expanding ISA coverage: Mac Mini M4 (ARM + Darwin),
Raspberry Pi 5 (resource-constrained), Orange Pi 5 (RISC-V), Star64 (RISC-V). Maps
the path from Tier 1 (atheistic) to Tier 2 (deistic) silicon independence.

---

## westGate Data Federation — Corrected Numbers

**The blurb shows 71.4 GB — this was stale from before overnight downloads completed.**

### Actual State: 343 GB on ZFS

| Dataset | Size | Files | Provenance |
|---------|------|-------|-----------|
| UniProt TrEMBL DAT | 110 GB | 1 | FULL |
| PDB mmCIF (full mirror) | 88 GB | 257,179 | Manifest + BLAKE3 |
| UniRef90 | 30 GB | 1 | FULL |
| TrEMBL FASTA | 38 GB | 1 | FULL |
| PDB70 HHsearch | 27 GB | 1 | FULL |
| LINCS L1000 | 20 GB | 6 | FULL |
| ChEMBL 37 | 15 GB | 2 | FULL |
| PubChem (SMILES, InChI-Key, Synonym, Mass) | 11 GB | 5 | FULL |
| NOAA GHCND | 3.5 GB | 3 | FULL |
| GTEx V8 | 2.4 GB | 4 | FULL |
| UniProt Swiss-Prot | 764 MB | 3 | FULL |
| PDB structures (506 individual) | 361 MB | 506 | FULL |
| SILVA 138.1 | 188 MB | 1 | FULL |
| ZINC20 SMILES | 160 MB | 110 | FULL |
| USDA NASS Census 2017 | 132 MB | 1 | FULL |
| MassBank NIST | 63 MB | 1 | FULL |
| PhysioNet MIT-BIH | 22 MB | 1 | FULL |
| LTEE REL606 | 5.8 MB | 1 | FULL |
| USGS earthquake monthly | 2.1 MB | 1 | FULL |
| AME2020 nuclear masses | 1.2 MB | 2 | FULL |
| **Total on ZFS** | **343 GB** | **257,830+** | **22 datasets** |

### ZFS Pool

| Metric | Value |
|--------|-------|
| Used | 343 GB |
| Available | 50.4 TB |
| Usage | 0.68% |
| CAS objects | 4,788 |
| Snapshots | 2 |

### Data Federation Progress vs Schedule

| Batch | Planned | Complete | Notes |
|-------|---------|----------|-------|
| Batch 1 | ~200 GB | ~172 GB | BindingDB, PubChem full SDF still pending (browser) |
| Batch 2 | ~160 GB | ~171 GB | UniRef90 + PDB70 + TrEMBL done early |
| Batch 3 | ~75 GB | ~1 GB | USDA, USGS, AME2020 done. EPA/BRENDA need registration |
| Batch 4 | ~212 GB | 0 | TCGA, AmeriFlux, IRIS next |
| Batch 5 | ~29 TB | 0 | AlphaFold, SRA — month-scale |

**Batches 1+2 are effectively complete.** We pulled forward TrEMBL and UniRef90 from later
batches because the bandwidth was available overnight.

---

## Dormant Spring/Garden Readiness

| Project | Data Ready | What's Needed |
|---------|-----------|---------------|
| **tideGlass** | LINCS L1000, PubChem, ChEMBL, ZINC20 | Phase 0 scaffold exists, data in CAS |
| wetSpring | UniProt, UniRef90, GTEx, SILVA, PDB, LTEE | Breseq + LTEE compute on strandGate |
| neuralSpring | UniRef90, PDB70, PDB mmCIF, TrEMBL | MSA + structure prediction data |
| hotSpring | PDB mmCIF, AME2020 | QCD production on strandGate/biomeGate |
| healthSpring | LINCS, ChEMBL, PubChem | Clinical + drug repurposing |
| groundSpring | USGS earthquake, NOAA GHCND | GIS data |
| airSpring | USDA NASS, NOAA GHCND | Atmospheric + agricultural |

---

## Next for westGate

| Priority | Action |
|----------|--------|
| **Batch 3** | GEO SOFT curated subset (~50 GB) — wetSpring |
| **Batch 3** | NIST PFAS reference data (~500 MB) — wetSpring PFAS |
| **Batch 4** | TCGA expression + clinical (~200 GB) — wetSpring, healthSpring |
| **Tooling** | Fix `bulk_ingest.py` timeout for 100GB+ files (hit on TrEMBL DAT) |
| **Dormant** | tideGlass Phase 0 activation — data is ready |

---

*Cascade absorbed. Silicon deism is live on biomeGate. westGate data federation at 343 GB
(4.8× ahead of blurb numbers), 22 datasets with full provenance, Batches 1+2 effectively
complete. 50.4 TB available. The sovereign data cloud model is proving out — every byte
grabbed at 1G, served forever at 10G, zero egress.*
