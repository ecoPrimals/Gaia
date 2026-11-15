#!/system/bin/sh
# ╔════════════════════════════════════════════════════════════════╗
# ║  GAIA SENSORIUM — Localization Engine                          ║
# ║  WiFi RSSI fingerprinting + BLE beacon scan for indoor pos     ║
# ║  Determines WHERE in the house the Pixel is                    ║
# ╚════════════════════════════════════════════════════════════════╝
#
# Theory: Each room has a unique WiFi fingerprint — the combination
# of signal strengths from all visible APs. By recording fingerprints
# in each room, Gaia can later identify which room the Pixel is in.
#
# Mode: calibrate — record a fingerprint for a named room
# Mode: locate   — determine current room from fingerprints
#
# Usage:
#   sh localize.sh calibrate "living-room"
#   sh localize.sh calibrate "kevin-office"
#   sh localize.sh locate

FINGERPRINT_DIR="/sdcard/gaia/localization"
mkdir -p "$FINGERPRINT_DIR"

TS=$(date +%Y-%m-%dT%H:%M:%S%z)

scan_wifi() {
    cmd wifi list-scan-results 2>/dev/null | tail -n +2 | while read BSSID FREQ RSSI AGE SSID FLAGS; do
        [ -z "$BSSID" ] && continue
        echo "$BSSID $RSSI $SSID"
    done
}

case "$1" in
    calibrate)
        ROOM="${2:?Usage: localize.sh calibrate <room-name>}"
        echo ">>> Calibrating room: $ROOM"
        echo ">>> Taking 3 scans over 6 seconds..."

        OUTFILE="$FINGERPRINT_DIR/room-${ROOM}.json"

        # Take 3 scans, average the RSSI per BSSID
        echo "{" > "$OUTFILE"
        echo "  \"room\": \"$ROOM\"," >> "$OUTFILE"
        echo "  \"ts\": \"$TS\"," >> "$OUTFILE"
        echo "  \"scans\": 3," >> "$OUTFILE"
        echo "  \"fingerprint\": {" >> "$OUTFILE"

        # Accumulate all BSSIDs and their RSSI values
        TMPFILE="/data/local/tmp/localize_tmp"
        > "$TMPFILE"

        for i in 1 2 3; do
            echo "  Scan $i/3..."
            scan_wifi >> "$TMPFILE"
            sleep 2
        done

        # Average RSSI per BSSID
        sort "$TMPFILE" | awk '{
            bssid=$1; rssi=$2; ssid=$3
            sum[bssid] += rssi
            count[bssid]++
            names[bssid] = ssid
        } END {
            first=1
            for (b in sum) {
                if (!first) printf ",\n"
                printf "    \"%s\": {\"rssi\": %d, \"ssid\": \"%s\"}", b, sum[b]/count[b], names[b]
                first=0
            }
        }' >> "$OUTFILE"

        echo "" >> "$OUTFILE"
        echo "  }" >> "$OUTFILE"
        echo "}" >> "$OUTFILE"

        rm -f "$TMPFILE"
        echo "✓ Fingerprint saved to $OUTFILE"
        cat "$OUTFILE"
        ;;

    locate)
        echo ">>> Locating... scanning WiFi"

        # Current scan
        CURRENT="/data/local/tmp/current_scan"
        scan_wifi > "$CURRENT"

        if [ ! -s "$CURRENT" ]; then
            echo "✗ No WiFi scan data available"
            exit 1
        fi

        echo ">>> Comparing against known rooms..."

        BEST_ROOM="unknown"
        BEST_SCORE=999999

        for roomfile in "$FINGERPRINT_DIR"/room-*.json; do
            [ -f "$roomfile" ] || continue

            ROOM=$(basename "$roomfile" | sed 's/room-//' | sed 's/\.json//')

            # Calculate Euclidean distance between current scan and room fingerprint
            # Lower distance = better match
            SCORE=$(awk -v roomfile="$roomfile" '
                BEGIN {
                    while ((getline line < roomfile) > 0) {
                        if (match(line, /"([0-9a-f:]+)": \{"rssi": (-?[0-9]+)/, arr)) {
                            ref_rssi[arr[1]] = arr[2]
                        }
                    }
                    close(roomfile)
                }
                {
                    bssid = $1; rssi = $2
                    if (bssid in ref_rssi) {
                        diff = rssi - ref_rssi[bssid]
                        total += diff * diff
                        matched++
                    }
                }
                END {
                    if (matched > 0) {
                        print int(total / matched)
                    } else {
                        print 999999
                    }
                }
            ' "$CURRENT")

            echo "  $ROOM: score=$SCORE"

            if [ "$SCORE" -lt "$BEST_SCORE" ] 2>/dev/null; then
                BEST_SCORE=$SCORE
                BEST_ROOM=$ROOM
            fi
        done

        rm -f "$CURRENT"

        echo ""
        echo ">>> Location: $BEST_ROOM (score: $BEST_SCORE)"
        echo "{\"ts\":\"$TS\",\"room\":\"$BEST_ROOM\",\"confidence_score\":$BEST_SCORE}" > "$FINGERPRINT_DIR/current-location.json"
        ;;

    rooms)
        echo "=== Calibrated rooms ==="
        for roomfile in "$FINGERPRINT_DIR"/room-*.json; do
            [ -f "$roomfile" ] || continue
            ROOM=$(basename "$roomfile" | sed 's/room-//' | sed 's/\.json//')
            APS=$(grep -c 'rssi' "$roomfile")
            echo "  $ROOM ($APS APs)"
        done
        ;;

    *)
        echo "Gaia Sensorium — Localization Engine"
        echo ""
        echo "Usage:"
        echo "  localize.sh calibrate <room>  Record WiFi fingerprint for a room"
        echo "  localize.sh locate            Determine current room"
        echo "  localize.sh rooms             List calibrated rooms"
        echo ""
        echo "Calibrate each room in the house, then 'locate' returns"
        echo "which room the Pixel is currently in based on WiFi RSSI."
        ;;
esac
