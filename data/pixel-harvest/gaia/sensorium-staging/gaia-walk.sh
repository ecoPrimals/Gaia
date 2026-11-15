#!/data/data/com.termux/files/usr/bin/bash
export HOME="/data/data/com.termux/files/home"
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
export LD_LIBRARY_PATH="/data/data/com.termux/files/usr/lib"

TOUR="$HOME/gaia/tour"
LOG="$TOUR/tour.jsonl"
N=0
INT="${1:-20}"

mkdir -p "$TOUR/wifi" "$TOUR/photos"

termux-toast "🌍 GAIA EXPLORER ACTIVE" &
termux-vibrate -d 500 &

while true; do
    N=$((N + 1))
    TS=$(date +%Y-%m-%dT%H:%M:%S)
    TAG=$(date +%H%M%S)
    
    # WiFi (the key data for localization)
    SCAN=$(termux-wifi-scaninfo 2>/dev/null)
    echo "$SCAN" > "$TOUR/wifi/scan-${N}-${TAG}.json"
    APS=$(echo "$SCAN" | python3 -c "import json,sys;print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)
    
    CONN=$(termux-wifi-connectioninfo 2>/dev/null)
    RSSI=$(echo "$CONN" | python3 -c "import json,sys;print(json.load(sys.stdin).get('rssi','?'))" 2>/dev/null)
    
    # Pressure (floor detection)
    HPA=$(termux-sensor -s "ICP20100 Pressure Sensor" -n 1 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(round(list(d.values())[0]['values'][0],2))" 2>/dev/null || echo "?")
    
    # Light
    LUX=$(termux-sensor -s "TMD3719 Ambient Light" -n 1 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(round(list(d.values())[0]['values'][0],1))" 2>/dev/null || echo "?")
    
    # Steps
    STEPS=$(termux-sensor -s "Step Counter" -n 1 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(int(list(d.values())[0]['values'][0]))" 2>/dev/null || echo "?")
    
    # Photo (background)
    termux-camera-photo -c 0 "$TOUR/photos/eye-${N}-${TAG}.jpg" 2>/dev/null &
    
    # Speak (background - non-blocking!)
    termux-tts-speak -r 0.85 -p 0.8 "Capture ${N}. ${APS} signals. Pressure ${HPA}." &
    termux-vibrate -d 150 &
    termux-toast "📍 #${N} APs:${APS} RSSI:${RSSI} ${HPA}hPa ${LUX}lux" &
    
    # Log
    echo "{\"n\":$N,\"ts\":\"$TS\",\"aps\":$APS,\"rssi\":\"$RSSI\",\"hpa\":\"$HPA\",\"lux\":\"$LUX\",\"steps\":\"$STEPS\"}" >> "$LOG"
    
    # Report to eastGate
    curl -s --connect-timeout 2 -o /dev/null "http://192.168.4.244:8080/data/gut/tour-live.json" 2>/dev/null &
    
    echo "[$TS] #$N | APs:$APS | RSSI:$RSSI | ${HPA}hPa | ${LUX}lux | steps:$STEPS"
    
    sleep "$INT"
done
