# After Action Report: sporeGate Live Deployment (Wave 115)

**Date**: 2026-06-16
**Duration**: ~4 hours (initial activation through stable LAN)
**Outcome**: SUCCESS — full sovereign routing for multi-subnet LAN
**Gate**: sporeGate (GMKtec NucBox M6, Pop!_OS 22.04)

---

## Summary

sporeGate was deployed as a live LAN router replacing the MikroTik CRS310's
L3 function. The deployment was performed via a USB kit with scripted configs,
but required significant adhoc intervention due to real-world topology
complexity not anticipated in the deployment kit.

---

## Adhoc Interventions (things the kit didn't handle)

### 1. Interface Naming Surprise

**Problem**: Kit referenced `enp2s0` for LAN. Actual kernel name was `eno1`.
**Root cause**: The NucBox M6's onboard Realtek NIC gets `eno1` as primary name
with `enp2s0` as an altname. systemd-networkd matched via altname — worked by luck.
**Impact**: dnsmasq and nftables both had `enp2s0` hardcoded → service failures.
**Fix**: Updated dnsmasq.conf and nftables.conf to use `eno1`.
**Lesson**: Deployment kits should either:
- Use udev `.rules` files for deterministic naming
- Auto-detect interfaces by MAC or PCI path
- Use systemd `.link` files to force names

### 2. IP Conflict with CRS310

**Problem**: Both sporeGate and CRS310 claimed `[LAN_IP]`.
**Root cause**: CRS310 was still in router mode serving DHCP from that IP.
**Fix**: Temporarily used `[LAN_IP]` for sporeGate, factory-reset CRS310 via
REST API (password from sticker), then reclaimed `[LAN_IP]`.
**Lesson**: Kit should include a "pre-flight" that scans for IP conflicts before
assuming the target IP is available.

### 3. Dnsmasq vs systemd-resolved Port Conflict

**Problem**: Dnsmasq couldn't bind port 53 — systemd-resolved was listening.
**Fix**: `systemctl disable --now systemd-resolved`
**Lesson**: Kit's install script should disable systemd-resolved automatically.

### 4. Cross-Subnet Routing (192.168.1.x on bridge)

**Problem**: Eero mesh clients have [ISP]-range IPs (192.168.1.x) but are physically
on the CRS310 bridge (same L2 as eno1). They couldn't reach the internet because:
- Their gateway is [LAN_IP] ([ISP]) which is on enp1s0
- But their traffic arrives on eno1
- sporeGate's `rp_filter` dropped these "impossible source" packets
- Return traffic from NAT had no route back to 192.168.1.x via eno1

**Fix** (multi-step, discovered iteratively):
1. Disabled `rp_filter` globally and on eno1
2. Enabled `proxy_arp` on eno1 (answer ARPs for [LAN_IP])
3. Added policy routing: fwmark 0x1 → table 100 → [LAN_IP]/24 dev eno1
4. Added nftables mangle: mark de-NATed return packets going to 192.168.1.x
5. Added /32 host routes for known clients

**Lesson**: Any deployment where the LAN bridge carries multiple subnets needs:
- Proxy ARP for the foreign gateway
- Policy routing for return traffic
- rp_filter=0 (or loose mode)
This should be a documented pattern: "multi-subnet bridge routing"

### 5. Omada Router (10.0.x.x subnet)

**Problem**: The Omada router creates its own 10.0.4.0/22 subnet for WiFi clients.
Initially assumed clients might need direct routing through sporeGate.
**Discovery**: Omada is doing its own NAT — all client traffic appears as
[LAN_IP] to sporeGate. No adhoc routing needed for normal operation.
**Adhoc added anyway**: Route `10.0.0.0/16 dev eno1` + mangle mark for 10.0.x.x.
This is defensive — handles the case where Omada is switched to bridge mode.
**Lesson**: When downstream routers do their own NAT (double-NAT), the upstream
router doesn't need special routing. Document this in topology so future operators
don't over-engineer.

### 6. IPv6 Black Hole (iPhone Stall)

