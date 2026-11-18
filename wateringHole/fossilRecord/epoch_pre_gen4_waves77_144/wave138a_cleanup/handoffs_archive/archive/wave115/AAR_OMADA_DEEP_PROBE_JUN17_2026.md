# AAR — Omada SX3008F Deep Probe

**Date**: 2026-06-17 17:00 EDT
**From**: sporeGate overwatch
**Controller**: Omada SDN Controller v5.15.24.19 on sporeGate
**Switch**: SX3008F v1.20 (firmware 1.20.0 Build 20231011)

---

## Physical Discovery

**All 8 ports are SFP+ 10G.** This is a pure SFP+ switch — no RJ45 ports at all.

### Port Map (Live)

| Port | Link | Speed | TX | RX | What's Connected |
|------|------|-------|----|----|------------------|
| 1 | UP | 10G | 80 GB | 250 GB | **CRS310 trunk** (10G AOC from backbone) |
| 2 | UP | 10G | 7.5 GB | 2.4 GB | Compute node A (SFP+ NIC) |
| 3 | UP | 10G | 12.5 GB | 23 GB | Compute node B (SFP+ NIC) |
| 4 | DOWN | - | - | - | Empty SFP+ slot |
| 5 | DOWN | - | - | - | Empty SFP+ slot |
| 6 | DOWN | - | - | - | Empty SFP+ slot |
| 7 | DOWN | - | - | - | Empty SFP+ slot |
| 8 | UP | 10G | 243 GB | 66 GB | **TL-SG605S-M2** (2.5G expansion switch via SFP+ to RJ45 adapter) |

**Traffic insight**: Port 8 (TL-SG605S expansion) has the most TX (243 GB) — most downstream devices are behind it. Port 1 (CRS310 trunk) has the most RX (250 GB) — that's upstream traffic from backbone.

### Connected Clients (18 total, via DHCP/ARP)

| IP | MAC | Likely Device |
|----|-----|---------------|
| 192.168.4.1 | [MAC_SCRUBBED] | **sporeGate** (via CRS310 trunk) |
| 192.168.4.101 | [MAC_SCRUBBED] | **Eero 6** (WiFi bridge) |
| 192.168.4.111 | [MAC_SCRUBBED] | **hub2 itself** (Omada management) |
| 192.168.4.115 | [MAC_SCRUBBED] | hub2 data MAC |
| 10.0.4.1 | [MAC_SCRUBBED] | hub2 management IP |
| 192.168.4.133 | [MAC_SCRUBBED] | Compute device |
| 192.168.4.147 | [MAC_SCRUBBED] | Compute device |
| 192.168.4.149 | [MAC_SCRUBBED] | Compute device |
| 192.168.4.152 | [MAC_SCRUBBED] | Compute device |
| 192.168.4.223 | [MAC_SCRUBBED] | Compute device |
| 192.168.4.235 | [MAC_SCRUBBED] | Compute device |
| 192.168.4.237 | [MAC_SCRUBBED] | Compute device (also [MAC_SCRUBBED]) |
| 192.168.4.248 | [MAC_SCRUBBED] | Compute device |

---

## Can We Run NUCLEUS on It?

**No.** The SX3008F is an ASIC-based managed switch, not a compute node. It has:
- Embedded firmware (not Linux, no SSH shell)
- No user-space process capability
- No storage, no package manager
- Managed exclusively through the Omada controller API or web UI

It's infrastructure, not compute. In K-Derm terms: it's the **cytoskeleton** — structural transport fabric. NUCLEUS runs on gates (Linux machines) plugged INTO the switch.

What it CAN do for the ecosystem:
- **VLAN tagging** — isolate compute traffic from human WiFi
- **Port profiles** — assign different VLAN profiles per port
- **802.1X** — port-based authentication (future: bearDog integration?)
- **STP** — spanning tree to prevent loops
- **LLDP-MED** — device discovery protocol (gates can detect their zone)
- **Bandwidth control** — per-port ingress/egress rate limits
- **Storm control** — protect against broadcast storms
- **Port isolation** — prevent inter-port communication (useful for untrusted guests)
- **DHCP L2 relay** — relay DHCP to sporeGate from isolated VLANs
- **Loopback detection** — per-port and per-VLAN

---

## VLAN Capabilities

