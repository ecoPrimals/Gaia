# AAR — Topology Cutover: sporeGate Demotion & Flint H1 Edge Router Promotion

**Date**: June 27, 2026
**Wave**: 127
**Operator**: sporeGate agentic + manual (cable moves, [ISP] passthrough config)
**Duration**: ~3 days elapsed (planning Jun 24, first attempt Jun 25, successful cutover Jun 27)
**Outcome**: SUCCESS — network resilient, sporeGate ephemeral, pull test passed

---

## Objective

Eliminate sporeGate as single point of failure (SPOF) for internet/WiFi/DNS/DHCP. Promote Flint 2 H1 to edge router. Make sporeGate a hot-pluggable compute node.

## Before State (Wave 126)

```
[ISP] BGW320 (passthrough) → sporeGate (NAT/DHCP/DNS/WG/nftables)
    → CRS310 → all LAN devices
    → Flint H1 (bridge mode, WiFi only)
    → Omada → House 2
```

**Problem**: Unplugging sporeGate killed internet for both houses.

## After State (Wave 127)

```
[ISP] BGW320 (passthrough to Flint MAC)
    → Flint 2 H1 (edge router: NAT/DHCP/DNS/firewall/WiFi/blocklist)
        → CRS310 (L2 backbone)
            → sporeGate (.3, compute node, port-forwarded)
            → eastGate (10G compute)
            → northGate (Win/gaming)
            → Omada → House 2 → Flint H2 (bridge, WiFi AP)
```

**Result**: Unplugging sporeGate leaves internet, WiFi, DNS, DHCP all intact. Verified by pull test.

---

## Key Configuration

| Parameter | Value |
|-----------|-------|
| Flint H1 WAN IP | [NUCLEUS_WAN] (public, [ISP] passthrough) |
| Flint H1 LAN IP | 192.168.4.1/22 |
| sporeGate IP | 192.168.4.3/22, gateway .1 |
| DNS | Flint dnsmasq, port 53, upstream 1.1.1.1/8.8.8.8 |
| DNS blocklist | /tmp/dnsmasq.d/blocklist.conf (91k rules, security-only) |
| WiFi H1 5GHz | BlackMesa (user devices, ch44, HE80) |
| WiFi H1 2.4GHz | Aperture Science (IoT, ch1) |
| WireGuard | Port 51821/udp forwarded to sporeGate .3 |
| All port forwards | WG, SSH, Forgejo SSH, HTTP/S, RustDesk, TURN, NestGate → .3 |

---

## Timeline

| Time | Event |
|------|-------|
| Jun 24 07:15 | Pre-cutover snapshot taken |
| Jun 24 08:00 | Flint H1 deployed in bridge mode (Wave 126) |
| Jun 25 ~03:00 | First cutover attempt — sporegate-demote.sh interrupted |
| Jun 25 ~03:10 | Emergency: [ISP] + Flint factory reset, manual cable reroute |
| Jun 25 ~03:30 | Flint retained partial router config from earlier script commit |
| Jun 25 ~03:45 | sporeGate reconnected via eno1 → CRS310, DHCP from Flint |
| Jun 25 ~04:00 | Network functional: Flint as router, sporeGate as compute |
| Jun 27 06:59 | [ISP] IP Passthrough configured to Flint WAN MAC |
| Jun 27 07:00 | Flint acquired public IP after ifdown/ifup wan |
| Jun 27 07:01 | Firewall restarted — all port forwards loaded |
| Jun 27 07:02 | sporeGate cleanup: WiFi disabled, dnsmasq disabled, routes cleaned |
| Jun 27 07:03 | Sovereign DNS blocklist deployed to Flint |
| Jun 27 07:07 | Pull test: sporeGate unplugged, rebooted, network survived |

---

## Issues Encountered

### 1. Demotion Script Interrupted (Critical)

