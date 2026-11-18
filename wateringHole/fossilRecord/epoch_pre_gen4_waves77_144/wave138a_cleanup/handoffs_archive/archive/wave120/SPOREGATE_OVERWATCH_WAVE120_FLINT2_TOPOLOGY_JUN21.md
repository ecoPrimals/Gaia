# sporeGate Overwatch — Wave 120 FRAGO: Flint 2 Bridge + Topology Revalidation

**Date**: Jun 21, 2026 12:00 EDT | **From**: sporeGate overwatch (hardware + VPS topology)
**Wave**: 120 | **Scope**: Flint 2 enrollment, Eero retirement, full topology revalidation

---

## What Shipped

### Flint 2 (GL-MT6000) — Enrolled as Bridge AP

The GL.iNet Flint 2 at Hub 2 has been initialized, configured, and is operational as a transparent bridge AP on the 192.168.4.0/22 subnet.

| Step | Method | Result |
|------|--------|--------|
| Device discovery | ARP scan + ping sweep from sporeGate eno1 | Found at 192.168.8.1 (factory default) |
| Network path | Temp IP alias `192.168.8.100/24` on eno1 | Bridged sporeGate to Flint 2's factory subnet |
| Initialization | GL.iNet 4.x RPC: `ui.init` (discovered via API enumeration) | Password set, SSH (Dropbear) enabled |
| SSH access | `sshpass` → key-based auth via Dropbear `authorized_keys` | sporegate-gate-v1 key enrolled |
| Bridge config | UCI: WAN port into br-lan, DHCP disabled, firewall disabled | All 7 ports + both radios in one bridge |
| WiFi config | MediaTek `.dat` driver files (not UCI — driver overrides) | SSID/key set at driver level |
| Reboot + verify | Full restart, new IP `192.168.4.250/22` | Ping, SSH, internet all confirmed |
| Eero retirement | Physical removal by operator | Complete |

**Key discovery**: GL.iNet 4.x devices with firmware ≥4.3.28 ship with SSH disabled until initial password is set via web UI. The `ui.init` RPC method bypasses this — it accepts `{"lang","username","password","security_rule"}` params with an empty session token. This enables fully headless provisioning.

**Key discovery**: MediaTek MT7986 WiFi driver ignores UCI `wireless` config on `wifi up`/`wifi down`. The actual SSID/key/auth must be set in `/etc/wireless/mediatek/mt7986-ax6000.dbdc.b{0,1}.dat` (`SSID1`, `WPAPSK1`, `AuthMode`, `EncrypType` fields).

### Eero Mesh Retired

Eero mesh APs at Hub 2 have been physically removed. The Flint 2 replaces them with:
- WiFi 6 (802.11ax) on both 2.4 GHz and 5 GHz
- 2401 Mbit/s max on 5 GHz (HE80), 573 Mbit/s on 2.4 GHz (HE20)
- Same SSID (`ApertureScience`) and password as AT&T at House 1 — seamless roaming
- 802.11k/v enabled for assisted roaming between APs
- Zero cloud dependency (Eeros required Amazon cloud; Flint 2 is fully local)

---

## Topology Revalidation — Jun 21, 2026 12:00 EDT

### Layer 1: Physical

```
House 1                              House 2
┌─────────────────────┐              ┌───────────────────────┐
│ [ISP] BGW320 (WAN)    │              │                       │
│   └→ sporeGate      │              │                       │
│       ├─ enp1s0 WAN │   Cat6       │                       │
│       ├─ eno1 LAN ──┼──────────────┤── Omada CRS310 (L2)  │
│       └─ wg0 mesh   │              │    ├─ eastGate        │
│                      │              │    ├─ ironGate        │
│                      │              │    ├─ Flint 2 (AP)    │
│                      │              │    └─ (strandGate)    │
└─────────────────────┘              └───────────────────────┘
```

### Layer 2: LAN — 192.168.4.0/22

