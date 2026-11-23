# petalTongue v1.6.6 — Live Dashboard + NestGate-Aware Index Routing

**Date**: May 13, 2026
**Primal**: petalTongue
**Trigger**: primalSpring Glacial Debt Escalation audit — "backend=nestgate is UNBLOCKED (Session 60 transport parity shipped) — live dashboard wiring"

## Context

NestGate Session 60 shipped `content.*` transport parity across all paths
(SemanticRouter, isomorphic IPC, HTTP API). petalTongue's meta-tier is CLEAN
with no blocking gaps. This handoff covers the niche evolution work: making
the web dashboard live and wiring NestGate-aware index resolution.

## Changes

### 1. Live Dashboard (`web/index.html`)

**Before**: Static HTML with 3 hardcoded cards and a one-shot `fetch('/api/status')`.
No SSE subscription, no primal discovery rendering, no topology display.

**After**: Full live ecosystem dashboard:
- Subscribes to `/api/events` (SSE) for real-time `DataSnapshot` updates
- Fetches `/api/snapshot` on load for immediate state
- Renders discovered primals: name, health pill, type, capabilities, endpoint
- Renders topology edges with source → target and edge type
- Connection status indicator (live / reconnecting)
- Status bar: mode, backend, event counter
- Dark/light mode via `prefers-color-scheme`
- Zero external dependencies (vanilla JS, no frameworks)

### 2. NestGate-Aware Index Routing

**Before**: `GET /` always served `include_str!("../web/index.html")` regardless
of backend setting.

**After**: When `backend=nestgate`, `GET /` routes through `nestgate_index()`:
1. Tries `content.resolve("/")` from NestGate via UDS JSON-RPC
2. If NestGate returns content, serves it with the resolved MIME type
3. If NestGate has no root document (or is unreachable), falls back to the
   compiled-in dashboard

This enables NestGate-published root documents (e.g., sporePrint landing pages)
to be served transparently while maintaining a guaranteed fallback.

### 3. Doc Cleanup

- `CONTEXT.md`: Removed "blocked on NestGate" language. `backend=nestgate` is
  UNBLOCKED with Session 60 transport parity.
- `CHANGELOG.md`: New entry documenting live dashboard and NestGate index routing.
- `START_HERE.md`: Updated CLI examples to reflect live dashboard and NestGate CAS.

## Backend Routing Refactor

Converted `match cfg.backend { "nestgate" => ..., _ => ... }` to `if`/`else`
per `clippy::single_match_else`.

## Quality Gate

- `cargo fmt --check`: PASS
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`: PASS (0 warnings)
- `cargo test --workspace --all-features`: 222 tests, 0 failures
- `cargo doc --workspace --no-deps --all-features`: PASS
- All 39 web_mode tests pass including SPA, CORS, and index handler tests

## Files Changed

| File | Change |
|------|--------|
| `web/index.html` | Rewritten — live SSE dashboard |
| `src/web_mode.rs` | `nestgate_index()` handler, if/else routing |
| `CONTEXT.md` | NestGate unblocked status |
| `CHANGELOG.md` | New entry |
| `START_HERE.md` | Updated CLI descriptions |

## Remaining Niche Evolution

- NestGate content pipeline E2E validation (live composition)
- `content.get` support (currently only `content.resolve`)
- Dashboard enhancements: graph visualization, capability matrix
