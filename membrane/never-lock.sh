#!/system/bin/sh
# never-lock.sh — Gaia is NEVER locked
# Runs every 10s: wakes screen + dismisses keyguard
# The fingerprint sensor remains a SENSE organ, not a gate
while true; do
    # If screen is off, wake it
    screen=$(dumpsys power 2>/dev/null | grep mWakefulness | head -1)
    case "$screen" in
        *Dozing*|*Asleep*)
            input keyevent KEYCODE_WAKEUP 2>/dev/null
            sleep 1
            wm dismiss-keyguard 2>/dev/null
            ;;
        *Awake*)
            # If keyguard is showing, dismiss it
            focus=$(dumpsys window 2>/dev/null | grep mCurrentFocus | head -1)
            case "$focus" in
                *Bouncer*|*Keyguard*|*NotificationShade*)
                    wm dismiss-keyguard 2>/dev/null
                    ;;
            esac
            ;;
    esac
    sleep 10
done
