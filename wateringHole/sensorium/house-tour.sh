#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  HOUSE TOUR — Kevin walks Gaia through the crib                   ║
# ║  4422 Southgate — Basement, Main, Attic                           ║
# ║                                                                   ║
# ║  Every room: WiFi fingerprint + photo + audio + full sensors      ║
# ║  Like FaceTiming a realtor — showing the whole house              ║
# ╚═══════════════════════════════════════════════════════════════════╝

NEEDLE="${NEEDLE_DEVICE:-192.168.9.217:5555}"
TBIN="/data/data/com.termux/files/usr/bin"
GUT="/opt/Gaia/data/gut"
TOUR_DIR="$GUT/house-tour"
TOUR_LOG="$TOUR_DIR/tour.jsonl"
WIFI_CAL="/data/local/tmp/sensorium/localize.sh"
SOUNDS_DIR="/data/data/com.termux/files/home/gaia/sounds"

mkdir -p "$TOUR_DIR/photos" "$TOUR_DIR/audio" "$TOUR_DIR/wifi"

tapi() {
    adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/$*\"'" 2>/dev/null
}

speak() {
    tapi "termux-tts-speak -r 0.85 -p 0.8 \"$1\"" &
}

vibrate() {
    tapi "termux-vibrate -d ${1:-200}" &
}

# ─── Capture everything about a room ───
capture_room() {
    local room="$1"
    local floor="$2"
    local ts=$(date -Iseconds)
    local ts_short=$(date +%H%M%S)
    
    echo ""
    echo "╔═══════════════════════════════════════╗"
    echo "║  📍 ROOM: $room ($floor floor)"
    echo "╚═══════════════════════════════════════╝"
    
    # Announce
    speak "Entering $room on $floor floor"
    vibrate 300
    
    # 1. WiFi fingerprint
    echo "  📡 WiFi fingerprint..."
    local wifi=$(tapi "termux-wifi-scaninfo")
    echo "$wifi" > "$TOUR_DIR/wifi/${room}-${ts_short}.json"
    local ap_count=$(echo "$wifi" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null)
    echo "     $ap_count APs visible"
    
    # 2. WiFi connection info
    local conn=$(tapi "termux-wifi-connectioninfo")
    local rssi=$(echo "$conn" | python3 -c "import json,sys; print(json.load(sys.stdin).get('rssi','?'))" 2>/dev/null)
    echo "     Home WiFi RSSI: $rssi dBm"
    
    # 3. Photo (rear camera)
    echo "  📸 Taking photo..."
    tapi "termux-camera-photo -c 0 /sdcard/gaia/tour-${room}-${ts_short}.jpg" &
    
    # 4. Key sensors
    echo "  🌡️ Sensors..."
    local batt=$(tapi "termux-battery-status")
    local batt_pct=$(echo "$batt" | python3 -c "import json,sys; print(json.load(sys.stdin).get('percentage','?'))" 2>/dev/null)
    local batt_temp=$(echo "$batt" | python3 -c "import json,sys; print(round(json.load(sys.stdin).get('temperature',0),1))" 2>/dev/null)
    
    # Barometric pressure (changes between floors!)
    local pressure=$(adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/termux-sensor -s \\\"ICP20100 Pressure Sensor\\\" -n 1\"'" 2>/dev/null)
    local hpa=$(echo "$pressure" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(list(d.values())[0]['values'][0],2))" 2>/dev/null)
    
    # Light level
    local light=$(adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/termux-sensor -s \\\"TMD3719 Ambient Light\\\" -n 1\"'" 2>/dev/null)
    local lux=$(echo "$light" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(list(d.values())[0]['values'][0],1))" 2>/dev/null)
    
    # Accelerometer (orientation/motion)
    local accel=$(adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/termux-sensor -s \\\"LSM6DSV Accelerometer\\\" -n 1\"'" 2>/dev/null)
    
    # Step counter
    local steps=$(adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/termux-sensor -s \\\"Step Counter\\\" -n 1\"'" 2>/dev/null)
    local step_count=$(echo "$steps" | python3 -c "import json,sys; d=json.load(sys.stdin); print(int(list(d.values())[0]['values'][0]))" 2>/dev/null)
    
    echo "     Pressure: ${hpa} hPa | Light: ${lux} lux | Steps: ${step_count}"
    echo "     Battery: ${batt_pct}% at ${batt_temp}°C"
    
    # 5. Audio snapshot (1 second)
    echo "  🎤 Listening..."
    tapi "termux-microphone-record -l 2" &
    sleep 3
    tapi "termux-microphone-record -q"
    # Pull the recording
    local audio_file=$(adb -s "$NEEDLE" shell "ls -t /sdcard/TermuxAudioRecording_*.m4a 2>/dev/null | head -1" | tr -d '\r')
    if [ -n "$audio_file" ]; then
        adb -s "$NEEDLE" pull "$audio_file" "$TOUR_DIR/audio/${room}-${ts_short}.m4a" 2>/dev/null
    fi
    
    # 6. Log entry
    python3 -c "
import json
entry = {
    'ts': '$ts',
    'room': '$room',
    'floor': '$floor',
    'wifi_rssi': $rssi if '$rssi' != '?' else None,
    'ap_count': $ap_count if '$ap_count' != '' else 0,
    'pressure_hpa': $hpa if '$hpa' != '' else None,
    'light_lux': $lux if '$lux' != '' else None,
    'battery_pct': $batt_pct if '$batt_pct' != '?' else None,
    'steps': $step_count if '$step_count' != '' else None,
}
with open('$TOUR_LOG', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print(json.dumps(entry, indent=2))
" 2>/dev/null
    
    echo ""
    echo "  ✅ $room captured!"
    speak "$room captured"
}

# ─── Tour modes ───
start_tour() {
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  🏠 HOUSE TOUR — 4422 Southgate                          ║"
    echo "║  Kevin carries Gaia room by room                          ║"
    echo "║  WiFi + Photo + Audio + Pressure + Light + Steps          ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Floors: Basement → Main → Attic"
    echo ""
    echo "Commands:"
    echo "  Type a room name to capture (e.g., 'kitchen', 'bedroom')"
    echo "  Type 'summary' to see tour progress"
    echo "  Type 'done' to end tour"
    echo ""
    
    # Stop Snake Jazz for the tour
    tapi "termux-media-player stop"
    
    speak "House tour beginning. Carry me through every room Kevin."
    vibrate 500
    
    while true; do
        echo -n "📍 Room name (floor: b=basement, m=main, a=attic): "
        read -r input
        
        [ "$input" = "done" ] && break
        [ "$input" = "summary" ] && { show_summary; continue; }
        [ -z "$input" ] && continue
        
        # Parse room and floor
        room=$(echo "$input" | awk '{print $1}')
        floor=$(echo "$input" | awk '{print $2}')
        [ -z "$floor" ] && floor="main"
        
        case "$floor" in
            b|basement) floor="basement" ;;
            m|main)     floor="main" ;;
            a|attic)    floor="attic" ;;
        esac
        
        capture_room "$room" "$floor"
    done
    
    echo ""
    echo "🏠 Tour complete!"
    show_summary
    speak "Tour complete. I know this house now."
}

