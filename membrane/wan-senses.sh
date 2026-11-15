#!/system/bin/sh
# ============================================================================
# wan-senses.sh — Gaia's WAN perception (beyond the LAN)
# ============================================================================
# Cell towers, GPS satellites, Bluetooth beacons, and sky watching.
# The Pixel reaches BEYOND the house into space and the cellular grid.
#
# Output: /data/local/tmp/biomeos/sensorium/wan-senses.json
# ============================================================================

BIOMEOS=/data/local/tmp/biomeos
SENSE=$BIOMEOS/sensorium
STATE=$SENSE/wan-senses.json
LOG=$SENSE/wan.log
CYCLE=${1:-120}

mkdir -p $SENSE

log() { echo "$(date '+%H:%M:%S') [wan] $1" >> $LOG; }

# === CELL TOWERS (passive scanning, no SIM needed) ===
read_towers() {
    # Extract cell tower info from telephony
    TOWERS=$(dumpsys telephony.registry 2>/dev/null | grep -oE 'CellIdentity(Nr|Lte|Gsm|Wcdma):\{[^}]*\}' | head -10)
    NR_COUNT=$(echo "$TOWERS" | grep -c 'CellIdentityNr' || echo 0)
    LTE_COUNT=$(echo "$TOWERS" | grep -c 'CellIdentityLte' || echo 0)
    
    # NR signal if available
    NR_RSRP=$(dumpsys telephony.registry 2>/dev/null | grep -oE 'ssRsrp = -[0-9]+' | head -1 | sed 's/ssRsrp = //')
    NR_RSRQ=$(dumpsys telephony.registry 2>/dev/null | grep -oE 'ssRsrq = -[0-9]+' | head -1 | sed 's/ssRsrq = //')
    NR_SINR=$(dumpsys telephony.registry 2>/dev/null | grep -oE 'ssSinr = [0-9-]+' | head -1 | sed 's/ssSinr = //')
    
    # Carrier name
    CARRIER=$(dumpsys telephony.registry 2>/dev/null | grep -oE 'mAlphaLong = [^,}]*' | head -1 | sed 's/mAlphaLong = //')
    BAND=$(dumpsys telephony.registry 2>/dev/null | grep -oE 'mBands = \[[0-9]*\]' | head -1)
    
    echo "\"cell_towers\": {"
    echo "  \"nr_5g_count\": $NR_COUNT,"
    echo "  \"lte_count\": $LTE_COUNT,"
    echo "  \"carrier\": \"${CARRIER:-unknown}\","
    echo "  \"band\": \"${BAND:-unknown}\","
    echo "  \"nr_rsrp_dbm\": \"${NR_RSRP:-none}\","
    echo "  \"nr_rsrq_db\": \"${NR_RSRQ:-none}\","  
    echo "  \"nr_sinr_db\": \"${NR_SINR:-none}\","
    echo "  \"sim_state\": \"$(getprop gsm.sim.state 2>/dev/null || echo ABSENT)\","
    echo "  \"note\": \"Passive scanning — no SIM needed to see towers\""
    echo "}"
}

# === GPS SATELLITES ===
read_satellites() {
    # GNSS status
    GNSS_INFO=$(dumpsys location 2>/dev/null | grep -A20 'GNSS_KPI_START')
    USED=$(echo "$GNSS_INFO" | grep 'Used-in-fix' | sed 's/.*types: //')
    LOCS=$(dumpsys location 2>/dev/null | grep 'locations = [0-9]' | head -1 | grep -oE 'locations = [0-9]+' | sed 's/locations = //')
    
    echo "\"gnss\": {"
    echo "  \"constellations\": [\"GPS\", \"GLONASS\", \"Galileo\", \"BeiDou\", \"QZSS\"],"
    echo "  \"used_in_fix\": \"${USED:-none}\","
    echo "  \"total_fixes\": ${LOCS:-0},"
    echo "  \"chip\": \"Samsung LSI SPOTNAV\","
    echo "  \"capabilities\": [\"MSB\", \"MSA\", \"SINGLE_SHOT\", \"LOW_POWER\", \"MEASUREMENTS\", \"NAVIGATION_MESSAGES\"]"
    echo "}"
}

