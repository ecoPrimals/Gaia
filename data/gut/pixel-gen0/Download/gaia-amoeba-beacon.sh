#!/data/data/com.termux/files/usr/bin/bash
# Gaia Amoeba Beacon — runs on grapheneGate (Termux)
# Sends sensor data to eastGate every 30 seconds
# Even when USB is disconnected, WiFi reaches home

EASTGATE="http://192.168.4.244:8443"
INTERVAL=30

while true; do
  TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  # Read sensors via termux-sensor (if available)
  SENSOR_DATA=""
  if command -v termux-sensor &>/dev/null; then
    SENSOR_DATA=$(termux-sensor -s "accelerometer,gyroscope,light,pressure,proximity" -n 1 2>/dev/null | head -20)
  fi
  
  # WiFi info via termux-wifi-connectioninfo
  WIFI_DATA=""
  if command -v termux-wifi-connectioninfo &>/dev/null; then
    WIFI_DATA=$(termux-wifi-connectioninfo 2>/dev/null)
  fi
  
  # WiFi scan via termux-wifi-scaninfo
  SCAN_DATA=""
  if command -v termux-wifi-scaninfo &>/dev/null; then
    SCAN_DATA=$(termux-wifi-scaninfo 2>/dev/null)
  fi
  
  # Battery via termux-battery-status
  BATTERY_DATA=""
  if command -v termux-battery-status &>/dev/null; then
    BATTERY_DATA=$(termux-battery-status 2>/dev/null)
  fi
  
  # Location via termux-location  
  LOCATION_DATA=""
  if command -v termux-location &>/dev/null; then
    LOCATION_DATA=$(termux-location -p network -r once 2>/dev/null)
  fi
  
  # Build payload
  PAYLOAD=$(cat <<EOF
{
  "ts": "$TS",
  "source": "termux-beacon",
  "gate": "grapheneGate",
  "sensors": $( [ -n "$SENSOR_DATA" ] && echo "$SENSOR_DATA" || echo '{}' ),
  "wifi": $( [ -n "$WIFI_DATA" ] && echo "$WIFI_DATA" || echo '{}' ),
  "wifi_scan": $( [ -n "$SCAN_DATA" ] && echo "$SCAN_DATA" || echo '[]' ),
  "battery": $( [ -n "$BATTERY_DATA" ] && echo "$BATTERY_DATA" || echo '{}' ),
  "location": $( [ -n "$LOCATION_DATA" ] && echo "$LOCATION_DATA" || echo '{}' )
}
EOF
)
  
  # Beacon to eastGate — ZK imprint + sensor data
  curl -s -X POST "$EASTGATE/api/zk/imprint" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"grapheneGate-beacon\",\"hw\":\"Pixel8a\"}" >/dev/null 2>&1
  
  # Send sensor payload to neutron channel
  curl -s -X POST "$EASTGATE/api/neutron" \
    -H "Content-Type: application/json" \
    -d "{\"channel\":\"amoeba-beacon\",\"author\":\"grapheneGate\",\"body\":\"$TS beacon\"}" >/dev/null 2>&1
  
  echo "[$TS] Beacon sent to eastGate"
  sleep $INTERVAL
done
