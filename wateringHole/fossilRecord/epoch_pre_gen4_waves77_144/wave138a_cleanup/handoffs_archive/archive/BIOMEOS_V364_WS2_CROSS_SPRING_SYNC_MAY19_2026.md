# biomeOS → primalSpring: WS-2 Cross-Spring Provenance Exchange (RootPulse)

**Date:** May 19, 2026
**Author:** biomeOS team (southGate)
**Audience:** primalSpring, wetSpring, all delta springs, provenance trio teams
**Status:** WS-2 RESOLVED — `nest.sync` signal graph defined
**Version:** v3.64
**License:** AGPL-3.0-or-later

---

## WS-2: Cross-Spring Data Exchange — RESOLVED

### Problem

NestGate stores locally but no protocol existed for another spring's
NUCLEUS to pull provenance-wrapped data subsets. Each spring operated as
a data silo. The ask: biomeOS defines a `rootpulse.sync` composition
graph that orchestrates cross-spring provenance exchange via the trio.

### Solution: `nest.sync` signal

Implemented as a **nest-tier atomic signal** (`nest.sync`) — a 6-node
sequential pipeline for cross-spring braid subset pull with full
provenance continuity through the trio. This is the signal-dispatch
equivalent of the `rootpulse_federate` workflow graph, scoped to
braid subset pull with cross-gate routing.

### Pipeline

```
nest.sync
  ├── 1. fetch_dag_slice   (rhizoCrypt)   — dag.checkout_slice from remote via cross-gate
  ├── 2. verify_proof      (rhizoCrypt)   — dag.verify_proof integrity check
  ├── 3. store_content     (nestGate)     — content.put locally
  ├── 4. sync_braid        (sweetGrass)   — braid.sync remote attribution
  ├── 5. commit_sync       (loamSpine)    — session.commit to local ledger
  └── 6. attribute_sync    (sweetGrass)   — braid.create sync event (optional)
```

### Invocation

Springs can call `nest.sync` directly as a JSON-RPC method:

```json
{
  "jsonrpc": "2.0",
  "method": "nest.sync",
  "params": {
    "remote_gate": "wetspring-nucleus",
    "session_id": "barrick-2009-sovereign-run-001",
    "spine_id": "main",
    "content_filter": {
      "braid_ids": ["braid-abc123"],
      "time_range": { "after": "2026-05-18T00:00:00Z" }
    }
  },
  "id": 1
}
```

Or via `signal.dispatch`:

```json
{
  "jsonrpc": "2.0",
  "method": "signal.dispatch",
  "params": {
    "signal": "nest.sync",
    "params": {
      "remote_gate": "wetspring-nucleus",
      "session_id": "barrick-2009-sovereign-run-001"
    }
  },
  "id": 1
}
```

Or via `capability.call` (auto-intercepted by signal graph):

```json
{
  "jsonrpc": "2.0",
  "method": "capability.call",
  "params": {
    "capability": "nest",
    "operation": "sync",
    "args": { "remote_gate": "...", "session_id": "..." }
  },
  "id": 1
}
```

### What was added

| Component | Change |
|-----------|--------|
| `graphs/signals/nest_sync.toml` | 6-node sequential pipeline with `cross_gate` fragment |
| `config/signal_tools.toml` | `nest.sync` schema with `remote_gate`, `session_id`, `spine_id`, `content_filter` params |
| `config/capability_registry.toml` | `provenance.sync_braid` → sweetGrass `braid.sync` translation |
| `routing.rs` route table | `("nest.sync", Route::SemanticCapabilityCall)` first-class entry |
| Signal dispatch tests | `nest_sync_graph_has_cross_spring_pipeline` + updated counts (16→17) |

### Cross-gate mechanism

The `nest.sync` graph leverages the existing cross-gate `capability.call`
forwarding in `capability_call.rs`. When a signal node targets a remote
primal (via the `remote_gate` parameter), the graph executor routes
through `AtomicClient::from_endpoint()` → remote NUCLEUS Neural API.

The `cross_gate` fragment in graph metadata declares this dependency.
No new cross-gate infrastructure was needed — the forwarding layer from
v3.60+ handles this.

### Degradation

If `nest.sync` is unavailable (trio primals not composed, remote gate
unreachable), springs fall back to:
1. Direct IPC calls (4-call provenance trio pattern)
2. Git-based braid exchange (existing `rootpulse_federate` workflow)

### Prerequisites for E2E validation

- [ ] Live rhizoCrypt + loamSpine + sweetGrass deployment on both springs
- [ ] Cross-gate registration between NUCLEUS instances (songbird relay
  or direct socket path)
- [ ] sweetGrass `braid.sync` method implementation (method registered
  in primalSpring capability registry but execution handler depends on
  sweetGrass v0.8+)

---

## Non-biomeOS items (acknowledged, not actionable by biomeOS)

| # | Gap | Owner | biomeOS status |
|---|-----|-------|----------------|
| WS-1 | Ionic contract negotiation | primalSpring Track 4 | Needs spec — architectural |
| WS-3 | Public chain anchor | loamSpine | Spec-level, no implementation pressure |
| WS-4 | Client WASM renderer | petalTongue | Phase 3, Plotly.js functional |
| WS-9 | Cross-tier parity (L3) | wetSpring | Requires live trio deployment |
| WS-11 | Variant caller calibration | wetSpring | Active, not biomeOS scope |

### CG-8 interaction (songbird cross-gate dispatch)

`nest.sync` uses the same cross-gate forwarding infrastructure that CG-8
(Cross-gate dispatch via songbird) will eventually replace with
relay-mediated routing. When songbird's relay layer is ready, `nest.sync`
will automatically benefit — the graph nodes use `capability.call` with
`gate` parameter, which routes through whatever transport layer is active
(currently direct socket, future songbird relay).
