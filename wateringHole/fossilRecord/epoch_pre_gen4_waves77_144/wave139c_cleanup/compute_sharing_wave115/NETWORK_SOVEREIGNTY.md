# Network Sovereignty Architecture

**Status**: Planned | **Owner**: ops (physical) + cellMembrane (primal layer)
**Date**: 2026-06-16 | **Wave**: 115+

---

## Principle

The network mirrors the biological cell model: an outer membrane (periplasm) separates
the untrusted extracellular environment from the sovereign cytoplasm. Each function
gets dedicated hardware. No device does two jobs.

---

## Current State (pre-sporeGate)

```
[ISP] Gateway ([LAN_IP])
    │ NAT + WiFi + DHCP + DNS (all on one weak consumer SoC)
    │
    ▼
CRS310-8G+2S+IN ([LAN_IP]) ← doing L3 routing (wrong role)
    │ RouterOS mode, serving [LAN_IP]/22
    │ SSH/Winbox CLOSED (management access limited)
    │
    ├── 10G SFP+ → eastGate ([LAN_IP]), other towers
    ├── 2.5G RJ45 → fieldGate ([LAN_IP]), NUCs
    └── WiFi via [ISP] → phones ([LAN_IP]/24)
```

**Problems**:
- CRS310 doing L3 routing on a hardware-switch ASIC (CPU-bound NAT)
- [ISP] gateway still handling WiFi devices on separate subnet
- Two NAT boundaries ([ISP] + CRS310) creates confusion
- Intermittent: web failures, WiFi drops, SSH timeouts to VPS
- No monitoring, no alerting, no firewall beyond defaults

---

## Target State: sporeGate as LAN Periplasm

```
[ISP] Gateway (bridge/passthrough mode — modem only)
    │
    ▼ RJ45 1G (WAN)
sporeGate — GMKtec NucBox M6 ← SOVEREIGNTY BOUNDARY
    │ Ryzen 7 6800H / 32GB / Pop!_OS or Ubuntu
    │ eth0 = WAN (DHCP from [ISP] or public IP in passthrough)
    │ eth1 = LAN ([LAN_IP]/22, DHCP server, DNS)
    │ nftables NAT + stateful firewall
    │ NUCLEUS: bearDog, skunkBat, songBird, loamSpine
    │ WireGuard tunnel to golgiBody (persistent VPN)
    │
    ▼ eth1 2.5G
CRS310-8G+2S+IN ([LAN_IP], pure L2 bridge)
    ├── 10G SFP+ → eastGate, towers (compute mesh)
    ├── 2.5G RJ45 → fieldGate, NUCs
    └── 2.5G RJ45 → WiFi AP
```

---

## Biological Mapping

| Network Layer | Biological Analog | Function |
|---------------|-------------------|----------|
| [ISP]/ISP | Extracellular space | Untrusted, uncontrolled environment |
| sporeGate | Periplasm (outer membrane) | Sovereignty boundary, filtering, transport |
| CRS310 | Endoplasmic reticulum | Internal transport (no decisions, just routing packets) |
| Towers + NUCs | Organelles | Compute (each runs NUCLEUS) |
| golgiBody VPS | Remote periplasm | Same role as sporeGate but for WAN-facing services |
| WireGuard tunnel | Axon / inter-membrane channel | Persistent encrypted link between periplasms |

---

## Hardware Inventory

| Device | Model | Role | NICs | Location |
|--------|-------|------|------|----------|
| sporeGate | GMKtec NucBox M6 | Router + primal gate | 2x 2.5G RJ45 | Physical, next to CRS310 |
| CRS310 | MikroTik CRS310-8G+2S+IN | L2 switch | 8x 2.5G + 2x 10G SFP+ | Rack/shelf |
| [ISP] Gateway | Varies (BGW320, etc.) | Modem/bridge | 1G fiber + WiFi | ISP-provided |
| eastGate | Custom tower | Primary compute | 10G SFP+ | LAN |
| fieldGate | NUC | Canary/worker | 2.5G RJ45 | LAN |

---

## Subnet Plan

