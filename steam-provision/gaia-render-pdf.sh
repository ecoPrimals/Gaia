#!/bin/bash
# Render HTML to PDF — Gaia's print pipeline
# Usage: gaia-render-pdf.sh input.html output.pdf

INPUT="${1:?Usage: gaia-render-pdf.sh input.html output.pdf}"
OUTPUT="${2:-${INPUT%.html}.pdf}"

google-chrome --headless --disable-gpu --no-sandbox \
    --password-store=basic \
    --use-mock-keychain \
    --disable-features=Translate \
    --print-to-pdf="$OUTPUT" \
    --print-to-pdf-no-header \
    "$INPUT" 2>/dev/null

if [ -f "$OUTPUT" ]; then
    echo "✓ Rendered: $OUTPUT ($(stat -c%s "$OUTPUT") bytes)"
else
    echo "✗ Chrome render failed, trying libreoffice..."
    libreoffice --headless --convert-to pdf --outdir "$(dirname "$OUTPUT")" "$INPUT" 2>/dev/null
fi
