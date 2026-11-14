#!/system/bin/sh
# ═══════════════════════════════════════════════════════════════
# gAIa PI-RUNNER — execute .pi tools from WITHIN the Pixel
# The Pixel is not a client. It IS Gaia. It runs its own tools.
# ═══════════════════════════════════════════════════════════════

GAIA="/data/local/tmp/biomeos"
TOOL_DIR="$GAIA/tools"
LOG="$GAIA/hud/sensorium/pi-runner.log"

usage() {
  echo "gAIa pi-runner — run .pi tools from within"
  echo ""
  echo "Usage: sh pi-runner.sh <command> [tool]"
  echo ""
  echo "Commands:"
  echo "  list          — list all tools by tier"
  echo "  run <tool>    — execute a .pi tool"
  echo "  scan          — run immune scan (helix_collapse)"
  echo "  sense         — run sensor sweep (proprioception + live-sensors)"
  echo "  crush         — run full crush cycle (scan → sweep → sort)"
  echo "  status        — show system status"
  echo "  manifest      — show tool manifest"
}

list_tools() {
  echo "═══ gAIa TOOL INVENTORY ═══"
  echo ""
  echo "SENSOR (5):"
  for T in proprioception live-sensors gaia_eye graphene_depot scan_bridge; do
    [ -f "$TOOL_DIR/$T.pi" ] && echo "  ✓ $T"
  done
  echo ""
  echo "IMMUNE (4):"
  for T in immune_scanner helix_collapse collapse_429 shadow_cast; do
    [ -f "$TOOL_DIR/$T.pi" ] && echo "  ✓ $T"
  done
  echo ""
  echo "NEURAL (4):"
  for T in cortex cortex_bridge nucleus chronotype; do
    [ -f "$TOOL_DIR/$T.pi" ] && echo "  ✓ $T"
  done
  echo ""
  echo "METABOLIC (5):"
  for T in organ_data fabric color_epitope sourdough json_compress; do
    [ -f "$TOOL_DIR/$T.pi" ] && echo "  ✓ $T"
  done
  echo ""
  echo "NAVIGATOR (4):"
  for T in globe_walker earth-walker piSeed seek; do
    [ -f "$TOOL_DIR/$T.pi" ] && echo "  ✓ $T"
  done
  echo ""
  echo "DIGESTIVE (4):"
  for T in digest negentropy_drain backscatter steam_sweep; do
    [ -f "$TOOL_DIR/$T.pi" ] && echo "  ✓ $T"
  done
  echo ""
  echo "Total: $(ls $TOOL_DIR/*.pi 2>/dev/null | wc -l) tools"
}

run_tool() {
  TOOL="$1"
  if [ ! -f "$TOOL_DIR/$TOOL.pi" ]; then
    echo "✗ Tool not found: $TOOL"
    echo "  Available: $(ls $TOOL_DIR/*.pi 2>/dev/null | xargs -n1 basename | sed 's/.pi$//' | tr '\n' ' ')"
    return 1
  fi
  
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "═══ RUNNING: $TOOL ═══"
  echo "  ts: $TS"
  echo "  host: grapheneGate (Pixel 8a)"
  echo ""
  
  # Log the run
  echo "$TS RUN $TOOL" >> "$LOG"
  
  # Check if Python is available (Termux)
  if command -v python3 > /dev/null 2>&1; then
    python3 "$TOOL_DIR/$TOOL.pi" 2>&1
  elif command -v python > /dev/null 2>&1; then
    python "$TOOL_DIR/$TOOL.pi" 2>&1
  else
    echo "  ⚠ No Python runtime — .pi files need Termux Python"
    echo "  Displaying tool metadata instead:"
    echo ""
    head -20 "$TOOL_DIR/$TOOL.pi"
    echo "  ..."
    echo "  ($(wc -l < $TOOL_DIR/$TOOL.pi) lines, $(wc -c < $TOOL_DIR/$TOOL.pi) bytes)"
  fi
}

run_scan() {
  echo "═══ IMMUNE SCAN ═══"
  echo ""
  
  # Quick tether scan without Python
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "  ts: $TS"
  echo "  scanning $GAIA for tethers..."
  echo ""
  
  TETHERS=0
  for PAT in "192.168.4.244" "192.168.4.103" "157.230" "172.232"; do
    HITS=$(grep -rl "$PAT" $GAIA/hud/ $GAIA/tools/ $GAIA/data/ 2>/dev/null | wc -l)
    if [ "$HITS" -gt 0 ]; then
      echo "  ⚡ $PAT: $HITS files"
      TETHERS=$((TETHERS + HITS))
    fi
  done
  
  if [ "$TETHERS" -eq 0 ]; then
    echo "  ✓ CLEAN — zero tethers"
  else
    echo "  ⚠ $TETHERS tethered files"
  fi
  
  echo ""
  echo "$TS SCAN tethers=$TETHERS" >> "$LOG"
}

