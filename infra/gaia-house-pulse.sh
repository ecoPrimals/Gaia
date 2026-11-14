#!/bin/bash
DATA_DIR="/home/eastgate/Development/ecoPrimals/infra/hud/site/public/data"

# ZK: subnet derived from gateway, octets are the identity
SUBNET="192.168.4"
GG=0; ping -c1 -W1 "$SUBNET.127" &>/dev/null && GG=1
CC=0; ping -c1 -W1 "$SUBNET.169" &>/dev/null && CC=1

ALIVE=0
for octet in 1 2 3 100 103 107 147 148 169 176 197 237 238 244; do
    ping -c1 -W1 "$SUBNET.$octet" &>/dev/null && ((ALIVE++))
done

VOICE="false"; [ "$CC" = "1" ] && VOICE="true"

cat > "$DATA_DIR/house-pulse.json" << JEOF
{
  "ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "grapheneGate": $GG,
  "chromecast": $CC,
  "alive_devices": $ALIVE,
  "voice_ready": $VOICE
}
JEOF

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | devices=$ALIVE gg=$GG cc=$CC"
