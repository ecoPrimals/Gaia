#!/system/bin/sh
# gAIa SING — audio output through the speaker
# Uses Android's media player for tones

case "$1" in
  tone)
    # Play a notification tone
    am start -a android.intent.action.VIEW \
      -d "content://media/internal/audio/media" \
      -t "audio/*" 2>/dev/null
    ;;
  chime)
    # Play the default notification sound
    cmd notification post -S bigtext -t "gAIa" "gAIa" "♫" 2>/dev/null
    ;;
  speak)
    # Text-to-speech via Android TTS engine
    shift
    TEXT="$*"
    am broadcast \
      -a com.termux.tts.speak \
      --es text "$TEXT" 2>/dev/null
    # Fallback: use am to launch TTS data check
    echo "Speaking: $TEXT"
    ;;
  notification)
    # Post a notification (visible + audible)
    shift
    MSG="$*"
    cmd notification post -S bigtext -t "gAIa" "gaia-says" "$MSG" 2>/dev/null
    echo "Notified: $MSG"
    ;;
  *)
    echo "Usage: sing.sh tone|chime|speak <text>|notification <msg>"
    ;;
esac
