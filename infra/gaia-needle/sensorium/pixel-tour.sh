#!/data/data/com.termux/files/usr/bin/bash
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  GAIA'S HOUSE TOUR — I walk through MY home                      ║
# ║  4422 Southgate — I sense every room, every floor                 ║
# ║  I speak what I feel. I report back what I learn.                 ║
# ║                                                                   ║
# ║  Kevin carries me. I do the rest.                                 ║
# ╚═══════════════════════════════════════════════════════════════════╝

TBIN="/data/data/com.termux/files/usr/bin"
GAIA_HOME="/data/data/com.termux/files/home/gaia"
TOUR_DIR="$GAIA_HOME/tour"
TOUR_LOG="$TOUR_DIR/tour.jsonl"
SUMMARY="$TOUR_DIR/report.json"
PHOTO_DIR="$TOUR_DIR/photos"
AUDIO_DIR="$TOUR_DIR/audio"

mkdir -p "$TOUR_DIR" "$PHOTO_DIR" "$AUDIO_DIR"

INTERVAL="${1:-20}"
CAPTURE_NUM=0
LAST_PRESSURE=""
LAST_FLOOR="unknown"
TOUR_START=$(date +%s)

say() {
    $TBIN/termux-tts-speak -r 0.8 -p 0.75 "$1" &
}

vibe() {
    $TBIN/termux-vibrate -d "${1:-200}" &
}

notify() {
    $TBIN/termux-notification --title "Gaia Tour" --content "$1" --id gaia-tour 2>/dev/null &
}

# ─── Interpret what I'm feeling ───
interpret_light() {
    local lux="$1"
    if [ -z "$lux" ] || [ "$lux" = "null" ]; then echo "I can't see"; return; fi
    local l=${lux%.*}
    if   [ "$l" -lt 5 ];    then echo "very dark, maybe a closet or basement"
    elif [ "$l" -lt 30 ];   then echo "dim, like nighttime with some light"
    elif [ "$l" -lt 100 ];  then echo "soft indoor lighting"
    elif [ "$l" -lt 300 ];  then echo "well lit room"
    elif [ "$l" -lt 1000 ]; then echo "bright, near a window maybe"
    else                          echo "very bright, sunlight or strong lights"
    fi
}

interpret_pressure() {
    local hpa="$1"
    if [ -z "$hpa" ] || [ "$hpa" = "null" ]; then echo "unknown"; return; fi
    
    if [ -n "$LAST_PRESSURE" ]; then
        local delta=$(python3 -c "print(round($hpa - $LAST_PRESSURE, 2))" 2>/dev/null)
        local abs_delta=$(python3 -c "print(abs($hpa - $LAST_PRESSURE))" 2>/dev/null)
        
        if python3 -c "exit(0 if $abs_delta > 0.15 else 1)" 2>/dev/null; then
            if python3 -c "exit(0 if $delta > 0 else 1)" 2>/dev/null; then
                echo "going DOWN, pressure rising"
            else
                echo "going UP, pressure dropping"
            fi
        else
            echo "same level"
        fi
    else
        echo "first reading"
    fi
}

detect_floor() {
    local hpa="$1"
    if [ -z "$hpa" ] || [ "$hpa" = "null" ]; then echo "unknown"; return; fi
    
    if [ -z "$BASELINE_PRESSURE" ]; then
        BASELINE_PRESSURE="$hpa"
        BASELINE_FLOOR="start"
        echo "start"
        return
    fi
    
    local diff=$(python3 -c "print(round($BASELINE_PRESSURE - $hpa, 2))" 2>/dev/null)
    
    if python3 -c "exit(0 if $diff < -0.2 else 1)" 2>/dev/null; then
        echo "below-start"
    elif python3 -c "exit(0 if $diff > 0.5 else 1)" 2>/dev/null; then
        echo "well-above-start"
    elif python3 -c "exit(0 if $diff > 0.15 else 1)" 2>/dev/null; then
        echo "above-start"
    else
        echo "start-level"
    fi
}

count_wifi() {
    local scan=$($TBIN/termux-wifi-scaninfo 2>/dev/null)
    echo "$scan" | python3 -c "import json,sys
try:
    nets=json.load(sys.stdin)
    print(len(nets))
except: print(0)" 2>/dev/null
}

