# sweetGrass v0.7.45 — Wave 76 Cross-Gate Attribution Schema

**Date**: 2026-06-03  
**FRAGO**: wave76-parity-sprint-provenance  
**Gate**: strandGate  
**Version**: v0.7.44 → v0.7.45  

---

## Mission

Define cross-gate attribution schema for multi-gate provenance braids.
When Gate A's bearDog trusts Gate B's key, that's a PROV-O `wasAttributedTo`
relationship spanning gate boundaries. sweetGrass now models this.

## Schema Additions

### CrossGateAttribution (new struct)

```rust
pub struct CrossGateAttribution {
    pub origin_gate: Arc<str>,       // Gate originating the event
    pub target_gate: Arc<str>,       // Gate receiving/verifying
    pub trust_event: CrossGateTrustEvent,
    pub origin_agent: Did,           // Signer on origin gate
    pub target_agent: Option<Did>,   // Verifier on target gate
    pub family_id: Option<String>,   // BTSP family binding
}
```

### CrossGateTrustEvent (new enum)

`KeyExchange`, `TrustIssuerRegistered`, `GateEnrollment`, `FamilyEnrollment`,
`CrossGateAttestation`, `MeshJoin`, `MeshLeave`

### EcoPrimalsAttributes — new field

`source_gate: Option<Arc<str>>` — gate identity alongside `source_primal`

### BraidMetadata — new field

`cross_gate: Option<CrossGateAttribution>` — typed cross-gate context

### ActivityType — new variants

`KeyExchange`, `TrustEstablishment`, `GateEnrollment`, `CrossGateAttestation`

### Witness tier constants

`WITNESS_TIER_GATEWAY`, `WITNESS_TIER_ANCHOR`, `WITNESS_TIER_EXTERNAL`
`Witness::from_gateway_ed25519()` constructor

### QueryFilter

`source_gate: Option<Arc<str>>` + `with_source_gate()` across all backends

### PROV-O Export

`sourceGate`, `crossGateAttribution`, `originGate`, `targetGate`, `trustEvent`,
`originAgent`, `targetAgent`, `familyId` terms added to JSON-LD context

## Tests Added

| Test | Coverage |
|------|----------|
| `test_create_cross_gate_trust_braid` | Key exchange cross-gate braid CRUD |
| `test_create_gate_enrollment_braid` | Gate enrollment with family_id |
| `test_cross_gate_witness_gateway_tier` | Gateway-tier witness persistence |
| `test_query_by_source_gate` | source_gate filter across backends |
| `test_cross_gate_activity_types` | KeyExchange activity type CRUD |
| `test_export_cross_gate_attribution` | PROV-O JSON-LD export with full CGA |
| `test_export_cross_gate_minimal` | Minimal CGA (no target_agent/family) |
| `test_context_includes_cross_gate_terms` | JSON-LD context vocabulary |

## Metrics

| Metric | v0.7.44 | v0.7.45 |
|--------|---------|---------|
| Tests | 1,588 | 1,602 |
| LOC | 57,176 | 59,957 |
| Source files | 195 | 206 |
| Clippy warnings | 0 | 0 |
| Methods | 39 | 39 |

## Files Changed

### New
- `crates/sweet-grass-core/src/braid/cross_gate.rs`
- `crates/sweet-grass-service/src/handlers/jsonrpc/tests_cross_gate.rs`

### Modified (schema)
- `crates/sweet-grass-core/src/braid/types.rs` — `source_gate` on ecop, `cross_gate` on metadata
- `crates/sweet-grass-core/src/braid/mod.rs` — re-exports
- `crates/sweet-grass-core/src/braid/builder.rs` — `cross_gate()` setter
- `crates/sweet-grass-core/src/activity/mod.rs` — trust activity types
- `crates/sweet-grass-core/src/dehydration.rs` — tier constants, gateway constructor

### Modified (handlers)
- `crates/sweet-grass-service/src/handlers/jsonrpc/braid.rs` — `cross_gate`/`source_gate` params
- `crates/sweet-grass-service/src/handlers/jsonrpc/mod.rs` — test module registration

### Modified (query/store)
- `crates/sweet-grass-store/src/traits/mod.rs` — `source_gate` filter
- `crates/sweet-grass-store/src/memory/filter.rs` — source_gate matching
- `crates/sweet-grass-store-nestgate/src/store.rs` — source_gate matching
- `crates/sweet-grass-store-redb/src/store/mod.rs` — source_gate filter
- `crates/sweet-grass-store-postgres/src/store/mod.rs` — source_gate SQL filter
- `crates/sweet-grass-query/src/provo/mod.rs` — cross-gate PROV-O export

### Modified (docs/specs)
- `specs/DATA_MODEL.md` — v0.4.0, cross-gate schema, JSON-LD example
- `README.md`, `CONTEXT.md`, `ROADMAP.md`, `sporeprint/validation-summary.md`

## Bincode Lesson Reinforced

`QueryFilter::source_gate` initially had `skip_serializing_if` — broke tarpc Bincode.
Fixed by using `#[serde(default)]` only. Same pattern as v0.7.44 lesson.

## Coordination

- rhizoCrypt and loamSpine need matching cross-gate event schemas
- bearDog w135 TrustedIssuerRegistry is the trust source; sweetGrass records, not verifies
- Gate identity flows: bearDog → primal handler → sweetGrass braid with `cross_gate` metadata

## ACK

FRAGO wave76-parity-sprint-provenance — sweetGrass portion COMPLETE.
