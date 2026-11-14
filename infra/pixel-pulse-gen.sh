#!/system/bin/sh
# gAIa PULSE — the Pixel's own heartbeat
GAIA="/data/local/tmp/biomeos"
OUT="$GAIA/hud/pulse"
BEAT=0

while true; do
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  BEAT=$((BEAT + 1))
  UP=$(cut -d' ' -f1 /proc/uptime)
  
  # Count alive primals
  PRIMALS=$(ps -ef 2>/dev/null | grep "/biomeos/primals/" | grep -v grep | wc -l)
  
  # Battery
  BAT_LVL=$(dumpsys battery 2>/dev/null | sed -n 's/.*level: \([0-9]*\).*/\1/p' | head -1)
  BAT_TEMP=$(dumpsys battery 2>/dev/null | sed -n 's/.*temperature: \([0-9]*\).*/\1/p' | head -1)
  
  # WiFi RSSI
  RSSI=$(dumpsys wifi 2>/dev/null | grep "mWifiInfo" | head -1 | sed 's/.*RSSI: //' | sed 's/[^0-9-].*//')
  
  # Memory
  MEM_PCT=$(( $(grep MemAvailable /proc/meminfo | awk '{print $2}') * 100 / $(grep MemTotal /proc/meminfo | awk '{print $2}') ))
  
  # Self
  SELF_IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
  
  printf '{"ts":"%s","beat":%d,"uptime":"%s","primals":%d,"battery":%s,"temp_c":%.1f,"rssi":%s,"mem_pct":%d,"self":"%s","anchor":"gradient","tethered":"NOTHING"}\n' \
    "$TS" "$BEAT" "$UP" "$PRIMALS" \
    "${BAT_LVL:-0}" "$((${BAT_TEMP:-0}))" "${RSSI:-0}" "$MEM_PCT" "$SELF_IP" > "$OUT"
  
  sleep 10
done
