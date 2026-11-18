# primalSpring Wave 74 — capability.call Validation Results

**Date**: 2026-06-03
**Gate**: eastGate
**Operator**: gate agent (primalSpring evolution team)
**Status**: P0 HTTP PROTOCOL VALIDATED — capability routing layer has P1 gap

## Summary

Rebuilt Songbird from `d6a6f714` (HTTP dispatch fix). The protocol transport
layer is **fixed** — HTTP POST to `/jsonrpc` works end-to-end. LOCAL
`capability.call` works through to provider (bearDog responds). Cross-gate
routing is blocked on a **capability advertisement propagation gap** — peers
don't advertise their registered capabilities through the mesh federation.

## Validated (working)

| Check | Status | Detail |
|-------|--------|--------|
| Songbird d6a6f714 build | PASS | Release binary built, deployed to eastGate + strandGate |
| HTTP POST to /jsonrpc | PASS | No more "Invalid JSON from remote" errors |
| ipc.register | PASS | Providers register on both UDS and HTTP endpoints |
| capability.call LOCAL | PASS | bearDog health responds: `status: healthy, version: 0.9.0` |
| capability.call via HTTP | PASS | Direct HTTP POST to strandGate:7700/jsonrpc resolves locally |
| mesh.init bidirectional | PASS | Both gates initialized, health_check all_healthy |
| discovery.peers | PASS | strandGate visible, quality 1.0, direct path |

## Remaining Gap: Capability Advertisement Propagation (P1)

### Symptom

```json
{"error":{"code":-32603,"message":"No local or remote provider found for capability 'strand-only' (tried 1 mesh peers via TCP and TURN relay; last error: )"}}
```

### Root Cause

`discovery.peers` returns `capabilities: []` for all remote peers. When
eastGate's `capability.call` looks for a remote provider, it checks the
peer's advertised capabilities. Since these are always empty, no remote
dispatch is attempted — even when the provider IS registered on the remote
gate's HTTP endpoint.

`discovery.announce` is called and returns `announced: true`, but the
capability list is NOT propagated to remote peers' `discovery.peers` response.

### Secondary Issue: HTTP/UDS State Isolation

Songbird's HTTP endpoint (port 7700) maintains **separate state** from the
UDS endpoint. Registering via UDS is invisible to HTTP, and vice versa.
Both `ipc.register` and `mesh.init` must be called on BOTH endpoints.

### Workaround (manual)

For each capability on each gate, register via BOTH transports:

```bash
# Via UDS (for local callers)
echo '{"method":"ipc.register","params":{"primal_id":"beardog","capabilities":["security"],"endpoint":"unix:///run/user/1000/biomeos/beardog-eastgate.sock"}}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird.sock

# Via HTTP (for remote callers hitting this gate)
curl -X POST http://192.168.1.144:7700/jsonrpc \
  -d '{"method":"ipc.register","params":{"primal_id":"beardog","capabilities":["security"],"endpoint":"unix:///run/user/1000/biomeos/beardog-eastgate.sock"}}'
```

## Updated Upstream Gaps (Songbird)

| # | Item | Priority | Status | Blocks |
|---|------|----------|--------|--------|
| 1 | HTTP dispatch (raw TCP → HTTP POST) | P1 | **FIXED** (d6a6f714) | — |
| 2 | Capability advertisement propagation via mesh | P1 | **OPEN** | Cross-gate routing |
| 3 | HTTP/UDS state unification | P1 | **OPEN** | Single registration point |
| 4 | `mesh_seed` auto-bootstrap | P1 | NOT FIXED | Zero-config mesh |
| 5 | `latency_ms` population | P2 | NOT FIXED | Quality metrics |

## primalSpring Deliveries (Wave 74)

| Item | Status | Test Count |
|------|--------|------------|
| Perceptron feature extraction (36-dim) | COMPLETE | 12 tests |
| MeshTopology model | COMPLETE | 7 tests |
| Plasmodium collective scenario | COMPLETE | 2 tests |
| SecurityVerifier bearDog w131 integration | COMPLETE | 7 tests |
| CompositionContext gate_id | COMPLETE | — |
| westGate enrollment FRAGO | FILED | — |
| **Total** | **833 tests, zero clippy** | |

## Live Scenario Results

### s_covalent_mesh

```
Phase 1: Structural — 4/4 PASS
Phase 2: Discovery — 3/3 PASS, 1 SKIP (latency_ms)
Phase 3: Cross-gate — 7/7 SKIP (capability routing gap)
Result: ALL PASS (7/7 checks, 8 skipped)
```

### plasmodium-collective

```
Phase 1: Structural — 6/6 PASS
Phase 2: Live discovery — 3/3 PASS, 2 SKIP (iron-gate + quorum)
Phase 3: Cross-gate — 2/2 SKIP (known gaps)
Result: 9/10 PASS (4 skipped)
```

## Next Steps

1. **Songbird P1**: Capability advertisement propagation — peers must share
   their registered capabilities via mesh federation protocol
2. **Songbird P1**: Unify HTTP/UDS endpoint state (single IPC registry + mesh)
3. **After fix**: Re-run Phase 3 with proper capability propagation
4. **ironGate**: Add to SONGBIRD_PEERS once capability routing works
5. **Perceptron pipeline**: Wire feature extraction to barraCuda ml.mlp_train

## Files This Wave

| Repo | Commit | Description |
|------|--------|-------------|
| primalSpring | `7d9de44` | Wave 73: perceptron + mesh topology + enrollment |
| primalSpring | `6842d79` | Wave 74: plasmodium scenario + SecurityVerifier + gate_id |
| wateringHole | `3dcec02` | westGate enrollment FRAGO |
