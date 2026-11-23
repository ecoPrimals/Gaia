# projectFOUNDATION — Wave 24 FN-1 / FN-5 Resolution

**Date**: May 19, 2026
**From**: projectFOUNDATION (sporeGarden/gardens)
**To**: primalSpring (audit response)
**Context**: Resolution of FN-1 (BLAKE3 backfill) and FN-5 (Thread 1 WCM
CI validation) from primalSpring Wave 24 downstream gaps audit.

---

## FN-1: BLAKE3 Backfill — RESOLVED (partial)

### What was done

Fetched 11 public data sources for Thread 1 WCM from NCBI E-utilities,
UniProt streaming API, and KEGG REST API. Computed BLAKE3 hashes using
`b3sum` (Rust) and updated `data/sources/thread01_wcm.toml` in place.

**Result**: 10/25 sources now have BLAKE3 hashes.

### Fetched and hashed

| Source ID | Database | Accession | BLAKE3 (first 16) |
|-----------|----------|-----------|-------------------|
| ncbi_mg_genome | NCBI | NC_000908.2 | `7b247198c66e6fa7` |
| ncbi_mg_assembly | NCBI | GCA_000027325.1 | `0a8ff703568e8880` |
| uniprot_mg_proteome | UniProt | UP000000807 | `5c1e27ec868405be` |
| kegg_mg | KEGG | mge | `15c66456aee5b829` |
| ncbi_ecoli_genome | NCBI | NC_000913.3 | `67dee55704e1183e` |
| uniprot_ecoli_proteome | UniProt | UP000000625 | `79497129a06cbfca` |
| kegg_ecoli | KEGG | eco | `0749a78559066a8e` |
| ncbi_syn3a_genome | NCBI | CP016816.2 | `0687f00d56d0d477` |
| ncbi_syn3a_bioproject | NCBI | PRJNA357500 | `6c4cc430ec088bd1` |
| ncbi_syn3a_assembly | NCBI | GCA_900015295.1 | `d814dea9b5237c1d` |

### Known issue

`UP000018174` (M. mycoides proteome): UniProt streaming API returns
empty (20 bytes) as of May 19, 2026. Proteome may be reclassified.
Documented in source TOML with notes field.

### Remaining 15 sources (not auto-fetchable)

BRENDA enzyme kinetics (2), EcoCyc pathways, GitHub source repos (3),
literature DOIs (4), AlphaFold DB predictions, GROMACS binary,
Martini force field, EMDB cryo-ET (accessions pending), NIST TECRdb.
These require manual download, commit pinning, or accession enumeration.

---

## FN-5: Thread 1 WCM CI Validation — RESOLVED

### What was done

Extended the CI pipeline with two new validation gates:

1. **Hash coverage regression gate**: CI now fails if Thread 1 WCM
   drops below 10 hashed sources (baseline). Also gates overall hash
   count at >= 10.

2. **Thread 1 WCM source-target integrity check**: New CI step
   validates:
   - Source TOML parses and has BLAKE3 hashes
   - Target TOML parses with correct `total_targets` count
   - All targets reference valid springs
   - All numeric targets have tolerance fields
   - Workload directory exists with correct thread metadata

Both checks pass locally. CI pipeline now has **13 steps** (was 12).

### Bug fixes included

- **blake3_hash fallback**: `fetch_sources.sh` fallback used
  `hashlib.blake2b` (not BLAKE3). Fixed to require `blake3` Python
  module or error clearly instead of silently producing wrong hashes.

- **Tolerance truthiness**: New CI check initially failed on
  qualitative targets with `tolerance = 0.0` (Python falsy). Fixed
  to use `'tolerance' in t` (key existence) instead of value truth.

---

## Files Changed

| File | Change |
|------|--------|
| `data/sources/thread01_wcm.toml` | 10 blake3 fields populated, metadata updated |
| `data/sources/BLAKE3_BACKFILL_STATUS.md` | Full status with per-source detail |
| `deploy/fetch_sources.sh` | blake3_hash fallback bug fixed |
| `.github/workflows/ci.yml` | Hash regression gate + WCM integrity check |
| `validation/handbacks/UPSTREAM_AUDIT_PREP_MAY15_2026.md` | WCM source status updated |
| `README.md` | Source count updated with BLAKE3 count |

---

## Ecosystem Posture (Thread 1 WCM)

| Metric | Before | After |
|--------|--------|-------|
| BLAKE3 hashed sources | 0/25 | **10/25** |
| CI hash regression gate | None | **10 baseline** |
| CI WCM integrity check | None | **PASS** |
| WCM targets validated | 0/27 | 0/27 (upstream-blocked) |
| WCM workloads | 3 | 3 |

Thread 1 WCM targets remain 0/27 validated — this is a **degraded**
state (RPC stack unreachable), not a broken one. The pipeline handles
this with `[SKIP]` per `docs/DEGRADATION_BEHAVIOR.md`.
