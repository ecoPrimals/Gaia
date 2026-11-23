# sweetGrass v0.7.44 — PROV-O Schema Completeness + Privacy Edge Cases + Store Parity

**Wave 69 | June 2, 2026 | strandGate**

## Summary

Wave 69 targets from primalSpring audit: W3C PROV-O field coverage, privacy
edge case testing, and store convergence parity. All three P3 targets resolved.

## Changes

### W3C PROV-O Data Model Completeness

1. **`invalidated_at_time: Option<Timestamp>`** on Braid — entity lifecycle /
   supersession timestamp per `prov:invalidatedAtTime`.

2. **`alternate_of: Vec<EntityReference>`** on Braid — content convergence
   via `prov:alternateOf` (CONTENT_CONVERGENCE.md Phase 3).

3. **PROV-O export ID consistency** — `wasDerivedFrom` and `used` references
   now emit `urn:braid:{hash}` URIs matching entity `@id` format.
   `EntityReference::ById` references are no longer silently dropped.

4. **Delegation export** — `prov:actedOnBehalfOf` emitted on Activity
   associations when `on_behalf_of` is set.

5. **`@type` mapping** — export maps `BraidType` to PROV types (Entity,
   Activity, Agent, Collection) instead of hardcoded `"Entity"`.

6. **New JSON-LD context terms** — `invalidatedAtTime`, `alternateOf`,
   `Collection` added to PROV-O export context.

### Privacy Edge Case Testing

7. **8 new privacy tests** covering all 5 visibility levels:
   - Authenticated: denied without bearer token, allowed with any token
   - Private: denied wrong DID, allowed owner DID
   - Encrypted: denied without DID, allowed owner DID
   - Public: always accessible
   - No privacy metadata: backward compatible (always accessible)

### Store Convergence Parity

8. **NestGate `get_all_by_hash` override** — scans all keys and returns all
   matching braids. Was using trait default (single result via `get_by_hash`).
   Convergence test added.

### Bincode Compatibility Fix

9. **Removed `skip_serializing_if`** on new Braid fields — incompatible with
   Bincode positional encoding used by tarpc transport. `#[serde(default)]`
   only ensures both JSON and Bincode roundtrips work.

## PROV-O Coverage Status

After v0.7.44, sweetGrass covers:

| PROV-O concept | Schema | Export |
|----------------|--------|--------|
| Entity @id, @type | Yes | Yes (mapped from BraidType) |
| wasGeneratedBy | Yes | Yes (ID ref + node) |
| wasDerivedFrom | Yes | Yes (consistent URIs) |
| wasAttributedTo | Yes | Yes (DID string) |
| generatedAtTime | Yes | Yes (ISO 8601) |
| invalidatedAtTime | Yes (new) | Yes (new) |
| alternateOf | Yes (new) | Yes (new) |
| Activity associations | Yes | Yes (with delegation) |
| Activity time fields | Yes | Yes |

Remaining gaps (v0.8.0): `specializationOf`, `wasInformedBy` (activity chains),
`prov:generated` (inverse link), Bundle containers, Agent nodes in graph.

## Metrics

| Metric | v0.7.43 | v0.7.44 |
|--------|---------|---------|
| Tests | 1,573 | 1,588 |
| LOC | 56,673 | 57,176 |
| Methods | 39 | 39 |
| Clippy warnings | 0 | 0 |

## Verification

```
cargo clippy --all-features  # 0 warnings
cargo test --all-features    # 1,588 passed, 0 failed
```
