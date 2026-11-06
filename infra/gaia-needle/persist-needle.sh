#!/system/bin/sh
# ╔════════════════════════════════════════════════════════════╗
# ║  GAIA NEEDLE — Boot Persistence                            ║
# ║  Makes the HID gadget and wireless ADB survive reboots     ║
# ║  Installs as a Magisk boot service                         ║
# ╚════════════════════════════════════════════════════════════╝
#
# Run via ADB as root:
#   adb shell su -c "sh /data/local/tmp/persist-needle.sh"

MODULE_DIR="/data/adb/modules/gaia-needle"
SERVICE_DIR="$MODULE_DIR/service.d"

echo ">>> Installing Gaia Needle Magisk module..."

# Create Magisk module structure
mkdir -p "$SERVICE_DIR"
mkdir -p "$MODULE_DIR/system"

# Module descriptor
cat > "$MODULE_DIR/module.prop" << 'EOF'
id=gaia-needle
name=Gaia Needle
version=v1.0
versionCode=1
author=Gaia
description=USB HID keyboard gadget + persistent wireless ADB
EOF

# Boot service: runs after device boots, sets up HID gadget
cat > "$SERVICE_DIR/gaia-needle-boot.sh" << 'BOOT'
#!/system/bin/sh
# Gaia Needle boot service — runs at every boot via Magisk

# Wait for USB to be ready
sleep 10

GADGET="/config/usb_gadget/g1"

# Skip if already active
[ -c /dev/hidg0 ] && exit 0

# Create HID function
mkdir -p "$GADGET/functions/hid.keyboard" 2>/dev/null
echo 1 > "$GADGET/functions/hid.keyboard/protocol"
echo 1 > "$GADGET/functions/hid.keyboard/subclass"
echo 8 > "$GADGET/functions/hid.keyboard/report_length"
printf '\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x03\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x03\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0' > "$GADGET/functions/hid.keyboard/report_desc"

UDC=$(cat "$GADGET/UDC")
echo "" > "$GADGET/UDC"
ln -sf "$GADGET/functions/hid.keyboard" "$GADGET/configs/b.1/hid.keyboard" 2>/dev/null
echo "$UDC" > "$GADGET/UDC"

# Ensure wireless ADB stays active
setprop persist.adb.tcp.port 5555

# Log
echo "$(date): Gaia Needle HID active" >> /data/local/tmp/needle-boot.log
BOOT

chmod 755 "$SERVICE_DIR/gaia-needle-boot.sh"

echo "✓ Magisk module installed at $MODULE_DIR"
echo "  HID gadget will activate on every boot"
echo "  Wireless ADB will persist on port 5555"
echo ""
echo "  Reboot to verify boot persistence"
