# AAR: southGate Hostname Fix + Mesh Validation — Wave 157j-b

**Gate:** southGate  
**Family:** 89df7a2d (southgate-sovereign)  
**Date:** 2026-08-12  
**To:** sporeGate Topology Team  
**Depends:** cellMembrane `b84bed6` (peer registry), wateringHole `42834e5e1` (TOPOLOGY_MAP LAN IPs)

---

## Actions Taken

### 1. Hostname Fixed

```
pop-os → southGate (hostnamectl set-hostname southGate)
```

OS-level hostname now correct. However, songBird's `node_id` reports as `"songbird"`
(binary name), not the system hostname. songBird does not expose a `--node-id` CLI
flag. swarmVine correctly reports `node_id: "southGate"` via its `--gate-id` flag.

**Topology team item:** songBird needs a `--node-id` or `--gate-id` flag to set mesh
identity independently of binary name.

### 2. Peer Registry Pulled

Pulled wateringHole with sporeGate's fixes:
- `TOPOLOGY_MAP.toml`: LAN IPs added to `mesh.songbird_covalent` peers
- Confirmed entries: sporeGate=`.3`, eastGate=`.244`, ironGate=`.237`,
  strandGate=`.169`, blueGate=`.210`, southGate=`.149`

**Note:** southGate's entry says `lan_ip = "192.168.4.149"` but our actual DHCP
address is `192.168.4.148`. Minor discrepancy — `.149` is a neighboring device
(ARP shows different MAC). Not blocking.

### 3. songBird Restarted + LAN Peers Connected

After restart, connected to all TOPOLOGY_MAP LAN peers:

| Gate | Address | Status |
|------|---------|--------|
| sporeGate | 192.168.4.3:7700 | connected |
| eastGate | 192.168.4.244:7700 | connected |
| ironGate | 192.168.4.237:7700 | connected |
| strandGate | 192.168.4.169:7700 | connected |
| blueGate | 192.168.4.210:7700 | timeout (may not be running) |

Total mesh peers: **8** (4 LAN + 4 legacy registry), all `reachable: true`.

### 4. Incoming Federation Connections Observed

songBird log shows LAN peers actively connecting TO us:

```
Federation from 192.168.4.3 (sporeGate)
Federation from 192.168.4.244 (eastGate)
Federation from 192.168.4.149
Federation from 192.168.4.212
```

Bidirectional mesh is forming. The "riboCipher signal (0x47)" warnings are protocol
version negotiation — legacy path deprecated at Wave 112, not blocking connectivity.

### 5. swarmVine Gossip — ACTIVE

```
node_id:          southGate
peer_count:       4
total_ingested:   342
nonce_history:    342 (dedup active)
entries_sent:     304/peer (×4 peers = 1,216 total)
entries_received: 0 (peers not sending back — push-only phase)
entries_rejected: 0
tower_entries:    1
```

Epidemic sweep is running at 30s intervals. southGate is successfully propagating
gossip entries to all 4 LAN peers.

---

## Current State Summary

| Metric | Before (157j) | After (157j-b) |
|--------|---------------|-----------------|
| Hostname | pop-os | **southGate** |
| songBird node_id | pop-os | songbird (needs --node-id) |
| swarmVine node_id | southGate | **southGate** ✓ |
| Mesh peers | 9 (stale) | **8** (4 LAN live) |
| Gossip peers | 4 | **4** |
| Gossip entries sent | 4 | **1,216** |
| Gossip entries ingested | 39 | **342** |
| Incoming federation | none | **4 peers connecting** |
| TOPOLOGY_MAP | absent | **pulled (LAN IPs)** |

---

## Remaining (for topology team)

1. **songBird --node-id flag** — binary uses its own name. Needs code change.
2. **southGate LAN IP in TOPOLOGY_MAP** — listed as `.149`, actual is `.148`.
3. **blueGate** — `.210:7700` timed out. May need depot pull + restart.
4. **entries_received: 0** — peers accept our gossip but don't push back.
   Might be normal (push-only phase) or might need gossip.subscribe registration.
5. **riboCipher legacy warnings** — federation connections use old path.
   Not blocking but should be resolved when all gates update.

---

*Signed: southGate validation gate | family 89df7a2d | Wave 157j-b*
