# AAR — Flint 2 #2 House 1 Deployment

**Date**: June 24, 2026
**Wave**: 126
**Device**: GL.iNet Flint 2 (GL-MT6000), firmware 4.8.4
**Operator**: sporeGate agentic (SSH + GL.iNet RPC API)
**Duration**: ~45 min (including 3 power cycles, 1 bridge loop recovery)
**Outcome**: SUCCESS — House 1 WiFi sovereign on `ApertureScience`

---

## Timeline

| Time | Event |
|------|-------|
| 11:13 | Flint 2 powered on, label photographed (MAC [MAC_SCRUBBED]) |
| 11:15 | Device discovered at 192.168.1.109 ([ISP] subnet, WAN port connected to [ISP]) |
| 11:17 | sporeGate wlp3s0 connected to Flint default WiFi (GL-MT6000-358) |
| 11:18 | Admin panel reachable at 192.168.8.1 via WiFi LAN interface |
| 11:20 | Password set + WiFi configured via GL.iNet RPC `ui.init` API call |
| 11:22 | SSH enabled, 5GHz SSID corrected to `ApertureScience` |
| 11:24 | Bridge mode configured via UCI — **ERROR: eth1 (WAN port) added to bridge** |
| 11:25 | Bridge loop: [ISP] + CRS310 on same L2 segment. Flint L3 dead, WiFi still broadcasting |
| 11:28 | User unplugged ATT→WAN cable. Flint still unreachable (eth1 = CRS310 uplink path) |
| 11:35 | Identified: CRS310 cable in "WAN/LAN1" port = `eth1` in UCI, removed from bridge |
| 11:38 | User moved CRS310 cable from WAN/LAN1 to LAN2 (1G). Flint came online |
| 11:42 | Port mapping confirmed: `lan1` = 2.5G LAN port, `eth1` = WAN/LAN1 combo port |
| 11:45 | eth1 re-added to bridge, then removed. Clean config: `lan1-lan5` only |
| 11:49 | User swapped cable to `lan1` (2.5G). Confirmed 2500Mbps link speed |
| 12:07 | Full validation: ping, SSH, DNS, WiFi, 2.5G link — all green |
| 12:07 | Static DHCP: 192.168.4.251 (`flint2-hub1`) confirmed |

---

## Root Causes of Issues

### 1. Bridge Loop (Critical)

**What happened**: Added `eth1` to the bridge while a cable from [ISP] was
also connected to `eth1`. This bridged the [ISP] network (192.168.1.x) with
the sporeGate network (192.168.4.x) at L2, creating DHCP conflicts and
broadcast storms.

**Lesson**: Never add a WAN-facing port to a bridge without confirming what's
on the other end. Bridge mode bridges ALL traffic including DHCP — two DHCP
servers on the same L2 = chaos.

**Future mitigation**: metalForge should validate bridge membership against
known network segments before allowing config commits.

### 2. Port Name / Physical Label Mismatch (High)

**What happened**: The physical port labeled "WAN/LAN1" on the GL-MT6000
maps to `eth1` in UCI (WAN mode by default), NOT to `lan1`. The UCI name
`lan1` maps to a different physical port. Cable was plugged into "WAN/LAN1"
(eth1) but the bridge only had `lan1-lan5`.

**Lesson**: GL.iNet firmware port naming is model-specific and doesn't always
match physical labels. The "WAN/LAN1" combo port defaults to WAN mode (eth1)
and only becomes `lan1` when explicitly switched via firmware.

**Port map for GL-MT6000 (confirmed)**:

| Physical Label | UCI Name | Speed | Default Mode |
|---------------|----------|-------|-------------|
| WAN | eth1 | 2.5G | WAN (DHCP client) |
| WAN/LAN1 | eth1 (WAN mode) or lan1 (LAN mode) | 2.5G | WAN |
| LAN1 | lan1 | 2.5G | Bridge member |
| LAN2 | lan2 | 1G | Bridge member |
| LAN3 | lan3 | 1G | Bridge member |
| LAN4 | lan4 | 1G | Bridge member |
| LAN5 | lan5 | 1G | Bridge member |

**Correction**: After testing, `lan1` at 2500Mbps is the correct 2.5G port.
The CRS310 cable was moved there for max throughput.

**Future mitigation**: metalForge `device_registry.toml` must include
physical-to-UCI port mapping for each device model. Provisioning probes
should verify carrier state on expected ports before applying bridge config.

### 3. GL.iNet First-Boot Requires Web Wizard (Medium)

**What happened**: SSH is disabled until the admin password is set via the
web wizard (JavaScript SPA). curl can't complete the wizard. The web admin
is only accessible from the LAN side (192.168.8.x), not the WAN side.

