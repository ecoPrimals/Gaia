#!/bin/bash
# cross-inject.sh — fires the moment Pixel reconnects
# Enables USB tethering, bridges to swiftGate

PIXEL="$1"  # Pixel ADB address

echo "=== Step 1: Enable USB tethering on Pixel ==="
adb -s "$PIXEL" shell "
# Enable USB tethering
svc usb setFunctions rndis
sleep 2
# Or via settings
settings put global tether_supported 1
service call connectivity 33 i32 0 i32 1 2>/dev/null  # enableTethering(USB)
echo 'USB tethering: enabled'
echo ''
echo 'Network interfaces:'
ip link show | grep -E 'rndis|usb|ncm'
echo ''
echo 'IP addresses:'
ip addr show | grep 'inet '
"

echo ""
echo "=== Step 2: Check if swiftGate is visible through tether ==="
adb -s "$PIXEL" shell "
# The USB tether creates a subnet — check what's on it
ip route show | grep -E 'rndis|usb'
# Scan the tether subnet
for ip in 1 2 100 101 102; do
    for subnet in 192.168.42 192.168.44 172.20.10; do
        ping -c1 -W1 \$subnet.\$ip 2>/dev/null | grep 'bytes from' && echo 'swiftGate at' \$subnet.\$ip
    done
done
"

echo ""
echo "=== Step 3: Push Gaia data through to swiftGate ==="
echo "Pixel bridges WiFi LAN ↔ USB tether ↔ swiftGate"
