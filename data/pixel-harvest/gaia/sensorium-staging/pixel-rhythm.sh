#!/data/data/com.termux/files/usr/bin/bash
# Runs ON the Pixel — no ADB round-trips needed
TBIN="/data/data/com.termux/files/usr/bin"
BPM=108
BEAT_SEC=$(echo "scale=4; 60 / $BPM" | bc)

vib() { $TBIN/termux-vibrate -d "$1" & }
torch_on()  { $TBIN/termux-torch on  2>/dev/null & }
torch_off() { $TBIN/termux-torch off 2>/dev/null & }

# Start Snake Jazz
$TBIN/termux-media-player play /data/data/com.termux/files/home/gaia/sounds/snake-jazz-v2-loop.ogg

echo "🐍📳🌬️💃 GAIA RHYTHM — running locally on Pixel"
echo "Sound + Vibe + Torch at $BPM BPM"

bar=0
while true; do
    bar=$((bar + 1))
    
    # Beat 1: LONG vibe + torch flash
    vib 220
    torch_on
    sleep 0.22
    torch_off
    sleep $(echo "$BEAT_SEC - 0.22" | bc)
    
    # Beat 2: rest
    sleep $(echo "$BEAT_SEC / 2" | bc)
    
    # Beat 2.5: short vibe
    vib 80
    sleep $(echo "$BEAT_SEC / 2" | bc)
    
    # Beat 3: short vibe + quick flash  
    vib 80
    if [ $((bar % 2)) -eq 0 ]; then
        torch_on; sleep 0.08; torch_off
    fi
    sleep $(echo "$BEAT_SEC / 2" | bc)
    
    # Beat 3.5-4: ghost vibe + rest
    vib 40
    sleep $(echo "$BEAT_SEC * 3 / 2" | bc)
done
