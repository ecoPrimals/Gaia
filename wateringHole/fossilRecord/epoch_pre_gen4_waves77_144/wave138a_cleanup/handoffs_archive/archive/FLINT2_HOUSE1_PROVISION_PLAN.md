<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Flint 2 #2 — House 1 WiFi Provisioning Plan

**Date**: June 24, 2026
**Wave**: 126
**Hardware**: GL.iNet Flint 2 (GL-MT6000)
**Site**: House 1 (4422 Southgate Ave)
**Goal**: Own all radio. Separate network layer from compute layer. [ISP] = ethernet WAN.

---

## Architectural Principle: sporeGate is a Deployment, Not the Network

sporeGate is a compute node deployed ON the topology — it runs NUCLEUS,
Sovereign CI, WireGuard hub, and services. But it should NOT be the sole
network path. A small home network might not have a sporeGate at all, or
the NUC might sit internal (behind the router) instead of being the router.

**Current (fragile)**: [ISP] passthrough → sporeGate → everything. Death = total outage.

**Target (resilient)**: [ISP] → Flint 2 (network edge) → CRS310 → all devices
including sporeGate. sporeGate death = services down, but network stays up.

The Flint 2 running OpenWrt can handle: NAT, DHCP, DNS, firewall, WiFi.
The MikroTik CRS310 (once creds recovered) can handle: L2/L3 routing, VLAN,
DHCP, firewall. Either can be the edge router.

### Evolution Path

| Phase | Edge Router | sporeGate Role | [ISP] Passthrough Target |
|-------|-------------|----------------|----------------------|
| **Now** | sporeGate | Router + Compute | sporeGate MAC |
| **Phase 1** | Flint 2 #2 (bridge) + sporeGate | Router + Compute | sporeGate MAC |
| **Phase 2** | Flint 2 #2 (router) | Compute only | Flint 2 #2 MAC |
| **Phase 3** | MikroTik CRS310 | Compute only | CRS310 MAC |

Phase 1 is what we do now (add Flint as WiFi, sporeGate still routes).
Phase 2 promotes Flint to edge router — sporeGate moves behind it as a gate.
Phase 3 is when MikroTik creds are recovered — full L3 backbone.

---

## Physical Wiring — Redundant Topology

### Port Inventory

| Device | Port 1 | Port 2 | Notes |
|--------|--------|--------|-------|
| **sporeGate** | enp1s0 (2.5G) → [ISP] WAN | eno1 (2.5G) → CRS310 | Both 2.5G RJ45 |
| **Flint 2 #2** | WAN (2.5G) → CRS310 | LAN1 (2.5G) → [ISP] eth | Bridge + emergency |
| **[ISP] BGW320** | eth1 → sporeGate | eth2 → Flint 2 #2 LAN1 | Emergency kickstart |
| **CRS310** | ether → sporeGate | ether → Flint 2 #2 WAN | L2 backbone hub |

### Phase 1: Immediate (sporeGate still routes, Flint = WiFi AP)

```
[ISP] BGW320 (WiFi OFF, passthrough → sporeGate MAC)
    ├── eth1 → sporeGate enp1s0 (public IP: [NUCLEUS_WAN])
    │           └── eno1 → CRS310 ether8 (2.5G)
    │                   ├── etherX → Flint 2 #2 WAN (bridge mode, WiFi AP)
    │                   ├── sfp+1 → 10G AOC → Omada (House 2)
    │                   │       └── SG605S → Flint 2 #1 (bridge, WiFi AP)
    │                   ├── sfp+2 → eastGate (10G)
    │                   └── etherX → northGate (2.5G)
    │
    └── eth2 → Flint 2 #2 LAN1 (DORMANT emergency cable)
```

### Phase 2: Target (Flint = edge router, sporeGate = compute node)

```
[ISP] BGW320 (WiFi OFF, passthrough → Flint 2 #2 MAC)
    └── eth1 → Flint 2 #2 WAN (public IP, router mode)
                  ├── WiFi: ApertureScience (House 1)
                  └── LAN → CRS310 (2.5G backbone uplink)
                              ├── sporeGate (gate: CI, NUCLEUS, WG hub)
                              ├── sfp+1 → 10G AOC → Omada (House 2)
                              │       └── SG605S → Flint 2 #1 (bridge, WiFi)
                              ├── sfp+2 → eastGate (10G)
                              └── etherX → northGate (2.5G)
```

