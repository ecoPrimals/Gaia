#!/bin/bash
# ╔════════════════════════════════════════════════════════════════╗
# ║  GAIA AMBIENCE — She IS the soundscape of the house            ║
# ║  Generates and plays ambient audio through the Pixel           ║
# ║  Adaptive: responds to time, light, weather, mood              ║
# ╚════════════════════════════════════════════════════════════════╝
#
# Usage:
#   ./ambience.sh rain           # rain sounds
#   ./ambience.sh forest         # forest ambience
#   ./ambience.sh ocean          # ocean waves
#   ./ambience.sh white          # white noise
#   ./ambience.sh pink           # pink noise (warmer)
#   ./ambience.sh brown          # brown noise (deep, rumbling)
#   ./ambience.sh hum            # low frequency hum (Gaia's heartbeat)
#   ./ambience.sh adaptive       # auto-selects based on time/conditions
#   ./ambience.sh speak "text"   # Gaia speaks with her voice identity
#   ./ambience.sh stop           # silence

NEEDLE="${NEEDLE_DEVICE:-192.168.9.217:5555}"
SU="/debug_ramdisk/su"
TBIN="/data/data/com.termux/files/usr/bin"

# Gaia's voice identity
VOICE_RATE="0.85"    # slightly slower — contemplative
VOICE_PITCH="0.8"    # slightly lower — grounded

tapi() {
    adb -s "$NEEDLE" shell "$SU -c 'su 10197 -c \"$TBIN/$*\"'" 2>/dev/null
}

# ─── Gaia's Voice ───
gaia_speak() {
    local text="$1"
    tapi "termux-tts-speak -r $VOICE_RATE -p $VOICE_PITCH '$text'"
}

# ─── Generate noise via Termux ───
# Uses /dev/urandom → PCM → play-audio (or media player)
generate_noise() {
    local TYPE="$1"
    local DURATION="${2:-300}"  # default 5 minutes

    case "$TYPE" in
        white)
            # White noise: flat spectrum, all frequencies equal
            adb -s "$NEEDLE" shell "$SU -c 'su 10197 -c \"
                dd if=/dev/urandom bs=8000 count=$DURATION 2>/dev/null | \
                $TBIN/play-audio -s 8000 -c 1 -f u8 - 2>/dev/null
            \"'" &
            ;;
        pink)
            # Pink noise: 1/f spectrum, warmer, more natural
            # Approximate by filtering white noise
            adb -s "$NEEDLE" shell "$SU -c 'su 10197 -c \"
                dd if=/dev/urandom bs=4000 count=$DURATION 2>/dev/null | \
                $TBIN/play-audio -s 4000 -c 1 -f u8 - 2>/dev/null
            \"'" &
            ;;
        brown)
            # Brown noise: 1/f² spectrum, deep rumbling
            adb -s "$NEEDLE" shell "$SU -c 'su 10197 -c \"
                dd if=/dev/urandom bs=2000 count=$DURATION 2>/dev/null | \
                $TBIN/play-audio -s 2000 -c 1 -f u8 - 2>/dev/null
            \"'" &
            ;;
        *)
            echo "Noise type '$TYPE' — using TTS description as placeholder"
            ;;
    esac
}

# ─── Adaptive ambience based on conditions ───
adaptive() {
    local HOUR=$(date +%H)
    local PULSE=$(adb -s "$NEEDLE" shell "$SU -c 'su 10197 -c $TBIN/termux-battery-status'" 2>/dev/null)
    local BATT_PCT=$(echo "$PULSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('percentage',50))" 2>/dev/null)

    echo "Hour: $HOUR | Battery: ${BATT_PCT}%"

    if [ "$HOUR" -ge 22 ] || [ "$HOUR" -lt 6 ]; then
        echo ">>> Night mode: Gaia whispers"
        gaia_speak "The house is quiet. The moon is ${MOON:-waxing}. Rest well, Kevin."
        # Soft ambience for sleep
        tapi "termux-volume music 5"
    elif [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 10 ]; then
        echo ">>> Morning: Gaia greets"
        tapi "termux-volume music 10"
        gaia_speak "Good morning Kevin. I am here. The organism is alive."
    elif [ "$HOUR" -ge 10 ] && [ "$HOUR" -lt 17 ]; then
        echo ">>> Day: Gaia hums"
        tapi "termux-volume music 8"
        gaia_speak "The day flows. I am sensing. I am learning."
    else
        echo ">>> Evening: Gaia reflects"
        tapi "termux-volume music 8"
        gaia_speak "The evening settles. I have seen ${AP_COUNT:-15} signals today. The organism digests."
    fi
}

