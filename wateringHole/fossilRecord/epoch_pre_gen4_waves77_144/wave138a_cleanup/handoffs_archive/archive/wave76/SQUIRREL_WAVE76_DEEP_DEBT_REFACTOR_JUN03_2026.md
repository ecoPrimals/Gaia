# Squirrel Wave 76 — Deep Debt Refactor + Hygiene

**Date**: June 3, 2026
**Version**: v0.1.0 (commit bd2ff660)
**Owner**: eastGate
**Context**: FRAGO wave76-parity-sprint-eastgate-tools P3 + deep debt execution

## What Was Delivered

### Smart Refactoring (>800L file elimination)

**`provider_trait.rs` (983→728L, -26%)**:
- Extracted generic `rpc_roundtrip<S: AsyncRead+AsyncWrite+Unpin>` — eliminates
  duplicated Unix/TCP I/O code (~40 lines) with a single transport-agnostic function
- Extracted `workload_status_from_wire()` — eliminates duplicated `match status_str`
  blocks across `get_workload_status` and `list_workloads`
- Moved 260-line test module to dedicated `provider_trait_tests.rs`
- Fixed `#[allow(clippy::...)]` → `#[expect(clippy::..., reason = "...")]`

**`router.rs` (803→~810L, structural improvement)**:
- Extracted `providers_for_capability()` generic method eliminating duplicated
  image/text provider filter+map+log pattern
- Added `Send + Sync` bounds correctly for async compatibility

### Dependency Hygiene

- **Removed `mockall`** from 6 crates + workspace `Cargo.toml` — declared as
  dev-dependency but **never imported** in any `.rs` file. Reduces compilation
  time and dependency surface.

### Hardcoding Evolution

- `"127.0.0.1"` in `jsonrpc_server.rs` TCP bind → `universal_constants::network::LOCALHOST_IPV4`

### Mesh Env Var Coverage (session A)

| Module | Constants Added |
|--------|---------------|
| `primals` | `SONGBIRD_FEDERATION_ENABLED`, `SONGBIRD_FEDERATION_PORT`, `SONGBIRD_FEDERATION_BIND`, `SONGBIRD_PEERS`, `SONGBIRD_SERVICE_CONFIG_PATH` |
| `btsp` | `BIRDSONG_KEY_LABEL`, `LINEAGE_ROOT_PREFIX`, `LINEAGE_MAX_DEPTH` |
| `federation` | `ENABLED` (legacy alias) |
| `ecosystem` | `BIOMEOS_SOCKET_DIR` |

### Deprecated Constant Migration (session A)

Replaced all 6 usages of `BIOMEOS_SOCKET_FALLBACK_DIR` with `get_socket_dir()`:
- `capabilities/discovery.rs`, `discovery_service.rs`, `lifecycle.rs` (2×)
- `universal-patterns/transport/discovery.rs`, `ipc_client/discovery.rs`, `registry/discovery.rs`

## Audit Results

| Dimension | Status |
|-----------|--------|
| `unsafe` blocks | **0** — workspace `forbid(unsafe_code)` |
| Production mocks | **0** — all behind `#[cfg(test)]` |
| `todo!()`/`unimplemented!()` | **0** |
| `TODO`/`FIXME`/`HACK` in code | **0** |
| Hardcoded primal names | **0 raw** — all behind constants or deprecated serde aliases |
| Files >800L (prod) | **0** — `env_vars.rs` (1091L) excluded as flat registry |
| Stale scripts/debris | **0** — no `.sh`, `.py`, `.bak`, `.old` files |
| Tracked credentials | **0** — `.env` and `mcp-config.env` both gitignored |

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --all` | PASS |
| `cargo clippy --workspace` | 0 warnings (pedantic + nursery + cargo) |
| `cargo test --workspace --lib --tests` | 7,098 passed / 0 failed |
| `cargo deny check` | advisories ok, bans ok, licenses ok, sources ok |

## Remaining (non-blocking, team-cadence)

| Item | Priority | Notes |
|------|----------|-------|
| `router.rs` discovery extraction | LOW | `new_with_discovery` has `#[expect(too_many_lines)]`; partially extracted to `router_init.rs` |
| `bincode` 1.x unmaintained | LOW | Transitive via `tarpc`; tracked in `deny.toml` |
| Doctest linking (musl) | LOW | Toolchain issue: static-pie musl doctests fail at link stage |

## For primalSpring

Squirrel is stadial-current. P3/P4 items all resolved. Zero debt markers.
Next natural evolution: live provider E2E in compositions (Wave 55+ target).
