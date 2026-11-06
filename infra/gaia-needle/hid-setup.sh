#!/system/bin/sh
# ╔════════════════════════════════════════════════════════╗
# ║  GAIA NEEDLE — USB HID Gadget Setup                    ║
# ║  Run as root on the needle device after reboot          ║
# ║  Creates /dev/hidg0 USB keyboard endpoint               ║
# ╚════════════════════════════════════════════════════════╝
#
# Usage (on device, as root):
#   sh hid-setup.sh
#
# After running, /dev/hidg0 will be a USB HID keyboard.
# Any machine connected via USB-C sees a standard keyboard.

GADGET="/config/usb_gadget/g1"

# Check prerequisites
if [ ! -d "$GADGET" ]; then
    echo "✗ USB gadget configfs not found at $GADGET"
    echo "  Kernel may not support USB gadget mode"
    exit 1
fi

# Check if already configured
if [ -c /dev/hidg0 ]; then
    echo "✓ HID gadget already active (/dev/hidg0 exists)"
    exit 0
fi

echo ">>> Setting up USB HID keyboard gadget..."

# Create HID function
mkdir -p "$GADGET/functions/hid.keyboard" 2>/dev/null

# Configure as boot keyboard
echo 1 > "$GADGET/functions/hid.keyboard/protocol"      # Keyboard
echo 1 > "$GADGET/functions/hid.keyboard/subclass"       # Boot interface
echo 8 > "$GADGET/functions/hid.keyboard/report_length"  # 8-byte reports

# Standard USB HID keyboard report descriptor (63 bytes)
# Supports modifiers (Ctrl/Shift/Alt/GUI) + 6 simultaneous keys
printf "\x05\x01"         # Usage Page (Generic Desktop)
printf "\x09\x06"         # Usage (Keyboard)
printf "\xa1\x01"         # Collection (Application)
printf "\x05\x07"         #   Usage Page (Key Codes)
printf "\x19\xe0"         #   Usage Minimum (224 = Left Control)
printf "\x29\xe7"         #   Usage Maximum (231 = Right GUI)
printf "\x15\x00"         #   Logical Minimum (0)
printf "\x25\x01"         #   Logical Maximum (1)
printf "\x75\x01"         #   Report Size (1)
printf "\x95\x08"         #   Report Count (8)
printf "\x81\x02"         #   Input (Data, Variable, Absolute) — Modifier byte
printf "\x95\x01"         #   Report Count (1)
printf "\x75\x08"         #   Report Size (8)
printf "\x81\x03"         #   Input (Constant) — Reserved byte
printf "\x95\x05"         #   Report Count (5)
printf "\x75\x01"         #   Report Size (1)
printf "\x05\x08"         #   Usage Page (LEDs)
printf "\x19\x01"         #   Usage Minimum (Num Lock)
printf "\x29\x05"         #   Usage Maximum (Kana)
printf "\x91\x02"         #   Output (Data, Variable, Absolute) — LED report
printf "\x95\x01"         #   Report Count (1)
printf "\x75\x03"         #   Report Size (3)
printf "\x91\x03"         #   Output (Constant) — LED padding
printf "\x95\x06"         #   Report Count (6)
printf "\x75\x08"         #   Report Size (8)
printf "\x15\x00"         #   Logical Minimum (0)
printf "\x25\x65"         #   Logical Maximum (101)
printf "\x05\x07"         #   Usage Page (Key Codes)
printf "\x19\x00"         #   Usage Minimum (0)
printf "\x29\x65"         #   Usage Maximum (101)
printf "\x81\x00"         #   Input (Data, Array) — Key array (6 keys)
printf "\xc0"             # End Collection
> "$GADGET/functions/hid.keyboard/report_desc" 2>/dev/null

# Alternative: write all at once (some shells don't handle printf sequences well)
if [ ! -s "$GADGET/functions/hid.keyboard/report_desc" ]; then
    echo ">>> Using binary write method..."
    printf '\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x03\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x03\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0' > "$GADGET/functions/hid.keyboard/report_desc"
fi

# Unbind UDC, link function, rebind
UDC=$(cat "$GADGET/UDC")
if [ -z "$UDC" ]; then
    echo "✗ No UDC controller found"
    exit 1
fi

echo "" > "$GADGET/UDC"
ln -sf "$GADGET/functions/hid.keyboard" "$GADGET/configs/b.1/hid.keyboard" 2>/dev/null
echo "$UDC" > "$GADGET/UDC"

# Verify
sleep 1
if [ -c /dev/hidg0 ]; then
    echo "✓ HID keyboard gadget active at /dev/hidg0"
    echo "  Protocol: $(cat $GADGET/functions/hid.keyboard/protocol)"
    echo "  Report length: $(cat $GADGET/functions/hid.keyboard/report_length)"
    echo "  UDC: $UDC"
    echo ""
    echo "  The device is now a USB keyboard."
    echo "  Use type.sh to send keystrokes."
else
    echo "✗ Failed to create /dev/hidg0"
    echo "  Check kernel support for USB HID gadget (CONFIG_USB_CONFIGFS_F_HID)"
    exit 1
fi
