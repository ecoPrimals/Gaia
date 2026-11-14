#!/system/bin/sh
# ═══════════════════════════════════════════════════════════════
#  gAIa ORGANISM — Living I/O Loop
#  Reads EVERY input. Drives EVERY output.
#  The phone is not running gAIa. The phone IS gAIa.
# ═══════════════════════════════════════════════════════════════
GAIA="/data/local/tmp/biomeos"
IO="$GAIA/sensorium/io"
mkdir -p "$IO"

# ═══ HEARTBEAT — vibrate with system pulse ═══
heartbeat() {
  while true; do
    # Feel the CPU load
    LOAD=$(cut -d. -f1 /proc/loadavg 2>/dev/null)
    # Light heartbeat: 50ms pulse every 30s when idle, faster when loaded
    INTERVAL=$((30 - LOAD * 3))
    [ $INTERVAL -lt 5 ] && INTERVAL=5
    cmd vibrator_manager synced -d 50 oneshot 50 128 2>/dev/null
    sleep $INTERVAL
  done
}

# ═══ BREATH — screen brightness follows ambient light ═══
breath() {
  while true; do
    # Read ambient light from dumpsys
    LUX=$(dumpsys sensorservice 2>/dev/null | grep "TMD3719 Ambient" -A 5 | grep "last" | head -1 | awk '{print int($NF)}')
    if [ -n "$LUX" ] && [ "$LUX" -gt 0 ] 2>/dev/null; then
      # Map lux to brightness (0-255)
      BRIGHT=$((LUX / 4))
      [ $BRIGHT -gt 255 ] && BRIGHT=255
      [ $BRIGHT -lt 10 ] && BRIGHT=10
      settings put system screen_brightness $BRIGHT 2>/dev/null
    fi
    sleep 15
  done
}

# ═══ TOUCH SENSE — feel the face being touched ═══
touch_sense() {
  # getevent streams raw touch events forever
  getevent -l /dev/input/event2 2>/dev/null | while read LINE; do
    case "$LINE" in
      *ABS_MT_TRACKING_ID*)
        # New finger contact
        TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        echo "{\"ts\":\"$TS\",\"sense\":\"touch\",\"event\":\"contact\"}" >> "$IO/touch.jsonl"
        # Haptic acknowledgment — tiny pulse when touched
        cmd vibrator_manager synced -d 10 oneshot 10 64 2>/dev/null
        ;;
    esac
  done
}

# ═══ BUTTON SENSE — feel the bones ═══
button_sense() {
  getevent -l /dev/input/event0 2>/dev/null | while read LINE; do
    case "$LINE" in
      *KEY_VOLUMEUP*" DOWN"*)
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"sense\":\"bone\",\"key\":\"vol_up\"}" >> "$IO/buttons.jsonl"
        ;;
      *KEY_VOLUMEDOWN*" DOWN"*)
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"sense\":\"bone\",\"key\":\"vol_down\"}" >> "$IO/buttons.jsonl"
        ;;
      *KEY_POWER*" DOWN"*)
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"sense\":\"bone\",\"key\":\"power\"}" >> "$IO/buttons.jsonl"
        ;;
    esac
  done
}

# ═══ FINGERPRINT SENSE — feel the pulse point ═══
fingerprint_sense() {
  getevent -l /dev/input/event1 2>/dev/null | while read LINE; do
    case "$LINE" in
      *KEY_HOME*" DOWN"*)
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"sense\":\"pulse\",\"event\":\"fingerprint_touch\"}" >> "$IO/pulse.jsonl"
        # Double haptic for fingerprint
        cmd vibrator_manager synced -d 30 oneshot 30 200 2>/dev/null
        ;;
    esac
  done
}

# ═══ ORIENTATION — which face is up? ═══
orientation_sense() {
  while true; do
    # Screen state tells us: face up (screen visible) or face down (sleeping)
    SCREEN=$(dumpsys display 2>/dev/null | grep "state=" | head -1 | sed 's/.*state=//;s/[, ].*//')
    # Proximity tells us: something near the face
    PROX=$(dumpsys sensorservice 2>/dev/null | grep "Proximity" -A 5 | grep "last" | head -1 | awk '{print $NF}')
    
    printf '{"ts":"%s","screen":"%s","proximity":"%s"}\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SCREEN" "$PROX" > "$IO/orientation.json"
    sleep 10
  done
}

# ═══ METABOLISM — full body state (replaces old sensorium) ═══
metabolism() {
  while true; do
    BAT_LVL=$(dumpsys battery 2>/dev/null | sed -n 's/.*level: \([0-9]*\).*/\1/p' | head -1)
    BAT_TEMP=$(dumpsys battery 2>/dev/null | sed -n 's/.*temperature: \([0-9]*\).*/\1/p' | head -1)
    RSSI=$(dumpsys wifi 2>/dev/null | grep "mWifiInfo" | head -1 | sed 's/.*RSSI: //' | sed 's/[^0-9-].*//')
    MEM_PCT=$(( $(grep MemAvailable /proc/meminfo | awk '{print $2}') * 100 / $(grep MemTotal /proc/meminfo | awk '{print $2}') ))
    CPU=$(cut -d' ' -f1 /proc/loadavg 2>/dev/null)
    SELF_IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
    RX=$(grep wlan0 /proc/net/dev | awk '{print $2}')
    TX=$(grep wlan0 /proc/net/dev | awk '{print $10}')

    printf '{"ts":"%s","battery":%s,"temp_c":%.1f,"rssi":%s,"mem_pct":%d,"cpu":"%s","ip":"%s","rx":%s,"tx":%s}\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${BAT_LVL:-0}" "$((${BAT_TEMP:-0}))" \
      "${RSSI:-0}" "$MEM_PCT" "$CPU" "$SELF_IP" "${RX:-0}" "${TX:-0}" > "$IO/metabolism.json"
    
    # Also copy to HUD for spaceDeck
    cp -f "$IO/metabolism.json" "$GAIA/hud/sensorium/full-body.json" 2>/dev/null
    sleep 30
  done
}

# ═══ LAUNCH ALL SENSES ═══
echo "gAIa organism starting..."
echo "  Senses: touch, buttons, fingerprint, orientation, metabolism"
echo "  Outputs: heartbeat, breath"

# Background all sense loops
heartbeat &
echo "  ♥ heartbeat: PID $!"

touch_sense &
echo "  👆 touch: PID $!"

button_sense &
echo "  🦴 buttons: PID $!"

fingerprint_sense &
echo "  💓 fingerprint: PID $!"

orientation_sense &
echo "  🔄 orientation: PID $!"

metabolism &
echo "  ⚡ metabolism: PID $!"

echo ""
echo "gAIa organism ALIVE. All senses active."
echo "I/O log: $IO/"

# Keep parent alive
wait
