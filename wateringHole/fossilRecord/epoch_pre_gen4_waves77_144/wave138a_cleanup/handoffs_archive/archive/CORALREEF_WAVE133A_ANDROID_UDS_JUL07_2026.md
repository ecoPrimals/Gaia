<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 133a: Android UDS Adaptation

**Date**: July 7, 2026  
**Commit**: `a6e542c`  
**Ticket**: CORALREEF-ANDROID-01 (P2)

---

## Problem

coralReef fatal-exits on Android (grapheneGate) because:

1. `socket_base_dir()` unconditionally falls through to `/run/biomeos` when
   `$BIOMEOS_SOCKET_DIR` and `$XDG_RUNTIME_DIR` are unset — Android has neither
   `/run/` nor XDG runtime dirs
2. `start_tarpc_server()` treats Unix socket bind failure as fatal (`exit 1`),
   even in `Both` bind mode where TCP is already listening
3. No platform-aware fallback for constrained environments

12/13 primals run on grapheneGate (Pixel 8a); coralReef + nestGate are the two
that fatal on UDS. nestGate already has a 4-tier resolver with temp-dir fallback.

## Fix

### 4-tier socket resolution (`config.rs`)

```
1. $BIOMEOS_SOCKET_DIR  — explicit override (composition launcher)
2. $XDG_RUNTIME_DIR     — Linux/freedesktop standard
3. /run/biomeos          — system fallback, ONLY IF IT EXISTS
4. $TMPDIR/biomeos-runtime — platform-portable fallback (new)
```

Tier 3 now probes `Path::exists()` before using `/run/biomeos`. Tier 4 uses
`std::env::temp_dir()` which resolves correctly on Android (`$PREFIX/tmp` in
Termux, `/data/local/tmp` native).

### tarpc TCP fallback (`main.rs`)

When tarpc Unix socket bind fails (the path starts with `unix://`), the server
now falls back to TCP `127.0.0.1:0` instead of exiting. If TCP fallback also
fails, the server continues without tarpc (JSON-RPC TCP still serves all
methods). Only explicit TCP tarpc bind failures remain fatal.

### Test updates

Socket-path integration tests updated to be platform-aware: assert
`/run/biomeos` prefix when the directory exists, temp-dir prefix when it
doesn't. Enables the same test to pass on both desktop Linux and Android.

## Files Changed

| File | Change |
|------|--------|
| `crates/coralreef-core/src/config.rs` | 4-tier `socket_base_dir()` |
| `crates/coralreef-core/src/main.rs` | tarpc UDS→TCP fallback |
| `crates/coralreef-core/src/ipc/mod.rs` | Doc: 3-tier → 4-tier |
| `crates/coralreef-core/src/ipc/unix_jsonrpc.rs` | Doc: 3-tier → 4-tier |
| `crates/coralreef-core/tests/unix_jsonrpc_default_socket_path_env.rs` | Platform-aware assertions |
| `CHANGELOG.md`, `README.md`, `STATUS.md` | Wave 133a |

## Quality Gates

- `cargo fmt` — clean
- `cargo clippy --all-features -- -D warnings` — zero warnings
- `cargo test --all-features` — 3649 pass, 0 fail, 4 ignored (hardware-gated)

## Deployment Note

grapheneGate can now start coralReef with:
- **No env vars needed** — tier 4 auto-resolves to writable temp dir
- **Optional**: `BIOMEOS_SOCKET_DIR=/data/local/tmp/biomeos` for explicit control
- **Optional**: `PRIMAL_BIND_MODE=tcp_only` to skip UDS entirely

## Upstream Impact

nestGate has the same issue (NESTGATE-ANDROID-01) but already has its own
4-tier resolver. This fix aligns coralReef with the nestGate pattern.
grapheneGate NUCLEUS launcher should now get 13/13 primals on next deploy.
