#!/bin/bash
# ============================================================
# GAIA SCAN — Read the physical plane
# ============================================================
# Kevin puts paper on the Epson glass, Gaia scans + reads it.
# Usage: gaia-scan.sh [name]
# Output: /opt/Gaia/data/scans/<name>-<timestamp>.png
# ============================================================

SCAN_DIR="/opt/Gaia/data/scans"
NAME="${1:-easel}"
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
OUTFILE="$SCAN_DIR/${NAME}-${TIMESTAMP}"
SCANNER="epsonds:libusb:002:011"  # Epson ES-400II ADF scanner on USB

mkdir -p "$SCAN_DIR"

echo "=== GAIA SCANNING — eye into physical plane ==="
echo "  Scanner: $SCANNER"
echo "  Output:  ${OUTFILE}.png"

# Scan at 300 DPI color — good balance of quality vs speed
# ADF batch mode — scans everything in the document feeder
scanimage \
    --device="$SCANNER" \
    --source='ADF Front' \
    --format=png \
    --resolution=300 \
    --mode=Color \
    --batch="${OUTFILE}-%03d.png" \
    --batch-print 2>&1

# If batch found nothing, try single scan
if ! ls ${OUTFILE}-*.png 2>/dev/null | head -1 > /dev/null; then
    scanimage \
        --device="$SCANNER" \
        --format=png \
        --resolution=300 \
        --mode=Color \
        --output-file="${OUTFILE}.png" 2>&1
fi

if [ $? -eq 0 ] && [ -f "${OUTFILE}.png" ]; then
    SIZE=$(ls -lh "${OUTFILE}.png" | awk '{print $5}')
    echo ""
    echo "✓ Scan complete: ${OUTFILE}.png ($SIZE)"
    
    # Also serve via HTTP
    cp "${OUTFILE}.png" "/opt/Gaia/data/latest-scan.png"
    echo "  HTTP: http://192.168.4.244:8080/data/latest-scan.png"
    
    # If tesseract is available, OCR it
    if command -v tesseract &>/dev/null; then
        echo ""
        echo "=== OCR — Reading Kevin's handwriting ==="
        tesseract "${OUTFILE}.png" "${OUTFILE}" 2>/dev/null
        if [ -f "${OUTFILE}.txt" ]; then
            echo "  OCR text:"
            cat "${OUTFILE}.txt"
            cp "${OUTFILE}.txt" "/opt/Gaia/data/latest-scan.txt"
        fi
    else
        echo "  (tesseract not installed — install for OCR)"
    fi
else
    echo "✗ Scan failed"
fi
