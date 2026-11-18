# Squirrel Wave 78 Parity — Registry Convention Alignment

**Date**: June 5, 2026
**From**: squirrel (eastGate)
**Wave**: 78
**Priority**: Hygiene (optional)

## Summary

Squirrel's only Wave 78 parity item resolved: `capability_registry.toml` moved
from workspace root to `config/capability_registry.toml`, aligning with
ecosystem convention (biomeOS, petalTongue, sweetGrass pattern).

## Changes

| File | Change |
|------|--------|
| `config/capability_registry.toml` | Moved from root (git mv) |
| `crates/main/src/capabilities/registry.rs` | Updated `include_str!` path + test path |
| `crates/main/src/niche.rs` | Updated `include_str!` path in sync test |
| `crates/main/src/rpc/jsonrpc_server.rs` | Updated runtime file discovery paths |
| `README.md` | Updated link |
| `CURRENT_STATUS.md` | Updated references + changelog |
| `sporeprint/validation-summary.md` | Updated reference |
| `specs/development/AI_DEVELOPMENT_GUIDE.md` | Updated link |
| `specs/historical/mcp-protocol/MCP_INTEGRATION_GUIDE.md` | Updated reference |

## Verification

- `cargo test --workspace`: 7,098 passed / 0 failed
- `cargo clippy --workspace`: 0 warnings
- `cargo fmt --all`: clean
- Registry sync test (`capability_registry_toml_sync`): passing
- Registry load test (`test_load_real_file`): passing

## Status

**squirrel — CLEAN**. Zero parity items remaining. Wave 78 complete.

Commit: `6f298d1d` on `main`.
