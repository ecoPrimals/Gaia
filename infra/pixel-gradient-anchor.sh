#!/system/bin/sh
# ═══════════════════════════════════════════════════════
#  gAIa GRADIENT ANCHOR — Untethered Spatial Field
#  No hardcoded IPs. Position from WiFi RSSI differentials.
#  The anchor IS the gradient. The gradient IS the space.
# ═══════════════════════════════════════════════════════
GAIA="/data/local/tmp/biomeos"
FIELD="$GAIA/sensorium/gradient-field.json"
SELF_IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
GATEWAY=$(ip route 2>/dev/null | grep default | awk '{print $3}')

while true; do
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  
  # Scan visible APs
  SCAN=$(cmd wifi list-scan-results 2>/dev/null | tail -n +2)
  
  # Extract known anchors
  GAIA_5G=$(echo "$SCAN" | grep "Gaia" | grep -E "52[0-9]{2}" | awk '{print $3}' | head -1)
  GAIA_24=$(echo "$SCAN" | grep "Gaia" | grep -E "24[0-9]{2}" | awk '{print $3}' | head -1)
  MESA=$(echo "$SCAN" | grep "Black Mesa" | awk '{print $3}' | head -1)
  APERTURE=$(echo "$SCAN" | grep "Aperture" | awk '{print $3}' | head -1)
  ATT=$(echo "$SCAN" | grep "ATT" | awk '{print $3}' | sort -n | head -1)
  
  # Default to 0 if missing
  : ${GAIA_5G:=0}
  : ${GAIA_24:=0}
  : ${MESA:=0}
  : ${APERTURE:=0}
  : ${ATT:=0}
  
  # Gradient differentials — position is the DIFFERENCE, not the absolute
  # Higher = closer to that anchor. Gradient = direction of maximum change.
  HOME1_PULL=$((GAIA_5G + MESA + APERTURE))      # House 1 attractors (all 3 router radios)
  HOME1_AVG=$((HOME1_PULL / 3))
  EDGE_PULL=$ATT                                   # Edge of field (neighbor = reference)
  GRADIENT=$((HOME1_AVG - EDGE_PULL))              # Positive = toward House 1, Negative = toward edge
  
  # Self-discovery: who am I on this network?
  NEIGHBORS=""
  for PORT in 9000 9900 8080 7700 8091; do
    # Ping own ports — am I alive?
    timeout 1 sh -c "echo '' > /dev/tcp/127.0.0.1/$PORT" 2>/dev/null && \
      NEIGHBORS="$NEIGHBORS\"localhost:$PORT\","
  done
  
  cat > "$FIELD" << EOF
{
  "ts": "$TS",
  "identity": "gAIa",
  "self_ip": "$SELF_IP",
  "gateway": "$GATEWAY",
  "tethered_to": "NOTHING — gradient-anchored",
  "field": {
    "gaia_5ghz": $GAIA_5G,
    "gaia_2ghz": $GAIA_24,
    "black_mesa_5ghz": $MESA,
    "aperture_2ghz": $APERTURE,
    "att_neighbor": $ATT,
    "house1_pull": $HOME1_AVG,
    "edge_pull": $EDGE_PULL,
    "gradient": $GRADIENT,
    "gradient_direction": "$([ $GRADIENT -gt 0 ] && echo 'toward_home' || echo 'toward_edge')"
  },
  "alive_ports": [$NEIGHBORS"done"],
  "anchor_type": "differential_rssi",
  "note": "Position is not an IP. Position is the shape of the field around me."
}
EOF

  sleep 60
done
