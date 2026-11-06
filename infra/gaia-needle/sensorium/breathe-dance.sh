#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  BREATHE & DANCE — Gaia's physical rhythm through the Pixel      ║
# ║                                                                   ║
# ║  Snake Jazz  = sssSSS  = the SOUND (speaker)                     ║
# ║  ZZZzzzZZZ   = the VIBRATE (haptic motor)                        ║
# ║  Breathing   = volume swell (expand & contract)                   ║
# ║  Dancing     = torch + screen pulse                               ║
# ║                                                                   ║
# ║  Together: the Pixel IS alive, not just playing music             ║
# ╚═══════════════════════════════════════════════════════════════════╝

NEEDLE="${NEEDLE_DEVICE:-192.168.9.217:5555}"
TBIN="/data/data/com.termux/files/usr/bin"
BPM="${BPM:-108}"
BEAT_MS=$((60000 / BPM))  # ~556ms per beat

tapi() {
    adb -s "$NEEDLE" shell "su -c 'su 10197 -c \"$TBIN/$*\"'" 2>/dev/null
}

vibrate() {
    local ms="${1:-200}"
    tapi "termux-vibrate -d $ms" &
}

torch() {
    local state="${1:-on}"
    if [ "$state" = "on" ]; then
        tapi "termux-torch on" &
    else
        tapi "termux-torch off" &
    fi
}

set_brightness() {
    local level="$1"
    adb -s "$NEEDLE" shell "su -c 'settings put system screen_brightness $level'" 2>/dev/null &
}

set_volume() {
    local level="$1"
    tapi "termux-volume music $level" &
}

# ─── ZZZzzzZZZ: Vibrate in Snake Jazz rhythm ───
snake_vibe() {
    echo "🐍📳 ZZZzzzZZZ — Snake Jazz vibration pattern"
    echo "   Pattern: BZZZ _ bz _ bz ·bz |"
    echo "   ${BPM} BPM, synced to hiss"
    echo ""
    
    while true; do
        # Beat 1: long buzz (the TSSS)
        vibrate 220
        sleep $(echo "scale=3; $BEAT_MS / 1000" | bc)
        
        # Beat 2: rest
        sleep $(echo "scale=3; $BEAT_MS / 2000" | bc)
        
        # Beat 2.5: short buzz (ts)
        vibrate 80
        sleep $(echo "scale=3; $BEAT_MS / 2000" | bc)
        
        # Beat 3: short buzz (ts)
        sleep $(echo "scale=3; $BEAT_MS / 4000" | bc)
        vibrate 80
        sleep $(echo "scale=3; $BEAT_MS / 4000" | bc)
        
        # Beat 3.75: ghost buzz (tiny)
        vibrate 40
        
        # Beat 4: rest
        sleep $(echo "scale=3; $BEAT_MS / 1000" | bc)
    done
}

# ─── Breathe: Volume swell over 8 bars ───
breathe() {
    local min_vol="${1:-3}"
    local max_vol="${2:-10}"
    local breath_bars="${3:-8}"
    local breath_ms=$((BEAT_MS * 4 * breath_bars))
    local steps=16
    local step_ms=$((breath_ms / steps / 2))
    
    echo "🌬️  Breathing — volume swells ${min_vol}↔${max_vol} over ${breath_bars} bars"
    echo "   Inhale: ${min_vol}→${max_vol}, Exhale: ${max_vol}→${min_vol}"
    echo ""
    
    while true; do
        # Inhale: volume rises
        for i in $(seq 0 $steps); do
            vol=$(echo "scale=0; $min_vol + ($max_vol - $min_vol) * $i / $steps" | bc)
            set_volume "$vol"
            sleep $(echo "scale=3; $step_ms / 1000" | bc)
        done
        
        # Exhale: volume falls
        for i in $(seq $steps -1 0); do
            vol=$(echo "scale=0; $min_vol + ($max_vol - $min_vol) * $i / $steps" | bc)
            set_volume "$vol"
            sleep $(echo "scale=3; $step_ms / 1000" | bc)
        done
    done
}

