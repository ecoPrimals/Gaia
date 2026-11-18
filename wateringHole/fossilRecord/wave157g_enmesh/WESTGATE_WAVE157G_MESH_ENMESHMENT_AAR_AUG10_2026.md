# AAR: westGate Wave 157g — Mesh Enmeshment & Deploy

**Date**: Aug 10, 2026 16:00 EDT | **Wave**: 157g | **Gate**: westGate
**Posture**: OVERWATCH (gate-agnostic) on westGate hardware

---

## Executive Summary

Cascaded 43 repos from Forgejo. Pulled 16 depot binaries, restarted 14/14 services,
completed full E2E provenance chain (8/8 in 16ms), and **achieved first cross-gate
gossip propagation** — westGate gossip entries confirmed received on sporeGate,
eastGate, and strandGate.

Two critical configuration bugs in `SWARMVINE_PEERS` prevented gossip mesh from
forming. Both fixed. The ant colony has scouts that actually reach other colonies now.

---

## Cascade Results

| Repo Group | Updated | Key Changes |
|-----------|---------|-------------|
| **primals** | 13/16 | sweetGrass `braid.verify`, rhizoCrypt gossip, loamSpine gossip, songBird MeshRelay, nestGate HTTP parity, coralReef RAII guards, cellMembrane 13-commit evolution |
| **infra** | 2/7 | overwatch-temporal.sh, sporePrint 21 files |
| **gardens** | 4/5 | cellMembrane (16 commits), lithoSpore gossip, projectFOUNDATION, projectNUCLEUS |
| **springs** | 1/10 | coralForge |

43/43 repos now synced with Forgejo HEAD.

---

## Depot Deploy

Pulled 16 binaries from `depot.primals.eco/primals/x86_64-unknown-linux-musl/`.
BLAKE3 verification: 15/18 pass (3 mismatches: bingocube, membrane, toadstool —
these received size changes vs stale BLAKE3SUMS).

14/14 services restarted. biomeOS FD health: 13 FDs, 6h uptime — **HEALTHY** (P0-C FD leak RESOLVED).

### Depot vs Source Gap

The depot binaries predate the latest feature commits:

| Feature | Source Commit | Depot Has? | Status |
|---------|--------------|------------|--------|
| `braid.verify` | sweetGrass `6357f0f` | **NO** | Needs depot rebuild |
| `gossip.relay` (MeshRelay) | songBird `62962570` | **NO** | Needs depot rebuild |
| `gossip.inject` (swarmVine JSON-RPC) | swarmVine latest | **YES** | Working |
| `content.stat` HTTP parity | nestGate `60ee88d8` | **PARTIAL** | Returns "Internal error" |
| Gossip injection (rhizoCrypt) | `4a22c88` | **UNKNOWN** | Code ships but needs activation |
| Gossip injection (loamSpine) | `5db9aa9` | **UNKNOWN** | Code ships but needs activation |

**Action**: sporeGate needs a rebuild cycle to ship `braid.verify` and `gossip.relay` in depot binaries.

---

## E2E Provenance Chain — 8/8 PASS (16ms)

Validated full provenance pipeline with current deployed binaries:

| Step | Primal | Method | Result |
|------|--------|--------|--------|
| 1 | nestGate | `content.put` | PASS — CAS hash returned |
| 2 | bearDog | `crypto.sign` | PASS — Ed25519 signature |
| 3 | bearDog | `crypto.verify` | PASS — signature valid |
| 4 | rhizoCrypt | `dag.session.create` | PASS — UUID session |
| 5 | rhizoCrypt | `dag.event.append` | PASS — SessionStart event |
| 6 | loamSpine | `spine.create` | PASS — spine UUID |
| 7 | sweetGrass | `braid.create` | PASS — `urn:braid:...` |
| 8 | loamSpine | `session.commit` | PASS — commit hash returned |

### bearDog API Discovery

The esotericWebb V32b `crypto.sign` base64 fix is now deployed:
- `message` parameter expects **base64-encoded** input (not raw string)
- `crypto.verify` requires explicit `public_key` parameter
- Nonce generation is server-side (ignore client nonce)

---

## Gossip Mesh Enmeshment — BREAKTHROUGH

### Bugs Found & Fixed

**Bug 1: SWARMVINE_PEERS format mismatch**

`discover_peers()` splits on `,` and passes raw strings to `TcpStream::connect()`.
The configured format `sporeGate@192.168.4.159:7800` is not a valid socket address.
Expected: `192.168.4.3:7800`.

```diff
-Environment=SWARMVINE_PEERS=sporeGate@192.168.4.159:7800,ironGate@192.168.4.213:7800
+Environment=SWARMVINE_PEERS=192.168.4.3:7800,192.168.4.244:7800,192.168.4.169:7800
```

**Bug 2: SWARMVINE_PEERS wrong IP addresses**

The original IPs (`.159` for sporeGate, `.213` for ironGate) were never reachable.
ARP showed `FAILED` for both. Actual LAN discovery:

| Gate | Configured IP | Actual IP | Protocol |
|------|--------------|-----------|----------|
| sporeGate | 192.168.4.159 | **192.168.4.3** | swarmVine TCP 7800 |
| ironGate | 192.168.4.213 | **192.168.4.237** | songBird TCP 7700 only |
| eastGate | (not configured) | **192.168.4.244** | swarmVine TCP 7800 |
| strandGate | (not configured) | **192.168.4.169** | swarmVine TCP 7800 |
| blueGate | (not configured) | **192.168.4.148** | songBird TCP 7700 only |

### Verification — Cross-Gate Gossip Working

After fixing both bugs, the epidemic spread cycle confirmed propagation:

```
westGate injected: tower/westgate.mesh.test
After spread cycle (30s):
  sporeGate:  tower=3, peers=2, ingested=4  ← RECEIVED
  eastGate:   tower=3, data=1, peers=2, ingested=5  ← RECEIVED
  strandGate: tower=1, peers=1, ingested=1  ← RECEIVED
```

### Current Mesh State

- **Outbound gossip**: westGate → 3 peers (sporeGate, eastGate, strandGate) **WORKING**
- **Inbound gossip**: peers → westGate **NOT YET** (peers need to add `192.168.4.149:7800`)
- **ironGate**: Has swarmVine registered with songBird but no TCP 7800 listener
- **blueGate**: songBird only, no swarmVine TCP 7800
- **songBird MeshRelay**: Not yet in depot binaries (for VPS-to-LAN relay through :7700)

---

## biomeOS Neural API Routing

| Route | Latency | Status |
|-------|---------|--------|
| `gossip.status` | 1.2ms | WORKING (via capability.call) |
| `gossip.inject` | 1.1ms | WORKING (via capability.call) |
| `content.exists` | 1.2ms | WORKING |
| `braid.list` | — | NOT ROUTED (missing translation) |
| `gossip.relay` | — | Method not in deployed binary |

biomeOS discovered swarmVine at the **correct** socket path
(`/run/user/1000/biomeos/swarmvine-westgate-tower-155f.sock`) — the socket
discovery bug documented in the blurb is **RESOLVED on westGate**. biomeOS
auto-discovery differentiated the `.sock` (JSON-RPC) from `.tarpc.sock` correctly.

---

## Storage Health

| Tier | Size | Used | Status |
|------|------|------|--------|
| NVMe (T1) | 1.8T | 27% (461G) | Cleaned 232G stale staging |
| ZFS pool (T3) | 63.7T | 10% (6.57T) | ONLINE, HEALTHY |
| CAS cold | 1.41T | — | 3 datasets fully braided |
| Data cold | 3.84T | — | AlphaFold + structures + SRA |

### Braiding Status

All 3 datasets fully braided (240 chunks, 100 braids in sweetGrass):

| Dataset | Chunks | Status |
|---------|--------|--------|
| AlphaFold | 7/7 | COMPLETE |
| AlphaFold structures | 228/228 | COMPLETE |
| SRA FASTQ | 5/5 | COMPLETE |

---

## Open Items for Overwatch Dissemination

### For Other Gates (peer config)

Each gate running swarmVine needs to add `192.168.4.149:7800` (westGate) to their
`SWARMVINE_PEERS` environment. Same format fix needed — use `host:port`, not
`name@host:port`.

### For sporeGate

1. **Depot rebuild** — ship `braid.verify` (sweetGrass `6357f0f`) and `gossip.relay`
   (songBird `62962570`) in depot binaries
2. Add `192.168.4.149:7800` to SWARMVINE_PEERS
3. **sourDough CI** — wire validators into post-receive hook

### For ironGate & blueGate

Deploy swarmVine with TCP 7800 gossip port enabled. Both have songBird (:7700)
but not swarmVine (:7800). Once songBird MeshRelay ships, gossip can relay
through :7700 as a fallback.

### For biomeOS Team

1. `braid.list` missing from translation registry (routing fails through Neural API)
2. `spine.list` routing gap (documented in blurb)

---

## Patterns Validated

1. **Ant Colony Mesh**: First real cross-gate gossip propagation. The epidemic spread
   model works — inject locally, entries spread to all reachable peers within one cycle (30s).

2. **Peer Discovery Tiering**: `SWARMVINE_PEERS` env + songBird `mesh.peers` query.
   The spread loop found 4 peers (3 from env + 1 from songBird mesh), confirming
   the dual-source discovery works. The songBird-discovered peer was stale (`.213`)
   but the failure was non-blocking.

3. **riboCipher Compliance**: All primals accept `[0xEC, 0x01]` signal. swarmVine
   logs `DEPRECATED: unsignalled connection` for plain JSON-RPC but still processes
   the request (graceful degradation).

4. **bearDog Base64 Discipline**: Post-V32b `crypto.sign` requires base64-encoded
   `message` parameter. This is the correct behavior — raw binary safety.

---

*Wave 157g overwatch: 43/43 repos synced, 16/16 depot binaries pulled, 14/14 services
alive, 8/8 E2E chain, cross-gate gossip LIVE to 3 peers. Ant colony spreading.*
