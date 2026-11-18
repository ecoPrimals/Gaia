<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Derivation Anchoring Standard

**Version**: 1.0 — May 28, 2026
**Status**: Active
**First Instance**: hotSpring CompChem GuideStone v1.7.0
**Extends**: `TARGETED_GUIDESTONE_STANDARD.md` §4 (Validation Harness)

---

## Principle

> *"What if Planck's constant got a second definition? We'd want one location
> for the evolution."*

Every numeric threshold used in a pass/fail decision must live in exactly ONE
canonical file. Code reads from that file. If the file and the binary disagree,
validation fails. No inline comments. No magic numbers. No silent drift.

This is the difference between a justification (a comment someone can delete)
and an anchor (a structural dependency the system enforces).

---

## The Problem This Solves

```
BEFORE (comments-as-documentation):
  const THRESHOLD: f64 = 5.0; // see Iglesias-Fernández 2015
  
  - Someone changes 5.0 to 2.0 in code → comment becomes a lie
  - Someone updates the paper reference → code is stale
  - Two binaries compiled at different times → different constants, same label
  - Reviewer asks "why 5.0?" → developer hunts through git blame
```

```
AFTER (structural anchoring):
  derivations/threshold_calibration.toml  ← ONE source of truth
       │
       │  loaded at runtime
       ▼
  Code uses value from file
       │
       │  Phase 0 verifies
       ▼
  Compiled fallbacks MUST match file (or validation FAILS)
```

---

## Architecture

### Layer Model

Every constant traces through a 5-layer empirical chain:

| Layer | Name | Question Answered |
|-------|------|------------------|
| 1 | Numerical precision | "How accurate is our instrument?" |
| 2 | Reproducibility floor | "How much does the same measurement vary between runs?" |
| 3 | Signal measurement | "What did we actually measure?" |
| 4 | Decomposition | "Which sub-components contribute to the signal?" |
| 5 | Literature calibration | "How does our measurement compare to published values?" |

The threshold is then: `max(3 × Layer2, physically_motivated_minimum)` with the
constraint that `signal / threshold > 1` (real effects pass).

### Anchoring Categories

Every constant receives one of these categories:

| Category | Meaning | Can Change? |
|----------|---------|-------------|
| `mathematical` | Derived from pure math (e.g., 3σ truncation) | Only if math is wrong |
| `literature` | Published value with DOI | Only if paper is retracted/superseded |
| `convention` | Community standard (e.g., IUPAC definitions) | Only if convention changes |
| `derived` | Calculated from our own measurements (Layers 1-5) | Yes, with new calibration data |
| `policy` | Governance decision (not physics) | Yes, with documented rationale |
| `operational` | System behavior allowance (restart boundaries, etc.) | Yes, with operational evidence |
| `format_precision` | Limited by file format digits | Only if format changes |

---

## Required Files

### `derivations/threshold_calibration.toml`

The canonical file inside every pseudoSpore. Structure:

```toml
[meta]
version = "1.0"
calibration_date = "2026-05-28"
calibration_system = "description of what was measured"

# Layer 1-5 measurements (the evidence base)
[layer1_numerical_precision]
description = "..."
rmsd = 0.0001

[layer2_reproducibility]
max_parity_rmsd = 0.30

[layer3_signal]
rmsd_kjmol = 2.39

# Derived thresholds (the conclusions)
[thresholds.my_threshold]
value = 1.5
unit = "kJ/mol"
derivation = "max(3 × 0.30, 0.50) = 0.90 → 1.5"
signal = 2.39
snr = 1.59

# Pipeline constants
[pipeline.my_pipeline_constant]
value = 2.0
location = "main.rs:1883"
derivation = "..."
_anchoring = "derived"
```

### `tolerances.toml`

Every entry MUST have a `derivation` field pointing into the calibration file:

```toml
[[tolerance]]
name = "my_threshold"
value = 1.5
unit = "kJ/mol"
derivation = "thresholds.my_threshold"
reference = "derivations/threshold_calibration.toml [thresholds.my_threshold]"
```

Entries without `derivation` are flagged with `_anchoring = "NEEDS_CALIBRATION"`
and MUST NOT be used for hard pass/fail decisions until anchored.

---

## Runtime Enforcement

### Phase 0: Constant Self-Consistency

Every `guidestone validate` run begins with Phase 0:

1. Load `derivations/threshold_calibration.toml` from the pseudoSpore directory
2. Extract all `value` fields from `[thresholds.*]` and `[pipeline.*]` sections
3. Compare against compiled-in fallback constants
4. If ANY value disagrees: **FAIL** with message identifying the drift

