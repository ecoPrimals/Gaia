# westGate Data Federation — Download Schedule

**Gate**: westGate (ZFS raidz1, 50.7 TB available)
**Connection**: 1 Gbps fiber (residential — avoid saturation)
**Policy**: Download in batches, off-peak preferred, never >80% sustained for >1h
**Every byte with provenance = latent value (zero egress at 10G LAN)**
**Updated**: Aug 4, 2026 (stats current; dataset table reflects Sessions 1-3)

---

## COMPLETED (on ZFS with full provenance)

### Proteomics & Structural Biology (283 GB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| UniProt TrEMBL FASTA + DAT | 110 GB | 1 | UniProt FTP |
| PDB mmCIF (full mirror) | 88 GB | 257,179 | RCSB rsync |
| UniRef90 | 68 GB | 2 | UniProt FTP |
| AlphaFold v6 (46/46 ref proteomes, COMPLETE) | 79 GB | 46 | EBI FTP |
| PDB70 HHsearch profiles | 27 GB | 1 | MPI |
| InterPro protein-domain annotations | 13 GB | 1 | EBI FTP |
| NCBI CDD (Conserved Domain DB) | 4.4 GB | 1 | NCBI FTP |
| OrthoDB v11 gene orthology | 1.8 GB | 2 | OrthoDB |
| IntAct molecular interactions | 1.3 GB | 1 | EBI FTP |
| UniProt Swiss-Prot + proteomes | 876 MB | 5 | UniProt FTP |
| Ensembl Compara protein homologies | 198 MB | 1 | Ensembl FTP |
| Pfam-A domain HMMs | 399 MB | 1 | EBI FTP |
| PDB structures (506 individual) | 361 MB | 506 | RCSB |
| Tabula Muris FACS scRNA-seq atlas | 294 MB | 3 | Figshare |
| BioGRID protein interactions | 173 MB | 1 | BioGRID |
| ProteomeXchange PXD005353+PXD002089 | 15 KB | 2 | PRIDE API |
| STRING v12.0 human PPIs | 80 MB | 1 | STRING-DB |
| PDBe SIFTS mappings | 5.8 MB | 1 | EBI FTP |

### Genomics & Variants (27 GB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| NCBI Gene (Info+GO+Acc+gene2go+gene2pubmed) | 9.3 GB | 6 | NCBI FTP |
| NCBI Assembly summaries (RefSeq+GenBank) | 1.8 GB | 2 | NCBI FTP |
| dbSNP common variants (GRCh38) | 1.5 GB | 1 | NCBI FTP |
| RefSeq Human GRCh38 + GTF | 981 MB | 2 | NCBI FTP |
| GBIF backbone taxonomy | 926 MB | 1 | GBIF |
| Atlantic salmon genome Ssal_v3.1 | 715 MB | 1 | NCBI FTP |
| NCBI Bacteria assembly summary | 218 MB | 1 | NCBI FTP |
| ClinVar clinical variants | 184 MB | 1 | NCBI FTP |
| GENCODE v46 (GTF + transcripts) | 95 MB | 2 | EBI FTP |
| gnomAD v4.1 constraints | 91 MB | 1 | Google Cloud |
| GWAS Catalog (studies+ancestry+traits) | 184 MB | 4 | EBI FTP |
| GIAB HG001 benchmark (VCF + BED) | 135 MB | 2 | NCBI |
| NCBI Taxonomy | 72 MB | 1 | NCBI FTP |
| Ensembl GRCh38.113 (GTF + regulatory) | 69 MB | 2 | Ensembl FTP |
| ENCODE cCREs (1M elements) | 61 MB | 1 | SCREEN |
| PlasmoDB P. falciparum 3D7 (genome+GFF+proteome) | 35 MB | 3 | VEuPathDB |
| HGNC gene nomenclature | 16 MB | 1 | HGNC |
| GTDB bacterial+archaeal taxonomy | 9.7 MB | 2 | GTDB |
| SRA BioProject metadata (12 projects) | 1 MB | 13 | NCBI Entrez |

