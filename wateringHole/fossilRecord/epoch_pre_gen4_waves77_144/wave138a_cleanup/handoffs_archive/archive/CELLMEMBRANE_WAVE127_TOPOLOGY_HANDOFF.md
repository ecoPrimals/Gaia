# cellMembrane Team Blurb — Wave 127 Topology Update

**Date**: Jun 27, 2026 07:30 EDT | **Wave**: 127 | **From**: sporeGate topology session
**Status**: Physical topology stabilized. Infrastructure layer independent of compute. Ready for k-derm transport evolution.

---

## What Changed (Wave 127)

The physical network underwent a full topology cutover. **sporeGate is no longer the edge router.** The plasma membrane role has moved to dedicated infrastructure hardware.

### New Architecture

```
INTERNET
    │
    ▼
[ISP] BGW320 (passthrough only, no NAT)
    │
    ▼
┌─────────────────────────────────────────────┐
│  Flint 2 H1 — EDGE ROUTER (plasma membrane) │
│  WAN: [NUCLEUS_WAN] (public, passthrough)  │
│  LAN: 192.168.4.1/22                         │
│  Services: NAT, DHCP, DNS, firewall, WiFi    │
│  DNS blocklist: 91k rules (security-only)    │
│  Port forwards → sporeGate .3               │
└──────────────────────┬──────────────────────┘
                       │ lan1 (2.5G)
                       ▼
┌─────────────────────────────────────────────┐
│  CRS310 — L2 BACKBONE (10G/2.5G switching)   │
├──────────────┬──────────────┬───────────────┤
│ sfp+1: Omada │ sfp+2: east  │ ether: gates  │
│ (10G, H2)    │ Gate (10G)   │ (2.5G each)   │
└──────────────┴──────────────┴───────────────┘
        │                              │
        ▼                              ▼
   House 2 (Omada→Flint H2)    sporeGate (.3)
   WiFi: ApertureScience        COMPUTE NODE
                                 WG hub, Caddy,
                                 Forgejo, services
```

### Key Changes for cellMembrane

| Before (Wave 126) | After (Wave 127) |
|-------------------|-------------------|
| sporeGate = gateway at .1 | sporeGate = compute at .3 |
| Flint = bridge (WiFi only) | Flint = edge router (full stack) |
| Unplug sporeGate = network dead | Unplug sporeGate = network survives |
| dnsmasq on sporeGate | dnsmasq on Flint (.1) |
| NAT/firewall on sporeGate | NAT/firewall on Flint |
| [ISP] passthrough → sporeGate | [ISP] passthrough → Flint WAN MAC |

---

## What This Means for Transport Layers

The physical substrate is now **stable and independent of compute**. This enables full k-derm transport iteration without risking network outages.

### LAN Transport (inner membrane)

- Gateway is now `192.168.4.1` (Flint), not sporeGate
- All gates still get `192.168.4.x/22` via DHCP from Flint
- sporeGate at `.3` is just another LAN peer — same L2 domain
- CRS310 backbone unchanged (2.5G/10G switching)
- cellMembrane LAN discovery/relay should target `.3` for sporeGate services
- DNS: `.primals.local` domains resolved by Flint dnsmasq

### WAN Transport (outer membrane)

- Public IP: `[NUCLEUS_WAN]` on Flint WAN
- WireGuard port: `51821/udp` forwarded from Flint → sporeGate:51821
- SSH: `22/tcp` forwarded → sporeGate:22
- HTTPS: `443/tcp` forwarded → sporeGate:443 (Caddy)
- All inbound WAN traffic still terminates at sporeGate — transparent to remote peers
- WireGuard mesh intact (golgi handshake active, 10.13.37.0/24 overlay)
- Remote gates (flockGate, etc.) see no change — same public IP, same ports

### VPS Transport (golgi relay)

- No change. WireGuard tunnel from sporeGate (.2) → golgi (.1) still active
- golgi endpoint: `[RELAY_PUBLIC]:51820`
- Auto-cascade relay continues (15min interval)
- BTSP/relay.forward paths unchanged

---

## What cellMembrane Should Evolve

Now that the infrastructure layer is resilient, the k-derm transport layers can iterate freely:

1. **LAN discovery**: Update any hardcoded `.1` references to use DNS (`sporegate.primals.local`) or the WireGuard overlay IP (`10.13.37.2`). The gateway is no longer sporeGate.

2. **Failover awareness**: cellMembrane can now model the two-layer architecture — if a compute node disappears, transport should gracefully degrade (retry, reroute via golgi relay) rather than assuming network death.

3. **Port-forward transparency**: From cellMembrane's perspective, inbound connections still arrive at sporeGate's interfaces. The Flint DNAT is invisible to application-layer code.

4. **DNS-based service discovery**: Flint's dnsmasq serves `.primals.local` — cellMembrane can register service names here for LAN peer discovery without hardcoding IPs.

5. **Hot-plug compute model**: sporeGate can now travel (personal NUC, data science hotspot, hazardous network anchor). cellMembrane transport should handle reconnection gracefully when a gate re-appears on the mesh after absence.

---

## Connectivity to sporeGate (for development)

```bash
# SSH (from LAN)
ssh sporegate@192.168.4.3

# SSH (from WAN / remote gate)
ssh sporegate@[NUCLEUS_WAN]

# SSH (via WireGuard overlay)
ssh sporegate@10.13.37.2

# Forgejo
https://git.primals.eco  (→ 443 → sporeGate Caddy)
ssh://git.primals.eco:2222  (→ 2222 → Forgejo)
```

---

## Verified State

| Check | Status |
|-------|--------|
| Internet (8.8.8.8) | 13ms, 0% loss |
| WireGuard mesh | Handshake active |
| DNS blocking (ads) | juicyads.com → NXDOMAIN |
| DNS allow (adult) | redgifs.com → resolves |
| Pull test | sporeGate unplugged + rebooted, network survived |
| Flint uptime | 1d 21h (never went down during cutover) |

---

*Infrastructure layer is sealed. Compute layer is free. Build the membrane.*
