<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef Wave 144 — Silicon Atheism Phase 2: Transport Abstraction (Client-Side)

**Date**: 2026-07-16  
**Commit**: `99444c5`  
**Status**: Client-side transport abstraction complete. Server-side scoped for next wave.

---

## Summary

Centralized all client-side UDS `connect` calls behind platform-dispatched
functions in a new `local_transport` module. Production code no longer touches
raw `UnixStream::connect` — platform dispatch is centralized in one module
per crate, following the petalTongue Phase 2 reference pattern (abstraction
over gating).

## Changes

| File | Before | After |
|------|--------|-------|
| `local_transport.rs` (NEW) | — | `connect_local()` (async) + `connect_local_sync()` — Unix UDS, non-Unix `Unsupported` |
| `ecosystem/mod.rs` | raw `UnixStream::connect` + `std::os::unix::net::UnixStream` | `local_transport::connect_local()` + `connect_local_sync()` |
| `ipc/btsp.rs` | raw `tokio::net::UnixStream::connect` | `local_transport::connect_local()` |
| `service/provenance.rs` | raw `std::os::unix::net::UnixStream::connect` | `local_transport::connect_local_sync()` |
| `primal-rpc-client/transport.rs` | duplicated `#[cfg(unix)]`/`#[cfg(not(unix))]` blocks (4 functions) | internal `connect_local()` helper, unified roundtrip functions (2 functions) |

## Quality Gates

- `cargo clippy --all-features -- -D warnings` — zero warnings
- `cargo check --target x86_64-pc-windows-gnu` — zero warnings
- `cargo test --all-features` — 3649+ tests, 0 failures
- `cargo build --release --bin coralreef` — clean

## Phase 2 Remaining (Server-Side — Next Wave)

| Component | File | Work |
|-----------|------|------|
| JSON-RPC listener | `ipc/unix_jsonrpc.rs` | Abstract `UnixListener::bind` behind `bind_local()` |
| tarpc listener | `ipc/tarpc_transport.rs` | Abstract `UnixListener::bind` behind `bind_local()` |
| Orchestration | `main.rs` | De-cfg `ResolvedBind::UdsOnly` / `Both` match arms |
| BoundAddr | `ipc/mod.rs` | Unify `#[cfg(unix)] Unix(PathBuf)` variant |
| Signal handling | `server_lifecycle.rs` | Abstract `tokio::signal::unix` (parallel track) |

## Cross-Primal Alignment

coralReef now follows the same pattern as petalTongue (`petal-tongue-platform`,
`1af1a98`). When the shared `primal-transport` / `membrane-transport` crate is
created, `connect_local()` implementations can migrate to it.
