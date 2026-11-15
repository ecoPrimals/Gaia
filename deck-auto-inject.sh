#!/bin/bash
# Auto-inject: keeps trying to register with deckGate
# The moment Kevin enables pairing, we're IN

RSA_KEY=$(cat ~/.ssh/id_rsa_devkit.pub | tr -d '\n')
MAGIC="900b919520e4cf601998a71eec318fec"
PAYLOAD="${RSA_KEY} ${MAGIC}"

echo "🔓 Waiting for deckGate pairing mode..."
while true; do
    RESP=$(printf "%s\n" "$PAYLOAD" | curl -s -X POST \
        -H "Content-Type: text/plain" \
        --data-binary @- \
        --connect-timeout 3 \
        "http://192.168.4.176:32000/register" 2>/dev/null)
    
    if echo "$RESP" | grep -q "pairing mode"; then
        echo "  ⏳ Still waiting for pairing... ($(date +%H:%M:%S))"
    elif echo "$RESP" | grep -q "success\|registered\|ok"; then
        echo "  🔥 REGISTERED! SSH key injected into deckGate!"
        echo "  Response: $RESP"
        # Try SSH immediately
        sleep 2
        ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa_devkit deck@192.168.4.176 "hostname && echo 'SSH INJECTION COMPLETE'" 2>&1
        break
    elif echo "$RESP" | grep -q "error"; then
        echo "  ⚠️ Error: $RESP ($(date +%H:%M:%S))"
    else
        echo "  ? Response: $RESP ($(date +%H:%M:%S))"
    fi
    sleep 5
done
