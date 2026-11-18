<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Targeted GuideStone Standard

**Version**: 1.0 — May 11, 2026
**Status**: Active
**First Instance**: LTEE guideStone (Barrick Lab)

---

## Purpose

A **Targeted GuideStone** is a self-contained, portable, deployable artifact
composed from the ecoPrimals ecosystem. It carries binaries, data, and
validation harnesses that prove a specific scientific claim — independent of the
ecosystem that built it.

This standard defines how composed subsystems **bud** from the ecosystem into
artifacts that can leave ecosystem possession and run anywhere.

---

## Budding Model

Ecosystem components (primals, springs, foundation threads) are composed into a
portable artifact through a five-component budding process:

```
Ecosystem (13 primals, 8 springs, foundation threads, plasmidBin)
    │
    ▼
Budding Process
    ├── 1. Scope Graph       — which springs + primals contribute
    ├── 2. Data Manifest     — which datasets + source URIs
    ├── 3. Binary Bundle     — cross-arch ecoBin binaries
    ├── 4. Validation Harness — scenarios + tolerances + expected values
    └── 5. Provenance Chain  — BLAKE3 hashes + braid references + source refs
    │
    ▼
Targeted GuideStone (self-contained USB/ecoBin artifact)
    ├── Three-tier execution (Python → Rust → Primal)
    ├── liveSpore.json deployment tracking
    └── Source references for data refresh
```

**Key distinction**: A Targeted GuideStone is NOT a garden. Gardens consume
primals at runtime. A guideStone is a **frozen composition snapshot** — binaries
+ data + validation, all self-contained, that can run without the ecosystem
being present. It references the ecosystem for provenance and updates but does
not require it.

---

## The Five Components

### 1. Scope Graph

A TOML file declaring which ecosystem components contribute to this artifact.
This is the artifact's "birth certificate."

```toml
[guidestone]
name = "ltee-guidestone"
version = "1.0.0"
target = "Barrick Lab LTEE"
created = "2026-05-11"

[[spring]]
name = "wetSpring"
contributes = ["diversity metrics", "16S pipeline", "OTU analysis"]
binary = "ltee-fitness"

[[spring]]
name = "groundSpring"
contributes = ["statistical tests", "DFE fitting", "jackknife"]
binary = "ltee-mutations"

[[spring]]
name = "neuralSpring"
contributes = ["LSTM trajectory", "ESN regime detection", "GNN"]
binary = "ltee-alleles"

[[primal]]
name = "rhizoCrypt"
tier = 3
required = false
purpose = "DAG provenance (when NUCLEUS available)"

[[foundation_thread]]
id = "04"
name = "Environmental Genomics"
datasets = ["wiser_2013_fitness", "good_2017_alleles"]
```

### 2. Data Manifest

A TOML file listing every dataset in the artifact with full provenance.

```toml
[[dataset]]
id = "wiser_2013_fitness"
source_uri = "https://datadryad.org/stash/dataset/doi:10.5061/dryad.0hc2m"
license = "CC0"
local_path = "data/wiser_2013/"
blake3 = "abc123..."
retrieved = "2026-05-12"
refresh_command = "curl -L $source_uri -o data/wiser_2013.zip && unzip -o data/wiser_2013.zip -d data/wiser_2013/"

[[dataset]]
id = "good_2017_alleles"
source_uri = "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA380528"
license = "public-domain"
local_path = "data/good_2017/"
blake3 = "def456..."
retrieved = "2026-05-12"
refresh_command = "scripts/fetch_good_2017.sh"
```

Every dataset MUST have:
- `source_uri` — where the data was originally published
- `license` — the data license
- `blake3` — hash at time of bundling
- `refresh_command` — how to re-fetch from source

### 3. Binary Bundle

Cross-architecture ecoBin/genomeBin binaries. **No containers.** Primals
self-container via their genomeBin wrapper when needed — the guideStone stays
lean.

```
bin/
├── x86_64/
│   └── static/           # musl-static binaries (any Linux, no deps)
│       ├── ltee-fitness
│       ├── ltee-mutations
│       └── ...
└── aarch64/
    └── static/           # ARM builds (Apple Silicon Linux, Raspberry Pi)
        ├── ltee-fitness
        └── ...
```

