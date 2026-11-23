# LAN-First Tower Transport Spec

**Date**: Aug 4, 2026 | **Wave**: 156d | **From**: sporeGate (eastGate overwatch)
**Status**: **PROVEN** — 4 LAN peers at priority 0, 1ms RTT vs 77ms WG overlay

---

## Architecture Change: WireGuard → Outer Membrane Only

### Before (WG-centric)
```
sporeGate ←─ WG tunnel ──→ golgi (VPS hub) ←─ WG tunnel ──→ eastGate
                               ~36ms              ~77ms total
```
All inter-gate traffic routed through golgi VPS even for gates on the same LAN.

### After (LAN-first, WG as fallback)
```
sporeGate ←─── LAN TCP ───→ eastGate    (~1ms, priority 0)
sporeGate ←─── LAN TCP ───→ ironGate    (~1ms, priority 0)
sporeGate ←─── LAN TCP ───→ blueGate    (~1ms, priority 0)
sporeGate ←─── LAN TCP ───→ strandGate  (~1ms, priority 0)
sporeGate ←─── WG overlay ─→ golgi      (~36ms, priority 1)  ← outer membrane only
sporeGate ←─── WG overlay ─→ flockGate  (~36ms, priority 1)  ← WAN gate
```

### Measured Performance

| Path | RTT | vs LAN |
|------|-----|--------|
| LAN direct (192.168.4.x:7700) | **~1ms** | 1× |
| WG overlay → golgi | ~36ms | 36× slower |
| WG overlay → eastGate via golgi | ~77ms | **77× slower** |
| WG overlay → ironGate via golgi | ~75ms | 75× slower |

---

## songBird Endpoint Priority System

songBird already has multi-tier path selection built in:

| Priority | EndpointType | When Used |
|----------|--------------|-----------|
| **0** | `Local` | Same-LAN TCP (192.168.4.x:7700) |
| 1 | `Overlay` | WireGuard mesh (10.13.37.x:7700) |
| 2 | `Direct` | WAN/public TCP |
| 3 | `FamilyRelay` | Relay through another gate |
| 4 | `TorOnion` | .onion fallback |

`get_best_path()` always picks lowest priority. LAN wins when available.

---

## WireGuard New Role: Outer Membrane

WireGuard remains essential for:

1. **golgi relay** — VPS has no LAN, WG is its only mesh path
2. **WAN gates** — flockGate (house 2), any remote gate
3. **Encrypted fallback** — if LAN path fails, WG overlay is automatic fallback
4. **External access** — SSH into gates from outside the LAN
5. **nestgate.io proxy** — golgi → sporeGate petalTongue over WG

WireGuard is NOT deprecated — it moves from "only transport" to "outer membrane
transport" while LAN primals handle the inner membrane.

---

## Implementation: What Changed

### sporeGate (DONE)

1. **`/etc/systemd/system/songbird-gateway.service.d/lan-first.conf`**
   ```ini
   [Service]
   Environment=SONGBIRD_LOCAL_PEERS=eastGate@192.168.4.244:7700,ironGate@192.168.4.237:7700,blueGate@192.168.4.210:7700,strandGate@192.168.4.169:7700
   ```

2. **`/usr/local/bin/songbird-mesh-init.sh`** — updated to pass `lan_peers`
   in `mesh.init` RPC with all LAN-reachable gates as `Local` endpoints,
   and WAN gates (golgi, flockGate) as `overlay_peers`.

3. **Runtime verified**: `mesh.peers` shows 4 local (priority 0) + 2 overlay
   (priority 1) after re-init.

### ironGate (DONE — runtime init)

Mesh initialized via SSH with sporeGate + eastGate as LAN peers,
golgi as overlay. Needs persistent config for reboot survival.

### Remaining Gates (TODO)

| Gate | LAN IP | songBird:7700 | Status |
|------|--------|---------------|--------|
| eastGate | 192.168.4.244 | OPEN | Needs LAN peer re-init |
| ironGate | 192.168.4.237 | OPEN (after UFW reload) | Runtime init done, needs persist |
| blueGate | 192.168.4.210 | OPEN | Needs LAN peer re-init |
| strandGate | 192.168.4.169 | SSH reachable, 7700 not probed | Needs songBird federation port check |
| northGate | 192.168.4.147 | SSH closed, 7700 closed | Windows — needs configuration |

---

## Firewall Fix: ironGate

UFW rules were present in config but NOT applied to iptables. Fix:
```
sudo ufw reload
```
This loaded the 7700/tcp ALLOW from 192.168.4.0/22 into live iptables.
All LAN gates should verify their UFW rules are actually loaded.

---

## Evolution Path

### Phase 1: LAN-First Init (DONE on sporeGate)
- Wire `SONGBIRD_LOCAL_PEERS` in systemd service
- Update `mesh.init` to classify LAN gates as `Local`
- Verify 1ms RTT for LAN peers

### Phase 2: Propagate to All LAN Gates
- Each LAN gate needs its songBird re-initialized with LAN peers
- UFW/firewall audit — ensure 7700/tcp open from LAN subnet
- Persist via systemd env or biomeOS graph

### Phase 3: Manifest-Driven LAN Seeding
- cellMembrane reads `[gates.*].lan_ip` + `zone` from manifest
- Auto-generates `SONGBIRD_LOCAL_PEERS` for same-zone gates
- No manual env var wiring needed

### Phase 4: LAN Auto-Discovery
- songBird `mesh.auto_discover` (UDP multicast port 2300)
- Zero-config — new gates on LAN automatically register as Local
- Complements manifest-driven seeding for dynamic/temporary gates

### Phase 5: WG Deprecation for LAN
- Remove WG overlay peer entries for same-LAN gates
- WG remains ONLY for golgi + WAN gates
- `primal.eco` DNS resolves to LAN IPs, not WG IPs
- Inner membrane traffic never leaves the LAN

---

## Relationship to Three-Domain Topology

| Domain | Transport | Priority |
|--------|-----------|----------|
| **primals.eco** (outer) | Cloudflare → golgi Caddy → WG | N/A (public HTTP) |
| **nestgate.io** (peti) | golgi Caddy → WG → sporeGate petalTongue | WG (outer membrane relay) |
| **primal.eco** (inner) | **LAN TCP :7700** (songBird Tower Atomic) | **Local (priority 0)** |

The inner membrane runs on primals, not on WireGuard. WireGuard becomes
infrastructure for the outer membrane boundary, like a firewall between
the peptidoglycan and the extracellular space.