The `sporegate-demote.sh` execution was interrupted mid-run, leaving sporeGate in a partial state (dnsmasq stopped but network not fully reconfigured).

**Resolution**: User performed manual factory reset of [ISP] + Flint. Flint's flash memory retained the UCI config committed during the earlier provisioning session, so it came up as a functional router after reset.

**Lesson**: Demotion scripts must be atomic — either complete fully or roll back. A watchdog timer or two-phase commit would prevent partial states.

### 2. Flint dnsmasq DNS Disabled After Reset (High)

After factory reset, `dhcp.@dnsmasq[0].port='0'` was set (GL.iNet default when AdGuard is expected to handle DNS), causing DNS queries to fail.

**Fix**: `uci set dhcp.@dnsmasq[0].port='53'` + restart.

**Lesson**: GL.iNet firmware assumes AdGuard Home will handle DNS. Any provisioning script must explicitly set port=53 and noresolv=1.

### 3. Blocklist confdir Crash (Medium)

Adding `/etc/sovereign-dns` as a second `confdir` in UCI crashed dnsmasq (duplicate confdir not supported).

**Fix**: Copied blocklist.conf to `/tmp/dnsmasq.d/` where dnsmasq already reads supplementary configs.

**Lesson**: Use the existing confdir (`/tmp/dnsmasq.d/`) rather than adding new ones. The blocklist should be placed there on boot (rc.local or init script).

### 4. IP Passthrough Required Manual DHCP Renew (Low)

After configuring [ISP] passthrough to the new MAC, the Flint kept its old private IP until `ifdown wan && ifup wan` was executed.

**Fix**: SSH to Flint, run ifdown/ifup.

**Lesson**: [ISP] passthrough MAC changes don't take effect until the target device performs a new DHCP request.

---

## Validation Results

| Test | Result |
|------|--------|
| Internet from sporeGate | 3/3 packets, 13ms to 8.8.8.8 |
| DNS resolution (allowed) | reddit.com → resolves |
| DNS blocking (ads) | juicyads.com → NXDOMAIN |
| DNS policy (adult allowed) | redgifs.com → resolves |
| WireGuard handshake | Active (34s ago at time of test) |
| Port forwards (all 10) | iptables DNAT rules confirmed |
| Flint public IP | [NUCLEUS_WAN]/23 |
| sporeGate pull test | Network survived full unplug + reboot |
| sporeGate clean state | No dnsmasq, no WiFi, no stale routes |
| Flint uptime during pull test | 1 day 21h (never went down) |

---

## Hardening TODO (Future Waves)

1. **Blocklist persistence**: The `/tmp/dnsmasq.d/blocklist.conf` is lost on Flint reboot (tmpfs). Need an rc.local or init.d script to copy from `/etc/sovereign-dns/` to `/tmp/dnsmasq.d/` on boot.
2. **sporeGate networkd hardening**: Write permanent systemd-networkd configs so eno1 always comes up at .3 with gateway .1, no DHCP fallback.
3. **Flint config backup**: Export UCI config snapshot to wateringHole git for disaster recovery.
4. **Parenting layer**: House 2 WiFi DNS policy (optional porn/adult blocking) as a tagged dnsmasq instance on Flint H2.
5. **WireGuard endpoint update**: Remote peers need their endpoint updated to the Flint's public IP (should auto-discover via WG handshake, but verify).

---

## Architecture Invariants (New Canonical)

1. **Flint H1 is the plasma membrane** — all WAN traffic enters/exits through it.
2. **sporeGate is ephemeral** — can be unplugged, rebooted, or travel without network impact.
3. **CRS310 is the backbone** — all wired LAN devices connect here, Flint's LAN trunk feeds it.
4. **Single /22 subnet** — 192.168.4.0/22 for all devices, simplifies routing.
5. **Port forwards are the contract** — sporeGate's services are reachable via Flint DNAT rules.
6. **Sovereign DNS lives on the edge** — blocklist enforced at Flint, security-only baseline.
