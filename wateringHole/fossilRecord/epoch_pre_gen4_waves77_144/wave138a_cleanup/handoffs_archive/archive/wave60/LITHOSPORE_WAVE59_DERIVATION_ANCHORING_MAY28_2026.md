# lithoSpore Wave 59: Derivation Anchoring + Deep Debt Polish

**Date**: May 28, 2026
**Author**: lithoSpore
**Context**: Wave 59 Mountain Blurb — derivation anchoring gap, code debt

---

## Summary

Wave 59 audit identified that PSEUDOSPORE_STANDARD GUIDESTONE-GRADE items 12-14
were spec'd but not implemented. This wave closes that gap plus remaining code debt.

## Shipped

### Derivation anchoring (GUIDESTONE-GRADE items 11-14)

1. **`PseudoSporeEnvelope::validate()`** — new checks:
   - Item 11: warns if `tolerances.toml` missing
   - Item 12: warns if `derivations/threshold_calibration.toml` missing
   - Item 13: flags `[[tolerance]]` entries without `derivation` field
   - Item 14: flags `_anchoring = "NEEDS_CALIBRATION"` entries
   - New test: `guidestone_grade_tolerance_checks`

2. **`litho emit-pseudospore`** — new step 9:
   - Copies `derivations/` from source (profile parent) if present
   - Otherwise scaffolds `derivations/threshold_calibration.toml` stub
   with 5-layer chain template per DERIVATION_ANCHORING_STANDARD v1.0

### Code debt (continued from Wave 58)

- `validate::run` → `pub(crate)` (last stale `pub` in binary crate)
- `PseudoSporeEnvelope::load()` warnings → accumulated in `load_warnings`
  field instead of `eprintln!` (structured, no side effects)
- `validate()` now includes load warnings in result

### Doc sync

- GLOSSARY: NC-1.4 "pending" → "resolved (v3.81)"
- PRIMAL_REGISTRY: `litho_core::pseudospore` → `pseudospore-core` (retired)
- lithoSpore root docs: 191→192 tests, derivation anchoring in ARCHITECTURE

## Metrics

```
192 tests, 0 failures
0 clippy warnings
0 unsafe code
All files ≤ 800 LOC (domain_profile.rs 798, audit/domain.rs 799)
75/75 science checks
cargo deny: advisories ok, bans ok, licenses ok, sources ok
```

## NC-5 Status

GUIDESTONE-GRADE emission gate now has code support. Remaining gates are
operational: biomeOS v3.84 VPS deploy → hotSpring column U → groundSpring
column U → NC-5.live → stadial.

---

*Wave 59. Derivation anchoring wired. Deploy the ecosystem.*
