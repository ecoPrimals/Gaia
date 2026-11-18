<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# AAR — sporeGate Fragility & Single-Point-of-Failure Debt

**Date**: June 24, 2026
**Wave**: 126
**Gate**: sporeGate
**Trigger**: Reboot during printer provisioning dropped RustDesk, DNS, DHCP, NAT, and WireGuard simultaneously. Operator had to resort to USB phone hotspot for access.

---

## Incident Timeline

1. Operator begins WiFi printer provisioning at House 2
2. Printer setup offers WPS (insecure) or manual IP — neither is seamless
3. Something during the attempt triggers a sporeGate reboot (09:10)
4. ALL services go down simultaneously: DHCP, DNS, NAT, RustDesk relay, WireGuard endpoint, NUCLEUS fleet
5. northGate (House 1) loses RustDesk connectivity — no remote access to sporeGate
6. Operator must physically connect USB hotspot from mobile phone
7. Services restore after boot (09:11), but RustDesk session from northGate is broken
8. Ad-hoc recovery: USB tethering + WiFi both active, creating 3 default routes

---

## Root Cause: sporeGate is a Single Point of Everything

sporeGate currently runs ALL of the following with zero redundancy:

| Function | Impact When Down |
|----------|-----------------|
| DHCP server (dnsmasq) | All WiFi/LAN clients lose IP renewal |
| DNS resolver (dnsmasq + stubby DoT) | All LAN devices lose name resolution |
| NAT / Firewall (nftables + masquerade) | All LAN devices lose internet |
| WireGuard endpoint (.2) | Mesh overlay partitioned from hub |
| RustDesk relay (21115-21117) | Remote access from northGate severed |
| Sovereign CI (build authority) | No primal builds possible |
| NestGate (content-addressed storage) | Depot operations blocked |
| 13 NUCLEUS primals | Fleet compute halted |

**A single reboot takes down the entire ecosystem for all users and all gates.**

---

## Fragility Patterns Found

### 1. No DHCP Lease Persistence

dnsmasq has no explicit `dhcp-leasefile` configured. Default path not found on disk. After reboot, all clients must re-request leases. This causes brief connectivity gaps for WiFi devices.

**Fix**: Add `dhcp-leasefile=/var/lib/dnsmasq/dnsmasq.leases` to `/etc/dnsmasq.conf` and ensure the directory exists.

### 2. Stale DNS Entry from Wrong Subnet

```
address=/printer.primals.local/192.168.1.114
```

Points to the old AT&T subnet (192.168.1.x), not the LAN subnet (192.168.4.x). This is dead config debt from pre-passthrough era.

**Fix**: Remove or update to correct subnet once printer is provisioned.

### 3. Route Table Pollution

9 routes across 4 interfaces. Three default routes with overlapping metrics:

```
default via [NUCLEUS_WAN] dev enp1s0 metric 100   ([ISP] WAN)
default via 172.20.10.1 dev enx4a352b698dd0 metric 100   (USB hotspot)
default via 172.20.10.1 dev wlp3s0 metric 600   (WiFi hotspot)
```

[ISP] WAN and USB hotspot share metric 100. Traffic could route through the wrong interface. The 192.168.1.0/24 subnet appears on BOTH WAN and LAN interfaces.

**Fix**: USB hotspot should have metric > 200 (backup only). Remove stale 192.168.1.0/24 LAN route when not needed.

### 4. NVIDIA Driver Noise

25+ `NVRM: No NVIDIA GPU found` errors every boot. sporeGate has AMD GPU (Ryzen 5 6600H). The NVIDIA driver package is installed but has no hardware.

**Fix**: `sudo apt remove --purge nvidia-*` or blacklist the module.

### 5. Stale Mangle Table (Not Persisted)

Live ruleset contains a mangle table from AT&T passthrough setup:

```
table ip mangle { chain prerouting {
    iifname "enp1s0" ip daddr 192.168.1.0/24 ip daddr != 192.168.1.233 mark 0x1
}}
```

This rule is NOT in `/etc/nftables.conf` and will vanish on reboot. Either persist it or confirm it's stale.

**Fix**: If needed, add to `/etc/nftables.conf`. If stale, remove with `nft delete table ip mangle`.

### 6. systemd-networkd DHCP Server Conflict

`/etc/systemd/network/20-lan.network` has `DHCPServer=yes` with its own static leases, while dnsmasq ALSO serves DHCP. Two DHCP servers on the same interface is a race condition.

**Fix**: Remove `DHCPServer=yes` and `[DHCPServer*]` sections from the networkd config (dnsmasq is authoritative).

