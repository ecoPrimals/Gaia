# sporePrint Content Transplant — Wave 133d

**Date**: Jul 8, 2026 | **From**: eastGate overwatch | **To**: sporePrint team
**Priority**: HIGH — fills the largest content gap on primals.eco (Philosophy section is empty promises)

---

## Mission

Transplant mature essays from `whitePaper/` (private) into `sporePrint/content/` (public). These documents are ready or near-ready — they just need Zola frontmatter and minor edits.

The Philosophy section currently says "Coming: atlasHugged Essays" with a table of 6 promised topics. We're delivering those essays now.

---

## Phase 1: Philosophy Essays (atlasHugged → `content/philosophy/`)

Source: `infra/whitePaper/gen3/atlasHugged/`

These are standalone philosophical essays. No private contacts, no strategy, no names that need redacting. They need Zola `+++` frontmatter and weight ordering.

| Source File | Target File | Weight | sporePrint Promise It Fulfills |
|-------------|-------------|--------|-------------------------------|
| `04_THE_HUMAN_SEARCH.md` | `content/philosophy/the_human_search.md` | 10 | (companion to Constrained Evolution) |
| `06_THE_TEMPTATION_OF_KINGDOMS.md` | `content/philosophy/the_temptation_of_kingdoms.md` | 20 | "Sovereign vs Open Source" |
| `07_THE_MOBILITY_EDGE.md` | `content/philosophy/the_mobility_edge.md` | 30 | "The Mobility Edge" |
| `08_DISCOVERY_IS_LOCAL.md` | `content/philosophy/discovery_is_local.md` | 40 | "Local Discovery, Global Publication" |
| `10_I_OWN_NOTHING.md` | `content/philosophy/i_own_nothing.md` | 50 | "Attribution over Identity" / economics |
| `12_THE_KNOWLEDGE_NUMERIC.md` | `content/philosophy/the_knowledge_numeric.md` | 60 | "Knowledge Is Numeric" |

### Frontmatter template (apply to each)

```toml
+++
title = "<Essay Title from H1>"
description = "<One-sentence summary>"
date = 2026-03-17
weight = <see table>

[taxonomies]
primals = []
springs = []
+++
```

### Edit instructions (Phase 1)

- Strip any existing header metadata (if present — these are raw markdown)
- The H1 (`# Title`) becomes the `title` field in frontmatter — remove the H1 line from body
- Keep all content as-is — these are philosophy, not strategy
- Add cross-links at bottom where natural (e.g., Mobility Edge → link to K-NOME page)
- Date: use `2026-03-17` (gen3 publication date) for all

### Update `_index.md`

Replace the "Coming: atlasHugged Essays" section with actual links to the new pages. Remove the "For now, the code is the argument" deferral paragraph.

---

## Phase 2: Builder Narrative (Medium drafts → `content/story/`)

Source: `infra/whitePaper/outreach/medium/split/ecoPrimal/`

These three articles tell the builder's story. They were written for external publication (Medium) but HN is now the target channel. On sporePrint they serve as the human narrative arc — "how did one person build this?"

Create a new section: `content/story/_index.md`

| Source File | Target File | Weight |
|-------------|-------------|--------|
| `01_I_DONT_KNOW_RUST.md` | `content/story/i_dont_know_rust.md` | 10 |
| `02_THE_SOVEREIGN_LAB.md` | `content/story/the_sovereign_lab.md` | 20 |
| `03_70_PAPERS_ONE_STACK.md` | `content/story/70_papers_one_stack.md` | 30 |

### `content/story/_index.md`

```toml
+++
title = "Story"
description = "How one microbiologist built a sovereign compute ecosystem in a basement without knowing Rust."
sort_by = "weight"
template = "section.html"
+++

The builder's narrative. Three essays documenting the journey from bench
microbiologist to 14,314 validated checks in pure Rust on commodity hardware.

| Essay | What It Covers |
|-------|---------------|
| [I Don't Know Rust](@/story/i_dont_know_rust.md) | The constraint that made everything else possible |
| [The Sovereign Lab](@/story/the_sovereign_lab.md) | What sovereign means in practice — hardware, data, electricity |
| [70 Papers, One Stack](@/story/70_papers_one_stack.md) | The evidence: reproducing published science at scale |
```

### Edit instructions (Phase 2)

- Remove any lines referencing "attsi" by name (e.g., "attsi sees what I carry", "attsi has written about why this matters") — these reference the private second voice
- Replace with neutral phrasing or simply delete the sentence
- Sync check/test counts with `EVIDENCE_SNAPSHOT.md` if any numbers are stale
- Add Zola frontmatter (same template as above, date = 2026-07-08)
- Add to nav bar in `templates/base.html` (between Lab and the divider)

---

## Phase 3: Methodology Depth (gen4/knome → `content/methodology/`)

Source: `infra/whitePaper/gen4/knome/SHARING_THE_PEN.md`

| Source File | Target File |
|-------------|-------------|
| `gen4/knome/SHARING_THE_PEN.md` | `content/methodology/sharing_the_pen.md` |

### Edit instructions (Phase 3)

- Add Zola frontmatter
- This is the "methodology is the product" argument — why CC-BY-SA on methodology matters
- Cross-link from `K_NOME_PROGRAMMING.md` and `HOW_TO_START_A_SPRING.md`
- No redactions needed — this is conceptual, no private contacts

---

## Nav / Sidebar Updates

After all phases, update `templates/base.html`:

1. Add "Story" nav link (between "Lab" and the divider `<li class="nav-divider">`)
2. Add "Story" to sidebar tree (after Lab, before Philosophy)
3. Philosophy section will now have 6 child pages — ensure tree expansion works

---

## Do NOT Transplant (boundaries)

These stay private:
- `atlasHugged/` chapters 01, 03, 05, 09, 11 — defer to Phase 2 batch (editorial tone review needed)
- `THE_PROMPT_BANK.md` — internal working vocabulary
- `attsi/non-anon/contact/` — private faculty relationships
- `SHOW_HN_PUBLICATION.md` — internal launch strategy
- Any file in `gen5/collaborators/`

---

## Verification

After transplant:
- `zola build` passes
- `zola check` — new pages have no broken internal links
- Philosophy `_index.md` no longer says "Coming"
- Story section appears in nav + sidebar
- Total page count increases by ~10

---

## Success Criteria

A visitor to primals.eco/philosophy/ finds 6 real essays, not a table of contents.
A visitor to primals.eco/story/ finds the human narrative arc.
The site feels **complete** — engineering + science + philosophy + story.