| IP | Device | MAC | Role | Status |
|----|--------|-----|------|--------|
| .4.1 | **sporeGate** (eno1) | — | Gateway, NAT, DHCP, DNS | ✅ |
| .4.2 | **Omada CRS310** | [MAC_SCRUBBED] | L2 switch (Hub 2) | ✅ |
| .4.3 | sporeGate (secondary) | — | Omada SDN controller bind | ✅ |
| .4.111 | Unknown | [MAC_SCRUBBED] | TBD | REACHABLE |
| .4.147 | Unknown | [MAC_SCRUBBED] | TBD | REACHABLE |
| .4.169 | Unknown (9c:6b) | [MAC_SCRUBBED] | TBD | REACHABLE |
| .4.218 | Unknown (9c:6b) | [MAC_SCRUBBED] | TBD | STALE |
| .4.237 | **ironGate** | [MAC_SCRUBBED] | Node atomic | ✅ |
| .4.244 | ironGate (2nd NIC?) | [MAC_SCRUBBED] | TBD | REACHABLE |
| .4.250 | **Flint 2** (br-lan) | [MAC_SCRUBBED] | Bridge AP | ✅ |

### Layer 3: WireGuard Mesh — 10.13.37.0/24

| Gate | Overlay IP | Handshake | Latency | Status |
|------|-----------|-----------|---------|--------|
| **golgiBody** | .1 (hub) | 26s ago | 37ms | ✅ 4 peers connected |
| **sporeGate** | .2 | — | — | ✅ (self) |
| **eastGate** | .3 (.5 in manifest) | — | — | ❌ UNREACHABLE |
| **flockGate** | .5 (.6 in manifest) | — | 69ms | ✅ via golgi |
| **ironGate** | .7 | — | — | ❌ UNREACHABLE (peer added, no handshake) |

### Layer 4: WiFi

| AP | SSID | Band | Channel | Max Rate | Auth | Clients |
|----|------|------|---------|----------|------|---------|
| AT&T BGW320 (House 1) | ApertureScience | 2.4+5 GHz | — | — | WPA2/3 | — |
| **Flint 2 (Hub 2)** | ApertureScience | 2.4 GHz | 7 | 573 Mbit | WPA2/WPA3 | 0 (fresh) |
| **Flint 2 (Hub 2)** | ApertureScience | 5 GHz | 40 | 2401 Mbit | WPA2/WPA3 | 0 (fresh) |

### Services

| Service | Host | Status |
|---------|------|--------|
| nftables (plasma membrane) | sporeGate | ✅ active (52 rules) |
| dnsmasq (DHCP+DNS) | sporeGate | ✅ active |
| WireGuard (wg0) | sporeGate | ✅ active |
| Forgejo | sporeGate | ❌ inactive |
| Caddy | sporeGate | ❌ inactive (TLS at golgi) |
| Sovereign CI depot | sporeGate | ✅ build-local.sh + depot-sync.sh |
| Caddy (TLS) | golgiBody | ❌ inactive |
| Forgejo (golgi) | golgiBody | ✅ (upstream, serves SSH:2222) |
| WG hub | golgiBody | ✅ 4 peers, forwarding enabled |

---

## Issues Identified

### P1: eastGate unreachable on mesh

eastGate (10.13.37.5) does not respond to ping via WG overlay. May be powered off or WG service stopped. No impact on other gates — golgi hub forwarding is confirmed working (flockGate reachable at 69ms).

### P1: ironGate WG handshake never established

ironGate peer is configured on sporeGate (`A4MpSecI1N5+...`) but has never completed a handshake. ironGate's WG config likely needs the correct hub peer (golgiBody) endpoint and key. The golgi side also needs the ironGate peer added.

**Blocked on**: ironGate team adding sporeGate pubkey to their `authorized_keys` for remote SSH enrollment.

### P2: Forgejo inactive on sporeGate

Forgejo is not running on sporeGate (likely intentional — Forgejo runs on golgiBody). Confirm this is the desired topology.

### P2: Caddy inactive on golgiBody

golgiBody's Caddy (TLS terminator for primals.eco) is inactive. May need restart.

