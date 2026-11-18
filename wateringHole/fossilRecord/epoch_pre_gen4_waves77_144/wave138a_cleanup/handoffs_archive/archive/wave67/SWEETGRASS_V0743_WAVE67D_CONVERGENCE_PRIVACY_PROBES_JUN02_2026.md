# sweetGrass v0.7.43 — Content Convergence + Privacy Integration + Health Probes

**Wave 67d | June 2, 2026 | strandGate**

## Summary

Three structural evolutions: store backends achieve content convergence parity,
privacy module wired into braid CRUD with access enforcement, and health probes
evolved from stubs to live UDS socket interrogation.

## Changes

### Content Convergence (Store Parity)

1. **redb `MultimapTableDefinition`** — `BY_HASH` evolved from 1:1 `TableDefinition`
   to 1:many `MultimapTableDefinition`. Multiple braids sharing a content hash are
   now preserved. `remove_indexes` targets individual braid entries. `get_all_by_hash`
   override scans multimap and loads each braid. New test `test_content_convergence_get_all_by_hash`.

2. **postgres `get_all_by_hash`** — override uses `fetch_all` on the non-unique
   `data_hash` index (was `fetch_optional` returning one arbitrary row). Content
   convergence queries now return all matching braids.

### Privacy Integration

3. **`BraidMetadata.privacy`** — `Option<PrivacyMetadata>` field wired through types,
   builder, and handlers. `PrivacyLevel` variants: `Public`, `Authenticated`, `Private`,
   `Encrypted`, `AnonymizedPublic`.

4. **`BraidBuilder::privacy()`** — fluent setter for constructing braids with privacy
   constraints programmatically.

5. **`braid.create` privacy param** — accepts optional `privacy: { "visibility": "private" }`
   in JSON-RPC params.

6. **`braid.get` access enforcement** — `check_braid_privacy_access()` enforces:
   - Public/AnonymizedPublic: always allowed
   - Authenticated: requires bearer token
   - Private/Encrypted: requires caller DID matching owner or `has_access()` grant
   - Returns `PERMISSION_DENIED (-32001)` on denial

7. **Privacy serde evolution** — `PrivacyLevel` gains `rename_all = "snake_case"` for
   wire format; `PrivacyMetadata` gains `#[serde(default)]` for partial deserialization.

### Health Probes

8. **`health_detailed` live integration probes** — `check_integrations()` evolved from
   static `None` stubs to async UDS probes. Probes `security.sock` (signing),
   `provenance.sock` (anchoring), `discovery.sock`, `compute.sock` via JSON-RPC
   `health.liveness` with 2s timeout. Returns real `connected` / `error` status.

## Metrics

| Metric | v0.7.42 | v0.7.43 |
|--------|---------|---------|
| Tests | 1,571 | 1,573 |
| LOC | 56,356 | 56,673 |
| Methods | 39 | 39 |
| Clippy warnings | 0 | 0 |

## Files Modified

- `crates/sweet-grass-store-redb/src/lib.rs` — MultimapTableDefinition
- `crates/sweet-grass-store-redb/src/store/mod.rs` — multimap operations + get_all_by_hash
- `crates/sweet-grass-store-redb/src/store/tests/crud.rs` — convergence test
- `crates/sweet-grass-store-postgres/src/store/mod.rs` — get_all_by_hash override
- `crates/sweet-grass-core/src/braid/types.rs` — privacy field on BraidMetadata
- `crates/sweet-grass-core/src/braid/builder.rs` — privacy setter
- `crates/sweet-grass-core/src/privacy/mod.rs` — serde defaults + rename
- `crates/sweet-grass-service/src/handlers/jsonrpc/braid.rs` — privacy in create/get
- `crates/sweet-grass-service/src/handlers/jsonrpc/mod.rs` — caller_did helper
- `crates/sweet-grass-service/src/handlers/health/mod.rs` — async probes
- `crates/sweet-grass-service/src/handlers/health/tests.rs` — probe tests

## Migration Notes

- **redb databases**: Existing databases using old 1:1 `BY_HASH` table need recreation.
  Fresh deployments and test databases are unaffected.
- **Privacy field**: Backward compatible — `Option<PrivacyMetadata>` defaults to `None`.
  Existing braids without privacy metadata continue to work normally (treated as Public).

## Remaining Evolution Targets (v0.8.0)

- Wire `AnchorManager` into `anchoring.anchor` (requires loamSpine live)
- `auth.check` token verification via BearDog
- Wire `CircuitBreaker` around outbound integration clients
- `activities_for_braid` join table parity on redb/nestgate
- Privacy retention enforcement (background cleanup)
- Privacy-scoped query filters

## Verification

```
cargo clippy --all-features  # 0 warnings
cargo test --all-features    # 1,573 passed, 0 failed
```
