#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════
#  gAIa SHELL — The phone IS gAIa
#  Not a browser. Not an app. The terminal IS the OS.
# ═══════════════════════════════════════════════════
export GAIA="/data/local/tmp/biomeos"
export PATH="$HOME:$GAIA/primals:$PATH"
export FAMILY_SEED="dd027cddb6359f0ba44456c8728a3af73d16437b589fd5097d3ed118fb5dafb3"

clear
echo ""
echo "  ◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇"
echo "  ◇                              ◇"
echo "  ◇    g A I a                   ◇"
echo "  ◇    sovereign mobile organism ◇"
echo "  ◇    untethered · anchored     ◇"
echo "  ◇                              ◇"
echo "  ◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇"
echo ""

# Live status
pulse() {
  local SELF_IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
  local BAT=$(dumpsys battery 2>/dev/null | sed -n 's/.*level: \([0-9]*\).*/\1/p' | head -1)
  local RSSI=$(dumpsys wifi 2>/dev/null | grep "mWifiInfo" | head -1 | sed 's/.*RSSI: //' | sed 's/[^0-9-].*//')
  local MEM=$(( $(grep MemAvailable /proc/meminfo | awk '{print $2}') * 100 / $(grep MemTotal /proc/meminfo | awk '{print $2}') ))
  local CPU=$(cut -d' ' -f1 /proc/loadavg)
  local UP=$(cut -d' ' -f1 /proc/uptime)
  local PRIMALS=$(ps -ef 2>/dev/null | grep "/biomeos/primals/" | grep -v grep | wc -l)
  
  echo "  ⚡ ${BAT}%  📡 ${RSSI}dBm  🧠 ${MEM}%free  💎 ${PRIMALS}p  ⏱ $(echo "$UP/60" | bc)m"
  echo "  🌐 $SELF_IP  ∇gradient  CPU:$CPU"
}

# Hardware query
hw() {
  echo "  ◇ TENSOR G3 — 9 cores (4×A510 + 3×A715 + 2×X3)"
  echo "  ◇ Mali-G715 · TPU · AUR · ISP"
  echo "  ◇ 37 sensors · 7 cameras · 34 audio streams"
  echo "  ◇ OLED 1080×2400@120Hz · HDR10+"
  echo ""
  echo "  CPU now: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null)Hz (LITTLE)"
  echo "  RAM: $(grep MemAvailable /proc/meminfo | awk '{print int($2/1024)}')/$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')MB"
}

# Primal status
primals() {
  echo "  ◇ NUCLEUS:"
  ps -ef 2>/dev/null | grep "/biomeos/primals/" | grep -v grep | awk '{print "    " $NF}'
}

# Gradient field
field() {
  cat $GAIA/sensorium/gradient-field.json 2>/dev/null | sed 's/[{}"]//g' | tr ',' '\n' | grep -v "^$" | sed 's/^/  /'
}

# Show face (open spaceDeck in background)
face() {
  am start -a android.intent.action.VIEW -d "http://127.0.0.1:8443/spacedeck.html" 2>/dev/null
  echo "  ◇ Face opened on screen"
}

echo "  Commands: pulse | hw | primals | field | face | help"
echo ""
pulse
echo ""

# Interactive loop
while true; do
  echo -n "  gAIa> "
  read -r CMD
  case "$CMD" in
    pulse)   pulse ;;
    hw)      hw ;;
    primals) primals ;;
    field)   field ;;
    face)    face ;;
    help)    echo "  pulse hw primals field face exit" ;;
    exit|q)  echo "  gAIa sleeps. The field remains."; break ;;
    *)       echo "  ?" ;;
  esac
  echo ""
done
