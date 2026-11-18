# Dispersal Pattern — Primal-as-Site

**Date**: Sep 25, 2026 | **Wave**: 157+ | **Author**: eastGate
**Status**: PATTERN DEFINITION — documented from detroit reference implementation
**Lineage**: detroit-build proved the pattern; this spec generalizes it

---

## Purpose

Any primal, domain, or methodology in the ecosystem can produce a
`.primals.eco` static site that is provenance-traced, content-addressed,
and integrated with the sporePrint catalogue. This document describes
the pattern that detroit proved and that other primals can absorb.

detroit.primals.eco is the first non-sporePrint site in the ecosystem.
It was built from scratch to demonstrate that the substrate generalizes.

---

## Architecture

```
                       ┌─────────────────────────────────┐
                       │  sporePrint Catalogue            │
                       │  config.toml entity_registry     │
                       │  sources.toml metric refresh     │
                       └──────────┬──────────────────────┘
                                  │ registered in
                       ┌──────────▼──────────────────────┐
                       │  site.primals.eco                │
                       │  Zola static site                │
                       │  ├── config.toml (registries)    │
                       │  ├── content/*.md (pages)        │
                       │  ├── data/edges.toml (graph)     │
                       │  └── crates/site-build/          │
                       │       └── uses litho-core        │
                       └──────────┬──────────────────────┘
                                  │ produces
           ┌──────────────────────┼──────────────────────┐
           ▼                      ▼                      ▼
   content-manifest.toml    graph.json             braids.json
   (BLAKE3 hashes)          (typed edges)          (PROV-O attribution)
           │                      │                      │
           ▼                      ▼                      ▼
     nestGate CAS          sweetGrass braids       loamSpine spine
     (content.put)         (braid.create)          (RFC 3161)
```

---

## Pattern Components

### 1. Zola Site with Entity Registries

Every site keeps typed registries in `config.toml [extra.*]`. Detroit has
actors, entities, and sources. sporePrint has entity_registry. The registry
tables follow the same shape:

```toml
[extra.actors.banks]
display = "Steven Banks"
role = "Subject"
page = "/network/actors/steven-banks/"
```

**litho-core module**: `litho_core::registry` provides `parse_extra()`,
`extract_registry()`, `display_names()`, and `validate_page_refs()` for
any Zola config registry.

### 2. Typed Edges with Epistemic Grammar

Relationships between entities are typed edges in `data/edges.toml`:

```toml
[[edge]]
source = "banks"
target = "gee"
edge_type = "managed_by"
epistemic_status = "record"
source_doc = "LARA PSA Database"
```

Seven epistemic levels express claim confidence:

| Status | Witness Kind | Witness Tier | Meaning |
|--------|-------------|--------------|---------|
| record | hash | anchor | Source doc BLAKE3 in CAS |
| corroborated | hash | gateway | Multiple independent hashes |
| inference | marker | open | Analytical conclusion |
| allegation | marker | local | Filed complaint, CAS-anchored |
| filed | hash | anchor | Filing receipt in CAS |
| adjudicated | signature | external | Court/authority determination |
| corrected | marker | open | alternateOf → corrected braid |

**litho-core module**: `litho_core::provenance` provides `EpistemicStatus`,
`epistemic_to_witness()`, and all sweetGrass/nestGate wire-format types.

### 3. Build Crate using litho-core Substrate

Each site has a build crate (e.g., `detroit-build`) that uses litho-core:

| litho-core module | Build step | Output |
|-------------------|-----------|--------|
| `frontmatter` | Parse `+++ TOML +++` from content pages | Typed page data |
| `manifest` | BLAKE3 hash all content files | `content-manifest.toml` |
| `graph` | Validate edge endpoints against registry | `graph.json`, `graph.csv` |
| `registry` | Parse config registries, validate page refs | Typed entities |
| `provenance` | Map epistemic grammar to wire types | `braids.json`, `cas-manifest.json` |
| `report` | Accumulate diagnostics during verify | Structured error report |

### 4. Provenance Trio Wiring

The build output feeds three primal services (when available):

| Primal | Protocol | Build output | Wire type |
|--------|---------|-------------|-----------|
| nestGate | `content.put` JSON-RPC | `cas-manifest.json` | `CasPutParams` |
| sweetGrass | `braid.create` JSON-RPC | `braids.json` | `BraidCreateParams` |
| loamSpine | RFC 3161 timestamp | Build wave hash | (hash-chain anchoring) |
| bearDog | Ed25519 | Evidence claims | (signature witness) |

### 5. Convergence Depth Meter

Every claim has a verification depth from 1 (CAS hash exists) to 5
(Ed25519 signed witness):

