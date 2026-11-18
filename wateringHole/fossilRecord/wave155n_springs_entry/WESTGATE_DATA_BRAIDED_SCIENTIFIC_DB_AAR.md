# AAR: westGate as Data-Braided Scientific Database — Full Survey

**Date**: Aug 2, 2026 09:35 EDT
**Gate**: westGate
**Wave**: 155n
**Author**: westGate overwatch (agent-assisted)
**ZFS**: 347 GB used / 50.4 TB available (0.69%)

---

## TL;DR

Full survey of westGate's data federation status, remaining datasets across the entire
ecosystem, registration/API key requirements for the user, and AlphaFold slow-download
strategy. **tideGlass base data is first priority** — we have 5/7 critical datasets,
need 2 more (NF Data Portal via Synapse, OCTAD reference). After tideGlass, the survey
identifies ~80 additional datasets across genomics, molecular dynamics, environmental,
and clinical domains that would make westGate a fully data-braided scientific database.

---

## CURRENT STATE: 347 GB, 25 Datasets, Full Provenance

| Category | Datasets | Size |
|----------|----------|------|
| Protein/Structure | PDB mmCIF (257K), UniProt, UniRef90, TrEMBL, PDB70 | 293 GB |
| Drug Discovery | ChEMBL, PubChem, ZINC20, LINCS L1000 | 46 GB |
| Cancer Genomics | TCGA Xena, GEO SOFT (11 series incl CCLE, GDSC) | 3.4 GB |
| Environmental | NOAA GHCND, USGS earthquake, USDA NASS | 3.6 GB |
| Expression | GTEx V8 | 2.4 GB |
| Reference | SILVA, AME2020, MassBank, PhysioNet, LTEE | 280 MB |
| **Total** | **25 datasets** | **347 GB** |

---

## PRIORITY 1: tideGlass Base Data

tideGlass (GPS drug repurposing platform) needs 7 specific data types across its 7 modules.
Status of each:

| Module | Data Need | Dataset | Status | Action |
|--------|-----------|---------|--------|--------|
| 1. RGES correlation | L1000 expression profiles | LINCS L1000 Level 5 | **ON ZFS** (20 GB) | Ready |
| 2. RCL noise cleaning | LINCS VCaP profiles | LINCS L1000 Level 5 | **ON ZFS** | Ready |
| 3. Expression prediction | GPS4Drug training data | ChEMBL + PubChem | **ON ZFS** (26 GB) | Ready |
| 4. Reversal screening | ZINC screened subset | ZINC20 SMILES | **ON ZFS** (160 MB) | Ready |
| 5. MCTS optimization | Molecular search space | ZINC20 + ChEMBL | **ON ZFS** | Ready |
| 6. OCTAD parity | OCTAD HCC baseline | **OCTAD reference** | **MISSING** | Need download |
| 7. NF extension | NF disease signatures | **NF Data Portal (Synapse)** | **MISSING** | Need Synapse account |

**Additional tideGlass data (would enhance but not block)**:

| Dataset | Why | Size | Source | Status |
|---------|-----|------|--------|--------|
| CCLE expression | Cell line drug response (GDSC parity) | **ON ZFS** (GEO GSE36139) | GEO | Ready |
| GDSC drug sensitivity | Genomics of Drug Sensitivity in Cancer | **ON ZFS** (GEO GSE68379) | GEO | Ready |
| BindingDB | Binding affinity for compound ranking | ~1 GB | bindingdb.org | Needs browser |
| DrugBank | Drug targets, ADMET, PK | ~500 MB | drugbank.com | Needs academic license |
| Connectivity Map | Drug perturbation ↔ disease | Overlaps LINCS | clue.io | Needs registration |

### tideGlass Action Items

1. **OCTAD reference data** — downloadable from octad.org or R package. Agent can grab this.
2. **NF Data Portal** — requires Synapse account (see registration section below).
3. **BindingDB** — browser download needed (JSP session cookies).

---

## PRIORITY 2: NCBI & Genomic Data

### What We Can Grab Now (no registration needed)

