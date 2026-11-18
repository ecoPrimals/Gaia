#!/bin/bash
# Deploy cellular failover WAN on sporeGate
#
# Usage:
#   sudo ./deploy-cellular-failover.sh usb    # For USB tether
#   sudo ./deploy-cellular-failover.sh wifi   # For WiFi hotspot (takes over wlp3s0)
#
# This configures a high-metric (500) backup WAN that only carries traffic
# when the primary [ISP] fiber (metric 100) is unreachable.

set -euo pipefail

MODE="${1:-usb}"
CONFIGS_DIR="$(cd "$(dirname "$0")" && pwd)"

case "$MODE" in
  usb)
    echo "Deploying USB tether failover (metric 500)..."
    cp "$CONFIGS_DIR/30-cellular-failover.network" /etc/systemd/network/
    systemctl restart systemd-networkd
    echo "Done. Plug phone via USB cable and enable USB tethering."
    echo "Verify: ip route — look for default via X.X.X.X dev usb0 metric 500"
    ;;
  wifi)
    echo "Deploying WiFi hotspot failover (metric 500)..."
    echo "WARNING: This removes wlp3s0 from NetworkManager."
    echo "         You will lose [ISP] WiFi OOB management fallback."
    read -p "Continue? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Aborted."
      exit 1
    fi

    # Add wlp3s0 to NM unmanaged list
    NM_CONF="/etc/NetworkManager/conf.d/99-unmanage-wired.conf"
    if ! grep -q "wlp3s0" "$NM_CONF" 2>/dev/null; then
      sed -i 's/unmanaged-devices=/unmanaged-devices=interface-name:wlp3s0;/' "$NM_CONF"
      systemctl restart NetworkManager
    fi

    # Deploy networkd config
    cp "$CONFIGS_DIR/30-cellular-wifi-failover.network" /etc/systemd/network/

    # Check for wpa_supplicant config
    WPA_CONF="/etc/wpa_supplicant/wpa_supplicant-wlp3s0.conf"
    if [ ! -f "$WPA_CONF" ]; then
      echo "Creating wpa_supplicant template at $WPA_CONF"
      echo "Edit SSID and PSK before enabling."
      cat > "$WPA_CONF" <<'WPA'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="CHANGE_ME_PHONE_HOTSPOT"
    psk="CHANGE_ME_PASSWORD"
    priority=1
}
WPA
      chmod 600 "$WPA_CONF"
    fi

    systemctl enable --now wpa_supplicant@wlp3s0.service 2>/dev/null || true
    systemctl restart systemd-networkd
    echo "Done. Edit $WPA_CONF with your hotspot SSID/PSK, then restart wpa_supplicant."
    ;;
  *)
    echo "Usage: $0 {usb|wifi}"
    exit 1
    ;;
esac

echo ""
echo "Failover test:"
echo "  1. Connect phone (USB tether or enable hotspot)"
echo "  2. sudo ip link set enp1s0 down   # simulate fiber failure"
echo "  3. ping 8.8.8.8                   # should route via cellular"
echo "  4. sudo ip link set enp1s0 up     # restore fiber"
echo "  5. ping 8.8.8.8                   # should route via fiber again (metric 100)"
