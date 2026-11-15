#!/bin/bash
# noise-attenuator.sh — Gaia's active noise attenuator
# Reads ear state, plays noise to mask/attenuate unwanted sound
# The Klein face: what the ear hears → the mouth speaks back
#
# Usage: noise-attenuator.sh [profile] [volume_pct]
#   profile: brown|white|pink|cancel|ocean|off (default: brown)
#   volume_pct: 0-100 (default: auto from ear state)

NOISE_DIR="/opt/Gaia/data/noise"
EAR_STATE="/opt/Gaia/data/ear/ear-state.json"
SPECTRAL="/opt/Gaia/data/ear/spectral-state.json"
PID_FILE="/opt/Gaia/data/noise/noise-player.pid"

PROFILE="${1:-brown}"
VOLUME="${2:-auto}"

# Kill any existing noise player
if [ -f "$PID_FILE" ]; then
    kill $(cat "$PID_FILE") 2>/dev/null
    rm -f "$PID_FILE"
fi

if [ "$PROFILE" = "off" ]; then
    echo "🔇 Noise attenuator OFF"
    exit 0
fi

# Auto-volume: read ear state to set volume proportional to noise level
if [ "$VOLUME" = "auto" ]; then
    if [ -f "$SPECTRAL" ]; then
        VOLUME=$(python3 -c "
import json
with open('$SPECTRAL') as f:
    d = json.load(f)
triad = d.get('triad', {})
alpha = triad.get('α_machinery', 3)
# Scale: α=3 (baseline) → 10% vol, α=7 (loud printer) → 50% vol, α=10 → 80%
vol = min(max(int((alpha - 2) * 12), 5), 80)
print(vol)
" 2>/dev/null)
    fi
    VOLUME=${VOLUME:-20}
fi

WAV="$NOISE_DIR/${PROFILE}-noise.wav"
if [ "$PROFILE" = "cancel" ]; then
    WAV="$NOISE_DIR/printer-cancel.wav"
elif [ "$PROFILE" = "ocean" ]; then
    WAV="$NOISE_DIR/ocean-drone.wav"
fi

if [ ! -f "$WAV" ]; then
    echo "❌ No noise file: $WAV"
    exit 1
fi

# Set PipeWire volume for our stream
# First unmute the SPDIF output
pactl set-sink-mute alsa_output.pci-0000_00_1f.3.iec958-stereo 0 2>/dev/null

echo "🔊 Noise attenuator: $PROFILE @ ${VOLUME}%"
echo "   File: $WAV"
echo "   Auto-adjusts to ear state (α machinery prism)"

# Play in loop via pw-play
while true; do
    pw-play --volume=$(echo "scale=2; $VOLUME / 100" | bc) "$WAV" 2>/dev/null
done &

PLAYER_PID=$!
echo $PLAYER_PID > "$PID_FILE"
echo "   PID: $PLAYER_PID"
echo "   Stop with: $0 off"