### Current State
- **1 VLAN** (Default, VLAN 1) — everything is flat L2
- **3 port profiles**: All, Default, Disable
- **No isolation** — all ports can talk to all ports
- `supportMultiVlan: true` — the switch SUPPORTS multiple VLANs

### What We Can Do
1. **Create VLAN-tagged networks** via the controller
2. **Assign port profiles** with native/tagged VLAN memberships
3. **Trunk ports** — carry multiple VLANs (e.g., port 1 as trunk to CRS310)
4. **Access ports** — force a single VLAN per port

### VLAN Limitation
Creating VLANs with gateways requires an Omada gateway/router in the controller. Since sporeGate is our router (not an Omada product), we can only create **VLAN-only** (L2-only) networks on the switch. sporeGate handles routing between VLANs via sub-interfaces on eno1.

### Proposed VLAN Segmentation (for cellMembrane team)

| VLAN | Name | Purpose | Ports |
|------|------|---------|-------|
| 1 | default | Management, trunk | Port 1 (trunk to CRS310) |
| 100 | compute | Gate compute traffic (NUCLEUS) | Ports 2, 3, 4, 5, 6 |
| 200 | storage | NestGate/storage traffic | Dedicated port when needed |
| 300 | human-wifi | Eero bridge (via TL-SG605S) | Port 8 (tagged) |

sporeGate would add VLAN sub-interfaces (`eno1.100`, `eno1.200`, `eno1.300`) to route between VLANs. The CRS310 would need matching VLAN config on its sfp+1 port.

---

## Bridge Capabilities

The switch itself IS a bridge — that's what L2 switching means. What we can control:

1. **Inter-port bridging** — currently all ports bridged (flat L2). Can isolate per-VLAN.
2. **STP bridge** — spanning tree prevents loops if we add redundant links
3. **LAG/Link Aggregation** — bond multiple SFP+ ports for higher throughput (needs API exploration via web UI)
4. **Port mirroring** — mirror traffic from one port to another for monitoring/debugging

---

## API Access Summary

**Working endpoints:**
- `sites/{id}/devices` — list/detail devices
- `sites/{id}/switches/{mac}/ports` — full port config and stats
- `sites/{id}/clients` — connected client list
- `sites/{id}/setting/lan/networks` — VLAN/network config
- `sites/{id}/setting/lan/profiles` — port profile definitions
- `maintenance/controllerStatus` — controller health
- `users/current` — auth/session info

**Not accessible via API (use web UI):**
- Device rename, port rename
- LLDP neighbor table
- Running config dump
- Mirror/LAG config
- ACL rules (needs different parameter format)
- STP global config
- IGMP snooping config

---

## Topology Correction Confirmed

The earlier assumption that the SX3008F has RJ45 ports was wrong. **All 8 ports are SFP+.** The 2.5G RJ45 devices (Eero, NUCs, towers) connect through the TL-SG605S-M2 expansion switch on port 8, which has SFP+ uplink to the Omada and 2.5G RJ45 downlinks.

```
CRS310 sfp+1 ──[80m AOC 10G]──→ hub2 Port1 (SFP+)
                                  hub2 Port2 (SFP+) → compute-a (10G NIC)
                                  hub2 Port3 (SFP+) → compute-b (10G NIC)
                                  hub2 Port4-7 (SFP+) → EMPTY
                                  hub2 Port8 (SFP+) → TL-SG605S-M2 (2.5G expansion)
                                                        ├─ Eero 6 (WiFi bridge)
                                                        ├─ NUCs (fieldGate, etc.)
                                                        └─ Towers
```

---

## Next Steps for cellMembrane Team

1. **LLDP integration** — gates can query LLDP to detect which hub/port they're on (auto-zone detection for `topology.resolve`)
2. **VLAN-aware firewall rules** — `FirewallRuleset` could generate VLAN sub-interface rules when zone segmentation is active
3. **Omada API client** — a Rust client for the Omada controller API could enable `gate.discover` to query the switch directly
4. **Port profile automation** — deploy VLAN profiles programmatically when a new gate is plugged in

## Next Steps for sporeGate Overwatch

1. **VLAN segmentation** — create compute VLAN via web UI, test with one gate
2. **Port labeling** — name ports in web UI to match our topology model
3. **TL-SG605S investigation** — is this switch also Omada-manageable? Could be adopted into the same controller
4. **Eero isolation** — when Eero goes to bridge mode, put it on a separate VLAN to keep WiFi traffic isolated from compute
