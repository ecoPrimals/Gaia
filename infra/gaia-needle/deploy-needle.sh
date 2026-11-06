#!/bin/bash
# ╔════════════════════════════════════════════════════════╗
# ║  GAIA NEEDLE — Deploy to Android device                ║
# ║  Turns any rooted Android into a wireless USB keyboard ║
# ╚════════════════════════════════════════════════════════╝
#
# Prerequisites:
#   - Device has unlocked bootloader
#   - Magisk installed with root + ADB access
#   - Device connected via ADB (USB or wireless)
#
# Usage: ./deploy-needle.sh <device>
#   device = ADB device ID (e.g., 192.168.9.217:5555 or serial)

set -e

DEVICE="${1:?Usage: deploy-needle.sh <adb-device>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SU="/debug_ramdisk/su"

echo "╔══════════════════════════════════════╗"
echo "║  GAIA NEEDLE — Deploying to $DEVICE"
echo "╚══════════════════════════════════════╝"

# ─── Verify connection ───
echo ""
echo ">>> Verifying ADB connection..."
adb -s "$DEVICE" shell echo "ADB OK" || { echo "✗ Cannot reach device"; exit 1; }

# ─── Verify root ───
echo ">>> Verifying root..."
ROOT_CHECK=$(adb -s "$DEVICE" shell "$SU -c id" 2>&1)
if echo "$ROOT_CHECK" | grep -q "uid=0"; then
    echo "✓ Root: $ROOT_CHECK"
else
    echo "✗ No root access. Ensure Magisk is installed and Superuser Access = 'Apps and ADB'"
    echo "  Got: $ROOT_CHECK"
    exit 1
fi

# ─── Enable persistent wireless ADB ───
echo ""
echo ">>> Enabling persistent wireless ADB..."
adb -s "$DEVICE" shell "$SU -c 'setprop persist.adb.tcp.port 5555'"
adb -s "$DEVICE" shell "$SU -c 'settings put global adb_wifi_enabled 1'"
echo "✓ Wireless ADB persistent on port 5555"

# ─── Setup USB HID keyboard gadget ───
echo ""
echo ">>> Setting up USB HID keyboard gadget..."
adb -s "$DEVICE" shell "$SU -c '
    # Create HID keyboard function
    mkdir -p /config/usb_gadget/g1/functions/hid.keyboard 2>/dev/null

    # Configure as keyboard (protocol=1, subclass=1, 8-byte reports)
    echo 1 > /config/usb_gadget/g1/functions/hid.keyboard/protocol
    echo 1 > /config/usb_gadget/g1/functions/hid.keyboard/subclass
    echo 8 > /config/usb_gadget/g1/functions/hid.keyboard/report_length

    # Standard USB HID keyboard report descriptor
    printf \"\\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0\" > /config/usb_gadget/g1/functions/hid.keyboard/report_desc

    # Link to active USB config (must unbind/rebind UDC)
    UDC=$(cat /config/usb_gadget/g1/UDC)
    echo "" > /config/usb_gadget/g1/UDC
    ln -sf /config/usb_gadget/g1/functions/hid.keyboard \
           /config/usb_gadget/g1/configs/b.1/hid.keyboard 2>/dev/null
    echo "$UDC" > /config/usb_gadget/g1/UDC

    # Verify
    if [ -c /dev/hidg0 ]; then
        echo "HID_OK"
    else
        echo "HID_FAIL"
    fi
'"

echo "✓ USB HID keyboard gadget active"

# ─── Push typing scripts ───
echo ""
echo ">>> Deploying scripts..."
adb -s "$DEVICE" push "$SCRIPT_DIR/type.sh" /data/local/tmp/type.sh
adb -s "$DEVICE" shell "$SU -c 'chmod 755 /data/local/tmp/type.sh'"

# Push target scripts
adb -s "$DEVICE" shell "mkdir -p /data/local/tmp/targets"
for target in "$SCRIPT_DIR"/targets/*.sh; do
    [ -f "$target" ] || continue
    adb -s "$DEVICE" push "$target" "/data/local/tmp/targets/$(basename "$target")"
    adb -s "$DEVICE" shell "$SU -c 'chmod 755 /data/local/tmp/targets/$(basename "$target")'"
done

echo "✓ Scripts deployed"

# ─── Save state ───
echo ""
echo ">>> Saving needle state..."
DEVICE_MODEL=$(adb -s "$DEVICE" shell getprop ro.product.model | tr -d '\r')
DEVICE_IP=$(adb -s "$DEVICE" shell "ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print \$2}' | cut -d/ -f1" | tr -d '\r')
MAGISK_VER=$(adb -s "$DEVICE" shell "$SU -c 'magisk -v'" 2>/dev/null | tr -d '\r')
BATTERY=$(adb -s "$DEVICE" shell cat /sys/class/power_supply/battery/capacity | tr -d '\r')

cat > "$SCRIPT_DIR/needle-state.json" << EOF
{
  "ts": "$(date -Iseconds)",
  "device": "$DEVICE",
  "model": "$DEVICE_MODEL",
  "wifi_ip": "$DEVICE_IP",
  "wireless_adb": "${DEVICE_IP}:5555",
  "magisk": "$MAGISK_VER",
  "hid": "/dev/hidg0",
  "battery": "$BATTERY%",
  "status": "NEEDLE_READY"
}
EOF
echo "✓ State saved to needle-state.json"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ★ NEEDLE DEPLOYED                           ║"
echo "║  Device: $DEVICE_MODEL"
echo "║  WiFi:   ${DEVICE_IP}:5555"
echo "║  Root:   Magisk $MAGISK_VER"
echo "║  HID:    /dev/hidg0 ACTIVE"
echo "║                                              ║"
echo "║  Plug USB-C into target, then run:           ║"
echo "║  ./inject.sh ${DEVICE_IP}:5555 --target NAME ║"
echo "╚══════════════════════════════════════════════╝"
