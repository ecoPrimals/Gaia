# rhizoCrypt — Wave 133e-b Handoff: Vendor Decoupling

**Date**: Jul 7, 2026 | **Commit**: `2d9c146` | **Tests**: 1,894 (+25)

## Summary

Systematic elimination of vendor-named types from rhizoCrypt's public API:

### Vendor Decoupling (P0 + P1)
- `SongbirdClient/Config/Rpc` → `DiscoveryClient/Config/Rpc` with `#[deprecated]` aliases
- `MockSongbirdServer` → `MockDiscoveryServer`
- `songbird_rpc`/`songbird_types` re-exported as `discovery_rpc`/`discovery_types`
- `BearDogHttpClient` → `SigningHttpClient`, `ToadStoolHttpClient` → `ComputeHttpClient`
- `NestGateHttpClient` → `StorageHttpClient`, `LoamSpineHttpClient` → `PermanentHttpClient`
- `LoamSpineRpc` → `PermanentStorageRpc`
- All error types renamed accordingly

### Architecture
- `transport_tests.rs` (823L, last >800L file) split into 6 domain submodules
- Zero files now exceed the 800L threshold

### Coverage (+25 tests)
- New `niche_derived_tests.rs`: `normalize_method`, `cost_tier`, `health_liveness`,
  `health_readiness`, `identity_get`, `announce_payload`, `mcp_tools`, `capability_list`,
  `method_locality_counts`, `SEMANTIC_MAPPINGS`, `CONSUMED_CAPABILITIES`, `DEPENDENCIES`

### Gates
- `cargo fmt` — clean
- `cargo clippy` — 0 warnings (pedantic + nursery)
- `cargo doc` — 0 warnings
- `cargo test` — 1,894 passed, 0 failed
- 213 `.rs` files, ~61,344 lines

### Remaining Vendor Coupling
- Module directory still named `songbird/` (internal protocol adapter — acceptable)
- `SONGBIRD_*` env var fallbacks still exist with deprecation logging
- File names `beardog_http.rs` etc. retained (internal adapter naming — low priority)
