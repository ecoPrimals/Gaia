#!/bin/bash
# seti-position.sh — WiFi-based position estimation
# Like SETI@home used GPS to locate radio receivers,
# we use WiFi RSSI to locate the Pixel on the property.
#
# Known AP positions (on the property map, 0-100% coordinates):
#   Router (House 1):     x=47, y=50  — Aperture Science, GAIA, Black Mesa
#   Omada AP (House 1):   x=24, y=40  — ApertureScience 5GHz
#   Flint (House 2):      x=22, y=34  — KinderLab, GAIA
#   eero #1 (House 1):    x=44, y=45  — near sporeGate
#   eero #2 (satellite):  x=35, y=40  — mesh, middle area

OUT="/opt/Gaia/data/seti-position.json"

# Get Pixel's current WiFi connection info
WIFI_INFO=$(adb -s 192.168.4.156:5555 shell "dumpsys wifi | grep -E 'mWifiInfo|SSID|BSSID|RSSI|mFrequency'" 2>/dev/null | head -5)
CONNECTED_BSSID=$(echo "$WIFI_INFO" | grep -oP 'BSSID: \K[0-9a-f:]+' | head -1)
CONNECTED_RSSI=$(echo "$WIFI_INFO" | grep -oP 'RSSI: \K-?[0-9]+' | head -1)
CONNECTED_SSID=$(echo "$WIFI_INFO" | grep -oP 'SSID: \K[^,]+' | head -1 | tr -d '"')
CONNECTED_FREQ=$(echo "$WIFI_INFO" | grep -oP 'Frequency: \K[0-9]+' | head -1)

# Get scan results for triangulation
SCAN=$(adb -s 192.168.4.156:5555 shell "cmd wifi list-scan-results" 2>/dev/null | tail -n +2)

# Known AP positions on property map (percent coordinates)
# Format: BSSID_prefix → x,y,name
declare -A AP_POS
AP_POS["be:a2:c1"]="47,50,Router_ApertureScience"
AP_POS["82:c9:70"]="47,50,Router_GAIA"
AP_POS["22:2f:9f"]="47,50,Router_BlackMesa"
AP_POS["b6:c3:31"]="24,40,Omada_5GHz"
AP_POS["ae:44:09"]="24,40,Omada_2.4GHz"
AP_POS["62:3c:cb"]="22,34,Flint_KinderLab_2.4"
AP_POS["a2:7b:08"]="22,34,Flint_KinderLab_5"
AP_POS["ce:ef:ef"]="22,34,Flint_GAIA"
AP_POS["c8:e3:06:c6:77:a"]="44,45,eero_Gateway"
AP_POS["78:76:89:96:e5:8"]="38,42,eero_Satellite"

# Determine position: which house is the Pixel in?
HOUSE="unknown"
BSSID_LC=$(echo "$CONNECTED_BSSID" | tr '[:upper:]' '[:lower:]')
case "$BSSID_LC" in
    be:a2:c1*|82:c9:70*|22:2f:9f*|c8:e3:06*)
        HOUSE="house1" ;;
    b6:c3:31*|ae:44:09*)
        HOUSE="house1_omada" ;;
    62:3c:cb*|a2:7b:08*|ce:ef:ef*)
        HOUSE="house2" ;;
    *)
        HOUSE="unknown" ;;
esac

# Weighted triangulation from scan results
TOTAL_W=0
SUM_X=0
SUM_Y=0
BEACON_JSON=""

while read -r bssid freq rssi age ssid rest; do
    [ -z "$bssid" ] && continue
    bssid_lc=$(echo "$bssid" | tr '[:upper:]' '[:lower:]')
    prefix6="${bssid_lc:0:8}"
    prefix17="${bssid_lc:0:17}"
    
    pos=""
    for key in "${!AP_POS[@]}"; do
        if [[ "$bssid_lc" == "$key"* ]]; then
            pos="${AP_POS[$key]}"
            break
        fi
    done
    
    [ -z "$pos" ] && continue
    
    IFS=',' read -r ax ay aname <<< "$pos"
    
    # Weight = inverse of distance (stronger signal = closer = more weight)
    w=$(python3 -c "import math; print(10**(($rssi + 30)/20))" 2>/dev/null)
    [ -z "$w" ] && continue
    
    SUM_X=$(python3 -c "print($SUM_X + $ax * $w)")
    SUM_Y=$(python3 -c "print($SUM_Y + $ay * $w)")
    TOTAL_W=$(python3 -c "print($TOTAL_W + $w)")
    
    [ -n "$BEACON_JSON" ] && BEACON_JSON="$BEACON_JSON,"
    BEACON_JSON="$BEACON_JSON{\"bssid\":\"$bssid\",\"ssid\":\"$ssid\",\"rssi\":$rssi,\"freq\":$freq,\"ap_x\":$ax,\"ap_y\":$ay,\"name\":\"$aname\"}"
done <<< "$SCAN"

# Calculate estimated position
if python3 -c "exit(0 if $TOTAL_W > 0 else 1)" 2>/dev/null; then
    EST_X=$(python3 -c "print(round($SUM_X / $TOTAL_W, 1))")
    EST_Y=$(python3 -c "print(round($SUM_Y / $TOTAL_W, 1))")
else
    EST_X=35
    EST_Y=37
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

cat > "$OUT" << EOF
{
  "timestamp": "$NOW",
  "pixel": {
    "connected_bssid": "$CONNECTED_BSSID",
    "connected_ssid": "$CONNECTED_SSID",
    "connected_rssi": ${CONNECTED_RSSI:--127},
    "connected_freq": ${CONNECTED_FREQ:-0},
    "house": "$HOUSE",
    "estimated_x": $EST_X,
    "estimated_y": $EST_Y,
    "confidence": "$(python3 -c "print('high' if $TOTAL_W > 1 else 'low')" 2>/dev/null)"
  },
  "triangulation": {
    "beacons_used": [$BEACON_JSON],
    "total_weight": $TOTAL_W,
    "method": "rssi_weighted_centroid"
  }
}
EOF

echo "SETI position: House=$HOUSE x=$EST_X y=$EST_Y (via $CONNECTED_SSID @ ${CONNECTED_RSSI}dBm)"
