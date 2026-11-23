# hotSpring — Wave 20 Schema Standardization (May 16, 2026)

## Summary

hotSpring has absorbed primalSpring Wave 20 schema standardization:
`capability.list` canonical envelope, `primal.list` registry sync,
`nest.commit` signal dispatch, and `s_schema_standard` validation scenario.

---

## Changes

### capability.list canonical envelope

`capabilities_list_response()` in `niche/tables.rs` returns the canonical
Wave 20 shape:

```json
{
  "capabilities": ["physics.nuclear_eos", "compute.dispatch", ...],
  "count": 47,
  "primal": "hotspring"
}
```

The `capabilities` array was already correct (flat string array). Added
`count` (array length) and `primal` (niche identity) per Wave 20 spec.

### primal.list registry sync

Added `primal.list` as a routed capability in `capability_registry.toml`
(biomeOS-served, domain `primal`). Corresponding entry added to
`ROUTED_CAPABILITIES` in `niche/tables.rs`. Cross-sync test validates
presence against primalSpring registry.

### nest.commit signal dispatch

`commit_provenance()` in `dag_provenance.rs` dispatches the `nest.commit`
signal via `signal.dispatch`. biomeOS decomposes into:
`event.append` → `crypto.sign` → `content.put` → `session.commit` → `braid.create`.

Falls back to direct `ledger.record` + `attribution.braid` multi-call for
pre-v3.57 biomeOS (same pattern as `tower.publish` fallback).

Signal promoted from candidate to adopted in `[signals]` section.

### s_schema_standard scenario

New validation scenario validates:
- capability.list response shape (array, count, primal fields)
- Signal registry presence (3 adopted, 1 candidate)
- Niche identity constants (name, domain, local/routed capabilities)

### Metrics

| Metric | Before | After |
|--------|--------|-------|
| Lib tests (default) | 595 | **596** |
| Lib tests (barracuda-local) | 1,041 | **1,045** |
| Scenarios (default) | 17 | **18** |
| Adopted signals | 2 | **3** |
| Candidate signals | 2 | **1** |
| Clippy warnings | 0 | **0** |

---

## Wave 20 Checklist Status

- [x] `capability.list` canonical envelope (`capabilities` + `count` + `primal`)
- [x] Registry sync target: 452 (`primal.list` added)
- [x] `nest.commit` signal dispatch (with fallback)
- [x] Schema-standard drift check scenario
- [ ] `--provenance-dir` for Thread 10 (optional — deferred)
