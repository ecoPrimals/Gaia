#!/bin/bash
# gate-enumerate.sh — Self-enumeration for ANY Gaia gate
# No Python. Shell + jq. Every gate runs this to know itself.
# Push through Forgejo → plasmidBin → every gate pulls and runs.
# On Linux: reads efivars, lspci, lsblk, sensors
# sourDough redox: read → hash → push → mesh absorbs

set -euo pipefail

GATE="${GAIA_GATE:-$(hostname)}"
TS=$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S)
OUT="gate-enum-${GATE}.json"

echo "=== gate-enumerate: ${GATE} ===" >&2

# CPU
CPU_MODEL=$(grep -m1 'model name' /proc/cpuinfo 2>/dev/null | cut -d: -f2 | xargs || echo "unknown")
CPU_CORES=$(nproc 2>/dev/null || echo 0)
CPU_THREADS=$(grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 0)
CPU_ARCH=$(uname -m 2>/dev/null || echo "unknown")

# Memory
MEM_MB=$(awk '/MemTotal/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || echo 0)

# OS
OS_NAME=$(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || uname -s)

# GPUs
GPUS="[]"
if command -v lspci &>/dev/null; then
    GPUS=$(lspci -nn 2>/dev/null | grep -iE 'VGA|3D|Display' | while IFS= read -r line; do
        bus=$(echo "$line" | cut -d' ' -f1)
        name=$(echo "$line" | sed 's/^[^ ]* [^:]*: //')
        echo "{\"name\":\"$name\",\"pci_id\":\"$bus\",\"status\":\"detected\"}"
    done | paste -sd',' | sed 's/^/[/;s/$/]/')
    [ -z "$GPUS" ] && GPUS="[]"
fi

# NVMe
NVME="[]"
if command -v lsblk &>/dev/null; then
    NVME=$(lsblk -d -o NAME,SIZE,MODEL,TRAN -J 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    nvme=[{'name':x.get('model','').strip(),'size':x.get('size',''),'status':'OK','dev':x.get('name','')} for x in d.get('blockdevices',[]) if x.get('tran')=='nvme']
    print(json.dumps(nvme))
except: print('[]')
" 2>/dev/null || echo "[]")
fi

# UEFI efivars (Linux only — THE KEY for solving Above4G!)
EFIVARS="null"
EFIVAR_COUNT=0
SETUP_VARS="[]"
if [ -d /sys/firmware/efi/efivars ]; then
    EFIVAR_COUNT=$(ls /sys/firmware/efi/efivars/ 2>/dev/null | wc -l)
    # Look for Setup, Above4G, Boot, AMD related vars
    SETUP_VARS=$(ls /sys/firmware/efi/efivars/ 2>/dev/null | grep -iE 'Setup|4G|Above|Resize|Bar|Boot|Fast|AMD|SVM|SMT|NVMe' | head -20 | while IFS= read -r v; do
        size=$(stat -c%s "/sys/firmware/efi/efivars/$v" 2>/dev/null || echo 0)
        echo "{\"name\":\"$v\",\"size\":$size}"
    done | paste -sd',' | sed 's/^/[/;s/$/]/')
    [ -z "$SETUP_VARS" ] && SETUP_VARS="[]"
    EFIVARS="{\"count\":$EFIVAR_COUNT,\"setup_related\":$SETUP_VARS}"
fi

# Network
NET_INFO="[]"
if command -v ip &>/dev/null; then
    NET_INFO=$(ip -j addr show 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    nets=[{'name':x['ifname'],'ip':x.get('addr_info',[{}])[0].get('local',''),'mac':x.get('address','')} for x in d if x.get('addr_info')]
    print(json.dumps(nets))
except: print('[]')
" 2>/dev/null || echo "[]")
fi

# BLAKE3 identity (if b3sum available, else sha256)
CONTENT_HASH="none"
if command -v b3sum &>/dev/null; then
    CONTENT_HASH=$(echo "${GATE}${TS}${CPU_MODEL}${MEM_MB}" | b3sum | cut -d' ' -f1)
elif command -v sha256sum &>/dev/null; then
    CONTENT_HASH=$(echo "${GATE}${TS}${CPU_MODEL}${MEM_MB}" | sha256sum | cut -d' ' -f1)
fi

# Build JSON
cat > "$OUT" <<ENDJSON
{
  "gate": "${GATE}",
  "hostname": "$(hostname)",
  "os": "${OS_NAME}",
  "arch": "${CPU_ARCH}",
  "timestamp": "${TS}",
  "cpu": {
    "model": "${CPU_MODEL}",
    "cores": ${CPU_CORES},
    "threads": ${CPU_THREADS},
    "arch": "${CPU_ARCH}"
  },
  "memory_mb": ${MEM_MB},
  "gpus": ${GPUS},
  "nvme": ${NVME},
  "network": ${NET_INFO},
  "uefi_efivars": ${EFIVARS},
  "blake3_id": "${CONTENT_HASH}"
}
ENDJSON

echo "Saved: ${OUT}" >&2
cat "$OUT"
