#!/system/bin/sh
# ╔════════════════════════════════════════════════════════════════╗
# ║  GAIA SENSORIUM — Voice (Larynx)                              ║
# ║  Text-to-speech output — Gaia speaks through the Pixel        ║
# ╚════════════════════════════════════════════════════════════════╝
#
# Usage (on device, as root):
#   sh voice.sh "Hello Kevin"
#   sh voice.sh --volume 0.8 "The organism is healthy"
#
# Uses Android's built-in TTS engine via am broadcast

TEXT="${1:?Usage: voice.sh [--volume N] TEXT}"

# Handle volume flag
VOLUME=""
if [ "$1" = "--volume" ]; then
    VOLUME="$2"
    shift 2
    TEXT="$*"
fi

# Method 1: Use am to trigger TTS via broadcast
# This requires a small helper app or uses the accessibility TTS
am broadcast \
    -a android.intent.action.TTS_QUEUE_PROCESSING_COMPLETED \
    --es utteranceId "gaia-$(date +%s)" 2>/dev/null

# Method 2: Use cmd to invoke TTS directly (Android 12+)
# The media session approach
content call \
    --uri content://com.android.providers.media.documents/ \
    --method speak \
    --extra text:s:"$TEXT" 2>/dev/null

# Method 3: If Termux is installed, use termux-tts-speak
if command -v termux-tts-speak >/dev/null 2>&1; then
    echo "$TEXT" | termux-tts-speak
    exit 0
fi

# Method 4: Use media player to play a tone (fallback)
# Generate notification sound as acknowledgment
input keyevent KEYCODE_NOTIFICATION 2>/dev/null

echo "Voice: $TEXT"
echo "(Install Termux + termux-api for reliable TTS)"
