# biomeOS v3.75 Handoff — Cross-Gate Routing: Songbird Mesh Dispatch

**Date**: May 24, 2026
**Versions**: v3.74–v3.75
**Scope**: Shadow deploy membrane validation, Songbird Wave 211 mesh dispatch integration

---

## v3.74 — Wave 47 Audit: Shadow Deploy Membrane Gate

- `composition.deploy.shadow` (dry-run) now validates membrane-model graphs
  with the same `validate_membrane_graph()` gate used by live deploy.
- Previously shadow deploy would report `valid: true` for graphs that live
  deploy would reject due to membrane domain violations.
- `validate_membrane_graph()` visibility elevated to `pub(super)`.
- 1 new test: `shadow_deploy_membrane_graph_flags_compute_violations`.

## v3.75 — Cross-Gate Routing: Songbird Mesh Dispatch Integration

### `try_relay_dispatch()` → `try_songbird_mesh_dispatch()`

Replaced the legacy 2-step cross-gate protocol (`relay.allocate` + custom
forward to relay TCP endpoint) with Songbird's unified `capability.call`
handler from Wave 211.

**Before (v3.73):**
```
biomeOS → relay.allocate on Songbird → get relay TCP endpoint → forward custom payload
```

**After (v3.75):**
```
biomeOS → capability.call { capability, operation, params, routing: "any" } → Songbird UDS
  Songbird → local UDS provider? return
  Songbird → mesh TCP to remote peer? forward with routing: "local" → return
  Songbird → TURN relay fallback? forward → return
```

### Mesh fallback on local discovery failure

Both the translation path and direct discovery path now fall back to Songbird
mesh dispatch when `discover_capability()` finds no local provider. This
enables multi-gate NUCLEUS compositions where primals on remote gates are
reached via Songbird's mesh peer network without requiring explicit gate
registration.

### Response unwrapping

Songbird wraps responses as `{ provider, gate, result }`. biomeOS extracts
the inner `result` for transparent consumer experience.

### Routing contract updated

`specs/CAPABILITY_CALL_ROUTING_CONTRACT.md` documents the Songbird mesh
dispatch tier including wire contract and response unwrapping semantics.

---

## Test Count

| Version | Tests (biomeos-atomic-deploy) | Tests (workspace-wide) |
|---------|-------------------------------|------------------------|
| v3.74   | 1,315                         | 4,304                  |
| v3.75   | 1,315                         | 4,304                  |

All: 0 failures, 0 clippy warnings, fmt PASS.

---

## Files Changed

- `crates/biomeos-atomic-deploy/src/handlers/capability_call.rs` — mesh dispatch
- `crates/biomeos-atomic-deploy/src/handlers/graph/execute.rs` — pub(super) visibility
- `crates/biomeos-atomic-deploy/src/handlers/graph/validation.rs` — membrane gate
- `crates/biomeos-atomic-deploy/src/neural_api_server/routing_tests.rs` — new test
- `specs/CAPABILITY_CALL_ROUTING_CONTRACT.md` — mesh dispatch documentation

---

## Downstream Impact

- **primalSpring**: Both audit items RESOLVED (membrane deploy gate + Songbird
  remote forwarding). Zero upstream blockers remain.
- **Songbird**: Wave 211 `capability.call` handler is now consumed by biomeOS.
  Wire contract aligned: `{ capability, operation, params, routing }`.
- **Multi-gate compositions**: `capability.call` dispatched through biomeOS
  can now transparently reach primals on remote gates via Songbird mesh TCP.
- **nest.sync graph**: Cross-gate orchestration now has a transparent mesh
  path when gates are not pre-registered.

---

**Committed**: v3.74–v3.75 on `main`, pushed via SSH.