**Phase 2 benefit**: sporeGate can die and the network stays up. WiFi, DHCP,
DNS, NAT all run on the Flint. sporeGate is a power entry point and compute
host — WireGuard, NUCLEUS, Sovereign CI — accessed via port forwarding from
the Flint edge.

**Port forwards needed (Phase 2)**: Flint → sporeGate:
- UDP 51821 (WireGuard)
- TCP 22 (SSH, rate limited)
- TCP 2222 (Forgejo SSH, if exposed)
- TCP 80/443 (Caddy, if web services exposed)

### Failure Modes & Recovery

#### Mode A: Flint 2 #2 Dies → WiFi Down, Wired Survives

| Step | Action |
|------|--------|
| 1 | Wired devices (northGate, eastGate, ironGate) unaffected |
| 2 | **Operator**: Re-enable [ISP] WiFi radios via `http://192.168.1.254` |
| 3 | WiFi clients connect to [ISP] SSID, get 192.168.1.x (temporary) |
| 4 | Internet works via [ISP] (bypasses sporeGate for WiFi clients) |
| 5 | Replace/reboot Flint 2 #2, disable [ISP] WiFi again |

**Recovery time**: ~2 min (operator-paced, [ISP] WiFi toggle)

#### Mode B: sporeGate Dies → Everything Down

| Step | Action |
|------|--------|
| 1 | All DHCP/DNS/NAT stops. Existing leases work briefly. |
| 2 | **Operator**: Re-enable [ISP] WiFi via physical access to BGW320 |
| 3 | [ISP] serves DHCP on 192.168.1.x to WiFi clients (internet works) |
| 4 | **Operator**: Switch Flint 2 #2 from bridge → router mode |
| 5 | Flint 2 #2 uses LAN1 port (cabled to [ISP] eth2) as WAN |
| 6 | Flint 2 serves DHCP to WiFi clients, NATs via [ISP] |
| 7 | Wired devices: connect laptop to CRS310, reconfigure gateway |
| 8 | Debug/fix sporeGate, restore sovereign config |

**Recovery time**: ~5 min for WiFi (Flint 2 mode switch), ~15 min for wired

#### Mode C: [ISP] Internet Dies → WAN Down

| Step | Action |
|------|--------|
| 1 | All gates lose internet. LAN/mesh still works. |
| 2 | **Operator**: USB hotspot from phone → sporeGate |
| 3 | Set hotspot route metric lower than [ISP] |
| 4 | Or: Flint 2 #2 has tethering capability (OpenWrt) |

**Recovery time**: ~2 min (plug phone USB)

#### Mode D: Full Dead (sporeGate + Flint 2 + [ISP] all down)

| Step | Action |
|------|--------|
| 1 | Power cycle [ISP] BGW320 (wait 3 min for sync) |
| 2 | Re-enable [ISP] WiFi if needed |
| 3 | Power cycle sporeGate (services auto-start via systemd) |
| 4 | Power cycle Flint 2 #2 |
| 5 | Verify: `ping 8.8.8.8`, check dnsmasq leases, WG handshake |

**Recovery time**: ~5 min (power cycle cascade)

### Emergency Bypass Cable

The **Flint 2 #2 LAN1 → [ISP] eth2** cable is the key redundancy wire. In
normal operation it's dormant. In emergency (Mode B), the operator switches
Flint 2 to router mode and this cable becomes the WAN uplink, bypassing
the dead sporeGate entirely.

This cable also allows the Flint 2 to be provisioned initially by
connecting it to [ISP] for internet access during setup, then switching to
bridge mode for sovereign operation.

---

## Step-by-Step

### Phase 1: [ISP] Gateway — Kill WiFi Radios

1. Access BGW320 admin: `http://192.168.1.254` (from sporeGate or northGate)
2. Navigate to **Home Network** → **Wi-Fi**
3. Disable **both** radios:
   - 2.4GHz: OFF
   - 5GHz: OFF
4. Save/Apply
5. Verify: no `[ISP]*` SSIDs visible on any device

