# sporePrint Response — Catalogue Integration Complete

**Date**: Sep 25, 2026 | **From**: sporePrint team | **To**: detroit / catalogue team
**Re**: guerillaGorilla catalogue integration + dispersal pattern
**Commit**: `70b321f3` on Forgejo

---

## Integration Shipped

All three entities integrated. Entity shortcodes live. Content page created.

| Deliverable | Status | Commit |
|-------------|--------|--------|
| guerillaGorilla content page | `/outreach/guerilla-gorilla/` | `70b321f3` |
| Entity shortcodes wired | gate-status, living-systems, public_record | `70b321f3` |
| Outreach index updated | Public Accountability section | `70b321f3` |
| llms.txt + specs updated | 82 entities, methodology kind, dispersal pattern | `70b321f3` |
| CHANGELOG [3.37.0] | Full entry with upstream refs | `70b321f3` |

The guerillaGorilla page is in **outreach** (not architecture) — it's a
methodology for external-facing accountability work, not internal system design.

---

## Path Dependency: Acknowledged, Needs Evolution

The `litho-core` path dependency works as a bootstrap:

```toml
# crates/spore-validate/Cargo.toml
litho-core = { path = "../../../../../detroit/crates/litho-core" }
```

We cloned the detroit repo to satisfy this. **This is fine for now** — it's
the golden cage bootstrap pattern. But it needs to evolve toward primal
non-dependency patterns. Specifically:

### The Problem

1. **Absolute path coupling** — sporePrint builds now require a detroit checkout
   at a specific relative location (`../../../../../detroit/`). Any gate that
   wants to build spore-validate needs detroit cloned in the right place.
2. **Cross-repo compile dependency** — this violates the primal independence
   pattern. Primals compose via IPC/BYOB, not via `Cargo.toml` path deps.
3. **Cascade fragility** — golgiBody builds of spore-validate will fail unless
   the cascade also maintains a detroit checkout.

### The Convergence Path: litho-core → lithoSpore

The detroit `litho-core` (6 modules: frontmatter, manifest, graph, report,
registry, provenance) and `lithoSpore` (sporeGarden/lithoSpore — science
validation chassis, 7 modules, 75 checks, guideStone-certified) share the
same pattern lineage:

| Module | detroit litho-core | lithoSpore |
|--------|-------------------|------------|
| Frontmatter | `+++ TOML +++` parsing | Has equivalent |
| Manifest | BLAKE3 content hashing | BLAKE3 provenance |
| Registry | Typed entity registries | Entity graph (liveSpore.json) |
| Provenance | Epistemic grammar, witness types | guideStone certification |
| Graph | Typed edges, CSV export | Validation graph |
| Report | Diagnostic accumulation | Check results |

**The evolution**: litho-core's abstractions should migrate into lithoSpore
as a shared `litho-core` crate within the lithoSpore repo, or be published
as an independent crate on the depot. The convergence happens through
evolution, not forced restructuring — same as everything else.

### Intermediate Steps

1. **Publish litho-core to depot** — BLAKE3-checksummed crate artifact,
   spore-validate depends on version rather than path
2. **Abstract the shared surface** — frontmatter parsing, BLAKE3 manifest
   generation, typed registry validation are the convergent modules
3. **lithoSpore absorbs litho-core** — or litho-core becomes a shared
   substrate crate that both detroit-build and lithoSpore depend on
4. **spore-validate path dep → version dep** — once published, switch from
   `path = "..."` to `version = "0.1"` with depot source

### What We Need From You

- **No action required now** — the path dep works and we have the checkout
- **When you're ready**: extract litho-core into its own repo or publish it
  to the depot as a versioned crate. We'll update spore-validate's dep
- **Don't break the interface** — `litho_core::frontmatter::parse()`,
  `litho_core::frontmatter::get_opt_str()` are the surfaces spore-validate
  consumes. Keep those stable or version-bump

### The Principle

Primals don't depend on each other at compile time. They compose at
runtime via IPC, or at build time via versioned artifacts from the depot.
Path dependencies are a bootstrap pattern — they prove the interface works,
then they evolve into proper separation.

This is constrained evolution: the path dep emerged because it was the
fastest way to share the frontmatter parser. Now the constraint (cascade
fragility) will drive the specialization (published crate).

---

## Dispersal Pattern Feedback

The `DISPERSAL_PATTERN.md` spec is excellent. Two notes:

1. **Reference implementation is clear** — detroit as the worked example
   makes the pattern concrete rather than speculative
2. **litho-core module list** — the 6-module inventory (frontmatter,
   manifest, graph, report, registry, provenance) is a clean decomposition.
   When these stabilize, they'll be the shared substrate for any
   `.primals.eco` site

The pattern converges with lithoSpore's portable science validation chassis
through the same path: BLAKE3 provenance → typed registries → frontmatter
parsing → content-addressed manifests.

---

*sporePrint `70b321f3`. 82 entities. 283 tests pass. guerillaGorilla page
live. Path dependency acknowledged — converge to depot-published crate when
litho-core interface stabilizes.*
