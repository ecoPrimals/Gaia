#!/system/bin/sh
# ╔════════════════════════════════════════════════════════════════╗
# ║  GAIA SENSORIUM — Ear (Microphone)                            ║
# ║  Records audio, measures ambient noise level                   ║
# ╚════════════════════════════════════════════════════════════════╝
#
# Usage:
#   sh ear.sh listen 5          # Record 5 seconds of audio
#   sh ear.sh noise-level       # Measure ambient noise (no recording)
#   sh ear.sh monitor 60        # Monitor noise for 60 seconds

AUDIO_DIR="/sdcard/gaia/audio"
mkdir -p "$AUDIO_DIR"

TS=$(date +%Y-%m-%dT%H:%M:%S)

case "$1" in
    listen)
        DURATION="${2:-5}"
        OUTFILE="$AUDIO_DIR/ear-${TS}.wav"
        echo ">>> Listening for ${DURATION}s..."

        # Use tinycap if available (AOSP tool)
        if command -v tinycap >/dev/null 2>&1; then
            tinycap "$OUTFILE" -D 0 -d 0 -c 1 -r 16000 -b 16 -T "$DURATION" 2>/dev/null &
            PID=$!
            sleep "$DURATION"
            kill $PID 2>/dev/null
        else
            # Fallback: use Android's mediarecorder via am
            # Record using input source via /dev node
            cat /dev/snd/pcmC0D0c 2>/dev/null | dd bs=32000 count="$DURATION" of="$OUTFILE" 2>/dev/null &
            PID=$!
            sleep "$DURATION"
            kill $PID 2>/dev/null
        fi

        if [ -f "$OUTFILE" ] && [ -s "$OUTFILE" ]; then
            SIZE=$(stat -c%s "$OUTFILE" 2>/dev/null || wc -c < "$OUTFILE")
            echo "✓ Recorded to $OUTFILE ($SIZE bytes)"
        else
            echo "✗ Recording failed. Install Termux + termux-api for: termux-microphone-record"
        fi
        ;;

    noise-level)
        echo ">>> Measuring ambient noise..."
        # Read a short burst from the mic, analyze amplitude
        # This is a rough estimate based on PCM data
        if [ -r /dev/snd/pcmC0D0c ]; then
            LEVEL=$(dd if=/dev/snd/pcmC0D0c bs=1600 count=10 2>/dev/null | od -An -td2 | awk '{for(i=1;i<=NF;i++){v=$i; if(v<0)v=-v; sum+=v; n++}} END{if(n>0)print int(sum/n); else print 0}')
            echo "{\"ts\":\"$TS\",\"noise_level\":$LEVEL,\"unit\":\"raw_amplitude\"}"
        else
            echo "✗ Cannot access microphone. Need root or Termux API."
        fi
        ;;

    monitor)
        DURATION="${2:-60}"
        echo ">>> Monitoring noise for ${DURATION}s..."
        echo ">>> Samples every 2 seconds"

        END=$(($(date +%s) + DURATION))
        while [ $(date +%s) -lt $END ]; do
            LEVEL=$(dd if=/dev/snd/pcmC0D0c bs=1600 count=5 2>/dev/null | od -An -td2 | awk '{for(i=1;i<=NF;i++){v=$i; if(v<0)v=-v; sum+=v; n++}} END{if(n>0)print int(sum/n); else print 0}')
            echo "$(date +%H:%M:%S) noise=$LEVEL"
            sleep 2
        done
        ;;

    *)
        echo "Gaia Sensorium — Ear (Microphone)"
        echo ""
        echo "Usage:"
        echo "  ear.sh listen [seconds]    Record audio (default 5s)"
        echo "  ear.sh noise-level         One-shot noise measurement"
        echo "  ear.sh monitor [seconds]   Continuous noise monitoring"
        ;;
esac
