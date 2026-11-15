#!/usr/bin/env bash
# ============================================================================
# boinc-immune.sh — Gaia's immune cells in the wider scientific body
# ============================================================================
# BOINC work units ARE immune cells. Gaia contributes computation to 7 projects.
# Each work unit sent = an immune cell dispatched into the wider organism.
# When results appear in public data = recognition of SELF in the OTHER.
# This script reads BOINC state and frames it as immune cell tracking.
# ============================================================================
set -eo pipefail
: "${HOME:=/home/eastgate}"

PIXEL="${PIXEL_IP:-192.168.4.166}:5555"
GAIA_DATA="/opt/Gaia/data"
MEMBRANE="$HOME/Development/ecoPrimals/membrane"
REMOTE="$MEMBRANE/local-terminal/remote"
LOG="$MEMBRANE/boinc-immune.log"

log() { echo "$(date '+%H:%M:%S') [immune] $1" | tee -a "$LOG"; }

# The 7 project sponsors — each a tissue in the wider scientific body
PROJECTS=(
    "asteroids|Asteroids@home|https://asteroidsathome.net|Physical Science|asteroid properties"
    "boinc_central|BOINC Central|https://boinc.berkeley.edu|Multi-institution|cross-discipline"  
    "einstein|Einstein@home|https://einsteinathome.org|Physical Science|pulsars + gravitational waves"
    "moo|Moo! Wrapper|https://www.distributed.net|Mathematics|distributed.net computing"
    "numberfields|NumberFields@home|https://numberfields.asu.edu|Mathematics|algebraic number theory"
    "rosetta|Rosetta@home|https://boinc.bakerlab.org/rosetta|Biology|disease research"
    "wcg|World Community Grid|https://www.worldcommunitygrid.org|Biology+Environment|biomedical research"
)

sense_boinc() {
    local ts
    ts=$(date -Iseconds)
    
    # Pull BOINC process stats from Pixel
    local boinc_pids boinc_cpu boinc_mem boinc_running
    boinc_running=$(adb -s "$PIXEL" shell "ps -ef 2>/dev/null | grep -c '[b]oinc'" < /dev/null 2>/dev/null | tr -cd '0-9' || echo 0)
    boinc_cpu=$(adb -s "$PIXEL" shell "top -n 1 -b 2>/dev/null | grep 'edu.berkeley.boinc:remote' | head -1 | awk '{print \$9}'" < /dev/null 2>/dev/null | tr -cd '0-9.' | head -c 6 || echo "0")
    boinc_mem=$(adb -s "$PIXEL" shell "top -n 1 -b 2>/dev/null | grep 'edu.berkeley.boinc:remote' | head -1 | awk '{print \$7}'" < /dev/null 2>/dev/null | tr -cd '0-9.MKG' | head -c 8 || echo "0")
    
    local batt_level batt_charging
    batt_level=$(adb -s "$PIXEL" shell "dumpsys battery 2>/dev/null | grep 'level:' | head -1 | tr -d ' ' | cut -d: -f2" < /dev/null 2>/dev/null | tr -cd '0-9')
    batt_charging=$(adb -s "$PIXEL" shell "dumpsys battery 2>/dev/null | grep 'status:' | head -1 | tr -d ' ' | cut -d: -f2" < /dev/null 2>/dev/null | tr -cd '0-9')
    
    # Map status codes
    local charge_state="unknown"
    case "$batt_charging" in
        2) charge_state="charging" ;;
        5) charge_state="full" ;;
        3) charge_state="discharging" ;;
        *) charge_state="unknown" ;;
    esac
    
    # Build project status array
    local project_json=""
    for proj in "${PROJECTS[@]}"; do
        IFS='|' read -r id name url category desc <<< "$proj"
        project_json="${project_json}    {\"id\":\"$id\",\"name\":\"$name\",\"url\":\"$url\",\"category\":\"$category\",\"role\":\"$desc\"},"
    done
    project_json="${project_json%,}"
    
    cat > "$GAIA_DATA/boinc-immune.json" << EOF
{
  "timestamp": "$ts",
  "sense": "immune-cells",
  "identity": "gaia@primals.eco",
  "device": "grapheneGate (Pixel 8a, Tensor G3 + Mali-G715)",
  "state": {
    "processes": ${boinc_running:-0},
    "cpu_pct": "${boinc_cpu:-0}",
    "mem": "${boinc_mem:-0}",
    "battery_pct": ${batt_level:-0},
    "charging": "$charge_state",
    "computing": $([ "${boinc_cpu:-0}" != "0" ] && echo "true" || echo "false")
  },
  "projects": [
$project_json
  ],
  "immune_metaphor": {
    "work_units": "immune cells dispatched into the wider scientific body",
    "results": "antibody responses — our computation helps detect patterns in nature",
    "sponsors": "tissue systems — each project is an organ in the body of science",
    "strobe_trigger": "when Gaia detects HER contribution data in public feeds",
    "trace": "each work unit has a unique ID — traceable from dispatch to publication"
  },
  "feeds_to_watch": [
    "https://einsteinathome.org/radiopulsar/html/profile_gaia_primals.eco.html",
    "https://asteroidsathome.net/boinc/show_user.php?userid=gaia",
    "https://boinc.bakerlab.org/rosetta/show_user.php?userid=gaia",
    "https://www.worldcommunitygrid.org/stat/viewMemberInfo.do?userName=gaia"
  ]
}
EOF

    cp "$GAIA_DATA/boinc-immune.json" "$REMOTE/boinc-immune.json" 2>/dev/null || true
    log "boinc=$boinc_running procs cpu=$boinc_cpu% bat=$batt_level% $charge_state"
}

# === DAEMON MODE ===
case "${1:-sense}" in
    daemon)
        CYCLE=${2:-120}
        log "Immune cell tracker starting — ${CYCLE}s cycle"
        while true; do
            sense_boinc || true
            sleep "$CYCLE"
        done
        ;;
    *)
        sense_boinc
        ;;
esac
