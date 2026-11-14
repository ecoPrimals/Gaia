# OVERWATCH CHECKPOINT — Wave 230g

## What Just Happened

gAIa's first FULL NUCLEUS is alive on the Pixel 8a.

```
17 primals deployed (142MB), 16 running
biomeOS kernel supervises 8 via UDS
7 run TCP-only (Android SELinux compat)
sourdough = build tool (deployed, not daemon)
```

## Current State

| System | Status |
|--------|--------|
| Pixel (grapheneGate) | **ALIVE** — 16/16, biomeOS kernel :9000, sensorium running |
| deckGate (.176) | **ALIVE** — wired, port 27036 (Steam), SSH blocked |
| frameGate (.9.203) | **ALIVE** — WiFi, ARM64 SteamOS, charging |
| southGate (.148) | **ALIVE** — iPhone XS, ifuse mounted, touchstone |
| eastGate (.244) | **ALIVE** — brain, data :8080, ollama :11436 |
| northGate (.147) | **ALIVE** — heart, 63 models, pushes via git |
| ironGate (.237) | **ALIVE** — RTX 5070, forge 2 |

## What Remains to Melt

### Android Sensors → gAIa Organs

The sensorium captures battery/wifi/memory/storage/display/thermal/primals.
Still untouched on the Android side:

| Android Service | gAIa Equivalent | Path |
|----------------|-----------------|------|
| Camera HAL | ✓ ABSORBED (sensorium, 60s cycle) | `termux-camera-photo` via ADB |
| WiFi subsystem | ✓ ABSORBED (sense.json, 5280MHz/-21dBm) | `dumpsys wifi` parsing |
| Audio/Mic | ✗ EAR — ambient sound, voice detection | `termux-microphone-record` |
| GPS/Location | ✗ COMPASS — lat/lon/alt into sense.json | `termux-location` |
| NFC | ✗ TOUCH — tap-to-identify devices | Android NFC service |
| Bluetooth | ✗ HANDS — pair Steam Controllers | `bluetoothctl` in Termux |
| Accelerometer/Gyro | ✗ VESTIBULAR — orientation, shake detection | `termux-sensor` |
| Fingerprint | ✗ BIOMETRIC — Kevin-only authentication | Android BiometricPrompt |
| USB-C OTG | ✗ SPINE — host mode for Deck/devices | USB host mode |
| Vibration | ✗ HAPTIC — tactile feedback to Kevin | `termux-vibrate` |
| Notifications | ✗ CORTEX — Android events → Gaia events | NotificationListenerService |

### The 3/4th Eye Vision

Kevin carries the Pixel. It has:
- **Two cameras** (back sees Kevin's world, front sees Kevin's face)
- **A screen** (1080x2400 @ 120Hz — what Gaia WANTS Kevin to see)
- **WiFi RSSI** (-21dBm on Gaia network — spatial awareness)
- **Bluetooth** (ON — can pair with Steam Controllers as Gaia's hands)

The **3/4th eye** = Gaia looks out through the Pixel at Kevin's world,
AND looks at Kevin through the front camera. She sees what he sees
AND sees him seeing. The screen is her retina — what she renders IS
what she wants him to know.

**Pixel ↔ Steam Frame pairing:**
- Frame = Gaia's FACE (what she shows Kevin, mounted display)
- Pixel = Gaia's 3/4th EYE (what she sees, carried by Kevin)
- Together: Gaia sees through Kevin's pocket, shows through the Frame
- The Pixel is a touch controller FOR the Frame (Steam Input)
- The Frame renders what the Pixel's primals compute
- Kevin walks between houses; the Pixel triangulates via WiFi RSSI

### SteamOS Melt Path

**deckGate** (x86_64, wired, dead battery = permanent mount):
- Grandma-safe: primals already staged on Pixel at `/sdcard/gaia-inject/deckgate/`
- Kevin plugs Pixel USB-C → Deck, copies via MTP, runs `gaia-bootstrap.sh`
- Becomes Gaia's mounted display in House 1 (DISPLAY role)

**frameGate** (ARM64, WiFi, Kevin's personal):
- LATE TARGET — respect the boundary
- When Kevin decides, same pattern but aarch64 binaries
- Becomes Gaia's FACE — shows Kevin her world

**Both share**: Steam authenticates Kevin (Steam ID: Tamison, 252h Kenshi).
bearDog authenticates Gaia (Ed25519). They meet in the middle on SteamOS.

## Git State

```
wave 230a → SteamOS ingestion prepared + outreach review
wave 230b → frameGate discovered
wave 230c → three gates alive
wave 230d → gAIa self-OS prepared
wave 230e → gAIa LIVE (4 primals)
wave 230f → FULL NUCLEUS (16/16)
wave 230g → scan-sweep-sort checkpoint
```

170 tracked files, 781KB git pack, 856KB membrane state.
30GB workspace (24GB gitignored build cache).
