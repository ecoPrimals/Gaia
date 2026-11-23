# Inner Membrane Pure Primals Spec

**Date**: Aug 8, 2026 | **Wave**: 157a | **From**: sporeGate (eastGate overwatch)
**Status**: ACTIVE — Phase 1 mesh connectivity DONE, Phases 2-3 require multi-team code evolution
**Depends**: LAN_FIRST_TOWER_TRANSPORT_SPEC.md, RIBOCIPHER_TRANSPORT_SIGNAL_STANDARD.md, NEURAL_API_ACTIVATION_SPEC.md

---

## Problem Statement

Inner membrane communication still relies on WireGuard tunnels and SSH for:
- Gate-to-gate health checks (SSH → curl)
- Depot binary distribution (SSH rsync)
- NUCLEUS bootstrap (SSH → systemctl)
- Data access across gates (SSH → socket)

WG+SSH is an **early sovereign pattern** — outer membrane access for human operators. Inner membrane should be **pure primals**: Tower Atomic mesh handles all inter-gate primal communication without WG or SSH in the path.

## Three Gaps

### Gap 1: Sparse Mesh — RESOLVED (Phase 1)

**Before** (Aug 8, 09:00):
- sporeGate songBird: 6 peers (westGate MISSING, southGate MISSING)
- strandGate songBird: 1 peer (golgi only — cross-house isolation)

**After** (Aug 8, 10:15):
- sporeGate songBird: 8 peers including westGate (LAN, reachable)
- strandGate songBird: 5 peers (was 1 — sporeGate, westGate, blueGate, ironGate, golgi)

**Fix applied**: `SONGBIRD_LOCAL_PEERS` env var in songBird systemd units. Format:
```
SONGBIRD_LOCAL_PEERS=gateName@ip:7700,gateName2@ip2:7700
```
This seeds explicit LAN peers for gates that can't discover each other via birdsong multicast (cross-house, different broadcast domains).

**Remaining**: southGate not discoverable on LAN (may be powered off or services not bound to TCP). When online, add to `SONGBIRD_LOCAL_PEERS` on neighboring gates.

### Gap 2: riboCipher Tier 2 (`0xED`) Not Operational Cross-Gate

#### Current state

| Primal | Tier 1 `0xEC` (clear) | Tier 2 `0xED` (mito) | Tier 3 `0xEE` (nuclear) |
|--------|:---------------------:|:---------------------:|:-----------------------:|
| bearDog | FULL | FULL (`decode_mito_tag`) | Recognized, closed |
| songBird | FULL | Constants defined, not decoded | Not impl |
| skunkBat | FULL | REJECT | REJECT |
| biomeOS | FULL | Not impl | Not impl |
| All others | FULL | Not impl | Not impl |

Tier 1 (`0xEC`) works for **same-gate** UDS communication. Tier 2 (`0xED`) is required for **cross-gate** WAN/LAN communication where the wire is untrusted (even on LAN — defense in depth). Only bearDog can decode `0xED` today.

#### What each team needs to do

**bearDog team**: Expose `decode_mito_tag()` as a capability via Neural API:
- Method: `crypto.ribocipher.decode_mito` or `genetic.decode_mito_tag`
- Input: 4-byte HMAC tag from `0xED` envelope
- Output: decoded protocol type (0x01 NDJSON, 0x03 BTSP, etc.)
- This lets any primal validate `0xED` frames by delegating to bearDog

**songBird team** (critical path): Accept `0xED` on federation port (:7700):
- Current: federation port handles birdsong protocol only
- Needed: accept `0xED` connections, delegate HMAC decode to bearDog, then route inner protocol
- Wire flow for cross-gate RPC:
```
  Caller gate's songBird → [0xED][hmac_tag:4] → Remote gate's songBird
  Remote songBird → bearDog.decode_mito_tag(tag) → protocol_type
  Remote songBird → route to local primal socket → response → relay back
```

