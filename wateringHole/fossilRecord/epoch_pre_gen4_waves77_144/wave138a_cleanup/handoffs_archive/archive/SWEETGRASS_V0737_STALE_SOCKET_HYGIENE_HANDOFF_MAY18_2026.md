# sweetGrass v0.7.37 — Stale Socket Hygiene

**Date**: May 18, 2026
**From**: sweetGrass team
**Audit**: primalSpring stale socket detection + cleanup (May 18, 2026)

---

## Summary

sweetGrass already had all core socket hygiene in place (`unlink()`
before `bind()`, graceful shutdown cleanup, capability symlink management).
v0.7.37 adds PID file support alongside the socket so downstream
consumers can use `kill(pid, 0)` for instant (0ms) liveness checks
instead of the 100ms `connect()` probe.

---

## Socket Lifecycle (already present)

| Step | Implementation | Location |
|------|---------------|----------|
| `unlink()` before `bind()` | `std::fs::remove_file(path)` before `UnixListener::bind()` | `uds.rs:227-229` |
| Graceful shutdown cleanup | `cleanup_socket_at()` on SIGINT/SIGTERM | `service.rs:338` |
| Capability symlink | `provenance.sock -> sweetgrass.sock` | `uds.rs:create_capability_symlink()` |
| Stale symlink replacement | Remove + recreate on startup | `uds.rs:679-687` |

## New: PID File Support

- **On startup**: `sweetgrass.pid` written alongside socket containing the
  process PID. Any stale PID file is removed before write.
- **On shutdown**: PID file removed alongside socket and symlink.
- **Consumer usage**: `kill(pid, 0)` returns 0 if process exists, -1 if not.
  Costs 0ms vs 100ms for `connect()` probe.

File naming: `{primal}.sock` → `{primal}.pid` (same stem, `.pid` extension).
Example: `/run/user/1000/biomeos/sweetgrass.pid`

---

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.37 |
| Tests | 1,553 pass (+4 PID file tests) |
| LOC | 55,164 |
| Clippy | 0 warnings |

---

## Downstream Action Required

None. The PID file is opt-in for consumers — existing `connect()` probes
continue to work. primalSpring's `socket_is_alive()` can add a
`kill(pid, 0)` fast-path when a `.pid` file exists.