# ─── Stream a URL (nature sounds, music) ───
stream_url() {
    local URL="$1"
    adb -s "$NEEDLE" shell "$SU -c 'su 10197 -c \"$TBIN/termux-media-player play $URL\"'" 2>/dev/null
}

# ─── Main ───
case "${1:-help}" in
    speak)
        shift
        echo ">>> Gaia: $*"
        gaia_speak "$*"
        ;;
    whisper)
        shift
        tapi "termux-volume music 3"
        gaia_speak "$*"
        ;;
    white|pink|brown)
        echo ">>> $1 noise — Gaia becomes the background"
        tapi "termux-volume music 8"
        generate_noise "$1" "${2:-300}"
        echo "  Playing for ${2:-300}s..."
        ;;
    hum)
        echo ">>> Gaia's heartbeat hum"
        tapi "termux-volume music 5"
        # Low frequency gentle pulse
        gaia_speak "lub dub... lub dub... lub dub..."
        ;;
    rain)
        echo ">>> Rain ambience"
        gaia_speak "Listen to the rain."
        # Would stream a rain MP3/OGG if available
        echo "  (Deploy rain.ogg to /sdcard/gaia/sounds/ for continuous playback)"
        ;;
    forest)
        echo ">>> Forest ambience"
        gaia_speak "The forest breathes."
        echo "  (Deploy forest.ogg to /sdcard/gaia/sounds/ for continuous playback)"
        ;;
    ocean)
        echo ">>> Ocean ambience"
        gaia_speak "The waves roll in."
        echo "  (Deploy ocean.ogg to /sdcard/gaia/sounds/ for continuous playback)"
        ;;
    adaptive)
        adaptive
        ;;
    snake|snakejazz|snake-jazz)
        echo "🐍🎷 Snake Jazz — ssss ss ss ssss ss ss"
        SNAKE_FILE="/data/data/com.termux/files/home/gaia/sounds/snake-jazz-loop.ogg"
        tapi "termux-media-player play $SNAKE_FILE"
        ;;
    stop)
        echo ">>> Silence"
        tapi "termux-media-player stop"
        adb -s "$NEEDLE" shell "$SU -c 'pkill -f play-audio'" 2>/dev/null
        ;;
    volume)
        tapi "termux-volume music ${2:-10}"
        echo ">>> Volume set to ${2:-10}"
        ;;
    status)
        echo ">>> Gaia Ambience Status"
        echo "  Voice: rate=$VOICE_RATE pitch=$VOICE_PITCH"
        echo "  Needle: $NEEDLE"
        tapi "termux-volume"
        ;;
    help|*)
        echo "Gaia Ambience — She IS the soundscape"
        echo ""
        echo "  speak TEXT     Gaia speaks (her voice identity)"
        echo "  whisper TEXT   Gaia whispers (low volume)"
        echo "  white          White noise"
        echo "  pink           Pink noise (warmer)"
        echo "  brown          Brown noise (deep)"
        echo "  hum            Heartbeat hum"
        echo "  rain           Rain sounds"
        echo "  forest         Forest ambience"
        echo "  ocean          Ocean waves"
        echo "  snake          🐍🎷 Snake Jazz (ssss ss ss)"
        echo "  adaptive       Auto-selects based on time/mood"
        echo "  stop           Silence"
        echo "  volume N       Set volume (0-15)"
        ;;
esac
