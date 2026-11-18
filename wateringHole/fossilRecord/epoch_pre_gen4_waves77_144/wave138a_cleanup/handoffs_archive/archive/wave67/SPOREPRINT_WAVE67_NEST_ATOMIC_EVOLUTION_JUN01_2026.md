# sporePrint Wave 67 — Nest Atomic / Pure-Primal Evolution

**Date:** June 1, 2026
**Author:** Agent (Wave 67 implementation)
**Status:** Implementation complete, deployment pending

---

## Summary

Evolved sporePrint from a Zola-only static site to a hybrid architecture where:
- **Zola** remains as the validation oracle and current production renderer
- **petalTongue** gains full document content rendering capability (Universal User Interface)
- **Nest Atomic** composition orchestrates storage, rendering, and provenance
- **primalSpring** validates parity between Zola output and petalTongue output

This is the foundational infrastructure for the pure-primal rendering path.

---

## Deliverables

### 1. petalTongue — Content Scene Graph (`petal-tongue-scene`)

**File:** `crates/petal-tongue-scene/src/document.rs`

New types for document content as a parallel scene graph to the Grammar of Graphics:

- `DocumentNode` enum — Page, Heading, Paragraph, CodeBlock, BlockQuote, List, Table, ThematicBreak, EntityReference, EntityMetrics, NavTree, RawHtml
- `PageMeta` — TOML front-matter metadata (title, description, taxonomies, extras)
- `Inline` — Text, Bold, Italic, Code, Link, Entity, LineBreak
- `EntityRef` — resolved entity with key, display, emoji, href, description
- `SiteContent` — full site model for startup loading
- `EntityRegistryEntry` — mirrors sporePrint config.toml schema

4 unit tests, `toml` workspace dep added.

### 2. petalTongue — Content Rendering Pipeline

**File:** `src/content_render.rs`

Full pipeline from raw markdown to typed document tree:

- `split_front_matter()` — `+++` delimiter handling
- `parse_front_matter()` — TOML table to `PageMeta`
- `compile_markdown()` — pulldown-cmark events to `DocumentNode` tree
- `resolve_shortcodes()` — `{{ entity(name="...") }}` expansion against registry
- `parse_document()` — complete entry point for a single page

8 unit tests.

### 3. petalTongue — Document Modality Compilers

**File:** `crates/petal-tongue-scene/src/modality/document_compiler.rs`

DocumentNode to ModalityOutput compilation:

- `compile_to_html()` — semantic HTML with entity links, code highlighting classes, nav trees, accessibility attributes
- `compile_to_description()` — structured text for screen readers (indented, labeled sections)

5 unit tests.

### 4. petalTongue — Web Content Route

**File:** `src/web_mode/content_backend.rs`

Enhanced `content_fallback()` handler:

- Accept header negotiation (`text/html`, `text/plain`, `application/json`)
- Query parameter override (`?modality=description`, `?modality=json`)
- Markdown detection (`.md` extension or `text/markdown` MIME)
- Automatic routing through DocumentNode pipeline

### 5. projectNUCLEUS — Deploy Graph

**File:** `graphs/sporeprint_composition.toml`

Nest Atomic composition for sporePrint:

- Includes `nest_atomic` fragment (beardog + songbird + skunkbat + nestgate + rhizocrypt + loamspine + sweetgrass)
- petalTongue node: `web --backend content-provider --port 8080`
- spore-validate node: `certify --emit` (run_once)
- Deployment hints: Caddy reverse-proxy, primals.eco domain, publish pipeline

### 6. primalSpring — Validation Scenario

**File:** `ecoPrimal/src/validation/scenarios/s_sporeprint_pure_primal.rs`

5-phase validation (Tier::Rust):

1. **Content Parsing** — front-matter validity, entity registry presence
2. **Entity Resolution** — registry coverage (50+ entities), shortcode resolution rate (>= 90%)
3. **Modality Output** — structural feasibility (headings + body)
4. **Composition Graph** — deploy graph completeness (nest_atomic, petaltongue, capabilities)
5. **Certification** — deploy.yml certify step, manifest.json presence, merkle_root field

Registered in `build_registry()` (58 scenarios total).

---

## Metrics

| Metric | Value |
|--------|-------|
| New files created | 5 |
| New tests added | 17 (4 + 8 + 5 in petalTongue) |
| primalSpring scenarios | 58 (was 57) |
| projectNUCLEUS graphs | 14 (was 13) |

---

## Architecture Diagram

```
sporePrint content/ + config.toml
    → content.put → NestGate (BLAKE3 CAS)
    → content.resolve → petalTongue
    → DocumentNode tree
    → ModalityCompiler dispatch:
        - HTML (sighted users)
        - Description (screen readers)
        - Braille (tactile displays)
        - Audio (spoken navigation)

Zola remains as validation oracle:
    spore-validate certify → compare manifest
    primalSpring scenario → structural parity check
```

---

## Upstream Review Requests

### For petalTongue team:
- Review `document.rs` types — are they complete for your scene graph?
- Review `content_render.rs` — any pulldown-cmark patterns you'd change?
- Confirm `compile_to_html` output structure meets your web mode expectations

### For projectNUCLEUS team:
- Review `sporeprint_composition.toml` — does `includes = ["nest_atomic"]` reference correctly?
- Confirm `run_once = true` semantics for the spore-validate node

### For primalSpring team:
- Review scenario: is `Tier::Rust` appropriate (all checks are structural)?
- Note: `routing-consistency` scenario has 6 pre-existing failures (unrelated to this work)

---

## Next Steps (Wave 68+)

1. VPS deployment: run the Nest Atomic composition on golgiBody-ext
2. DNS cutover: Caddy → petalTongue:8080 for primals.eco
3. Provenance trio wiring: content.put → rhizoCrypt DAG + loamSpine ledger
4. Live comparison: Zola output vs petalTongue output (pixel/structure diff)
5. GitHub Pages becomes shadow-only (firewall until testing complete)
