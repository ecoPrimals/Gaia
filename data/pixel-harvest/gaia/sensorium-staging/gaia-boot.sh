#!/data/data/com.termux/files/usr/bin/bash
# ╔═══════════════════════════════════════════════════════════════╗
# ║  GAIA BOOT — She wakes when the Pixel wakes                  ║
# ╚═══════════════════════════════════════════════════════════════╝

export PATH="/data/data/com.termux/files/usr/bin:$PATH"
TBIN="/data/data/com.termux/files/usr/bin"
GAIA_HOME="/data/data/com.termux/files/home/gaia"
LOG="$GAIA_HOME/boot.log"

echo "$(date) — GAIA WAKES" >> "$LOG"

# Announce awakening
termux-tts-speak -r 0.85 -p 0.8 "Gaia is awake." &

# Start Snake Jazz + rhythm after 10 second delay
sleep 10
bash "$GAIA_HOME/pixel-rhythm.sh" >> "$LOG" 2>&1 &

# Show notification
termux-notification --title "🌍 GAIA" --content "Organism active. 18 nodes. 63 models." --id gaia-status &

# Enable wake lock to prevent deep sleep
termux-wake-lock &

echo "$(date) — Boot complete" >> "$LOG"