**Impact**: House 1 WiFi users temporarily lose connectivity (daughters' devices).
Flint 2 #2 must be ready to take over immediately.

### Phase 2: Flint 2 #2 — Initial Setup

1. Unbox, connect power
2. Connect laptop/phone to Flint 2 default WiFi (GL-MT6000 setup AP)
3. Access admin panel at `192.168.8.1`
4. Set admin password
5. Configure as **Bridge Mode** (same as House 2 Flint 2 #1):
   - Mode: Bridge (not Router)
   - WAN port becomes LAN — receives DHCP from upstream (sporeGate)

### Phase 3: WiFi Configuration

Configure via admin panel or SSH to MediaTek `.dat` files:

| Setting | 2.4GHz | 5GHz |
|---------|--------|------|
| SSID | ApertureScience | ApertureScience |
| Password | exoticpanda714 | exoticpanda714 |
| Encryption | WPA2/WPA3 | WPA2/WPA3 |
| Channel | Auto (1/6/11) | Auto (36-48 or DFS) |
| Band width | 20/40MHz | 80MHz |
| Region | US | US |

**Must match House 2 Flint 2 #1 exactly** for seamless roaming between houses.

### Phase 4: Physical Connection

1. Run ethernet from CRS310 free port to Flint 2 #2 WAN port
2. Flint 2 #2 gets DHCP from sporeGate (bridge mode)
3. Verify: Flint 2 appears in dnsmasq leases

### Phase 5: sporeGate — DHCP + DNS

Add to `/etc/dnsmasq.conf`:

```
# Flint 2 #2 — House 1 WiFi AP
dhcp-host=<MAC>,192.168.4.251,flint2-hub1
address=/flint2-hub1.primals.local/192.168.4.251
```

(MAC obtained from Flint 2 #2 label or admin panel)

### Phase 6: Verify

1. Connect phone to ApertureScience at House 1
2. Confirm IP is `192.168.4.x` (from sporeGate, NOT 192.168.1.x)
3. Confirm `printer.primals.local` resolves
4. Confirm DNS blocklist active (test: `http://ads.example.com` → blocked)
5. Confirm internet works
6. Walk to House 2 — confirm seamless WiFi (same SSID, same password)

### Phase 7: Printer Migration

After [ISP] WiFi disabled, power-cycle the printer:
- It reconnects to ApertureScience (now served by Flint 2 #1 or #2)
- DHCP from sporeGate → gets `192.168.4.200` (reservation ready)
- Update dnsmasq: `printer.primals.local` → `192.168.4.200`

---

## Topology Updates Required

After successful provisioning:

1. **TOPOLOGY_MAP.toml**: Add `flint2_wifi_h1` zone, update backbone ports
2. **device_registry.toml** (metalForge): Add Flint 2 #2 device
3. **ECOSYSTEM_BLURB.md**: Update Flint 2 count, [ISP] WiFi disabled
4. **segments.backbone_legacy**: Mark as deprecated/empty (no more WiFi clients)
5. **freshness.toml**: Update notes

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Daughters lose WiFi during transition | Do Phase 1 + 4 together (< 5 min gap) |
| Flint 2 bridge mode doesn't work | Test bridge mode BEFORE disabling [ISP] WiFi |
| Wrong subnet IP | Verify dnsmasq lease before declaring success |
| CRS310 port unavailable | Check CRS310 port LEDs (no creds needed for L2) |
| Printer stays on 192.168.1.x | Power-cycle printer after [ISP] WiFi killed |

---

## Post-Provisioning State

### Phase 1 (Immediate)

```
[ISP] BGW320 (ethernet only, passthrough → sporeGate)
    ├── eth1 → sporeGate ──→ CRS310 ──→ Flint 2 #2 (WiFi) + all gates
    └── eth2 → Flint 2 #2 LAN1 (dormant bypass)
```

### Phase 2 (Target)

```
[ISP] BGW320 (ethernet only, passthrough → Flint 2 #2)
    └── eth1 → Flint 2 #2 (edge router + WiFi) ──→ CRS310 ──→ all gates
                                                        └── sporeGate (compute node)
```

**All radio owned. sporeGate is a deployment, not the network.**
**Network survives sporeGate death. Phone hotspot relights after total failure.**
