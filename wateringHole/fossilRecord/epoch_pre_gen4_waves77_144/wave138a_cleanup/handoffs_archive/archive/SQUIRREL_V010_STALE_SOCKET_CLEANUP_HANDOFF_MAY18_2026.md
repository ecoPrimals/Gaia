# Squirrel v0.1.0 — Stale Socket Detection + Cleanup Handoff

**Date:** May 18, 2026
**From:** Squirrel team
**Ref:** primalSpring audit "Stale Socket Detection + Cleanup — All Teams"
**License:** AGPL-3.0-or-later

---

## Summary

Squirrel's response to the primalSpring stale-socket audit (southGate production
incident, 50+ stale biomeOS sockets). All three asks addressed:

1. **Server-side `unlink()` before `bind()`** — ALREADY IMPLEMENTED (`prepare_socket_path`)
2. **Shutdown cleanup** — ALREADY IMPLEMENTED (`cleanup_socket` via signal handlers)
3. **Consumer-side connect-probe liveness** — NEW, implemented this session
4. **PID file** — NEW, optional LOW ask, implemented this session

---

## What Was Already Present (Server-Side)

Squirrel already had stale socket prevention on the server side:

- `rpc::unix_socket::prepare_socket_path()` — removes any existing socket file
  before bind. Called before every `UnixListener::bind()` in `jsonrpc_server.rs`.
- `capabilities::lifecycle::cleanup_socket()` — removes socket file on SIGTERM,
  SIGINT, or Ctrl+C. Called from `install_signal_handlers()`.

No changes were needed for the "most important" ask.

---

## New Changes (Consumer-Side + PID File)

### 1. `socket_is_alive()` — Async Connect-Probe (discovery.rs)

```rust
pub async fn socket_is_alive(path: &Path) -> bool {
    tokio::time::timeout(
        Duration::from_millis(50),
        UnixStream::connect(path),
    ).await.is_ok_and(|r| r.is_ok())
}
```

Replaces `path.exists()` in:
- `try_explicit_env()` — env-var configured provider sockets
- `try_discovery_service()` — sockets returned by discovery service

### 2. `socket_is_alive_sync()` — Sync Connect-Probe (lifecycle.rs, discovery_service.rs)

```rust
fn socket_is_alive_sync(path: &Path) -> bool {
    if !path.exists() { return false; }
    std::os::unix::net::UnixStream::connect(path).is_ok()
}
```

Replaces `path.exists()` in:
- `find_biomeos_socket()` — biomeOS orchestrator socket lookup
- `discover_socket()` — discovery service socket lookup

### 3. PID File (main.rs)

```rust
let pid_path = format!("{socket_path}.pid");
std::fs::write(&pid_path, process::id().to_string())?;
// Removed on graceful shutdown
```

Consumers can `kill(pid, 0)` for instant liveness checks without connect overhead.

---

## Design Decisions

- **Registry paths NOT probed**: `try_registry_query` (Neural API, legacy registry)
  keeps `path.exists()` because the subsequent `query_registry()` call does
  `UnixStream::connect` itself — this IS the liveness check. A pre-probe would
  consume a connection slot from single-accept servers.
- **Sync probe uses `connect()` not `connect_timeout()`**: `connect_timeout` does
  not exist on `std::os::unix::net::UnixStream`. For Unix domain sockets, `connect()`
  returns immediately (ECONNREFUSED for stale, success for alive) so no timeout needed.
- **50ms async timeout**: Matches primalSpring's `socket_is_alive()` specification in
  `CAPABILITY_BASED_DISCOVERY_STANDARD` v1.3.0 §5.

---

## Quality Gates

| Gate | Result |
|------|--------|
| `cargo fmt --all` | PASS |
| `cargo clippy -D warnings` | 0 warnings |
| `cargo test --workspace --lib --tests` | 7,089 pass / 0 fail |
| `cargo deny check` | advisories ok, bans ok, licenses ok, sources ok |

---

## Test Changes

- `discover_capability_returns_env_provider_without_probe` → renamed to
  `discover_capability_returns_env_provider_with_alive_socket`. Now binds a real
  `UnixListener` instead of file-touching a fake socket path.
- `test_discover_capability_via_env_var` (integration test) → updated to bind a
  real `UnixListener` for the same reason.

---

## Commit

Single commit on `main` branch of `ecoPrimals/squirrel`.
