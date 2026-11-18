# biomeOS v3.92 — Wave 70 Handoff

**Date**: 2026-06-02
**Commit**: d0f168b8
**Author**: southGate

## Summary

Wave 70 focused on three deep-debt vectors: eliminating duplicate family_id
helpers, splitting the resources.rs type file, and massively expanding
environment variable SSOT coverage.

## Changes

### 1. Family ID SSOT Unification
- **model_cache/types.rs**: Removed duplicate `resolve_family_id_from_env()`.
  Now calls canonical `biomeos_core::family_discovery::get_family_id()`.
- **spore/documentation.rs**: Removed trivial `Spore::resolve_family_id()`
  wrapper that just delegated to the same canonical function.
- **graph/node_handlers.rs**: Improved `resolve_family_id(env)` to check
  `FAMILY_ID` before `FAMILY_ID_LEGACY` for correct precedence.

### 2. resources.rs Split (777 → 437 lines)
- Extracted 335-line `#[cfg(test)] mod tests` to `resources_tests.rs`
  via `#[path]` attribute. 29 tests verified passing.

### 3. env_config::vars SSOT Expansion (+23 constants, 24 call sites)
- **New constants**: `PRIMAL_BINARY`, `PRIMAL_SOCKET_PATH`, `PRIMAL_SOCKET`,
  `PRIMAL_ID`, `PRIMAL_NAME`, `PRIMAL_HTTP_PORT`, `AI_DEFAULT_MODEL`,
  `AI_HTTP_PROVIDERS`, `SPORE_ROOT`, `PLASMODIUM_PEERS`, `MCP_PORT`,
  `DISCOVERY_SOCKET_LEGACY`, `JWT_SECRET_LEGACY`, `FAMILY_SEED_LEGACY`,
  `MDNS_DISCOVERED_ENDPOINT`, `BROADCAST_DISCOVERED_ENDPOINT`,
  `MULTICAST_DISCOVERED_ENDPOINT`, `SECURITY_ENDPOINT`, `TEST_BIND`,
  `TEST_PORT`, `BIOMEOS_DISCOVERY_ENDPOINT`, `ECOPRIMAL_PREFIX`,
  `ECOPRIMAL_CONFIG_DIR`
- **Wired across**: biomeos-core (8 files), biomeos-types (3 files),
  biomeos-api, biomeos-atomic-deploy (4 files), biomeos-graph,
  biomeos-federation, biomeos (nucleus.rs)

### 4. Error Context Evolution
- `capability_translation/mod.rs`: Converted two `map_err(|e| anyhow!(...))` to
  idiomatic `.context()` calls with `anyhow::Context`.

## Verification
- `cargo check --workspace`: PASS
- `cargo clippy --workspace`: 0 warnings
- `cargo test --workspace`: 1316 pass, 4 known flaky (neural_router::discovery)
