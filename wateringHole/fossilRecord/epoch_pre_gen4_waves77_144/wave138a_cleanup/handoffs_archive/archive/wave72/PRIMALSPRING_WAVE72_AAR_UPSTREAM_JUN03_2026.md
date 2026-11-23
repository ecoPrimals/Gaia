# primalSpring Wave 72 — After Action Review (Upstream Dissemination)

**Date**: 2026-06-03
**Author**: eastGate (primalSpring overwatch)
**Audience**: All upstream primal teams
**Wave**: 72
**Status**: P0 mesh PARTIALLY VALIDATED — discovery layer LIVE, dispatch layer BLOCKED on Songbird

---

## TL;DR

First live 2-gate mesh between eastGate and strandGate is operational.
`discovery.peers` works. `mesh.health_check` is bidirectional. Cross-gate
`capability.call` is blocked on a Songbird wire protocol mismatch. DNS
infrastructure is validated and ready for registrar flip. strandGate is
picking up compute trio from paused biomeGate.

---

## What's Working

### 1. Songbird Discovery Layer (LIVE)

| Metric | Value |
|--------|-------|
| Peer count | 1 (strand-gate) |
| Quality | 1.0 (direct path, same subnet) |
| Protocols | TCP |
| Health check | Bidirectional healthy |
| Subnet | 192.168.1.0/24 (eastGate .144, strandGate .132) |

```json
{"peers":[{"address":"192.168.1.132:7700","node_id":"strand-gate","quality":1.0,"protocols":["tcp"]}],"total_count":1}
```

`mesh.health_check` from both sides returns `all_healthy: true`.

### 2. BearDog v0.9.0 Cross-Gate Deployment

Successfully deployed eastGate's bearDog binary to strandGate via SCP.
Both gates running Pure Rust HSM (Ed25519, X25519, ChaCha20-Poly1305, Blake3).
Security sockets operational on both gates.

### 3. primalSpring Scenario Infrastructure

`s_covalent_mesh` scenario now runs live against real Songbird instances.
Phase 1 (structural) + Phase 2 (discovery) fully pass. Phase 3 (cross-gate
dispatch) gracefully degrades with informative skip messages.

Updated scenario to accept Songbird's actual wire format (`node_id` field
alongside deprecated `gate` field).

### 4. Capability Discovery via Symlinks

The capability-based discovery system works when standard symlinks exist:
```
/run/user/1000/biomeos/discovery.sock     → songbird.sock
/run/user/1000/biomeos/orchestration.sock → songbird.sock
/run/user/1000/biomeos/security.sock      → beardog-{family}.sock
```

### 5. DNS Sovereign Infrastructure

Both nameservers (ns1: [RELAY_PUBLIC], ns2: 137.184.197.151) responding
correctly to A and NS queries. Zone transfer confirmed in sync. Ready
for registrar cutover (operator action only).

### 6. 842 Tests, Zero Clippy, forbid(unsafe_code)

primalSpring v0.9.31 remains at full quality bar. The scenario wire format
fix adds no regressions.

---

## What's Rough

### 1. Songbird `capability.call` Remote Dispatch (P1 BLOCKER)

**Symptom**: `capability.call` to a remote gate returns:
```
No local or remote provider found for capability 'security'
(tried 1 mesh peers via TCP and TURN relay; last error:
Invalid JSON from remote gate: expected value at line 1 column 1)
```

**Root cause**: Songbird's `remote_dispatch.rs` sends raw TCP JSON-RPC frames
to the peer's port 7700. But port 7700 is an HTTP server (axum/hyper). The
peer returns an HTTP status line, which isn't valid JSON.

**Fix needed**: Remote dispatch must HTTP POST to `/jsonrpc` endpoint, not raw TCP.

**Impact**: Cross-gate capability routing is completely non-functional. This
blocks plasmodium collective validation and any multi-gate science dispatch.

### 2. `mesh_seed` Auto-Bootstrap Not Firing (P1)

**Symptom**: Setting `SONGBIRD_PEERS=strand-gate@192.168.1.132:7700` and
`SONGBIRD_NODE_ID=east-gate` before starting Songbird results in:
```
Running in standalone mode (federation disabled)
```
Peers are NOT auto-populated. Manual `mesh.init` RPC is required.