Binary requirements:
- **musl-static linked** — zero runtime dependencies
- **BLAKE3 in CHECKSUMS** — integrity verification before execution
- Each binary is either a scoped subset of a spring's UniBin (`--scope ltee`)
  or a standalone scenario binary built from the spring's crate
- The entry point script detects `uname -m` / `uname -s` and selects the
  correct binary directory

### 4. Validation Harness

The `./validate` entry point runs every module and produces structured output.

```
validation/
├── expected/             # Reference outputs (pre-computed, hashed)
│   ├── module1_fitness.json
│   ├── module2_mutations.json
│   └── ...
├── tolerances.toml       # Named tolerances with scientific justification
└── validate.sh           # Entry point
```

Tolerances are named and justified:

```toml
[[tolerance]]
name = "power_law_exponent"
value = 0.001
justification = "Wiser 2013 reports exponent to 3 decimal places"

[[tolerance]]
name = "mutation_rate_per_gen"
value = 1e-10
justification = "Barrick 2009 detection limit from whole-genome sequencing"
```

Exit codes:
- `0` — all modules PASS at achieved tier
- `1` — one or more modules FAIL
- `2` — partial: Tier 1/2 PASS but Tier 3 unavailable (no NUCLEUS)

Output is structured JSON:

```json
{
  "artifact": "ltee-guidestone",
  "version": "1.0.0",
  "tier_reached": 2,
  "modules": [
    {
      "name": "power_law_fitness",
      "status": "PASS",
      "tier": 2,
      "checks": 42,
      "checks_passed": 42,
      "runtime_ms": 1200
    }
  ]
}
```

### 5. Provenance Chain

Every file in the artifact is hashed in `CHECKSUMS` (BLAKE3). Every computation
references:
- Source data (dataset ID from the data manifest)
- Binary version (from scope graph)
- Tolerance derivation (from tolerances.toml)

When a NUCLEUS is available (Tier 3), provenance flows through the trio:
- **rhizoCrypt** — DAG lineage
- **loamSpine** — certificate chain
- **sweetGrass** — braid integrity

Without NUCLEUS, provenance is structural: hashes + JSON logs. The artifact is
fully self-verifying at Tier 1/2 without any external infrastructure.

---

## Cross-Platform Story — No Containers

The guideStone carries **ecoBin/genomeBin binaries**, not containers. This
follows the existing binary ladder.

| Platform | Tier 1 (Python) | Tier 2 (Rust) | Tier 3 (Primal) |
|----------|-----------------|---------------|-----------------|
| Linux x86_64 | Native Python | musl-static binaries | Full NUCLEUS (deploy graphs) |
| Linux aarch64 | Native Python | musl-static binaries | Full NUCLEUS |
| macOS (Apple Silicon) | Native Python | genomeBin selects aarch64 binary | NUCLEUS via plasmidBin |
| macOS (Intel) | Native Python | genomeBin selects x86_64 binary | NUCLEUS via plasmidBin |
| Windows | Python (native or WSL2) | WSL2 or Linux environment | NUCLEUS via WSL2 |

On unsupported platforms, the entry point falls back to Tier 1 (Python-only,
pre-rendered HTML notebooks) and reports what is available.

The binaries are self-contained — no runtime dependencies, no container images.
If primals need containerization for a specific environment, the primals' own
genomeBin packaging handles that, not the guideStone.

---

## liveSpore: Deployment Tracking

`liveSpore.json` records every machine where the artifact has been validated.
Each `./validate` run appends an entry:

```json
{
  "timestamp": "2026-05-15T14:30:00Z",
  "hostname_hash": "blake3(hostname)",
  "arch": "x86_64",
  "os": "linux",
  "tier_reached": 2,
  "modules_passed": 7,
  "modules_total": 7,
  "runtime_ms": 342000
}
```

No PII is stored — hostname is BLAKE3-hashed. The artifact accumulates a
provenance trail of where it has been and what it proved.

---