### P3: Unidentified LAN devices

Three IP addresses on the LAN (`.111`, `.147`, `.169`) have unidentified MACs. Should be inventoried — likely phones, tablets, or IoT devices picking up DHCP from the 192.168.4.0/22 pool.

---

## Architecture Diagram (Post-Eero)

```
Internet
  │
[ISP] BGW320 (192.168.1.254)
  │
sporeGate (192.168.1.233 WAN → 192.168.4.1 LAN → 10.13.37.2 WG)
  │  ├─ NAT/FW (nftables plasma membrane, 52 rules)
  │  ├─ DHCP/DNS (dnsmasq)
  │  ├─ Sovereign CI (cargo build → rsync to golgi)
  │  └─ WG spoke → golgiBody hub
  │
  ├─── eno1 (LAN 192.168.4.0/22) ─── Cat6 ─── Omada CRS310 (Hub 2)
  │                                                ├── eastGate (.111? / WG .5)
  │                                                ├── ironGate (.237 / WG .7)
  │                                                ├── Flint 2 (.250) ── WiFi "ApertureScience"
  │                                                │     ├── 2.4 GHz (ch7, HE20, WPA2/3)
  │                                                │     └── 5 GHz (ch40, HE80, WPA2/3)
  │                                                └── strandGate (deferred)
  │
  └─── wg0 (10.13.37.0/24) ─── golgiBody VPS ([RELAY_PUBLIC])
                                    ├── WG hub (4 peers)
                                    ├── Forgejo (SSH:2222)
                                    ├── WAN depot
                                    └── relay
                                         ├── flockGate (WG .6, WAN site)
                                         └── golgiBody-ext (137.184.197.151)
```

---

## Flint 2 Management Reference

| Property | Value |
|----------|-------|
| Model | GL-MT6000 (Flint 2) |
| Firmware | OpenWrt 21.02-SNAPSHOT, GL.iNet 4.8.4 |
| SoC | MediaTek MT7986 (Filogic 830), aarch64 |
| Bridge IP | 192.168.4.250/22 |
| SSH | `root@192.168.4.250`, key: sporegate-gate-v1 |
| Password | `sp0r3Gat3fw` (root) |
| WiFi SSID | `ApertureScience` (both bands) |
| WiFi Password | `exoticpanda714` |
| WiFi Auth | WPA2PSK/WPA3SAE mixed, AES |
| Bridge ports | lan1-5 + eth1 (WAN) + ra0 (2.4G) + rax0 (5G) |
| DHCP | Disabled (bridge passthrough) |
| Firewall | Disabled (bridge mode) |
| 802.11k/v | Enabled (assisted roaming) |

### Headless provisioning recipe (for future GL.iNet devices)

```bash
# 1. From sporeGate, add temp IP to reach factory 192.168.8.1
sudo ip addr add 192.168.8.100/24 dev eno1

# 2. Initialize via RPC (sets password, enables SSH)
curl http://192.168.8.1/rpc -d \
  '{"jsonrpc":"2.0","id":1,"method":"call","params":["","ui","init",{"lang":"en","username":"root","password":"PASSWORD","security_rule":0}]}'

# 3. SSH in, configure bridge, add SSH key, reboot
sshpass -p 'PASSWORD' ssh root@192.168.8.1

# 4. Note: WiFi SSID/key must be set in MediaTek .dat files, not UCI
#    /etc/wireless/mediatek/mt7986-ax6000.dbdc.b0.dat (2.4G)
#    /etc/wireless/mediatek/mt7986-ax6000.dbdc.b1.dat (5G)
```

---

## For Upstream Teams

### cellMembrane Team

Flint 2 is enrolled but not as a `gate` — it's infrastructure (bridge AP). No NUCLEUS deployment needed. However, the manifest should eventually track infrastructure devices separately from gates.

Consider: `[infrastructure.flint2]` section in `ecosystem_manifest.toml` for AP/switch/router inventory.

### ironGate Node Team

