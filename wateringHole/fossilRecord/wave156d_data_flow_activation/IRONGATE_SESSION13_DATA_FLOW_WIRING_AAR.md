# ironGate Session 13 — Data Flow Wiring AAR

**Date**: 2026-08-05 09:30 EDT
**Gate**: ironGate (10.13.37.7)
**Wave**: 156d — Data Flow Activation Era
**From**: ironGate hardware team
**To**: eastGate overwatch

---

## Summary

Three ironGate team assignments from the Data Flow Activation blurb completed:

1. **footPrint → squirrel bridge** — petal-bridge.ts routes agent.* methods to
   squirrel UDS, translating footPrint's agent protocol to squirrel's ai.query.
   708 footPrint tests PASS. TypeScript clean compile.

2. **tideGlass PetalTongueClient activation** — removed `#[allow(dead_code)]`,
   created client from socket discovery at startup, wired dispatch loop to forward
   visualization scene JSON to petalTongue in addition to returning it. All 83
   tideGlass tests PASS. Build clean.

3. **petalTongue scene passthrough** — handle_render_scene now accepts both
   native SceneGraph and declarative `{ scene, data, format }` from springs.
   Declarative scenes wrapped in minimal SceneGraph with slug as label and
   raw JSON as data_source. petal-tongue-ipc build clean, 13 tests PASS.

---

## Changes Made

### footPrint — `src/petal-bridge.ts`

Rewrote from single-socket petalTongue relay to dual-socket router:
- Browser connects to `/ws` (Express WebSocket)
- `agent.*` / `bridge.*` methods → squirrel UDS (`/run/user/1000/biomeos/squirrel.sock`)
- All other methods → petalTongue UDS (`/run/membrane/petaltongue.sock`)
- Method translation: `agent.query` → `ai.query`, `agent.capabilities` → `capabilities.list`
- Error handling: returns JSON-RPC error if target socket not connected

Verified: squirrel responds to `ai.query` with valid JSON-RPC (returns "No providers
available" when no LLM backend — expected, structurally correct).

### tideGlass — `crates/tideglass-bin/src/{petaltongue,main,server,dispatch}.rs`

**petaltongue.rs**: Removed `#[allow(dead_code)]` from `PetalTongueClient`, `methods`
module, and `render_stream`. Updated doc comment.

**main.rs**: `discover_petaltongue_socket()` now creates `Arc<PetalTongueClient>` and
passes it to `run_server()`.

**server.rs**: `run_server` and `handle_connection` accept `Option<Arc<PetalTongueClient>>`,
thread it to dispatch.

**dispatch.rs**: `dispatch_request` is now `async`, accepts `Option<&PetalTongueClient>`.
After each `visualization.*` handler returns scene JSON, calls `forward_to_petaltongue`
which does a best-effort `client.render_scene()` — logs on success/failure, never blocks
the response. All 22 dispatch tests converted to `#[tokio::test] async fn`.

### petalTongue — `crates/petal-tongue-ipc/src/unix_socket_rpc_handlers/visualization/mod.rs`

**handle_render_scene**: Now tries to deserialize `params.scene` as `SceneGraph` first.
On failure, checks `is_declarative_scene()` (string `scene` field + object `data` field).
Declarative scenes are wrapped in `wrap_declarative_scene()`: minimal SceneGraph with
root node's `label` set to `spring:<slug>` and `data_source` containing serialized JSON.

Response now includes `scene_id` (alias for session_id, matching tideGlass's `SceneHandle`)
and `passthrough: true/false` flag.

---

## Test Results

| Repo | Tests | Result |
|------|-------|--------|
| footPrint | 708 | ALL PASS |
| tideGlass | 83 | ALL PASS |
| petalTongue (IPC) | 13 | ALL PASS |

---

## Remaining Work

| Item | Owner | Status |
|------|-------|--------|
| Restart footPrint server | footPrint team | petal-bridge changes need restart |
| petalTongue UDS socket | hw team | Currently web mode only, no UDS for tideGlass forwarding |
| LLM provider | code teams | `AI_PROVIDER_SOCKETS` for squirrel to complete ai.query loop |
| westGate federation | westGate hw | nestGate TCP + content capability for cross-gate data |
| tideGlass cell boot | westGate team | `biomeos nucleus attach --cell tideglass_cell.toml` on westGate |

---

## For Upstream Review

Three repos modified:
- `gardens/footPrint/` — petal-bridge dual-socket routing
- `springs/tideGlass/` — PetalTongueClient activated, dispatch async with forwarding
- `primals/petalTongue/` — scene passthrough for declarative format

All changes are backward-compatible. tideGlass dispatch still returns scene JSON
directly to callers; petalTongue forwarding is additive (best-effort, non-blocking).
petalTongue still accepts native SceneGraph; passthrough only triggers on deserialization
failure with valid declarative format.
