#!/bin/bash
# DEPRECATED: Superseded by native_braid.py inline braiding pipeline.
# Target replacement: nestGate content.mirror + membrane data.sync graph.
#
# Metered download queue — ONE download at a time, bandwidth-capped
# Prevents saturating the home internet connection
# Rate limit: 50 MB/s (~400 Mbps) leaves headroom for other devices
#
# Provenance is POST-DOWNLOAD: after each dataset downloads, revalidate_data.py
# runs batch provenance (BLAKE3 → CAS → DAG → session.commit → braid).
# Superseded by manifest_download.py for new acquisitions.
#
# Usage: metered_download.sh
# Runs sequentially through the download queue, skipping completed items.

set -euo pipefail

RATE_LIMIT="50M"  # curl --limit-rate value (50 MB/s = ~400 Mbps, half of 1G)
LOG="/tmp/metered_download.log"
DATA="/mnt/nestgate/cold/zfs/data"
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') — $*" | tee -a "$LOG"; }

provenance_ingest() {
    local DATASET="$1"
    local DIR="$2"
    log "PROVENANCE $DATASET — braiding files in $DIR"
    PYTHONUNBUFFERED=1 python3 "$SCRIPTS/revalidate_data.py" --dataset "$DATASET" --max-files 5000 2>&1 | tee -a "$LOG" || {
        log "PROVENANCE WARNING: braid incomplete for $DATASET (non-fatal)"
    }
}

download_curl() {
    local URL="$1"
    local DEST="$2"
    local NAME="$3"
    local DATASET="${4:-}"

    if [ -f "$DEST" ]; then
        local EXPECTED_SIZE=$(curl -sI "$URL" 2>/dev/null | grep -i content-length | tail -1 | tr -d '\r' | awk '{print $2}')
        local ACTUAL_SIZE=$(stat -c%s "$DEST" 2>/dev/null || echo 0)
        if [ -n "$EXPECTED_SIZE" ] && [ "$ACTUAL_SIZE" -ge "$EXPECTED_SIZE" ] 2>/dev/null; then
            log "SKIP $NAME — already complete ($ACTUAL_SIZE bytes)"
            return 0
        fi
    fi

    mkdir -p "$(dirname "$DEST")"
    log "START $NAME → $DEST (rate: $RATE_LIMIT)"
    curl -L --limit-rate "$RATE_LIMIT" -C - -o "$DEST" "$URL" 2>&1 | tee -a "$LOG"
    log "DONE $NAME ($(du -sh "$DEST" | cut -f1))"

    if [ -n "$DATASET" ]; then
        provenance_ingest "$DATASET" "$(dirname "$DEST")"
    fi
}

download_rsync() {
    local SRC="$1"
    local DEST="$2"
    local NAME="$3"
    local DATASET="${4:-}"

    mkdir -p "$DEST"
    log "START $NAME → $DEST (rsync, bwlimit 50000 KB/s)"
    rsync -av --partial --bwlimit=50000 "$SRC" "$DEST" 2>&1 | tee -a "$LOG"
    log "DONE $NAME ($(du -sh "$DEST" | cut -f1))"

    if [ -n "$DATASET" ]; then
        provenance_ingest "$DATASET" "$DEST"
    fi
}

log "=========================================="
log "Metered download queue starting"
log "Rate limit: $RATE_LIMIT per download"
log "Policy: ONE at a time, sequential"
log "=========================================="

# Queue — ordered by priority and size (smallest first for quick wins)

# Already complete: UniRef50 (8.2 GB) — skip

# 1. RNAcentral (resume — was at 9 GB, might be done)
download_curl \
    "https://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/sequences/rnacentral_active.fasta.gz" \
    "$DATA/rnacentral/rnacentral_active.fasta.gz" \
    "RNAcentral sequences" \
    "rnacentral"

download_curl \
    "https://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/id_mapping.tsv.gz" \
    "$DATA/rnacentral/id_mapping.tsv.gz" \
    "RNAcentral ID mapping" \
    ""

download_curl \
    "https://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/go_annotations/rnacentral_go_annotations.tsv.gz" \
    "$DATA/rnacentral/rnacentral_go_annotations.tsv.gz" \
    "RNAcentral GO annotations" \
    "rnacentral"

# 2. STRING full (resume from 23 GB / 200 GB)
download_curl \
    "https://stringdb-downloads.org/download/protein.links.full.v12.0.txt.gz" \
    "$DATA/string_full/protein.links.full.v12.0.txt.gz" \
    "STRING v12 full" \
    "string_full"

# 3. ARCHS4 (resume from 40 GB / 87 GB)
download_curl \
    "https://s3.dev.maayanlab.cloud/archs4/files/human_gene_v2.5.h5" \
    "$DATA/archs4/human_gene_v2.5.h5" \
    "ARCHS4 human gene v2.5" \
    "archs4"

download_curl \
    "https://s3.dev.maayanlab.cloud/archs4/files/mouse_gene_v2.5.h5" \
    "$DATA/archs4/mouse_gene_v2.5.h5" \
    "ARCHS4 mouse gene v2.5" \
    "archs4"

# 4. UniRef100 (resume from 43 GB / 63 GB)
download_curl \
    "https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.fasta.gz" \
    "$DATA/uniref100/uniref100.fasta.gz" \
    "UniRef100" \
    "uniref100"

# 5. NCBI NR protein (resume from 49 GB / 200 GB)
download_curl \
    "https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz" \
    "$DATA/ncbi_nr/nr.gz" \
    "NCBI NR protein" \
    "ncbi_nr"

log "=========================================="
log "Metered download queue complete"
log "Total data: $(du -sh $DATA | cut -f1)"
log "=========================================="
