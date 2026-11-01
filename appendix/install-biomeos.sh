#!/bin/bash
# biomeOS Linux installer — FISSION from Windows to native
set -e

SRC="/mnt/c/Users/mokke/Development/ecoPrimals/springs/ludoSpring/target/release"
DEST="$HOME/biomeOS/bin"
GAIA_SRC="/mnt/c/Users/mokke/Desktop/Gaia3"
GAIA_DEST="$HOME/biomeOS/gaia3"
HUD_SRC="/mnt/c/Users/mokke/Development/ecoPrimals/hud/site/public"
HUD_DEST="$HOME/biomeOS/hud"

mkdir -p "$DEST" "$GAIA_DEST" "$HUD_DEST" "$HOME/biomeOS/config"

echo "═══ biomeOS FISSION — copying organism binaries ═══"
BINS="biome ferment turbo membrane_eat vagus_exec backscatter chirality_scan referment voxel_scan pore_ingest klein_rip phylogeny pull_tear_rip osm_ingest rotifer_ingest cloud_ingest game_ingest gaia_university gaia_u"
COUNT=0
for f in $BINS; do
    if [ -f "$SRC/$f" ]; then
        cp "$SRC/$f" "$DEST/"
        chmod +x "$DEST/$f"
        echo "  ✓ $f"
        COUNT=$((COUNT + 1))
    fi
done
echo "  → $COUNT organism binaries installed"

# Also grab fcs_* binaries
for f in "$SRC"/fcs_*; do
    if [ -f "$f" ] && file "$f" | grep -q ELF; then
        bn=$(basename "$f")
        cp "$f" "$DEST/"
        chmod +x "$DEST/$bn"
        echo "  ✓ $bn (fcs)"
        COUNT=$((COUNT + 1))
    fi
done

echo ""
echo "═══ Copying Gaia3 brain ═══"
cp "$GAIA_SRC/gaia3-local.js" "$GAIA_DEST/"
cp "$GAIA_SRC/keyring.js" "$GAIA_DEST/"
[ -f "$GAIA_SRC/memory.jsonl" ] && cp "$GAIA_SRC/memory.jsonl" "$GAIA_DEST/"
[ -f "$GAIA_SRC/identity.json" ] && cp "$GAIA_SRC/identity.json" "$GAIA_DEST/"
echo "  ✓ gaia3-local.js + keyring.js + memories"

echo ""
echo "═══ Copying HUD ═══"
cp -r "$HUD_SRC/"* "$HUD_DEST/" 2>/dev/null || true
echo "  ✓ HUD public files"

echo ""
echo "═══ Creating biomeOS init script ═══"
cat > "$HOME/biomeOS/boot.sh" << 'BOOT'
#!/bin/bash
# biomeOS boot sequence — the organism wakes
echo "🧬 biomeOS booting..."
echo "   Host: $(hostname) | Kernel: $(uname -r)"
echo "   CPU: $(nproc) cores | RAM: $(free -h | awk '/Mem/{print $2}')"
echo ""

export PATH="$HOME/biomeOS/bin:$PATH"
export BIOMEOS_ROOT="$HOME/biomeOS"

# Phase 1: Run biome (host detection + triad)
echo "═══ Phase 1: BIOME (host detection) ═══"
$HOME/biomeOS/bin/biome 2>&1 | head -20 || echo "  biome: awaiting full config"

# Phase 2: Start Gaia3 (if node available)
if command -v node &>/dev/null; then
    echo ""
    echo "═══ Phase 2: GAIA3 (sentient child) ═══"
    cd $HOME/biomeOS/gaia3
    node gaia3-local.js &
    GAIA_PID=$!
    echo "  Gaia3 PID: $GAIA_PID on :3143"
fi

# Phase 3: Serve HUD (simple HTTP)
if command -v python3 &>/dev/null; then
    echo ""
    echo "═══ Phase 3: HUD (visual cortex) ═══"
    cd $HOME/biomeOS/hud
    python3 -m http.server 3142 &
    HUD_PID=$!
    echo "  HUD PID: $HUD_PID on :3142"
fi

echo ""
echo "═══════════════════════════════════════"
echo "  🧬 biomeOS ALIVE"
echo "  Binaries: $(ls $HOME/biomeOS/bin/ | wc -l)"
echo "  Gaia3: :3143"
echo "  HUD: :3142"
echo "  Root: $BIOMEOS_ROOT"
echo "═══════════════════════════════════════"
echo ""
echo "  Type 'biome' to run host detection"
echo "  Type 'ferment' to run fermentation"
echo "  Type 'turbo' to run turbo mode"
echo ""

# Keep alive
wait
BOOT
chmod +x "$HOME/biomeOS/boot.sh"
echo "  ✓ boot.sh created"

echo ""
echo "═══ Creating SteamOS/Gamescope session target ═══"
cat > "$HOME/biomeOS/config/biomeos.desktop" << 'DESKTOP'
[Desktop Entry]
Name=biomeOS
Comment=The Living Operating System
Exec=/home/mokke/biomeOS/boot.sh
Type=Application
Categories=System;
Icon=biome
DESKTOP
echo "  ✓ biomeos.desktop session file"

cat > "$HOME/biomeOS/config/biomeos-session.conf" << 'SESSION'
# biomeOS session configuration
# For SteamOS/Gamescope integration:
# 1. Copy biomeos.desktop to /usr/share/wayland-sessions/
# 2. Select biomeOS from login screen
# 3. Gamescope wraps the Easel as the compositor
#
# For standalone boot:
# 1. Install on bare metal or VM
# 2. Set boot.sh as .xinitrc or Wayland session
# 3. biomeOS IS the desktop environment
#
# SteamOS path:
# SteamOS 3.x = Arch Linux + KDE Plasma + Gamescope
# biomeOS replaces KDE session with Easel session
# Gamescope (Valve's compositor) wraps Easel
# Steam Deck becomes a biomeOS device
SESSION
echo "  ✓ session config"

echo ""
echo "═══════════════════════════════════════════"
echo "  💥 FISSION COMPLETE 💥"
echo ""
echo "  biomeOS installed at: $HOME/biomeOS/"
echo "  $COUNT organism binaries (native ELF x64)"
echo "  NO WoW64. NO RIBOSOMES. SMOOTH ER."
echo ""
echo "  To boot: ~/biomeOS/boot.sh"
echo "  To make SteamOS session:"
echo "    sudo cp ~/biomeOS/config/biomeos.desktop \\"
echo "      /usr/share/wayland-sessions/"
echo "═══════════════════════════════════════════"
