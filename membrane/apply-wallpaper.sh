#!/bin/bash
# Run this after Kevin unlocks the Pixel to set wallpaper autonomously
PIXEL="${1:-192.168.4.166:5555}"

echo "Waiting for unlock..."
while true; do
    # Check if screen is unlocked (can get window focus)
    STATE=$(adb -s $PIXEL shell "dumpsys window | grep 'mCurrentFocus'" 2>/dev/null)
    if echo "$STATE" | grep -q "StatusBar\|Launcher\|Home"; then
        echo "UNLOCKED! Setting wallpaper..."
        break
    fi
    sleep 5
done

# Open wallpaper picker flow
adb -s $PIXEL shell "am start -n com.android.wallpaper/.picker.CategoryPickerActivity" 2>/dev/null
sleep 3
# Tap Wallpapers
adb -s $PIXEL shell "input tap 540 1330"
sleep 2
# Tap Choose a photo  
adb -s $PIXEL shell "input tap 540 350"
sleep 3
# Scroll to find wallpapers
adb -s $PIXEL shell "input swipe 540 1800 540 1100 300"
sleep 1
adb -s $PIXEL shell "input swipe 540 1800 540 1100 300"
sleep 1
adb -s $PIXEL shell "input swipe 540 1800 540 1100 300"
sleep 2
# Tap first image (mycelium)
adb -s $PIXEL shell "input tap 85 580"
sleep 3
# Tap Next
adb -s $PIXEL shell "input tap 950 180"
sleep 3
# Tap Apply (careful with coordinates)
adb -s $PIXEL shell "input tap 540 1850"
sleep 2
adb -s $PIXEL shell "input tap 540 1870"
sleep 1

echo "Wallpaper applied!"
# Go home
adb -s $PIXEL shell "input keyevent KEYCODE_HOME"