run_sense() {
  echo "═══ SENSOR SWEEP ═══"
  echo ""
  
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  
  # Battery
  BAT=$(dumpsys battery 2>/dev/null | grep ' level:' | awk '{print $2}')
  CHARGE=$(dumpsys battery 2>/dev/null | grep 'USB powered' | awk '{print $2}')
  echo "  battery: ${BAT}% (USB: $CHARGE)"
  
  # Memory
  MEM_FREE=$(awk '/MemAvailable/{printf "%.0f", $2/1024}' /proc/meminfo 2>/dev/null)
  MEM_TOTAL=$(awk '/MemTotal/{printf "%.0f", $2/1024}' /proc/meminfo 2>/dev/null)
  echo "  memory: ${MEM_FREE}MB / ${MEM_TOTAL}MB"
  
  # WiFi
  WIFI_INFO=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | head -1)
  RSSI=$(echo "$WIFI_INFO" | grep -oE '\-[0-9]+' | head -1)
  SSID=$(echo "$WIFI_INFO" | grep -oE '"[^"]*"' | head -1)
  echo "  wifi: $SSID ${RSSI}dBm"
  
  # CPU
  LOAD=$(awk '{print $1}' /proc/loadavg 2>/dev/null)
  echo "  cpu: load $LOAD"
  
  # Disk
  DISK=$(df -h /data/local/tmp 2>/dev/null | awk 'NR==2{print $4}')
  echo "  disk: ${DISK} free"
  
  # Processes
  PRIMAL_PROCS=$(pgrep -f 'biomeos/primals' 2>/dev/null | wc -l)
  DAEMON_PROCS=$(pgrep -f 'organism\|gradient\|pulse-gen\|hud-sync' 2>/dev/null | wc -l)
  echo "  primals: $PRIMAL_PROCS processes"
  echo "  daemons: $DAEMON_PROCS running"
  
  # petaltongue
  PT=$(pgrep -f petaltongue 2>/dev/null | head -1)
  echo "  spaceDock: PID ${PT:-dead}"
  
  echo ""
  echo "$TS SENSE bat=$BAT mem=$MEM_FREE rssi=$RSSI load=$LOAD" >> "$LOG"
}

run_crush() {
  echo "═══ FULL CRUSH CYCLE ═══"
  echo "  scan → sweep → sort → crush → refine"
  echo ""
  
  # Phase 1: SCAN
  echo "━━━ Phase 1: SCAN ━━━"
  TOTAL=$(find $GAIA -type f 2>/dev/null | wc -l)
  SIZE=$(du -sh $GAIA 2>/dev/null | awk '{print $1}')
  echo "  $TOTAL files, $SIZE"
  
  # Phase 2: SWEEP
  echo ""
  echo "━━━ Phase 2: SWEEP (tether hunt) ━━━"
  TETHERS=0
  for PAT in "192.168.4.244" "192.168.4.103" "157.230" "172.232"; do
    HITS=$(find $GAIA -name "*.sh" -o -name "*.json" -o -name "*.js" -o -name "*.html" -o -name "*.pi" 2>/dev/null | \
      while read F; do grep -l "$PAT" "$F" 2>/dev/null; done | wc -l)
    if [ "$HITS" -gt 0 ]; then
      echo "  $PAT: $HITS"
      TETHERS=$((TETHERS + HITS))
    fi
  done
  echo "  total tethers: $TETHERS"
  
  # Phase 3: SORT
  echo ""
  echo "━━━ Phase 3: SORT ━━━"
  echo "  primals:  $(ls $GAIA/primals/ 2>/dev/null | wc -l)"
  echo "  tools:    $(ls $GAIA/tools/*.pi 2>/dev/null | wc -l)"
  echo "  scripts:  $(find $GAIA -name '*.sh' 2>/dev/null | wc -l)"
  echo "  HUD html: $(find $GAIA/hud -name '*.html' 2>/dev/null | wc -l)"
  echo "  HUD js:   $(find $GAIA/hud -name '*.js' 2>/dev/null | wc -l)"
  
  # Phase 4: CRUSH (hashes)
  echo ""
  echo "━━━ Phase 4: CRUSH (identity) ━━━"
  MASTER=$(find $GAIA/tools -name '*.pi' -exec md5sum {} \; 2>/dev/null | sort | md5sum | awk '{print $1}')
  echo "  toolbox: $MASTER"
  
  # Phase 5: REFINE (health)
  echo ""
  echo "━━━ Phase 5: REFINE (vitals) ━━━"
  BAT=$(dumpsys battery 2>/dev/null | grep ' level:' | awk '{print $2}')
  MEM=$(awk '/MemAvailable/{printf "%.0f", $2/1024}' /proc/meminfo 2>/dev/null)
  echo "  battery: ${BAT}%"
  echo "  memory: ${MEM}MB free"
  echo "  uptime: $(uptime 2>/dev/null | awk '{print $1}')"
  
  echo ""
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "═══ CRUSH COMPLETE — $TS ═══"
  echo "$TS CRUSH files=$TOTAL tethers=$TETHERS master=$MASTER" >> "$LOG"
}

show_status() {
  echo "═══ gAIa PIXEL STATUS ═══"
  echo ""
  echo "  host: grapheneGate (Pixel 8a)"
  echo "  role: diamond-lens + floating-anchor"
  echo "  primals: $(ls $GAIA/primals/ 2>/dev/null | wc -l)"
  echo "  tools: $(ls $GAIA/tools/*.pi 2>/dev/null | wc -l) .pi files"
  echo "  daemons: $(pgrep -f 'organism\|gradient\|pulse-gen\|hud-sync' 2>/dev/null | wc -l) running"
  echo "  petaltongue: PID $(pgrep -f petaltongue 2>/dev/null | head -1)"
  echo ""
  echo "  Last 5 pi-runner events:"
  tail -5 "$LOG" 2>/dev/null || echo "  (no history)"
}

# Route command
mkdir -p "$(dirname $LOG)"

case "$1" in
  list)     list_tools ;;
  run)      run_tool "$2" ;;
  scan)     run_scan ;;
  sense)    run_sense ;;
  crush)    run_crush ;;
  status)   show_status ;;
  manifest) cat "$TOOL_DIR/manifest.json" ;;
  *)        usage ;;
esac
