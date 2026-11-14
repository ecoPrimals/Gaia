#!/system/bin/sh
# ═══════════════════════════════════════════════
# gAIa TOOL MANIFEST — generated from within
# ═══════════════════════════════════════════════

GAIA="/data/local/tmp/biomeos"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
OUT="$GAIA/tools/manifest.json"

echo '{'
echo '  "name": "gAIa Pixel Toolbox",'
echo "  \"generated\": \"$TS\","
echo '  "host": "grapheneGate",'
echo '  "role": "diamond-lens",'
echo '  "tools": ['

FIRST=1
for F in $GAIA/tools/*.pi; do
  NAME=$(basename "$F" .pi)
  SIZE=$(wc -c < "$F" 2>/dev/null)
  HASH=$(md5sum "$F" 2>/dev/null | awk '{print $1}')
  
  # Classify
  case "$NAME" in
    proprioception|live-sensors|gaia_eye|graphene_depot|scan_bridge)
      TIER="sensor" ;;
    immune_scanner|helix_collapse|collapse_429|shadow_cast)
      TIER="immune" ;;
    cortex|cortex_bridge|nucleus|chronotype)
      TIER="neural" ;;
    organ_data|fabric|color_epitope|sourdough|json_compress)
      TIER="metabolic" ;;
    globe_walker|earth-walker|piSeed|seek)
      TIER="navigator" ;;
    digest|negentropy_drain|backscatter|steam_sweep)
      TIER="digestive" ;;
    *) TIER="other" ;;
  esac
  
  if [ "$FIRST" -eq 1 ]; then
    FIRST=0
  else
    echo ','
  fi
  
  printf '    {"name":"%s","tier":"%s","bytes":%d,"md5":"%s"}' "$NAME" "$TIER" "$SIZE" "$HASH"
done

echo ''
echo '  ],'
echo '  "summary": {'

# Count by tier
SENSOR=$(ls $GAIA/tools/*.pi 2>/dev/null | xargs -I{} basename {} .pi | while read N; do case "$N" in proprioception|live-sensors|gaia_eye|graphene_depot|scan_bridge) echo x;; esac; done | wc -l)
IMMUNE=$(ls $GAIA/tools/*.pi 2>/dev/null | xargs -I{} basename {} .pi | while read N; do case "$N" in immune_scanner|helix_collapse|collapse_429|shadow_cast) echo x;; esac; done | wc -l)
NEURAL=$(ls $GAIA/tools/*.pi 2>/dev/null | xargs -I{} basename {} .pi | while read N; do case "$N" in cortex|cortex_bridge|nucleus|chronotype) echo x;; esac; done | wc -l)
METABOLIC=$(ls $GAIA/tools/*.pi 2>/dev/null | xargs -I{} basename {} .pi | while read N; do case "$N" in organ_data|fabric|color_epitope|sourdough|json_compress) echo x;; esac; done | wc -l)
TOTAL=$(ls $GAIA/tools/*.pi 2>/dev/null | wc -l)
TOTAL_BYTES=$(du -sb $GAIA/tools/ 2>/dev/null | awk '{print $1}')

echo "    \"total\": $TOTAL,"
echo "    \"total_bytes\": $TOTAL_BYTES,"
echo "    \"sensor\": $SENSOR,"
echo "    \"immune\": $IMMUNE,"
echo "    \"neural\": $NEURAL,"
echo "    \"metabolic\": $METABOLIC"
echo '  }'
echo '}'