### Drug Discovery & Chemistry (48 GB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| LINCS L1000 Level 5 + metadata | 20 GB | 6 | NCBI GEO |
| ChEMBL 37 | 15 GB | 2 | EBI |
| PubChem (SMILES+InChI+Synonym+Mass) | 11 GB | 5 | NCBI FTP |
| PubChem BioAssay | 11 GB | 4 | NCBI FTP |
| GPS Platform v5+v6 (Gonzales tideGlass) | 1.5 GB | 8 | Zenodo 17653393+17956238 |
| BindingDB (All+Assays+rsid) | 583 MB | 3 | BindingDB |
| ZINC20 SMILES (drug-like) | 244 MB | 110 | ZINC20 |
| ChEBI (OBO + SDF) | 129 MB | 3 | EBI FTP |
| Every Cure MATRIX Knowledge Graph | 51 MB | 1 | GitHub |

### Cancer & Disease (24 GB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| TCGA Pan-Cancer (expression+mutation+methylation+protein+clinical) | 15 GB | 9 | Xena/GDC |
| COSMIC v104 (CGC+screens+resistance+breakpoints) | 5.2 GB | 7 | Sanger |
| GEO SOFT cancer expression (original+expanded) | 3.6 GB | 20 | NCBI GEO |
| Open Targets Platform v26.06 | 1.2 GB | 18 | EBI FTP |
| NF Data Portal (NF1 drugs + NF2 kinomics) | 666 MB | 658 | Synapse |
| TCGA Xena (supplementary) | 461 MB | 4 | UCSC Xena |

### Transcriptomics & Expression (2.5 GB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| GTEx V8 expression | 2.4 GB | 4 | GTEx Portal |
| Human Protein Atlas tissue data | 7.1 MB | 1 | HPA |

### Ontologies & Annotations (580 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| Reactome pathways + interactors | 295 MB | 4 | Reactome |
| SILVA 138.1 SSURef NR99 | 188 MB | 1 | arb-silva.de |
| Rfam RNA families (CMs + regions + clans) | 163 MB | 3 | EBI FTP |
| MONDO disease ontology | 103 MB | 1 | MONDO |
| HPO (OBO + annotations) | 45 MB | 2 | HPO |
| Gene Ontology (OBO + human GAF + GOA) | 52 MB | 3 | GO Consortium |
| ExPASy (ENZYME + PROSITE) | 33 MB | 2 | ExPASy |
| MGI mouse gene models | 17 MB | 2 | Jackson Lab |
| MSigDB gene sets (5 collections) | 15 MB | 5 | Broad |
| Uberon anatomy ontology | 13 MB | 1 | OBO Foundry |
| miRBase microRNA sequences | 13 MB | 2 | miRBase |
| OBO Ontologies (Sequence Ontology, ENVO) | 10 MB | 2 | OBO Foundry |
| Disease Ontology (DOID) | 6.8 MB | 1 | DO |
| KEGG (pathways+compounds+reactions+enzymes) | 4.4 MB | 5 | KEGG REST |
| Cell Ontology | 3.5 MB | 1 | OBO Foundry |

### Metabolism & Enzymes (2 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| BRENDA enzyme kinetics (Km/kcat/Ki) | 633 KB | 74 | BRENDA SOAP |
| Molecular Force Fields (CHARMM36) | 1.1 MB | 2 | MacKerell Lab |
| AME2020 nuclear masses | 641 KB | 2 | IAEA/NDS |

### Clinical & Pharmacogenomics (1.1 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| ClinGen gene-disease validity | 1.1 MB | 1 | ClinGen |

### Environment & Climate (5.6 GB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| NOAA GHCND | 3.5 GB | 3 | NOAA |
| PhysioNet PTB-XL | 1.8 GB | 1 | PhysioNet |
| USDA NASS Census 2017 | 132 MB | 1 | USDA |
| MassBank spectra | 115 MB | 1 | MassBank |
| PhysioNet MIT-BIH | 22 MB | 1 | PhysioNet |
| USGS earthquake catalog (2000-2026) | 10 MB | 29 | USGS |
| NASA GISS temperature anomalies | 23 KB | 2 | NASA GISS |
| NOAA GML CO2+CH4 | 87 KB | 3 | NOAA GML |

### Ecology & Evolution (261 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| Earth Microbiome Project 16S BIOM | 110 MB | 1 | Qiita FTP |
| PLUMED-NEST data repository | 142 MB | 1 | GitHub |
| LTEE REL606 genome | 5.8 MB | 1 | NCBI |
| Tara Oceans station data | 3.9 MB | 1 | Pangaea |

