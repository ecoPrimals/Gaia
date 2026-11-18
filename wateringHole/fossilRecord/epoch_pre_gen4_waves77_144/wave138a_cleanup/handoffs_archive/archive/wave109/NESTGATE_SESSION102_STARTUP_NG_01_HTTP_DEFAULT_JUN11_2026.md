# NestGate Session 102 — STARTUP-NG-01: Default HTTP in server mode

**Date**: 2026-06-11
**Commit**: `66126899`
**Wave**: 109 (guideStone Deployment Convergence)
**Stream**: 1 — Standard Primal Startup Contract

---

## What Changed

`nestgate server` now enables HTTP by default, converging on the guideStone standard:

```
$PRIMAL server --bind-mode $PRIMAL_BIND_MODE --port $PORT
```

### CLI Changes

| Before | After |
|--------|-------|
| `nestgate server` → socket-only | `nestgate server` → HTTP on port 8080 |
| `nestgate server --enable-http` → HTTP | `nestgate server --socket-only` → UDS only |
| `--socket-only` (default true, unused) | `--socket-only` (explicit opt-out) |
| `--enable-http` (explicit opt-in) | Removed |

### PRIMAL_BIND_MODE Support

| Value | Effect |
|-------|--------|
| `tcp_only` / `tcp` | Force HTTP on (overrides `--socket-only`) |
| `uds_only` / `uds` | Force socket-only (overrides HTTP default) |
| `fallback` / `auto` / unset | Respect CLI flag (HTTP default, `--socket-only` opt-out) |

### Legacy Symlink

`nestgate-server` symlink now also defaults to HTTP (`enable_http: true`).

---

## Files Modified

| File | Change |
|------|--------|
| `cli/subcommands.rs` | Removed `--enable-http`, `--socket-only` now bool opt-in |
| `cli/run.rs` | Added `resolve_enable_http()` with `PRIMAL_BIND_MODE` |
| `cli/tests.rs` | 3 tests updated + 7 new `resolve_enable_http` tests |
| `commands/env.rs` | 10 new tests for uncovered env helpers |
| `main.rs` | Legacy symlink defaults HTTP |
| Root docs (x9) | Session 102, Jun 11, 2026 |
| `CHANGELOG.md` | Session 102 entry |
| `sporeprint/validation-summary.md` | Updated counts (3,880 tests) |

---

## Test Results

- **3,880 workspace tests**, 0 failures
- Clippy clean (zero warnings on nestgate code)
- 17 new tests this session

---

## Remaining

- Stream 1 item complete for nestGate.
- No Stream 3 items (health convergence) assigned to nestGate — already responds to JSON-RPC health.
- Deep debt sweep continues as time permits.
