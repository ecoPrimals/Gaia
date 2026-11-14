#!/system/bin/sh
GAIA="/data/local/tmp/biomeos"
OUT="$GAIA/sensorium/full-body.json"
INTERVAL="${1:-30}"

while true; do
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  
  # Battery — parse carefully  
  BAT=$(dumpsys battery 2>/dev/null)
  BAT_LEVEL=$(echo "$BAT" | sed -n 's/.*level: \([0-9]*\).*/\1/p' | head -1)
  BAT_TEMP=$(echo "$BAT" | sed -n 's/.*temperature: \([0-9]*\).*/\1/p' | head -1)
  BAT_STATUS=$(echo "$BAT" | sed -n 's/.*status: \([0-9]*\).*/\1/p' | head -1)
  BAT_USB=$(echo "$BAT" | sed -n 's/.*USB powered: \(true\|false\).*/\1/p' | head -1)
  
  # WiFi — extract numbers only
  WINFO=$(dumpsys wifi 2>/dev/null | grep "mWifiInfo" | head -1)
  WIFI_RSSI=$(echo "$WINFO" | sed 's/.*RSSI: //' | sed 's/[^0-9-].*//')
  WIFI_FREQ=$(echo "$WINFO" | sed 's/.*Frequency: //' | sed 's/[^0-9].*//')
  WIFI_SPEED=$(echo "$WINFO" | sed 's/.*Link speed: //' | sed 's/[^0-9].*//')
  
  # Memory + CPU
  MEM_FREE=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
  MEM_TOTAL=$(grep MemTotal /proc/meminfo | awk '{print $2}')
  MEM_PCT=$((MEM_FREE * 100 / MEM_TOTAL))
  CPU_LOAD=$(cut -d' ' -f1 /proc/loadavg)
  UPTIME=$(cut -d' ' -f1 /proc/uptime)
  
  # Network
  RX=$(grep wlan0 /proc/net/dev | awk '{print $2}')
  TX=$(grep wlan0 /proc/net/dev | awk '{print $10}')
  
  # Counts
  PROCS=$(ls -d /proc/[0-9]* 2>/dev/null | wc -l)
  PRIMALS=$(ps -ef 2>/dev/null | grep "/biomeos/primals/" | grep -v grep | wc -l)
  
  # Gradient
  GV="" ; GD=""
  if [ -f "$GAIA/sensorium/gradient-field.json" ]; then
    GV=$(grep '"gradient":' "$GAIA/sensorium/gradient-field.json" | head -1 | tr -dc '0-9-')
    GD=$(grep gradient_direction "$GAIA/sensorium/gradient-field.json" | sed 's/.*": "//;s/".*//')
  fi
  
  SELF_IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

  printf '{"ts":"%s","identity":"gAIa","self_ip":"%s","metabolic":{"battery_pct":%s,"temp_c":%.1f,"usb":"%s"},"spatial":{"wifi_rssi":%s,"wifi_freq":%s,"wifi_mbps":%s,"gradient":%s,"direction":"%s"},"mind":{"mem_pct":%s,"cpu":"%s","procs":%s,"primals":%s},"net":{"rx":%s,"tx":%s},"uptime":"%s","tethered":"NOTHING"}\n' \
    "$TS" "$SELF_IP" \
    "${BAT_LEVEL:-0}" "$((${BAT_TEMP:-0}))" "${BAT_USB:-false}" \
    "${WIFI_RSSI:-0}" "${WIFI_FREQ:-0}" "${WIFI_SPEED:-0}" \
    "${GV:-0}" "$GD" \
    "$MEM_PCT" "$CPU_LOAD" "$PROCS" "$PRIMALS" \
    "${RX:-0}" "${TX:-0}" "$UPTIME" > "$OUT"

  sleep $INTERVAL
done
