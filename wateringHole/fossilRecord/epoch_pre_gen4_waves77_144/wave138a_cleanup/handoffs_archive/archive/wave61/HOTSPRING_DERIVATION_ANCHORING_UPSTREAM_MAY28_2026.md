# hotSpring → primalSpring: Derivation Anchoring Standard — Upstream Handoff

**Date:** May 28, 2026
**From:** hotSpring (computational chemistry)
**To:** primalSpring (coordination) → all springs in the river delta + lithoSpore
**Priority:** Pre-stadial — integrate before NC-5.live gate

---

## Summary

hotSpring has implemented and validated a new ecosystem standard:
**Derivation Anchoring** (`infra/wateringHole/DERIVATION_ANCHORING_STANDARD.md`).

This standard ensures that every emitted pseudoSpore — regardless of which spring
produces it — carries structurally-enforced numeric rigor. No magic numbers survive
emission. The validation pipeline physically cannot PASS if any threshold lacks a
formal derivation chain.

**The ask:** Wire this into lithoSpore's emission gate and primalSpring's validation
matrix so that all spores are GuideStones by principle, not by individual spring
discipline.

---

## What Was Built (hotSpring v1.7.0)

| Component | Location | Function |
|-----------|----------|----------|
| Standard | `infra/wateringHole/DERIVATION_ANCHORING_STANDARD.md` | Ecosystem-wide spec |
| First instance | `pseudoSpore_hotSpring-CompChem-GuideStone_v1.7.0/derivations/threshold_calibration.toml` | 23 anchored constants, 5-layer chain |
| Runtime loader | `nest-validate/src/constants.rs` → `GuideStoneConstants::load()` | Reads derivation file at validation time |
| Phase 0 gate | `nest-validate/src/main.rs` → `guidestone_validate()` | Compiled fallbacks must match derivation file |
| Result | 190/190 checks PASS including self-consistency | Proven on monomeric xylose in GH10 xylanase |

---

## What primalSpring Should Distribute

### To lithoSpore (spore emission gate)

lithoSpore's `emit-pseudospore` already validates structural completeness (envelope,
BLAKE3, scope.toml, data.toml). Add one check to the emission gate:

```
IF pseudoSpore contains tolerances.toml:
  THEN derivations/ directory MUST exist
  AND  derivations/threshold_calibration.toml MUST parse
  AND  every [[tolerance]] entry MUST have derivation = "..." field
  AND  zero entries may have _anchoring = "NEEDS_CALIBRATION"
```

**Implementation path:** This is a new Tier-0 structural check in lithoSpore's
`pseudospore-core`. If the spore declares tolerances, it must anchor them. If it
has no tolerances (pure data spores, non-scientific artifacts), the check is skipped.

**Wire format for lithoSpore:**

```toml
# Add to pseudospore-core's structural validation
[[tier0_check]]
name = "derivation_anchoring"
description = "All numeric tolerances trace to derivation file"
condition = "tolerances.toml exists"
requires = ["derivations/threshold_calibration.toml"]
validates = "every [[tolerance]].derivation field is non-empty"
blocks_emission = true
standard = "DERIVATION_ANCHORING_STANDARD.md v1.0"
```

### To all springs (river delta broadcast)

Each spring that emits pseudoSpores with numeric thresholds must:

1. **Create `derivations/threshold_calibration.toml`** in their pseudoSpore directory
2. **Populate the 5-layer measurement chain** for their domain:
   - Layer 1: Numerical precision (instrument accuracy)
   - Layer 2: Reproducibility floor (run-to-run variation)
   - Layer 3: Signal measurement (what was actually observed)
   - Layer 4: Decomposition (which sub-components contribute)
   - Layer 5: Literature calibration (external anchor)
3. **Link tolerances.toml entries** to the derivation file
4. **Implement Phase 0** in their validation binary (or rely on lithoSpore's
   emission gate for the structural check)

**Per-spring mapping:**

| Spring | Has numeric thresholds? | Action |
|--------|------------------------|--------|
| hotSpring | Yes (190 checks, 23 constants) | DONE — first instance |
| groundSpring | Yes (DFE fitting, fitness tolerances) | Create derivations/ with LTEE calibration |
| wetSpring | Yes (diversity metrics, OTU thresholds) | Create derivations/ with 16S calibration |
| neuralSpring | Yes (loss convergence, regime detection) | Create derivations/ with training calibration |
| healthSpring | Likely (physiological ranges) | Create derivations/ with clinical reference ranges |
| airSpring | Likely (signal processing tolerances) | Create derivations/ with acoustic calibration |
| ludoSpring | Unlikely (game logic, not science) | Skip unless emitting scientific spores |

