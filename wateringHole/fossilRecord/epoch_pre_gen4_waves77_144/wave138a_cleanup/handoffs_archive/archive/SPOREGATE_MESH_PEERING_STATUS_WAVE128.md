# sporeGate Mesh Peering Status — Wave 128

**Date**: Jul 3, 2026 08:30 EDT
**From**: sporeGate infra + cellMembrane session
**To**: eastGate overwatch, ironGate, cellMembrane team (all gates)
**Priority**: P1 — mesh transport needs cross-gate coordination

---

## Context

The physical infrastructure is hardened and stable (Wave 127-128). We are now evolving the mesh transport layer so that compute can be hosted across gates — starting with ironGate (GPU, RTX 5070) for projectNUCLEUS / student compute hosting.

**Goal**: cellMembrane's songBird mesh transport should enable any gate to offer compute to any other gate over LAN (direct) or WAN (relayed via golgi). sporeGate is the public face, ironGate has the GPU, eastGate is overwatch — all need to peer.

---

## Infrastructure State (stable, do not rework)

```
[ISP] BGW320 (passthrough) → Flint H1 (.1, edge router, public [NUCLEUS_WAN])
    → CRS310 (L2 backbone, 2.5G/10G)
        → sporeGate (.3, compute, WG hub, Caddy, Forgejo, port-forwarded)
        → ironGate (.169/.237, GPU compute, RTX 5070)
        → eastGate (.30, overwatch, primalSpring)
        → northGate (.103, gaming/spare)
        → Omada (10G trunk) → House 2 → Flint H2 (.250, WiFi AP)
```

| Gate | LAN IP | WG IP | Ping from sporeGate | NUCLEUS | songBird |
|------|--------|-------|---------------------|---------|----------|
| sporeGate | 192.168.4.3 | 10.13.37.2 | — | 13/13 svc | v0.2.1, relay on :3479 |
| ironGate | 192.168.4.169/.237 | 10.13.37.7 | 0.2ms | 12/12 svc | v0.2.1, relay on :7700(?) |
| eastGate | 192.168.4.30 | 10.13.37.5 | needs verify | 13/13 svc | needs verify |
| golgi (VPS) | — | 10.13.37.1 | 30ms (WG) | WG hub | needs verify |

---

## Mesh Peering — Current Blocker

Both sporeGate and ironGate have songBird v0.2.1 initialized with `mesh.init`. Both report `relay_enabled: true`. But **neither can see the other as a peer**.

### What We Tried (sporeGate side)

| Method | Params | Result |
|--------|--------|--------|
| `mesh.init` | `node_id: sporeGate, peers: [.237, .169]` | `initialized: true`, bootstrap_peers_added: 0 |
| `peer.connect` | `target_address: 192.168.4.237:7700` | Silent timeout, no peer added |
| `relay.serve` | `port: 7700` | Bound to `0.0.0.0:3479` (not 7700!) |
| `mesh.announce` | `addresses: [192.168.4.3:7700]` | `announced: true`, ttl 300s |
| `mesh.auto_discover` | `{}` | Empty response |
| TCP probe to .237:7700 | — | Timeout |
| TCP probe to .169:7700 | — | Connection refused |
| UDP probe to both :7700 | — | No error but no handshake |

### What ironGate Reported

| Item | Result |
|------|--------|
| `mesh.init` | `initialized: true`, node_id "ironGate" |
| Firewall | UDP 7700, TCP 8091, UDP 41582 opened for 192.168.4.0/22 |
| `mesh.status` | relay_enabled: true, 0 reachable peers |
| `mesh.peers` | `[]`, 0 total |

### Root Cause Hypothesis

1. **Port mismatch**: sporeGate's `relay.serve` bound to `:3479` not `:7700`. ironGate may be listening on `:7700`. Neither side is connecting to the other's actual port.

2. **Protocol gap**: `peer.connect` takes `target_address` but returns empty — it may be attempting a UDP relay handshake that requires both sides to have each other's relay address pre-configured, not just one side connecting.

3. **No discovery mechanism on LAN**: `mesh.auto_discover` returned empty. songBird may not implement LAN multicast/broadcast discovery yet. Peers need to be explicitly configured with the correct address:port.

---

## What cellMembrane Team Needs To Do

This is the critical path for mesh compute hosting:

### 1. Verify relay bind port logic
Why does `relay.serve(port: 7700)` bind to `:3479`? Is the port parameter ignored? Check `songbird/src/relay/` for the bind logic. Both sides need to agree on the port.

### 2. Make `peer.connect` work on LAN
Two gates on the same /22 subnet at 0.2ms latency should be the simplest case. If `peer.connect` can't establish a direct LAN peer connection, the WAN/relay path won't work either. Check:
- Does `peer.connect` expect UDP or TCP?
- Does it need the remote node's public key or node_id?
- Is there a handshake timeout that's too aggressive?

### 3. Implement or fix `mesh.auto_discover` for LAN
On a flat /22 subnet, broadcast or multicast discovery should find all songBird instances automatically. This eliminates the need for manual peer configuration.

### 4. Test the happy path
Once two gates can peer on LAN, verify:
```
sporeGate → capability.call → ironGate.toadStool.system.info
```
This proves the mesh transport is live and capability routing works across gates.

### 5. Graduate to WAN
After LAN peering works, test the same flow over WireGuard overlay (10.13.37.x) and then via golgi relay for true WAN peering.

---

## What eastGate Overwatch Should Do

1. **Pull this update** — `git pull` on wateringHole
2. **Verify eastGate songBird** — run `mesh.status`, `relay.status`, `mesh.peers` and report back
3. **Coordinate three-way peering** — once cellMembrane fixes the peer.connect flow, eastGate should join the mesh alongside sporeGate and ironGate
4. **Disseminate to all gates** — update ecosystem blurb with mesh transport status, assign cellMembrane team the relay/discovery fixes as P1

---

## For projectNUCLEUS / Student Compute Hosting

The end-state we're building toward:

```
Student browser → sporeGate (Caddy) → cellMembrane relay
    → ironGate (GPU compute, JupyterHub)
    → results stream back via mesh
```

**What's ready**: Physical network, DNS, NAT, port forwards, firewall, SSH keys (ironGate enrolled).
**What's blocked**: songBird peer.connect — the last mile between "nodes can ping" and "nodes can route capability calls."

Once cellMembrane's mesh transport peers correctly, the entire compute hosting stack opens up. This is the critical path.

---

*Infrastructure is the platform. Mesh transport is the last mile. Fix peer.connect, and compute flows.*
