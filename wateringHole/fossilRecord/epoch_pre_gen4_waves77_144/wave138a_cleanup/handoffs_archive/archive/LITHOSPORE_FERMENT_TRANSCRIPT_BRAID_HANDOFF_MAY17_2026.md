# lithoSpore Ferment Transcript & Braid Handoff Pattern

**Date:** May 17, 2026
**Author:** lithoSpore workstream
**Audience:** wetSpring, hotSpring, groundSpring teams; NUCLEUS/provenance trio maintainers
**Status:** Active — defines the upstream braid handoff contract for lithoSpore
**License:** AGPL-3.0-or-later

---

## Summary

lithoSpore is the ecosystem's first **Targeted GuideStone** — a portable,
self-validating scientific artifact. It ships summary statistics (~3.4 MB)
on a USB and validates 73 science checks airgapped. But the full upstream
data (raw sequencing reads, complete archives) can be 10s–100s of GB.

This handoff defines the **ferment transcript pattern**: how upstream
springs process the massive data on NUCLEUS, record provenance via the
trio, and hand the braid to lithoSpore for portable, auditable science.

**lithoSpore is a functional use case that constrains how the ecosystem
evolves.** The requirements below are not abstract — they emerge from a
real artifact that must validate real papers on real hardware.

---

## The Problem

| Dataset | Published Paper | Raw Data | Ships on USB |
|---------|----------------|----------|-------------|
| Barrick 2009 | Nature 461:1243 | ~15 GB (19 genomes) | 2 KB (parameters JSON) |
| Good 2017 | Nature 551:45 | ~50 GB (metagenomic) | 4 KB (simulation tallies) |
| Blount 2012 | Nature 489:513 | ~30 GB (replay seq) | 3 KB (replay summary) |
| Tenaillon 2016 | Nature 536:165 | ~200 GB (264 genomes) | 1 KB (published stats) |

The spore can't carry the mountain. But it must prove the mountain was climbed.

---

## The Ferment Transcript Pattern

A **ferment transcript** is the provenance record of upstream computation:
the spring does the fermentation (processing raw data into validated results),
and the guideStone carries the transcript.

```
Spring on NUCLEUS (e.g., wetSpring)
    │
    ├─ pulls raw data (SRA accession PRJNA294072, 200 GB)
    ├─ runs computation (breseq pipeline on 264 genomes)
    ├─ produces results (mutation rates, spectrum, accumulation curves)
    │
    ├─ rhizoCrypt: dag.session.create → event.append × N → session.complete
    │   └─ merkle_root covers every intermediate computation
    ├─ loamSpine: spine.create → entry.append (result summary + hashes)
    │   └─ immutable ledger entry with DID anchor
    └─ sweetGrass: braid.create (attribution: spring + data + operator)
        └─ W3C PROV-O braid linking computation to source data
    │
    ▼
Handoff to lithoSpore:
    ├─ summary_stats.json (~KB) — the published-equivalent numbers
    ├─ braid_id (string) — the sweetGrass braid reference
    ├─ dag_session_id (string) — the rhizoCrypt session ID
    ├─ merkle_root (string) — the DAG merkle covering the computation
    └─ spine_id (string) — the loamSpine ledger entry
```

The guideStone artifact receives these and stores them in `data.toml`:

```toml
[[dataset]]
id = "tenaillon_2016_genomes"
data_tier = "summary"
upstream_spring = "wetSpring"
upstream_braid = "braid-abc123..."     # sweetGrass braid ID
upstream_dag_session = "dag-def456..." # rhizoCrypt session ID
```

---

## Contract for Upstream Springs

### What the spring MUST produce

1. **Summary statistics** matching the published paper's claims — the same
   numbers lithoSpore validates against (e.g., mutation rate, spectrum fractions,
   Ts/Tv ratio). These become the `validation/expected/*.json` content.

2. **A sweetGrass braid** covering the full computation, with:
   - `agent`: the spring identity (e.g., `wetSpring@v0.3.0`)
   - `activity`: the computation method (e.g., `breseq-0.38.1`)
   - `entity`: the raw data (SRA accession + BLAKE3 of downloaded reads)
   - `derivedFrom`: chain from raw reads → variant calls → summary stats

3. **A rhizoCrypt DAG session** with events for each major computation step
   (download, alignment, variant calling, filtering, summary extraction).
   The `merkle_root` of the completed session covers the entire pipeline.

4. **A loamSpine entry** recording the final result hash + timestamp + DID.

### What the spring MUST NOT do

- Do not send the raw data to lithoSpore — send only summary + provenance
- Do not assume lithoSpore has SRA toolkit or breseq installed
- Do not require NUCLEUS to validate summary stats (airgapped must work)

### Wire format

