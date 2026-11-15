#!/bin/bash
# ear-daemon.sh — Gaia's always-on ear
# The REAL ear: sporeGate's Logitech Brio 100 USB mic
# eastGate has no physical mic — sporeGate is our cochlea
#
# Pattern: SSH → record on sporeGate → SCP back → analyze locally → state
# Feeds: ear-state.json (served at :8443 and :8080)

EAR_DIR="/opt/Gaia/data/ear"
SPORE="sporegate@192.168.4.3"
SSH_KEY="$HOME/.ssh/id_ed25519"
SSH_OPTS="-o ConnectTimeout=5 -o IdentitiesOnly=yes -o BatchMode=yes -i $SSH_KEY"
CYCLE_S=30
BRIO_DEV="plughw:2,0"  # Logitech Brio 100 on sporeGate

mkdir -p "$EAR_DIR"
CYCLE_COUNT=0

classify_sound() {
    local rms=$1 peak=$2
    if (( rms > 3000 )); then
        echo "loud_event"      # printer pump, door slam, voice
    elif (( rms > 1000 )); then
        echo "active"          # conversation, music, mechanical
    elif (( rms > 500 )); then
        echo "ambient"         # TV background, typing, room tone
    elif (( rms > 200 )); then
        echo "quiet"           # faint hum, HVAC
    else
        echo "silence"         # nothing (or mic dead)
    fi
}

while true; do
    TS=$(date +%Y%m%d_%H%M%S)
    REMOTE_WAV="/tmp/gaia-ear-${TS}.wav"
    LOCAL_WAV="$EAR_DIR/ear_${TS}.wav"
    CYCLE_START=$(date +%s)

    # Record on sporeGate via SSH (Brio mic, CD quality, CYCLE_S seconds)
    ssh $SSH_OPTS $SPORE \
        "arecord -D $BRIO_DEV -f cd -d $CYCLE_S -t wav $REMOTE_WAV 2>/dev/null" 2>/dev/null

    if [ $? -ne 0 ]; then
        cat > "$EAR_DIR/ear-state.json" << EOF
{
  "ts": "$(date -Iseconds)",
  "state": "deaf",
  "source": "sporeGate:brio100",
  "error": "ssh_failed",
  "daemon": "ear-daemon",
  "cycle_s": $CYCLE_S
}
EOF
        echo "[$(date)] ear: DEAF — sporeGate unreachable"
        sleep $CYCLE_S
        continue
    fi

    # Pull WAV to eastGate
    scp $SSH_OPTS $SPORE:$REMOTE_WAV "$LOCAL_WAV" 2>/dev/null
    ssh $SSH_OPTS $SPORE "rm -f $REMOTE_WAV" 2>/dev/null &

    if [ ! -f "$LOCAL_WAV" ] || [ ! -s "$LOCAL_WAV" ]; then
        echo "[$(date)] ear: empty WAV"
        sleep 5
        continue
    fi

    # Analyze: per-second RMS/peak + overall + event detection
    ANALYSIS=$(python3 << PYEOF
import wave, struct, math, json, sys

try:
    w = wave.open("$LOCAL_WAV", "r")
    nframes = w.getnframes()
    rate = w.getframerate()
    ch = w.getnchannels()
    frames = w.readframes(nframes)
    w.close()

    if len(frames) < 4:
        print(json.dumps({"error": "empty"}))
        sys.exit(0)

    samples = struct.unpack(f'<{len(frames)//2}h', frames)
    duration = nframes / rate

    overall_rms = math.sqrt(sum(s**2 for s in samples) / len(samples))
    overall_peak = max(abs(s) for s in samples)
    overall_db = 20 * math.log10(overall_rms / 32768 + 1e-10)

    seconds = []
    loud_events = 0
    max_rms = 0
    for sec in range(int(duration)):
        start = sec * rate * ch
        end = min(start + rate * ch, len(samples))
        chunk = samples[start:end]
        if not chunk:
            continue
        rms = math.sqrt(sum(x**2 for x in chunk) / len(chunk))
        peak = max(abs(x) for x in chunk)
        if rms > max_rms:
            max_rms = rms
        if rms > 3000:
            loud_events += 1
        seconds.append({"s": sec, "rms": round(rms), "peak": peak})

    # Detect printer cycle: loud burst (>3000) surrounded by ambient (<1000)
    printer_detected = False
    for i, s in enumerate(seconds):
        if s["rms"] > 3000:
            before_quiet = i > 0 and seconds[i-1]["rms"] < 1500
            after_quiet = i < len(seconds)-1 and seconds[i+1]["rms"] < 1500
            if before_quiet or after_quiet:
                printer_detected = True
                break

    print(json.dumps({
        "rms": round(overall_rms),
        "peak": overall_peak,
        "db": round(overall_db, 1),
        "max_rms": round(max_rms),
        "loud_events": loud_events,
        "printer_cycle": printer_detected,
        "seconds": seconds,
        "duration": round(duration, 1)
    }))
except Exception as e:
    print(json.dumps({"error": str(e)}))
PYEOF
    )

    # Extract fields
    RMS=$(echo "$ANALYSIS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('rms',0))")
    PEAK=$(echo "$ANALYSIS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('peak',0))")
    DB=$(echo "$ANALYSIS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('db',-96))")
    MAX_RMS=$(echo "$ANALYSIS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('max_rms',0))")
    LOUD=$(echo "$ANALYSIS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(int(d.get('loud_events',0)))")
    PRINTER=$(echo "$ANALYSIS" | python3 -c "import sys,json; d=json.load(sys.stdin); print('true' if d.get('printer_cycle') else 'false')")
    SECS_JSON=$(echo "$ANALYSIS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get('seconds',[])))")

    STATE=$(classify_sound $RMS $PEAK)

    # Write ear state — the organism's hearing
    cat > "$EAR_DIR/ear-state.json" << EOF
{
  "ts": "$(date -Iseconds)",
  "mic": {
    "rms": $RMS,
    "peak": $PEAK,
    "db": $DB,
    "max_rms": $MAX_RMS,
    "state": "$STATE"
  },
  "events": {
    "loud_bursts": $LOUD,
    "printer_cycle": $PRINTER
  },
  "seconds": $SECS_JSON,
  "source": "sporeGate:brio100",
  "device": "$BRIO_DEV",
  "daemon": "ear-daemon",
  "cycle_s": $CYCLE_S,
  "file": "ear_${TS}.wav"
}
EOF

    # Rotate: keep last 10 WAVs (5 minutes of audio history)
    ls -1t "$EAR_DIR"/ear_*.wav 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

    CYCLE_END=$(date +%s)
    ELAPSED=$((CYCLE_END - CYCLE_START))
    echo "[$(date)] ear: rms=$RMS peak=$PEAK db=${DB}dB state=$STATE loud=$LOUD printer=$PRINTER (${ELAPSED}s)"

    # Run spectral analysis + Akida classification + full attenuator
    python3 /opt/Gaia/ear-spectral.py 2>/dev/null &
    python3 /opt/Gaia/akida-ear-pipe.py 2>/dev/null &
    # Full 7-sense attenuator sweep every 4th cycle (~2min)
    CYCLE_COUNT=$(( (CYCLE_COUNT + 1) % 4 ))
    if [ "$CYCLE_COUNT" -eq 0 ]; then
        python3 /opt/Gaia/attenuate-all.py 2>/dev/null &
    fi

    # If cycle took less than CYCLE_S, the sleep was in the recording itself — no extra wait needed
done
