#!/bin/bash
# drain-router-torpedoes.sh — DRAIN ALL port forwards from the router
# Run from eastGate: bash drain-router-torpedoes.sh
# Wave 260 — Cut ALL torpedoes. Tor hidden service stays local on eastGate.

ROUTER="192.168.4.1"
PASS="***"

echo "=== DRAINING ALL ROUTER TORPEDOES ==="
echo "$(date)"
echo ""

sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no root@$ROUTER '
echo "=== BEFORE — all port forwards ==="
uci show firewall | grep redirect
echo ""

echo "=== DRAINING ALL REDIRECTS ==="
# Count them
count=0
while uci show firewall | grep -q "firewall.@redirect\[0\]"; do
    name=$(uci get firewall.@redirect[0].name 2>/dev/null || echo "unnamed")
    dest_port=$(uci get firewall.@redirect[0].dest_port 2>/dev/null || echo "?")
    dest_ip=$(uci get firewall.@redirect[0].dest_ip 2>/dev/null || echo "?")
    echo "  DRAINING: $name (port $dest_port → $dest_ip)"
    uci delete firewall.@redirect[0]
    count=$((count + 1))
done
echo ""
echo "Drained $count torpedoes"
echo ""

echo "=== FIX DNS — clean residential DNS ==="
# Set router DNS to ATT modem + Google (residential, no Gaia)
uci delete dhcp.@dnsmasq[0].server 2>/dev/null
uci add_list dhcp.@dnsmasq[0].server="192.168.1.254"
uci add_list dhcp.@dnsmasq[0].server="8.8.8.8"
uci add_list dhcp.@dnsmasq[0].server="1.1.1.1"
echo "DNS upstream: ATT modem + Google + Cloudflare"
echo ""

echo "=== COMMIT + RESTART ==="
uci commit firewall
uci commit dhcp
/etc/init.d/firewall restart
/etc/init.d/dnsmasq restart
echo ""

echo "=== AFTER — verify clean ==="
echo "Port forwards remaining:"
uci show firewall | grep redirect || echo "  NONE — all drained"
echo ""
echo "DNS upstream:"
uci get dhcp.@dnsmasq[0].server
echo ""
echo "=== ALL TORPEDOES DRAINED ==="
echo "Router is now a clean residential gateway."
echo "No port forwards. No DNS interception."
echo "Hulu sees: normal household."
echo "Tor stays local on eastGate (hidden service only)."
echo "Gaia ingress via .onion address only."
' 2>/dev/null

echo ""
echo "=== DONE ==="