```
Phase 0: Constant Self-Consistency
  FAIL: PDB_RESOLUTION_TOL: derivation=0.02 vs compiled=0.01 (Δ=0.01)
  → Recompile nest-validate after updating threshold_calibration.toml
```

This ensures:
- Updating the derivation file without recompiling → caught
- Updating code without updating derivation → caught
- Two people using different binary versions → caught on first validate

### Fail-Closed Behavior

If `derivations/threshold_calibration.toml` is missing, validation REFUSES to
run. There is no "proceed with defaults" mode for validation (only for
non-gating preparation steps like `finalize`).

---

## Lifecycle: How Constants Evolve

### New Calibration Data

When new simulations produce better measurements:

1. Update `derivations/threshold_calibration.toml` with new Layer 1-5 values
2. Recalculate thresholds using the standard formula
3. Update `tolerances.toml` entries
4. Recompile the validator binary
5. Run `guidestone validate` — Phase 0 confirms consistency
6. Commit together (derivation + code + tolerances = atomic change)

### New Physical System

When extending to a new substrate, enzyme, or domain:

1. Create a new `[thresholds.system_name]` section in the derivation file
2. Populate Layers 1-5 with measurements from the new system
3. Derive thresholds specific to that system's noise floor and signal
4. The same binary reads the same file — no code changes needed if the
   constants already exist in the schema

### Challenging a Value

If a reviewer (human or automated) questions a threshold:

1. Point them to `derivations/threshold_calibration.toml`
2. The derivation chain is right there: measurement → formula → value
3. If they disagree with the formula, update the derivation, recompile, re-validate
4. Git history shows exactly when and why every value changed

---

## Relationship to Existing Standards

| Standard | Relationship |
|----------|-------------|
| `TARGETED_GUIDESTONE_STANDARD.md` | This standard EXTENDS §4 (Validation Harness). Where that standard says "Named tolerances with scientific justification," this standard says HOW those justifications must be structured and enforced. |
| `ANCHORING_STANDARD.md` | Complementary. That standard covers ecosystem-wide anchoring. This covers numeric constant anchoring within a single artifact. |
| `DEPLOYMENT_VALIDATION_STANDARD.md` | Phase 0 (self-consistency) is a new validation phase that precedes all domain-specific checks. |

---

## Anti-Patterns

### DON'T: Justify in comments

```rust
// BAD: comment can rot
const THRESHOLD: f64 = 5.0; // Iglesias-Fernández 2015 says 5-15 kJ/mol
```

### DON'T: Hardcode without loading

```rust
// BAD: two sources of truth
let threshold = 5.0; // TODO: read from config
```

### DON'T: Put values in tolerances.toml without derivation

```toml
# BAD: magic number with hand-wave
[[tolerance]]
name = "my_threshold"
value = 5.0
justification = "seems about right"
```

### DO: Single source, runtime load, Phase 0 guard

```rust
// GOOD: code reads from the one file
let c = GuideStoneConstants::load(&dir)?;
let threshold = c.cross_landscape_1d_kjmol; // 1.5 (from file)
```

```toml
# GOOD: value has full derivation chain
[thresholds.cross_landscape_1d]
value = 1.5
derivation = "max(3 × noise_floor, kT/5) = max(0.90, 0.50) → 1.5"
noise_floor = 0.30
signal = 2.39
snr = 1.59
```

---

## Implementation Checklist

For any new GuideStone artifact:

- [ ] Create `derivations/threshold_calibration.toml`
- [ ] Populate Layer 1-5 measurements from actual calibration runs
- [ ] Derive all thresholds from measurements (no magic numbers)
- [ ] Implement `GuideStoneConstants::load()` that reads the TOML at runtime
- [ ] Add Phase 0 self-consistency check to validation entry point
- [ ] Ensure `guidestone validate` fails if derivation file is missing
- [ ] Include `derivations/` in the BLAKE3 integrity hash
- [ ] Every `tolerances.toml` entry has `derivation = "..."` pointer
- [ ] Zero entries marked `_anchoring = "NEEDS_CALIBRATION"`
- [ ] Git commit message references "Derivation Anchoring Standard v1.0"

---

## GuideStone Registry Update

Add to `TARGETED_GUIDESTONE_STANDARD.md` registry:

| Name | Version | Anchoring Status |
|------|---------|-----------------|
| hotspring-cazyme-fel | 1.7.0 | Full: 23/23 constants anchored, Phase 0 enforced |

---

## Summary

All future work is only as functional as the validation, replication, and rigor
built beneath it. This standard ensures that rigor is structural — not
aspirational. A constant without a derivation is a liability. A derivation
without runtime enforcement is a suggestion. Both together make science.
