# Songbird — Wave 55 NC-2 Mesh Stability Response

**Date**: 2026-05-27  
**From**: Songbird team  
**Version**: v0.2.1  
**Audit item**: NC-2 — Mesh stability for multi-gate

---

## Investigation Summary

Comprehensive code-level investigation of cold-start race conditions, memory
pressure vectors, and restart resilience in Songbird's mesh initialization.

**Verdict**: No panic vectors in any startup path. The "intermittent crashes"
on southGate (7/13 health-responding) are operational, not code-level.

---

## Code Fix: TCP Fallback Mesh Seed Gap

Found and fixed a gap where `start_tcp_fallback()` (used when UDS bind fails
due to SELinux/permissions) **never fired `spawn_mesh_seed`**. If southGate
ever falls to TCP fallback mode, mesh would never auto-initialize.

**Before**: TCP fallback path → `is_ready=true` → accept loop (no mesh seed)  
**After**: TCP fallback path → `is_ready=true` → `spawn_mesh_seed()` → accept loop

This is the only code-level issue found. All other paths are robust.

---

## Investigation Findings

### No Crash Vectors in Startup

| Path | Behavior |
|------|----------|
| `spawn_mesh_seed` | Errors logged via `warn!`, never panics |
| `spawn_announce` | Connect/write failures non-fatal |
| `handle_init` | Returns `Result<Value, String>`, all failures soft |
| Accept loop | Per-connection errors logged, never propagate |
| Socket bind | Unconditional `unlink()` before bind; permission errors silenced |
| `discovery.peers` before seed completes | Returns empty list (not error) |

### Restart Resilience

- Mesh state is fully in-memory (`Arc<RwLock<Option<Arc<BeaconMesh>>>>`)
- Every startup re-bootstraps from `SONGBIRD_PEERS` env var
- No persistent state needed — env vars are the source of truth
- `unlink()` before `bind()` handles stale sockets from crashed processes
- Double-init (auto-seed + external `mesh.init`) is safe: last writer wins

### Likely Causes for southGate 7/13

1. **`SONGBIRD_PEERS` not set or malformed** → mesh never seeds; external `mesh.init` required
2. **Other primals crashing** (OOM, fd exhaustion) → not Songbird's fault
3. **Cold-start timing window** — health probes hitting Songbird before mesh seed completes see empty peers (not a crash, just partial visibility)
4. **Zombie process holding socket** — a previous Songbird instance not cleanly killed

### Clippy Fix

Fixed new `clippy::unnecessary_get_then_check` lint in `graph/coordination`
test (`.get("node1").is_none()` → `!deps.contains_key("node1")`).

---

## Recommended Ops Actions for southGate

1. Verify `SONGBIRD_PEERS` and `SONGBIRD_NODE_ID` are set in the environment
2. Check logs for `"SONGBIRD_PEERS not set or empty"` or `"Failed to auto-seed mesh"`
3. Verify UDS mode (not TCP fallback): look for `"Starting TCP IPC fallback"`
4. After kill/restart: confirm no zombie `songbird` processes (`pgrep songbird`)
5. Check memory pressure: `free -h` and `dmesg | grep -i oom`
6. Time-align: compare first `discovery.peers` response vs `"Auto-seeding mesh"` log

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 8,070 lib passed, 0 failures, 23 ignored |
| Clippy | Zero warnings (pedantic + nursery, `-D warnings`, May 27) |
| Code changes | 1 fix (TCP fallback mesh seed) + 1 clippy lint |
| Crash vectors found | **0** |
| Restart-safe | Yes (env-var re-seeding on every startup) |

---

## Status

Songbird remains deep-debt-zero. Ready for live `s_covalent_mesh` coordination
when southGate ops are stabilized. No code changes needed for NC-2 beyond the
TCP fallback fix shipped here.