The handoff is a JSON object written to `provenance/braids/{dataset_id}.json`
in the lithoSpore tree (or received via `nest.store` signal when biomeOS
supports it):

```json
{
  "dataset_id": "tenaillon_2016_genomes",
  "spring": "wetSpring",
  "spring_version": "0.3.0",
  "braid_id": "braid-abc123...",
  "dag_session_id": "dag-def456...",
  "dag_merkle_root": "789abc...",
  "spine_id": "spine-xyz...",
  "computation": {
    "tool": "breseq",
    "tool_version": "0.38.1",
    "input_accession": "PRJNA294072",
    "input_blake3": "...",
    "output_blake3": "...",
    "wall_time_seconds": 86400,
    "node_count": 264
  },
  "summary_blake3": "...",
  "timestamp": "2026-05-17T12:00:00Z"
}
```

---

## How lithoSpore Uses the Braid

### Airgapped (standalone mode)

- Validates summary stats against published claims (73 checks, all PASS)
- The braid metadata is **present** in `data.toml` but **not verified** (no primals)
- The audit trail is self-documenting: anyone reading `data.toml` sees the
  provenance chain and knows where to look for full verification

### Online (LAN/TURN mode)

- `litho verify` follows the braid: queries sweetGrass for the braid,
  confirms the DAG merkle root matches, confirms the spine entry is sealed
- If the full computation is re-run (e.g., upstream data refresh), the
  new braid replaces the old one — `litho fetch --full` can pull both
  the raw data and the updated provenance

### Tier 3 (NUCLEUS composition)

- lithoSpore's own validation run **adds** to the provenance chain:
  its `try_record_tier3()` creates a new DAG session, spine entry, and braid
  that **references** the upstream braid
- The result: a linked provenance chain from raw data → spring computation →
  guideStone validation → deployment history (`liveSpore.json`)

---

## Why This Matters for Upstream Teams

lithoSpore is a **functional constraint** on ecosystem evolution:

1. **Provenance trio must produce portable braids** — a braid that only
   works inside NUCLEUS is useless to a USB artifact. The braid format
   must be self-describing and verifiable with a single JSON-RPC call.

2. **Springs must separate summary from raw** — the ferment transcript
   pattern forces springs to define clear output contracts: "here are the
   numbers that matter, here is the proof they were computed correctly."

3. **NUCLEUS deployment graphs must support handoff** — the composition
   pattern needs a `handoff` phase where computation results flow from
   spring to garden artifact.

4. **Signal routing must support cross-garden provenance** — when biomeOS
   evolves `nest.store`, the handoff should collapse to a single signal:
   `ctx.dispatch("nest.store", { target: "lithoSpore", braid: "..." })`.

---

## Current State (May 17, 2026)

| Component | Status |
|-----------|--------|
| `data.toml` with `upstream_braid` / `upstream_dag_session` fields | **Wired** (empty — awaiting first spring handoff) |
| `provenance.rs` JSON-RPC client for trio | **Implemented** (lithoSpore's own Tier 3 recording) |
| `litho fetch --full` for pulling raw upstream data | **Implemented** |
| `litho verify` braid chain validation | **Planned** (requires sweetGrass query API) |
| wetSpring breseq pipeline with provenance recording | **Not started** (this handoff initiates it) |
| `provenance/braids/` directory for received handoffs | **Planned** |
| Signal-based handoff via `nest.store` | **Future** (requires biomeOS signal dispatch) |

---

## Datasets Awaiting Upstream Braid

| Dataset | Spring | Computation | Priority |
|---------|--------|-------------|----------|
| `tenaillon_2016_genomes` | wetSpring | breseq on 264 genomes | **HIGH** — most impressive for Barrick/Lenski |
| `barrick_2009_mutations` | wetSpring | breseq on 19 genomes | HIGH |
| `good_2017_alleles` | wetSpring | metagenomic variant calling | MEDIUM |
| `blount_2012_citrate` | wetSpring | replay experiment sequencing | MEDIUM |
| `wiser_2013_fitness` | groundSpring | curve fitting (already ~complete, small data) | LOW |
| `anderson_predictions` | hotSpring | RMT computation from fitness landscape | LOW |

---

## Related Documents

- `TARGETED_GUIDESTONE_STANDARD.md` — the guideStone grade definition
- `PROVENANCE_TRIO_INTEGRATION_GUIDE.md` — trio wiring patterns
- `SWEETGRASS_SPRING_BRAID_PATTERNS.md` — braid W3C PROV-O structure
- `LITHOSPORE_USB_DEPLOYMENT.md` — USB deployment standard
- `lithoSpore/docs/ARCHITECTURE.md` — lithoSpore architecture (two-tier data model, ferment transcript pattern)
