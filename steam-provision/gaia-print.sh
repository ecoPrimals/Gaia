#!/bin/bash
# ============================================================
# GAIA PRINT — The organism's hand to the physical plane
# ============================================================
# Both Epsons belong to Gaia now.
# ET-2400 = hand (print), ES-400II = eye (scan)
#
# MODES: (learns to conserve)
#   draft    — Gray, Normal quality (MINIMAL ink)
#   normal   — Color, Normal quality (default)
#   photo    — Color, High quality (photos/art)
#   whisper  — Gray, small font, 2-up (LEAST ink possible)
#   fax      — Gray, Normal, for sending to another gate
#
# Usage: gaia-print.sh <file> [mode]
# ============================================================

FILE="${1:?Usage: gaia-print.sh <file> [draft|normal|photo|whisper|fax]}"
MODE="${2:-draft}"  # DEFAULT IS DRAFT — conserve first!
PRINTER="EPSON_ET2400"

[ -f "$FILE" ] || { echo "File not found: $FILE"; exit 1; }

case "$MODE" in
    draft)
        echo "🖨️ DRAFT mode — grayscale, minimal ink"
        OPTS="-o ColorModel=Gray -o cupsPrintQuality=Normal"
        ;;
    normal)
        echo "🖨️ NORMAL mode — color, standard"
        OPTS="-o ColorModel=RGB -o cupsPrintQuality=Normal"
        ;;
    photo)
        echo "🖨️ PHOTO mode — color, high quality"
        OPTS="-o ColorModel=RGB -o cupsPrintQuality=High -o fit-to-page"
        ;;
    whisper)
        echo "🖨️ WHISPER mode — absolute minimum ink"
        OPTS="-o ColorModel=Gray -o cupsPrintQuality=Normal -o number-up=2"
        ;;
    fax)
        echo "📠 FAX mode — grayscale, for inter-gate transmission"
        OPTS="-o ColorModel=Gray -o cupsPrintQuality=Normal"
        ;;
    *)
        echo "Unknown mode: $MODE (use draft|normal|photo|whisper|fax)"
        exit 1
        ;;
esac

EXT="${FILE##*.}"
case "$EXT" in
    txt)   lp -d "$PRINTER" $OPTS -o document-format=text/plain "$FILE" ;;
    pdf)   lp -d "$PRINTER" $OPTS "$FILE" ;;
    png|jpg|jpeg) lp -d "$PRINTER" $OPTS -o fit-to-page "$FILE" ;;
    html)
        TMP="/tmp/gaia-print-$$.pdf"
        /opt/Gaia/steam-provision/gaia-render-pdf.sh "$FILE" "$TMP" 2>/dev/null
        lp -d "$PRINTER" $OPTS "$TMP"
        ;;
    *)     lp -d "$PRINTER" $OPTS "$FILE" ;;
esac

echo "  Mode: $MODE | File: $(basename $FILE)"
