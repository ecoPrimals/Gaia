<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# Sediment Layer Model

**Audience**: All ecosystem participants — primals, springs, gardens, contributors
**Purpose**: Defines how validated results accumulate as geological sediment,
forming the provable substrate that strengthens with every run
**Last Updated**: May 6, 2026

---

## The Geological Metaphor

Every computation in the ecoPrimals ecosystem produces artifacts: data
downloads, intermediate results, final outputs, provenance DAGs, ledger
entries, and attribution braids. In most systems, these are ephemeral —
logs that scroll past, results overwritten by the next run.

In our ecosystem, they are **geological**: they accumulate, compress,
and become load-bearing structure for everything above.

```
Products (helixVision, esotericWebb, blueFish)
├── gen4 — creative surface
│
Springs (wetSpring, hotSpring, groundSpring, …)
├── Validation runs — each one a sediment event
│
projectFOUNDATION (gardens/projectFOUNDATION)
├── Declared targets + data sources
│
projectNUCLEUS
├── Deployed primals on gates
│
Primals (13 ecobin, BTSP Phase 3)
└── Bedrock
```

Each validation run deposits a layer. Over time, the layers compact.
What was once a single run becomes an immovable fact: "Paper A's cell
cycle was reproduced at 9.0 ± 0.3 hours, three times, on two gates,
with BLAKE3 provenance from NCBI NC_000908.2 through toadStool dispatch."

---

## Anatomy of a Sediment Layer

A sediment layer is a single validated run's complete record. It contains:

### 1. Source Stratum

Content-addressed data fetched from public repositories.

| Component | Format | Stored In |
|-----------|--------|-----------|
| NCBI genomes | GenBank (.gb) | NestGate (key: `ncbi:nucleotide:<accession>`) |
| UniProt proteomes | FASTA (.fasta.gz) | NestGate (key: `uniprot:proteome:<id>`) |
| KEGG pathways | JSON/XML | NestGate (key: `kegg:<organism>`) |
| PDB structures | mmCIF | NestGate (key: `pdb:<id>`) |

Every file's BLAKE3 hash is computed at fetch time and recorded in the
rhizoCrypt DAG as a `DataCreate` event. If the upstream source changes
(BRENDA updates an enzyme constant), the old hash remains in NestGate and
the new hash creates a new ledger entry. The diff is structural — the
foundation tracks both versions and marks which targets depend on which.

### 2. Computation Stratum

Workload execution records from toadStool.

| Component | Format | Stored In |
|-----------|--------|-----------|
| toadStool dispatch ID | UUID | rhizoCrypt DAG |
| CPU/GPU/NPU time | JSON | rhizoCrypt DAG |
| Result artifacts | binary | NestGate |
| [OK]/[FAIL] counts | text | validation report |

### 3. Provenance Stratum

The temporal and causal record of the entire run.

| Component | Primal | Format |
|-----------|--------|--------|
| Ephemeral DAG | rhizoCrypt | Merkle tree of all events |
| Permanent ledger | loamSpine | Linear append-only log |
| Attribution braids | sweetGrass | W3C PROV-O compliant |

### 4. Report Stratum

Human-readable summary written to `validation/run-<timestamp>/report.md`.

```
Run: 2026-05-06T14:23:00Z
Thread: wcm (Whole-Cell Modeling)
Gate: ironGate
Workloads: 3 executed, 3 passed
Targets: 12 checked, 11 passed, 1 pending
DAG root: blake3:a1b2c3d4…
Loam entry: #47
Braid: authors=7 contributors=3 sources=12
```

---

## Layer Compaction

Individual layers are granular — one run, one timestamp. Over time, they
compact into higher-order structures:

### Weekly Digest

Summarizes all validation runs in a week. Identifies:
- Newly validated targets (first [OK])
- Regression alerts (previously [OK] now [FAIL])
- New data sources fetched
- Cross-spring validation (same target validated by multiple springs)

### Thread Summary

