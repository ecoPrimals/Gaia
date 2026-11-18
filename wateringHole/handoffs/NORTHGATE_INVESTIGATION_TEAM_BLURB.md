# northGate Investigation Team — OSINT Loading + Evidence Braiding

**Date**: Sep 25, 2026 | **Wave**: 157 | **From**: sporeGate pipeline team
**To**: northGate investigation team (tamison / mokke)
**Posture**: Infrastructure READY. Pipeline PROVEN. Evidence braiding LIVE. Ready for data load.

---

## What's Ready For You

The [detroit.primals.eco](https://detroit.primals.eco) evidence infrastructure is fully automated. You push data,
the system braids it, serves it, and notifies search engines — all in one pipeline.

| Layer | Status | What It Does |
|-------|--------|-------------|
| **Evidence depot** | ✅ LIVE | BLAKE3-hashed file storage, SCP push to golgiBody |
| **Provenance trio** | ✅ LIVE | rhizoCrypt DAG + loamSpine spine + sweetGrass braid |
| **Auto-publish** | ✅ LIVE | Git push → build → evidence push → braid → SEO notify |
| **Caddy serving** | ✅ LIVE | `/evidence/*` file browser + `/evidence/` landing page |
| **SEO triple** | ✅ LIVE | IndexNow + GSC + Google Indexing API |

---

## How to Load OSINT Data

### 1. File Organization

Place evidence in the detroit evidence depot under collection directories:

```
detroit/evidence/
├── mde-foia-sep25/          ← existing (MDE FOIA responses)
├── osint-property/          ← NEW: property records, deed transfers
├── osint-corporate/         ← NEW: LARA filings, SOS records, annual reports
├── osint-financial/         ← NEW: campaign finance, IRS TEOS, bankruptcy
├── osint-court/             ← NEW: PACER filings, state court records
├── osint-media/             ← NEW: news articles, public statements, screenshots
└── osint-social/            ← NEW: public social media posts, event photos
```

### Naming Convention

```
{date}_{source}_{subject}_{description}.{ext}

Examples:
  2026-09-25_lara_purpose-group_annual-report-2024.pdf
  2026-09-25_ichat_banks-brian_criminal-history.pdf
  2026-09-25_pacer_14-46410_holland-bankruptcy-schedule.pdf
  2026-09-25_transparencyusa_banks-pac_contribution-report.pdf
  2026-09-25_waynecounty_2025200597_deed-transfer.pdf
```

### 2. Commit & Push

```bash
cd ~/Development/detroit
git add evidence/osint-property/ evidence/osint-corporate/  # etc.
git commit -m "evidence: add OSINT property records for Purpose Group entities"
git push origin main
```

The webhook pipeline will automatically:
1. Build the site (121+ pages)
2. Generate all artifacts (graph.json, site.json, llms.txt, manifest)
3. SCP push evidence to golgiBody
4. Braid evidence collections via the provenance trio
5. Notify search engines (IndexNow, GSC, Google Indexing API)
6. Verify consistency (sitemap vs site.json)

### 3. Verify

After push, check the output:
```
remote: webhook: detroit published to detroit.primals.eco (121 pages)
remote:   [artifacts] artifacts generated: ✅ All layers consistent...
remote:   [evidence] evidence pushed: N files synced
remote:   [braids] braided: osint-property (5 entries), osint-corporate (3 entries)
remote:   [seo] indexnow: 120 URLs submitted
remote:   [verify] consistency OK
```

Browse at: `https://detroit.primals.eco/evidence/`

---

## Braiding: How It Works

Every file you add gets a cryptographic provenance chain:

```
File on disk → BLAKE3 hash → rhizoCrypt DAG → loamSpine spine → sweetGrass braid
```

| Step | What Happens | Result |
|------|-------------|--------|
| **Hash** | BLAKE3 digest of the file | Content-addressable identity |
| **DAG** | Events grouped into a Merkle session | Tamper-evident session |
| **Spine** | Session committed to append-only ledger | Immutable history |
| **Braid** | PROV-O braid linking source→evidence→analysis | Cross-reference graph |

This means:
- **Every file has a provenance chain** — you can prove it existed at a specific time
- **Collections are atomic** — all files in a directory are braided as one session
- **The braid is the evidence** — the cryptographic chain IS the integrity proof

---

## OSINT Source Categories

Match these to the existing detroit source hierarchy:

| Tier | Source Type | Examples | Epistemic Status |
|------|-----------|----------|-----------------|
| **Primary** | Government databases | ICHAT, LARA, PACER, OTIS, TEOS | `record` |
| **Primary** | Court filings | Complaints, motions, orders | `record` or `filed` |
| **Primary** | FOIA responses | Agency letters, attached documents | `record` |
| **Secondary** | News articles | Detroit Free Press, Deadline Detroit, WXYZ | `corroborated` (if 2+ sources) |
| **Secondary** | Campaign finance | TransparencyUSA, MI SOS filings | `record` |
| **Tertiary** | Social media | Public posts, event photos | `allegation` or `inference` |
| **Tertiary** | Interviews | Recorded conversations (with consent) | `allegation` |

### Source Attribution

When adding OSINT, include a `README.md` in each collection:

```markdown
# osint-property — Wayne County Property Records

**Source**: Wayne County Register of Deeds
**URL**: https://waynecountylandrecords.com
**Access date**: 2026-09-25
**Search terms**: "Purpose Group", "Brian Banks", "Joseph Holland"
**Epistemic status**: record (government database)

## Files

| File | Subject | Doc# |
|------|---------|------|
| 2026-09-25_waynecounty_2025200597_deed-transfer.pdf | Purpose Group → Banks | 2025200597 |
```

---

## What You Can Add to the Site Content

Beyond evidence files, you can also add:
- New actor pages in `site/content/network/` (if new individuals are discovered)
- New entity pages in `site/content/network/entities/` (if new LLCs/nonprofits found)
- New edges in `data/edges.toml` (if new connections are documented)
- New entries in `site/config.toml` `[extra.actors]` or `[extra.entities]`

After adding actors/entities/edges, `detroit-build --check` will verify consistency:
```bash
cd ~/Development/detroit
detroit-build --check
```

---

## Key Databases to Search

These are the primary OSINT sources for the detroit investigation:

| Source | URL | What to Search |
|--------|-----|---------------|
| **MI ICHAT** | apps.michigan.gov/ichat | SID 2029469K (Banks), 2321035P (Holland) |
| **LARA** | cofs.lara.state.mi.us | Entity IDs: 803294855, 803295082, 802070120 |
| **PACER** | pacer.uscourts.gov | Cases: 09-46072, 14-46410, 26-47542 |
| **IRS TEOS** | apps.irs.gov/app/eos | EIN: 33-3537910, 87-2342269, 47-2441160 |
| **Wayne County ROD** | waynecountylandrecords.com | Doc#: 2025200597, 2025201292 |
| **TransparencyUSA** | transparencyusa.org | Candidate: Brian Banks |
| **State Bar MI** | zeekbeek.com/SBM | Search: Brian Banks (zero results) |
| **MDOC OTIS** | mdocweb.state.mi.us/OTIS2 | #443789 (Holland) |
| **MI SOS** | mi.gov/sos | Campaign finance: Bank on Banks PAC |
| **Google Scholar** | scholar.google.com | Case citations for related RICO patterns |

---

## Infrastructure Notes

- **Evidence depot path**: `/home/sporegate/Development/detroit/evidence/`
- **GolgiBody mirror**: `/opt/ecoPrimals/detroit/evidence/` (auto-synced on push)
- **Public URL**: `https://detroit.primals.eco/evidence/`
- **Provenance sockets** (sporeGate):
  - `/run/rhizocrypt/rpc.sock` — DAG
  - `/run/loamspine/rpc.sock` — Spine
  - `/run/sweetgrass/rpc.sock` — Braid
- **Build tool**: `detroit-build --root ~/Development/detroit`

---

## Contact

Questions about infrastructure or braiding: **sporeGate pipeline team**
Questions about legal strategy or filing: refer to `detroit/filings/`
Investigation coordination: **publicrecord@primals.eco**

---

*northGate team: the infrastructure is ready. Load the data. The braids follow automatically.
Every file you add gets a provenance chain. Every push updates the public record.
The system works — you just need to feed it.*