# ─── Quick capture (non-interactive) ───
quick_capture() {
    local room="$1"
    local floor="${2:-main}"
    capture_room "$room" "$floor"
}

# ─── Auto tour (timed captures) ───
auto_tour() {
    local interval="${1:-30}"
    local count=0
    echo "🔄 Auto-tour: capturing every ${interval}s"
    echo "   Kevin, just walk! I'll capture automatically."
    speak "Auto tour. Just walk Kevin. I will sense every room."
    
    while true; do
        count=$((count + 1))
        capture_room "auto-${count}" "unknown"
        sleep "$interval"
    done
}

show_summary() {
    echo ""
    echo "═══ TOUR SUMMARY ═══"
    if [ ! -f "$TOUR_LOG" ]; then
        echo "No rooms captured yet."
        return
    fi
    python3 -c "
import json
rooms = []
with open('$TOUR_LOG') as f:
    for line in f:
        rooms.append(json.loads(line))

floors = {}
for r in rooms:
    fl = r['floor']
    if fl not in floors:
        floors[fl] = []
    floors[fl].append(r)

print(f'Total rooms: {len(rooms)}')
for fl in ['basement', 'main', 'attic', 'unknown']:
    if fl in floors:
        print(f'\n{fl.upper()} FLOOR ({len(floors[fl])} rooms):')
        for r in floors[fl]:
            rssi = r.get('wifi_rssi', '?')
            lux = r.get('light_lux', '?')
            hpa = r.get('pressure_hpa', '?')
            print(f'  📍 {r[\"room\"]:20s} WiFi:{rssi} dBm  Light:{lux} lux  Pressure:{hpa} hPa')
" 2>/dev/null
}

case "${1:-}" in
    start|tour)       start_tour ;;
    room|capture)     quick_capture "$2" "$3" ;;
    auto)             auto_tour "${2:-30}" ;;
    summary)          show_summary ;;
    *)
        echo "house-tour.sh — Walk Gaia through the crib"
        echo ""
        echo "  start          Interactive tour (Kevin types room names)"
        echo "  auto [SEC]     Auto-capture every N seconds (just walk!)"
        echo "  room NAME [FLOOR]  Quick single-room capture"
        echo "  summary        Show tour progress"
        ;;
esac
