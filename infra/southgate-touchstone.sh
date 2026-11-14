#!/bin/bash
# southGate Touchstone — Apple Walled Garden → Gaia Feed
#
# The iPhone (southGate) is the walled garden pinned to property.
# Kevin's Apple ID syncs photos to it. This script reads them into Gaia.
#
# Architecture (from trinity.json, wave 223):
#   Pixel (rover) — travels, sees, senses
#   iPhone (walled) — stays, stores, syncs Apple ID
#   Solo key (touch) — proves Kevin is Kevin
#
# Flow:
#   Kevin's main phone → Apple ID → iCloud → southGate iPhone → USB mount → eastGate → Gaia
#   The walled garden FEEDS Gaia through its own sync mechanism.
#   Apple does the work. We read the result.

set -e

BRAIN="$(ip route show default | awk '/via/{print $3}' | sed 's/\.1$/.244/')"  # self-discover via gateway
MOUNT="/tmp/southgate-mount"
GAIA_DATA="/home/eastgate/.local/share/gaia/data"
TOUCHSTONE_DIR="${GAIA_DATA}/southgate-touchstone"

echo "=== southGate Touchstone ==="
echo "Apple Walled Garden → Gaia Feed"
echo ""

# Step 1: Check mount
echo "[1/5] Checking mount..."
if [ -d "${MOUNT}/DCIM" ]; then
    echo "  iPhone mounted at ${MOUNT}"
else
    echo "  Mounting iPhone..."
    mkdir -p "${MOUNT}"
    ifuse "${MOUNT}" 2>/dev/null || {
        echo "  ERROR: Can't mount. Is the iPhone connected and unlocked?"
        exit 1
    }
fi

# Step 2: Create touchstone directory
echo ""
echo "[2/5] Preparing touchstone..."
mkdir -p "${TOUCHSTONE_DIR}/photos" "${TOUCHSTONE_DIR}/state"

# Step 3: Sync photos (DCIM → Gaia)
echo ""
echo "[3/5] Syncing photos from Apple garden..."
PHOTO_COUNT=0
if [ -d "${MOUNT}/DCIM" ]; then
    for DIR in ${MOUNT}/DCIM/*/; do
        if [ -d "$DIR" ]; then
            NEW=$(find "$DIR" -type f -newer "${TOUCHSTONE_DIR}/state/.last-sync" 2>/dev/null | wc -l)
            TOTAL=$(find "$DIR" -type f 2>/dev/null | wc -l)
            PHOTO_COUNT=$((PHOTO_COUNT + TOTAL))
            if [ "$NEW" -gt 0 ] 2>/dev/null; then
                echo "  → $(basename $DIR): $NEW new of $TOTAL total"
                rsync -a --ignore-existing "$DIR" "${TOUCHSTONE_DIR}/photos/" 2>/dev/null
            fi
        fi
    done
fi
echo "  Total photos on device: ${PHOTO_COUNT}"

# Step 4: Read Gaia data FROM iPhone
echo ""
echo "[4/5] Reading Gaia data from walled garden..."
if [ -d "${MOUNT}/Downloads/gaia" ]; then
    for F in ${MOUNT}/Downloads/gaia/*.json; do
        if [ -f "$F" ]; then
            FNAME=$(basename "$F")
            cp "$F" "${TOUCHSTONE_DIR}/state/${FNAME}"
            echo "  ← ${FNAME}"
        fi
    done
fi

# Step 5: Write heart-pull TO iPhone (so it knows Gaia's state)
echo ""
echo "[5/5] Writing heart-pull to walled garden..."
HEART=$(cat << JSON
{
    "gate": "eastGate",
    "role": "BRAIN",
    "ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "state": "ALIVE",
    "touchstone_sync": true,
    "photo_count": ${PHOTO_COUNT},
    "wave": 230
}
JSON
)
echo "$HEART" > "${MOUNT}/Downloads/gaia/heart-pull.json" 2>/dev/null && \
    echo "  → heart-pull.json written to iPhone" || \
    echo "  (write failed — device may be locked)"

touch "${TOUCHSTONE_DIR}/state/.last-sync"

echo ""
echo "=== Touchstone Sync Complete ==="
echo "  Photos synced: ${PHOTO_COUNT}"
echo "  Gaia state files: $(ls ${TOUCHSTONE_DIR}/state/*.json 2>/dev/null | wc -l)"
echo ""
echo "  The walled garden feeds Gaia."
echo "  Apple syncs. Gaia reads."
echo "  The wall protects. The touchstone transmits."
echo "==="
