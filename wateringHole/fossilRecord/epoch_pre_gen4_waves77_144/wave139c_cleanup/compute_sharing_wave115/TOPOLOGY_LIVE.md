# Live Topology — sporeGate Sovereign LAN

**Last verified**: 2026-06-16 20:54 EDT
**Status**: All subnets routing, IPv4 NAT active, IPv6 forwarding disabled

---

## Physical Chain

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERNET (WAN)                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Fiber
                                ▼
┌───────────────────────────────────────┐
│  [ISP] Gateway (BGW320)                 │
│  [LAN_IP]  MAC [MAC_SCRUBBED] │
│  Mode: NAT router (target: passthrough│
│  WiFi: [ISP] native (fallback only)     │
└───────────────────┬───────────────────┘
                    │ RJ45 1G (LAN port)
                    ▼
┌───────────────────────────────────────┐
│  sporeGate (GMKtec NucBox M6)         │
│  WAN: enp1s0 = [LAN_IP] (DHCP)  │
│  LAN: eno1   = [LAN_IP]/22        │
│  NAT + Firewall + DHCP + DNS          │
│  OS: Pop!_OS 22.04                    │
└───────────────────┬───────────────────┘
                    │ RJ45 2.5G
                    ▼
┌───────────────────────────────────────┐
│  MikroTik CRS310-8G+2S+IN            │
│  Pure L2 Bridge (no routing)          │
│  Management: [LAN_IP]             │
│  8x 2.5G RJ45 + 2x 10G SFP+         │
└──┬─────────┬─────────┬───────────────┘
   │         │         │
   │ 10G     │ 2.5G    │ 2.5G
   │ SFP+    │ RJ45    │ RJ45
   ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌─────────────────────┐
│eastGate│ │  NUCs  │ │ Omada Router         │
│(tower) │ │(future)│ │ [LAN_IP]        │
│.4.30   │ │        │ │ Internal: 10.0.4.1   │
│ ⚠ down │ │        │ │ NATs clients → .4.115│
└────────┘ └────────┘ └──────────┬──────────┘
                                  │ (wired or wireless backhaul)
                                  ▼
                       ┌─────────────────────┐
                       │  Eero Mesh (bridge)  │
                       │  Other-house WiFi    │
                       │  Clients: 10.0.x.x  │
                       │  (via Omada DHCP)    │
                       └─────────────────────┘
```

---

## Subnet Map

| Subnet | CIDR | Gateway | DHCP Server | Purpose |
|--------|------|---------|-------------|---------|
| Sovereign LAN | [LAN_IP]/22 | [LAN_IP] (sporeGate) | sporeGate | All wired devices, towers, NUCs |
| [ISP] Legacy | [LAN_IP]/24 | [LAN_IP] ([ISP]) | [ISP] | Eero clients pending migration |
| Omada Internal | 10.0.4.0/22 | 10.0.4.1 (Omada) | Omada | WiFi clients behind Omada NAT |
| Management | — | — | — | CRS310: .4.2, Omada: .4.115 |

---

## Active Devices (verified 2026-06-16)

| IP | MAC | Identity | Connection |
|----|-----|----------|------------|
| [LAN_IP] | sporeGate eno1 | **Router/Gateway** | — |
| [LAN_IP] | (CRS310) | **L2 Switch** | Direct to sporeGate |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown (TP-Link?) | CRS310 2.5G |
| [LAN_IP] | [MAC_SCRUBBED] | **Omada Router** | CRS310 → 10G |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown | CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown | CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown | CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown | CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown | CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown | CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown | CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Unknown | CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Eero/[ISP] client | Bridge via CRS310 |
| [LAN_IP] | [MAC_SCRUBBED] | Eero/[ISP] client | Bridge via CRS310 |

---

## How to Add a NUC

Any NUC plugged into the CRS310 (or any port downstream of sporeGate) will:

1. Get a DHCP lease from sporeGate: `[LAN_IP]–249`
2. Get DNS: `[LAN_IP]`
3. Get internet via sporeGate NAT
4. Be reachable from all other LAN devices

```bash
# On the new NUC, after plugging in:
ip addr show           # Verify 192.168.4.x address
ping [LAN_IP]       # Verify gateway
ping 8.8.8.8           # Verify internet
ssh sporegate@[LAN_IP]  # SSH to sporeGate

# To give it a static lease (optional):
# On sporeGate, add to /etc/systemd/network/20-lan.network [DHCPServer]:
#   [DHCPServerStaticLease]
#   MACAddress=xx:xx:xx:xx:xx:xx
#   Address=192.168.4.XX
```

---

## How to Add a Router / AP

To add another router (e.g., second Omada, or a travel router):

**Option A: Bridge mode (transparent, inherits sporeGate DHCP)**
- Plug into CRS310
- Disable DHCP on the new router
- Set to bridge/AP-only mode
- Clients get 192.168.4.x directly from sporeGate

**Option B: NAT mode (own subnet, isolated WiFi)**
- Plug WAN port into CRS310
- Router gets 192.168.4.x from sporeGate DHCP
- Router runs its own DHCP (e.g., 10.0.x.x, 172.16.x.x)
- Router NATs client traffic → appears as single IP to sporeGate
- This is how the Omada currently works

**Option C: VLAN (future, after CRS310 VLAN config)**
- Assign a VLAN to specific CRS310 ports
- sporeGate manages inter-VLAN routing
- Requires CRS310 VLAN configuration via REST API

---

## How to Extend to Another Property

The current Eero mesh extends to another house. To add more locations:

1. **Wired backhaul** (best): Run ethernet between properties → plug into CRS310
2. **Wireless bridge** (current): Eero mesh or point-to-point bridge → Omada handles NAT
3. **WireGuard tunnel** (remote): NUC at remote site → VPN to sporeGate → appears on LAN

---

## Key Routing Rules

| Traffic | Path | Mechanism |
|---------|------|-----------|
| 192.168.4.x → internet | eno1 → enp1s0 → [ISP] | IPv4 masquerade |
| 192.168.1.x → internet | eno1 → enp1s0 → [ISP] | Proxy ARP + masquerade |
| 10.0.x.x → internet | Omada NATs → [LAN_IP] → sporeGate | Double NAT |
| IPv6 (any) | **BLOCKED** | No IPv6 forwarding (causes iPhone stalls) |
| LAN ↔ LAN | Direct via CRS310 bridge | L2 switching |

---

## Known Issues

- [ ] **eastGate down** — [LAN_IP] unreachable (physical check needed)
- [ ] **[ISP] still in NAT mode** — double NAT until passthrough enabled
- [ ] **IPv6 disabled** — will re-enable when proper prefix delegation is set up
- [ ] **Omada management** — need to access controller to map devices/SSIDs
- [ ] **Device identification** — many MACs unidentified (need nmap scan or DHCP hostname logging)

---

## Future Evolution

| Phase | Action | Benefit |
|-------|--------|---------|
| Omada access | Log into controller, map SSIDs/VLANs | Full visibility |
| [ISP] passthrough | Eliminate double-NAT | Public IP on sporeGate |
| DHCP hostnames | Enable `--dhcp-fqdn` in dnsmasq | Auto-identify devices |
| VLAN segmentation | CRS310 VLANs + Omada VLANs | Traffic isolation |
| WireGuard to golgiBody | Encrypted tunnel to VPS | Sovereign mesh |
| Add NUCs | Plug and play (DHCP) | More compute |
| Proxmox on sporeGate | VM/container orchestration | Cloneable gate |
