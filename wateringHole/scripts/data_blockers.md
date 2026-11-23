# Data Federation — Blockers & Issues Log

**Gate**: westGate
**Started**: Aug 2, 2026
**Updated**: Aug 4, 2026

Track failures, user-intervention items, and issues to circle back to.

---

## NEEDS USER (registration, browser, licence acceptance)

| # | Dataset | Blocker | Action Required | Priority |
|---|---------|---------|----------------|----------|
| 1 | Copernicus ERA5 | Licence not accepted | Visit [ERA5 licence page](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download#manage-licences), click Accept | P2 |
| 2 | DepMap/CCLE | Cloudflare bot protection | Download via browser from [DepMap portal](https://depmap.org/portal/download/all/), grab CCLE_expression.csv + CRISPRGeneEffect.csv | P1 |
| 3 | HMDB metabolites | Cloudflare bot protection | Download via browser from [HMDB downloads](https://hmdb.ca/downloads), grab hmdb_metabolites.zip (~3 GB) | P2 |
| 4 | DisGeNET | API key obtained but REST API serves React SPA | API key: `6763ddf4...fc37d`. All download endpoints return HTML. **Need browser download** of SQLite DB from [DisGeNET downloads](https://www.disgenet.org/downloads) | P2 |
| 5 | EPA CompTox PFAS | Browser-only download | Download PFAS compound list from [CompTox Dashboard](https://comptox.epa.gov/dashboard/) | P1 |
| 6 | EcoCyc E. coli | Registered (mokkevin@msu.edu, expires 2027-08-02) | Flat file download needs browser auth at [BioCyc downloads](https://biocyc.org/download-flatfiles.shtml). **Need browser download**. | P3 |
| 7 | OMIM genemap2 | API request submitted (mokkevin@msu.edu) | Awaiting approval — JHU responds within 2 business days. Once key arrives, download via REST API. | P2 |
| 8 | MSigDB full JSON | Registered (mokkevin@msu.edu) | **RESOLVED** — Downloaded all 35 GMT + JSON collections for v2026.1.Hs (70+ files, 44+ MB). Full XML still needs login. | **DONE** |
| 9 | DrugBank | Requires academic registration | Register at [DrugBank](https://go.drugbank.com/releases/latest) for download access | P2 |
| 10 | Bgee expression | Cloudflare bot protection | Download via browser from [Bgee](https://bgee.org/?page=download) | P3 |
| 11 | AmeriFlux BASE | Requires registration | Register at [AmeriFlux](https://ameriflux.lbl.gov/) for BASE data access | P2 |
| 12 | PharmGKB downloads | Requires terms acceptance | Agree to terms at [PharmGKB](https://www.pharmgkb.org/downloads) | P2 |

## DOWNLOAD FAILURES (scripted retry possible)

| # | Dataset | Issue | Error | Retry Strategy | Status |
|---|---------|-------|-------|---------------|--------|
| 1 | GWAS Catalog associations | EBI API returns Tomcat 500 | 992 bytes HTML error | Used FTP rsync — 700 MB full release | **RESOLVED** |
| 2 | GEO GSE62944 (TCGA recount) | NCBI FTP returns tiny stub | 200 OK, 2.5 KB | GEO supplementary files available separately | WONTFIX |
| 3 | NIST PFAS SRD | API endpoint wrong/moved | 154 bytes | Found via data.nist.gov JSON API — 1.1 MB XLSX | **RESOLVED** |
| 4 | Open Targets | FTP path structure changed | 404 on json/ directory | Find current release parquet/json paths | RESOLVED |
| 5 | Dryad LTEE fitness (Wiser 2013) | API returns 401/403 | Auth/redirect broken | Dryad API v2 finds files but download endpoint returns 401 | OPEN |
| 6 | HomoloGene | NCBI FTP 404 | Possibly discontinued | Replaced with OrthoDB v11 | RESOLVED |
| 7 | Ensembl regulatory build | Specific file path 404 | 196 bytes | Find current release filename | RESOLVED |
| 8 | PDB validation summary | RCSB URL changed | 323 bytes redirect | Find new reports URL | LOW |
| 9 | SIGNOR signaling | Download requires POST/JS | Returns HTML page | Found REST API (getData.php) — 21 MB TSV | **RESOLVED** |
| 10 | CORUM complexes | Download page changed | 0 bytes | Site returns 0 bytes for all download URLs | OPEN |
| 11 | Pathway Commons | URL structure changed (v12/v13 both 404) | 693 bytes | Moved to download.baderlab.org — v14 downloaded (10 MB) | **RESOLVED** |
| 12 | dbNSFP | S3 bucket "dbnsfp" no longer exists | NoSuchBucket error | Google Sites page returns JS blob, no direct link found | OPEN |
| 13 | BOLD Systems API | API returns partial HTML | 10 KB mixed HTML/TSV | May need smaller taxonomic queries | LOW |
| 14 | BioModels SBML | Download endpoint changed | 0 bytes | Research current EBI BioModels API | LOW |
| 15 | TAIR GO annotations | Requires authentication | 118 byte redirect | Register at arabidopsis.org | LOW |
| 16 | MalariaGEN Pf6 metadata | Site redesigned, all URLs return HTML | 42 KB HTML | GCS bucket also gone (NoSuchBucket) | OPEN |
| 17 | Michigan EGLE PFAS GIS | ArcGIS API returns empty/error | 11-72 bytes | Need correct FeatureServer URL | OPEN |
| 18 | EPA UCMR5 PFAS | URL rotates with each data release | 6.5 KB HTML | Found 2023-08 URLs on EPA site — 26 MB downloaded | **RESOLVED** |
| 19 | CAZy/dbCAN HMMs | URL structure changed | 18 KB HTML | Downloaded run_dbcan v4.1.4 (718 KB) from GitHub releases | **RESOLVED** |
| 20 | HMP gene catalog | NCBI HMPDACC FTP returns XML | 990 bytes | HMP portal API also non-functional | OPEN |
| 21 | BioGRID chemicals | Download URL returns HTML | 7 KB | Release archive page returns empty listings | LOW |
| 22 | USDA PLANTS | CSV URL changed/requires AJAX | 710 bytes HTML | Use alternative botanical data source | LOW |
| 23 | FEMA NFHL | REST endpoint returns HTML | 1.5 KB | Need current ArcGIS service URL | LOW |
| 24 | Human Cell Atlas | API endpoint changed | 130 bytes | Found correct API (dcp60 catalog) — 532 projects, 25 saved | **RESOLVED** |

## TECHNICAL ISSUES

| Issue | Detail | Impact | Resolution |
|-------|--------|--------|------------|
| NCBI FTP rate limiting | Aggressive 403 on parallel requests (>2) | Slows GEO/NCBI bulk downloads | Sequential with 10s delays; NCBI API key helps for Entrez but not FTP |
| Xena Hub S3 bucket access | pancanatlas S3 returns AccessDenied | Some TCGA supplementary files | Used toil-xena-hub S3 as fallback (got expression + mutations) |
| EBI FTP file paths change | Filenames include version numbers that rotate | 404 on specific files | List directory first to find current filenames |
| GEO SOFT vs supplementary | Large GEO series (LINCS) return metadata stubs in SOFT format | Missing embedded data | Use GEO supplementary files or direct data downloads instead |

## SUCCESSFULLY RESOLVED THIS SESSION

| Issue | Resolution |
|-------|------------|
| AlphaFold version mismatch | URLs were v4, current is v6 — all 46 proteomes downloaded |
| ChEBI SDF filename | Was `ChEBI_complete_3star.sdf.gz`, actual is `chebi_3_stars.sdf.gz` |
| COSMIC cell lines API | API path returns ServerError for cell lines product |
| USGS query limit | 20K event limit — split into yearly queries (27 files) |
| Pfam/InterPro downloads | Needed longer timeouts (InterPro = 12 GB) |
| Open Targets path | FTP restructured — data is under `output/` not `output/etl/json/` |
| Ensembl regulatory build | Filename had wrong date — found correct via directory listing |
| Uberon/CL ontology | raw.githubusercontent.com 404 — used purl.obolibrary.org instead |
| MSigDB | Full JSON needs login — individual GMT collections downloadable without auth |
| HomoloGene | Discontinued by NCBI — replaced with OrthoDB v11 |
| Sarkas ZIP 14 bytes | GitHub `main` branch → `master` branch fixed download |
| SRA RunInfo API | Old Trace API returns HTML — switched to Entrez esearch+efetch |
| NCBI gene expansions | Added gene2go (1.3 GB) + gene2pubmed (268 MB) via FTP |
| Tabula Muris data | Found 290 MB FACS + 4 MB annotations on Figshare via API |
| SILVA NR99 expansion | Added 197 MB NR99 SSURef to existing SILVA 138.1 |

---

## SESSION STATS

### Session 2 (Aug 2, 2026 evening — contacts + baseCamp sweep)

- **Source**: Deep scan of `attsi/non-anon/contact/`, baseCamp papers, garden scopes
- **New datasets acquired**: 30+ (GPS Platform, Murillo Plasma+Surrogate, Jones PFAS, Tabula Muris, EMP, PLUMED-NEST, breseq, CQ.AAT1, SEPP/SATe, HotQCD, PhyNetPy, NCBI Assembly, Ensembl Compara, OSM, MIMIC demo, plus expansions to gene_info/gene2go/gene2pubmed, GOA, SILVA NR99, Reactome interactors, Rfam clans, OBO ontologies, and SRA metadata for 12 BioProjects)
- **Data volume added**: ~8 GB new + expansions
- **Provenance**: 100% — all 30+ datasets through full 5-step chain
- **Grand total**: 515 GB, 130 datasets, 535 files

### Session 1 (Aug 2, 2026 — initial sweep)

- **Datasets attempted**: ~50
- **Datasets acquired**: 30+ new
- **Success rate**: ~60% (rest blocked by auth, Cloudflare, URL changes, rate limits)
- **Data volume this session**: ~67 GB new data

### Session 3 (Aug 3, 2026 morning — blocker resolution + AlphaFold full sync)

- **Blockers resolved**: 7 (GWAS Catalog, NIST PFAS, SIGNOR, Pathway Commons, EPA UCMR5, dbCAN, HCA)
- **New datasets**: 6 provenance-tracked
- **AlphaFold full sync**: Started via rsync with systemd timer (restart-safe). Swiss-Prot CIF (37 GB) + PDB (27 GB) + sequences.fasta (118 GB) + metadata downloading.
- **GWAS Catalog**: Full FTP release (700 MB) via rsync — bypassed broken API

### Running Total (Aug 5, 2026 AM)

- **Grand total**: ~3.21 TB used, 153 datasets on ZFS (50.7 TB pool, 6.3% used)
- **CAS pool**: ~452 GB (grown from 135 GB via provenance trailer)
- **AlphaFold full sync**: COMPLETE (v1-v6 + metadata). Provenance convoy braiding at **145/s** (4-worker native socket).
- **Provenance**: 460x total throughput improvement (0.3/s → 38/s spine alignment → 145/s native socket convoy)
- **Convoy AAR**: Primals never the bottleneck. nestGate 16K RPCs/s, rhizoCrypt <1ms batch. Socat subprocess spawning was the glue bottleneck.
- **Convergence sweep**: 0 CONVERGED, 5 CAS-ONLY, 89 PARTIAL, 32 PRIMORDIAL, 21 EMPTY
- **GPS data**: CONVERTED (11 JSON, 103 MB CAS-ingested with BLAKE3)
- **biomeOS**: v4.57 deployed (source-built), 14/14 HEALTHY, `nucleus attach` available
- **Blockers remaining**: 5 OPEN download failures, 12 need-user items
- **Blockers resolved (Sessions 1-3)**: 7 of 24

*Circle back to NEEDS USER items when user has time for registrations.*
*Remaining OPEN items: Dryad LTEE, CORUM, dbNSFP, MalariaGEN, EGLE PFAS, HMP — all require deeper API research or have moved.*
*AlphaFold full sync runs daily at 3 AM via systemd timer — fully restart-safe.*