| Dataset | Size | Source | Spring/Garden | FTP/API |
|---------|------|--------|---------------|---------|
| NCBI RefSeq reference genomes | ~50 GB | ftp.ncbi.nlm.nih.gov | wetSpring | FTP |
| NCBI taxonomy dump | ~500 MB | ftp.ncbi.nlm.nih.gov | wetSpring | FTP |
| NCBI Gene2GO | ~200 MB | ftp.ncbi.nlm.nih.gov | wetSpring | FTP |
| NCBI Gene Info (Homo sapiens) | ~50 MB | ftp.ncbi.nlm.nih.gov | wetSpring | FTP |
| GTDB r220 (genome taxonomy) | ~80 GB | data.gtdb.ecogenomic.org | wetSpring | FTP |
| GEO supplementary files (cancer) | ~20 GB | ftp.ncbi.nlm.nih.gov | wetSpring | FTP |
| PlasmoDB (Plasmodium genomes) | ~2 GB | plasmodb.org | wetSpring (ABG) | FTP |
| SalmoBase (salmon genomes) | ~20 GB | salmobase.org | wetSpring (ABG) | FTP |
| Reactome pathways | ~500 MB | reactome.org | healthSpring | API |
| MONDO disease ontology | ~100 MB | monarchinitiative.org | healthSpring | API |
| Dryad SATe-II alignments | ~500 MB | datadryad.org | wetSpring | API |
| Human Protein Atlas | ~5 GB | proteinatlas.org | wetSpring | FTP |
| **Subtotal** | **~180 GB** | | | |

### NCBI SRA (Curated BioProjects) — Targeted, Not Bulk

Instead of downloading all of SRA (~50 PB), we grab specific BioProjects:

| BioProject | Description | Size | Spring |
|------------|-------------|------|--------|
| PRJNA294072 | LTEE genomes (Tenaillon 2016) | ~50 GB | wetSpring |
| PRJNA380528 | LTEE allele frequencies (Good 2017) | ~20 GB | wetSpring |
| GSE166686 | Salmon RNA-seq | ~10 GB | wetSpring (ABG) |
| GSE269132 | Salmon expression | ~10 GB | wetSpring (ABG) |

---

## PRIORITY 3: ABG Group Molecular Dynamics Data

The ABG group (Alistaire, hotSpring) uses GROMACS for molecular dynamics. Key data:

| Dataset | Description | Size | Source | Status |
|---------|-------------|------|--------|--------|
| CHARMM36 force field | Standard protein FF params | ~50 MB | mackerell.umaryland.edu | Can grab |
| CHARMM22* force field | Modified backbone params | ~50 MB | mackerell.umaryland.edu | Can grab |
| AMBER99SB-ILDN force field | Alternative protein FF | ~30 MB | ambermd.org | Can grab |
| GLYCAM force field | Carbohydrate parameters | ~20 MB | glycam.org | Can grab |
| PLUMED-NEST inputs (8 plumIDs) | Enhanced sampling protocols | ~500 MB | plumed-nest.org | Can grab |
| CAZy/ez-CAZy GH data | Glycoside hydrolase classification | ~200 MB | cazy.org | Can grab |
| ILDG gauge configurations | Lattice QCD configs (Bazavov) | ~100 GB+ | ildg.net | Needs registration |
| FPEOS tables (Militzer) | Dense matter EOS | ~1 GB | Berkeley | Academic contact |

### Force Field Downloads (no registration)

These are small but scientifically critical — hotSpring validates barraCuda (GPU MD)
against GROMACS with these exact parameter sets:

```
CHARMM36:   mackerell.umaryland.edu/charmm_ff.shtml
AMBER:      ambermd.org/AmberTools.php
OPLS-AA:    Bundled with GROMACS
GLYCAM:     glycam.org/docs/forcefield/parameters
```

---

## PRIORITY 4: Large-Scale Datasets (Month-Scope)

| Dataset | Size | Source | Strategy |
|---------|------|--------|----------|
| **AlphaFold DB v4** | ~23 TB | alphafold.ebi.ac.uk | See below |
| HMP Phase II | ~500 GB | hmpdacc.org | FTP, overnight |
| Cell x Gene | ~500 GB | cellxgene.cziscience.com | API |
| Earth Microbiome Project | ~200 GB | earthmicrobiome.org | FTP |
| ERA5-Land (Copernicus) | ~3 TB | cds.climate.copernicus.eu | Needs CDS API key |
| MalariaGEN Pf6 | ~50 GB | malariagen.net | FTP |
| NCBI SRA (curated) | ~2 TB | ncbi.nlm.nih.gov | sra-toolkit |

