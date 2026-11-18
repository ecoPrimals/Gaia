# biomeOS v3.66 — Wave 38 Cross-Gate Wiring + CG-8 Relay Fallback

**Date:** May 22, 2026
**From:** biomeOS team
**To:** primalSpring, songbird, projectNUCLEUS
**Version:** v3.66
**License:** AGPL-3.0-or-later

---

## Summary

Resolves both biomeOS items from primalSpring Wave 38:

1. **`nest.sync` live orchestration** — cross-gate wiring so `remote_gate` flows from caller params through signal dispatch into graph execution, enabling `fetch_dag_slice` to target a remote NUCLEUS.
2. **CG-8: `capability.call` → songbird** — relay fallback in cross-gate dispatch. When a gate isn't directly registered, biomeOS attempts `relay.allocate` through Songbird before failing.

---

## Item 1: nest.sync Cross-Gate Wiring

### Problem

The `nest_sync.toml` graph (shipped v3.64) defined a 6-node cross-spring pipeline but had no mechanism to route the first node (`fetch_dag_slice`) to the remote spring's NUCLEUS. The `remote_gate` parameter was documented in comments and the tool schema but was never propagated into the graph execution environment.

### Resolution

| Component | Change |
|-----------|--------|
| `graphs/signals/nest_sync.toml` | Added `[graph.env]` with `remote_gate = ""` placeholder. `fetch_dag_slice` node gets `gate = "remote_gate"`. Nodes 2-6 have no gate (execute locally). |
| `handlers/signal.rs` | Signal dispatch extracts `remote_gate` from caller params and injects it into the `env` field of `execute_params`. |
| `handlers/graph/execute.rs` | Caller-provided `env` in execute params now merged into graph env (overrides TOML defaults). Extracted before `tokio::spawn` boundary for lifetime safety. |
| `tests/signal_dispatch_tests.rs` | Updated `nest_sync_graph_has_cross_spring_pipeline` to assert: `fetch_dag_slice` has `gate = "remote_gate"`, other nodes have no gate, `graph.env` declares `remote_gate`. |

### Flow

```
nest.sync { remote_gate: "tcp://westgate:9001", session_id: "abc" }
  → routing.rs: SemanticCapabilityCall → capability.call { capability: "nest", operation: "sync" }
  → signal intercept: nest is a signal tier → signal.dispatch
  → signal.rs: extracts remote_gate, injects into env
  → graph.execute: env["remote_gate"] = "tcp://westgate:9001"
  → GateRegistry::from_graph_env picks up remote_gate as gate endpoint
  → fetch_dag_slice (gate = "remote_gate") → forwarded to westgate NUCLEUS
  → verify_proof, store_content, sync_braid, commit_sync, attribute_sync → local
```

### E2E Prerequisites (unchanged from v3.64 handoff)

- [ ] Live rhizoCrypt + loamSpine + sweetGrass on both springs
- [ ] Cross-gate registration between NUCLEUS instances
- [ ] sweetGrass `braid.sync` method implementation (v0.8+)
- [ ] westGate NUCLEUS deployment (projectNUCLEUS Wave 38 priority 1)

---

## Item 2: CG-8 — capability.call → Songbird Relay Fallback

### Problem

Cross-gate `capability.call` routing required pre-registered gates in `GateRegistry` (via `[graph.env]` or `route.register`). If a gate wasn't registered, the call failed immediately. This blocked multi-gate mesh compositions where gates may only be reachable through Songbird's TURN relay (NAT, CGNAT, residential networks).

### Resolution

| Component | Change |
|-----------|--------|
| `handlers/capability_call.rs` | Added `try_relay_dispatch()` method. When `gate` param targets an unregistered gate, attempts `relay.allocate` through Songbird (discovered via `relay` capability), then forwards through the allocated relay endpoint. |
| Error message | Updated from "not registered" to "not registered and relay fallback unavailable" to distinguish the two failure modes. |
| `capability_call_tests.rs` | New test `test_call_with_unknown_gate_mentions_relay` validates the fallback error path when no Songbird is available. |

### Tiered Dispatch

```
capability.call { gate: "westgate", capability: "dag", operation: "checkout_slice" }
  1. Check GateRegistry → direct TCP/UDS forward (fast path)
  2. If not registered → try_relay_dispatch:
     a. Discover Songbird via "relay" capability
     b. relay.allocate { gate: "westgate" } → get relay channel + endpoint
     c. Forward capability.call through relay endpoint
  3. If relay unavailable → error with "relay fallback unavailable"
```

### Songbird Integration Contract

biomeOS calls:
- `relay.allocate { gate: "<gate_name>", method: "<method>" }` → expects `{ endpoint: "tcp://...", channel_id: "..." }`
- Then `capability.call` on the returned endpoint with `relay_channel` field

Songbird owns the relay allocation, TURN transport, and channel lifecycle. biomeOS owns the routing decision (when to use relay vs direct).

### Interaction with nest.sync

nest.sync benefits from CG-8 indirectly: if `remote_gate` resolves through `GateRegistry` (direct), it uses fast path. If the remote gate is behind NAT and only reachable via Songbird relay, the graph executor's `forward_to_remote_gate` calls `capability.call` which now has the relay fallback.

---

## Test Results

- `signal_dispatch_tests`: 11/11 pass (including updated `nest_sync_graph_has_cross_spring_pipeline`)
- `capability_call_tests`: 3/3 pass (including new `test_call_with_unknown_gate_mentions_relay`)
- `biomeos-atomic-deploy` lib: 1276/1276 pass
- Clippy: 0 warnings
- All production `.rs` files under 800 lines

---

## Remaining Horizons (biomeOS perspective)

| Item | Status | Blocks |
|------|--------|--------|
| nest.sync E2E validation | Wired, untested | westGate NUCLEUS deploy |
| CG-8 E2E relay dispatch | Wired, untested | Songbird relay.allocate in production |
| nest.store (R5) | RESOLVED v3.63 | — |
| spore.instantiate (R7) | DEFERRED-TO-STADIAL v3.63 | lithoSpore Tier 3 |
| primal.list (Wave 20) | RESOLVED v3.65 | — |
