# AAR — westGate: Synapse + NCBI API Keys & NF Data Portal Acquisition

**Gate**: westGate  
**Wave**: 155f (continuing)  
**Date**: 2026-08-02  
**Scope**: API key configuration, NF Data Portal (Synapse) data acquisition  
**Duration**: ~10 minutes credential setup + download + provenance

---

## What Happened

The user completed two registrations and provided credentials:

1. **NCBI API Key** — Created via NCBI account (`ecoprimal@orcid`), linked to ORCiD `0009-0004-2141-0321`. Key stored locally in `~/.ncbi_api_key` (chmod 600). Increases Entrez/SRA rate limit from 3 req/s to 10 req/s.

2. **Synapse Personal Access Token** — Created via Synapse account (`ecoPrimal`). Stored in `~/.synapseConfig` (standard synapseclient location, chmod 600). Scopes: view, download, modify.

**Neither credential is committed to git.**

With the Synapse PAT, we immediately pulled the NF Data Portal data that was blocking tideGlass Module 7.

---

## NF Data Portal — What We Downloaded

| Category | Files | Size | Synapse IDs |
|----------|-------|------|-------------|
| NF1 HTS primary screening (8K compounds + structures) | 1 | 27.2 MB | syn8299192 |
| NF1 drug response (>19%) | 1 | 284 KB | syn7286293 |
| NF1 dose-response nonlinear fits | 595 | 554 KB | syn8395313–syn8395970 |
| NF1 dose-response keys/docs | 4 | 200 KB | syn8371217–syn8395266 |
| NF2 Synodos drug screen (processed + raw) | 2 | 1.5 MB | syn6138237, syn6138251 |
| NF2 kinomics peptide-level (211 MB) | 49 | 618 MB | syn6179345–syn6182638 |
| NF2 kinomics protein-level | 1 | 6.1 MB | syn6181167 |
| NF2 kinomics differential expression | 1 | 2.3 MB | syn6182317 |
| NF2 kinomics baseline (LFQ + iTRAQ) | 2 | 1.0 MB | syn6182623, syn6182638 |
| Dose-response Prism + curve fits | 2 | 3.5 MB | syn8371219, syn8371220 |
| **TOTAL** | **658** | **666 MB** | |

### Provenance Results

| Pipeline Step | Pass Rate |
|---------------|-----------|
| BLAKE3 hash | 658/658 |
| nestGate CAS | 658/658 |
| rhizoCrypt DAG | 658/658 |
| loamSpine Merkle cert | 658/658 |
| bearDog Ed25519 sign | 658/658 |
| sweetGrass attribution | 658/658 |

**100% full provenance on all 658 files.**

---

## tideGlass Module Status (Updated)

| Module | Data Source | Status |
|--------|-----------|--------|
| Module 1 — Drug compound libraries | ChEMBL 37 (15 GB), PubChem (11 GB), ZINC20 (160 MB) | COMPLETE |
| Module 2 — Gene expression signatures | LINCS L1000 (20 GB), GTEx V8 (2.4 GB), GEO SOFT (3 GB) | COMPLETE |
| Module 3 — Protein structures | PDB mmCIF (88 GB), PDB70 (27 GB) | COMPLETE |
| Module 4 — Disease ontology | MONDO (103 MB), Reactome (96 MB) | COMPLETE |
| Module 5 — Cancer reference | TCGA Xena (449 MB), GEO SOFT cancer (3 GB) | COMPLETE |
| Module 6 — Genomic reference | RefSeq GRCh38 (981 MB), NCBI Gene (7 GB), UniProt (148 GB) | COMPLETE |
| Module 7 — NF Data Portal | NF1 drug screen + NF2 kinomics (666 MB) | **COMPLETE** |

**All 7 tideGlass modules now have base data on ZFS with full provenance.**

---

## westGate Data Federation — Current State

| Metric | Value |
|--------|-------|
| ZFS used | 356 GB |
| ZFS available | 50.4 TB |
| ZFS utilization | 0.70% |
| Datasets on ZFS | 32 directories |
| CAS objects | 5,500+ |
| Total files with provenance | ~260K |
| NUCLEUS status | 13/13 running |
| ZFS pool health | ONLINE, 0 errors |

---

## Remaining API Keys / Registrations

| Service | Status | Impact |
|---------|--------|--------|
| NCBI (Entrez/SRA) | DONE — key `cbab...4009` | 10 req/s rate limit |
| Synapse (NF Portal) | DONE — PAT configured | Full download access |
| Clue.io (LINCS CMap API) | PENDING | Connectivity Map query access |
| BindingDB | PENDING (browser-only download) | Drug-target binding data |
| EcoCyc | PENDING (academic license) | E. coli metabolism |
| BRENDA | PENDING (registration) | Enzyme kinetics |

---

## What Worked

1. **Synapse client setup was instant** — `pip install synapseclient`, single dotfile config, authenticated on first try.
2. **Table query API is powerful** — SQL-like queries against Synapse file views let us surgically pull exactly the processed data tideGlass needs, not terabytes of raw FASTQ.
3. **Provenance pipeline handled 658 files in 17 seconds total** — the three-pass approach (root files, NF1 dose-response, NF2 kinomics) kept things organized.
4. **NCBI API key is trivially configured** — one dotfile, immediate effect.

## What Didn't Work

1. **NF2 expression/proteomics in processed tabular format** — Query returned 0 results because these are stored as raw FASTQ/BAM, not CSV/TSV. The actual analysis results may be in separate Synapse projects or supplementary tables.
2. **Synapse API deprecation warnings** — `synapseclient` 4.13.0 has deprecated `syn.get()`, `syn.tableQuery()`, and `syn.getUserProfile()` in favor of a new model-based API. Functional now but will need updating before 5.0.

## What Needs Evolution

1. **Synapse data should be queryable via biomeOS** — A `synapseSpring` primal or Neural API endpoint could expose Synapse table queries through the mesh, letting any gate access NF Portal data with provenance baked in.
2. **NCBI API key should be mesh-shared** — Rather than each gate maintaining its own `~/.ncbi_api_key`, the key should be stored in `bearDog` or `rhizoCrypt` and injected into API calls by the requesting primal.
3. **NF Portal has 490K+ files** — We grabbed the processed analysis subset (658 files, 666 MB). The raw sequencing data is terabytes and should only be fetched when specific analyses require it (pull-on-demand, not pre-fetch).

---

**Bottom line**: tideGlass Module 7 is now COMPLETE. All 7 modules have base data on ZFS with full provenance. westGate's data-braided scientific database now spans 32 datasets, 356 GB, ~260K files, all with BLAKE3 + CAS + DAG + Merkle + Ed25519 + attribution provenance. The user's NCBI and Synapse accounts are configured for future acquisitions.
