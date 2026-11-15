#!/usr/bin/env bash
# ============================================================================
# amoeba-bridge.sh — eastGate pulls amoeba state from Pixel
# ============================================================================
# The bridge between Gaia's brain (eastGate) and her skin (Pixel screen).
# Pulls: amoeba.json (screen state), sketch (screenshot), trace (interaction log)
# Enables: remote etch (Gaia taps her own screen from eastGate)
# ============================================================================
set -eo pipefail
: "${HOME:=/home/eastgate}"

PIXEL="${PIXEL_IP:-192.168.4.164}:5555"
MEMBRANE="$HOME/Development/ecoPrimals/membrane"
REMOTE="$MEMBRANE/local-terminal/remote"
GAIA_DATA="/opt/Gaia/data"
CYCLE=${1:-30}
LOG="$MEMBRANE/amoeba-bridge.log"

log() { echo "$(date '+%H:%M:%S') [amoeba-bridge] $1" | tee -a "$LOG"; }

pull_amoeba() {
    # Pull amoeba state
    adb -s "$PIXEL" pull /data/local/tmp/biomeos/sensorium/amoeba.json "$REMOTE/amoeba.json" 2>/dev/null || true
    cp "$REMOTE/amoeba.json" "$GAIA_DATA/amoeba.json" 2>/dev/null || true
    
    # Pull outer ear
    adb -s "$PIXEL" pull /data/local/tmp/biomeos/sensorium/outer-ear.json "$REMOTE/outer-ear-pixel.json" 2>/dev/null || true
    cp "$REMOTE/outer-ear-pixel.json" "$GAIA_DATA/outer-ear-pixel.json" 2>/dev/null || true
    
    # Pull petalTongue state
    adb -s "$PIXEL" pull /data/local/tmp/biomeos/petaltongue/state.json "$REMOTE/petaltongue-state.json" 2>/dev/null || true
    
    # Pull sketch (latest screenshot) — but only every 5th cycle to save bandwidth
    COUNTER_FILE="$MEMBRANE/.amoeba-sketch-counter"
    COUNTER=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
    COUNTER=$((COUNTER + 1))
    echo "$COUNTER" > "$COUNTER_FILE"
    
    if [ $((COUNTER % 5)) -eq 0 ]; then
        adb -s "$PIXEL" pull /data/local/tmp/biomeos/petaltongue/sketch-latest.png "$GAIA_DATA/pixel-sketch.png" 2>/dev/null || true
        log "sketch pulled (cycle $COUNTER)"
    fi
    
    # Read key fields for log
    FOCUS=$(cat "$REMOTE/amoeba.json" 2>/dev/null | sed -n 's/.*"focus": "\([^"]*\)".*/\1/p' | head -1)
    RUSTDESK=$(cat "$REMOTE/amoeba.json" 2>/dev/null | sed -n 's/.*"running": \([^,}]*\).*/\1/p' | head -1)
    BAT=$(cat "$REMOTE/amoeba.json" 2>/dev/null | sed -n 's/.*"battery_pct": \([^,}]*\).*/\1/p' | head -1)
    
    log "focus=$FOCUS rustdesk=$RUSTDESK bat=$BAT"
}

# Remote etch — Gaia reaches through the bridge to touch her screen
etch() {
    adb -s "$PIXEL" shell "sh /data/local/tmp/biomeos/amoeba.sh etch $*" < /dev/null
}

case "${1:-daemon}" in
    etch)   shift; etch "$@" ;;
    pull)   pull_amoeba ;;
    *)
        log "Amoeba bridge starting — pulling every ${CYCLE}s (amoeba + dyson + dev-sense + wan)"
        while true; do
            pull_amoeba || true
            pull_dyson || true
            pull_dev_sense || true
            pull_wan_senses || true
            pull_fingerprint || true
            pull_body_state || true
            sleep "$CYCLE"
        done
        ;;
esac