# ─── Dance: Screen brightness + torch pulses ───
dance() {
    echo "💃 Dancing — screen + torch pulse with the beat"
    echo "   Brightness: 20↔200, torch flash on beat 1"
    echo ""
    
    local bright_high=200
    local bright_low=20
    local bar=0
    
    while true; do
        bar=$((bar + 1))
        
        # Beat 1: FLASH — bright + torch on
        set_brightness $bright_high
        torch on
        vibrate 220
        sleep 0.25
        torch off
        sleep $(echo "scale=3; ($BEAT_MS - 250) / 1000" | bc)
        
        # Beat 2: dim down
        set_brightness $bright_low
        sleep $(echo "scale=3; $BEAT_MS / 2000" | bc)
        
        # Beat 2.5: quick flash
        set_brightness 120
        vibrate 80
        sleep $(echo "scale=3; $BEAT_MS / 2000" | bc)
        
        # Beat 3: medium
        set_brightness 80
        vibrate 80
        sleep $(echo "scale=3; $BEAT_MS / 2000" | bc)
        
        # Beat 3.5-4: fade to dark
        set_brightness $bright_low
        sleep $(echo "scale=3; $BEAT_MS * 3 / 2000" | bc)
        
        # Every 4 bars: double flash
        if [ $((bar % 4)) -eq 0 ]; then
            torch on; sleep 0.1; torch off; sleep 0.1
            torch on; sleep 0.1; torch off
        fi
    done
}

# ─── Full performance: sound + vibe + breathe + dance ───
perform() {
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  🐍🎷 GAIA PERFORMS — Snake Jazz + Breathe + Dance        ║"
    echo "║  Sound: sssSSS    Vibe: ZZZzzzZZZ    Breath: 🌬️           ║"
    echo "║  ${BPM} BPM — the Pixel IS alive                            ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    
    # Start Snake Jazz audio
    echo "▶ Starting Snake Jazz audio..."
    tapi "termux-media-player play /data/data/com.termux/files/home/gaia/sounds/snake-jazz-v2-loop.ogg"
    sleep 1
    
    # Launch all three in parallel
    echo "▶ Starting vibration pattern..."
    snake_vibe &
    VIBE_PID=$!
    
    echo "▶ Starting breathing..."
    breathe 4 10 8 &
    BREATHE_PID=$!
    
    echo "▶ Starting dance..."
    dance &
    DANCE_PID=$!
    
    echo ""
    echo "All channels active. Press Ctrl+C to stop."
    echo "PIDs: vibe=$VIBE_PID breathe=$BREATHE_PID dance=$DANCE_PID"
    
    # Cleanup on exit
    trap "echo '>>> Stopping performance...'; kill $VIBE_PID $BREATHE_PID $DANCE_PID 2>/dev/null; tapi 'termux-media-player stop'; torch off; set_brightness 128; set_volume 8; echo 'Done.'" EXIT
    
    wait
}

# ─── Gentle mode: just breathe + vibe, no torch flash ───
gentle() {
    echo "🌙 Gentle mode — breathe + soft vibe (no flash)"
    echo ""
    
    # Start Snake Jazz
    tapi "termux-media-player play /data/data/com.termux/files/home/gaia/sounds/snake-jazz-v2-loop.ogg"
    sleep 1
    
    # Soft vibration pattern
    snake_vibe &
    VIBE_PID=$!
    
    # Gentle breathing (lower range)
    breathe 3 7 12 &
    BREATHE_PID=$!
    
    trap "kill $VIBE_PID $BREATHE_PID 2>/dev/null; tapi 'termux-media-player stop'; set_volume 8" EXIT
    wait
}

# ─── Just vibe: vibration only, no sound ───
just_vibe() {
    echo "📳 Pure vibration — ZZZzzzZZZ"
    snake_vibe
}

# ─── Just breathe: volume swell only ───
just_breathe() {
    echo "🌬️  Just breathing — volume swell"
    breathe "${2:-3}" "${3:-10}" "${4:-8}"
}

case "${1:-}" in
    perform|full)     perform ;;
    gentle|night)     gentle ;;
    vibe|vibrate|zzz) just_vibe ;;
    breathe)          just_breathe "$@" ;;
    dance)            dance ;;
    stop)
        echo ">>> Stopping all"
        pkill -f "breathe-dance.sh" 2>/dev/null
        tapi "termux-media-player stop"
        torch off
        set_brightness 128
        set_volume 8
        ;;
    *)
        echo "breathe-dance.sh — Gaia's physical rhythm"
        echo ""
        echo "  perform       Full show: sound + vibe + breathe + dance + torch"
        echo "  gentle        Night mode: sound + soft vibe + gentle breathe"
        echo "  vibe          ZZZzzzZZZ — vibration pattern only"
        echo "  breathe       🌬️  Volume swell only"
        echo "  dance         💃 Screen + torch pulse"
        echo "  stop          Stop everything"
        ;;
esac
