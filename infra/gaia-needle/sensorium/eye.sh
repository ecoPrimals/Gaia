#!/system/bin/sh
# ╔════════════════════════════════════════════════════════════════╗
# ║  GAIA SENSORIUM — Eye (Camera)                                ║
# ║  Captures photos, scans environment, reads QR codes            ║
# ╚════════════════════════════════════════════════════════════════╝
#
# Usage:
#   sh eye.sh snap              # Take a photo (rear camera)
#   sh eye.sh snap front        # Take a photo (front camera)
#   sh eye.sh timelapse 60 10   # 60 seconds, photo every 10s

PHOTO_DIR="/sdcard/gaia/photos"
mkdir -p "$PHOTO_DIR"

TS=$(date +%Y-%m-%dT%H:%M:%S)

case "$1" in
    snap)
        CAMERA="${2:-rear}"
        OUTFILE="$PHOTO_DIR/eye-${TS}-${CAMERA}.jpg"

        echo ">>> Capturing ($CAMERA camera)..."

        # Use Android camera intent via am
        if [ "$CAMERA" = "front" ]; then
            CAM_ID=1
        else
            CAM_ID=0
        fi

        # Method 1: screencap for screen capture
        if [ "$CAMERA" = "screen" ]; then
            screencap -p "$OUTFILE"
            echo "✓ Screenshot saved to $OUTFILE"
            exit 0
        fi

        # Method 2: Use am to trigger camera capture
        # This opens the camera app briefly
        am start -a android.media.action.STILL_IMAGE_CAMERA 2>/dev/null
        sleep 2
        # Capture via input event (simulate shutter)
        input keyevent KEYCODE_CAMERA 2>/dev/null
        sleep 2
        # Back out
        input keyevent KEYCODE_BACK 2>/dev/null

        # Find the most recent photo
        LATEST=$(ls -t /sdcard/DCIM/Camera/*.jpg 2>/dev/null | head -1)
        if [ -n "$LATEST" ]; then
            cp "$LATEST" "$OUTFILE"
            echo "✓ Photo saved to $OUTFILE"
        else
            echo "△ Camera triggered but photo not found in DCIM."
            echo "  For reliable camera: install Termux + termux-api"
            echo "  Then: termux-camera-photo -c $CAM_ID $OUTFILE"
        fi
        ;;

    screenshot)
        OUTFILE="$PHOTO_DIR/screen-${TS}.png"
        screencap -p "$OUTFILE"
        echo "✓ Screenshot: $OUTFILE"
        ;;

    timelapse)
        DURATION="${2:-60}"
        INTERVAL="${3:-10}"
        echo ">>> Timelapse: ${DURATION}s, photo every ${INTERVAL}s"

        END=$(($(date +%s) + DURATION))
        COUNT=0
        while [ $(date +%s) -lt $END ]; do
            OUTFILE="$PHOTO_DIR/timelapse-${TS}-$(printf '%04d' $COUNT).png"
            screencap -p "$OUTFILE" 2>/dev/null
            COUNT=$((COUNT + 1))
            echo "  Frame $COUNT saved"
            sleep "$INTERVAL"
        done
        echo "✓ Timelapse: $COUNT frames in $PHOTO_DIR"
        ;;

    *)
        echo "Gaia Sensorium — Eye (Camera)"
        echo ""
        echo "Usage:"
        echo "  eye.sh snap [rear|front|screen]  Capture photo"
        echo "  eye.sh screenshot                 Screen capture"
        echo "  eye.sh timelapse DURATION INTERVAL  Time-lapse"
        ;;
esac
