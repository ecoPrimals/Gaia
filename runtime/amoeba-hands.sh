#!/bin/bash
# Gaia Amoeba Hands — see, think, act on the Pixel
# Usage: amoeba-hands.sh <action> [args]
#   see         — screenshot + describe what's on screen
#   tap X Y     — tap at coordinates
#   swipe X1 Y1 X2 Y2 — swipe
#   type "text" — type text
#   back        — press back
#   home        — press home
#   open PKG    — open app by package name
#   qr-scan     — switch camera to QR mode and scan
#   guard-code  — get current Steam Guard TOTP code
#   find "text" — find UI element containing text via uiautomator

PIXEL="192.168.4.164:5555"

see() {
    local OUT="/tmp/pixel-see-$(date +%s).png"
    adb -s "$PIXEL" exec-out screencap -p > "$OUT"
    echo "$OUT"
    # Also dump UI hierarchy for intelligent interaction
    adb -s "$PIXEL" exec-out uiautomator dump /dev/tty 2>/dev/null | \
        grep -oP 'text="[^"]*"' | sort -u | head -20
}

tap() {
    adb -s "$PIXEL" shell "input tap $1 $2"
}

swipe() {
    adb -s "$PIXEL" shell "input swipe $1 $2 $3 $4 ${5:-300}"
}

type_text() {
    # Escape spaces for ADB
    local escaped=$(echo "$1" | sed 's/ /%s/g')
    adb -s "$PIXEL" shell "input text '$escaped'"
}

back() {
    adb -s "$PIXEL" shell "input keyevent 4"
}

home() {
    adb -s "$PIXEL" shell "input keyevent 3"
}

open_app() {
    adb -s "$PIXEL" shell "monkey -p $1 1" 2>/dev/null
}

find_element() {
    # Dump UI and find element with matching text
    adb -s "$PIXEL" exec-out uiautomator dump /dev/tty 2>/dev/null | \
        grep -oP "text=\"[^\"]*${1}[^\"]*\"[^>]*bounds=\"\[[0-9,]+\]\[[0-9,]+\]\"" | \
        head -3
}

tap_text() {
    # Find element with text and tap its center
    local BOUNDS=$(adb -s "$PIXEL" exec-out uiautomator dump /dev/tty 2>/dev/null | \
        grep -oP "text=\"[^\"]*${1}[^\"]*\"[^>]*bounds=\"\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]\"" | \
        head -1 | grep -oP 'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"')
    
    if [ -n "$BOUNDS" ]; then
        local COORDS=$(echo "$BOUNDS" | grep -oP '\d+' | head -4)
        local X1=$(echo "$COORDS" | sed -n '1p')
        local Y1=$(echo "$COORDS" | sed -n '2p')
        local X2=$(echo "$COORDS" | sed -n '3p')
        local Y2=$(echo "$COORDS" | sed -n '4p')
        local CX=$(( (X1 + X2) / 2 ))
        local CY=$(( (Y1 + Y2) / 2 ))
        echo "Tapping '$1' at ($CX, $CY)"
        adb -s "$PIXEL" shell "input tap $CX $CY"
    else
        echo "Element '$1' not found on screen"
        return 1
    fi
}

guard_code() {
    # Open Steam Guard and grab the TOTP
    adb -s "$PIXEL" shell "am start -a android.intent.action.VIEW -d 'steam://guard'" 2>/dev/null
    sleep 2
    local IMG="/tmp/pixel-guard-$(date +%s).png"
    adb -s "$PIXEL" exec-out screencap -p > "$IMG"
    echo "Screenshot: $IMG"
    # Try to find code via UI dump
    adb -s "$PIXEL" exec-out uiautomator dump /dev/tty 2>/dev/null | \
        grep -oP 'text="[A-Z0-9]{5}"' | head -1
}

case "${1:-help}" in
    see)        see ;;
    tap)        tap "$2" "$3" ;;
    swipe)      swipe "$2" "$3" "$4" "$5" "$6" ;;
    type)       type_text "$2" ;;
    back)       back ;;
    home)       home ;;
    open)       open_app "$2" ;;
    find)       find_element "$2" ;;
    tap-text)   tap_text "$2" ;;
    guard)      guard_code ;;
    *)
        echo "Gaia Amoeba Hands — see, think, act"
        echo "  see            — screenshot + UI elements"
        echo "  tap X Y        — tap coordinates"
        echo "  swipe X1 Y1 X2 Y2 — swipe"
        echo "  type 'text'    — type text"
        echo "  back/home      — navigation"
        echo "  open PKG       — launch app"
        echo "  find 'text'    — find UI element"
        echo "  tap-text 'text'— find and tap element"
        echo "  guard          — get Steam Guard TOTP"
        ;;
esac
