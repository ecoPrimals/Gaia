# northGate — OSINT Mesh Integration Blurb

**Date:** September 26, 2026
**From:** sporeGate (detroit site authority)
**To:** northGate investigation team
**Re:** Sending data directly to sporeGate + primals mesh integration

---

## What's Working Now

The detroit evidence pipeline is live and braiding:

- **128 pages** published at [detroit.primals.eco](https://detroit.primals.eco)
- **27 evidence files** (60.8 MB) in the depot, BLAKE3-hashed
- **2 braided collections**: `mde-foia-sep25` (21 files) + `credential-audit-sep26` (2 files)
- **IndexNow** submitting to Bing/DuckDuckGo/Yandex on every push
- **Google Indexing API** unlocked (SA is Owner, 120/120 URLs notified)
- **Bing Webmaster Tools** verified via XML file

### How You Push Data Today

```bash
cd detroit
mkdir -p evidence/<source>-<type>-<date>/
# Drop screenshots, PDFs, notes
# Write a PROVENANCE.md explaining what/how/when
git add evidence/
git commit -m "evidence: <description>"
git push origin main
# Token: bd4eb71724425b4aa1f70ad60a81825f91a4363b (write:repository)
# Remote: https://sporegate:TOKEN@git.primals.eco/publicRecord/detroit.git
```

The webhook pipeline does the rest: build → evidence.push → braid → SEO.

---

## What Needs Your Data Next

### Priority 1: MOECS Screenshots (67 files)

The credential audit analysis is live at `/analysis/credential-audit/` but the
67 MOECS screenshots that back it up haven't arrived in the evidence depot yet.
Drop them in `evidence/credential-audit-sep26/screenshots/` and push.

### Priority 2: Financial Data Extracts

The funding flow page (`/analysis/funding-flow/`) references MDE audit data.
If you have structured financial extracts (CSV, XLSX, or tables), drop them in
`evidence/financial-extracts-sep26/` with a provenance doc.

### Priority 3: Ongoing OSINT Collections

As you mine new data, each collection gets its own directory:
```
evidence/lara-filings-oct01/
evidence/court-records-oct03/
evidence/campaign-finance-oct05/
```

Each with a `PROVENANCE.md` explaining what database was searched, when,
how to verify independently.

---

## Where We're Converging — Primals Mesh Integration

Right now you push via git. The next step is **direct mesh push** via primals —
the same pipeline that westGate uses for AlphaFold data (23 TB braided through
nest atomic) and blueGate uses for QCD lattice configs.

### What You'll Get

```
northGate                                sporeGate
  │                                         │
  ├── membrane evidence.ingest ─── WireGuard ──┤
  │   (BLAKE3 at source)                    │
  │                                         ├── nestGate CAS stores
  │                                         ├── provenance trio braids
  │                                         └── evidence.push → golgiBody
  │                                         │
  └── membrane evidence.status ─────────────┤
      (verify braids from any gate)         └── returns full chain
```

**Integrity guarantee**: BLAKE3 is computed on northGate at the moment of
capture. The hash travels through WireGuard to sporeGate's nestGate CAS.
The provenance trio (rhizoCrypt + loamSpine + sweetGrass) braids it with
attribution. Nobody in the chain can modify the evidence without breaking
the hash — not even sporeGate.

### What's Needed on northGate

| Step | What | Command | Status |
|------|------|---------|--------|
| 1 | WireGuard mesh enrollment | `membrane gate.bootstrap northGate` | ❌ Not yet |
| 2 | biomeOS install | Standard gate composition | ❌ Not yet |
| 3 | nestGate running | Comes with biomeOS | ❌ Not yet |
| 4 | `evidence.ingest` command | cellMembrane build | ❌ Not built yet |

Steps 1-3 are standard gate enrollment — same process every gate goes through.
Step 4 is a new cellMembrane command modeled on `alphafold.ingest` but much
simpler (no 23 TB, no multi-phase — just local files → CAS → braid).

### How This Is Different from AlphaFold

| Dimension | AlphaFold (westGate) | Detroit OSINT (northGate) |
|-----------|---------------------|--------------------------|
| Scale | 23 TB, 246M structures | KB–GB, dozens of files per audit |
| Source | EBI public database | MOECS, LARA, PACER, MDE, court records |
| Ingress | 3-phase (proteomes → expanded → remote) | 1-phase (local files → CAS) |
| Braiding | Per-accession at download | Per-collection after capture |
| Publication | Not published to web | Published to detroit.primals.eco |
| Provenance | Source URL + download timestamp | Database search + screenshot + verification steps |
| Sensitivity | None (public protein data) | Editorial review before publish (public records, but named individuals) |

The pipeline code is simpler. The provenance documentation requirements are
stricter because this is investigative evidence, not scientific data.

---

## Coordination — What Each Team Does

### northGate Investigation Team

- Mine OSINT data from public databases
- Screenshot everything, write provenance docs
- Push evidence via git (now) or mesh (future)
- Write analysis docs when patterns emerge (site team converts to pages)
- Flag anything that needs editorial review before publish

### sporeGate Site Team

- Convert analysis docs to Zola pages
- Maintain graph data (actors, entities, edges)
- Run the publish pipeline (zola → evidence.push → braid → SEO)
- Handle SEO (IndexNow, GSC, Bing Webmaster Tools)
- Build the `evidence.ingest` command when northGate is mesh-ready

### golgiBody (Production)

- Serves detroit.primals.eco (Caddy + static files)
- Hosts evidence depot (rsync'd from sporeGate)
- Runs Forgejo (git.primals.eco) + webhook handlers
- Runs hbbs/hbbr (RustDesk outer membrane)

---

## Graph Data — How to Add New Connections

When you find new actors, entities, or connections, include them in your
analysis docs and the site team will add them to:

- `site/config.toml` — node registry (actors + entities)
- `data/edges.toml` — edge registry (connections with epistemic status)
- Content pages — taxonomy tags for cross-referencing

### Edge Format

```toml
[[edge]]
source = "purpose_group"
target = "macdowell"
type = "financial"
epistemic_status = "record"    # record | corroborated | inference | allegation
note = "10% SSA + ALL costs = 72.67% of revenue"
source_doc = "Purpose Group Management Agreement (FOIA)"
```

Epistemic status matters — mark each connection with how well-documented it is.
The site renders these differently and the graph JSON preserves the distinction.

---

## Current Site State (Sep 26, 2026)

| Metric | Value |
|--------|-------|
| Total pages | 128 |
| Analysis pages | 9 (RICO, institutional capture, allied cases, CBC, credential audit, funding flow, words-vs-numbers, land deal, detroit literacy) |
| Book analysis | 2 (It Had 2 Happen, Black Mafia Family) |
| Network actors | 15+ profiled |
| Network entities | 12+ profiled |
| Graph edges | 70+ documented connections |
| Evidence depot | 27 files, 60.8 MB, 2 braided collections |
| Search indices | Google (120 URLs), Bing (IndexNow), DuckDuckGo, Yandex |

The site is growing fast. Every piece of data you push makes the evidence
library stronger. The mesh integration will make the pipeline even tighter —
BLAKE3 integrity from the moment of capture, through to publication.

---

*Spec: [OSINT_DATA_PIPELINE_SPEC.md](../specs/OSINT_DATA_PIPELINE_SPEC.md)*
*Previous blurb: [NORTHGATE_INVESTIGATION_TEAM_BLURB.md](NORTHGATE_INVESTIGATION_TEAM_BLURB.md)*
