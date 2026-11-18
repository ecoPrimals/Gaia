# rhizoCrypt — Wave 142b: Transport Phase 2 + SessionTreeHash

**Date**: Jul 16, 2026 | **Commit**: `614ef3e`
**Tests**: 1,911 → 1,919 (+8) | **Lines**: ~62,103

## Changes

### Transport Phase 2: Structured Adapter Dispatch

Added `AdapterFactory::from_transport(&TransportEndpoint)` — creates protocol
adapters directly from the ecosystem's structured `TransportEndpoint` enum
instead of re-parsing string representations.

**Before** (Phase 1): Discovery yields `TransportEndpoint`, client calls
`.to_string()` → `AdapterFactory::create(&str)` re-parses the string.

**After** (Phase 2): Discovery yields `TransportEndpoint`, client calls
`AdapterFactory::from_transport(&endpoint)` — direct dispatch, no round-trip.

All 5 capability clients updated: signing, permanent, storage, compute,
provenance. `with_endpoint(&str)` methods unchanged for explicit overrides.

### SessionTreeHash — CAC Primitive (FRAGO)

New `SessionTreeHash` newtype wrapping `MerkleRoot`:
- Content-addressable cache key for entire session DAG state
- `SessionTreeHash::compute(vertices)` for direct computation
- `RhizoCrypt::session_tree_hash(session_id)` for runtime access
- `ZERO` constant, `from_root`, `root`, `as_bytes` accessors
- Re-exported from `rhizo_crypt_core::SessionTreeHash`

Enables duplicate detection and cache keying without full vertex comparison.

### Clone Optimization

Destructured `MergeRequest` in `service_branch_ops.rs` to iterate metadata
by value, eliminating unnecessary `String::clone()` calls on the merge
hot path. `parents.clone()` retained (needed for both builder and merge call).

### Integration Trait Wiring (142b-2, `9c3789a`)

All 3 capability provider traits now have production `impl` blocks:
- `impl SigningProvider for SigningClient` (6 methods)
- `impl PayloadStorageProvider for StorageClient` (3 methods)
- `impl PermanentStorageProvider for PermanentStorageClient` (5 methods)

Enables `Arc<dyn SigningProvider>` injection and mock substitution for
production paths (dehydration, attestation) without feature flags.

### Legacy Deprecation (142b-2)

- `READ_TIMEOUT` / `WRITE_TIMEOUT` constants — `#[deprecated]` (dead)
- `TransportHint` enum + `preferred_transport()` — `#[deprecated]`
- Vendor wire types narrowed to `pub(crate)` in 4 HTTP client modules

## Remaining Work

| Item | Status |
|------|--------|
| `TransportHint` removal (deprecated this wave) | Follow-up |
| `MeshRelay` routing implementation | Phase 3 |
| `dehydration_ops.rs` → trait-based dispatch | Follow-up |
| Incremental `SessionTreeHash` on append | Follow-up |
| `CircuitBreaker` / `RetryPolicy` wiring in adapters | Follow-up |

## Gate Results

- `cargo fmt --all --check` — clean
- `cargo clippy --workspace --all-features -- -D warnings` — zero warnings
- `cargo test --workspace --all-features` — 1,919 passed, 0 failed
- `RUSTDOCFLAGS="-D warnings" cargo doc` — clean