---

## AlphaFold DB: Slow Download Strategy

AlphaFold DB v4 is ~23 TB (200M+ predicted structures). At 1 Gbps:

| Metric | Value |
|--------|-------|
| Raw download time | ~2.7 days at 100% utilization |
| Realistic (50% off-peak) | ~5-6 days |
| ZFS space after | ~23 TB / 50.4 TB (46%) |

### Strategy: Incremental + Resumable

1. **rsync from EBI** — AlphaFold provides rsync access (like PDB). Idempotent, resumable.
2. **Organism-first**: Download by proteome priority:
   - Human (UP000005640) — ~800 GB — first
   - Model organisms (mouse, E. coli, yeast, zebrafish) — ~2 TB
   - Remaining proteomes — ~20 TB
3. **Bandwidth scheduling**: Run overnight/weekends only, `--bwlimit=50000` (50 MB/s)
4. **Manifest-based provenance**: Same pattern as PDB — hash all files, build manifest,
   single provenance chain per proteome batch

### Data Movement Considerations

When AlphaFold (or any large dataset) moves or updates:

- **rsync handles this**: `--delete` flag mirrors the source. Updated files get re-synced.
- **Provenance tracks versions**: Each rsync run produces a new manifest with new BLAKE3
  hashes. Old manifests are retained — you can diff them to see what changed.
- **ZFS snapshots protect**: Daily snapshots (14-day retention) mean we can roll back if
  a source pushes bad data.
- **Content-addressing is self-healing**: If a file's hash changes, nestGate CAS stores
  both versions. The old CAS object remains valid.
- **Mirror vs. transform**: We mirror the raw data (Tier 1). If AlphaFold retracts or
  updates a prediction, the next rsync picks it up. Our CAS retains the old version
  for provenance.

---

## REGISTRATIONS & API KEYS NEEDED (User Action)

These are accounts/keys the user needs to create. The agent cannot do this — they require
human identity verification, ToS acceptance, or institutional affiliation.

### HIGH PRIORITY (tideGlass + immediate science)

| Service | URL | Why | What You Get | Time |
|---------|-----|-----|-------------|------|
| **Synapse** (Sage Bionetworks) | synapse.org/register | NF Data Portal, DREAM Challenges, CTF datasets | API key for `synapseclient` Python package | 5 min (email verify) |
| **NCBI API key** | ncbi.nlm.nih.gov/account/settings | Higher rate limits for Entrez/SRA downloads (10 req/s vs 3) | API key for all NCBI services | 5 min |
| **Clue.io** (Broad Institute) | clue.io/register | Connectivity Map, LINCS API access, L1000 metadata | API key for CMap queries | 5 min |

### MEDIUM PRIORITY (next wave of data)

| Service | URL | Why | What You Get | Time |
|---------|-----|-----|-------------|------|
| **DrugBank** | drugbank.com/academic | Drug-target-ADMET data (academic license) | XML download access | Academic email required, ~1 day approval |
| **COSMIC** | cancer.sanger.ac.uk/cosmic/register | Somatic mutations in cancer | TSV downloads | Academic registration, ~1 day |
| **Copernicus CDS** | cds.climate.copernicus.eu/user/register | ERA5-Land weather reanalysis (3 TB) | CDS API key for `cdsapi` Python package | 10 min (ECMWF account) |
| **BRENDA** | brenda-enzymes.org/register.php | Enzyme kinetics database | Download access | Academic email |
| **EcoCyc** | ecocyc.org/subscribe.shtml | E. coli metabolic model | Full download access | Academic license request |
| **AmeriFlux** | ameriflux.lbl.gov/data/download-data/ | Eddy covariance flux data | Data access with attribution | Registration, free |
| **PhysioNet** (credentialed) | physionet.org/settings/credentialing | MIMIC-III ICU data (requires CITI training) | Full clinical dataset access | ~2 hours (CITI training + approval) |

### LOW PRIORITY (month-scale / specialized)

