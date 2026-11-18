# petalTongue — Stale Socket Cleanup + PID File

**Date**: May 18, 2026
**Primal**: petalTongue
**Trigger**: All-teams upstream ask — stale socket detection + cleanup
**Priority**: HIGH (downstream pipelines hitting stale sockets in production)

## Prior State

petalTongue already had both required defenses:
- `unlink()` before `bind()` — implemented since initial IPC server
- `Drop` cleanup — removes socket and capability symlink on shutdown

However, the implementation used `exists()` + conditional `remove_file()`/`remove_dir()`,
which has a TOCTOU (time-of-check-to-time-of-use) race.

## Changes

### 1. Startup Hardening (both server paths)

**`unix_socket_server.rs`** and **`server.rs`**: Replaced `exists()` check
with unconditional `remove_file()` that ignores `NotFound` errors:

```rust
match std::fs::remove_file(&socket_path) {
    Ok(()) => debug!("Removed stale socket: {}", socket_path.display()),
    Err(e) if e.kind() == std::io::ErrorKind::NotFound => {}
    Err(e) => return Err(...),
}
let listener = UnixListener::bind(&socket_path)?;
```

### 2. PID File

On successful bind, writes `petaltongue.pid` alongside `petaltongue.sock`:
- Content: server PID as ASCII decimal
- Enables instant `kill(pid, 0)` liveness checks without connect overhead
- Removed in `Drop` before socket cleanup

### 3. Shutdown (Drop) Simplification

Replaced `exists()` + type-check chain with unconditional `remove_file()`
plus `is_dir()` fallback for edge cases (defensive).

## Files Changed

| File | Change |
|------|--------|
| `crates/petal-tongue-ipc/src/unix_socket_server.rs` | TOCTOU fix, PID file helpers, Drop simplification |
| `crates/petal-tongue-ipc/src/server.rs` | TOCTOU fix for secondary server path |
| `CHANGELOG.md` | New entry |

## Quality Gate

- `cargo fmt --check`: PASS
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`: PASS
- `cargo test --workspace --all-features`: all tests pass, 0 failures
