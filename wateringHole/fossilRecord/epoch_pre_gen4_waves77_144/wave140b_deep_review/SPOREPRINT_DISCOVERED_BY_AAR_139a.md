# AAR — sporePrint DISCOVERED_BY Audit & Signal Sharpening (Wave 139a)

**Date**: 2026-07-14
**Team**: sporePrint (fireWatch to upstream overwatch)
**Wave**: 139a
**Gate**: eastGate → golgi (deploy pending)

---

## Summary

Conducted a full passive-discovery audit of the ecoPrimals external membrane — what happens when someone (AI bot, PI, homelabber, journalist, agent) stumbles onto us without context. Inverted the SHOW_HN active-presentation model to a DISCOVERED_BY passive-scrutiny standard. HN is Y Combinator — the engagement model now aligns with sovereign and commons surfaces only.

---

## What Was Done

### GitHub Signal Sharpening (COMPLETE)

**All 26 public repo descriptions** updated with science-framed language:
- 17 ecoPrimals repos (toadStool, coralReef, bearDog, songBird, nestGate, biomeOS, squirrel, loamSpine, barraCuda, rhizoCrypt, sweetGrass, petalTongue, sourDough, skunkBat, bingoCube, sporePrint, plasmidBin)
- 8 sporeGarden repos (lithoSpore, projectNUCLEUS, projectFOUNDATION, cellMembrane, metalForge, initioChem, helixVision, blueFish)
- 1 protoKarya repo (tideGlass)

**All 4 org profiles** updated via `gh api -X PATCH /orgs/`:
- ecoPrimals: "Scientific computing infrastructure — composable Pure Rust services..."
- syntheticChemistry: Updated check count (12,510+ → 20,695+), website → primals.eco
- sporeGarden: "Deployable scientific artifacts and creative products..."
- protoKarya: "External science compositions — field tools and collaborator-facing products..."
- All org emails cleared, locations cleared, websites → primals.eco

**ecoPrimal user profile** updated via `gh api -X PATCH /user`:
- Bio: "a tool that shapes itself" (attsi easter egg, no personal identity)
- Website: primals.eco
- Location, name, company: blank

### sporePrint Site Fixes

- **Contact page**: Fixed projectFOUNDATION 404 (→ `/lab/projectfoundation-validation-summary/`)
- **Contact page**: Replaced hardcoded "13-primal" with `total_stat` shortcode
- **Landing page**: Added naming clarification ("ecoPrimals is the ecosystem. sporePrint is this site. primals.eco is where you're reading it.")
- **Landing page**: Fixed guideStone tarball dead-end (→ plasmidBin getting-started link)
- **Glossary**: Clarified NUCLEUS 13-gate vs 15-ecosystem primal count distinction
- **Certification manifest**: Updated page count 271 → 304, date refreshed
- **llms.txt**: Updated outreach page count (11 → 14), removed hardcoded "175+" from story description
- **content-manifest.toml**: Copied to `static/` so it's served at web root

### Documentation

- **DISCOVERED_BY_STANDARD.md** created in wateringHole — passive discovery audit checklist with 6 personas, surface audit matrix, and remediation log
- **SIGNAL_SHARPENING.md** updated in whitePaper — all repo descriptions and org profiles marked DONE with execution tables
- **Engagement topology pivot**: SHOW_HN retained as internal rigor checklist only. HN explicitly identified as Y Combinator property, removed as engagement front. Engagement surfaces mapped to sovereign/commons only (primals.eco, ORCID, Zenodo, Keyoxide, crates.io, Forgejo, Reddit, Medium).

---

## Key Decisions

1. **DISCOVERED_BY supersedes SHOW_HN as engagement doctrine.** HN is part of Y Combinator's extractive flywheel. The HN rigor checklist survives as an internal quality bar ("would hostile experts find cracks?") without coupling to the platform.

2. **13 vs 15 primal count is both correct.** 15 = full ecosystem. 13 = typical NUCLEUS gate deployment. The glossary now explains this. Pages referencing NUCLEUS deployment say 13; pages referencing the ecosystem say 15.

3. **Org emails cleared.** Reduces scraper spam. Contact flows through primals.eco/contact/ or eco.primal@pm.me.

---

## Remaining (not sporePrint team scope)

| Item | Owner | Notes |
|------|-------|-------|
| footprint.primals.eco TLS broken | cellMembrane / golgi | HTTPS handshake fails after 308 redirect. Caddy SNI/cert fix needed. |
| rustChip description | ecoPrimal | Repo is archived (read-only). Low priority. |
| Populate ORCID profile | human | Bio, keywords, websites — manual via orcid.org |
| First Zenodo DOI | human + sporePrint | Create GitHub Release → Zenodo webhook |
| cargo publish spore-validate | human | `cargo login` done, `cargo publish` ready |
| Medium account for attsi | human | First essay republish |

---

## Metrics

- Repos updated: 26 descriptions + 4 org profiles + 1 user profile = **31 GitHub surface changes**
- Site files modified: 6 content files + 3 static assets = **9 sporePrint changes**
- New wateringHole docs: 1 (DISCOVERED_BY_STANDARD.md)
- Findings identified: 18 (6 high, 7 medium, 5 low)
- Findings fixed this wave: 12

---

*sporePrint fireWatch, Wave 139a. External membrane surface hardened for passive discovery. GitHub signal sharpened. Engagement model pivoted from extractive platform presentation to sovereign commons discovery.*
