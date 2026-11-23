# sporePrint AAR — Query Routing & Sidebar Compression (Wave 151c)

**Date**: 2026-07-26 | **Wave**: 151c | **Gate**: eastGate
**Scope**: sporePrint site structure — title templates, sidebar, canonical consolidation

---

## Mission

Address external review feedback that the site was winning "self-hosted
scientific computing" queries but Google couldn't determine *which page*
owns each sub-query. Every page competed for the same phrase due to
a shared title suffix. Sidebar also rendered full page listings on
large sections, inflating HTML weight.

---

## Actions Taken

### 1. Title template specialization (6 files)

**Before**: `Page Title — ecoPrimals — Self-Hosted Scientific Computing in Rust`
**After**: `Page Title | ecoPrimals`

Only the homepage retains the full keyword-rich title. Every other page
now has a short brand suffix (`| ecoPrimals`) so each page's own title
carries its search contract without competing against every other page
for the same phrase.

Files changed: `page.html`, `section.html`, `science_section.html`

### 2. Sidebar compression (templates/base.html, sass/_layout.scss)

- Sections with 40+ pages (lab = 130+) no longer list individual pages — only subsections with counts
- Subsection pages expand only when you're IN that subsection
- Page counts shown in parentheses: `Public Notebooks (98)`
- Inactive folds remain collapsed to section index links only

Effect: wetSpring page dropped from ~185 lines to 126 lines. The sidebar
is now contextual navigation, not a full site map.

### 3. Canonical author URLs in JSON-LD

Updated `author.url` from `https://primals.eco` to
`https://sporeprint.primals.eco` in `page.html`, `section.html`,
`science_section.html`.

### 4. Evidence drift resolution

Evidence Snapshot was already fully shortcoded (no hardcoded numbers).
Fixed last hardcoded "307 pages" in `acknowledgments.md` → `total_stat`
shortcode.

### 5. Caddy redirect confirmed

sporeGate topology team confirmed: `primals.eco → sporeprint.primals.eco`
301 permanent redirect has been live since Wave 150d, path-preserving,
with security headers. No action needed.

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Page title suffix length | ~55 chars | ~14 chars |
| Pages competing for "Self-Hosted Scientific Computing" | 313 | 1 (homepage) |
| wetSpring rendered HTML lines | ~185 | 126 |
| Hardcoded counts remaining | 1 | 0 |
| Canonical URL mismatches | 2 (JSON-LD author) | 0 |
| spore-validate errors | 0 | 0 |

---

## Divergences Found

1. **Google indexing both hosts**: Despite 301 redirects being live for
   weeks, Google still shows both `primals.eco` and `sporeprint.primals.eco`
   in results. This is a crawl-cycle lag, not a configuration issue.

2. **4 lab validation summaries missing weight**: `healthspring-`,
   `biomeos-`, `groundspring-`, `airspring-validation-summary.md` are
   in a sorted section without `weight` frontmatter. Not blocking but
   generates Zola warnings. Low priority.

3. **rustchip entity in registry but no content page tags it**: New spring
   added to config.toml entity registry but no content page references it
   yet. Needs a spring hub page when rustChip has public content.

---

## User Tasks (for overwatch compilation)

| Task | Priority | Status |
|------|----------|--------|
| Google Search Console: verify `primals.eco` ownership, request re-crawl | P1 | NOT STARTED |
| JOSS submission (barraCuda or wetSpring) | P2 | NOT STARTED |
| crates.io releases (focused, versioned) | P2 | NOT STARTED |
| Scientific Computing in Rust Monthly submission | P3 | NOT STARTED |
| Independent reproduction seek (DADA2 wedge) | P3 | NOT STARTED |
| DADA2 community engagement (affiliation-disclosed) | P3 | NOT STARTED |
| `eco.primal@primal.eco` activation | P3 | BLOCKED (infra) |

## Upstream Team Tasks

| Task | Team | Priority |
|------|------|----------|
| CITATION.cff in barraCuda repo | barraCuda | P2 |
| CITATION.cff in wetSpring repo | wetSpring | P2 |
| render-notebooks: use sporeprint.primals.eco canonical URL | biomeOS | P3 |
| "Reproduce It" sections in spring READMEs | All springs | P3 |
| rustChip spring hub page content | rustChip | P3 |
| Weight frontmatter for 4 lab validation summaries | sporePrint | P3 |

---

*Wave 151c: query routing shipped. 313 pages, each with its own search
contract. Sidebar compressed to contextual navigation. Canonical identity
fully consolidated across all layers (Caddy, Zola, JSON-LD, sitemap,
robots.txt). 0 errors.*
