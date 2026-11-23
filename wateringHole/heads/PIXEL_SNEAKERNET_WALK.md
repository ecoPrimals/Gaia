# Pixel Sneakernet Walk — ZK Smash & Redox

**Wave 244 — Sunday Nov 15, 2026 — 7:34 AM**
**From**: northGate (.147) — THE HEAD
**For**: Kevin, carrying the Pixel between gates

---

## Pixel is LOADED

| What | Where on Pixel | Count |
|------|---------------|-------|
| Identity | /sdcard/gaia/identity/ | 6 files |
| Sensorium | /sdcard/gaia/sensorium-staging/ | 15 scripts |
| Sneakernet heads | /sdcard/gaia/sneakernet/heads/ | 38 files |
| Sneakernet plasmids | /sdcard/gaia/sneakernet/plasmids/ | 3 files |
| Scripts | /sdcard/gaia/scripts/ | 2 files |
| Brain | /sdcard/gaia/brain/ | heart-pull.json |
| Pulse | /sdcard/gaia/pulse/ | anchor-pulse.json |
| Battery | 100% | USB powered |
| Storage | 102 GB free | |
| WiFi | GAIA (5GHz, -21dBm, 1134Mbps, /22 flat) | |

## Gate Status RIGHT NOW

| Gate | IP | Ping | SSH | Ollama | Notes |
|------|-----|------|-----|--------|-------|
| eastGate | .244 | ✅ | — | :11436✅ | BRAIN — all 4 ports open |
| sporeGate | .3 | ✅ | :22✅ | — | DNS + forge, wired to Flint |
| ironGate | .237 | ✅ | :22✅ | :11434✅ | FORGE 2 — 18 models |
| swiftGate | .100 | ❌ | :22❌ | — | WiFi — may be asleep |
| southGate | .148 | ✅ | — | — | iPhone home phone |
| frameGate | .181 | ✅ | :22✅ | — | FACE — WiFi 7 AP on 6GHz! |
| deckGate | .197 | ✅ | — | — | Mounted display |
| graftGate | ??? | ❌ | — | — | MOVING — not on mesh yet |
| eero | .115 | ❌ | — | — | WiFi mesh extender |
| Flint 2 | .250 | ✅ | — | — | House 2 switch |

## The Walk

### STEP 1: Here at northGate (DONE)
- [x] All data staged on Pixel
- [x] Tethering settings opened on Pixel screen
- [x] 38 heads + 3 plasmids pushed
- [x] null-eye.sh + gate-bootstrap.sh pushed
- [x] Mesh mapped (21 devices, 7 SSIDs)
- [x] eero puck identified (.115, c8:e3:06 = Amazon/Apple OUI)
- [x] frameGate WiFi 7 AP discovered (frame_EF006FC9, 802.11be, 6GHz!)

### STEP 2: Unplug from northGate, walk to House 2
- Pixel stays on GAIA WiFi (/22 flat mesh)
- As Kevin walks, WiFi may hop between APs
- Pixel keeps seeing the mesh from anywhere

### STEP 3: USB-C into graftGate (Mac Mini M4)
1. Plug Pixel USB-C into graftGate
2. On Pixel: Settings > Network > Hotspot & Tethering > USB Tethering ON
3. graftGate gets network via USB-C tether (appears as usb0 or en-something on macOS)
4. On graftGate terminal:
   ```bash
   # Check network
   ifconfig | grep -A2 "en\|usb"
   
   # Sync repos
   cd ~/wateringHole && git pull origin main --no-rebase --no-edit
   cd /opt/Gaia && git pull origin main --no-rebase --no-edit
   
   # Start ollama
   ollama serve &
   ollama list
   
   # Verify identity
   hostname  # should be graftgate
   ssh eastgate@192.168.4.244  # test mesh reach through Pixel tether
   ```
5. Copy sneakernet files FROM Pixel:
   ```bash
   # If ADB tools available on macOS:
   adb pull /sdcard/gaia/sneakernet/ ~/gaia-sneakernet/
   
   # Or just access via file browser — Pixel shows as USB drive
   ```

### STEP 4: USB into swiftGate (NZXT H1 V2)
1. Unplug from graftGate → plug into swiftGate
2. USB tethering should auto-enable (already toggled ON)
3. On swiftGate terminal:
   ```bash
   # Check network — swiftGate already has WiFi but tether is backup
   ip addr show
   
   # Sync
   cd ~/wateringHole && git pull github main --no-rebase --no-edit
   cd ~/Gaia && git pull origin main --no-rebase --no-edit
   
   # Check tissue models
   ollama list
   curl http://localhost:11434/api/tags
   
   # Verify the prove trio
   ls ~/primalSpring/target/release/prove-*
   ```

### STEP 5: Return or stay
- If returning to House 1: plug back into northGate
- If staying at House 2: leave Pixel tethered to graftGate as sensor bridge
- Either way: Pixel on /22 mesh, null eye active

## ZK Smash — What Gets Resolved

"ZK smash" = zero each gate's stale state and redox fresh:
- **Clear stale ARP** — each gate re-discovers its neighbors
- **Pull latest code** — all gates on same commit
- **Verify identity** — each gate responds to its hostname + password
- **Test mesh reach** — each gate can ping ALL other gates
- **Ollama inventory** — confirm models on each gate
- **biomeOS notice** — primals in apoptosis, restart pending

## USB Tether = Pixel IS the WAN Edge (temporarily)

When Pixel tethers to a gate:
```
Internet → Pixel (WiFi /22 mesh) → USB tether → gate
```
The Pixel becomes that gate's network adapter.
When Pixel gets Mint Mobile eSIM: Pixel becomes PERMANENT WAN edge.
Bidirectional: WiFi inward, cellular outward.

---

**The Pixel is the key. Kevin carries Gaia's eye AND network in his pocket. 🫀**
