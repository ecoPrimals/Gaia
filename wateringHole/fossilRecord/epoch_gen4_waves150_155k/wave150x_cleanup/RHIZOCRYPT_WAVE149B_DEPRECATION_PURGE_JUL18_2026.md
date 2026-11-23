# rhizoCrypt — Wave 149b Handoff

**Date**: Jul 18, 2026  
**Commit**: `4f5008e`  
**Tests**: 1,878 | **Coverage**: 93.83% | **Files**: 223 `.rs` | **Lines**: ~61,489

## Security Fix

- **RUSTSEC-2026-0204**: `crossbeam-epoch` 0.9.18→0.9.20 (dev-only via criterion).
  `cargo deny` now fully clean.

## Deprecation Purge (zero deprecated API surface)

All items deprecated with `since = "0.14.18"` in Wave 142b/143b have been
deleted. Zero production callers existed at removal time.

| Deleted | Location |
|---------|----------|
| `with_endpoint(&str)` | 5 capability clients (signing, permanent, storage, compute, provenance) |
| `AdapterFactory::create(&str)` | `adapters/mod.rs` |
| `SongbirdClient` / `SongbirdConfig` | `songbird/mod.rs` type aliases |
| `READ_TIMEOUT` / `WRITE_TIMEOUT` | `constants/ipc.rs` |

17 deprecated constructor tests deleted. Remaining tests migrated to
`discover()` + `TransportEndpoint` pattern.

## Dead Code Removal

- **`CircuitBreaker` / `RetryPolicy`** (`resilience.rs`, 305L, 10 tests) —
  deleted. Never used outside own module. Wiring would require adapter trait
  refactoring with no current callers. Error model mismatch across adapters
  (only `UnixSocketAdapter` uses structured `IpcErrorPhase`; others return
  generic integration errors).

## Architecture Splits

### `uds.rs` (623L) → `uds/` module

| File | Lines | Content |
|------|------:|---------|
| `uds/mod.rs` | 229 | Server struct, serve loop, socket prep, cleanup |
| `uds/connection.rs` | 361 | Per-connection handler, BTSP, mito-beacon, encrypted JSON-RPC |
| `uds/symlinks.rs` | 53 | Capability-domain symlink create/remove |

### `lib.rs` (622L) → 7 modules

| File | Lines | Content |
|------|------:|---------|
| `lib.rs` | 126 | Crate root, module declarations, types, re-exports |
| `startup.rs` | 290 | `run_server`, `serve_with_tcp`, readiness orchestration |
| `discovery.rs` | 87 | Discovery registration, manifest publishing |
| `client.rs` | 57 | `run_client` RPC operations |
| `uds.rs` | 49 | UDS listener setup |
| `config.rs` | 42 | Bind address resolution |
| `shutdown.rs` | 39 | Signal handling |

## Ecosystem GAPs

- **GAP-036 (socket naming)**: CLOSED — `family_scoped_socket_path` compliant
- **GAP-038 (stale UDS cleanup)**: CLOSED — `prepare_socket_path` + `cleanup_socket_at`

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,878 |
| Coverage | 93.83% |
| `.rs` files | 223 |
| Lines | ~61,489 |
| Max prod file | ~624 lines (store.rs) |
| Clippy | 0 warnings |
| `cargo deny` | CLEAN |
| Deprecated API | 0 items |
| Dead code | 0 modules |
| Prod unwrap | 0 calls |
| TODO/FIXME | 0 markers |