### Physics & Computation (330 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| Murillo Surrogate Learning (Zenodo) | 251 MB | 1 | Zenodo 10908462 |
| Murillo Dense Plasma DB | 77 MB | 1 | GitHub |
| HotQCD EOS Analysis | 2.5 MB | 2 | GitHub |

### Evolutionary & Computational Biology (173 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| PhyNetPy gene trees (NakhlehLab) | 81 MB | 1 | GitHub |
| breseq (Barrick Lab) | 47 MB | 1 | GitHub |
| SEPP/SATe phylogenetic alignments (Liu) | 27 MB | 1 | GitHub |
| Sarkas MD engine (Murillo Group) | 22 MB | 1 | GitHub |
| CQ.AAT1 chloroquine resistance (ABG) | 17 MB | 2 | GitHub |
| Multi-BGK kinetic solver (LANL) | 0.2 MB | 1 | GitHub |

### Environmental & Public Health (3 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| Jones PFAS MS Library | 0.2 MB | 3 | Zenodo 14341321 |
| KBS LTER main cropping yields | 0.1 MB | 1 | MSU LTER |

### Clinical Databases (11 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| MIMIC-III Clinical Demo | 10.8 MB | 1 | PhysioNet |

### Geospatial & Infrastructure (17 MB)

| Dataset | Size | Files | Source |
|---------|------|-------|--------|
| OSM Protected Areas (global) | 17 MB | 1 | Overpass API |
| USGS 3DEP elevation metadata | 0.04 MB | 1 | USGS |

---

| **Session 1-2 subtotal** | **~515 GB** | **~535 files** | **130 datasets** |
| **Current (Aug 4, 2026)** | **~3.65 TB** | **~1500+ files** | **154 datasets** |

---

## BLOCKED — Needs User Intervention

See `data_blockers.md` for full details. Key items:

1. **Copernicus ERA5**: Accept licence on website
2. **DepMap/CCLE**: Browser download (Cloudflare)
3. **HMDB**: Browser download (Cloudflare)
4. **DisGeNET**: Free registration
5. **EPA CompTox PFAS**: Browser session
6. **OMIM**: API key registration
7. **DrugBank**: Academic registration
8. **AmeriFlux**: Registration
9. **PharmGKB**: Terms acceptance

## REMAINING — Open Access (retry later)

| Dataset | Est. Size | Notes |
|---------|-----------|-------|
| GWAS Catalog associations | ~500 MB | EBI API outage — retry |
| COSMIC additional files | ~2 GB | Some API paths error |
| Open Targets (more entities) | ~5 GB | Got core 4 entities, can expand |
| GEO SOFT (more series) | ~50 GB | NCBI rate limiting |
| NCBI SRA (curated BioProjects) | ~2 TB | Large, batch over weeks |

## Batch 5 — Month-scale

| Dataset | Est. Size | Priority |
|---------|-----------|----------|
| AlphaFold DB v6 (full — 214M structures) | ~23 TB | P2 |
| HMP Phase II (gut microbiome) | ~500 GB | P2 |
| Cell x Gene (scRNA-seq) | ~500 GB | P3 |
| ERA5-Land (Copernicus) | ~3 TB | P3 |
| Earth Microbiome Project | ~200 GB | P2 |

---

## Running Total

| Milestone | Cumulative | % of ZFS |
|-----------|-----------|----------|
| Current (Aug 4, 2026) | **~3.65 TB** (154 datasets, ZFS 63.7 TB pool) | 5.7% |
| ~~AlphaFold 46/46~~ | 79 GB | **DONE** |
| ~~SRA FASTQ 5 BioProjects~~ | 267 GB | **DONE** |
| ~~AlphaFold full sync (v1-v6 + metadata)~~ | ~2.5 TB | **DONE** (trailer braiding at 43/s) |
| After user P1 registrations | +~5 GB | — |
| After GEO SOFT + TCGA full expansion | +~50 GB | — |
| After SRA curated BioProjects (2 TB) | ~6 TB | ~9.4% |
| After month-scale batch (AlphaFold full 214M) | ~26 TB | ~41% |

## Credential Vault

Encrypted API keys stored on golgiBody in `wateringHole/vault/`:
- NCBI, Synapse, Copernicus CDS, COSMIC, BRENDA
- AES-256 encrypted, ecosystem passphrase
