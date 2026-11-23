# sporePrint Wave 134c — Thesis Scaffold + lithoSpore Product + NUCLEUS Hosting Request

**Date**: July 9, 2026
**From**: sporePrint on eastGate
**To**: eastGate overwatch, cellMembrane (golgi), sporeGate CI, projectNUCLEUS, petalTongue
**Status**: CONTENT EVOLUTION SHIPPED — requesting upstream hosting + staging wiring

---

## What Shipped

### Content Evolution (249 pages, 16 sections)

1. **Thesis section scaffolded** (`content/thesis/`): 16-chapter PhD dissertation
   structure with abstracts, maturity badges, and cross-links. Mirrors gen3/thesis/.
   Content transplant is next wave — stubs are wired and navigable now.

2. **lithoSpore product page** (`content/products/lithoSpore.md`): Spore taxonomy,
   three operating modes, three-tier validation, pseudoSpore lifecycle. Links to
   existing lab/guidestone pages.

3. **Philosophy subtabs**: Sidebar groups atlasHugged into Stories/Framework/
   Synthesis/Reference. Section page cards also grouped.

4. **44 cross-references linked**: Inter-essay Document/Chapter references converted
   to Zola internal links across 6 essays.

5. **Complete atlasHugged**: 12 essays + bibliography, all cross-linked, properly
   weighted and structured.

### Metrics

| Metric | Value |
|--------|-------|
| Content pages | 249 |
| Sections | 16 (including thesis) |
| Philosophy essays | 12 + bibliography |
| Thesis chapters | 16 stubs + index + references |
| Cross-references linked | 44 |
| spore-validate tests | 272 |
| Build time | ~2.0s |

---

## Upstream Request: NUCLEUS Hosting + Content Staging

### To cellMembrane / golgi team

sporePrint is now 249 pages with substantial structure (thesis, philosophy,
products, lab, science). The content is ready for sovereign serving.

**Requests:**

1. **Confirm thin-relay composition on golgi** — sporePrint expects the golgi
   composition to be `thin-relay` (songBird + nestGate + cellMembrane). Is Zola
   still building locally, or are we consuming pre-built artifacts from sporeGate?

2. **Stage thesis section for serving** — the new `/thesis/` section with 18 pages
   should render through the existing pipeline. Verify it appears at
   `primals.eco/thesis/` after cascade.

3. **lithoSpore product accessible via mesh** — long-term: lithoSpore validation
   artifacts (USB images, pseudoSpore archives) should be downloadable through
   sporePrint. This requires NestGate CAS integration for binary distribution.
   Not urgent — current state is documentation only.

### To sporeGate CI team

4. **sporePrint build authority** — confirm sporeGate builds sporePrint (`zola build`
   + `spore-validate certify`) and rsyncs to golgi. If golgi is still building
   locally (`MEMBRANE_ZOLA_AUTO_BUILD=1`), this needs to transition to the
   sporeGate-builder / golgi-consumer model per thin-relay spec.

### To petalTongue team

5. **Thesis rendering readiness** — when petalTongue serves sporePrint content,
   the thesis section's `{{ maturity(level="planned") }}` shortcodes need to be
   resolved. Current static SVG fallback handles this gracefully via `viz_embed`.

6. **Live lithoSpore gallery** — future wave: the pseudoSpore gallery
   (`/lab/spores/`) should eventually pull from lithoSpore's `registry.toml`
   via petalTongue data service.

### To projectNUCLEUS

7. **sporePrint composition profile** — verify `graphs/sporeprint_composition.toml`
   reflects the current state: petalTongue web, NestGate CAS, songBird relay,
   bearDog TLS (pending CryptoProvider fix). Current serving is Caddy + Zola
   static output.

### To eastGate overwatch

8. **Content transplant staging** — the following gen3 content is queued for
   transplant in upcoming waves:
   - `thesis/` bulk content (16 chapters, ~3,000 lines)
   - `data/` faculty profiles and reproduction plans (~2,400 lines)
   - `about/` sovereign science, hardware, licensing (~2,900 lines)
   - `primals/` deep-dive per-primal docs (~2,000 lines)

9. **Historical document warehousing** — old docs and stale references can be
   warehoused on the pepti depot as fossil record. The provenance chain
   provides digital reference — same pattern as genetics comparison across
   generations.

---

## Divergence Status (from AAR 133a)

| ID | Issue | Status |
|----|-------|--------|
| SP-DIV-01 | GitHub Pages still load-bearing | **Open** — VPS serving 200, deploy.yml still active |
| SP-DIV-02 | Dual-push required | **Open** — continue until deploy.yml archived |
| SP-DIV-03 | No full NUCLEUS on VPS | **Partial** — 4 binaries deployed Wave 133c |
| SP-DIV-04 | cascade doesn't rebuild Zola | **Workaround** — Zola auto-build on golgi |
| SP-DIV-05 | deploy.yml still load-bearing | **Open** — labeled shadow |

**Blocker for full sovereignty:** bearDog CryptoProvider fix (UNIT-DIV-04).

---

## Next Wave Targets

1. **Thesis content transplant** — fill chapter stubs from gen3 source
2. **NUCLEUS hosting convergence** — sporeGate builds, golgi consumes
3. **lithoSpore deployment wiring** — NestGate CAS for binary distribution
4. **Evidence Snapshot page** — canonical metrics surface for outsiders
5. **SHOW_HN prep** — E-category items (cold clone, CI badges, reproduce guide)

---

*sporePrint is 249 pages of executable evidence. The structure is laid.
The content transplant machine is warm. The NUCLEUS composition is next.*
