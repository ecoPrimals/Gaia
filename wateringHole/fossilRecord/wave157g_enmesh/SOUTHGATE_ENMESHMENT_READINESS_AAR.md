# southGate AAR — Wave 157g Enmeshment Readiness Assessment

**Date**: Aug 10, 2026 15:40 | **Wave**: 157g | **Gate**: southGate
**Family**: 89df7a2d (southgate-sovereign)
**Mission**: Validate gossip mesh enmeshment readiness. Identify blockers.

---

## EXECUTIVE SUMMARY

southGate is **NOT ENMESHABLE with current depot binaries**. The deployed binaries
predate all gossip injection commits (rhizoCrypt, loamSpine, lithoSpore) and the
process leak fix (coralReef). Additionally, cross-gate TCP is unreachable due to
network topology (different physical subnets), and songBird MeshRelay is not
implemented in the current binary.

**Blockers (3)**:
1. Depot rebuild needed — current binaries lack gossip injection code
2. songBird MeshRelay not shipped — no relay path for cross-gate gossip
3. Network topology — gates on different subnets, WG deliberately OFF

**Non-blockers**: songBird mesh infrastructure is initialized, federation enabled,
relay flag set. Once binaries are rebuilt and MeshRelay ships, southGate is
architecturally ready.

---

## DETAILED FINDINGS

### 1. Depot Binary Gap — Source vs Deployed

The golgi depot has NOT been rebuilt since the gossip injection commits landed.
Current deployed binaries are from the Phase 2 pull (Aug 10 earlier today),
which predates:

| Primal | Source HEAD | Feature | In Depot Binary? |
|--------|-------------|---------|-----------------|
| rhizoCrypt | `4a22c88` | gossip.spread at 3 DAG lifecycle points | **NO** |
| loamSpine | `5db9aa9` | gossip.inject for swarmVine mesh | **NO** |
| lithoSpore | `4ac6cd1` | 4 validation events via gossip.spread | **NO** (not a NUCLEUS binary) |
| coralReef | `34469dc9` | RAII ChildGuard process leak fix | **NO** |
| songBird | `a3400d6f` | test hardening (not MeshRelay) | **NO** (but MeshRelay not shipped at all) |

**Evidence**: rhizoCrypt log shows `method gate: unauthenticated call to protected
method (permissive — allowing) method="gossip.spread"` — the method gate RECOGNIZES
the call but has no handler (binary is older than the implementation).

**Action needed**: sporeGate depot rebuild from Forgejo HEAD.

### 2. Network Topology — Cross-Gate TCP Unreachable

