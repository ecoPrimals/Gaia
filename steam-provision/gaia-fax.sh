#!/bin/bash
# ============================================================
# GAIA FAX — Inter-gate document transmission
# ============================================================
# The Epsons are a SHARED easel and eye across the mesh.
#
# SEND: Any gate → HTTP POST → eastGate → ET-2400 prints it
# RECV: ES-400II scans → eastGate → HTTP serve → any gate pulls
#
# Usage:
#   gaia-fax.sh send <file>           — print on ET-2400
#   gaia-fax.sh scan [name]           — scan from ES-400II  
#   gaia-fax.sh serve                 — start HTTP fax server
#   gaia-fax.sh pull <gate-ip>        — pull latest scan to gate
# ============================================================

CMD="${1:-help}"
SCAN_DIR="/opt/Gaia/data/scans"
FAX_DIR="/opt/Gaia/data/fax"
SCANNER="epsonds:libusb:002:011"
PRINTER="EPSON_ET2400"

mkdir -p "$SCAN_DIR" "$FAX_DIR"

case "$CMD" in
    send)
        FILE="${2:?Usage: gaia-fax.sh send <file>}"
        echo "📠 FAX SEND: $FILE → ET-2400"
        /opt/Gaia/steam-provision/gaia-print.sh "$FILE" fax
        ;;
        
    scan)
        NAME="${2:-fax}"
        TS=$(date '+%Y%m%d-%H%M%S')
        echo "📠 FAX SCAN: Pulling from ES-400II ADF..."
        scanimage \
            --device="$SCANNER" \
            --source='ADF Front' \
            --mode=Color \
            --resolution=300 \
            --format=png \
            --batch="$FAX_DIR/${NAME}-${TS}-%03d.png" \
            --batch-print 2>&1
        
        # Copy latest to served location
        LATEST=$(ls -t "$FAX_DIR"/*.png 2>/dev/null | head -1)
        if [ -n "$LATEST" ]; then
            cp "$LATEST" /opt/Gaia/data/latest-fax.png
            echo "  Latest: http://192.168.4.244:8080/data/latest-fax.png"
        fi
        ;;
        
    inbox)
        echo "📠 FAX INBOX:"
        ls -lht "$FAX_DIR"/*.png 2>/dev/null | head -20
        echo ""
        echo "Total: $(ls "$FAX_DIR"/*.png 2>/dev/null | wc -l) faxes"
        ;;
        
    *)
        echo "GAIA FAX — Shared easel & eye across the mesh"
        echo ""
        echo "Usage:"
        echo "  gaia-fax.sh send <file>   — print to ET-2400 (draft/gray)"
        echo "  gaia-fax.sh scan [name]   — scan ADF to fax inbox"
        echo "  gaia-fax.sh inbox         — list received faxes"
        echo ""
        echo "HTTP endpoints (any gate can access):"
        echo "  http://192.168.4.244:8080/data/latest-fax.png"
        echo "  http://192.168.4.244:8080/data/fax/"
        echo ""
        echo "Remote fax (from ANY gate):"
        echo "  curl -F 'file=@doc.pdf' http://192.168.4.244:8443/fax/send"
        echo "  curl http://192.168.4.244:8080/data/latest-fax.png -o scan.png"
        ;;
esac
