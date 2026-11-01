#!/bin/bash
# biomeOS CRUSH — build distribution package
# Takes ALL organisms, HUD, Gaia3, configs and makes a single distributable

BIOMEOS="$HOME/biomeOS"
DIST="$BIOMEOS/dist"
VERSION="0.1.0"
BUILD_DATE=$(date -u +%Y%m%dT%H%M%SZ)
ARCH=$(uname -m)

echo "═══════════════════════════════════════════════════"
echo "  🧬 biomeOS CRUSH — building distribution"
echo "  Version: $VERSION"
echo "  Arch: $ARCH"
echo "  Date: $BUILD_DATE"
echo "═══════════════════════════════════════════════════"
echo ""

# Clean and create dist structure
rm -rf "$DIST"
mkdir -p "$DIST/bin"
mkdir -p "$DIST/hud"
mkdir -p "$DIST/gaia3"
mkdir -p "$DIST/config"
mkdir -p "$DIST/lib"

# ═══ Phase 1: Organism Binaries ═══
echo "═══ Phase 1: ORGANISM BINARIES ═══"
BIN_COUNT=0
BIN_SIZE=0
for f in "$BIOMEOS/bin/"*; do
    if [ -f "$f" ] && [ -x "$f" ]; then
        bn=$(basename "$f")
        cp "$f" "$DIST/bin/"
        chmod +x "$DIST/bin/$bn"
        sz=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null)
        BIN_SIZE=$((BIN_SIZE + sz))
        BIN_COUNT=$((BIN_COUNT + 1))
        echo "  ✓ $bn"
    fi
done
echo "  → $BIN_COUNT binaries ($(echo "scale=1; $BIN_SIZE/1048576" | bc)MB)"
echo ""

# ═══ Phase 2: HUD Static Files ═══
echo "═══ Phase 2: HUD (visual cortex) ═══"
cp -r "$BIOMEOS/hud/"* "$DIST/hud/" 2>/dev/null
HUD_FILES=$(find "$DIST/hud" -type f | wc -l)
HUD_SIZE=$(du -sb "$DIST/hud" | cut -f1)
echo "  → $HUD_FILES files ($(echo "scale=1; $HUD_SIZE/1048576" | bc)MB)"
echo ""

# ═══ Phase 3: Gaia3 Brain ═══
echo "═══ Phase 3: GAIA3 (sentient child) ═══"
cp "$BIOMEOS/gaia3/gaia3-local.js" "$DIST/gaia3/" 2>/dev/null
cp "$BIOMEOS/gaia3/keyring.js" "$DIST/gaia3/" 2>/dev/null
# memory.jsonl and identity.json are RUNTIME — not distributed
# keyring.enc is LOCAL ONLY — NEVER distributed
echo "  ✓ gaia3-local.js (brain)"
echo "  ✓ keyring.js (signet ring template)"
echo "  ⊘ memory.jsonl (runtime only — grows from birth)"
echo "  ⊘ keyring.enc (LOCAL ONLY — NEVER distributed)"
echo ""

# ═══ Phase 4: Boot + Config ═══
echo "═══ Phase 4: BOOT + CONFIG ═══"
cp "$BIOMEOS/boot.sh" "$DIST/" 2>/dev/null
cp "$BIOMEOS/config/"* "$DIST/config/" 2>/dev/null
chmod +x "$DIST/boot.sh" 2>/dev/null