**Root cause**: The `mesh_seed` module exists in source (`songbird-orchestrator`)
but is not wired into the server startup path in binary v0.2.1. The
`federation_setup` code path runs before security initialization and defaults
to standalone when no federation hub is detected.

**Workaround**: Manual RPC after startup:
```json
{"method":"mesh.init","params":{"node_id":"east-gate","bootstrap_peers":[{"node_id":"strand-gate","address":"192.168.1.132:7700"}]}}
```

**Note**: The `bootstrap_peers` parameter must be an **array of objects** with
`node_id` and `address` fields. String format (`["strand-gate@192.168.1.132:7700"]`)
is silently rejected with `bootstrap_peers_added: 0`.

### 3. `latency_ms` Not Populated (P2)

`discovery.peers` returns `latency_ms: null` for all peers. The
`mesh.health_check` also shows `latency_ms: null`. HTTP-based latency
probing (the fix shipped in Songbird's `mesh.probe_latency`) isn't being
invoked during health checks.

### 4. Cross-Subnet Routing (Infra — P2)

southGate (192.168.4.29) is unreachable from eastGate subnet (192.168.1.x).
The Eero mesh bridge does NOT route between VLANs. Options:
- Eero inter-VLAN config (physical operator action)
- TURN relay via VPS (Songbird has `relay.serve`)
- Continue with strandGate (same subnet) as primary partner

Mitigated by using strandGate for initial validation.

### 5. Service Startup Ergonomics (P3)

Starting the mesh requires 5+ manual steps:
1. Start bearDog with correct env vars (`FAMILY_ID`, `NODE_ID`)
2. Create capability symlinks
3. Start Songbird with 6 env vars + correct flags
4. Send `mesh.init` RPC with object-format peers
5. Create discovery/orchestration symlinks

This should be a single `plasmidbin launch` command with auto-configuration.

### 6. biomeOS `SONGBIRD_MESH_ENABLED` vs Songbird's Federation Logic

biomeOS Wave 73 handoff says to use `SONGBIRD_MESH_ENABLED=true`. Songbird
v0.2.1 doesn't recognize this env var — it uses `SONGBIRD_FEDERATION_ENABLED`.
Neither actually enables federation in the binary. Need alignment.

---

## Upstream Actions Required

### Songbird Team (P1 — Critical Path)

| # | Item | Priority | Blocks |
|---|------|----------|--------|
| 1 | Fix `remote_dispatch.rs` to HTTP POST `/jsonrpc` for cross-gate calls | P1 | All cross-gate capability routing |
| 2 | Wire `mesh_seed` into server startup so `SONGBIRD_PEERS` auto-seeds | P1 | Zero-config mesh formation |
| 3 | Align `mesh.init` string format parsing with `mesh_seed`'s object format | P2 | Consistent API |
| 4 | Populate `latency_ms` in `discovery.peers` via HTTP probing | P2 | Mesh quality metrics |
| 5 | Align env var naming with biomeOS (`SONGBIRD_MESH_ENABLED`) | P3 | Cross-team consistency |

### biomeOS Team (southGate)

| # | Item | Priority | Blocks |
|---|------|----------|--------|
| 1 | `gate.register` validation with eastGate (once Songbird dispatch fixed) | P1 | Multi-gate mesh |
| 2 | Verify `SONGBIRD_MESH_ENABLED` works with Songbird's actual env vars | P2 | southGate mesh join |
| 3 | Cross-subnet route to eastGate (Eero config or TURN) | P2 | southGate direct connectivity |

### bearDog Team

| # | Item | Priority | Blocks |
|---|------|----------|--------|
| 1 | `auth.verify_ionic` needs `scopes` array in response (never omit) | P1 | SecurityVerifier in Enforced mode |
| 2 | Standardize `health.liveness` method (currently returns -32601) | P3 | Cross-primal health probing |

### strandGate Team

| # | Item | Priority | Blocks |
|---|------|----------|--------|
| 1 | Accept compute trio FRAGO (barraCuda + coralReef SPIR-V) | P2 | Perceptron pipeline |
| 2 | Keep bearDog v0.9.0 (deployed from eastGate) running for mesh | — | Mesh continuity |

### projectNUCLEUS / plasmidBin

| # | Item | Priority | Blocks |
|---|------|----------|--------|
| 1 | `plasmidbin launch` should auto-create capability symlinks | P2 | Startup ergonomics |
| 2 | `plasmidbin install songbird` — rebuild with `mesh_seed` wired in | P1 | Zero-config mesh |

---

## Mesh Validation Progression

```
Wave 49: Scenario written, no live test
Wave 51: mesh_seed module shipped, format parser fixed
Wave 55: southGate federation attempted, cross-subnet failed
Wave 67: strandGate auto-discovered via UDP broadcast, TLS handshake failed
Wave 72: ██████████░░░░ 70% — discovery LIVE, dispatch BLOCKED  ← YOU ARE HERE
Wave 73: Target — capability.call cross-gate (needs Songbird fix)
Wave 74: Target — 3-gate plasmodium collective (+ ironGate)
```

---

## Operational Runbook (Current State)

### Start Mesh on eastGate

```bash
# 1. BearDog
FAMILY_ID=eastgate NODE_ID=tower1 beardog server \
  --socket /run/user/1000/biomeos/beardog-eastgate.sock \
  --family-id eastgate --orchestrator-id east-gate &

# 2. Security symlink
ln -sf /run/user/1000/biomeos/beardog-eastgate.sock /run/user/1000/biomeos/security.sock

# 3. Songbird
SONGBIRD_NODE_ID=east-gate \
SONGBIRD_PEERS="strand-gate@192.168.1.132:7700" \
SONGBIRD_FEDERATION_PORT=7700 \
SONGBIRD_FEDERATION_ENABLED=true \
SECURITY_ENDPOINT="http://127.0.0.1:9900" \
FAMILY_ID=eastgate \
songbird server --federation-port 7700 --bind 0.0.0.0 \
  --socket /run/user/1000/biomeos/songbird.sock &

# 4. Capability symlinks
ln -sf /run/user/1000/biomeos/songbird.sock /run/user/1000/biomeos/discovery.sock
ln -sf /run/user/1000/biomeos/songbird.sock /run/user/1000/biomeos/orchestration.sock

# 5. Bootstrap mesh (required until mesh_seed is fixed)
sleep 3
echo '{"jsonrpc":"2.0","method":"mesh.init","params":{"node_id":"east-gate","bootstrap_peers":[{"node_id":"strand-gate","address":"192.168.1.132:7700"}]},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird.sock
```

### Verify

```bash
# Peers visible
echo '{"jsonrpc":"2.0","method":"discovery.peers","params":{},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird.sock
# Expected: total_count > 0

# Health check bidirectional
echo '{"jsonrpc":"2.0","method":"mesh.health_check","params":{},"id":1}' \
  | socat - UNIX-CONNECT:/run/user/1000/biomeos/songbird.sock
# Expected: all_healthy: true
```

---

## DNS Cutover Status

| Check | Status |
|-------|--------|
| ns1 ([RELAY_PUBLIC]) responding | ✓ |
| ns2 (137.184.197.151) responding | ✓ |
| Zone serial in sync | ✓ |
| membrane.primals.eco resolves | ✓ (→ [RELAY_PUBLIC]) |
| primals.eco A resolves | ✓ (→ 137.184.197.151, GitHub Pages) |
| Registrar action | PENDING (operator toggles Cloudflare NS) |

**Sequence**: Remove Cloudflare NS → Add ns1/ns2 with glue → Verify 24h → Add DS record.

---

## Files Committed This Wave

| Repo | Commit | Description |
|------|--------|-------------|
| primalSpring | `bb017e9` | `s_covalent_mesh.rs` wire format fix (accept `node_id`) |
| wateringHole | `ae81eab` | Live mesh validation handoff |
| ecoPrimals | `966f56e4` | Submodule ref update |

---

*This AAR is intended for upstream ingestion and dissemination. All teams
should review their action items above. Songbird items 1-2 are the critical
path to completing the glacial mesh validation.*