| Peer | Address (from songBird) | Reachable? | Reason |
|------|------------------------|------------|--------|
| west-gate | 10.0.0.5:3492 | **NO** | Different physical network |
| iron-gate | 192.168.1.238:7700 | **NO** | Different subnet (we're 192.168.4.x/22) |
| east-gate | 192.168.1.100:7700 | **NO** | Different subnet |
| south-gate (self) | 192.168.4.29:7700 | N/A | Self |
| WG mesh (10.13.37.x) | :7700, :7800 | **NO** | WG deliberately OFF |
| git.primals.eco:2222 | public DNS | **YES** | Forgejo SSH |
| depot.primals.eco:443 | public DNS | **YES** | Depot HTTPS |

**Our interface**: `192.168.4.148/22` on `enp4s0` (house2 LAN).

**Key insight**: southGate and other gates are on different physical networks
(different houses). Direct TCP between gates requires either:
- WireGuard tunnel (deliberately OFF for validation posture)
- songBird MeshRelay through a public-IP intermediary (golgiBody)
- Port forwarding / NAT traversal

### 3. songBird Mesh State

```
Version: 0.2.1
node_id: "pop-os" (should be "southgate")
Initialized: true
Relay enabled: true
Reachable peers: 4 (all STALE — last seen at boot, 4.1h ago)
Active federation connections: 0
Stale file-based peers: golgiBody (243h), flockGate (243h)
```

**Listening ports**:
- `:7700` — HTTP/riboCipher mesh endpoint (all interfaces)
- `:8091` — Discovery/federation HTTP (all interfaces)
- `:7780` — Internal (localhost only)

**Capability status**:

| Method | Status |
|--------|--------|
| `mesh.peers` | IMPLEMENTED — returns 4 stale peers |
| `mesh.status` | IMPLEMENTED — returns full state |
| `federation.status` | IMPLEMENTED — enabled, 0 connections |
| `mesh.relay` | **NOT IMPLEMENTED** — critical for cross-subnet routing |
| `gossip.subscribe` | **NOT IMPLEMENTED** |
| `gossip.inject` | **NOT IMPLEMENTED** |
| `swarmvine.status` | **NOT IMPLEMENTED** |
| `beacon.status` | **NOT IMPLEMENTED** |

### 4. swarmVine Discovery

- **No swarmVine-specific socket** exists (`*gossip*`, `*swarm*`, `*vine*` — none found)
- The blurb notes "biomeOS connects `.tarpc.sock` instead of JSON-RPC `.sock`" — this
  config issue would affect local gossip routing even if injection code existed
- `SWARMVINE_PEERS` env var: **NOT SET** on southGate
- No gossip-specific environment configuration present

### 5. Local IPC — Still Healthy

Despite enmeshment being blocked, the local NUCLEUS is fully operational:
- 13/13 processes, 43 sockets, 99 MB RSS
- 28 capability sockets responding (avg 0.105ms)
- beardog UDS: 17,595 conn/s, 0.057ms
- GPU: RTX 4060 healthy
- Process leak continues (~38/hr) but doesn't affect functionality

---

## ENMESHMENT READINESS MATRIX

| Requirement | Status | Blocker? |
|-------------|--------|----------|
| NUCLEUS running | ✓ 13/13 GREEN | No |
| gossip injection code deployed | ✗ Binary predates commits | **YES** |
| swarmVine socket available | ✗ Not present | **YES** (depends on biomeOS fix) |
| TCP 7700/7800 cross-gate reachable | ✗ Different subnets | **YES** (needs MeshRelay or WG) |
| songBird MeshRelay | ✗ Not implemented | **YES** |
| songBird federation | ✓ Enabled (0 connections) | No (infrastructure ready) |
| songBird relay_enabled flag | ✓ true | No |
| songBird listening on mesh port | ✓ :7700 all interfaces | No |
| riboCipher Tier 2 on :7700 | ✓ Active (HTTP framing) | No |
| Public endpoint connectivity | ✓ Forgejo + depot reachable | No |
| BTSP security | ✓ All primals enforce | No |

**Verdict**: 6/11 requirements met. 4 blockers remain (all upstream dependencies).

---

## RECOMMENDATIONS TO OVERWATCH

### For immediate enmeshment:

1. **sporeGate: Rebuild depot from HEAD** — This unblocks gossip injection on all
   gates that have already deployed Phase 2. Gates pull new binaries → gossip
   injection activates automatically.

2. **biomeOS: Fix swarmVine socket discovery** — Ensure swarmVine connects to the
   JSON-RPC socket (not `.tarpc.sock`). This enables local gossip routing.

3. **songBird: Ship MeshRelay** — Without this, gates on different physical networks
   cannot gossip. MeshRelay through golgiBody's public IP is the critical path for
   southGate (and likely ironGate, depending on topology).

4. **node_id configuration** — songBird reports `node_id: "pop-os"` instead of
   `"southgate"`. Should be set via env var or config for mesh identity.

### southGate-specific:

5. **WireGuard enrollment (optional fast-path)** — If WG were activated, cross-gate
   TCP would work immediately without waiting for MeshRelay. However, this contradicts
   the validation gate posture (proving system works WITHOUT WG).

6. **Process leak** — Still ~38/hr (depot binary predates RAII fix). Rebuild unblocks
   this too.

---

## WHAT SOUTHGATE CAN DO NOW

While waiting for upstream (depot rebuild + MeshRelay):

| Capability | Status | Notes |
|------------|--------|-------|
| Performance canary | ✓ ACTIVE | Baseline established, monitoring |
| GPU compute (QCD) | ✓ AVAILABLE | RTX 4060, 17.6K conn/s IPC |
| Local IPC validation | ✓ PROVEN | 28 sockets, sub-0.2ms |
| BTSP trust boundary | ✓ PROVEN | All primals enforce |
| Depot binary testing | ✓ READY | Will pull immediately when rebuilt |
| Gossip enmeshment | ✗ BLOCKED | Waiting on depot rebuild + MeshRelay |
| Cross-gate federation | ✗ BLOCKED | Waiting on MeshRelay or WG |

---

*southGate Wave 157g — Enmeshment assessment complete. 4 blockers identified (all
upstream). Local NUCLEUS healthy. Ready to enmesh immediately once depot rebuilds
and MeshRelay ships. Performance canary + GPU compute available now.*