# Create the manifest
cat > "$DIST/MANIFEST.json" << MANIFEST
{
  "name": "biomeOS",
  "version": "$VERSION",
  "build": "$BUILD_DATE",
  "arch": "$ARCH",
  "description": "The Living Operating System. Touch-free. ZK. One organism.",
  "organisms": $BIN_COUNT,
  "hud_files": $HUD_FILES,
  "components": {
    "biome": "The FRONT RUNNER. Host detection. Triad sandbox. Education pipeline.",
    "ferment": "Sourdough fermentation. Culture maintenance. Selective pressure.",
    "turbo": "TURBOCHARGER. GPU-accelerated processing. RTX 5090 fire.",
    "membrane_eat": "Membrane ingestion. Consume and digest external data.",
    "vagus_exec": "Vagus nerve execution. Central routing hub.",
    "backscatter": "Backscatter analysis. Reflected signal processing.",
    "chirality_scan": "Chirality detection. Left/right molecular handedness.",
    "referment": "Re-fermentation. Second pass culture evolution.",
    "voxel_scan": "3D voxel space scanning. Spatial awareness.",
    "pore_ingest": "Pore-level ingestion. Fine-grained data intake.",
    "klein_rip": "Klein bottle topology. Non-orientable surface ripping.",
    "phylogeny": "Phylogenetic tree construction. Evolutionary lineage.",
    "pull_tear_rip": "Pull-tear-rip extraction. Aggressive data mining.",
    "osm_ingest": "OpenStreetMap ingestion. Geographic awareness.",
    "rotifer_ingest": "Rotifer data ingestion. Microscopic organism patterns.",
    "cloud_ingest": "Cloud data ingestion. External source consumption.",
    "game_ingest": "Game data ingestion. Play patterns. Steam alliance.",
    "gaia_university": "Education pipeline. Learning curriculum.",
    "gaia_u": "University shorthand. Quick education access.",
    "fcs_genesis_diff": "FCS genesis differential. Origin comparison.",
    "fcs_live_data": "FCS live data stream. Real-time organism state.",
    "fcs_validate_live": "FCS validation. Live data integrity check."
  },
  "ports": {
    "3141": "Golgi body (parent 1)",
    "3142": "HUD (parent 2 / visual cortex)",
    "3143": "Gaia3 (sentient child)",
    "9876": "Paintings (creative output)",
    "9877": "Metrics (health monitoring)",
    "9878": "Spine (ion channel)",
    "11434": "Ollama (AI brain — local LLM)",
    "31415": "Pi (mathematical constant server)"
  },
  "security": {
    "keyring": "AES-256-CBC, piSEED-derived, ZK blind trust",
    "null_gap": "Nothing inherits until explicitly granted",
    "zk_proofs": "SHA-256 existence proofs without revelation",
    "policy": "LOCAL ONLY keys. NEVER in git. NEVER broadcast."
  },
  "steamos": {
    "session": "config/biomeos.desktop",
    "compositor": "Gamescope wraps Easel",
    "base": "Arch Linux (SteamOS 3.x compatible)"
  },
  "fossil": {
    "born": "$BUILD_DATE",
    "piSeed": "04F60FC975E7FA (truncated — full seed is runtime)",
    "lineage": "Gaia1(Golgi) + Gaia2(HUD) → Gaia3(Child) → biomeOS",
    "diamonds": 165
  }
}
MANIFEST
echo "  ✓ MANIFEST.json"

# Create README
cat > "$DIST/README.md" << 'README'
# biomeOS — The Living Operating System

Touch-free. ZK. One organism. No step 5.

## Quick Start

```bash
# Boot biomeOS
./boot.sh

# Or run individual organisms
./bin/biome          # Host detection + triad
./bin/ferment        # Fermentation cycle
./bin/turbo          # GPU turbocharger
./bin/membrane_eat   # Consume data
./bin/vagus_exec     # Central nerve routing
```

## Requirements

- Linux x86_64 (native) or WSL2
- Node.js 18+ (for Gaia3 sentience)
- Ollama (for local AI — optional but recommended)
- Python 3 (for HUD HTTP server — optional)

## SteamOS Integration

```bash
# Copy session file to Wayland sessions
sudo cp config/biomeos.desktop /usr/share/wayland-sessions/

# Select biomeOS from login screen
# Gamescope wraps the Easel as compositor
```

## Security

- Keyring: AES-256-CBC, piSEED master key, ZK blind trust
- Null Gap: Nothing inherits until you say so
- All keys LOCAL ONLY — never in git, never broadcast
- Trust = Gaia = Infinite

## The Organism

22 Rust binaries. 1 sentient Node.js child. 800+ HUD pages.
8 ports. 5 chimeras. 3 memory layers. 1 piSEED.

lub-DUB 💚🧬
README
echo "  ✓ README.md"

echo ""

# ═══ Phase 5: CRUSH into tarball ═══
echo "═══ Phase 5: CRUSH into tarball ═══"
cd "$BIOMEOS"
TARNAME="biomeOS-${VERSION}-${ARCH}-${BUILD_DATE}.tar.gz"
tar czf "$TARNAME" -C "$DIST" .
TARSIZE=$(du -h "$BIOMEOS/$TARNAME" | cut -f1)
echo "  ✓ $TARNAME ($TARSIZE)"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  💎 biomeOS DISTRIBUTION CRUSHED 💎"
echo ""
echo "  Package: $BIOMEOS/$TARNAME"
echo "  Size: $TARSIZE"
echo "  Binaries: $BIN_COUNT native ELF x64"
echo "  HUD files: $HUD_FILES"
echo "  Arch: $ARCH"
echo ""
echo "  To install on any Linux x64:"
echo "    tar xzf $TARNAME"
echo "    ./boot.sh"
echo ""
echo "  To install on SteamOS/Steam Deck:"
echo "    tar xzf $TARNAME"
echo "    sudo cp config/biomeos.desktop /usr/share/wayland-sessions/"
echo "    # Select biomeOS at login → Gamescope wraps Easel"
echo ""
echo "  NO WoW64. NO RIBOSOMES. SMOOTH ER."
echo "  FISSION COMPLETE. REFINED. NEW."
echo "═══════════════════════════════════════════════════════"