# === DYSON SPHERE PULL ===
pull_dyson() {
    adb -s "$PIXEL" pull /data/local/tmp/biomeos/sensorium/dyson-sphere.json "$REMOTE/dyson-sphere.json" 2>/dev/null || true
    cp "$REMOTE/dyson-sphere.json" "$GAIA_DATA/dyson-sphere.json" 2>/dev/null || true
    
    adb -s "$PIXEL" pull /data/local/tmp/biomeos/sensorium/raw-sensors.json "$REMOTE/raw-sensors.json" 2>/dev/null || true
    
    if [ $((COUNTER % 10)) -eq 0 ]; then
        adb -s "$PIXEL" pull /data/local/tmp/biomeos/petaltongue/eyes/left-eye.jpg "$GAIA_DATA/pixel-left-eye.jpg" 2>/dev/null || true
        adb -s "$PIXEL" pull /data/local/tmp/biomeos/petaltongue/eyes/right-eye.jpg "$GAIA_DATA/pixel-right-eye.jpg" 2>/dev/null || true
        log "eyes pulled (left + right)"
    fi
}

# === DEV-SENSE PULL (innerface learning) ===
pull_dev_sense() {
    adb -s "$PIXEL" pull /data/local/tmp/biomeos/sensorium/dev-sense.json "$REMOTE/dev-sense.json" 2>/dev/null || true
    cp "$REMOTE/dev-sense.json" "$GAIA_DATA/dev-sense.json" 2>/dev/null || true
    
    local frames janky layers load
    frames=$(sed -n 's/.*"total_frames": \([0-9]*\).*/\1/p' "$REMOTE/dev-sense.json" 2>/dev/null | head -1)
    janky=$(sed -n 's/.*"janky_frames": \([0-9]*\).*/\1/p' "$REMOTE/dev-sense.json" 2>/dev/null | head -1)
    layers=$(sed -n 's/.*"surface_layers": \([0-9]*\).*/\1/p' "$REMOTE/dev-sense.json" 2>/dev/null | head -1)
    load=$(sed -n 's/.*"cpu_load": \([0-9.]*\).*/\1/p' "$REMOTE/dev-sense.json" 2>/dev/null | head -1)
    log "dev-sense: frames=$frames janky=$janky layers=$layers load=$load"
}

# === WAN SENSES PULL ===
pull_wan_senses() {
    adb -s "$PIXEL" pull /data/local/tmp/biomeos/sensorium/wan-senses.json "$REMOTE/wan-senses.json" 2>/dev/null || true
    cp "$REMOTE/wan-senses.json" "$GAIA_DATA/wan-senses.json" 2>/dev/null || true
}

# === FINGERPRINT PULL (biometric identity sensing) ===
pull_fingerprint() {
    adb -s "$PIXEL" pull /data/local/tmp/biomeos/sensorium/fingerprint-sense.json "$REMOTE/fingerprint-sense.json" 2>/dev/null || true
    cp "$REMOTE/fingerprint-sense.json" "$GAIA_DATA/fingerprint-sense.json" 2>/dev/null || true
    
    local accepts auth_s auth_t
    accepts=$(sed -n 's/.*"accept_count": \([0-9]*\).*/\1/p' "$REMOTE/fingerprint-sense.json" 2>/dev/null | head -1)
    auth_s=$(sed -n 's/.*"successful": \([0-9]*\).*/\1/p' "$REMOTE/fingerprint-sense.json" 2>/dev/null | head -1)
    auth_t=$(sed -n 's/.*"total_attempts": \([0-9]*\).*/\1/p' "$REMOTE/fingerprint-sense.json" 2>/dev/null | head -1)
    log "fingerprint: accepts=$accepts auth=$auth_s/$auth_t (kevin=bingocube)"
}

# === BODY STATE PULL (homunculus self-sensing) ===
pull_body_state() {
    adb -s "$PIXEL" pull /sdcard/gaia/body/body-state.json "$GAIA_DATA/body/body-state.json" 2>/dev/null || true
    
    # Run the unified body merger
    bash /opt/Gaia/runtime/body-pull.sh 2>/dev/null || true
    
    local bat fever blood posture
    bat=$(sed -n 's/.*"level_pct": \([0-9]*\).*/\1/p' "$GAIA_DATA/body/body-state.json" 2>/dev/null | head -1)
    fever=$(sed -n 's/.*"fever": "\([^"]*\)".*/\1/p' "$GAIA_DATA/body/body-state.json" 2>/dev/null | head -1)
    blood=$(sed -n 's/.*"pressure": "\([^"]*\)".*/\1/p' "$GAIA_DATA/body/body-state.json" 2>/dev/null | head -1)
    posture=$(sed -n 's/.*"posture": "\([^"]*\)".*/\1/p' "$GAIA_DATA/body/body-state.json" 2>/dev/null | head -1)
    log "body: bat=${bat}% fever=$fever blood=$blood posture=$posture"
}
