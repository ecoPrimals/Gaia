<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 106: Stale Socket Prevention

**Date**: May 18, 2026
**From**: bearDog (crypto spine)
**To**: primalSpring, wetSpring, all primals
**Audit**: Stale Socket Detection + Cleanup (May 18, 2026)

---

## Summary

BearDog resolves the stale socket prevention upstream ask. The main CLI
server path now handles both SIGINT and SIGTERM, with explicit socket file
cleanup on shutdown.

---

## What Changed

### SIGTERM Signal Handling

`MultiTransportServer::start_all` (the `beardog server` production path)
now registers both:
- **SIGINT** (Ctrl+C) — already handled
- **SIGTERM** (systemd stop, `kill`, docker stop) — **new**

On either signal, all transport tasks are aborted and all
`UnixSocketIpcServer` instances receive explicit `stop()` calls.

### Explicit Socket Cleanup

After signal receipt:
1. `join_set.abort_all()` — cancel all transport tasks
2. Drain all tasks (log outcomes)
3. `server.stop()` — removes socket file + IPC capability symlinks

This is deterministic — it does not rely on `Drop` semantics which may
not fire during runtime teardown after task abort.

### Pre-existing Defense-in-Depth (confirmed)

BearDog already implements `unlink-before-bind` at 3 layers:

| Layer | Location | Mechanism |
|-------|----------|-----------|
| Config | `SocketConfig::prepare()` | `std::fs::remove_file` |
| Server constructor | `UnixSocketIpcServer::new()` | `tokio::fs::remove_file` |
| Platform bind | `UnixSocket::bind()` | `std::fs::remove_file` |

Even if a prior crash left a stale socket, the next startup removes it
before binding. The new SIGTERM handling prevents the crash scenario from
occurring in the first place (for graceful termination signals).

### `Drop` Implementation (unchanged, defense-in-depth)

`impl Drop for UnixSocketIpcServer` also removes the socket file. This
covers the rare case where `stop()` fails or the server is dropped via
a different code path.

---

## Compliance

| Requirement | Status |
|-------------|--------|
| `unlink()` before `bind()` on startup | PASS (3 layers) |
| Clean up on shutdown | PASS (explicit `stop()` + `Drop`) |
| SIGTERM handling | PASS (new) |
| PID file (optional) | Not implemented (LOW priority) |

---

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --all -- --check` | Clean |
| `cargo clippy -p beardog-tunnel --all-targets` | 0 errors |
| `cargo test --workspace` | 14,940+ pass, 1 pre-existing env-dependent |
| `cargo check -p beardog-tunnel` | Clean |

---

## Modified Files

- `crates/beardog-tunnel/src/multi_transport_server.rs` — SIGTERM + explicit stop
- `STATUS.md` — Wave 106 entry
- `CHANGELOG.md` — Wave 106 entry
