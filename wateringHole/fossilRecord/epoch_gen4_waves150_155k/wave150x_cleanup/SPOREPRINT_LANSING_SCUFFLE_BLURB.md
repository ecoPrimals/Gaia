# sporePrint Team Blurb — Lansing Scuffle & Consulting Model Content

**Wave**: 150p | **From**: eastGate overwatch
**Purpose**: Transplant the Lansing Scuffle campus vision and AGPL consulting
model into sporePrint public-facing pages.

---

## Context

The `whitePaper/lansingScuffle/` document set is mature. It describes a 3-5 year
plan to transform the John Bean Building (1305 S Cedar St, Lansing, MI — 464K SF,
1941 wartime factory, 8 MW power, currently vacant) into a solarpunk sovereign
campus: data center, wet lab, community services, and humanitarian outreach in
one building.

The economics model (`06_ECONOMICS.md`) now covers five revenue stages:

1. **Beachhead lease** — one room, $778/month
2. **Flywheel activation** — community supporters cover metabolic cost
3. **Subtenant ecosystem** — The Fledge, MSU Alliance, SmartZone, artists, manufacturers
4. **SBA 504 acquisition** — real financing math, $50K/month carrying cost
5. **Primal revenue** — contract compute (ionic bonding), grant-funded science,
   educational programs, products, and personal consulting

A key thesis — the **Lansing Shuffle Inversion** — contrasts the Scuffle with
the Lansing Shuffle entertainment venue: the Shuffle monetizes desirability
(riverfront); the Scuffle creates value from what others overlook (vacant
factory, train tracks, 8 MW power).

The **AGPL-3.0 consulting model** is also documented: the code is free for
humans forever. Revenue comes from the operator's personal expertise — deploying,
training, and maintaining the stack for companies who can't fork and close it.
LCC and community colleges get the operator free. Large companies pay market
consulting rates.

---

## Source Material (read before writing)

All source docs live in `infra/whitePaper/lansingScuffle/`:

| Document | What to extract |
|----------|----------------|
| `00_THE_SCUFFLE.md` | Vision, building facts, Shuffle/Scuffle inversion, constrained evolution |
| `01_ZONING_AND_ZONES.md` | K-Derm zone mapping for the building |
| `02_THERMAL_SOVEREIGNTY.md` | GPU heat → hot water → sand storage → rooftop gardens |
| `03_NETWORK_TOPOLOGY.md` | Building backbone + neighborhood mesh supernode |
| `04_WET_LAB_AND_GARDENS.md` | BSL-1 wet lab, rooftop agriculture, airSpring sensors |
| `05_COMMUNITY_AND_HUMANITARIAN.md` | Hot water, WiFi, warming center, sovereign identity, K-NOME |
| `06_ECONOMICS.md` | All 5 revenue stages, SBA 504 math, subtenant model, AGPL consulting, inversion crossover |
| `07_PREPOP_TIMELINE.md` | 3-5 year phased arc, Year 4-5 SBA 504 acquisition |
| `PROPERTY_PROFILE.md` | Physical facts from offering memorandum |
| `EXISTING_MODEL.md` | House topology → building topology mapping |

Also read:
- `infra/sporePrint/content/methodology/SCYBORG_LICENSING.md` — the triple license strategy
- `infra/sporePrint/content/architecture/SOVEREIGN_PRIOR_ART_CATALOG.md` — 52 innovations locked in commons
- `infra/sporePrint/content/audience/FOR_FACULTY_AND_PIS.md` — existing proprietary replacement table
- `protists/footPrint/projects/lansing-scuffle.json` — GeoJSON model of the building

---

## New Pages to Create

### 1. `content/vision/lansing_scuffle.md` — The Lansing Scuffle

Public-facing vision page. This is the "what if" page — what happens when
sovereign compute meets a 464K SF factory.

**Content to include:**
- The building: 1941 wartime factory, 464K SF, 8 MW power, 600 tons cooling,
  14'7" ceilings, rail spur, 12 acres. Currently vacant.
- The Shuffle/Scuffle inversion (keep it punchy — two paragraphs, not five)
- K-Derm zone model applied to floors (compute 3rd, science 2nd, community 1st)
- Thermal sovereignty loop: solar → compute → heat → hot water → gardens → food
- The beachhead: one room, $253/month, 400A/480V + 35-ton HVAC pre-installed
- Humanitarian anchor: hot water, WiFi, charging, warming — 24/7, no credentials
- The Fledge as sanctuary partner — the building solves the single-room problem
- Link to footPrint GeoJSON model if footPrint page exists
- Timeline: Year 0 (now, document) → Year 5 (ownership)

**Tone**: Aspirational but grounded. Numbers, not poetry. Show the building's
infrastructure specs as proof that this is not fantasy — the cannabis grow
already solved the power-density problem.

**Do NOT include**: SBA 504 loan math, detailed subtenant revenue tables, or
consulting rate cards. Those are internal planning docs. The public page shows
the vision and the entry point ($253/month), not the full financial model.

### 2. `content/outreach/consulting.md` — Sovereign Consulting

New outreach page for the consulting model. This replaces the implicit
"everything is free" with "the code is free, the expertise is available."

**Content to include:**
- The code is AGPL-3.0. Free for everyone, forever. Non-negotiable.
- What you're replacing (table from `FOR_FACULTY_AND_PIS.md` — NONMEM, Galaxy,
  Chromeleon, AlphaFold cloud, CUDA stack, etc.)