### 7. No Self-Monitoring or Self-Healing

When services crash or reboot occurs:
- No heartbeat check restarts failed services
- No notification to operator
- No health endpoint other gates can query
- metalForge probes run manually, not continuously

**Fix**: systemd watchdog on critical services, metalForge as a periodic health daemon, songBird mesh.status broadcast.

### 6. RustDesk Relay Depends on sporeGate Uptime

northGate's only remote path to sporeGate is through RustDesk, which runs ON sporeGate. Circular dependency — the tool to fix sporeGate requires sporeGate to be running.

**Fix**: Secondary access path. Options:
- golgi as RustDesk relay fallback (VPS, always up)
- SSH via WireGuard from any other gate (eastGate, ironGate)
- Flint 2 as emergency management AP with known static IP

---

## Recommended Debt Resolution (Before Adding Hardware)

### Immediate (This Wave)

| # | Action | Effort |
|---|--------|--------|
| 1 | Add `dhcp-leasefile` to dnsmasq, ensure dir exists | 5 min |
| 2 | Remove stale `printer.primals.local` DNS entry | 2 min |
| 3 | Clean USB hotspot route metrics (NetworkManager priority) | 10 min |
| 4 | Remove NVIDIA driver package | 5 min |
| 5 | Verify nftables persistence path (no `/etc/nftables.conf` file found — rules load from service, confirm mechanism) | 10 min |

### Next Wave (Before Flint 2 #2)

| # | Action | Effort |
|---|--------|--------|
| 6 | systemd watchdog for dnsmasq, stubby, WireGuard, RustDesk | 30 min |
| 7 | metalForge health daemon (periodic probe loop + alerting) | 2-4 hr |
| 8 | golgi as backup RustDesk relay (secondary access path) | 1 hr |
| 9 | cellMembrane `gate.health` endpoint for mesh-wide status | 2-4 hr |

### Future (Tier 3 Isomorphism)

| # | Action | Effort |
|---|--------|--------|
| 10 | DHCP failover (secondary dnsmasq on Flint 2 or ironGate) | 4 hr |
| 11 | DNS failover (secondary resolver) | 2 hr |
| 12 | gate.migrate: live-migrate NUCLEUS fleet off sporeGate during maintenance | Large |

---

## For Upstream Teams

### cellMembrane
- `gate.health` endpoint: expose service liveness as JSON-RPC method
- `temporal.watchdog`: restart primals that crash, notify via mesh
- Route-priority management: `membrane network.audit` to detect metric conflicts

### metalForge
- Continuous probe mode (`metalforge-cli probe --daemon --interval 60s`)
- Alert on degradation (service down > 30s)
- Lease file audit probe

### songBird
- `mesh.status` broadcast: periodic heartbeat so all gates know who's alive
- Failover path registration: if sporeGate goes dark, route through golgi

---

## Conclusion

The ecosystem infrastructure is proven and the firewall/mesh/DNS stack is solid when running. The problem is **resilience** — a single reboot cascades into total service loss with no automated recovery and no secondary access path. This debt must be resolved before adding the Flint 2 #2 hardware, which would increase the blast radius of any future outage.

## Addendum: AT&T WiFi Radio Still Active (DHCP Conflict)

**Discovery**: The Epson ET-2400 printer on ApertureScience WiFi received IP
`192.168.1.114` from the **AT&T BGW320's DHCP server** instead of sporeGate's
dnsmasq. The AT&T gateway's WiFi radios are still broadcasting and serving
DHCP on the 192.168.1.0/24 subnet, creating a competing DHCP server.

**Impact**: Any WiFi client can get an IP from the wrong DHCP server (AT&T
instead of sporeGate), landing on the wrong subnet with no DNS blocklist,
no DoT, and no sovereign DNS entries.

**Fix (with Flint 2 #2 provisioning)**:
1. Disable AT&T BGW320 WiFi radios (both 2.4GHz and 5GHz) via gateway admin
2. Flint 2 #2 takes over ALL House 1 WiFi (same SSID: ApertureScience)
3. AT&T BGW320 becomes pure ethernet WAN ingress — no radio, no DHCP for WiFi
4. Printer will then DHCP from sporeGate → moves to 192.168.4.200 automatically

**Current state**: Printer works at `printer.primals.local` → `192.168.1.114`
(ad-hoc, on AT&T subnet). DHCP reservation ready at `.200` for when it migrates.

---

**Priority**: Resolve items 1-5 immediately, items 6-9 before Flint 2 #2 provisioning.