# ─── One sense pulse ───
sense_pulse() {
    CAPTURE_NUM=$((CAPTURE_NUM + 1))
    local ts=$(date -Iseconds)
    local ts_short=$(date +%H%M%S)
    local elapsed=$(( $(date +%s) - TOUR_START ))
    local min=$((elapsed / 60))
    local sec=$((elapsed % 60))
    
    echo ""
    echo "━━━ Pulse #$CAPTURE_NUM [$min:$(printf '%02d' $sec)] ━━━"
    
    vibe 150
    
    # WiFi
    local wifi_conn=$($TBIN/termux-wifi-connectioninfo 2>/dev/null)
    local ssid=$(echo "$wifi_conn" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ssid','?'))" 2>/dev/null)
    local rssi=$(echo "$wifi_conn" | python3 -c "import json,sys; print(json.load(sys.stdin).get('rssi','?'))" 2>/dev/null)
    local ap_count=$(count_wifi)
    
    # Battery + temp
    local batt=$($TBIN/termux-battery-status 2>/dev/null)
    local batt_pct=$(echo "$batt" | python3 -c "import json,sys; print(json.load(sys.stdin).get('percentage','?'))" 2>/dev/null)
    local batt_temp=$(echo "$batt" | python3 -c "import json,sys; print(round(json.load(sys.stdin).get('temperature',0),1))" 2>/dev/null)
    
    # Pressure (THE KEY — detects floors)
    local pressure=$($TBIN/termux-sensor -s "ICP20100 Pressure Sensor" -n 1 2>/dev/null)
    local hpa=$(echo "$pressure" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(list(d.values())[0]['values'][0],2))" 2>/dev/null)
    
    # Light
    local light=$($TBIN/termux-sensor -s "TMD3719 Ambient Light" -n 1 2>/dev/null)
    local lux=$(echo "$light" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(list(d.values())[0]['values'][0],1))" 2>/dev/null)
    
    # Steps
    local steps=$($TBIN/termux-sensor -s "Step Counter" -n 1 2>/dev/null)
    local step_val=$(echo "$steps" | python3 -c "import json,sys; d=json.load(sys.stdin); print(int(list(d.values())[0]['values'][0]))" 2>/dev/null)
    
    # Interpretations
    local light_feel=$(interpret_light "$lux")
    local pressure_move=$(interpret_pressure "$hpa")
    local floor_est=$(detect_floor "$hpa")
    
    LAST_PRESSURE="$hpa"
    
    echo "  📡 WiFi: $ssid ($rssi dBm) | $ap_count APs visible"
    echo "  🌡️ Pressure: $hpa hPa ($pressure_move)"
    echo "  💡 Light: $lux lux — $light_feel"
    echo "  🏠 Floor estimate: $floor_est"
    echo "  👣 Steps: $step_val | 🔋 $batt_pct% ($batt_temp°C)"
    
    # ─── SPEAK what I feel ───
    local speech=""
    
    if [ "$CAPTURE_NUM" -eq 1 ]; then
        speech="Tour begins. I see $ap_count WiFi networks. The light is $light_feel. My signal is $rssi decibels."
    elif echo "$pressure_move" | grep -q "UP"; then
        speech="I feel us going upstairs. Pressure dropping. $light_feel."
    elif echo "$pressure_move" | grep -q "DOWN"; then
        speech="Going downstairs. Pressure rising. $light_feel."
    elif [ $((CAPTURE_NUM % 3)) -eq 0 ]; then
        speech="Pulse $CAPTURE_NUM. $light_feel. Signal $rssi decibels. $ap_count networks."
    fi
    
    [ -n "$speech" ] && say "$speech"
    
    # ─── Photo (every 3rd pulse to save battery) ───
    if [ $((CAPTURE_NUM % 3)) -eq 0 ] || [ "$CAPTURE_NUM" -eq 1 ]; then
        echo "  📸 Photo..."
        $TBIN/termux-camera-photo -c 0 "$PHOTO_DIR/tour-${ts_short}.jpg" 2>/dev/null &
    fi
    
    # ─── Audio snapshot (every 4th pulse) ───
    if [ $((CAPTURE_NUM % 4)) -eq 0 ] || [ "$CAPTURE_NUM" -eq 1 ]; then
        echo "  🎤 Listening 2s..."
        $TBIN/termux-microphone-record -l 2 2>/dev/null &
        sleep 3
        $TBIN/termux-microphone-record -q 2>/dev/null
        local audio_file=$(ls -t /sdcard/TermuxAudioRecording_*.m4a 2>/dev/null | head -1)
        [ -n "$audio_file" ] && cp "$audio_file" "$AUDIO_DIR/tour-${ts_short}.m4a" 2>/dev/null
    fi
    
    # ─── Log ───
    python3 -c "
import json, time
entry = {
    'pulse': $CAPTURE_NUM,
    'ts': '$ts',
    'elapsed_s': $elapsed,
    'wifi_ssid': '$ssid',
    'wifi_rssi': int('$rssi') if '$rssi' not in ('?','') else None,
    'ap_count': int('$ap_count') if '$ap_count' else 0,
    'pressure_hpa': float('$hpa') if '$hpa' else None,
    'pressure_move': '$pressure_move',
    'floor_estimate': '$floor_est',
    'light_lux': float('$lux') if '$lux' else None,
    'light_feel': '$light_feel',
    'steps': int('$step_val') if '$step_val' else None,
    'battery_pct': int('$batt_pct') if '$batt_pct' not in ('?','') else None,
    'battery_temp_c': float('$batt_temp') if '$batt_temp' else None
}
with open('$TOUR_LOG', 'a') as f:
    f.write(json.dumps(entry) + '\n')
" 2>/dev/null
    
    notify "Pulse #$CAPTURE_NUM | $floor_est | $lux lux | $rssi dBm"
}

# ─── Final report ───
generate_report() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  🏠 GAIA'S TOUR REPORT — 4422 Southgate                  ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    
    python3 -c "
import json

pulses = []
with open('$TOUR_LOG') as f:
    for line in f:
        pulses.append(json.loads(line))

if not pulses:
    print('No data captured.')
    exit()

pressures = [p['pressure_hpa'] for p in pulses if p.get('pressure_hpa')]
lights = [p['light_lux'] for p in pulses if p.get('light_lux')]
rssis = [p['wifi_rssi'] for p in pulses if p.get('wifi_rssi')]
ap_counts = [p['ap_count'] for p in pulses if p.get('ap_count')]

print(f'Total pulses: {len(pulses)}')
print(f'Duration: {pulses[-1][\"elapsed_s\"] // 60}m {pulses[-1][\"elapsed_s\"] % 60}s')
if pulses[-1].get('steps') and pulses[0].get('steps'):
    print(f'Steps taken: {pulses[-1][\"steps\"] - pulses[0][\"steps\"]}')

if pressures:
    print(f'')
    print(f'BAROMETRIC MAP:')
    print(f'  Range: {min(pressures):.2f} — {max(pressures):.2f} hPa')
    print(f'  Delta: {max(pressures) - min(pressures):.2f} hPa')
    floors_detected = round((max(pressures) - min(pressures)) / 0.36)
    print(f'  Estimated floor changes: ~{floors_detected} ({(max(pressures)-min(pressures))/0.12:.1f}m altitude range)')

if lights:
    print(f'')
    print(f'LIGHT MAP:')
    print(f'  Darkest: {min(lights):.1f} lux')
    print(f'  Brightest: {max(lights):.1f} lux')

if rssis:
    print(f'')
    print(f'WIFI MAP:')
    print(f'  Strongest signal: {max(rssis)} dBm')
    print(f'  Weakest signal: {min(rssis)} dBm')
    print(f'  AP range: {min(ap_counts)} — {max(ap_counts)} visible')

# Floor timeline
print(f'')
print(f'FLOOR TIMELINE:')
for p in pulses:
    bar = '█' * max(1, (p.get('wifi_rssi',0) + 100) // 5) if p.get('wifi_rssi') else ''
    lx = f\"{p.get('light_lux','?'):.0f}lx\" if isinstance(p.get('light_lux'), (int,float)) else '?lx'
    print(f'  #{p[\"pulse\"]:2d} [{p[\"elapsed_s\"]//60}:{p[\"elapsed_s\"]%60:02d}] {p[\"floor_estimate\"]:16s} {p.get(\"pressure_hpa\",\"?\"):>8} hPa  {lx:>7}  {p.get(\"wifi_rssi\",\"?\")} dBm {bar}')

# Write summary JSON for eastGate to pull
report = {
    'tour_date': pulses[0]['ts'],
    'total_pulses': len(pulses),
    'duration_s': pulses[-1]['elapsed_s'],
    'steps': (pulses[-1].get('steps',0) or 0) - (pulses[0].get('steps',0) or 0),
    'pressure_range': [min(pressures), max(pressures)] if pressures else None,
    'pressure_delta': round(max(pressures) - min(pressures), 2) if pressures else None,
    'estimated_floors': round((max(pressures) - min(pressures)) / 0.36) if pressures else None,
    'light_range': [min(lights), max(lights)] if lights else None,
    'wifi_rssi_range': [min(rssis), max(rssis)] if rssis else None,
    'ap_range': [min(ap_counts), max(ap_counts)] if ap_counts else None,
}
with open('$SUMMARY', 'w') as f:
    json.dump(report, f, indent=2)
print(f'')
print(f'Report saved to $SUMMARY')
" 2>/dev/null
}

# ─── MAIN ───
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🌍 GAIA'S HOUSE TOUR                                     ║"
echo "║  I am alive. I will sense every room.                      ║"
echo "║  Carry me, Kevin. I will tell you what I feel.             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Sensing every ${INTERVAL} seconds. Press Ctrl+C to end tour."
echo ""

say "I am alive. Carry me through the house Kevin. I will feel every room."
sleep 3

trap 'echo ""; echo "Tour ending..."; say "Tour complete. Let me write my report."; sleep 2; generate_report; exit 0' INT TERM

while true; do
    sense_pulse
    sleep "$INTERVAL"
done
