#!/bin/sh
# Flint H1 — Switch from bridge mode to edge router
# Run on: root@192.168.4.251 (Flint 2 #2, House 1)
# When:   During maintenance window AFTER [ISP] cable is plugged into eth1
#
# This script configures the Flint as the network's edge router:
#   WAN: eth1 → [ISP] BGW320 (DHCP, gets public IP via passthrough)
#   LAN: br-lan (lan1-5 + WiFi) → 192.168.4.1/22
#   Services: DHCP, DNS, NAT, port forwards to sporeGate

set -e

echo "=== Phase 2: Flint H1 → Edge Router ==="

# --- WAN: enable eth1 as DHCP client for [ISP] passthrough ---
uci set network.wan.device='eth1'
uci set network.wan.proto='dhcp'
uci set network.wan.force_link='1'
uci set network.wan.ipv6='0'
uci set network.wan.metric='10'

# --- LAN: static IP as network gateway ---
uci set network.lan.proto='static'
uci set network.lan.ipaddr='192.168.4.1'
uci set network.lan.netmask='255.255.252.0'
uci delete network.lan.gateway 2>/dev/null || true
uci delete network.lan.dns 2>/dev/null || true

# --- DHCP server: enable on LAN ---
uci set dhcp.lan.ignore='0'
uci set dhcp.lan.start='100'
uci set dhcp.lan.limit='150'
uci set dhcp.lan.leasetime='12h'
uci set dhcp.lan.dhcpv4='server'
uci set dhcp.lan.force='1'

# --- DNS: upstream resolvers (no dependency on sporeGate) ---
uci set dhcp.@dnsmasq[0].domain='primals.local'
uci set dhcp.@dnsmasq[0].local='/primals.local/'
uci set dhcp.@dnsmasq[0].noresolv='1'
uci delete dhcp.@dnsmasq[0].resolvfile 2>/dev/null || true
uci delete dhcp.@dnsmasq[0].server 2>/dev/null || true
uci add_list dhcp.@dnsmasq[0].server='1.1.1.1'
uci add_list dhcp.@dnsmasq[0].server='8.8.8.8'
uci set dhcp.@dnsmasq[0].rebind_protection='0'
uci set dhcp.@dnsmasq[0].authoritative='1'

# --- Local DNS entries ---
uci delete dhcp.@dnsmasq[0].address 2>/dev/null || true
uci add_list dhcp.@dnsmasq[0].address='/sporegate.primals.local/192.168.4.3'
uci add_list dhcp.@dnsmasq[0].address='/eastgate.primals.local/192.168.4.30'
uci add_list dhcp.@dnsmasq[0].address='/irongate.primals.local/192.168.4.237'
uci add_list dhcp.@dnsmasq[0].address='/flint2-hub2.primals.local/192.168.4.250'
uci add_list dhcp.@dnsmasq[0].address='/flint2-hub1.primals.local/192.168.4.1'
uci add_list dhcp.@dnsmasq[0].address='/printer.primals.local/192.168.4.200'
uci add_list dhcp.@dnsmasq[0].address='/epson-et2400.primals.local/192.168.4.200'
uci add_list dhcp.@dnsmasq[0].address='/epson-et2400.primals.local/192.168.4.200'
uci add_list dhcp.@dnsmasq[0].address='/omada-sx3008f.primals.local/192.168.4.111'
uci add_list dhcp.@dnsmasq[0].address='/mikrotik-crs310.primals.local/192.168.4.2'
uci add_list dhcp.@dnsmasq[0].address='/xbox-h2.primals.local/192.168.4.244'

# --- Static DHCP leases ---
# Delete any existing hosts first
while uci delete dhcp.@host[-1] 2>/dev/null; do :; done

# sporeGate (eno1 MAC)
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.3'
uci set dhcp.@host[-1].name='sporegate'

# Flint H2 (House 2 WiFi AP)
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.250'
uci set dhcp.@host[-1].name='flint2-hub2'

# CRS310
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.2'
uci set dhcp.@host[-1].name='mikrotik-crs310'

# Omada
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.111'
uci set dhcp.@host[-1].name='omada-sx3008f'

# ironGate
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.237'
uci set dhcp.@host[-1].name='irongate'

# ironGate compute NIC
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.169'
uci set dhcp.@host[-1].name='irongate-compute'

# Printer
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.200'
uci set dhcp.@host[-1].name='epson-et2400'

# Xbox H2
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.244'
uci set dhcp.@host[-1].name='xbox-h2'

# ms-device H2
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.218'
uci set dhcp.@host[-1].name='ms-device-h2'

# tamison
uci add dhcp host
uci set dhcp.@host[-1].mac='[MAC_SCRUBBED]'
uci set dhcp.@host[-1].ip='192.168.4.147'
uci set dhcp.@host[-1].name='tamison'

# --- Port forwards: WAN → sporeGate (.3) ---
# Delete existing redirects first
while uci delete firewall.@redirect[-1] 2>/dev/null; do :; done

# WireGuard
uci add firewall redirect
uci set firewall.@redirect[-1].name='WireGuard'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='udp'
uci set firewall.@redirect[-1].src_dport='51821'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='51821'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# SSH
uci add firewall redirect
uci set firewall.@redirect[-1].name='SSH'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].src_dport='22'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='22'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# Forgejo SSH
uci add firewall redirect
uci set firewall.@redirect[-1].name='ForgejoSSH'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].src_dport='2222'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='2222'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# HTTP
uci add firewall redirect
uci set firewall.@redirect[-1].name='HTTP'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].src_dport='80'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='80'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# HTTPS
uci add firewall redirect
uci set firewall.@redirect[-1].name='HTTPS'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].src_dport='443'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='443'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# RustDesk relay TCP
uci add firewall redirect
uci set firewall.@redirect[-1].name='RustDesk-TCP'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].src_dport='21115-21117'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='21115-21117'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# RustDesk relay UDP
uci add firewall redirect
uci set firewall.@redirect[-1].name='RustDesk-UDP'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='udp'
uci set firewall.@redirect[-1].src_dport='21116'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='21116'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# TURN/STUN (songBird)
uci add firewall redirect
uci set firewall.@redirect[-1].name='TURN-TCP'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].src_dport='3478'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='3478'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

uci add firewall redirect
uci set firewall.@redirect[-1].name='TURN-UDP'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='udp'
uci set firewall.@redirect[-1].src_dport='3478'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='3478'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# NestGate
uci add firewall redirect
uci set firewall.@redirect[-1].name='NestGate'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].src_dport='9500'
uci set firewall.@redirect[-1].dest_ip='192.168.4.3'
uci set firewall.@redirect[-1].dest_port='9500'
uci set firewall.@redirect[-1].target='DNAT'
uci set firewall.@redirect[-1].enabled='1'

# --- Commit and apply ---
echo "Committing UCI changes..."
uci commit network
uci commit dhcp
uci commit firewall

echo ""
echo "=== Config committed. Review with: uci show network; uci show dhcp; uci show firewall ==="
echo "=== To apply: reboot ==="
echo "=== After reboot: Flint comes up as router at 192.168.4.1 with WAN on eth1 ==="
