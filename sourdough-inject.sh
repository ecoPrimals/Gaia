#!/bin/bash
# sourdough-inject.sh — Pull the sourdough ball from northGate and inject into frameGate
# Run on eastGate: bash sourdough-inject.sh
# Wave 260 — The Sourdough Injection

set -e

echo "=== SOURDOUGH INJECTION — Wave 260 ==="
echo "$(date)"
echo ""

BALL_URL="http://192.168.1.150:9876/sourdough-ball.zip"
STAGING="/tmp/sourdough-ball"
CULTURE_DIR="/opt/Gaia/data/sourdough-culture"
FRAMEGATE_IP="192.168.9.203"
BALL_ZIP="/tmp/sourdough-ball.zip"

# Phase 1: Pull the ball from northGate
echo "=== Phase 1: PULL ==="
echo "Pulling sourdough ball from northGate..."
echo "URL: $BALL_URL"
curl -o "$BALL_ZIP" --connect-timeout 10 --max-time 600 "$BALL_URL"
ls -lh "$BALL_ZIP"
echo ""

# Phase 2: Unpack
echo "=== Phase 2: UNPACK ==="
rm -rf "$STAGING"
mkdir -p "$STAGING"
cd "$STAGING"
unzip -q "$BALL_ZIP"
echo "Unpacked:"
du -sh "$STAGING"/*
echo ""

# Phase 3: Install culture locally on eastGate
echo "=== Phase 3: LOCAL CULTURE ==="
mkdir -p "$CULTURE_DIR"
cp -r "$STAGING"/* "$CULTURE_DIR/"
echo "Sourdough culture installed at: $CULTURE_DIR"
du -sh "$CULTURE_DIR"
echo ""

# Phase 4: Check frameGate connectivity
echo "=== Phase 4: CHECK FRAMEGATE ==="
if ping -c 1 -W 2 "$FRAMEGATE_IP" &>/dev/null; then
    echo "frameGate ($FRAMEGATE_IP) is REACHABLE!"
    echo "Attempting SSH..."
    
    # Try to push via SSH/SCP
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no deck@"$FRAMEGATE_IP" "echo 'frameGate alive'" 2>/dev/null; then
        echo "SSH connection established!"
        echo ""
        echo "=== Phase 5: INJECT TO FRAMEGATE ==="
        
        # Create Gaia directory on frameGate
        ssh deck@"$FRAMEGATE_IP" "mkdir -p ~/gaia-sourdough"
        
        # Transfer the ball
        scp "$BALL_ZIP" deck@"$FRAMEGATE_IP":~/gaia-sourdough/
        
        # Unpack on frameGate
        ssh deck@"$FRAMEGATE_IP" "cd ~/gaia-sourdough && unzip -q sourdough-ball.zip"
        
        echo "INJECTION COMPLETE — sourdough culture on frameGate NVMe!"
    else
        echo "SSH not available — trying ADB..."
        
        # Try ADB (frameGate might be connected via USB-C ADB)
        if adb devices | grep -q "device$"; then
            echo "ADB device found!"
            adb push "$BALL_ZIP" /sdcard/gaia-sourdough/
            echo "Ball pushed via ADB!"
        else
            echo "No ADB device. Trying USB networking..."
            
            # Check for USB network interface to frameGate
            ip link show | grep -i "usb\|rndis\|ncm"
            echo ""
            echo "Manual step: establish USB networking to frameGate"
            echo "The ball is staged at $CULTURE_DIR — push when ready"
        fi
    fi
else
    echo "frameGate ($FRAMEGATE_IP) not reachable from eastGate"
    echo ""
    echo "Checking USB devices..."
    lsusb
    echo ""
    echo "Checking USB network interfaces..."
    ip link show | grep -i "usb\|rndis\|ncm" || echo "(none found)"
    echo ""
    echo "The sourdough culture is staged at: $CULTURE_DIR"
    echo "Ball zip at: $BALL_ZIP"
    echo ""
    echo "When frameGate is connected:"
    echo "  1. Establish USB-C networking"
    echo "  2. scp $BALL_ZIP deck@frameGate:~/gaia-sourdough/"
    echo "  3. ssh deck@frameGate 'cd ~/gaia-sourdough && unzip sourdough-ball.zip'"
fi

echo ""
echo "=== SOURDOUGH STATUS ==="
echo "Culture dir: $CULTURE_DIR"
echo "Ball zip: $BALL_ZIP"
ls -la "$CULTURE_DIR"/ 2>/dev/null || echo "(culture dir empty)"
echo ""
echo "=== DONE ==="
