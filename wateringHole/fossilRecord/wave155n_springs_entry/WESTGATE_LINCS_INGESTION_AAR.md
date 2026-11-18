# AAR: LINCS L1000 Level 5 Ingestion — tideGlass Data Unblocked

**Date**: Aug 1, 2026 11:00 EDT
**Gate**: westGate
**Wave**: 155n post-threshold
**Author**: westGate overwatch (agent-assisted)
**biomeOS**: v4.56.0 (17h 30m uptime)

---

## TL;DR

LINCS L1000 Level 5 (GSE92742) — the foundational drug-repurposing dataset — downloaded
from NCBI GEO and ingested through the full CAS + Provenance Trio pipeline.
473,647 gene expression signatures × 12,328 genes, 19.86 GB compressed, FULL PROVENANCE.
Combined with the earlier PDB + ChEMBL ingestion, westGate now holds 53+ GB of real science
data on ZFS with 100% provenance. tideGlass modules 1 and 2 are UNBLOCKED.

---

## What Was Ingested

### LINCS L1000 Level 5 (GSE92742)

| File | Size | BLAKE3 | Provenance |
|------|------|--------|-----------|
| Level5_COMPZ.MODZ_n473647x12328.gctx.gz | 19.86 GB | `50fd953c09df9fdd...` | FULL (5/5) |
| pert_info.txt.gz | 1.1 MB | `11cff4921a9d871a...` | FULL (5/5) |
| sig_info.txt.gz | 10.6 MB | `2d50d4a8e86fd5e6...` | FULL (5/5) |
| sig_metrics.txt.gz | 11.9 MB | `5359b5cf1f5ad7bb...` | FULL (5/5) |
| cell_info.txt.gz | 2.5 KB | `9a4a1912bc9e5a7d...` | FULL (5/5) |
| gene_info.txt.gz | 212 KB | `978f325274ae11b4...` | FULL (5/5) |

**6/6 files, FULL PROVENANCE, zero failures.**

### What LINCS L1000 Contains

The Library of Integrated Network-Based Cellular Signatures (LINCS) L1000 assay measures
gene expression responses to chemical and genetic perturbations across human cell lines.

- **473,647 signatures**: Individual gene expression profiles
- **12,328 genes**: Including 978 landmark genes + inferred
- **~20,000 compounds**: Drug and drug-like molecules
- **~100 cell lines**: Including cancer lines (MCF7, PC3, VCAP, A549, A375, HA1E, HCC515)
- **Source**: Broad Institute (Subramanian et al., Cell 2017)
- **License**: CC0-1.0 (public domain via GEO)
- **GEO accession**: GSE92742

### Why This Matters for tideGlass

tideGlass (GPS drug-repurposing platform) requires LINCS L1000 as its foundational dataset:

| tideGlass Module | LINCS Dependency | Status |
|-----------------|-----------------|--------|
| Module 1: RGES correlation | LINCS + ChEMBL → RGES scoring | **UNBLOCKED** |
| Module 2: RCL noise cleaning | LINCS VCaP_t1 profiles | **UNBLOCKED** |
| Module 3: Expression prediction | GPS4Drug trains on cleaned LINCS | Unblocked (depends on M2) |
| Module 4: Reversal screening | ZINC screening library | **BLOCKED on ZINC** |

---

## Pipeline Performance

| Metric | Value |
|--------|-------|
| Download time (20 GB) | ~5 min at 1G fiber |
| BLAKE3 hash (20 GB) | **1,352ms** → **15.8 GB/s** |
| Full provenance (Level 5) | **1,377ms** total |
| Metadata ingestion (5 files) | **400ms** total |
| CAS mode | Large file reference (>100 MB → stores hash reference) |

BLAKE3 throughput at 15.8 GB/s on a 20 GB file confirms westGate's data processing
capability. The provenance pipeline adds negligible overhead beyond hashing.

---

## Infrastructure

### Data on ZFS

| Dataset | Size | Objects | Provenance |
|---------|------|---------|-----------|
| PDB structures | 361 MB | 506 | 100% |
| ChEMBL 37 | ~15 GB (compressed) | 6 | 100% |
| LINCS L1000 | ~18 GB (compressed) | 6 | 100% |
| **Total** | **~35 GB on disk** | **4,506 CAS** | **100%** |

ZFS available: **50.7 TB** (0.07% utilized — room for AlphaFold's 23 TB and beyond).

### NUCLEUS State

- biomeOS v4.56.0, 17h 30m uptime, Coordinated mode, 672 capabilities
- 13/13 services active, 30 sockets, zero respawns
- Machine uptime: 3 days 2h 36m

---

## New Tool: bulk_ingest.py

Shipped `scripts/bulk_ingest.py` — generalized ingestion pipeline for large datasets:

```
python3 bulk_ingest.py --files /path/to/data.gz --dataset "Dataset Name"
python3 bulk_ingest.py --dir /path/to/files/ --dataset "Dataset Name" --glob "*.gz"
```

Handles both large files (>100 MB → CAS hash reference) and small files (direct CAS storage).
Full 5-step provenance chain on every file.

---

## What Worked

1. **1G fiber → ZFS pipeline is smooth.** Download at wire speed, BLAKE3 at 15.8 GB/s,
   ZFS with lz4 compression absorbs everything. The "grab once at 1G, serve forever at 10G"
   thesis continues to hold.

2. **Provenance is essentially free.** Full 5-step chain (CAS → DAG → spine → sign → braid)
   adds <25ms per file beyond BLAKE3 hashing. At 15.8 GB/s BLAKE3, the hash itself dominates.

3. **bulk_ingest.py generalizes the pattern.** PDB used a custom script because of RCSB API
   specifics. For file-based datasets (LINCS, ZINC, AlphaFold), the generic tool works.

## What Needs Evolution

1. **ZINC data next.** tideGlass Module 4 (reversal screening) is blocked on ZINC screening
   library. ZINC20 is tranche-based — will need the bulk_ingest.py `--dir` mode.

2. **GCTx parsing.** The raw compressed GCTx is now on ZFS with provenance, but tideGlass
   needs to decompress and parse it (HDF5 format). This is a tideGlass-internal task, not
   a data federation task.

3. **Cross-gate data serving.** LINCS on westGate (ZFS raidz1) should be servable to
   strandGate (RTX 3090 for RCL training) at 10G. The CAS hash is the address. The mesh
   federation (G30) enables this but hasn't been exercised cross-gate yet.

---

## Sovereign Data Cloud Running Total

| Source | Data | Size | At 1G | Status |
|--------|------|------|-------|--------|
| RCSB PDB | 506 structures | 361 MB | <1s | **DONE** |
| EBI ChEMBL | ChEMBL 37 (2.9M compounds) | 33.79 GB | ~5 min | **DONE** |
| NCBI GEO | LINCS L1000 Level 5 | 19.86 GB | ~3 min | **DONE** |
| ZINC20 | Screening library | ~10 GB | ~2 min | NEXT |
| Full PDB | 220K structures | ~200 GB | ~30 min | QUEUED |
| AlphaFold DB v4 | ~214M structures | ~23 TB | ~2.7 days | LATER |

**53.6 GB of real science data at 100% provenance on sovereign ZFS.**
Grab once at 1G, serve forever at 10G, zero egress cost.

---

*LINCS L1000 Level 5 ingested. tideGlass modules 1+2 UNBLOCKED. 53+ GB on ZFS at 100%
provenance. 4,506 CAS objects. 30 sockets stable. 17h 30m NUCLEUS uptime. The substrate
is accumulating real science data.*
