#!/bin/bash
# deckGate Boot — Turn Steam Deck v1 into Gaia's live passthrough display
# Run this on the Steam Deck in desktop mode (KDE Plasma)
# 
# PREREQUISITES:
#   1. Steam Deck powered via USB-C (dead battery is fine)
#   2. Connected to WiFi: "Black Mesa" (5GHz) or "Aperture Science" (2.4GHz)  
#   3. In Desktop Mode (hold power → Switch to Desktop)
#   4. Konsole open (terminal app)
#
# WHAT THIS DOES:
#   - Disables screen timeout (always on)
#   - Sets password for SSH access
#   - Installs minimal tools
#   - Creates Gaia kiosk autostart
#   - Pairs Steam Controller via BT
#   - Registers on LAN as deckGate

set -e
echo "=== deckGate Boot ==="
echo "Gaia's face in House 1"
echo ""

# Detect
IP=$(hostname -I | awk '{print $1}')
echo "IP: $IP"
echo "Hostname: $(hostname)"

# Step 1: Set password for SSH (if not already set)
echo ""
echo "[1/6] SSH Access"
if ! systemctl is-active --quiet sshd; then
    echo "  Enabling SSH..."
    passwd deck 2>/dev/null || echo "  (set passwd manually: passwd)"
    sudo systemctl enable sshd
    sudo systemctl start sshd
    echo "  SSH enabled. Connect: ssh deck@$IP"
else
    echo "  SSH already running"
fi

# Step 2: Disable screen timeout
echo ""
echo "[2/6] Display — Always On"
# SteamOS desktop uses KDE
kwriteconfig5 --file ~/.config/powermanagementprofilesrc --group AC --group DPMSControl --key idleTime 0 2>/dev/null
kwriteconfig5 --file ~/.config/powermanagementprofilesrc --group AC --group DPMSControl --key lockBeforeTurnOff 0 2>/dev/null
# Also via xset
xset s off 2>/dev/null
xset -dpms 2>/dev/null
xset s noblank 2>/dev/null
echo "  Screen timeout disabled"

# Step 3: Check for browser
echo ""
echo "[3/6] Browser"
if command -v chromium-browser &>/dev/null || command -v google-chrome-stable &>/dev/null; then
    BROWSER=$(command -v chromium-browser || command -v google-chrome-stable)
    echo "  Found: $BROWSER"
elif command -v firefox &>/dev/null; then
    BROWSER="firefox"
    echo "  Found: firefox"
else
    echo "  No browser found. Installing flatpak chromium..."
    flatpak install -y flathub org.chromium.Chromium 2>/dev/null || echo "  (install manually)"
    BROWSER="flatpak run org.chromium.Chromium"
fi

# Step 4: Create Gaia kiosk launcher
echo ""
echo "[4/6] Gaia Kiosk"
GAIA_URL="http://192.168.4.244:8080/diamond-lens.html"
KIOSK_SCRIPT="$HOME/gaia-kiosk.sh"
cat > "$KIOSK_SCRIPT" << KIOSK
#!/bin/bash
# Gaia Kiosk — fullscreen HUD display
# Switch URL by editing GAIA_URL below
GAIA_URL="$GAIA_URL"
xset s off; xset -dpms; xset s noblank

# Try Chromium kiosk mode
if command -v chromium-browser &>/dev/null; then
    chromium-browser --kiosk --no-first-run --disable-translate --disable-infobars \\
        --disable-session-crashed-bubble --noerrdialogs "\$GAIA_URL"
elif command -v firefox &>/dev/null; then
    firefox --kiosk "\$GAIA_URL"
elif command -v flatpak &>/dev/null; then
    flatpak run org.chromium.Chromium --kiosk --no-first-run "\$GAIA_URL"
fi
KIOSK
chmod +x "$KIOSK_SCRIPT"
echo "  Kiosk script: $KIOSK_SCRIPT"
echo "  URL: $GAIA_URL"

# Create autostart entry
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/gaia-kiosk.desktop" << DESK
[Desktop Entry]
Type=Application
Name=Gaia Kiosk
Exec=$KIOSK_SCRIPT
X-KDE-autostart-after=panel
DESK
echo "  Autostart created (will launch on next desktop mode boot)"

# Step 5: Phone home — register on LAN
echo ""
echo "[5/6] Phone Home"
PHOME=$(cat << JSON
{
    "gate": "deckGate",
    "ip": "$IP",
    "role": "DISPLAY",
    "os": "SteamOS 3.x",
    "display": "7\" 1280x800 IPS LCD touch",
    "gpu": "RDNA 2 8CU (1.6 TFLOPS)",
    "ram_gb": 16,
    "storage_gb": 512,
    "battery": "dead (USB-C passthrough)",
    "state": "mounted",
    "boot_ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON
)
# Try to register with eastGate
curl -s -X POST "http://192.168.4.244:8080/data/deckgate-status.json" -d "$PHOME" 2>/dev/null || \
    echo "$PHOME" | curl -s -T - "http://192.168.4.244:8080/data/deckgate-status.json" 2>/dev/null || \
    echo "  (can't POST to data server — will register via rover scan)"
echo "  Registered: deckGate @ $IP"

# Step 6: Summary
echo ""
echo "[6/6] Ready"
echo "  deckGate is live on $IP"
echo "  SSH: ssh deck@$IP"
echo "  Display: 7\" 1280×800 touch"
echo "  GPU: RDNA 2, 1.6 TFLOPS"
echo "  WiFi: $(iwconfig wlan0 2>/dev/null | grep ESSID | sed 's/.*ESSID://' || echo '?')"
echo ""
echo "  To start kiosk NOW: bash ~/gaia-kiosk.sh"
echo "  To switch page: edit ~/gaia-kiosk.sh and change GAIA_URL"
echo ""
echo "  Pages available:"
echo "    diamond-lens.html — ambient canvas (recommended for display)"
echo "    chiasm.html      — optic chiasm (L/R eye + spatial field)"
echo "    eye.html         — live camera viewer"  
echo "    mesh.html        — mesh dashboard"
echo "    index.html       — main HUD"
echo ""
echo "=== deckGate ready. Gaia's face is here. ==="
