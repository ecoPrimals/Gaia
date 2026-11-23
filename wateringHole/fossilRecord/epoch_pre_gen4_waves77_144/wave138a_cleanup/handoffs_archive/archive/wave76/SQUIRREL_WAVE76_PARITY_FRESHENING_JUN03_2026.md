# Squirrel Wave 76 Parity Sprint — Freshening

**Date**: June 3, 2026
**Version**: v0.1.0 (commit 3c8beda5)
**Owner**: eastGate
**FRAGO**: wave76-parity-sprint-eastgate-tools — P3

## What Was Delivered

### Mesh Env Var Coverage (P0 for this sprint)

Added to `universal-constants/src/env_vars.rs`:

| Module | Constant | Env Var |
|--------|----------|---------|
| `primals` | `SONGBIRD_FEDERATION_ENABLED` | `SONGBIRD_FEDERATION_ENABLED` |
| `primals` | `SONGBIRD_FEDERATION_PORT` | `SONGBIRD_FEDERATION_PORT` |
| `primals` | `SONGBIRD_FEDERATION_BIND` | `SONGBIRD_FEDERATION_BIND` |
| `primals` | `SONGBIRD_PEERS` | `SONGBIRD_PEERS` |
| `primals` | `SONGBIRD_SERVICE_CONFIG_PATH` | `SONGBIRD_SERVICE_CONFIG_PATH` |
| `federation` | `ENABLED` | `FEDERATION_ENABLED` (legacy alias) |

Context: biomeOS v4.03 renamed `SONGBIRD_MESH_ENABLED` → `SONGBIRD_FEDERATION_ENABLED`.
Squirrel now covers the full Songbird federation surface for centralized env access.

### BTSP Trust Env Vars

| Module | Constant | Env Var |
|--------|----------|---------|
| `btsp` | `BIRDSONG_KEY_LABEL` | `BTSP_BIRDSONG_KEY_LABEL` |
| `btsp` | `LINEAGE_ROOT_PREFIX` | `BTSP_LINEAGE_ROOT_PREFIX` |
| `btsp` | `LINEAGE_MAX_DEPTH` | `BTSP_LINEAGE_MAX_DEPTH` |

Context: BearDog Wave 119 S4 auth config added these for trust chain derivation.

### Deprecated Constant Migration

Replaced all 6 usages of `BIOMEOS_SOCKET_FALLBACK_DIR` (deprecated) with
`get_socket_dir()` across 5 files. Eliminates hardcoded `/tmp/biomeos` path.
Socket resolution now follows: `$BIOMEOS_SOCKET_DIR` → `$XDG_RUNTIME_DIR/biomeos` → `{temp_dir}/biomeos`.

### Hygiene

- Added `#[must_use]` to `find_biomeos_socket()` and `resolve_neural_api_socket()`
- Centralized `BIOMEOS_SOCKET_DIR` env var constant in ecosystem module
- Updated test for dynamic socket dir resolution

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --all` | PASS |
| `cargo clippy --workspace` | 0 warnings |
| `cargo test --workspace --lib --tests` | 7,097 passed / 0 failed |

## Files Changed

11 files, +104 / -56 lines.

## No Blocking Issues

Squirrel is stadial-current. P3 complete.
