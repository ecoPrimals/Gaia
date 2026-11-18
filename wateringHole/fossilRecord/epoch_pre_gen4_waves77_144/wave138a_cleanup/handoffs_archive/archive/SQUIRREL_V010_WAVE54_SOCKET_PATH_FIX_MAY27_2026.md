# Squirrel v0.1.0 — Wave 54 Filesystem Socket Path Fix

**Date:** May 27, 2026
**From:** Squirrel team
**To:** primalSpring, wetSpring, neuralSpring
**Priority:** MEDIUM — resolves southGate "socket not at expected name"

---

## Problem

The NUCLEUS launcher passes `--socket $XDG_RUNTIME_DIR/biomeos/squirrel-$FAMILY_ID.sock`
to Squirrel on startup. Squirrel accepted the argument and logged it, but the SQ-01
filesystem socket companion (the one biomeOS/launcher discover via `readdir()`) was
bound at a **different** path — one re-derived from environment variables.

The primary listener used a Linux abstract namespace socket (`\0squirrel`), which is
invisible to filesystem-based discovery. The SQ-01 companion socket was supposed to be
the discoverable filesystem socket, but it ignored the `--socket` CLI argument.

## Root Cause

In `crates/main/src/rpc/jsonrpc_server.rs`, the SQ-01 filesystem socket block called:

```rust
let fs_path = super::unix_socket::get_socket_path(&super::unix_socket::get_node_id());
```

This re-derived the socket path from env vars, ignoring `self.socket_path` which was
already correctly resolved from the `--socket` CLI argument (or config/env fallback).

## Fix

Changed to use `self.socket_path.clone()` — the path already resolved in `run_server()`
from the `--socket` CLI argument → config → env → XDG fallback chain:

```rust
let fs_path = self.socket_path.clone();
```

## Verification

- `cargo fmt` — clean
- `cargo clippy --workspace` — zero warnings
- `cargo test -p squirrel --lib` — 2,244 pass
- `cargo test -p squirrel --tests` — 14 pass
- `cargo deny check` — clean

## Expected Behavior After Deploy

When the launcher runs:
```
squirrel server --socket /run/user/1000/biomeos/squirrel-nucleus01.sock
```

Squirrel will now:
1. Bind abstract socket `\0squirrel` (primary, for in-host fast IPC)
2. Bind filesystem socket `/run/user/1000/biomeos/squirrel-nucleus01.sock` (SQ-01 companion)
3. Create `ai.sock` symlink → `squirrel-nucleus01.sock` (capability-domain discovery)
4. Write PID file at `squirrel-nucleus01.sock.pid`
5. Write primal manifest for bootstrap discovery

Both sockets serve the same JSON-RPC handler. The launcher's health probe on the
filesystem socket will now succeed.

## Status

- **Wave 54 ask**: RESOLVED
- **Squirrel southGate status**: Should be UP after next `plasmidBin harvest` + deploy
