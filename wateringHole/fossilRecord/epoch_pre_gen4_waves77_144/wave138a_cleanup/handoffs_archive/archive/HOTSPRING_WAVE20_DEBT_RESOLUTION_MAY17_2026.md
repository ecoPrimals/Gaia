# hotSpring — Wave 20 Debt Resolution (May 17, 2026)

**Spring:** hotSpring v0.6.32
**Date:** May 17, 2026
**Trigger:** primalSpring `WAVE20_DEBT_RESOLUTION_MAY17_2026.md` audit
**Tests:** 596 (default lib) / 1,045 (barracuda-local lib) — all pass, zero clippy

---

## Debt Items Resolved

### 1. Fossilized RPC — canonical `capability.list` envelope

`barracuda/src/bin/_fossilized/hotspring_primal.rs` now returns the Wave 20
canonical shape:

```rust
"capabilities.list" | "capability.list" => DispatchResult::Ok(json!({
    "capabilities": state.capabilities,
    "count": state.capabilities.len(),
    "primal": "hotspring",
})),
```

The library-side `capabilities_list_response()` in `niche/tables.rs` already
had this shape; this aligns the fossilized server binary.

### 2. `nest.commit` — candidate → adopted drift fixed

Removed `nest.commit` from candidate lists in:
- `docs/PRIMAL_GAPS.md` (GAP-HS-103 signal candidates section)
- `wateringHole/handoffs/HOTSPRING_WAVE17_SIGNAL_ADOPTION_HANDOFF_MAY16_2026.md`
- `wateringHole/handoffs/HOTSPRING_DOC_EVOLUTION_UPSTREAM_HANDOFF_MAY16_2026.md`

Only `nest.store` remains as candidate (awaiting nestGate evolution).

Signal adoption status is now consistent across all surfaces:

| Signal | Status |
|--------|--------|
| `primal.announce` | Adopted (Wave 17) |
| `node.compute` | Adopted (Wave 17) |
| `tower.publish` | Adopted (Wave 17) |
| `nest.commit` | Adopted (Wave 20) |
| `nest.store` | Candidate |

### 3. `commit_provenance()` documented as scaffolding

Added wiring status documentation to `dag_provenance.rs`:
- Ready for integration after `DagSession::dehydrate()`
- Natural wiring points: Titan V pipeline session finalization,
  `validate_*` binaries with full DAG lifecycle
- Not yet called — will be wired when live experiments produce
  provenance worth committing to the ledger

### 4. Test count clarification

- **Lib tests:** 596 (default) / 1,045 (barracuda-local) — verified, unchanged
- **Workspace `cargo test`:** Compile errors in biomeGate binaries due to
  feature-gate debt (`barracuda::device`, `barracuda::tensor`, etc. referenced
  without `required-features = ["barracuda-local"]` in `[[bin]]` entries)
- primalSpring's cited 1,607 figure includes binary tests — valid when
  biomeGate's feature gates are fixed

**Upstream ask for biomeGate:** Add `required-features = ["barracuda-local"]`
to `[[bin]]` entries that import `barracuda-local`-gated modules, so `cargo test`
compiles cleanly without feature flags.

---

## Files Changed

- `barracuda/src/bin/_fossilized/hotspring_primal.rs` (canonical envelope)
- `barracuda/src/dag_provenance.rs` (scaffolding doc)
- `docs/PRIMAL_GAPS.md` (GAP-HS-106 + nest.commit drift fix)
- `CHANGELOG.md`
- `wateringHole/handoffs/HOTSPRING_WAVE17_SIGNAL_ADOPTION_HANDOFF_MAY16_2026.md`
- `wateringHole/handoffs/HOTSPRING_DOC_EVOLUTION_UPSTREAM_HANDOFF_MAY16_2026.md`
