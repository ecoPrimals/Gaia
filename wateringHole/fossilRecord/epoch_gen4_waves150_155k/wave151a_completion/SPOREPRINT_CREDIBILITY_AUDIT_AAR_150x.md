# sporePrint Credibility Audit AAR — Wave 150x

**Date**: July 25, 2026 | **Wave**: 150x | **From**: eastGate overwatch
**Scope**: External review response — count consistency, claim qualification, maturity shelving
**Commit**: `f3b710d` (sporePrint main)

---

## What Happened

An external reviewer conducted a thorough audit of `primals.eco` and the
ecoPrimals GitHub presence. The review was overwhelmingly positive — calling
the project a "proto-institution for executable science" and identifying the
Evidence Snapshot as "the highest-leverage page." However, it surfaced
specific credibility leaks: inconsistent counts across surfaces, absolutist
claims that contradict documented exceptions, and products mixed by maturity.

sporePrint team treated the review as fossil-record truth and swept 30 files
in a single commit.

---

## What Was Fixed (sporePrint Scope)

### 1. Count Consistency — 8 → 9 springs, 3 → 4 orgs

**Root cause**: `config.toml` had `total_springs = 8` but 9 entities with
`kind = "spring"` (rustChip was missing from the count). Organization count
was 3 on the homepage but 4 in CONTEXT.md (protoKarya missing from template).

**Fix**: Updated `config.toml` totals, homepage template (added protoKarya
org card), and 15+ content pages. Replaced hardcoded counts with
`{{ total_stat() }}` shortcodes where possible.

**Files**: config.toml, templates/index.html, creative_surface.md,
atlas_memory_palace.md, SCYBORG_LICENSING.md, SPRING_CATALOG.md,
CROSS_SPRING_EVIDENCE_MAP.md, neural_api.md, ECOSYSTEM_INVENTORY.md,
COMPOSITION_PIPELINE.md, ECOSYSTEM_VISUALIZATION.md, PRIMAL_CATALOG.md,
CONTENT_MAP.md, llms.txt, README.md

### 2. Stale WGSL Shader Counts — 806/800+ → shortcode

**Root cause**: BarraCuda's shader count grew from 806 → 952, but 12 content
pages still hardcoded the old number. The reviewer's cited "860" appears to
come from barraCuda's README (upstream team responsibility).

**Fix**: Replaced all hardcoded WGSL counts with `{{ total_stat(stat="wgsl_files") }}`
in architecture, technical, methodology, audience, and outreach pages. Single
source of truth now flows from config.toml.

**Files**: SOVEREIGN_GPU_PIPELINE_PROFILE.md, SOVEREIGN_PRIOR_ART_CATALOG.md,
GRANT_TECHNICAL_APPENDIX.md, KNOWLEDGE_COMMONS_TARGETS.md, outreach/_index.md,
CAPABILITY_PARITY_BRIEF.md, HOW_TO_START_A_SPRING.md, EVOLUTION_TIMELINE.md,
PRIMAL_CATALOG.md

### 3. Qualified Absolutist Claims

**Root cause**: Homepage said `#![forbid(unsafe_code)]` universally and
"replaces the conventional stack." The internal standard (STANDARDS_AND_EXPECTATIONS
line 33) correctly scopes the unsafe exception to hardware-touching crates.
The external surface did not.

**Fix**:
- Homepage reframed from "replaces" to reviewer's stronger position:
  "produces self-contained scientific computations that reproduce published
  results on owned commodity hardware and carry their validation and provenance"
- `#![forbid(unsafe_code)]` now explicitly scoped: "forbidden by default,
  isolated to narrowly scoped, safety-documented hardware-containment crates"
- "any GPU" → "any GPU with Vulkan" / "tested: NVIDIA, AMD, Intel"
- "zero C dependencies" → "pure Rust" in stat ribbon
- Evidence Snapshot gained new Safety Model section documenting the toadStool
  exception and dependency chain analysis
- base.html structured data: removed "Replaces CUDA" from JSON-LD

### 4. Products Page Maturity Shelving

