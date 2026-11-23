# NestGate Session 101b: NG-DOWNCAST-01 Fix + Doc Refresh

**Date**: 2026-06-10
**Commits**: `1b3a2da1` (doc refresh), `7c3fe9a6` (bug fix) on `main`
**Wave**: 107 — NG-DOWNCAST-01 (LOW) resolved

---

## Summary

Fixed the only named NestGate item in Wave 107. `is_platform_constraint()`
now walks the full error chain, root docs refreshed to honest metrics,
capability registry synced, gitignore cleaned.

## NG-DOWNCAST-01 Fix

**Root cause**: `is_platform_constraint()` used `anyhow::Error::downcast_ref::<io::Error>()`
which only checks the top-level error type. When the `io::Error` was wrapped through
`.context()` or `anyhow::anyhow!("msg: {e}")`, the downcast failed silently, making the
function always return `false` for wrapped errors.

**Fix**:
1. Introduced `find_io_error()` which walks the full `source()` chain to find nested `io::Error`
2. Changed `UnixListener::bind` error path from `anyhow::anyhow!()` (stringifies, destroys type)
   to `.context()` (preserves original `io::Error` in the chain)
3. 7 new tests: chain-walking, context-wrapped IO errors, stringified IO errors (negative),
   deeply nested errors, `PRIMAL_BIND_MODE=fallback/tcp_only` env var interaction

**Workaround removed**: `NESTGATE_SOCKET=""` no longer needed; the error chain is now
properly inspected regardless of wrapping depth.

## Doc Refresh

- 8 root docs updated from Session 92 → Session 101 with honest test counts:
  3,863 total (2,325 lib, 874 RPC), 0 failures
- `capability_registry.toml` (root) synced from canonical `config/` source
  (was 11 lines behind, missing `transport_evolution = "phase2"`)
- `tests/capability_registry_crosscheck.rs` → `config/capability_registry.toml`
- `.gitignore` cleaned: removed stale showcase/bioinformatics entries
- `cargo clean`: freed 120.9 GB; clean rebuild validated

## Validation

- 3,790+ tests passing (1 pre-existing ZFS bridge failure)
- 0 clippy warnings
- Clean build from scratch validates

## NestGate Wave 107 Status

| Item | Status |
|------|--------|
| P2 | **ZERO** |
| LOW (NG-DOWNCAST-01) | **RESOLVED** (`7c3fe9a6`) |
| Remaining LOW | **ZERO** (skunkBat TCP-9750, sourDough segfault, etc. are other primals) |