**skunkBat team**: Evolve from REJECT to delegate-and-route for `0xED`:
- Current: `0xED` → `ConnectionIntent::Reject`
- Needed: `0xED` → bearDog.decode → route (or reject if HMAC invalid)

### Gap 3: Cross-Gate Capability Federation

#### Current state

westGate registered 26 capabilities with its local songBird (NG-05). `capability.resolve("content.get")` works on westGate. But sporeGate's Neural API **cannot resolve capabilities hosted on westGate**.

Each gate's capability registry is local-only. No gossip, no mesh broadcast, no federated resolution.

#### What each team needs to do

**songBird team**: Capability gossip protocol
- When a primal calls `ipc.register(name, capabilities, socket)`, songBird should announce those capabilities to mesh peers
- Method: `mesh.announce_capabilities` → broadcast to peers
- Peers add remote capabilities to their registry with a `remote:true` flag and the source gate
- Method: `capability.locate(name)` → check local, then broadcast to mesh, first-responder-serves

**biomeOS team**: Neural API cross-gate routing
- When `capability.resolve(name)` finds no local provider, query songBird for remote providers
- Route through songBird mesh relay (`0x07`) to the remote gate
- Return response to caller transparently

**All primals**: Self-register capabilities on startup
- Current: manual `ipc.register` scripts on westGate
- Needed: each primal reads its `primal-capabilities.toml` and calls `ipc.register` on its local songBird at boot
- sourDough reference impl exists; should be standard across all primals

## Sequencing

### Phase 1: Mesh Connectivity — DONE
- `SONGBIRD_LOCAL_PEERS` seeding on sporeGate and strandGate
- westGate now in mesh (LAN, reachable)
- strandGate: 1 → 5 peers

### Phase 2: riboCipher Tier 2 (bearDog + songBird + skunkBat)
- bearDog: expose `decode_mito_tag` capability
- songBird: `0xED` accept + decode on federation port
- skunkBat: `0xED` delegate-and-route instead of reject
- Validation: `mesh.connectivity_check` with `MITO_PREFIX` reports `ribocipher_accepted`

### Phase 3: Capability Federation (songBird + biomeOS)
- songBird: capability gossip to mesh peers
- biomeOS: cross-gate Neural API routing via songBird
- All primals: self-register on startup
- Validation: `capability.resolve("content.get")` on sporeGate returns westGate's nestGate

### Phase 4: WG Deprecation for Inner Membrane
- WG remains for: golgi VPS access, outer membrane human ops, enrollment bootstrap
- Inner membrane: all traffic via songBird mesh with `0xED` mito-obfuscated transport
- SSH remains for: human operator access only (not primal-to-primal)

## What WG Becomes

WireGuard is **not removed** — it's reclassified:
- **Outer membrane**: human operator access (RustDesk alternative), VPS connectivity
- **Enrollment bootstrap**: first-time gate setup before songBird mesh is established
- **Fallback**: when LAN is unavailable (remote gates, traveling)

Inner membrane traffic (primal-to-primal RPC, CAS federation, capability routing) moves entirely to Tower Atomic mesh with `0xED` mito-obfuscated transport.

## Ownership

| Component | Owner | Priority |
|-----------|-------|----------|
| `decode_mito_tag` capability | bearDog team | P1 |
| Federation port `0xED` accept | songBird team | P1 |
| `0xED` delegate (not reject) | skunkBat team | P2 |
| Capability gossip | songBird team | P2 |
| Cross-gate Neural API routing | biomeOS team | P2 |
| Primal self-registration | All primal teams | P3 |
| southGate mesh enrollment | overwatch ops | P3 |

---

*Inner Membrane Pure Primals — Phase 1 mesh connectivity DONE (westGate in mesh, strandGate 1→5 peers). Phase 2: riboCipher Tier 2 cross-gate transport (bearDog decode capability, songBird federation 0xED, skunkBat delegate). Phase 3: capability federation (songBird gossip, biomeOS cross-gate routing, primal self-registration). WG becomes outer membrane only.*
