#!/bin/bash
# SUPERSEDED by alphafold_bulk_download.py (async Python, systemd alphafold-bulk.service)
# Kept as fossil — bash+xargs prototype, no .prov_queue integration.
#
# AlphaFold DB — Full 214M+ structure bulk downloader (original bash version)
# Downloads every predicted structure CIF from the AlphaFold API
# Restart-safe: tracks completed accessions, skips already-downloaded files
#
# URL pattern: https://alphafold.ebi.ac.uk/files/AF-{ID}-F1-model_v6.cif
# Source manifest: accession_ids.csv (8.7 GB, ~217M entries)
# Estimated total: ~15 TB CIF data
# Estimated time: 5-10 days at 500 req/s

set -euo pipefail

DEST="/mnt/nestgate/cold/zfs/data/alphafold_structures"
ACCESSIONS="/mnt/nestgate/cold/zfs/data/alphafold/accession_ids.csv"
PROGRESS_FILE="$DEST/.progress"
LOG="/tmp/alphafold_bulk.log"
BASE_URL="https://alphafold.ebi.ac.uk/files"

PARALLEL_JOBS=200
BATCH_SIZE=10000
RATE_DELAY=0  # seconds between batches (0 = no delay, EBI handles it)

mkdir -p "$DEST"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') — $*" | tee -a "$LOG"; }

log "AlphaFold bulk structure download starting"

if [ ! -f "$ACCESSIONS" ]; then
    log "ERROR: accession_ids.csv not found at $ACCESSIONS"
    log "Downloading from EBI FTP..."
    rsync -av --progress --partial \
        "rsync://ftp.ebi.ac.uk/pub/databases/alphafold/accession_ids.csv" \
        "$ACCESSIONS" 2>&1 | tee -a "$LOG"
fi

TOTAL_ACCESSIONS=$(wc -l < "$ACCESSIONS")
log "Total accessions in manifest: $TOTAL_ACCESSIONS"

COMPLETED=0
if [ -f "$PROGRESS_FILE" ]; then
    COMPLETED=$(wc -l < "$PROGRESS_FILE")
    log "Resuming from checkpoint: $COMPLETED already completed"
fi

REMAINING=$((TOTAL_ACCESSIONS - COMPLETED))
log "Remaining to download: $REMAINING"

download_structure() {
    local LINE="$1"
    local UNIPROT_ID=$(echo "$LINE" | cut -d',' -f1)
    local AF_ID=$(echo "$LINE" | cut -d',' -f4)
    local VERSION=$(echo "$LINE" | cut -d',' -f5)

    # Organize into subdirectories by first 4 chars of accession for filesystem sanity
    # ~217M files / 65536 possible 4-char prefixes ≈ ~3300 files per dir
    local PREFIX="${UNIPROT_ID:0:2}"
    local SUBDIR="$DEST/$PREFIX"
    local OUTFILE="$SUBDIR/${AF_ID}-model_v${VERSION}.cif"

    if [ -f "$OUTFILE" ]; then
        return 0
    fi

    mkdir -p "$SUBDIR"

    if curl -sf -o "$OUTFILE" \
        "${BASE_URL}/${AF_ID}-model_v${VERSION}.cif" 2>/dev/null; then
        echo "$UNIPROT_ID" >> "$PROGRESS_FILE"
        return 0
    else
        rm -f "$OUTFILE"
        return 1
    fi
}
export -f download_structure
export DEST PROGRESS_FILE BASE_URL

# Skip already-completed lines and process in batches
SKIP_LINES=$COMPLETED
BATCH_NUM=0

log "Starting parallel downloads with $PARALLEL_JOBS workers"
log "Skipping first $SKIP_LINES completed entries"

tail -n +"$((SKIP_LINES + 1))" "$ACCESSIONS" | \
    xargs -P "$PARALLEL_JOBS" -L 1 -I {} bash -c 'download_structure "$@"' _ {} 2>>"$LOG" &

DOWNLOAD_PID=$!

# Progress reporting loop
while kill -0 $DOWNLOAD_PID 2>/dev/null; do
    sleep 300  # report every 5 minutes
    if [ -f "$PROGRESS_FILE" ]; then
        CURRENT=$(wc -l < "$PROGRESS_FILE")
        RATE=$(( (CURRENT - COMPLETED) * 12 ))  # per hour (every 5 min × 12)
        DISK=$(du -sh "$DEST" 2>/dev/null | cut -f1)
        log "Progress: $CURRENT / $TOTAL_ACCESSIONS ($DISK on disk, ~$RATE/hr)"
    fi
done

wait $DOWNLOAD_PID || true

FINAL=$(wc -l < "$PROGRESS_FILE" 2>/dev/null || echo 0)
FINAL_DISK=$(du -sh "$DEST" 2>/dev/null | cut -f1)
log "Download session complete: $FINAL / $TOTAL_ACCESSIONS structures ($FINAL_DISK)"
