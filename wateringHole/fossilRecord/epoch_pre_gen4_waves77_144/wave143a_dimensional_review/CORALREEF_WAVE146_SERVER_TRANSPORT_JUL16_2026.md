<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 146 Server-Side Transport Abstraction (July 16, 2026)

## Commit

`e006441` on `main`

## Summary

Completes Silicon Atheism Phase 2 transport abstraction for coralReef.
Wave 144 centralized client-side connects; Wave 146 centralizes server-side
binds and de-cfg-gates orchestration. All platform-specific socket code
(client + server) now lives in `local_transport.rs`.

## Changes

### `local_transport.rs` — Server-Side API

| Function | Purpose |
|----------|---------|
| `prepare_local_bind(path)` | Create parent dirs, remove stale socket file |
| `bind_local(path)` | `UnixListener::bind` on Unix, `Unsupported` on non-Unix |
| `path_in_ecosystem_namespace(path)` | Check if path uses ecosystem directory segment |
| `install_capability_symlink(path)` | Create `{domain}.sock` → instance symlink (moved from `unix_jsonrpc.rs`) |

### `BoundAddr::Unix` → `BoundAddr::Local`

Enum variant always compiled. Protocol string unchanged (`"unix"`) for
backward compatibility. Match arms no longer require `#[cfg(unix)]`.

### De-cfg-gated Modules

| File | Before | After |
|------|--------|-------|
| `unix_jsonrpc.rs` | `#[cfg(unix)] mod inner { ... }` wrapping 550 lines | Module always compiles; `start_unix_jsonrpc_server` returns `Unsupported` on non-Unix |
| `tarpc_transport.rs` | `#[cfg(unix)] start_tarpc_unix_server` | Function always available; non-Unix returns `Unsupported` via `IpcError::Tarpc` |
| `ipc/mod.rs` | `#[cfg(unix)] mod unix_jsonrpc` + 3 re-exports | All de-cfg-gated; `default_tarpc_bind()` always returns `unix://` path |
| `main.rs` | 12 `#[cfg(unix)]`/`#[cfg(not(unix))]` blocks | All removed — unified `Option<PathBuf>` flow |

### `main.rs` Orchestration

`ResolvedBind::UdsOnly` no longer has separate cfg arms. On non-Unix, the
`start_unix_jsonrpc_server` call returns `Unsupported`, which the caller
handles as a fatal error (UDS-only was explicitly requested). In `Both`
mode, local socket failure degrades gracefully with `tracing::warn`.

## Quality Gates

- `cargo clippy --all-features -- -D warnings` — PASS (zero warnings)
- `cargo check --target x86_64-pc-windows-gnu` — PASS (zero warnings)
- `cargo test --all-features` — PASS (3647 total, 0 failures, 4 ignored)

## Remaining Work (Phase 2)

| Item | Status |
|------|--------|
| Client-side `connect_local` | DONE (Wave 144) |
| Server-side `bind_local` | **DONE (Wave 146)** |
| Orchestration de-cfg-gate | **DONE (Wave 146)** |
| Signal handling | Already abstracted (no change needed) |
| Function rename (`unix_` → `local_`) | Deferred — backward-compatible |
| `LocalListener` newtype (future) | Deferred — awaiting ecosystem `TransportEndpoint` trait definition |
