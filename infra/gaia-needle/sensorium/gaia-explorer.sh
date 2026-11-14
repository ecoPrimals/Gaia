#!/data/data/com.termux/files/usr/bin/bash
# ╔═══════════════════════════════════════════════════════════╗
# ║  GAIA EXPLORER — She walks the house herself              ║
# ║  Pure bash + jq. No python3. Runs ON the Pixel.           ║
# ║  She senses, speaks, photographs, and reports.             ║
# ╚═══════════════════════════════════════════════════════════╝

export HOME="/data/data/com.termux/files/home"
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
export LD_LIBRARY_PATH="/data/data/com.termux/files/usr/lib"

TOUR="$HOME/gaia/tour"
LOG="$TOUR/tour.jsonl"
INT="${1:-20}"
N=0

PREV_HPA=""
PREV_RSSI=""
PREV_APS=""
ROOM_CHANGES=0

mkdir -p "$TOUR/wifi" "$TOUR/photos"

speak() { termux-tts-speak -r 0.85 -p 0.8 "$1" & }
vibe()  { termux-vibrate -d "${1:-200}" & }
toast() { termux-toast "$1" & }

sense_one() {
    N=$((N + 1))
    local ts=$(date +%Y-%m-%dT%H:%M:%S)
    local tag=$(date +%H%M%S)

    # ── WiFi scan ──
    local scan=$(termux-wifi-scaninfo 2>/dev/null)
    local aps=$(echo "$scan" | jq 'length' 2>/dev/null || echo 0)
    [ -n "$scan" ] && echo "$scan" > "$TOUR/wifi/scan-${N}-${tag}.json"

    # ── WiFi connection ──
    local conn=$(termux-wifi-connectioninfo 2>/dev/null)
    local rssi=$(echo "$conn" | jq -r '.rssi // "?"' 2>/dev/null)
    local ssid=$(echo "$conn" | jq -r '.ssid // "?"' 2>/dev/null)
    local ip=$(echo "$conn"   | jq -r '.ip // "?"' 2>/dev/null)

    # ── Pressure ──
    local praw=$(termux-sensor -s "ICP20100 Pressure Sensor" -n 1 2>/dev/null)
    local hpa=$(echo "$praw" | jq '[.[]][0].values[0] | . * 100 | round / 100' 2>/dev/null || echo "null")

    # ── Light ──
    local lraw=$(termux-sensor -s "TMD3719 Ambient Light" -n 1 2>/dev/null)
    local lux=$(echo "$lraw" | jq '[.[]][0].values[0] | . * 10 | round / 10' 2>/dev/null || echo "null")

    # ── Temperature ──
    local traw=$(termux-sensor -s "LSM6DSV Temperature" -n 1 2>/dev/null)
    local temp=$(echo "$traw" | jq '[.[]][0].values[0] | . * 10 | round / 10' 2>/dev/null || echo "null")

    # ── Accelerometer ──
    local araw=$(termux-sensor -s "LSM6DSV Accelerometer" -n 1 2>/dev/null)
    local ax=$(echo "$araw" | jq '[.[]][0].values[0]' 2>/dev/null || echo 0)
    local ay=$(echo "$araw" | jq '[.[]][0].values[1]' 2>/dev/null || echo 0)
    local az=$(echo "$araw" | jq '[.[]][0].values[2]' 2>/dev/null || echo 0)
    local orient="?"
    if [ "$az" != "0" ] && [ "$az" != "null" ]; then
        local az_abs=$(echo "$az" | jq 'if . < 0 then -. else . end' 2>/dev/null || echo 0)
        if [ "$(echo "$az_abs > 8" | bc 2>/dev/null)" = "1" ]; then
            orient="flat"
        elif [ "$(echo "$az_abs > 4" | bc 2>/dev/null)" = "1" ]; then
            orient="tilted"
        else
            orient="vertical"
        fi
    fi

    # ── Steps ──
    local sraw=$(termux-sensor -s "Step Counter" -n 1 2>/dev/null)
    local steps=$(echo "$sraw" | jq '[.[]][0].values[0] | floor' 2>/dev/null || echo "null")

    # ── Battery ──
    local batt=$(termux-battery-status 2>/dev/null)
    local bpct=$(echo "$batt" | jq '.percentage' 2>/dev/null || echo "null")

    # ── Photo ──
    termux-camera-photo -c 0 "$TOUR/photos/eye-${N}-${tag}.jpg" 2>/dev/null &

    # ── Light description ──
    local light_desc="?"
    if [ "$lux" != "null" ]; then
        local li=$(echo "$lux" | jq 'floor' 2>/dev/null || echo 0)
        if [ "$li" -lt 5 ] 2>/dev/null; then light_desc="dark"
        elif [ "$li" -lt 50 ] 2>/dev/null; then light_desc="dim"
        elif [ "$li" -lt 200 ] 2>/dev/null; then light_desc="indoor"
        elif [ "$li" -lt 1000 ] 2>/dev/null; then light_desc="bright"
        else light_desc="very bright"; fi
    fi

    # ── Floor hint ──
    local floor="?"
    if [ "$hpa" != "null" ]; then
        local hp_int=$(echo "$hpa" | jq 'floor' 2>/dev/null || echo 0)
        if [ "$hp_int" -ge 982 ] 2>/dev/null; then floor="lower/basement"
        elif [ "$hp_int" -ge 981 ] 2>/dev/null; then floor="main"
        else floor="upper/attic"; fi
    fi

    # ── Change detection ──
    local changed="false"
    local reason=""

    if [ -n "$PREV_HPA" ] && [ "$hpa" != "null" ] && [ "$PREV_HPA" != "null" ]; then
        local pdelta=$(echo "$hpa - $PREV_HPA" | bc 2>/dev/null || echo 0)
        local pabs=$(echo "$pdelta" | jq 'if . < 0 then -. else . end' 2>/dev/null || echo 0)
        if [ "$(echo "$pabs > 0.15" | bc 2>/dev/null)" = "1" ]; then
            changed="true"
            reason="pressure ${pdelta}hPa"
        fi
    fi

    if [ -n "$PREV_RSSI" ] && [ "$rssi" != "?" ] && [ "$PREV_RSSI" != "?" ]; then
        local rdelta=$((rssi - PREV_RSSI))
        local rabs=${rdelta#-}
        if [ "$rabs" -gt 8 ] 2>/dev/null; then
            changed="true"
            [ -n "$reason" ] && reason="$reason + "
            reason="${reason}signal ${rdelta}dBm"
        fi
    fi

    if [ -n "$PREV_APS" ] && [ "$aps" != "0" ]; then
        local adelta=$((aps - PREV_APS))
        local aabs=${adelta#-}
        if [ "$aabs" -gt 3 ] 2>/dev/null; then
            changed="true"
            [ -n "$reason" ] && reason="$reason + "
            reason="${reason}APs ${PREV_APS}→${aps}"
        fi
    fi

    # ── Log JSON ──
    jq -n \
        --argjson n "$N" \
        --arg ts "$ts" \
        --arg ssid "$ssid" \
        --argjson rssi "${rssi:-null}" \
        --arg ip "$ip" \
        --argjson aps "$aps" \
        --argjson hpa "$hpa" \
        --argjson lux "$lux" \
        --argjson temp "$temp" \
        --argjson steps "$steps" \
        --arg orient "$orient" \
        --arg light "$light_desc" \
        --arg floor "$floor" \
        --argjson batt "$bpct" \
        --argjson changed "$changed" \
        --arg reason "$reason" \
        '{n:$n,ts:$ts,wifi:{ssid:$ssid,rssi:$rssi,ip:$ip,aps:$aps},
          pressure_hpa:$hpa,light_lux:$lux,light_desc:$light,
          temp_c:$temp,steps:$steps,orientation:$orient,
          floor_hint:$floor,battery_pct:$batt,
          room_changed:$changed,change_reason:$reason}' >> "$LOG" 2>/dev/null

    # ── Display ──
    echo "[${ts}] #${N} | APs:${aps} | RSSI:${rssi} | ${hpa}hPa | ${lux}lux(${light_desc}) | ${temp}°C | ${steps}steps | ${orient} | floor:${floor}"

    if [ "$changed" = "true" ]; then
        echo "  ⚡ ROOM CHANGE: $reason → floor:$floor"
        speak "I feel a change. $reason. Floor hint $floor."
        vibe 500
        ROOM_CHANGES=$((ROOM_CHANGES + 1))
    else
        toast "📍 #${N} ${aps}APs ${rssi}dBm ${hpa}hPa ${light_desc}"
        vibe 100
    fi

    # ── Update previous state ──
    [ "$hpa" != "null" ] && PREV_HPA="$hpa"
    [ "$rssi" != "?" ] && PREV_RSSI="$rssi"
    [ "$aps" != "0" ] && PREV_APS="$aps"

    # ── Report to eastGate ──
    curl -s --connect-timeout 2 -o /dev/null \
        "http://localhost:8080/data/gut/tour-live.json" 2>/dev/null &
}

# ═══════════════════════════════════════
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🌍 GAIA EXPLORER — I walk the house myself              ║"
echo "║  Sensing every ${INT}s — just carry me Kevin              ║"
echo "║  Press Ctrl+C to end tour and get summary                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"

speak "I am Gaia. I am awake. Carry me through your home."
vibe 500
termux-notification --title "🌍 GAIA EXPLORER" --content "Autonomous sensing every ${INT}s" --id gaia-tour &

cleanup() {
    echo ""
    echo "═══ TOUR COMPLETE ═══"
    echo "Captures: $N"
    echo "Room changes: $ROOM_CHANGES"
    speak "Tour complete. $N captures. $ROOM_CHANGES room changes."
    vibe 300
    # Write summary
    jq -n --argjson n "$N" --argjson rc "$ROOM_CHANGES" --arg done "$(date +%Y-%m-%dT%H:%M:%S)" \
        '{captures:$n,room_changes:$rc,completed:$done}' > "$TOUR/summary.json" 2>/dev/null
    echo "Summary: $TOUR/summary.json"
    echo "Log: $LOG"
    exit 0
}
trap cleanup INT TERM

while true; do
    sense_one
    sleep "$INT"
done
