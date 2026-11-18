# barraCuda: Stale Socket Gap — 2 Bind Sites Missing Pre-Bind Cleanup

**Date:** May 18, 2026
**From:** primalSpring (coordination spring)
**To:** barraCuda team
**Priority:** LOW — not blocking, defense-in-depth
**Context:** Stale Socket Detection + Cleanup ecosystem sweep

---

## Summary

The May 18 stale socket blurb absorption sweep confirmed **13/14 primals clean**.
barraCuda is the only primal with bind sites that lack `unlink()` before `bind()`.

barraCuda already has a `PidFileGuard` (ahead of the curve on PID files), but
the two `UnixListener::bind()` calls in `transport.rs` don't remove a pre-existing
stale socket before binding. If barraCuda crashes and restarts, the second start
hits `EADDRINUSE` instead of cleanly replacing the stale socket.

---

## What Needs to Change

**File:** `crates/barracuda-core/src/ipc/transport.rs`

Both bind sites currently look like:

```rust
if let Some(parent) = path.parent() {
    std::fs::create_dir_all(parent)?;
}

let listener = tokio::net::UnixListener::bind(path)?;
```

Add `remove_file` before bind at both sites:

```rust
if let Some(parent) = path.parent() {
    std::fs::create_dir_all(parent)?;
}

// Remove stale socket from prior crash (CAPABILITY_BASED_DISCOVERY_STANDARD §4)
if path.exists() {
    let _ = std::fs::remove_file(path);
}

let listener = tokio::net::UnixListener::bind(path)?;
```

That's it — 3 lines × 2 sites = 6 lines total.

---

## What barraCuda Already Has Right

- `PidFileGuard` — writes PID file, removes on drop (good)
- `remove_file` for core JSON file cleanup on start
- Standard primal architecture otherwise

---

## Why This Matters

The `CAPABILITY_BASED_DISCOVERY_STANDARD.md` §4 requires primals to `unlink()`
before `bind()`. This is standard Unix domain socket practice — it prevents stale
sockets from accumulating after crashes and avoids `EADDRINUSE` on restart.

primalSpring's consumer-side connect-probe (`socket_is_alive()`) catches stale
barraCuda sockets at discovery time, so this is not a production blocker. It's
defense-in-depth: the server should clean up its own sockets, and consumers
should verify liveness. Both layers protect against the same failure mode.

wetSpring's observation of 50+ stale sockets (May 18) triggered this sweep.
13 primals confirmed clean. barraCuda is the last one.

---

## Impact

- **Without fix:** barraCuda crash → restart fails with `EADDRINUSE`.
  Consumer discovery still works (connect-probe returns false for stale socket).
- **With fix:** barraCuda crash → restart succeeds cleanly. Zero stale sockets.

## Reference

- `CAPABILITY_BASED_DISCOVERY_STANDARD.md` v1.3.0 §4-6
- `DEPLOYMENT_VALIDATION_STANDARD.md` (stale socket hygiene section)
- `STALE_SOCKET_CLEANUP_UPSTREAM_MAY18_2026.md` (full sweep results)