| Service | URL | Why | What You Get | Time |
|---------|-----|-----|-------------|------|
| **ILDG** | ildg.net | International Lattice Data Grid configs | Grid certificate access | Institutional affiliation |
| **dbGaP** | dbgap.ncbi.nlm.nih.gov | Controlled-access TCGA/GTEx individual-level | Controlled data access | IRB + DAR (weeks-months) |
| **Aqua-FAANG** | aqua-faang.eu | Aquaculture functional annotation | Data portal access | Registration |
| **USDA NASS API key** | quickstats.nass.usda.gov/api | Higher rate limits for crop data | API key | 5 min |

### ALREADY HAVE (no action needed)

| Service | Status |
|---------|--------|
| NCBI FTP (anonymous) | Open access — used for PDB, PubChem, GEO |
| UniProt FTP | Open access — used for Swiss-Prot, TrEMBL, UniRef90 |
| RCSB PDB rsync | Open access — used for full mmCIF mirror |
| GDC (TCGA open-access) | Open access — used for Xena matrices |
| NOAA/USGS/EPA | US Government — open access |

---

## WHAT THE AGENT CAN GRAB RIGHT NOW (no registration)

With the current session, I can immediately download:

### tideGlass Priority

| Dataset | Size | Source | Time |
|---------|------|--------|------|
| OCTAD reference tables | ~500 MB | GitHub/R package | ~1 min |

### NCBI Genomic

| Dataset | Size | Source | Time |
|---------|------|--------|------|
| NCBI taxonomy dump | ~500 MB | FTP | <1 min |
| NCBI Gene2GO | ~200 MB | FTP | <1 min |
| NCBI gene_info (human) | ~50 MB | FTP | <1 min |
| RefSeq human genome GRCh38 | ~3 GB | FTP | ~30s |

### Force Fields (ABG/GROMACS)

| Dataset | Size | Source | Time |
|---------|------|--------|------|
| CHARMM36 all-atom | ~50 MB | mackerell.umaryland.edu | <1 min |
| PLUMED-NEST inputs (8 plumIDs) | ~200 MB | plumed-nest.org | ~1 min |

### Additional Science

| Dataset | Size | Source | Time |
|---------|------|--------|------|
| Reactome pathways | ~500 MB | reactome.org | ~1 min |
| MONDO disease ontology | ~100 MB | monarchinitiative.org | <1 min |
| Human Protein Atlas | ~5 GB | proteinatlas.org | ~1 min |
| PlasmoDB P. falciparum | ~2 GB | plasmodb.org | ~30s |
| PhysioNet PTB-XL ECG | ~5 GB | physionet.org | ~1 min |

---

## PROJECTED ZFS USAGE

| Phase | Cumulative | % of 50.4 TB |
|-------|-----------|-------------|
| Current | 347 GB | 0.69% |
| After tideGlass + NCBI + FF | ~365 GB | 0.72% |
| After Batch 3 complete | ~420 GB | 0.83% |
| After NCBI SRA (curated BioProjects) | ~520 GB | 1.03% |
| After HMP + EMP + CxG | ~1.7 TB | 3.4% |
| After AlphaFold DB v4 | ~24.7 TB | 49% |
| After ERA5-Land | ~27.7 TB | 55% |

**At full saturation we use ~55% of ZFS.** The pool has room to grow with additional HDDs.

---

## VISION: westGate as Sovereign Scientific Data Cloud

The end state: westGate holds a provenance-braided mirror of every public dataset the
ecosystem touches. Every byte:

1. **BLAKE3 hashed** at ingest
2. **CAS stored** in nestGate (content-addressed, deduplicating)
3. **DAG tracked** in rhizoCrypt (causal graph of what came from where)
4. **Merkle certified** in loamSpine (tamper-evident chain)
5. **Ed25519 signed** by bearDog (gate identity)
6. **Attribution braided** in sweetGrass (license + author + source)

Grab once at 1 Gbps ingress. Serve forever at 10 Gbps LAN. Zero egress cost.
Every spring and garden on the mesh can pull any dataset at wire speed from westGate
instead of re-downloading from the internet. The provenance chain means they can
trust the data without re-fetching — the hash proves integrity, the signature proves
the gate that fetched it, the braid proves the license.

---

*Next steps: User registers for Synapse (tideGlass NF data), NCBI API key, Clue.io.
Agent grabs OCTAD, NCBI taxonomy, force fields, and continues Batch 3/4 downloads.
AlphaFold starts as organism-priority rsync with bandwidth limits.*
