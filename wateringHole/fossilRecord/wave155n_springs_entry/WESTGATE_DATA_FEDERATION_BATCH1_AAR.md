# AAR: westGate Data Federation — Batch 1 Execution

**Date**: Aug 1, 2026 11:20 EDT
**Gate**: westGate
**Wave**: 155n post-threshold
**Author**: westGate overwatch (agent-assisted)
**biomeOS**: v4.56.0 (17h+ uptime, 13/13 active, 30 sockets)

---

## TL;DR

Executed the first batch of systematic data federation: 10 datasets across 6 ecosystem
domains, all with full CAS + Provenance Trio pipeline. 38.2 GB on ZFS, 4,752 CAS objects,
131 files with 100% provenance. PDB bulk rsync (220K+ structures) running in background.
Total session: ~20 minutes of actual download time on 1G fiber, zero saturation impact.
Every byte is latent value — zero egress at 10G LAN.

---

## Datasets Ingested — Batch 1

| # | Dataset | Size on ZFS | Files | Provenance | Spring/Garden | Domain |
|---|---------|-------------|-------|-----------|---------------|--------|
| 1 | PDB (506 structures) | 361 MB | 506 | 100% | hotSpring, neuralSpring | Structural biology |
| 2 | ChEMBL 37 | ~15 GB | 2 | 100% | healthSpring, tideGlass | Drug discovery |
| 3 | LINCS L1000 Level 5 + metadata | ~20 GB | 6 | 100% | wetSpring, tideGlass | Gene expression |
| 4 | UniProt Swiss-Prot (FASTA + DAT + variants) | 764 MB | 3 | 100% | wetSpring, hotSpring | Protein sequences |
| 5 | ZINC20 SMILES (110 tranches) | 160 MB | 110 | 100% | healthSpring, tideGlass | Compound screening |
| 6 | GTEx V8 (TPM + reads + annotations) | 2.4 GB | 4 | 100% | wetSpring, healthSpring | Tissue expression |
| 7 | SILVA 138.1 (16S ref) | 188 MB | 1 | 100% | wetSpring | Taxonomy |
| 8 | PhysioNet MIT-BIH | 22 MB | 1 | 100% | healthSpring | Biosignals |
| 9 | MassBank NIST (reference spectra) | 63 MB | 1 | 100% | wetSpring (PFAS) | Mass spec |
| 10 | NOAA GHCND (stations + inventory) | 11 MB | 2 | 100% | groundSpring, airSpring | Weather |
| 11 | LTEE REL606 genome | 5.8 MB | 1 | 100% | wetSpring (lithoSpore) | Microbial evolution |
| **Total** | | **~38.2 GB** | **4,752 CAS** | **100%** | | |

### Still Running

- **Full PDB bulk rsync**: 1.4 GB of ~60 GB downloaded. 220K+ mmCIF structures. ETA: overnight.

### Needs Manual Download (browser required)

- **BindingDB**: Their download JSP requires session cookies. ~2 GB.
- **EPA CompTox PFAS**: URL changed. Need current endpoint.

---

## Pipeline Performance

| Metric | Value |
|--------|-------|
| BLAKE3 throughput (20 GB LINCS) | **15.8 GB/s** |
| BLAKE3 throughput (1.5 GB GTEx) | **13.4 GB/s** |
| BLAKE3 throughput (667 MB UniProt) | **11.3 GB/s** |
| Provenance overhead per file | **<25ms** |
| ZINC 110 files (244 MB) | **3.8s total** |
| UniProt 3 files (765 MB) | **1.4s total** |
| GTEx 4 files (2.4 GB) | **0.4s total** |
| LINCS Level 5 (20 GB) | **1.4s total** |

The provenance pipeline is essentially free. BLAKE3 hashing at 10-16 GB/s dominates, and
the 4-step RPC chain (CAS → DAG → spine → sign → braid) adds negligible time.

---

## ZFS Pool State

```
NAME                    USED  AVAIL
nestgate               38.2G  50.7T    (0.075% utilized)
```

| Dataset | ZFS Size | Objects |
|---------|----------|---------|
| chembl37 | 15 GB | 2 |
| lincs_l1000 | 20 GB | 6 |
| gtex_v8 | 2.4 GB | 4 |
| uniprot | 764 MB | 3 |
| silva_138 | 188 MB | 1 |
| zinc20_smiles | 160 MB | 110 |
| massbank | 63 MB | 1 |
| physionet | 22 MB | 1 |
| noaa_ghcnd | 11 MB | 2 |
| ltee | 5.8 MB | 1 |

---

## Bandwidth Impact Assessment

Total downloaded this session: ~25 GB (new data beyond earlier PDB + ChEMBL)
Duration: ~20 minutes
Average throughput: ~21 MB/s (well under the 120 MB/s 1G fiber capacity)
Residential impact: **NONE** — concurrent browsing/streaming unaffected.

### Why No Saturation

1. Most datasets are small (<1 GB) — download in seconds
2. Large datasets (LINCS 20 GB, GTEx 2.4 GB) are single-stream, self-throttling
3. PDB rsync runs at RCSB's pace, not ours
4. ZFS lz4 compression reduces write amplification
5. No concurrent uploads — pull only

