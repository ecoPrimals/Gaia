# DISCOVERED_BY Standard — Passive Discovery Audit

**Date**: 2026-07-14 (Wave 139a, reviewed 155h)
**Status**: Active standard
**Owner**: sporePrint team + overwatch
**Supersedes**: SHOW_HN_PUBLICATION.md as engagement strategy (that doc's rigor checklist is retained as internal quality bar only)

---

## The Pivot

SHOW_HN assumed **active presentation** to Hacker News — Y Combinator's audience, Y Combinator's platform, Y Combinator's extractive flywheel (funding → growth → exit → repeat). That engagement model embeds the ecosystem in exactly the gravity well it was built to escape. HN is a signal-targeting metric, not an engagement front.

DISCOVERED_BY assumes **passive discovery** — someone (AI bot, PI, homelabber, journalist, search engine) stumbles onto us without context, and the surface must hold up under scrutiny with zero preparation. No platform dependency. No single engagement front. The surface is sovereign and the quality bar is internal.

The AI bot review of Wave 138b proved this is the real threat model. An AI was able to:
1. Cross-reference institutional details to identify the human author
2. Find that "live validation results" were static snapshots
3. Note zero community engagement (0 stars, 0 issues, 0 PRs)
4. Flag page count inconsistencies as credibility issues
5. Identify broken pages (projectFOUNDATION 404) on the institutional path

**Discovery is the standard now.** Not presentation. Not platform engagement.

## Engagement Topology

The ecosystem's engagement surfaces align with sovereign and commons values:

| Surface | Why | Extractive? |
|---------|-----|-------------|
| **primals.eco** | The sovereign surface itself — owned, hosted, cryptographically anchored | No |
| **ORCID** | Academic commons, persistent researcher ID, not paywalled | No |
| **Zenodo** | Research data repository, DOI minting, CERN-operated commons | No |
| **Keyoxide** | Decentralized identity verification, no platform account required | No |
| **crates.io** | Open registry, community-governed, Rust Foundation | No |
| **Forgejo** | Self-hosted git, sovereign code hosting | No |
| **Reddit** | Community-moderated (r/homelab, r/selfhosted, r/rust) — imperfect but not VC-curated | Partial |
| **Medium (attsi)** | attsi's philosophical voice — attsi owns the voice, not the platform | Partial |

Surfaces intentionally **not** used as engagement fronts:
- **Hacker News** — Y Combinator property. Useful as internal quality bar ("would this survive HN scrutiny?"), not as engagement target.
- **Twitter/X** — extractive attention economy
- **LinkedIn** — professional extraction, identity leakage risk
- **Product Hunt** — VC showcase

The HN rigor checklist (evidence integrity, narrative readiness, honest limitations, comparison tables) is preserved as an internal standard in `SHOW_HN_PUBLICATION.md`. It answers: "if hostile experts examined us, would the claims hold?" That's a quality question, not a platform question.

---

## Persona Matrix

Every external-facing surface is evaluated against 6 discovery personas:

### 1. AI Bot (scraper/reviewer)
**Arrives via**: Crawls GitHub orgs + primals.eco, cross-references with public databases
**Evaluates**: identity.json, llms.txt, JSON-LD, ORCID, sitemap.xml, GitHub metadata
**Crack points**: Page count inconsistencies, stale certification manifest, identity leakage, content-manifest.toml not served

### 2. Homelabber (r/homelab, r/selfhosted)
**Arrives via**: Reddit link → outreach/homelab landing → tries to deploy
**Evaluates**: Can I run this today? What hardware do I need? Is there a binary?
**Crack points**: Scaffold maturity pages, no downloadable artifact, deploy step is TBD

### 3. PI / Grant Reviewer
**Arrives via**: Google Scholar, ORCID → primals.eco/lab/ or contact page
**Evaluates**: Lab evidence, provenance chains, reproducibility claims, institutional contact path
**Crack points**: Broken links on institutional path, primal count inconsistencies, no self-serve compute

### 4. Hacker News Reader
**Arrives via**: Show HN or related thread → primals.eco landing
**Evaluates**: Stats claims, try-it commands, GitHub activity, community signals
**Crack points**: Zero stars/issues/PRs, org bios sound like DevOps, blank repo descriptions, tarball not downloadable

### 5. LLM / Agent (llms.txt consumer)
**Arrives via**: robots.txt → llms.txt → site-index or sitemap.xml
**Evaluates**: Machine-readable structure, endpoint availability, content topology
**Crack points**: content-manifest.toml not served, site-index incomplete, stale counts in llms.txt

### 6. Journalist / Podcaster
**Arrives via**: Email contact or browsing primals.eco
**Evaluates**: Story, identity, claims, dual-voice model
**Crack points**: Triple naming confusion, dual-voice not explained to visitors, mycology branding

---

## Surface Audit Checklist

Run this checklist whenever content is deployed or presence changes. Each item is PASS/FAIL.

### GitHub Surface

| ID | Check | Command / Method |
|----|-------|-----------------|
| GH-1 | All repo descriptions contain "scientific" or domain keyword | `gh repo list {org} --json name,description` → grep |
| GH-2 | No blank descriptions on public repos | Same command, filter empty |
| GH-3 | Org websites point to primals.eco (not GitHub) | GitHub web UI check |
| GH-4 | Org bios lead with "scientific" framing | GitHub web UI check |
| GH-5 | ecoPrimal profile: no real name, no location, no institution | `gh api users/ecoPrimal` |
| GH-6 | No personal GitHub user in org memberships | `gh api orgs/{org}/members` |

### Live Site Surface

| ID | Check | Command / Method |
|----|-------|-----------------|
| LS-1 | All section indexes return 200 | `curl -sI https://primals.eco/{section}/` |
| LS-2 | Contact page institutional links resolve (no 404) | Manual click-through |
| LS-3 | identity.json valid JSON-LD | `curl -s https://primals.eco/identity.json \| python3 -m json.tool` |
| LS-4 | .well-known/aspe returns ASPE fingerprint | `curl -s https://primals.eco/.well-known/aspe` |
| LS-5 | All subdomains with DNS resolve over HTTPS | `curl -sI https://{sub}.primals.eco` |
| LS-6 | Security headers present (HSTS, CSP, X-Frame-Options) | `curl -sI` → inspect headers |
| LS-7 | Primal count consistent across landing, lab, contact, glossary | Manual audit or grep |
| LS-8 | Page count in certification manifest matches config.toml | Compare `manifest.json` vs `config.toml` |

### Agent Surface

| ID | Check | Command / Method |
|----|-------|-----------------|
| AG-1 | llms.txt section counts match reality | Compare stated vs actual page counts |
| AG-2 | content-manifest.toml served at web root | `curl -sI https://primals.eco/content-manifest.toml` |
| AG-3 | sitemap.xml returns 200 and valid XML | `curl -sI https://primals.eco/sitemap.xml` |
| AG-4 | robots.txt allows all agents | `curl -s https://primals.eco/robots.txt` |
| AG-5 | site-index lists all top-level pages | Manual comparison with sitemap.xml |

### Content Quality

| ID | Check | Command / Method |
|----|-------|-----------------|
| CQ-1 | No scaffold-maturity pages in top-level nav | Check maturity field in front matter |
| CQ-2 | Outreach pages either substantive or clearly labeled | Audit outreach/ front matter |
| CQ-3 | No hardcoded numbers that should use total_stat | `grep -r "175\|13 primal\|14,314" content/` |
| CQ-4 | Landing page naming clarification present | Check _index.md for ecosystem/site/domain explanation |
| CQ-5 | Try-it commands point to reachable resources | Manual test of clone + cargo test path |

---

## Audit Cadence

- **On every content deploy**: Run LS-1, LS-5, AG-2, LS-8 (automated — add to membrane content.rebuild)
- **Weekly**: Full GitHub surface audit (GH-1 through GH-6)
- **On content changes**: Run CQ-1 through CQ-5
- **On identity changes**: Full checklist

---

## Remediation Log

### Wave 139a (2026-07-14)

**GitHub Surface**:
- APPLIED: SIGNAL_SHARPENING repo descriptions to all ecoPrimals, sporeGarden, protoKarya repos
- REMAINING: Org bios and website URLs (requires GitHub web UI — documented in SIGNAL_SHARPENING.md)

**Site Content**:
- FIXED: Contact page projectFOUNDATION link (was 404, now points to lab validation summary)
- FIXED: Contact page primal count (was hardcoded "13", now uses total_stat shortcode)
- FIXED: Glossary NUCLEUS definition clarifies 13-on-gate vs 15-in-ecosystem distinction
- FIXED: Landing page naming clarification (ecoPrimals = ecosystem, sporePrint = site, primals.eco = domain)
- FIXED: Landing page guideStone tarball reference (replaced with plasmidBin getting-started link)
- FIXED: Certification manifest page count (271 → 304)

**Agent Surface**:
- FIXED: llms.txt outreach page count (11 → 14)
- FIXED: llms.txt story description (removed hardcoded "175+")
- FIXED: content-manifest.toml copied to static/ for web serving

**Infrastructure**:
- IDENTIFIED: footprint.primals.eco TLS broken (needs Caddy SNI/cert fix on golgi)

---

## Cross-References

- `whitePaper/gen5/thesis/SHOW_HN_PUBLICATION.md` — **internal rigor checklist only** (quality bar, not engagement target). HN is a Y Combinator property; the rubric tests "would hostile experts find cracks?" without coupling to the platform.
- `whitePaper/attsi/non-anon/SIGNAL_SHARPENING.md` — GitHub-specific presence audit (Phase 1 EXECUTED Wave 139a)
- `whitePaper/gen5/foundations/IDENTITY_ANCHORING_PATTERN.md` — identity architecture (dual-voice, cryptographic anchoring)
- `wateringHole/GLACIAL_SHIFT_READINESS.md` — criterion 8 (outer membrane hardened for public exposure)