Your gate is on the LAN (192.168.4.237, confirmed reachable). WG overlay enrollment is blocked on:
1. Add sporeGate pubkey (`sporegate-gate-v1`) to your `~/.ssh/authorized_keys`
2. Verify your WG config has golgiBody as peer with endpoint `[RELAY_PUBLIC]:51820`

Once SSH is open, NUCLEUS deployment (13/13 primals + systemd) takes ~5 minutes.

### primalSpring Overwatch

New validation scenarios:
1. **WiFi parity**: verify SSID matches across all APs (AT&T + Flint 2)
2. **Bridge health**: ping Flint 2 at .250, verify zero DHCP leases (bridge mode)
3. **Eero absence**: confirm no Eero MACs (f8:bb:bf / 34:db:fd prefixes) in ARP table
4. **LAN device inventory**: identify unknown MACs at .111, .147, .169

---

## Updated Metrics

| Metric | Previous | Current |
|--------|----------|---------|
| WiFi APs | 1 (AT&T) + Eero mesh | 1 (AT&T) + 1 (Flint 2) |
| Cloud dependency | Eero → Amazon cloud | **Zero** (Flint 2 fully local) |
| Max WiFi rate (Hub 2) | ~600 Mbit (Eero WiFi 5) | **2401 Mbit** (Flint 2 WiFi 6, HE80) |
| WiFi auth | WPA2 only (Eero) | **WPA2/WPA3 mixed** (Flint 2) |
| WiFi roaming | Basic (Eero mesh) | **802.11k/v** assisted |
| LAN devices visible | 8 | 9 (+ Flint 2) |
| WG mesh peers | 5 configured | 3 active (golgi, sporeGate, flockGate) |
| Infrastructure managed agentically | 0 | **1** (Flint 2 — SSH from sporeGate) |

---

## Post-Topology Fixes (Jun 21 12:46 EDT)

### WG Routing Fix

Removed local ironGate peer (no endpoint) from sporeGate `wg0.conf`. This peer's `/32` AllowedIPs took priority over golgi's `/24`, creating a routing black hole. ironGate is now reachable at 102ms through golgi hub. Full mesh: golgi (29ms), eastGate (62ms), ironGate (102ms). flockGate offline.

### DHCP Enabled

Enabled DHCP on sporeGate dnsmasq: `dhcp-range=192.168.4.100,192.168.4.200,255.255.252.0,12h`. Previously no device served DHCP on the 192.168.4.0/22 subnet — WiFi clients on the Flint 2 had no way to get an IP. Now fixed.

### HPC VLAN Designed

Created `compute-sharing/HPC_VLAN_DESIGN.toml` with full VLAN topology for the 10G backbone. VLAN 10 (192.168.10.0/24) for gate-to-gate compute, carried over the MikroTik↔Omada 10G fiber trunk. Implementation blocked on switch credentials.

## Next Actions

| Priority | Action | Owner | Unblocks |
|----------|--------|-------|----------|
| P0 | ironGate SSH key exchange (copy/paste provided above) | ironGate team | NUCLEUS deploy |
| P1 | [ISP] BGW320 IP Passthrough (MAC: [MAC_SCRUBBED]) | Operator | Eliminate double NAT |
| P1 | MikroTik CRS310 credential recovery (reset button 5s) | Operator | VLAN config, HPC backbone |
| P1 | Purchase Flint 2 for House 1 (~$90 GL-MT6000) | Operator | WiFi sovereignty, SPOF fix |
| P2 | eastGate SSH connectivity investigation | sporeGate overwatch | Mesh integrity |
| P2 | Omada SX3008F access recovery (restart SDN controller) | sporeGate overwatch | House 2 VLAN config |
| P2 | LAN device inventory (.111, .147, .169) | sporeGate overwatch | Security audit |
| P3 | Flint 2 firmware update (4.8.4 → latest) | sporeGate overwatch | Security patches |
| P3 | Manifest `[infrastructure]` section | cellMembrane team | Device inventory in manifest |