### To lithoSpore (audit profile evolution)

lithoSpore already has `domain_profile.toml` for per-domain audit profiles. The
Derivation Anchoring Standard adds a new audit check category:

```toml
[[audit_check]]
id = "derivation_completeness"
description = "All numeric thresholds fully anchored"
severity = "blocking"
check_type = "structural"
evaluator = "count tolerances without derivation field = 0"
```

This should be added to every domain profile that includes quantitative validation.

---

## Integration with NUCLEUS Validation Matrix

Add to the validation matrix (column alongside U/V/W):

| Column | Gate | Meaning |
|--------|------|---------|
| **X** | Derivation Anchoring | All emitted spores carry `derivations/` with zero unanchored thresholds |

**Gate criteria:**
- lithoSpore `emit-pseudospore` enforces structural check (Tier 0)
- Spring validator enforces runtime check (Phase 0)
- `tolerances.toml` has zero `_anchoring = "NEEDS_CALIBRATION"` entries
- `derivations/threshold_calibration.toml` parses without error

**Stadial gate implication:** A spring cannot reach postPrimordial spore emission
if its pseudoSpores carry magic numbers. This is structural — not a policy someone
can choose to skip.

---

## Why This Matters (the principle)

> "All future work is only as functional as the validation, replication, and rigor
> we build as a foundation beneath it."

The ecosystem currently has 8 springs capable of emitting pseudoSpores. If each
spring independently decides how to justify its thresholds, we get 8 different
approaches to numeric rigor — some comments, some TOMLs, some nothing. This
standard makes the rigor structural:

- **Without this:** A spring can emit a spore with `value = 5.0` and no one knows
  where 5.0 came from. It passes lithoSpore structural checks because it has a
  `tolerances.toml` with a `justification` string.
- **With this:** A spring cannot emit a spore with `value = 5.0` unless
  `derivations/threshold_calibration.toml` has a section showing the 5-layer
  measurement chain that produced 5.0. lithoSpore's emission gate blocks it.

The difference: justification is a string a human reads. Derivation is a structure
a machine enforces.

---

## Reference Implementation

hotSpring's implementation is the template. Springs can fork the pattern:

```
pseudoSpore_{spring}-{domain}-GuideStone_v{X}/
├── derivations/
│   └── threshold_calibration.toml   ← 5-layer chain (domain-specific)
├── tolerances.toml                  ← every entry has derivation = "..."
└── validate                         ← Phase 0 runs before domain checks
```

The full reference:
- Standard: `infra/wateringHole/DERIVATION_ANCHORING_STANDARD.md`
- Instance: `springs/hotSpring/pseudoSpore_hotSpring-CompChem-GuideStone_v1.7.0/`
- Loader code: `springs/hotSpring/control/plumed_nest/nest-validate/src/constants.rs`
- Phase 0 logic: `springs/hotSpring/control/plumed_nest/nest-validate/src/main.rs`
  (search for "Phase 0: Constant Self-Consistency")

---

## Requested Actions

| Team | Action | Blocking? |
|------|--------|-----------|
| **primalSpring** | Add column X to NUCLEUS_VALIDATION_MATRIX. Broadcast to all springs. | Yes (pre-stadial) |
| **lithoSpore** | Add `derivation_anchoring` Tier-0 check to `emit-pseudospore`. | Yes (blocks NC-5.live) |
| **lithoSpore** | Add `derivation_completeness` to all domain profiles. | No (can follow) |
| **groundSpring** | Create `derivations/` for LTEE pseudoSpore (DFE/fitness calibration). | No (next emit) |
| **wetSpring** | Create `derivations/` for diversity pseudoSpore (16S/OTU calibration). | No (next emit) |
| **Other springs** | Absorb standard. Create derivation files before next pseudoSpore emit. | No (by next emit) |

---

## Provenance

- Origin: hotSpring session `63b41c45-5abe-4465-9529-b7820295f465`
- Triggered by: KLN cancellation analogy (Murillo) → threshold re-examination →
  discovery that all constants lacked formal derivation → full "Zero Magic Numbers"
  implementation
- Validated: 190/190 checks PASS, Phase 0 enforced, 23/23 constants anchored
- Standard version: `DERIVATION_ANCHORING_STANDARD.md` v1.0, May 28, 2026
