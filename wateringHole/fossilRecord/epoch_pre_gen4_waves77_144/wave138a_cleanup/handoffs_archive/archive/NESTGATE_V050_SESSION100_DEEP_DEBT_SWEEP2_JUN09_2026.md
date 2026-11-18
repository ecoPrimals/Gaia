# NestGate v0.5.0 — Session 100: Deep Debt Sweep Pass 2

**Date**: 2026-06-09
**Gate**: ironGate
**Commit**: c602ef0e

## Changes

### BLAKE3 Hash Centralization
- Extracted `content_hash_hex(data: &[u8]) -> String` as the single canonical CAS hashing entry point
- Extracted `content_cas_path(family_id, blake3_hex) -> PathBuf` as shared CAS path builder
- Both live in `storage_paths` module (upgraded to `pub(crate)` visibility)
- Eliminated `blake3::hash(&data).to_hex().to_string()` from 4 production files:
  - `content_handlers.rs` — content.put
  - `content_stream.rs` — chunked CAS upload finalize + empty upload
  - `content_federation_handlers.rs` — replicate.pull integrity verify
  - `external_handlers.rs` — storage.fetch_external
- Removed duplicate `content_cas_path()` from `content_stream.rs` (was identical to `content_key_path()`)
- `content_key_path()` now delegates to `content_cas_path()` (legacy alias)

### CONNECTION_IDLE_LIMIT Dedup
- Consolidated 3 identical `Duration::from_secs(300)` constants into `protocol::CONNECTION_IDLE_LIMIT`
- Consumers updated:
  - `unix_socket_server/connection.rs` — module-level constant → import
  - `isomorphic_ipc/server/mod.rs` — associated constant → references shared
  - `isomorphic_ipc/tcp_fallback.rs` — associated constant → references shared

### Coverage Sprint — 45 New Tests
- `template_storage::operations` (19): store/retrieve roundtrip, input validation (empty name/family/user), family isolation, list filtering (user, tags, niche), community top ranking (scoring, min usage, limit, niche filter), increment usage, success rate bounds
- `storage_paths` (13): content_hash_hex determinism/collision, content_cas_path layout, content_key_path delegation, extract_namespace validation (7 cases), manifest_path layout
- `validation::runner` (6): validate, validate_strict, generate_report across valid/invalid/warning configs
- `protocol` (1): CONNECTION_IDLE_LIMIT value assertion

## Validation
- 3,790+ tests passing (cargo test --workspace)
- 1 pre-existing failure: `test_universal_storage_bridge_list_pools` (known since Session 98)
- 0 clippy warnings (pedantic + nursery)
- 0 compile warnings

## Files Modified (14)
- `nestgate-rpc/src/rpc/unix_socket_server/storage_paths.rs` — +130 (helpers + tests)
- `nestgate-rpc/src/rpc/template_storage/operations.rs` — +452 (tests)
- `nestgate-config/src/config/validation/runner.rs` — +108 (tests)
- `nestgate-rpc/src/rpc/protocol.rs` — +16 (shared constant + test)
- `nestgate-rpc/src/rpc/content_stream.rs` — +2/−16 (imports, dedup)
- `nestgate-rpc/src/rpc/unix_socket_server/content_handlers.rs` — +1/−1
- `nestgate-rpc/src/rpc/unix_socket_server/content_federation_handlers.rs` — +2/−1
- `nestgate-rpc/src/rpc/unix_socket_server/external_handlers.rs` — +3/−2
- `nestgate-rpc/src/rpc/unix_socket_server/mod.rs` — visibility change
- `nestgate-rpc/src/rpc/unix_socket_server/connection.rs` — constant dedup
- `nestgate-rpc/src/rpc/isomorphic_ipc/server/mod.rs` — constant dedup
- `nestgate-rpc/src/rpc/isomorphic_ipc/tcp_fallback.rs` — constant dedup
- `CHANGELOG.md`, `sporeprint/validation-summary.md`

## Ecosystem Context
- Wave 102: NestGate transport evolution DONE (Session 97-98)
- No P0/P1 items for NestGate in current wave
- Coverage sprint ongoing (84% → 90% target from Wave 82c)
