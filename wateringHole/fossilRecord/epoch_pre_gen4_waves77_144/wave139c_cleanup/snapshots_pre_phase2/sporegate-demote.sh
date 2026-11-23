#!/bin/bash
# sporeGate demotion — from edge router to compute node
# Run on: sporeGate DURING maintenance window
# When:   AFTER the [ISP] cable has been moved to Flint and Flint config is committed
#
# This script removes sporeGate's router duties:
#   - Stops dnsmasq (DHCP/DNS moves to Flint)
#   - Removes gateway IP (.1), keeps compute IP (.3)
#   - Sets default route through Flint (.1)
#   - Disables WAN interface (cable moved to Flint)
#   - Keeps: WireGuard, NUCLEUS, CI, RustDesk, Caddy

set -euo pipefail

echo "=== sporeGate Demotion: Router → Compute Node ==="
echo "Date: $(date)"
echo ""

# --- Step 1: Stop DHCP/DNS (Flint takes over) ---
echo "[1/5] Stopping dnsmasq..."
sudo systemctl stop dnsmasq
sudo systemctl disable dnsmasq
echo "  dnsmasq stopped and disabled"

# --- Step 2: Remove gateway IP, keep compute IP ---
echo "[2/5] Removing gateway IP (192.168.4.1)..."
sudo ip addr del 192.168.4.1/22 dev eno1 2>/dev/null || echo "  .1 already removed"
echo "  Keeping compute IP: 192.168.4.3/22"

# --- Step 3: Update networkd configs ---
echo "[3/5] Updating systemd-networkd configs..."

# LAN: compute node at .3, gateway is Flint at .1
sudo tee /etc/systemd/network/20-lan.network > /dev/null <<'EOF'
[Match]
Name=enp2s0

[Network]
Address=192.168.4.3/22
Gateway=192.168.4.1
DNS=192.168.4.1
IPForward=yes

[Route]
Destination=10.0.4.0/24
EOF

# WAN: disconnected (cable moved to Flint), mark unmanaged
sudo tee /etc/systemd/network/10-wan.network > /dev/null <<'EOF'
[Match]
Name=enp1s0

[Link]
Unmanaged=yes
EOF

echo "  networkd configs updated"

# --- Step 4: Apply network changes ---
echo "[4/5] Restarting systemd-networkd..."
sudo systemctl restart systemd-networkd
sleep 2

# Set default route explicitly (belt and suspenders)
sudo ip route replace default via 192.168.4.1 dev eno1 2>/dev/null || true
echo "  Default route: via 192.168.4.1 (Flint)"

# --- Step 5: Verify ---
echo "[5/5] Verifying..."
echo "  Interfaces:"
ip -4 addr show eno1 | grep inet
echo "  Default route:"
ip route show default
echo "  WireGuard:"
sudo wg show wg0 | head -5
echo ""
echo "=== sporeGate demoted to compute node ==="
echo "  IP: 192.168.4.3/22"
echo "  Gateway: 192.168.4.1 (Flint)"
echo "  WireGuard: running (port-forwarded through Flint)"
echo "  NUCLEUS/CI/RustDesk/Caddy: still running"
echo "  dnsmasq: STOPPED (Flint handles DHCP/DNS)"
