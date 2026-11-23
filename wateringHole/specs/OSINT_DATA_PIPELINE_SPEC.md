# OSINT Data Pipeline — detroit.primals.eco

**Version:** 1.0.0
**Date:** September 26, 2026
**Status:** Active
**Audience:** northGate investigation team, any gate contributing OSINT data to detroit

---

## Purpose

This spec defines how investigation teams push OSINT (Open Source Intelligence) data
into the detroit evidence library and how it gets braided, published, and indexed.
The pattern is the same lifecycle used for AlphaFold data on westGate and QCD data
on blueGate — but adapted for investigative evidence where provenance and chain of
custody matter more than throughput.

---

## How It Differs from Science Data

| Concern | Science Data (westGate/blueGate) | OSINT Evidence (northGate→detroit) |
|---------|----------------------------------|-------------------------------------|
| Volume | TB-scale (AlphaFold: 23 TB) | KB–GB scale (screenshots, PDFs, FOIAs) |
| Velocity | Batch ingest (millions of files) | Trickle-in (dozens per audit session) |
| Provenance | Source URL + download hash | Database search + timestamp + screenshot |
| Braiding | `content.ingest` → CAS at ingress | BLAKE3 manifest → `evidence.push` → braid |
| Publication | Not published to web | Published to evidence library + linked from analysis pages |
| Sensitivity | Public datasets | Public records, but editorial review before publish |
| Priority | Throughput | Integrity + verify-yourself chain |

---

## Architecture

```
northGate (investigation)
  │
  ├─── Git push to Forgejo ─────────────────────┐
  │    (evidence/ directory in detroit repo)      │
  │                                               ▼
  │                                     golgiBody (Forgejo)
  │                                       │
  │                                       ├── webhook fires
  │                                       ├── zola build
  │                                       ├── evidence.push (sync to depot)
  │                                       ├── evidence.braid (BLAKE3 Merkle)
  │                                       └── seo.notify (IndexNow + GSC)
  │
  └─── Direct CAS push (future) ────────┐
       via nest atomic UDS               │
       `content.ingest` per dataset       ▼
                                     sporeGate (authority)
                                       ├── evidence-manifest.toml
                                       ├── braids.json
                                       └── rsync → golgiBody depot
```

---

## Current Path: Git Push (Working Today)

### 1. Collect evidence on northGate

```bash
# Create a dated evidence collection
mkdir -p evidence/moecs-audit-sep26/
# Screenshots, PDFs, notes go here
# Each collection = one directory under evidence/
```

### 2. Write a provenance doc

Every collection MUST have a markdown file explaining:
- **What** was searched (database, search terms, date)
- **How** results were captured (screenshots, downloads, exports)
- **Who** can verify (public database URL, step-by-step instructions)

Example: `evidence/moecs-audit-sep26/AUDIT_PROVENANCE.md`

### 3. Push via Forgejo

```bash
# northGate has a Forgejo access token (bd4eb71724...)
cd detroit
git add evidence/moecs-audit-sep26/
git commit -m "evidence: MOECS credential audit Sep 26 — 67 screenshots"
git push origin main
```

The webhook pipeline automatically:
- Builds the site (zola)
- Runs `evidence.push` (syncs evidence/ to golgiBody depot)
- Runs `evidence.braid` (BLAKE3 hashes → braids.json)
- Runs `seo.notify` (IndexNow + GSC sitemap resubmit)

### 4. Evidence manifest is auto-updated

`evidence-manifest.toml` on sporeGate tracks every file:
```toml
[[files]]
path = "moecs-audit-sep26/screenshot-001.png"
blake3 = "a1b2c3..."
size = 123456
mime = "image/png"
```

### 5. Braid record created

`braids.json` records each collection's Merkle root:
```json
{
  "collection": "moecs-audit-sep26",
  "merkle_root": "05b62434...",
  "files": 67,
  "bytes": 15144,
  "braided_at": "2026-09-26T11:25:01Z"
}
```

---

## Future Path: Nest Atomic Direct Push

