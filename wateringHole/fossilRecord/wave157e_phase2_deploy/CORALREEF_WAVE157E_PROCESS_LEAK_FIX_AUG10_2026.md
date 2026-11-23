# coralReef — Wave 157e Process Leak Fix + Gossip Injection

**Date**: Aug 10, 2026  
**From**: coralReef on strandGate (eastGate overwatch)  
**Commit**: `18b9a681`  
**Previous handoff**: `CORALREEF_WAVE157D_DOC_SYNC_AUG10_2026.md`

---

## What Shipped

### Process Leak Fix (P2 — ~36 orphans/hr on southGate)

**Root cause**: Production coralReef spawns **zero child processes**. The orphans
came from test code — `cmd_server_process.rs` and `e2e_cross_primal.rs` spawn
`coralreef server` as a subprocess. If a test panics between `.spawn()` and the
kill/wait cleanup code, the `Child` handle is dropped without killing or reaping
the server process, creating an orphan.

**Fix**: RAII process guards that kill+reap on `Drop`:
- `ChildGuard` (sync, `std::process::Child`) — `kill()` + `wait()` on Drop
- `AsyncChildGuard` (async, `tokio::process::Child`) — `start_kill()` on Drop

Guards wrap spawned children immediately after `.spawn()`. All assertions and
test logic run while the guard is alive. On panic, the guard's destructor fires
and cleans up the child. On success, the happy-path SIGTERM+wait completes
normally and the guard's Drop is a no-op (child already exited).

**Verification**: All 3,810 tests pass, zero clippy warnings, zero failures.

### Gossip Injection Points (Documentation)

Identified coralReef's events for the swarmVine ant colony pattern:

| Event | Trigger | Payload |
|-------|---------|---------|
| `shader.compiled` | Successful compilation | `{target, compile_time_ms, binary_size, precision}` |
| `silicon.targets` | Startup / capability change | `{targets: ["sm86", "rdna2", ...]}` |
| `compiler.health` | Health state transition | `{status, methods_available, uptime_s}` |

Announced to swarmVine via `gossip.spread` when gossip mesh is enmeshed.
Currently documented only — blocked on TCP 7800 cross-gate reachability.

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | **3,814** total (3,810 passed, 4 ignored) |
| Clippy warnings | **0** |
| Unsafe | **0** |
| Process orphan rate (expected) | **0/hr** (was ~36/hr) |

---

## For Upstream Teams

- **skunkBat**: Shares the process leak P2 with coralReef. skunkBat team should
  audit their test subprocess handling for the same pattern (Child dropped without
  kill/wait). If skunkBat doesn't spawn test subprocesses, the southGate orphans
  may have been entirely from coralReef's test harness.
- **Gate ops (southGate)**: Process leak should be resolved after next depot rebuild
  with this fix. Monitor orphan count to confirm.

---

*Wave 157e — process leak fix (RAII guards, zero orphans expected), gossip injection
points documented. 3,810 tests. Zero clippy. Zero unsafe. Zero orphans.*