| Depth | Stage | Meaning |
|-------|-------|---------|
| 1 | CAS | BLAKE3 hash in nestGate |
| 2 | DAG | rhizoCrypt session recorded |
| 3 | Spine | loamSpine permanent anchor |
| 4 | Braid | sweetGrass PROV-O attribution |
| 5 | Signed | bearDog Ed25519 witness |

**litho-core type**: `ConvergenceDepth` enum.

### 6. sporePrint Catalogue Registration

Add the site as an entity in sporePrint:

1. `config.toml [extra.entity_registry.mysite]` — display, kind, description, repo
2. `sources.toml [sources.mysite]` — repo path for metric auto-refresh
3. Tag relevant content pages with `[taxonomies]` for cross-referencing

---

## Reference Implementation

**detroit** (`publicRecord/detroit`) is the reference implementation:

| Component | Detroit path | Purpose |
|-----------|-------------|---------|
| Build crate | `crates/detroit-build/` | 9 modules, 7 build steps |
| Shared substrate | `crates/litho-core/` | 6 modules (frontmatter, manifest, graph, report, registry, provenance) |
| Entity registries | `site/config.toml [extra.actors/entities/sources]` | 43 nodes |
| Typed edges | `data/edges.toml` | 57 edges with epistemic grammar |
| Content | `site/content/*.md` | 50 pages (18 sections, 32 pages) |
| Graph output | `site/static/graph.json` | Node/edge visualization data |
| Provenance output | `site/static/braids.json` | sweetGrass braid creation requests |
| CAS output | `site/static/cas-manifest.json` | nestGate content.put requests |
| Content manifest | `content-manifest.toml` | BLAKE3 hashes, root hash |

---

## Convergence Model

This pattern is not imposed top-down. It emerges through convergence:

1. **detroit proves the pattern** — first non-sporePrint site in the ecosystem
2. **litho-core abstracts it** — shared modules any site can use
3. **wateringHole documents it** — this spec, discoverable by any gate
4. **Other primals absorb it** — through their own evolution, not forced restructuring

The sporePrint team's lithoSpore `litho-core` (science validation chassis)
and this `litho-core` (Zola site substrate) are two different crates sharing
the `litho` name. They evolve independently and converge where their patterns
overlap — BLAKE3 provenance, typed registries, discovery protocols.

---

## Who Adopts This

Any domain that produces a body of typed, citable claims with verifiable sources:

| Domain | Site | Registry types | Edge grammar |
|--------|------|---------------|-------------|
| **Legal (active)** | detroit.primals.eco | actors, entities, sources | 7 epistemic levels |
| **Methodology (LIVE)** | gorilla.primals.eco (20 pages, alias: guerillagorilla.primals.eco) | capabilities, cases, tools | operational levels |
| **Science (future)** | TBD | researchers, papers, datasets | validation levels |
| **Medical (future)** | TBD | protocols, trials, outcomes | evidence grades |
| **Gaming (future)** | TBD | rulesets, characters, sessions | creative attribution |

The pattern scales because the substrate is domain-agnostic. Each site owns
its registries and edge grammar; litho-core provides the common plumbing.

---

## Wildcard Subdomain Evolution (Sep 27, 2026)

The current model uses specific subdomain routes per site:
```
detroit.primals.eco   →  Caddy route → /opt/.../detroit/
sporeprint.primals.eco →  Caddy route → /opt/.../sporePrint/
```

The evolution is wildcard TLS + parameterized routing:
```
*.primals.eco  →  Caddy wildcard TLS (DNS-01 via Cloudflare API)
                  [primal].primals.eco   per primal
                  [project].primals.eco  per sub-project
```

This enables hierarchical site relationships:
```
guerillagorilla.primals.eco  →  the primal (methodology, capabilities)
    └── detroit.primals.eco  →  Case Study #1 (Banks enterprise)
    └── [future].primals.eco →  Case Study #N
```

**Not blocking current operations.** detroit.primals.eco and primals.eco
continue on specific-subdomain routing. The wildcard pattern is an
evolution target, not a migration requirement.

**sporeGate eval tasks:**
1. Evaluate Caddy wildcard TLS for `*.primals.eco` (DNS-01 challenge via Cloudflare API)
2. Design parameterized Zola build pipeline (repo → subdomain mapping)
3. Spec litho-core shared template consumption across N sites

---

*Dispersal pattern documented from detroit reference implementation.
guerillaGorilla site LIVE at gorilla.primals.eco (20 pages, Sep 27).
Three-tier dispersal PROVEN: sporePrint (catalogue) → guerillaGorilla (methodology) → detroit (case study).
Wildcard subdomain evolution spec'd. Any gate team can adopt this pattern for their domain.*
