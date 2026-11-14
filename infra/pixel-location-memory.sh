#!/system/bin/sh
# gAIa LOCATION MEMORY — learns places by WiFi fingerprint
GAIA="/data/local/tmp/biomeos"
MEMORY="$GAIA/sensorium/places.jsonl"

# Snapshot current WiFi fingerprint
snapshot() {
  SCAN=$(cmd wifi list-scan-results 2>/dev/null | tail -n +2)
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  
  # Build fingerprint: sorted list of BSSID:RSSI pairs
  FP=""
  echo "$SCAN" | while read BSSID FREQ RSSI AGE SSID REST; do
    [ -n "$BSSID" ] && echo "$BSSID:$RSSI:$SSID"
  done | sort > /tmp/wifi-fp.txt
  
  # Hash the fingerprint for comparison
  HASH=$(cat /tmp/wifi-fp.txt | md5sum | cut -d' ' -f1)
  
  # Count of known APs
  AP_COUNT=$(wc -l < /tmp/wifi-fp.txt)
  
  # Strongest AP
  STRONGEST=$(sort -t: -k2 -n /tmp/wifi-fp.txt | tail -1)
  
  echo "{\"ts\":\"$TS\",\"hash\":\"$HASH\",\"aps\":$AP_COUNT,\"strongest\":\"$STRONGEST\"}"
}

case "$1" in
  learn)
    # Learn current location with a name
    NAME="$2"
    FP=$(snapshot)
    echo "$FP" | sed "s/}$/,\"name\":\"$NAME\"}/" >> "$MEMORY"
    echo "Learned: $NAME"
    echo "$FP"
    ;;
  where)
    # Compare current fingerprint to memory
    CURRENT=$(snapshot)
    HASH=$(echo "$CURRENT" | sed 's/.*"hash":"//;s/".*//')
    MATCH=$(grep "$HASH" "$MEMORY" 2>/dev/null | tail -1)
    if [ -n "$MATCH" ]; then
      NAME=$(echo "$MATCH" | sed 's/.*"name":"//;s/".*//')
      echo "I know this place: $NAME"
    else
      echo "New place. $CURRENT"
    fi
    ;;
  history)
    cat "$MEMORY" 2>/dev/null
    ;;
  *)
    echo "Usage: location-memory.sh learn <name> | where | history"
    ;;
esac