When northGate has biomeOS + nestGate running, it can push evidence directly
through the primal mesh — same pattern as westGate's AlphaFold pipeline:

```
northGate                           sporeGate
  │                                    │
  ├── membrane evidence.ingest ────────┤
  │   (content.ingest via UDS)         │
  │                                    ├── nestGate CAS stores files
  │                                    ├── rhizoCrypt DAG session
  │                                    ├── loamSpine commits Merkle
  │                                    └── sweetGrass attribution braid
  │                                    │
  └── membrane evidence.status ────────┤
      (verify ingress, check braids)   └── returns provenance chain
```

### What's Needed for Direct Push

| Component | Status | Gate |
|-----------|--------|------|
| biomeOS installed | ❌ Not yet | northGate |
| nestGate running | ❌ Not yet | northGate |
| WireGuard mesh membership | ❌ Not yet | northGate |
| `membrane evidence.ingest` command | ❌ Not built | cellMembrane |
| Signal graph `detroit_evidence_ingress.toml` | ❌ Not built | cellMembrane |
| Provenance trio (rhizoCrypt + loamSpine + sweetGrass) | ✅ Running | sporeGate |

### Implementation Order

1. **northGate mesh enrollment** — `membrane gate.bootstrap northGate`
2. **biomeOS deploy** — nestGate + provenance trio on northGate
3. **`membrane evidence.ingest`** — cellMembrane command, modeled on `alphafold.ingest` but simplified (no Phase B/C, just local directory → CAS)
4. **Signal graph** — `detroit_evidence_ingress.toml` in cellMembrane data/
5. **Cross-gate verification** — sporeGate can verify northGate's braids against its own CAS

---

## Evidence Collection Standards

### Directory Naming

```
evidence/<source>-<type>-<date>/
```

Examples:
- `evidence/moecs-audit-sep26/` — MOECS credential search results
- `evidence/mde-foia-sep25/` — MDE FOIA response documents
- `evidence/lara-filings-oct01/` — LARA corporate filing screenshots
- `evidence/court-records-oct03/` — PACER/Wayne County court documents

### Required Files Per Collection

| File | Purpose |
|------|---------|
| `PROVENANCE.md` or `*_PUBLISH.md` | What was collected, how, when, verification steps |
| Raw evidence files | Screenshots (.png), documents (.pdf), exports (.csv) |
| Optional: `ANALYSIS.md` or `*_BRAID.md` | Cross-referencing analysis connecting this evidence to other collections |

### BLAKE3 Integrity

Every file gets BLAKE3-hashed into `evidence-manifest.toml`. This means:
- **Tamper detection** — any modification changes the hash
- **Deterministic verification** — `b3sum <file>` reproduces the hash
- **Merkle root** — per-collection Merkle root in `braids.json`
- **Git-signed commits** — the commit hash + BLAKE3 = dual integrity chain

---

## Converging with the Broader Mesh

The detroit evidence pipeline is a **specific instance** of the general primal
data ingestion pattern. Every gate in the mesh can produce evidence or data:

| Gate | Data Type | Pipeline |
|------|-----------|----------|
| westGate | AlphaFold structures (23 TB) | `membrane alphafold.ingest` → nestGate CAS |
| blueGate | QCD lattice configs | `membrane hotspring.ingest` → nestGate CAS |
| northGate | OSINT evidence (screenshots, PDFs) | `git push` → evidence.push → braid (current) |
| northGate | OSINT evidence (future) | `membrane evidence.ingest` → nestGate CAS |
| sporeGate | Published sites + evidence depot | `membrane evidence.push` → golgiBody rsync |

The pattern is always:
1. **Acquire** — files land on a gate
2. **Hash** — BLAKE3 at ingress
3. **Store** — CAS (nest atomic) or evidence depot
4. **Braid** — provenance trio (rhizoCrypt → loamSpine → sweetGrass)
5. **Publish** — site build + SEO notify (for public evidence)

Detroit just adds step 5 (publication) to the standard data pipeline.
The investigation data flowing through northGate is structurally identical
to protein structures flowing through westGate — different domain, same
integrity guarantees.
