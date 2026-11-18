# sporePrint AAR — SEO Search Doors & Visibility Tuning

**Date**: Jul 26, 2026 | **Wave**: 151b | **Gate**: eastGate
**Scope**: sporePrint site SEO, content quality, outreach magnetization
**Commits**: 7 | **Files changed**: 192

---

## Mission

Respond to external SEO review identifying that ecoPrimals evidence was
spread across custom vocabulary and invisible to unbranded search queries
like "GPU-accelerated DADA2," "WGSL f64 scientific computing," and "lattice
QCD on consumer GPUs." Create discoverable "search doors" that searchers
can find without knowing ecoPrimals terminology.

---

## What Was Done

### 1. Search Door Pages (8 titles rewritten)

Rewrote page titles and H1s to lead with the search query, brand second:

| Old title | New title |
|-----------|-----------|
| Python vs Rust vs GPU — Performance Evidence | GPU-Accelerated DADA2 Benchmark: Rust vs Python |
| wetSpring Validation Results | Self-Hosted GPU-Accelerated 16S Bioinformatics |
| Sovereign GPU Pipeline | Cross-Vendor f64 Scientific GPU Computing in Rust and WGSL |
| Sovereign Lattice QCD | Lattice QCD on Consumer GPUs Without CUDA |
| Gate Mesh — Live Topology | Self-Hosted Distributed Scientific Compute Mesh |
| guideStone | Reproducible, Self-Verifying Scientific Software |
| 16S Pipeline Validation — wetSpring | Self-Hosted GPU-Accelerated 16S Pipeline |
| wetSpring — Life Science | GPU-Accelerated 16S Bioinformatics Without Galaxy or CUDA |

### 2. Reproduce It / Limitations Sections

Added structured sections to 4 key pages (DADA2 benchmark, lattice QCD,
GPU pipeline profile, mesh topology) with:
- Hardware used, dataset, date, author/ORCID
- One command to reproduce
- Honest limitations

### 3. Outreach Magnetization

- **Human-response signal**: "A human reads and responds to every message"
  added to 9 outreach pages (Valve, 99PI, GPU, gaming, neuromorphic,
  homelab, consulting, faculty PIs, contact)
- **Karpathy invitation**: New page — AI-assisted development at scale as
  existence proof (K-NOME methodology, 3.5M LOC, zero human-written code)
- **GPU manufacturer brief**: Expanded from 3-line scaffold to full page
  with shader domain table, tested hardware, concrete asks
- **Valve and 99PI/Radiolab**: Promoted from scaffold to live status

### 4. Notebook SEO Descriptions

All 96 auto-generated "Rendered from *.ipynb" descriptions replaced with
search-friendly summaries. Zero remaining auto-generated descriptions.

### 5. Canonical URL Consolidation

All static files (llms.txt, llms-science.txt, llms-products.txt,
llms-atlas.txt, llms-docs.txt, identity.json, robots.txt) and human-written
content pages now use `sporeprint.primals.eco` consistently. 105+ URL
updates across static files, 13 content pages fixed.

### 6. Structural Fixes

- 9 broken companion URLs fixed (uppercase paths → kebab-case slugs)
- Hardcoded LOC/test/page counts replaced with `total_stat()` shortcodes
- Meta keywords updated to unbranded search terms
- CITATION.cff added (GitHub "Cite this repository")
- Homepage restructured with "Key evidence pages" linking to search doors
- Internal cross-links: Mobility Edge → DADA2 benchmark, parity brief → DADA2

### 7. Email Transition Prep

`config.toml` annotated for `eco.primal@primal.eco` transition. 8 outreach
pages now have inline `mailto:` links — single-line change when mail goes live.

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Pages | 312 | 313 (+1 Karpathy invitation) |
| Auto-gen notebook descriptions | 96 | 0 |
| Broken companion URLs | 9 | 0 |
| Hardcoded ecosystem stats in content | 12+ | 0 |
| Stale primals.eco URLs in static files | 105+ | 0 |
| Outreach pages with human-response signal | 0 | 9 |
| Search door pages with reproduce/limitations | 0 | 4 |
| spore-validate errors | 0 | 0 |
| spore-validate warnings | 2 | 2 (pre-existing) |

---

## What Was NOT Done (Upstream / User Tasks)

### User Tasks (require human action)

1. **JOSS submission** — Prepare a focused submission for barraCuda or
   wetSpring. JOSS evaluates need, state of field, tests, reproducible
   examples. wetSpring or barraCuda are the strongest candidates.

2. **Search Console setup** — Register `sporeprint.primals.eco` in Google
   Search Console. Set up unbranded query filter excluding ecoPrimals,
   primals, sporePrint, wetSpring, barraCuda. Track unbranded impressions
   by landing page.

3. **crates.io releases** — Publish versioned releases of barraCuda and
   wetSpring crates. This creates external citation paths.

4. **Scientific Computing in Rust Monthly** — Submit a focused piece on
   WGSL f64 scientific compute or GPU-accelerated DADA2.

5. **Independent reproduction** — Seek one external benchmark of the
   DADA2 GPU pipeline. A credible outside result is worth more than
   additional self-authored pages.

6. **DADA2 community engagement** — Contribute a transparent,
   affiliation-disclosed answer to existing DADA2 GPU implementation
   requests, linking to reproducible evidence.

7. **eco.primal@primal.eco activation** — When primal.eco mail goes live,
   update `config.toml` email field and the 8 inline `mailto:` links.

### Upstream Team Tasks

8. **barraCuda team** — Add CITATION.cff to barraCuda repo with ORCID
   and GPU-focused keywords. GitHub renders citation information directly.

9. **wetSpring team** — Add CITATION.cff to wetSpring repo. Keywords
   should include "DADA2," "16S pipeline," "GPU bioinformatics."

10. **All spring teams** — Consider adding "Reproduce It" sections to
    spring READMEs with one-command validation (`cargo test --workspace`).

11. **biomeOS team** — Notebook body URLs still reference `primals.eco/`
    (auto-generated). Next `render-notebooks` run should use the canonical
    `sporeprint.primals.eco` base URL.

### Caddy / Infrastructure

12. **Caddy redirect** — Verify that `primals.eco` 301-redirects to
    `sporeprint.primals.eco` for all paths. If not already configured,
    this is the single most important SEO infrastructure change.

---

## Key Insight

The site had strong evidence but weak discoverability. The vocabulary was
internal (primal names, spring names, sovereign terminology). Searchers
don't know "barraCuda" — they search "GPU-accelerated DADA2." The search
door pattern puts the query first and the vocabulary second, creating
resonance between what searchers type and what the site says.

The reviewer's recommended "query ladder" — start with narrow, proven
claims where competition is weak (DADA2 GPU, lattice QCD consumer GPU),
then climb toward broader terms (scientific computing without CUDA,
self-hosted bioinformatics) as authority builds.

---

*sporePrint team — eastGate. Wave 151b.*