- Tiered model: humans free, education free, nonprofits free, companies pay
- What "consulting" means here: deployment, training, validation, integration —
  not ongoing license fees
- Link to `FOR_FACULTY_AND_PIS.md` for the full replacement table
- Link to `CAPABILITY_PARITY_BRIEF.md` for domain-by-domain comparison
- scyBorg triple license summary (AGPL + ORC + CC-BY-SA)

**Tone**: Direct. Not salesy. "Here's what the stack replaces. Here's what it
costs you. Here's what I charge if you need help." The page should feel like
the operator wrote it at a desk, not a marketing team in a conference room.

### 3. `content/audience/FOR_COMPANIES_AND_INSTITUTIONS.md` — For Companies

New audience page. The existing audience section has Faculty, Students, Hardware
Builders, and Compliance — but no page for companies evaluating the stack for
institutional deployment.

**Content to include:**
- AGPL-3.0 implications: what you can do (internal use, modify, deploy on own
  hardware), what triggers copyleft (distribution, SaaS), what the symbiotic
  exception is
- Proprietary stack replacement map (from `06_ECONOMICS.md` Revenue Channel 5)
- Consulting engagement model (not a subscription, not a license — a contractor)
- Air-gapped / regulated environment deployment (BSL-3/4, ITAR, 21 CFR Part 11)
- Hardware validation evidence (benchmarks, tested GPUs, tested NPUs)
- Link to `SOVEREIGN_PRIOR_ART_CATALOG.md` — 52 innovations in the commons

### 4. `content/vision/thermal_sovereignty_building.md` — Building-Scale Thermal

Public version of `02_THERMAL_SOVEREIGNTY.md`. How the thermal loop works at
464K SF: solar panels on 100K SF roof, GPU heat captured via glycol loops, sand
thermal batteries in warehouse bays, hot water cascade to community station,
rooftop greenhouses heated by compute exhaust.

This page links the existing `gen5/foundations/THERMAL_SOVEREIGNTY.md` concepts
to the building's actual infrastructure (8 MW, 18 HVAC units, 14'7" ceilings).

---

## Existing Pages to Update

### `content/outreach/_index.md`

Add to the Partnership Briefs section:

```markdown
## Vision

- **[The Lansing Scuffle](@/vision/lansing_scuffle.md)** — A 464K SF factory
  becoming a solarpunk sovereign campus: data center, wet lab, community
  services, and rooftop gardens in one building
- **[Building-Scale Thermal Sovereignty](@/vision/thermal_sovereignty_building.md)** —
  Solar → compute → heat → hot water → food. The full thermal loop at industrial scale

## Services

- **[Sovereign Consulting](@/outreach/consulting.md)** — The code is AGPL-3.0
  and free forever. Deployment, training, and integration consulting for
  departments and companies
```

### `content/audience/_index.md`

Add entry:

```markdown
- **A company or institution** evaluating this for deployment?
  **[For Companies and Institutions](@/audience/FOR_COMPANIES_AND_INSTITUTIONS.md)** —
  AGPL-3.0 implications, proprietary stack replacement, consulting model,
  regulated environment deployment
```

### `content/products/_index.md`

Add a "Campus" or "Infrastructure" subsection noting the Lansing Scuffle as
the physical-scale expression of the primal composition model. Not a product
to sell — a place where all the products converge.

### `content/products/footprint.md`

If not already present, note the Lansing Scuffle GeoJSON project
(`projects/lansing-scuffle.json`) as a known location in the footPrint tool.
The building is modeled with parcel boundary, building footprint, and K-Derm
zones.

---

## What NOT to Do

- **Do not publish financial details** (SBA 504 rates, subtenant revenue tables,
  consulting rate cards, breakeven analysis). The public site shows the vision
  and the entry point. The financial model is internal planning.
- **Do not publish property brochure content** directly. Reference the building's
  public listing if needed, but the offering memorandum details are not ours to
  republish.
- **Do not publish outreach letters** to specific companies (NVIDIA, Valve, etc.)
  as-is. The invitation pages in `content/outreach/` are the public versions.
- **Do not create pages that read like investor pitches.** This is a public
  science website. The consulting page should feel like documentation, not a
  sales funnel.

---

## Authoring Standards

- Follow existing sporePrint conventions: Zola frontmatter (`+++`), Tera
  templates, `{{ entity() }}` shortcodes for primal names
- Use `{{ total_stat() }}` macros for dynamic counts where available
- Images: if building photos exist, use them. If not, reference the footPrint
  GeoJSON model
- Cross-link to existing pages (lab notebooks, audience briefs, architecture
  docs) rather than duplicating content
- All new content is CC-BY-SA 4.0 per scyBorg triple license

---

## Priority Order

1. `consulting.md` — this has immediate utility (tells people how to engage)
2. `FOR_COMPANIES_AND_INSTITUTIONS.md` — fills the audience gap
3. `lansing_scuffle.md` — the vision page (can wait until building tour happens)
4. `thermal_sovereignty_building.md` — depends on #3
5. Index page updates — after the new pages exist

---

## Entry Points for the Team

Start with:
- `infra/wateringHole/STANDARDS_AND_EXPECTATIONS.md`
- `infra/wateringHole/handoffs/ECOSYSTEM_BLURB.md`
- `infra/sporePrint/config.toml` (entity registry, site config, template macros)
- `infra/sporePrint/content/` (existing content structure)
- `infra/whitePaper/lansingScuffle/06_ECONOMICS.md` (the full economic model — read but don't publish raw)