**Root cause**: Products page mixed live apps, research previews, and
architectural direction on one flat surface. Outsiders couldn't answer
"What can I use today?"

**Fix**: Reorganized into three shelves:

| Shelf | Products |
|-------|----------|
| **Deploy now** | footPrint, esotericWebb, Tower Atomic, cellMembrane |
| **Research preview** | lithoSpore, projectFOUNDATION, tideGlass |
| **Architectural direction** | projectNUCLEUS, Lansing Scuffle |

---

## What Remains Outside sporePrint Scope

These are systemic issues that require upstream team action. See companion
document: `foundations/EXTERNAL_CLAIM_CONVERGENCE_STANDARD.md`

### P1 — biomeOS README: "A++ LEGENDARY" / "Production Ready"

biomeOS describes itself as "Production Ready, A++ LEGENDARY" while
documenting pre-1.0 workspace semantic versioning. The internal evolutionary
grade is fine for internal logs but weakens institutional-facing surfaces.

**Request**: biomeOS team adopt dual labeling:
- **Internal**: stadial grade, wave, debt state (as-is)
- **External**: experimental / research-ready / deployment-ready / production-candidate

### P1 — barraCuda README: Stale WGSL Count (860 vs 952)

Reviewer cited 860 shaders from barraCuda README. Registry says 952.

**Request**: barraCuda team update README metrics or pull from a shared
count via CI.

### P1 — ecoPrimals GitHub Org Profile: Unscoped `#![forbid(unsafe_code)]`

The org profile says all code uses `#![forbid(unsafe_code)]`. toadStool
has 44 documented, justified unsafe blocks. The internal standard
(STANDARDS_AND_EXPECTATIONS §1) correctly scopes the exception.

**Request**: ecoPrimals org profile updated to:
> Unsafe code is forbidden by default and isolated to narrowly scoped,
> safety-documented hardware-containment crates where required.

### P2 — bearDog / skunkBat Source Publication

Reviewer noted these "available on request" rather than publicly inspectable,
creating a philosophical gap with the openness claims. The identity, crypto,
transport, and defensive-security foundation is precisely what skeptical
reviewers most need to inspect.

**Request**: Tower team evaluate timeline for public source publication.
This closes a disproportionately large trust gap.

### P2 — External Maturity Labeling Standard

All READMEs should distinguish internal evolutionary status from external
maturity level. Currently only sporePrint's products page does this.

**Request**: All teams adopt the maturity vocabulary from EVIDENCE_SNAPSHOT:
`implemented`, `reproduced`, `certified`, `architectural`, `planned`, `unaudited`

### P3 — Externalization Phase

The reviewer's strongest recommendation: the next phase should not be more
architecture. It should be externalization:

1. One canonical guideStone that a stranger can download and verify in minutes
2. One public external reproduction ledger showing failures as well as successes
3. One spring used by a scientist on data the ecosystem did not select
4. One institutional-quality technical report with claims narrower than evidence
5. Complete publication of foundational Tower source

---

## Lessons Learned

1. **Shortcodes are the answer to count drift.** Every hardcoded number is a
   future inconsistency. The `{{ total_stat() }}` and `{{ entity_stat() }}`
   pattern prevents this class of error entirely.

2. **Internal standards were already correct.** STANDARDS_AND_EXPECTATIONS
   correctly scoped the unsafe exception since its creation. The leak was
   from internal → external translation. The fix is convergence, not new policy.

3. **Reviewer's strongest framing is better than ours.** "Produces self-contained
   scientific computations that reproduce published results on commodity hardware
   and carry their validation and provenance" is more defensible and more
   compelling than "replaces the conventional stack."

4. **Maturity shelving is immediately actionable.** The three-shelf model
   (deploy now / research preview / architectural direction) should extend
   to all public-facing surfaces, not just the products page.

---

## Validation

- `spore-validate validate`: 0 errors, 2 pre-existing warnings
- `zola build`: 312 pages, 0 errors, 4 known warnings
- `spore-validate certify`: VALID — manifest matches current state
- Pushed to Forgejo: `7d994b3..f3b710d`
