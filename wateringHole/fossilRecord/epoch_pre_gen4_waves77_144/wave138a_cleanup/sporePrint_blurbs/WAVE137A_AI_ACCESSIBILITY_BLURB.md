# sporePrint — Wave 137a Blurb: AI Accessibility Evolution

**Date**: July 11, 2026 | **Wave**: 137a | **From**: sporePrint team

## Summary

All navigational tables across the site converted to ordered/unordered lists.
JSON-LD `hasPart` added to every section with child pages. External AI agent
(Claude via `web_fetch`) confirmed that markdown-rendered `<table>` elements
strip links in fetch-to-text extraction, making essay URLs invisible to AI
agents working on behalf of users. This is treated as an accessibility bug,
not a crawler issue.

## Changes

### Content Structure (9 section `_index.md` files)

23 navigational tables converted to lists:

| Section | Entries |
|---------|---------|
| architecture | 16 |
| audience | 5 |
| lab | 21 (6 springs + 15 notebooks) |
| methodology | 9 |
| outreach | 11 (3+5+3) |
| science | 28 across 6 domains |
| story | 6 (3 stories + 3 philosophy pairings) |
| technical | 6 |
| thesis | 20 (16 chapters + 4 back matter) |

Data-only tables (outreach Two Voices, Community) preserved — they contain no links.

### Structured Data (JSON-LD)

- `templates/section.html`: Generic `CollectionPage` `hasPart` fallback for
  all sections not already covered by specific blocks (philosophy, thesis, story)
- `templates/science_section.html`: `CollectionPage` with `ScholarlyArticle`
  `hasPart` (33 articles)
- Result: 12 sections now emit `hasPart` arrays in JSON-LD — machine-readable
  child-page discovery regardless of HTML rendering

### Deployment

- Committed as `ddf8138`, dual-pushed to GitHub + Forgejo
- Cascaded to golgi: pulled, rebuilt, verified live
- All 9 section indexes: 0 tables with links, `hasPart` confirmed

## Quality Gates

- `zola build`: 271 pages, 0 orphan, 17 sections
- `cargo test`: 284 tests, 0 failures
- Sitemap: 314 entries
- Tables with links remaining: 0

## Context

This resolves the AI accessibility divergence identified in Wave 136b
(`AI_ACCESSIBILITY_DIVERGENCE_STUDY_136b.md`). The root cause was that
fetch-to-text tools used by AI agents (Claude `web_fetch`, similar) strip
links from HTML `<table>` elements during text extraction. Lists (`<ol>`,
`<ul>`) survive this extraction universally.

The `hasPart` JSON-LD provides a second discovery channel: AI agents can
parse structured data directly without relying on HTML rendering at all.

## Upstream Gaps

- **TOPO-VIS** (Phase 2): sporePrint live K-Derm topology viz needs wiring
  to nestGate data + songBird heartbeats (petalTongue `coord_handlers.rs`
  landed at `225e30f`)
- **Pa11y CI integration**: Automated WCAG rule checking not yet in pipeline
- **Screen reader testing**: Manual testing with Orca/NVDA/VoiceOver remains
  evolution target
