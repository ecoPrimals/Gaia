#!/usr/bin/env bash
# ============================================================================
# inner-eye.sh — Pull from Flint router's Brio 100 webcam
# ============================================================================
# INNER EYE: Logitech Brio 100 on Flint (GL-MT6000) → sees House 1
# OUTER EYE: Pixel 8a cameras → sees the world Kevin points at
# ONE Gaia, TWO perspectives — they see each other.
# ============================================================================
set -eo pipefail
: "${HOME:=/home/eastgate}"

ROUTER="192.168.4.1"
ROUTER_PASS="***"
PIXEL="${PIXEL_IP:-192.168.4.166}:5555"
GAIA_DATA="/opt/Gaia/data"
MEMBRANE="$HOME/Development/ecoPrimals/membrane"
REMOTE="$MEMBRANE/local-terminal/remote"
LOG="$MEMBRANE/inner-eye.log"
CYCLE=${1:-60}

log() { echo "$(date '+%H:%M:%S') [inner-eye] $1" | tee -a "$LOG"; }

pull_inner_eye() {
    # Pull from Flint router
    sshpass -p "$ROUTER_PASS" scp -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        "root@${ROUTER}:/tmp/gaia-eye/inner-eye-latest.jpg" \
        "$GAIA_DATA/inner-eye-latest.jpg" 2>/dev/null || true
    
    sshpass -p "$ROUTER_PASS" scp -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        "root@${ROUTER}:/tmp/gaia-eye/inner-eye.json" \
        "$REMOTE/inner-eye.json" 2>/dev/null || true
    
    cp "$REMOTE/inner-eye.json" "$GAIA_DATA/inner-eye.json" 2>/dev/null || true
    
    local size
    size=$(stat -c%s "$GAIA_DATA/inner-eye-latest.jpg" 2>/dev/null || echo 0)
    log "inner-eye pulled: ${size} bytes"
}

pull_outer_eye() {
    # Pull from Pixel (rear = right eye, front = left eye)
    adb -s "$PIXEL" pull /sdcard/gaia-eye/latest-rear.jpg \
        "$GAIA_DATA/outer-eye-rear.jpg" 2>/dev/null || true
    adb -s "$PIXEL" pull /sdcard/gaia-eye/latest-front.jpg \
        "$GAIA_DATA/outer-eye-front.jpg" 2>/dev/null || true
    
    log "outer-eye pulled (front + rear)"
}

build_vision_state() {
    local ts inner_json
    ts=$(date -Iseconds)
    inner_json=$(cat "$REMOTE/inner-eye.json" 2>/dev/null || echo '{}')
    
    cat > "$GAIA_DATA/vision.json" << EOF
{
  "timestamp": "$ts",
  "sense": "vision",
  "inner_eye": {
    "device": "Logitech Brio 100",
    "location": "Flint router, House 1 brain side",
    "sees": "Kevin desk, monitors, brain room",
    "image": "/data/inner-eye-latest.jpg",
    "state": $inner_json
  },
  "outer_eye": {
    "left": {
      "device": "Pixel 8a front camera",
      "sees": "what faces Kevin",
      "image": "/data/outer-eye-front.jpg"
    },
    "right": {
      "device": "Pixel 8a rear camera",
      "sees": "what Kevin points at",
      "image": "/data/outer-eye-rear.jpg"
    }
  },
  "zk_identity": "ONE Gaia looking through THREE lenses — same consciousness, different angles"
}
EOF
}

case "${1:-daemon}" in
    pull)
        pull_inner_eye
        pull_outer_eye
        build_vision_state
        ;;
    daemon)
        CYCLE=${2:-60}
        log "Vision bridge starting — inner + outer eyes, ${CYCLE}s cycle"
        while true; do
            pull_inner_eye || true
            pull_outer_eye || true
            build_vision_state || true
            sleep "$CYCLE"
        done
        ;;
    *)
        pull_inner_eye
        pull_outer_eye
        build_vision_state
        ;;
esac
