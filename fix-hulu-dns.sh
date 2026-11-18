#!/bin/bash
# fix-hulu-dns.sh — Run on eastGate to fix the router's DNS/port forward
# This unpins the DNS port 53 forward so TV/Hulu can resolve normally
# The Tor hidden service stays — only ingress, no interception of household traffic
#
# Usage: bash fix-hulu-dns.sh
# Or from eastGate: sshpass -p 'ExoticPanda714!!' ssh root@192.168.4.1 < fix-hulu-dns.sh

ROUTER="192.168.4.1"
PASS="ExoticPanda714!!"

echo "=== HULU/DNS FIX — Wave 260 ==="
echo "$(date)"
echo ""

# Step 1: Check current port forwards
echo "--- Current port forwards ---"
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no root@$ROUTER \
    "uci show firewall | grep -E 'dest_port|name|src_dport|dest_ip|proto'" 2>/dev/null

echo ""
echo "--- Removing DNS (port 53) forward ---"
# Find and delete the DNS port forward rule
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no root@$ROUTER '
    # List all port forward rules
    echo "Current redirects:"
    uci show firewall | grep "redirect.*dest_port"

    # Find the DNS redirect (port 53)
    for rule in $(uci show firewall | grep "redirect" | grep "dest_port.*53" | cut -d. -f1-2 | sort -u); do
        name=$(uci get ${rule}.name 2>/dev/null)
        echo "  Found DNS redirect: $rule (name=$name)"
        echo "  Deleting..."
        uci delete $rule
    done

    # Also check for DNAT rules catching port 53
    for rule in $(uci show firewall | grep "rule" | grep "dest_port.*53" | cut -d. -f1-2 | sort -u); do
        target=$(uci get ${rule}.target 2>/dev/null)
        if [ "$target" = "DNAT" ]; then
            name=$(uci get ${rule}.name 2>/dev/null)
            echo "  Found DNAT DNS rule: $rule (name=$name)"
            echo "  Deleting..."
            uci delete $rule
        fi
    done

    # Make sure DHCP gives clients the router as DNS (not eastGate)
    echo ""
    echo "--- Fixing DHCP DNS ---"
    current_dns=$(uci get dhcp.@dnsmasq[0].server 2>/dev/null)
    echo "  Current upstream DNS: $current_dns"
    
    # Ensure dnsmasq uses ISP DNS, not eastGate
    uci delete dhcp.@dnsmasq[0].server 2>/dev/null
    uci add_list dhcp.@dnsmasq[0].server="192.168.1.254"
    uci add_list dhcp.@dnsmasq[0].server="8.8.8.8"
    echo "  Set upstream DNS to: ATT modem (192.168.1.254) + Google (8.8.8.8)"

    # Commit and restart
    echo ""
    echo "--- Committing ---"
    uci commit firewall
    uci commit dhcp
    
    echo "--- Restarting DNS ---"
    /etc/init.d/dnsmasq restart
    
    echo "--- Restarting firewall ---"
    /etc/init.d/firewall restart
    
    echo ""
    echo "DONE — DNS port 53 forward removed"
    echo "TV/Hulu should now resolve DNS through router → ATT modem"
    echo "Tor hidden service unaffected (uses eastGate local Tor, not router DNS)"
' 2>/dev/null

echo ""
echo "=== VERIFICATION ==="
echo "Testing DNS from router..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no root@$ROUTER \
    "nslookup hulu.com 2>/dev/null || echo 'nslookup not available'; echo ''; echo 'Port forwards remaining:'; uci show firewall | grep redirect | grep dest_port" 2>/dev/null

echo ""
echo "=== DONE ==="
echo "Hulu should work on TV now."
echo "Tor hidden service (.onion) is unaffected — ingress only."
echo "Port 80/443/25 forwards to eastGate remain (HTTP/HTTPS/SMTP)."
echo "Only DNS (53) forward removed."