| Subnet | CIDR | Gateway | Purpose |
|--------|------|---------|---------|
| Compute mesh | [LAN_IP]/22 | [LAN_IP] (sporeGate) | All towers, NUCs, switches |
| Management | [LAN_IP] | — | CRS310 WebFig |
| VPS (golgi) | 10.116.0.0/20 | DO internal | DigitalOcean VPC |
| WireGuard | 10.8.0.0/24 | 10.8.0.1 (sporeGate) | Encrypted tunnel mesh |

Future VLANs (Phase 5, once CRS310 is pure L2):

| VLAN | Subnet | Purpose |
|------|--------|---------|
| 1 (native) | [LAN_IP]/24 | Trusted compute |
| 10 | [LAN_IP]/24 | Mobile/WiFi (rate-limited) |
| 20 | [LAN_IP]/24 | Guest/ABG (sandboxed, relay-only) |
| 100 | [LAN_IP]/24 | Management (switch, router, APs) |

---

## Services on sporeGate

### Networking
- nftables (stateful firewall + NAT masquerade)
- systemd-networkd (interface config + DHCP server)
- dnsmasq or unbound (local DNS caching + forwarding)
- WireGuard (persistent VPN to golgiBody)

### Primals (NUCLEUS)
- bearDog: WireGuard key derivation, mutual auth with golgi
- skunkBat: Latency probes (VPS, 8.8.8.8, gateway), packet loss detection
- songBird: Mesh hub (LAN devices discover via mDNS/mesh, relay WAN traffic)
- loamSpine: Audit trail (connection logs, firewall events)

### Monitoring (skunkBat probes)
- `wan.latency`: ping 8.8.8.8 every 5s, alert if >50ms or loss >5%
- `vps.reachable`: ping golgi/pepti every 10s
- `nat.connections`: read nftables counter, alert if >50k
- `dns.resolution`: dig google.com, alert if >100ms
- `wan.bandwidth`: periodic speedtest (hourly)

---

## Phased Deployment

| Phase | What | Dependency | Risk |
|-------|------|-----------|------|
| 1 | Basic routing (NAT + DHCP + DNS) | Physical wiring | Low (rollback = unplug) |
| 2 | [ISP] bridge mode | [ISP] gateway config | Medium (may need [ISP] support) |
| 3 | Firewall hardening | Phase 1 stable for 24h | Low |
| 4 | NUCLEUS deployment | membrane binary built | Low |
| 5 | WireGuard to golgi | Phase 4 + golgi WireGuard config | Low |
| 6 | VLAN segmentation | CRS310 L3 stripped | Medium (all devices affected) |

---

## Why This Solves the Network Hiccups

1. **NAT offloaded**: Ryzen 7 vs CRS310's switch ASIC — unlimited connection tracking
2. **DNS local**: No round-trips to [ISP]'s overloaded resolver
3. **WireGuard VPN**: SSH to VPS through persistent encrypted tunnel (no NAT traversal)
4. **WiFi isolation**: Compute traffic never touches WiFi radio path
5. **Monitoring**: skunkBat detects degradation before humans notice
6. **Single gateway**: Eliminates multi-NAT confusion (one device, one responsibility)

---

## Security Posture

- **Default deny** inbound (nftables input chain drops all except established + LAN)
- **Stateful tracking** for all connections (Linux conntrack, not CRS310's limited table)
- **No exposed services** on WAN except WireGuard (if needed for remote access)
- **Local DNS** prevents DNS-level attacks/tracking from ISP
- **WireGuard** tunnel encrypts all VPS traffic (ISP cannot inspect)
- **Audit trail** via loamSpine (who connected, when, to what)

---

## Relationship to Existing Architecture

- **cellMembrane**: Manages gate.bootstrap for sporeGate, deploys NUCLEUS
- **golgiBody VPS**: Peer periplasm — WireGuard endpoint, Forgejo, relay
- **pepti VPS**: Build authority — unaffected by LAN topology change
- **fieldGate/eastGate**: Unchanged — just get a better gateway
- **RustDesk relay**: Once WireGuard is up, can route through tunnel (lower latency than NAT traversal)