**Problem**: iPhones connected to Eero WiFi could not load any content. Xbox worked.
**Root cause**: IPv6 forwarding was enabled in sysctl (`net.ipv6.conf.all.forwarding=1`)
but there was NO ip6 NAT (masquerade) rule. iPhones received IPv6 addresses via
SLAAC from Eero, tried IPv6 first (Apple's preference), packets forwarded out WAN
with private IPv6 src, return traffic never came back. iPhone waited for timeout (~30s)
before falling back to IPv4. Xbox either skipped IPv6 or fell back faster.
**Fix**: 
- Disabled IPv6 forwarding: `net.ipv6.conf.all.forwarding = 0`
- Added `table ip6 filter` with forward chain `policy drop`
- Clients now get immediate "no route" for IPv6, instant fallback to working IPv4.
**Lesson**: NEVER enable IPv6 forwarding without also configuring IPv6 NAT or having
a real IPv6 prefix delegation from the ISP. Kit should either:
- Include ip6 masquerade rule
- Or explicitly disable IPv6 forwarding (safer default)
- Document: "iPhone stall = usually IPv6 half-configured"

### 7. Secondary IP for DHCP Migration

**Problem**: After reclaiming [LAN_IP], existing LAN clients still had cached
DHCP leases pointing to [LAN_IP] (temporary IP) as DNS server.
**Fix**: Added `[LAN_IP]/22` as secondary address on eno1. Made dnsmasq listen
on both [LAN_IP] and [LAN_IP].
**Lesson**: When migrating gateway IP, always add the old IP as secondary until
all leases expire. Kit should include a "migration mode" that auto-detects and
preserves previous gateway IPs.

### 8. NetworkManager Interference

**Problem**: NetworkManager tried to manage wired interfaces, conflicting with
systemd-networkd's configuration.
**Fix**: Created `/etc/NetworkManager/conf.d/99-unmanage-wired.conf` excluding
`enp1s0`, `eno1`, and `enp2s0` from NM management.
**Lesson**: On Pop!_OS / Ubuntu desktop, NM is always present. Kit must include
the unmanage conf file. Alternatively, use Ubuntu Server which doesn't have NM.

---

## Deployment Kit Improvements (for next gate)

### Pre-flight checks (add to kit)
```bash
# 1. Detect actual interface names
IFACES=$(ip -j link show | jq -r '.[] | select(.link_type=="ether") | .ifname')
# 2. Scan for IP conflicts
arping -c 1 -I $LAN_IFACE $TARGET_IP
# 3. Check for port 53 listeners
ss -tlnp | grep :53
# 4. Check for existing DHCP servers on LAN
sudo tcpdump -i $LAN_IFACE -c 5 "port 67 or port 68"
```

### Config templating (replace hardcoded interface names)
```bash
# Use variables in all configs
WAN_IFACE=$(detect_wan_interface)
LAN_IFACE=$(detect_lan_interface)
sed -i "s/__WAN__/$WAN_IFACE/g" /etc/nftables.conf
sed -i "s/__LAN__/$LAN_IFACE/g" /etc/nftables.conf
```

### IPv6 safety default
```ini
# /etc/sysctl.d/99-router.conf — include this ALWAYS
net.ipv6.conf.all.forwarding = 0
# Only enable after configuring ip6 NAT or prefix delegation
```

### Multi-subnet bridge pattern (new doc for kit)
If LAN bridge carries devices from multiple subnets (common with mesh WiFi):
1. `proxy_arp=1` on LAN interface
2. `rp_filter=0` on LAN interface and globally
3. Policy route: mark de-NATed return traffic → send back to LAN
4. Dispatcher script for routes that can't be expressed in .network files

---

## Timeline

| Time | Event |
|------|-------|
| ~17:00 | USB kit mounted, instructions reviewed |
| ~17:15 | Deps installed, configs deployed |
| ~17:20 | First lockout (NM + networkd conflict) |
| ~17:30 | Fallback via WiFi, reworked NM exclusion |
| ~17:45 | IP conflict discovered (CRS310 vs sporeGate) |
| ~18:00 | CRS310 factory reset via REST API |
| ~18:15 | Basic routing working (192.168.4.x clients) |
| ~18:30 | DNS issues (systemd-resolved conflict, wrong listen-address) |
| ~18:45 | Cross-subnet debugging begins (192.168.1.x clients) |
| ~19:30 | rp_filter + proxy ARP + policy routing = working |
| ~20:15 | RustDesk installed and configured |
| ~20:30 | Full persistence (boot-stable) |
| ~20:40 | IPv6 issue discovered (iPhone stall) |
| ~20:42 | IPv6 forwarding disabled — iPhones restored |
| ~20:55 | Topology documented, primal onboarding started |
| ~21:05 | membrane fetched, 13 primals in depot, gate.bootstrap dry-run passes |

---

## Metrics

- **Total downtime for LAN clients**: ~45 min (during CRS310 reset + IP migration)
- **Adhoc interventions**: 8 (documented above)
- **Config files modified post-deployment**: 5 (nftables, dnsmasq, sysctl, NM, dispatcher)
- **New files created adhoc**: 2 (dispatcher script, ip6 filter)
- **Active clients at end**: 9 wired + N wireless via Omada
- **Conntrack utilization**: 366/262144 (0.14%)
- **Internet latency**: 10-15ms to 8.8.8.8

---

## Recommendations for cellMembrane Team

1. **gate.bootstrap should handle multi-subnet**: Add a `--topology bridge` flag
   that auto-configures proxy ARP + policy routing when it detects multiple subnets.

2. **Pre-flight scanner**: Add `membrane gate.preflight` command that checks interface
   names, IP conflicts, port availability, and existing DHCP servers before deploying.

3. **IPv6 policy**: Default to disabled forwarding. Add `membrane ipv6.enable` when
   ready with proper NAT66 or PD.

4. **Interface detection**: Use `membrane gate.detect-interfaces` instead of hardcoding.
   Match by driver, PCI path, or speed to determine WAN vs LAN.

5. **Rollback improvement**: Kit's rollback advice is "unplug sporeGate" — this works
   but should also include: restore NM management, flush nftables, stop dnsmasq.

6. **RustDesk integration**: Add `membrane remote.configure --relay golgiBody` to
   auto-fetch the hbbs key and configure RustDesk in one command.
