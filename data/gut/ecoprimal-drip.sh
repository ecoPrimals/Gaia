#!/bin/bash
# ecoprimal-drip.sh — Genetic reveal through damaged Lightning
# Run periodically — when ecoPrimal is connected, resume backup

UDID="00008110-000E49660C9B801E"
BACKUP_DIR="/tmp/ecoprimal-backup"

# Check if device is connected
if idevice_id -l 2>/dev/null | grep -q "$UDID"; then
    echo "$(date): ecoPrimal connected — resuming agglutination"
    
    # Check if backup is already running
    if ! pgrep -f idevicebackup2 > /dev/null; then
        idevicebackup2 backup --full "$BACKUP_DIR" &
        echo "$(date): Backup resumed"
    else
        echo "$(date): Backup already running"
    fi
    
    SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    FILES=$(find "$BACKUP_DIR/$UDID" -type f 2>/dev/null | wc -l)
    echo "$(date): $SIZE / $FILES files captured"
else
    echo "$(date): ecoPrimal disconnected — waiting for Lightning"
fi