**Solution found**: GL.iNet RPC API endpoint `ui.init` accepts headless
initialization:

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": ["", "ui", "init", {
    "lang": "en",
    "username": "root",
    "password": "<password>",
    "ssid": "<ssid>",
    "password_wifi": "<wifi_password>",
    "password_wifi_5g": "<wifi_password_5g>"
  }]
}
```

**Prerequisite**: Must be on the Flint's LAN subnet (192.168.8.x) or have
a route/alias. The RPC endpoint is at `http://192.168.8.1/rpc`.

**Future mitigation**: metalForge should include a `glinet-provision` probe
that automates first-boot initialization via this RPC call.

### 4. DHCP Renewal Kills SSH (Low)

**What happened**: Killing udhcpc to force a DHCP renewal releases the
current IP, dropping the SSH session. The new IP can't be reached because
we don't know it yet.

**Solution**: Use `nohup /etc/init.d/network restart &` via SSH to schedule
the restart, or let the lease expire naturally (dnsmasq static reservation
takes effect on next renewal).

**Future mitigation**: Always use background network restarts when connected
via the device's own IP.

---

## Hardening Recommendations

### For metalForge

1. **Device Port Registry**: Add physical-to-UCI port mapping per device
   model in `device_registry.toml`. Validate port carrier state before
   bridge config changes.

2. **GL.iNet Provision Probe**: Automate first-boot via `ui.init` RPC.
   Include `check_initialized` pre-check and post-validation.

3. **Bridge Safety Probe**: Before adding a port to a bridge, verify the
   remote end's network segment. Never bridge two different DHCP domains.

4. **Rollback Timer**: When making network changes remotely, set a cron
   job to revert config if the device becomes unreachable within 60s
   (similar to OpenWrt's `apply with revert` mechanism).

### For Provisioning Playbooks

1. **Cable-first, config-second**: Always connect cables to the correct
   ports BEFORE applying bridge mode. Verify link state via SSH.

2. **One port at a time**: When adding ports to a bridge, add one, verify
   connectivity, then add the next. Never batch-add ports to a bridge.

3. **Label your cables**: Physical labels on ethernet cables at both ends
   prevent the "which port is this" debugging cycle.

### For Heterogeneous Hardware Abstraction

The ecosystem runs GL.iNet (OpenWrt), MikroTik (RouterOS), TP-Link (Omada),
and commodity switches (SG605S). Each has different:

- Port naming conventions (UCI vs RouterOS vs Omada)
- Management interfaces (SSH+UCI, WinBox/REST, Omada SDN)
- Bridge/VLAN semantics
- Firmware update mechanisms

**metalForge must abstract these differences**:

```
[device_model.gl_mt6000]
manufacturer = "GL.iNet"
firmware = "OpenWrt (GL.iNet 4.x)"
management = "ssh+uci"
provision_api = "glinet_rpc"
ports = [
    { physical = "WAN", uci = "eth1", speed = 2500, default_role = "wan" },
    { physical = "LAN1", uci = "lan1", speed = 2500, default_role = "bridge" },
    { physical = "LAN2", uci = "lan2", speed = 1000, default_role = "bridge" },
    { physical = "LAN3", uci = "lan3", speed = 1000, default_role = "bridge" },
    { physical = "LAN4", uci = "lan4", speed = 1000, default_role = "bridge" },
    { physical = "LAN5", uci = "lan5", speed = 1000, default_role = "bridge" },
]

[device_model.mikrotik_crs310]
manufacturer = "MikroTik"
firmware = "RouterOS"
management = "ssh+ros"  # blocked until creds recovered
ports = [
    { physical = "ether1-8", ros = "ether1-ether8", speed = 2500, default_role = "switch" },
    { physical = "SFP+1", ros = "sfp-sfpplus1", speed = 10000, default_role = "trunk" },
    { physical = "SFP+2", ros = "sfp-sfpplus2", speed = 10000, default_role = "trunk" },
]
```

This enables metalForge probes to:
- Know which physical port corresponds to which software interface
- Validate bridge membership against the expected topology
- Detect cable-in-wrong-port errors before they cause outages
- Generate provisioning scripts for any supported device model

---

## Final State

```
Flint 2 #2 (GL-MT6000) — House 1

IP:     192.168.4.251 (static, flint2-hub1.primals.local)
MAC:    [MAC_SCRUBBED] (bridge)
Mode:   Bridge (DHCP from sporeGate, no local DHCP/DNS/firewall)
Uplink: lan1 → CRS310 ether port (2.5G, confirmed 2500Mbps)
WiFi:   ApertureScience (2.4GHz ch9 + 5GHz ch44, WPA2)
SSH:    root@192.168.4.251 (password: sporeG8secure)

WAN port (eth1): Empty, not in bridge. Reserved for future [ISP] emergency bypass.
Firewall: Disabled (not needed in bridge mode).
```

**All radio at House 1 is now sovereign.** [ISP] WiFi still broadcasting
(`Aperture Science` with space) but on a different SSID — no conflict.
Needs manual disable at `http://192.168.1.254` when convenient.