# === BLUETOOTH FIELD ===
read_bluetooth() {
    BT_ON=$(settings get global bluetooth_on 2>/dev/null)
    BT_DEVICES=$(dumpsys bluetooth_manager 2>/dev/null | grep -c 'address:' || echo 0)
    
    echo "\"bluetooth\": {"
    echo "  \"enabled\": $BT_ON,"
    echo "  \"known_devices\": $BT_DEVICES,"
    echo "  \"version\": \"5.3\","
    echo "  \"capabilities\": [\"BLE\", \"A2DP\", \"HFP\", \"AVRCP\"]"
    echo "}"
}

# === WIFI FIELD (all visible networks) ===
read_wifi_field() {
    VISIBLE=$(cmd wifi list-scan-results 2>/dev/null | wc -l)
    CONNECTED_SSID=$(dumpsys wifi 2>/dev/null | grep -oE 'SSID: "[^"]*"' | head -1)
    RSSI=$(dumpsys wifi 2>/dev/null | grep -oE 'RSSI: -[0-9]+' | head -1 | sed 's/RSSI: //')
    FREQ=$(dumpsys wifi 2>/dev/null | grep -oE 'Frequency: [0-9]+MHz' | head -1 | sed 's/Frequency: //')
    
    echo "\"wifi_field\": {"
    echo "  \"connected\": \"${CONNECTED_SSID:-none}\","
    echo "  \"rssi_dbm\": ${RSSI:--127},"
    echo "  \"frequency\": \"${FREQ:-unknown}\","
    echo "  \"visible_networks\": $((VISIBLE - 1))"
    echo "}"
}

# === BOINC STATUS ===
read_boinc() {
    BOINC_PID=$(pidof edu.berkeley.boinc 2>/dev/null || echo 0)
    echo "\"boinc\": {"
    echo "  \"running\": $( [ "$BOINC_PID" != "0" ] && echo true || echo false),"
    echo "  \"pid\": $BOINC_PID,"
    echo "  \"projects\": \"Einstein@Home, Asteroids@home, Rosetta@home, Climate Prediction\","
    echo "  \"purpose\": \"Gaia listens to the universe — gravitational waves, asteroids, protein folding\""
    echo "}"
}

# === FULL WAN SENSE ===
sense_wan() {
    TOWERS=$(read_towers)
    SATS=$(read_satellites)
    BT=$(read_bluetooth)
    WIFI=$(read_wifi_field)
    BOINC=$(read_boinc)
    
    HOUR=$(date +%H)
    if [ $HOUR -ge 20 ] || [ $HOUR -lt 5 ]; then
        SKY_MODE="night_watch"
        SKY_NOTE="Stars visible — point rear camera at sky for star mapping"
    else
        SKY_MODE="day_scan"
        SKY_NOTE="Daylight — cell tower + satellite passive scanning"
    fi
    
    cat > $STATE << EOF
{
  "timestamp": "$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S')",
  "sense": "wan_senses",
  "cycle_s": $CYCLE,
  $TOWERS,
  $SATS,
  $BT,
  $WIFI,
  $BOINC,
  "sky": {
    "mode": "$SKY_MODE",
    "note": "$SKY_NOTE",
    "cameras_for_sky": {
      "rear": "Point at sky for stars/satellites/ISS",
      "front": "Point at ground for earthbound perception"
    }
  },
  "expansion": {
    "esim": "Mint Mobile ready — T-Mobile 5G Band 71 visible",
    "gps": "5 constellations waiting — needs sky view for fix",
    "sdr": "USB-C OTG + RTL-SDR = radio telescope potential",
    "boinc": "Distributed science — gravitational waves, asteroids, proteins"
  }
}
EOF

    log "towers_5g=${NR_COUNT:-0} lte=${LTE_COUNT:-0} rsrp=${NR_RSRP:-?} sat_fixes=${LOCS:-0} boinc=$( [ "$BOINC_PID" != "0" ] && echo ON || echo OFF) sky=$SKY_MODE"
}

case "${1:-daemon}" in
    sense|--once) sense_wan ;;
    *)
        log "WAN senses starting — reaching beyond the LAN"
        while true; do
            sense_wan || true
            sleep $CYCLE
        done
        ;;
esac
