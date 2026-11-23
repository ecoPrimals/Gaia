# sporePrint Evolution Roadmap: Zola → petalTongue

**Version**: 0.1.0
**Date**: May 2026
**Audience**: petalTongue primal team
**Status**: Guidance — not yet actionable until Phase 1 contracts are stable

---

## Current State

sporePrint (primals.eco) is the public-facing website for ecoPrimals. It is
currently built with **Zola** (static site generator) and deployed to GitHub
Pages via a CI pipeline:

```
spore-validate --check → zola check → zola build → deploy-pages
```

petalTongue is the Universal User Interface primal (v1.6.6, 18 crates). It
has a `web` mode (Axum + SSE) that serves a full API dashboard with SPA
support, notebook rendering, and CORS, and a `petal-tongue-wasm` crate
with 14 browser-side rendering exports (grammar, binding, dashboard, batch,
scene graph, Tufte validation, threshold coloring, multi-modality).

The **Gonzales interactive explorer** (`static/gonzales/explorer.js`) already
uses petalTongue as an optional server-side chart renderer — the hybrid
pattern (Zola static + petalTongue dynamic) has a working precedent.

This document describes what petalTongue needs to implement to progressively
replace Zola as the sporePrint renderer.

---

## What Zola Currently Provides

### Content Model

- **72 markdown files** with TOML front matter under `content/`
- **Section semantics** via `_index.md` files (10 sections)
- **Permalinks** derived from directory structure and file names
- **Taxonomies**: `primals` and `springs` — auto-generated index pages at
  `/primals/` and `/springs/`, with per-term pages at `/primals/{key}/`
  and `/springs/{key}/`

### Entity Registry (the central data contract)

`config.toml` contains `[extra.entity_registry]` — a keyed map of ~50
entities with:

```toml
[extra.entity_registry.beardog]
display = "BearDog"
emoji = "🐻🐕"
kind = "primal"          # primal | spring | product | composition | concept | infra | org
description = "..."
loc = 142621
loc_display = "142,621"
tests = 5041
tests_display = "5,041"
files = 234
crates = 14
repo = "https://github.com/ecoPrimals/bearDog"
tier = "Foundation"
domain = "Cryptography and Identity"
composes = [...]
capabilities = [...]
```

**Key normalization**: taxonomy templates use `term.name | lower | replace(from=" ", to="")`.
Shortcodes additionally strip hyphens. Any replacement must preserve this
normalization or URLs will break.

### Four Shortcodes

| Shortcode | What it does |
|-----------|-------------|
| `entity(name="beardog")` | Renders a styled link to `/primals/beardog/` (for primals/springs) or inline span (for concepts) |
| `entity_metrics(name="beardog")` | One-line LOC/files/crates/tests from registry |
| `entity_stat(name="beardog", stat="loc_display")` | Single metric field |
| `total_stat(stat="total_loc_display")` | Lookup in `config.extra.totals` |

### Templates (Tera)

- `base.html` — shell, nav, sidebar tree, search, footer
- `index.html` — homepage with stats ribbon, audience cards, org cards
- `section.html` / `page.html` — standard content rendering
- `science_section.html` — science-specific section template
- `taxonomy_single.html` — per-term page (e.g. `/primals/beardog/`)
- `taxonomy_list.html` — taxonomy index (e.g. `/primals/`)

### CI Contracts

1. **`spore-validate --check`** — Rust binary that validates:
   - Entity registry schema/consistency per kind
   - Totals match summed registry
   - Content taxonomy tags match registry keys
   - Shortcode usage in markdown matches registry entries
2. **`zola check`** — link integrity validation
3. **Build search index** — elasticlunr JSON for client-side search
4. **Atom feed** — `atom.xml`

### Static Assets

- `css/main.css` — Catppuccin-ish design system, CSS variables, no external fonts
- `gonzales/` — interactive science explorer (Plotly, JSON datasets, optional petalTongue render)
- `img/` — OG card SVG
- System font stack (no CDN dependencies)

---

## URL Contracts (Must Not Break)

These URLs are linked from external sites, search engines, outreach documents,
and README files across the ecosystem:

| Pattern | Example | Source |
|---------|---------|--------|
| `/primals/{key}/` | `/primals/beardog/` | Taxonomy |
| `/springs/{key}/` | `/springs/hotspring/` | Taxonomy |
| `/science/{slug}/` | `/science/02-ltee-extensions/` | Content |
| `/architecture/{slug}/` | `/architecture/primal-catalog/` | Content |
| `/products/{slug}/` | `/products/helixvision/` | Content |
| `/glossary/` | `/glossary/` | Content (new) |
| `/atom.xml` | Feed | Config |

Any migration must preserve these or provide HTTP redirects.

---

## Progressive Migration Path

### Phase 0: Current (Zola + Gonzales hybrid)

Zola renders static pages. Gonzales explorer optionally calls petalTongue
for server-side chart rendering. No changes needed.

### Phase 1: petalTongue as API backend for interactive pages

