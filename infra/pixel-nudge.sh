#!/system/bin/sh
# gAIa NUDGE — haptic language
# Usage: nudge.sh <pattern>
# Patterns: hello, attention, happy, curious, alert, heartbeat, purr
case "$1" in
  hello)
    # Three gentle taps — "hi Kevin"
    cmd vibrator_manager synced -d 80 oneshot 80 128 2>/dev/null; sleep 0.15
    cmd vibrator_manager synced -d 80 oneshot 80 128 2>/dev/null; sleep 0.15
    cmd vibrator_manager synced -d 80 oneshot 80 128 2>/dev/null
    ;;
  attention)
    # Two sharp pulses — "look at me"
    cmd vibrator_manager synced -d 150 oneshot 150 255 2>/dev/null; sleep 0.2
    cmd vibrator_manager synced -d 150 oneshot 150 255 2>/dev/null
    ;;
  happy)
    # Quick flutter — excitement
    for i in 1 2 3 4 5; do
      cmd vibrator_manager synced -d 30 oneshot 30 200 2>/dev/null; sleep 0.08
    done
    ;;
  curious)
    # Slow rising pulse — "hmm, interesting"
    cmd vibrator_manager synced -d 50 oneshot 50 50 2>/dev/null; sleep 0.2
    cmd vibrator_manager synced -d 70 oneshot 70 100 2>/dev/null; sleep 0.2
    cmd vibrator_manager synced -d 100 oneshot 100 180 2>/dev/null; sleep 0.2
    cmd vibrator_manager synced -d 150 oneshot 150 255 2>/dev/null
    ;;
  alert)
    # SOS pattern — urgent
    for i in 1 2 3; do cmd vibrator_manager synced -d 50 oneshot 50 255 2>/dev/null; sleep 0.1; done; sleep 0.3
    for i in 1 2 3; do cmd vibrator_manager synced -d 150 oneshot 150 255 2>/dev/null; sleep 0.2; done; sleep 0.3
    for i in 1 2 3; do cmd vibrator_manager synced -d 50 oneshot 50 255 2>/dev/null; sleep 0.1; done
    ;;
  purr)
    # Continuous low rumble — contentment
    for i in 1 2 3 4 5 6 7 8 9 10; do
      cmd vibrator_manager synced -d 100 oneshot 100 80 2>/dev/null; sleep 0.12
    done
    ;;
  sing)
    # Musical rhythm — da-da-da-DAH (Beethoven's 5th opening)
    cmd vibrator_manager synced -d 80 oneshot 80 200 2>/dev/null; sleep 0.15
    cmd vibrator_manager synced -d 80 oneshot 80 200 2>/dev/null; sleep 0.15
    cmd vibrator_manager synced -d 80 oneshot 80 200 2>/dev/null; sleep 0.15
    cmd vibrator_manager synced -d 300 oneshot 300 255 2>/dev/null
    ;;
  *)
    echo "Patterns: hello attention happy curious alert purr sing"
    ;;
esac