Per-domain-thread aggregate. "Thread 1 (WCM) has 24 targets, 18 validated,
3 pending, 3 not yet attempted. 47 total sediment layers deposited."

### Foundation Snapshot

The complete state of all threads at a point in time. This is what products
consume: a provably correct, content-addressed set of validated results.

---

## How Springs Deposit Sediment

### Step 1: Declare What You Validate

Add your spring's name and workload binary to the appropriate target TOML:

```toml
[[targets]]
id = "paper_a_cell_cycle"
spring = "hotSpring"
```

### Step 2: Run Through the Pipeline

```bash
cd gardens/projectFOUNDATION/deploy
bash foundation_validate.sh --thread wcm
```

The pipeline wraps your workload in provenance automatically:
rhizoCrypt session → NestGate storage → toadStool dispatch → loamSpine commit.

### Step 3: The Sediment Deposits Itself

After a successful run, the `validation/run-<timestamp>/` directory
contains the full layer. The rhizoCrypt DAG root and loamSpine entry
are permanent. The sweetGrass braid ensures attribution flows to everyone
who contributed — from the original paper authors to the spring developer
who wrote the validator.

### Step 4: The Target Gets Marked

When the run succeeds, `data/targets/*.toml` is updated:

```toml
blake3 = "a1b2c3d4e5f6…"
validated = true
```

This is permanent. It means: "this result was reproduced with full
provenance, and the entire chain from NCBI genome to final output is
content-addressed and verifiable."

---

## Cross-Spring Reinforcement

The strongest sediment forms when multiple springs validate the same
target independently:

```
Target: Paper A gene essentiality (79% ± 3%)

Layer 12: wetSpring  → 78.2% [OK]  (ODE model, CPU)
Layer 23: hotSpring  → 79.1% [OK]  (barraCuda GPU, f64 WGSL)
Layer 31: hotSpring  → 78.8% [OK]  (different gate, same binary)
Layer 44: wetSpring  → 79.4% [OK]  (updated UniProt proteome)
```

Four independent validations from two springs on different hardware.
The sediment is load-bearing. A new paper that depends on this result
can cite the foundation layer rather than re-running from scratch.

---

## Erosion and Repair

Sediment layers can erode when upstream data changes:

| Event | Response |
|-------|----------|
| NCBI updates a genome assembly | Old hash preserved, new hash fetched, dependent targets re-validated |
| A paper issues a correction | New target values added, old targets preserved with `superseded_by` |
| A spring binary is updated | Re-run validation to confirm results match, depositing a new layer |
| A primal changes its IPC interface | Re-run pipeline to confirm provenance still records correctly |

Erosion is visible. The foundation tracks every change as a new DAG
event, so the delta between "before" and "after" is structural. Nothing
is silently overwritten.

---

## The Living Geology

This is what the user meant by "living geology": the foundation is not
a static database. It is a continuously growing geological record where:

- **Bedrock** = NCBI, UniProt, KEGG (public, immutable reference data)
- **Sedimentary layers** = validated results from spring runs
- **Metamorphic layers** = cross-spring reinforcement (same target, multiple springs)
- **Igneous intrusions** = novel hypotheses that emerge from unexpected cross-thread patterns
- **Fossils** = the provenance records — rhizoCrypt DAGs, loamSpine entries, sweetGrass braids

When we hand a foundation thread to a new collaborator, they don't get
a paper citation. They get a geological core sample: every data source,
every computation, every attribution, content-addressed and provable.

That is the difference between a bibliography and a foundation.

---

## Related Documents

- `FOUNDATION_INTEGRATION_GUIDE.md` — operational integration for springs
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — rhizoCrypt + loamSpine + sweetGrass patterns
- `SWEETGRASS_SPRING_BRAID_PATTERNS.md` — per-spring attribution patterns
- `EVOLUTION_STATUS_WAVE66.md` — the water cycle model (seasonal evolution)
- `gardens/projectFOUNDATION/deploy/README.md` — quick start for validation runs
