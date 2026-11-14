#!/system/bin/sh
# ═══════════════════════════════════════════════════════════
# gAIa REDOX ENGINE — scan, sweep, sort, crush, refine
# Runs FROM WITHIN the Pixel. The organism heals itself.
# ═══════════════════════════════════════════════════════════

GAIA="/data/local/tmp/biomeos"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
OUT="$GAIA/hud/sensorium/redox-report.json"

echo "═══ gAIa REDOX — scanning from within ═══"
echo "  ts: $TS"
echo ""

# ═══ SCAN: inventory everything ═══
echo "━━━ SCAN ━━━"
TOTAL_FILES=$(find $GAIA -type f 2>/dev/null | wc -l)
TOTAL_BYTES=$(du -sb $GAIA 2>/dev/null | awk '{print $1}')
TOTAL_MB=$((TOTAL_BYTES / 1048576))
PRIMAL_COUNT=$(ls $GAIA/primals/ 2>/dev/null | wc -l)
SCRIPT_COUNT=$(find $GAIA -name "*.sh" -o -name "*.py" -o -name "*.pi" 2>/dev/null | wc -l)
HUD_COUNT=$(find $GAIA/hud -name "*.html" 2>/dev/null | wc -l)
JS_COUNT=$(find $GAIA/hud -name "*.js" 2>/dev/null | wc -l)
TOOL_COUNT=$(ls $GAIA/tools/*.pi 2>/dev/null | wc -l)

echo "  files:    $TOTAL_FILES"
echo "  size:     ${TOTAL_MB}MB"
echo "  primals:  $PRIMAL_COUNT"
echo "  scripts:  $SCRIPT_COUNT"
echo "  tools:    $TOOL_COUNT .pi"
echo "  HUD html: $HUD_COUNT"
echo "  HUD js:   $JS_COUNT"

# ═══ SWEEP: check for tethers ═══
echo ""
echo "━━━ SWEEP (tether scan) ━━━"
TETHER_COUNT=0

# Check for hardcoded IPs
for PAT in "192.168.4.244" "192.168.4.103" "GAIA_BRAIN" "157.230" "172.232"; do
  HITS=$(grep -rl "$PAT" $GAIA/*.sh $GAIA/*.json $GAIA/tools/*.pi 2>/dev/null | wc -l)
  if [ "$HITS" -gt 0 ]; then
    echo "  ⚡ $PAT: $HITS files"
    TETHER_COUNT=$((TETHER_COUNT + HITS))
  fi
done

if [ "$TETHER_COUNT" -eq 0 ]; then
  echo "  ✓ ZERO tethers — fully autonomous"
else
  echo "  ⚠ $TETHER_COUNT tethered files found"
fi

# ═══ SORT: classify everything ═══
echo ""
echo "━━━ SORT ━━━"
echo "  KERNEL:"
ls $GAIA/primals/biomeOS 2>/dev/null && echo "    biomeOS ✓" || echo "    biomeOS ✗"

echo "  PRIMALS:"
for P in $(ls $GAIA/primals/ 2>/dev/null); do
  SIZE=$(du -sb "$GAIA/primals/$P" 2>/dev/null | awk '{print $1}')
  SIZE_KB=$((SIZE / 1024))
  echo "    $P: ${SIZE_KB}KB"
done

echo "  DAEMONS:"
for D in organism gradient-anchor pulse-gen hud-sync full-sensorium; do
  PID=$(pgrep -f "$D" 2>/dev/null | head -1)
  if [ -n "$PID" ]; then
    echo "    $D: PID $PID ✓"
  else
    echo "    $D: not running"
  fi
done

echo "  SENSES:"
for S in gradient-field.json full-body.json; do
  if [ -f "$GAIA/hud/sensorium/$S" ]; then
    AGE=$(( $(date +%s) - $(stat -c %Y "$GAIA/hud/sensorium/$S" 2>/dev/null || echo 0) ))
    echo "    $S: ${AGE}s ago"
  else
    echo "    $S: missing"
  fi
done

# ═══ CRUSH: compute hashes ═══
echo ""
echo "━━━ CRUSH (identity hashes) ━━━"

# Hash all primals
PRIMAL_HASH=""
for P in $(ls $GAIA/primals/ 2>/dev/null | sort); do
  H=$(md5sum "$GAIA/primals/$P" 2>/dev/null | awk '{print $1}')
  PRIMAL_HASH="${PRIMAL_HASH}:${H}"
done
GENOME_HASH=$(echo -n "$PRIMAL_HASH" | md5sum | awk '{print $1}')
echo "  genome:   $GENOME_HASH"

# Hash all scripts  
SCRIPT_HASH=$(find $GAIA -name "*.sh" -exec md5sum {} \; 2>/dev/null | sort | md5sum | awk '{print $1}')
echo "  scripts:  $SCRIPT_HASH"

# Hash all HUD
HUD_HASH=$(find $GAIA/hud -name "*.html" -exec md5sum {} \; 2>/dev/null | sort | md5sum | awk '{print $1}')
echo "  hud:      $HUD_HASH"

# Master hash
MASTER=$(echo -n "${GENOME_HASH}:${SCRIPT_HASH}:${HUD_HASH}:${TS}" | md5sum | awk '{print $1}')
echo "  MASTER:   $MASTER"

# ═══ REFINE: health check ═══
echo ""
echo "━━━ REFINE (health) ━━━"

# Battery
BAT_LEVEL=$(dumpsys battery 2>/dev/null | grep ' level:' | head -1 | awk '{print $2}')
BAT_CHARGE=$(dumpsys battery 2>/dev/null | grep 'USB powered' | head -1 | awk '{print $2}')
echo "  battery:  ${BAT_LEVEL}% (USB: ${BAT_CHARGE})"

# Memory
MEM_FREE=$(cat /proc/meminfo 2>/dev/null | awk '/MemAvailable/{printf "%.0f", $2/1024}')
MEM_TOTAL=$(cat /proc/meminfo 2>/dev/null | awk '/MemTotal/{printf "%.0f", $2/1024}')
echo "  memory:   ${MEM_FREE}MB / ${MEM_TOTAL}MB"

# WiFi
RSSI=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | grep -oE '\-[0-9]+' | head -1)
SSID=$(dumpsys wifi 2>/dev/null | grep 'mWifiInfo' | grep -oE '"[^"]*"' | head -1)
echo "  wifi:     $SSID ${RSSI}dBm"

# CPU
CPU_LOAD=$(cat /proc/loadavg 2>/dev/null | awk '{print $1}')
echo "  cpu:      load $CPU_LOAD"

# petaltongue
PT_PID=$(pgrep -f petaltongue 2>/dev/null | head -1)
echo "  spaceDock: PID ${PT_PID:-dead}"

# ═══ WRITE REPORT ═══
echo ""
echo "━━━ WRITING REPORT ━━━"

mkdir -p "$(dirname $OUT)"
printf '{"ts":"%s","scan":{"files":%d,"bytes":%d,"primals":%d,"scripts":%d,"tools":%d,"hud_html":%d,"hud_js":%d},"sweep":{"tethers":%d},"crush":{"genome":"%s","scripts":"%s","hud":"%s","master":"%s"},"refine":{"battery":%s,"mem_free_mb":%s,"mem_total_mb":%s,"rssi":%s,"cpu_load":"%s","spacedock_pid":"%s"}}\n' \
  "$TS" "$TOTAL_FILES" "$TOTAL_BYTES" "$PRIMAL_COUNT" "$SCRIPT_COUNT" "$TOOL_COUNT" "$HUD_COUNT" "$JS_COUNT" \
  "$TETHER_COUNT" "$GENOME_HASH" "$SCRIPT_HASH" "$HUD_HASH" "$MASTER" \
  "${BAT_LEVEL:-0}" "${MEM_FREE:-0}" "${MEM_TOTAL:-0}" "${RSSI:-0}" "${CPU_LOAD:-0}" "${PT_PID:-0}" \
  > "$OUT"

echo "  → $OUT"
echo ""
echo "═══ REDOX COMPLETE ═══"
echo "  $TOTAL_FILES files, ${TOTAL_MB}MB, $PRIMAL_COUNT primals"
echo "  $TETHER_COUNT tethers, master: $MASTER"
echo "  The organism knows itself. lub-DUB."