### Bandwidth Budget for Remaining Schedule

| Batch | Est. Size | Download Time | When |
|-------|-----------|---------------|------|
| Batch 1 (done) | ~38 GB | 20 min | Today |
| PDB bulk (running) | ~60 GB | Overnight | Today→tomorrow |
| Batch 2 (queued) | ~160 GB | ~25 min burst | This week |
| Batch 3 (queued) | ~75 GB | ~12 min burst | Next week |
| Batch 4 (large genomics) | ~1.5 TB | ~3h overnight | +2 weeks |
| Batch 5 (AlphaFold) | ~23 TB | ~3 days | Month-scale |

---

## tideGlass Unblock Status

| Module | Data Needed | Status |
|--------|------------|--------|
| M1: RGES correlation | ChEMBL + LINCS | **UNBLOCKED** |
| M2: RCL noise cleaning | LINCS VCaP_t1 | **UNBLOCKED** |
| M3: Expression prediction | GPS4Drug held-out | Depends on M2 |
| M4: Reversal screening | ZINC | **UNBLOCKED** (110 tranches on ZFS) |
| M5: MCTS optimization | MolSearch | Depends on M3 |
| M6: OCTAD parity | OCTAD HCC baseline | Needs download |
| M7: NF extension | NF disease signatures | Needs NF Data Portal (Synapse) |

**3 of 7 modules unblocked by data federation.** M3 and M5 are algorithm-dependent on M2.
M6 and M7 need specific portal access.

---

## Spring × Dataset Coverage

| Spring | Datasets on ZFS | Key Gaps |
|--------|----------------|----------|
| **wetSpring** | LINCS, UniProt, SILVA, MassBank, REL606, GTEx | SRA BioProjects, HMP, EMP |
| **healthSpring** | ChEMBL, LINCS, PhysioNet MIT-BIH, GTEx | BindingDB, DrugBank, TCGA |
| **hotSpring** | PDB (506), NOAA GHCND | Full PDB (running), PLUMED-NEST, BRENDA |
| **neuralSpring** | PDB (506) | Full PDB (running), UniRef90, PDB70, AlphaFold |
| **groundSpring** | NOAA GHCND | IRIS FDSN, KBS LTER |
| **airSpring** | NOAA GHCND | USDA NASS, AmeriFlux, ERA5-Land |
| **tideGlass** | ChEMBL, LINCS, ZINC, GTEx | NF Data Portal, OCTAD |

---

## Tools Shipped

1. **`bulk_ingest.py`**: Generalized ingestion tool for large datasets. Handles both large
   files (>100 MB → CAS hash reference) and small files (direct CAS storage). Full 5-step
   provenance chain on every file.

2. **`data_federation_schedule.md`**: Master download schedule with 5 batches, bandwidth
   estimates, and ZFS capacity projections.

---

## Observations

1. **The pipeline is proven at scale.** 4,752 CAS objects. 131 files across 10 datasets.
   Zero provenance failures. Zero NUCLEUS instability. 30 sockets stable through continuous
   ingestion. The provenance chain doesn't break under load because the overhead is negligible.

2. **Bandwidth management is trivial.** At 1G fiber, most science datasets download in
   seconds to minutes. The only multi-hour downloads are truly massive archives (full PDB,
   AlphaFold). Small datasets can be ingested opportunistically without any scheduling.

3. **Every byte is latent value.** 38 GB on ZFS today means 38 GB that never needs to be
   re-fetched. At 10G LAN, any gate in the mesh can access this data at wire speed. The
   egress cost of not having this data locally is real — cloud providers charge $0.05-0.09/GB
   for egress. 38 GB × 100 accesses = $190-342 saved. The economics compound with every
   dataset and every gate.

4. **The ZFS pool is barely touched.** 38.2 GB of 50.7 TB = 0.075%. Even the full schedule
   (including AlphaFold's 23 TB) only uses ~60% of capacity. This is a sovereign data lake
   that can grow for years.

5. **BindingDB and EPA need manual intervention.** Some data portals require browser sessions,
   captchas, or rotating URLs. This is expected — the pipeline handles the provenance, the
   human handles the access negotiation. Future evolution: NestGate providers with stored
   credentials for authenticated sources.

---

## Next Steps

- PDB bulk rsync completes overnight → ingest through provenance → persist to ZFS
- BindingDB manual download → ingest
- ZINC: download remaining tranches (currently have AA-AD, need AE-ZZ for full coverage)
- Start Batch 2: UniRef90 (100 GB), PDB70 (15 GB), NCBI BioProjects
- Queue Batch 3: TCGA expression, IRIS FDSN, BRENDA, EcoCyc
- Schedule AlphaFold DB v4 (23 TB) for a weekend download

---

*38.2 GB on ZFS. 4,752 CAS objects. 10 datasets at 100% provenance. 13/13 NUCLEUS stable.
PDB bulk rsync running. The sovereign data lake is accumulating. Every byte is one less
egress charge, one more dataset at 10G to the mesh.*
