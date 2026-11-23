# sporeGate Activation — LAN Periplasm Router

**Hardware**: GMKtec NucBox M6 (Ryzen 7 6800H, 32GB RAM, 2x 2.5G RJ45)
**Role**: Sovereign LAN perimeter — NAT, firewall, DHCP, DNS, VPN, NUCLEUS primals
**Date**: 2026-06-16

---

## Physical Wiring

```
[ISP] Gateway LAN port ──RJ45──► sporeGate eth0 (WAN interface)
sporeGate eth1 (LAN interface) ──RJ45──► CRS310 RJ45 port
```

After wiring: CRS310 becomes pure L2 switch. sporeGate handles all L3.

---

## CRITICAL: WiFi as Out-of-Band Management

**sporeGate MUST keep WiFi enabled and connected at all times.**

Since sporeGate IS the LAN router, any misconfiguration of wired interfaces
locks out all other gates (including eastGate). WiFi provides an out-of-band
fallback so agents can still SSH in and self-heal without physical access.

```bash
# Ensure WiFi stays up even when systemd-networkd manages wired interfaces:
nmcli device wifi connect "<SSID>" password "<PSK>"
nmcli connection modify "<SSID>" connection.autoconnect yes
nmcli connection modify "<SSID>" ipv4.route-metric 600
# High route-metric ensures WiFi is fallback only (wired preferred for data)
```

**Biological analogy**: WiFi = flagellar emergency signaling — when the cell wall
(wired periplasm) is compromised, the organism retains a secondary communication path.

---

## Step 1: OS Install (if not already Linux)

Pop!_OS or Ubuntu Server 24.04. Either works. Key: systemd-networkd for networking.

---

## Step 2: Identify NICs

```bash
ip link show
# Find the two 2.5G interfaces (likely enp1s0, enp2s0 or similar)
# Label them: WAN (facing [ISP]) and LAN (facing CRS310)
```

---

## Step 3: Network Configuration

Create `/etc/systemd/network/10-wan.network`:
```ini
[Match]
Name=enp1s0

[Network]
DHCP=yes

[DHCPv4]
UseDNS=no
UseRoutes=yes
```

Create `/etc/systemd/network/20-lan.network`:
```ini
[Match]
Name=enp2s0

[Network]
Address=[LAN_IP]/22
DHCPServer=yes

[DHCPServer]
PoolOffset=100
PoolSize=150
DNS=[LAN_IP]
DefaultLeaseTimeSec=3600
```

Enable:
```bash
sudo systemctl enable --now systemd-networkd
sudo systemctl disable NetworkManager  # if present
```

---

## Step 4: IP Forwarding

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/99-router.conf
sudo sysctl -p /etc/sysctl.d/99-router.conf
```

---

## Step 5: NAT (nftables)

Create `/etc/nftables.conf`:
```
#!/usr/sbin/nft -f

flush ruleset

table ip filter {
    chain input {
        type filter hook input priority 0; policy drop;
        iif "lo" accept
        ct state established,related accept
        iifname "enp2s0" accept
        icmp type echo-request accept
        tcp dport 22 accept
        drop
    }

    chain forward {
        type filter hook forward priority 0; policy accept;
        ct state established,related accept
        iifname "enp2s0" accept
        drop
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}

table ip nat {
    chain postrouting {
        type nat hook postrouting priority 100; policy accept;
        oifname "enp1s0" masquerade
    }
}
```

Enable:
```bash
sudo systemctl enable --now nftables
```

---

## Step 6: DNS (dnsmasq)

```bash
sudo apt install dnsmasq
```

`/etc/dnsmasq.conf`:
```
interface=enp2s0
bind-interfaces
listen-address=[LAN_IP]
no-dhcp-interface=enp2s0
server=1.1.1.1
server=8.8.8.8
cache-size=1000
```

(DHCP is handled by systemd-networkd above, dnsmasq just does DNS caching.)

---

## Step 7: CRS310 Reconfiguration

After sporeGate is working as the gateway:
1. Access CRS310 WebFig (currently at [LAN_IP] — will change)
2. Remove all L3 config (IP addresses, DHCP server, NAT rules, firewall)
3. Set to bridge mode (all ports in one bridge, no routing)
4. Assign management IP: [LAN_IP]/22 (static, for WebFig access)
5. Result: CRS310 is a pure 10G/2.5G switch

---

## Step 8: Verify

```bash
# From any LAN device (eastGate, fieldGate):
ping [LAN_IP]        # sporeGate (should be <1ms)
ping 8.8.8.8            # internet via sporeGate NAT
ssh sporegate           # SSH to sporeGate
dig google.com @[LAN_IP]  # DNS resolution
```

---

## Step 9: NUCLEUS Deployment (after routing is stable)

Once routing is proven stable for 24h:
```bash
# On sporeGate:
mkdir -p ~/Development/ecoPrimals
# Clone from Forgejo (sovereign) or GitHub
git clone ssh://git@git.primals.eco:2222/ecoPrimals/cellMembrane.git ~[KEY_SCRUBBED]
# Build or fetch membrane binary
# Run gate.bootstrap sporeGate
```

Primals for sporeGate:
- bearDog (WireGuard key management)
- skunkBat (network monitoring)
- songBird (mesh hub / WAN relay)
- loamSpine (audit trail)

---

## Rollback

If anything breaks, unplug sporeGate and plug CRS310 directly back to [ISP].
All devices will get DHCP from CRS310 again (it's still configured as router until you strip its L3).
