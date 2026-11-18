# airSpring Wave 20 Absorption — Schema Standardization

**Date**: May 16, 2026
**Spring**: airSpring v0.10.0 | **Tests**: 1,057 lib + 62 forge = 1,435 total
**Registry**: 452-method canonical sync (Wave 20)

---

## Changes Applied

### `capability.list` Canonical Envelope

airSpring's `handle_capability_list` now returns the canonical subset:

```json
{
  "capabilities": ["science.et0_fao56", "science.et0_hargreaves", "...51 total..."],
  "count": 51,
  "primal": "airspring",
  "version": "0.10.0",
  "domain": "ecology",
  "total": 51,
  "science": [...],
  "infrastructure": [...],
  "composition": { ... },
  "operation_dependencies": [...],
  "cost_estimates": [...],
  "uptime_secs": 1234
}
```

Top-level `"capabilities"` (flat string array) and `"count"` are the canonical fields.
Enriched fields (`science`, `infrastructure`, `composition`, `operation_dependencies`, `cost_estimates`) retained for domain-specific consumers.

### Registry Sync: 452

- Cross-sync test now asserts `canonical.len() >= 452`
- `primal.list` added to `methods.rs` as `PRIMAL_LIST` constant
- airSpring does NOT serve `primal.list` (biomeOS serves it) — we sync against it

### Not Yet Applied

- **`--provenance-dir`**: Will wire when E3 LTEE reproduction starts (Thread 5+6 capture)
- **`s_schema_standard` scenario**: Considered for future — airSpring CI cross-sync tests serve the same purpose

---

## Verification

```
cargo test --features local,testutil --lib          → 1,057 passed, 0 failed
cargo test --features local,testutil --test capability_cross_sync → 3 passed
cargo test (forge)                                  → 62 passed
cargo clippy (pedantic+nursery)                     → 0 new warnings
```

---

**Submitted by**: airSpring v0.10.0
**For**: primalSpring Wave 20 review