Extend `petaltongue web` mode to serve:
- Entity registry data via JSON API (`/api/entities`, `/api/entity/{key}`)
- Totals and metrics via JSON API (`/api/totals`)
- Grammar-rendered visualizations (ecosystem graphs, primal relationships)

Zola continues to render all static content. New interactive pages (beyond
Gonzales) can call petalTongue APIs from client-side JavaScript.

**Contract**: petalTongue must consume `config.toml`'s `[extra.entity_registry]`
and `[extra.totals]` shapes. Parse the same TOML, expose via API.

### Phase 2: petalTongue renders taxonomy pages

Replace Zola's taxonomy rendering with petalTongue-served pages at
`/primals/{key}/` and `/springs/{key}/`. These are the most dynamic pages
(entity profiles, metrics, capabilities, cross-references).

**Requirements**:
- Parse `config.toml` entity registry
- Match Zola's key normalization (`lower | replace spaces`)
- Render entity profiles (description, metrics, capabilities, composed systems)
- List all pages that tag each taxonomy term (requires content index)
- Preserve URL structure exactly

### Phase 3: petalTongue renders content pages

Replace Zola's markdown rendering with petalTongue-served pages for
`content/` markdown files.

**Requirements**:
- Parse markdown with TOML front matter
- Implement section semantics (`_index.md` hierarchy)
- Implement shortcode equivalents (4 shortcodes → petalTongue components)
- Generate sidebar navigation tree (equivalent to `base.html` tree)
- Syntax highlighting for code blocks
- Table of contents generation

### Phase 4: petalTongue as full site renderer

Remove Zola from the pipeline entirely. petalTongue serves all pages.

**Requirements**:
- Search index (replace elasticlunr or use petalTongue's own search API)
- Atom feed generation
- Sitemap
- Link validation (replace `zola check`)
- Static asset serving (CSS, JS, images)
- Meta tags (OG, Twitter cards, JSON-LD)

---

## WASM Path (WS-4 — Evolved May 2026)

`petal-tongue-wasm` provides near server-parity client-side rendering
(14 `#[wasm_bindgen]` exports, 30 tests, CI `wasm32-unknown-unknown` check):

| Export | Purpose |
|--------|---------|
| `render_grammar` / `render_grammar_to_modality` | Grammar expression → SVG/description/terminal |
| `render_binding` / `render_binding_to_modality` | DataBinding → any modality |
| `render_binding_with_thresholds` | Status-colored heatmaps/fieldmaps |
| `render_bindings` | Batch render → JSON array of `{id, label, svg}` |
| `render_dashboard` | Multi-panel dashboard grid (configurable layout) |
| `compile_scene` / `render_scene` / `render_scene_to_modality` | SceneGraph JSON round-trip |
| `validate_grammar` | Tufte constraint evaluation (7 constraints) → report JSON |
| `version` / `init` | Meta + `console_error_panic_hook` browser traces |

**Remaining integration steps**:
1. Place the WASM bundle in `web/static/` (or serve from sporePrint CDN)
2. Extend explorer SPA to load the WASM module for offline rendering
3. Replace Plotly.js toggle with `petal-tongue-wasm` toggle

This can happen independently of the Zola migration — WASM bundles can
be included as static assets in the Zola build.

---

## spore-validate Continuity

`spore-validate` is a Rust binary that validates content integrity. It must
continue to work throughout the migration:

- **Phase 1-2**: No changes needed. Zola still renders most pages.
- **Phase 3**: `spore-validate` needs to validate against petalTongue's
  shortcode equivalents (or petalTongue must accept the same shortcode
  syntax as Zola)
- **Phase 4**: `spore-validate --check` replaces `zola check` for link
  validation. The `validate` subcommand continues as-is (registry-focused).

---

## Design System Continuity

`css/main.css` defines the visual language. Key constraints:

- **CSS variables** for theming (light/dark via `prefers-color-scheme`)
- **No external fonts or CDNs** — system font stack
- **Entity-specific CSS classes** (`.entity-ref`, `.entity-profile`,
  `.cap-table`, `.entity-composes`) must be preserved or replaced with
  equivalent petalTongue component styling
- **Responsive breakpoint** at 960px (sidebar collapses)

petalTongue should either consume the same CSS or provide a compatible
design system that preserves the visual identity.

---

## What NOT to Do

1. **Don't break URLs.** External links, search engine indexes, and outreach
   documents reference sporePrint pages. Any URL change requires redirects.
2. **Don't fork the entity registry.** One source of truth: `config.toml`.
   petalTongue consumes it; it doesn't maintain a parallel registry.
3. **Don't rewrite content.** Markdown files in `content/` are the
   authoritative source. petalTongue renders them; it doesn't replace them.
4. **Don't remove spore-validate.** The validation gate is a quality
   contract, not a Zola dependency.
5. **Don't deploy petalTongue web mode to production before Phase 2 is
   complete.** The current `web/index.html` is a dev dashboard, not a
   public site.
