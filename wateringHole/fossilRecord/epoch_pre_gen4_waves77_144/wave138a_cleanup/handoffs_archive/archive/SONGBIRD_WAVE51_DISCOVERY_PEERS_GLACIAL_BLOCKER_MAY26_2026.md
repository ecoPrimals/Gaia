# Songbird Wave 51 — `discovery.peers` Glacial Blocker Resolution

**Date**: May 26, 2026  
**Primal**: Songbird v0.2.1  
**Audit**: Wave 51/primalSpring  
**Impact**: Unblocks stadial entry, covalent HPC, cellMembrane multi-host NUCLEUS

---

## Problem

`discovery.peers` returned empty across all 4 operational gates despite successful
`mesh.init` with `bootstrap_peers`. This blocked:
- Cross-gate `capability.call` routing
- Covalent HPC formation
- cellMembrane multi-host NUCLEUS mesh layer
- primalSpring `s_covalent_mesh` validation scenario

---

## Root Causes Fixed

### 1. Orchestrator dispatch gap (Wave 50 fix, pushed earlier)

The orchestrator's `pure_rust_server` dispatch table routed `discovery.peers` to a
registry-only query, bypassing the mesh entirely. Fixed by wiring `discovery_peers_json()`
which merges results from `mesh_handler.handle_peers()` + registry, de-duplicating by node_id.

### 2. No auto-seeding from environment (Wave 51 — this fix)

Gates set `SONGBIRD_PEERS` but nothing consumed it on startup. An external `mesh.init` RPC
call was required before `discovery.peers` could populate.

**New**: `mesh_seed` module reads `SONGBIRD_PEERS` on startup and auto-initializes the mesh.
Zero-config — peers appear in `discovery.peers` immediately on boot.

### 3. Format mismatch (Wave 51 — this fix)

Existing handoff docs documented `SONGBIRD_PEERS=192.168.1.144:7700,192.168.1.238:7700`
(address-only), but the initial parser only accepted `node_id@host:port`.

**New**: Parser supports both formats. Bare addresses get auto-generated node_id (`peer-{ip}`).

### 4. Hardcoded port in remote dispatch (Wave 51 — refactoring)

`forward_to_remote_gate` used `DEFAULT_HTTP_PORT` (8080) for all peers regardless of their
advertised port. Added `EndpointType::socket_addr()` — peers are now contacted on their
actual advertised port.

---

## What Shipped

| Item | Crate | Tests |
|------|-------|-------|
| `mesh_seed` module (auto-seeding) | `songbird-orchestrator` | 7 unit + 1 E2E |
| `SONGBIRD_PEERS` + `SONGBIRD_NODE_ID` env vars | `songbird-orchestrator` | — |
| Dual format parser (`node@host:port` + `host:port`) | `songbird-orchestrator` | 4 parser tests |
| `discovery_peers_json()` merge | `songbird-orchestrator` | 1 E2E |
| `DiscoveryHandler` mesh bridge | `songbird-universal-ipc` | 1 E2E |
| `remote_dispatch.rs` extraction (906→614L) | `songbird-universal-ipc` | existing tests |
| `EndpointType::socket_addr()` | `songbird-onion-relay` | — |
| `--peers` flag in `nucleus_launcher.sh` | `infra/plasmidBin` | — |

---

## Operator Actions Required

For gates to immediately have working `discovery.peers`:

```bash
# Option A: Set env var before starting Songbird
export SONGBIRD_PEERS="iron-gate@192.168.1.238:7700,south-gate@192.168.4.29:7700"
export SONGBIRD_NODE_ID="east-gate"

# Option B: Use nucleus_launcher --peers flag
./nucleus_launcher.sh --family-id abc123 --peers "iron-gate@192.168.1.238:7700"

# Option C: Bare address format (backward compat)
export SONGBIRD_PEERS="192.168.1.238:7700,192.168.4.29:7700"
```

After Songbird starts, verify:
```bash
echo '{"jsonrpc":"2.0","method":"discovery.peers","params":{},"id":1}' | nc -q1 127.0.0.1 7700
# Expected: {"result":{"peers":[...], "total_count": N}}  where N > 0
```

---

## Validation Path

primalSpring scenarios ready to validate:
- `s_covalent_mesh` — `discovery.peers` returns peer_count > 0
- `s_cross_gate_capability_call` — `capability.call` routes to remote gate

**Next step**: Rebuild Songbird from plasmidBin on eastGate + ironGate, set `SONGBIRD_PEERS`
on both, run primalSpring live validation.

---

## Commits

1. `38871a08` — `feat(mesh): auto-seed peers from SONGBIRD_PEERS env var on startup`
2. `9a3912bd` — `fix(mesh_seed): support address-only SONGBIRD_PEERS format`
3. `5e81f0d0` — `refactor(ipc): extract remote_dispatch module + evolve port hardcoding`
