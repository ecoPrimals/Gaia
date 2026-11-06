#!/bin/bash
# ╔════════════════════════════════════════════════════════╗
# ║  GAIA NEEDLE — Inject a target machine                 ║
# ║  Types commands through the needle's USB keyboard      ║
# ╚════════════════════════════════════════════════════════╝
#
# Usage: ./inject.sh <needle-device> --target <name>
#   needle-device = ADB address of the needle (e.g., 192.168.9.217:5555)
#   target = injection target name (matches targets/<name>.sh)
#
# Or manual typing:
#   ./inject.sh <needle-device> --type "text to type"
#   ./inject.sh <needle-device> --line "command + enter"
#   ./inject.sh <needle-device> --ctrl-alt-t

set -e

NEEDLE="${1:?Usage: inject.sh <needle-device> [--target NAME | --type TEXT | --line TEXT]}"
shift

SU="/debug_ramdisk/su"
TYPE="/data/local/tmp/type.sh"

# Verify needle is connected
echo ">>> Connecting to needle at $NEEDLE..."
adb -s "$NEEDLE" shell echo "NEEDLE_OK" >/dev/null 2>&1 || {
    echo "✗ Cannot reach needle device at $NEEDLE"
    echo "  Try: adb connect $NEEDLE"
    exit 1
}

# Verify root and HID
adb -s "$NEEDLE" shell "$SU -c 'test -c /dev/hidg0 && echo HID_OK'" 2>/dev/null | grep -q HID_OK || {
    echo "✗ HID gadget not active on needle. Run deploy-needle.sh first."
    exit 1
}

echo "✓ Needle ready at $NEEDLE"

# ─── Route command ───

case "$1" in
    --target)
        TARGET="${2:?Specify target name}"
        TARGET_SCRIPT="/data/local/tmp/targets/${TARGET}.sh"
        echo ">>> Injecting target: $TARGET"
        adb -s "$NEEDLE" shell "$SU -c 'sh $TARGET_SCRIPT'" 2>&1
        ;;
    --type)
        shift
        echo ">>> Typing: $*"
        adb -s "$NEEDLE" shell "$SU -c 'sh $TYPE \"$*\"'" 2>&1
        ;;
    --line)
        shift
        echo ">>> Typing + Enter: $*"
        adb -s "$NEEDLE" shell "$SU -c 'sh $TYPE --line \"$*\"'" 2>&1
        ;;
    --enter)
        adb -s "$NEEDLE" shell "$SU -c 'sh $TYPE --enter'" 2>&1
        ;;
    --ctrl-alt-t)
        echo ">>> Sending Ctrl+Alt+T (open terminal)..."
        adb -s "$NEEDLE" shell "$SU -c 'sh $TYPE --ctrl-alt-t'" 2>&1
        ;;
    --interactive)
        echo ">>> Interactive mode — type commands, they appear on target"
        echo "    (Ctrl+D to exit)"
        while IFS= read -r -p "needle> " line; do
            adb -s "$NEEDLE" shell "$SU -c 'sh $TYPE --line \"$line\"'" 2>&1
            sleep 0.5
        done
        ;;
    *)
        echo "Usage: inject.sh <needle-device> [options]"
        echo ""
        echo "Options:"
        echo "  --target NAME       Run a target injection script"
        echo "  --type TEXT         Type text on target"
        echo "  --line TEXT         Type text + Enter on target"
        echo "  --enter             Press Enter"
        echo "  --ctrl-alt-t        Open terminal on Linux target"
        echo "  --interactive       Interactive typing mode"
        echo ""
        echo "Targets:"
        adb -s "$NEEDLE" shell "ls /data/local/tmp/targets/ 2>/dev/null" | sed 's/\.sh$//'
        ;;
esac