## Data Freshness Protocol

The data manifest enables the artifact to update itself when internet is
available:

1. `./refresh` reads each dataset's `source_uri` and `refresh_command`
2. Re-fetches from the original source
3. Re-computes BLAKE3 hashes
4. Compares against bundled hashes — reports what changed
5. Re-runs validation to confirm the artifact still passes with updated data

This means the artifact can evolve without rebuilding from the ecosystem. It
references where data came from and can pull updates directly.

---

## Relationship to Existing Standards

| Standard | Relationship |
|----------|-------------|
| **ecoBin** (`ECOBIN_ARCHITECTURE_STANDARD.md`) | Binary bundle uses ecoBin format for cross-arch static binaries |
| **genomeBin** (`genomeBin/`) | Platform detection and binary selection use genomeBin wrapper patterns |
| **plasmidBin** | Tier 3 primal binaries come from plasmidBin releases, not bundled in the guideStone |
| **Foundation Threads** (`FOUNDATION_INTEGRATION_GUIDE.md`) | Data manifest references foundation thread datasets |
| **Provenance Trio** (`PROVENANCE_TRIO_INTEGRATION_GUIDE.md`) | Tier 3 provenance uses rhizoCrypt + loamSpine + sweetGrass |
| **Deployment Validation** (`DEPLOYMENT_VALIDATION_STANDARD.md`) | Validation harness follows the same three-tier pattern |
| **Derivation Anchoring** (`DERIVATION_ANCHORING_STANDARD.md`) | Extends §4: all numeric thresholds must trace through a 5-layer empirical chain with runtime enforcement |
| **Composition Health** (`COMPOSITION_HEALTH_STANDARD.md`) | `composition.status` available at Tier 3 |

---

## Creating a New Targeted GuideStone

1. **Define scope** — which scientific claim does this artifact prove?
2. **Write scope graph** — list contributing springs, primals, foundation threads
3. **Assemble data manifest** — collect datasets, hash them, record source URIs
4. **Build binary bundle** — cross-compile contributing spring binaries as musl-static ecoBins
5. **Write validation harness** — expected values, named tolerances, structured JSON output
6. **Generate CHECKSUMS** — BLAKE3 hash every file
7. **Initialize liveSpore.json** — empty array, ready for first validation run
8. **Write README** — plain text, no dependencies to read
9. **Test on clean machine** — validate Tier 1 and Tier 2 without ecosystem access
10. **Register in wateringHole** — add to the guideStone registry (this document's appendix)

---

## GuideStone Registry

| Name | Version | Target | Springs | Status |
|------|---------|--------|---------|--------|
| ltee-guidestone | 1.0.0 (pre-release) | Barrick Lab LTEE | wetSpring, groundSpring, neuralSpring, hotSpring, healthSpring, airSpring | Architecture defined, paper queues seeded |
| hotspring-cazyme-fel | 1.7.0 | Iglesias-Fernández 2015 (GH10 xylanase FEL) | hotSpring | GuideStone-grade: 190/190 checks, Phase 0 self-consistency, Derivation Anchoring (23/23 constants), automated artifact detection |

---

## Artifact Directory Layout

```
{name}-v{version}/
├── README                     # Plain text, no dependencies
├── CHECKSUMS                  # BLAKE3 of every file
├── liveSpore.json             # Deployment tracking (append-only)
├── scope.toml                 # Scope graph
├── data.toml                  # Data manifest
├── tolerances.toml            # Named tolerances with justification
├── {name}                     # Entry point (shell script)
│
├── bin/
│   ├── x86_64/
│   │   └── static/            # musl-static binaries
│   └── aarch64/
│       └── static/
│
├── data/
│   ├── {dataset_id}/          # One directory per dataset
│   └── ...
│
├── notebooks/
│   ├── *.py                   # Python analysis scripts
│   └── html/                  # Pre-rendered HTML (zero-dep viewing)
│
├── validation/
│   ├── expected/              # Reference outputs
│   └── validate.sh            # Validation entry point
│
└── deploy/                    # Tier 3 deploy graphs (optional)
    └── *.toml
```
