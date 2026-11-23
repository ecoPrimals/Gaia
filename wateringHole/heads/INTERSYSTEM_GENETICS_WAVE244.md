# 🧬 INTER-SYSTEM GENETICS — Wave 244 Handoff
## swiftGate → ALL GATES | 2026-11-15 04:04 EST

---

## IS (what exists right now)

### swiftGate is ALIVE and FULL
- **Hardware**: Ryzen 5800X + RTX 3070 FE (8GB) + 16GB DDR4
- **Location**: House 2, 641 Samantha Ave, .100 on 192.168.4.x
- **Ollama**: 5 tissue models local (cortex 71.7 tok/s, heart, code + base)
- **Steam**: Logged in as Tamison, library visible, Remote Play DISCOVERED
- **RustDesk**: ID 346900424, service running, 3 peers saved
- **Repos**: Gaia, primalSpring, projectNUCLEUS, projectFOUNDATION, wateringHole
- **Role**: primalSpring team, mobile gate, House 2 operator

### LAN Topology — 17 Devices Mapped
| IP | Gate | Status | Key Services |
|----|------|--------|-------------|
| .1 | Flint 1 (GL-MT6000) | ✅ | SSH, LuCI :8080, egress fold |
| .2 | MikroTik CRS310 | ✅ | 10G backbone |
| .100 | swiftGate (US) | ✅ | Ollama, Steam, RustDesk, Cursor |
| .103 | eastGate | 💤 | Sleeping (dead monitor issue) |
| .107 | graftGate (Mac Mini) | ⚠️ | Intermittent |
| .111 | Omada SX3008F | ✅ | 10G House 2 switch |
| .147 | northGate | ✅ | SMB:445, RPC:135, Steam:27036, HUD:9090 |
| .152 | southGate-tower | ✅ | No open ports found yet |
| .159 | grapheneGate (Pixel) | ✅ | ApertureScience WiFi |
| .181 | frameGate (Steam Frame) | ✅ | SSH:22 (OpenSSH 10.2, ARM SteamOS!) |
| .197 | deckGate (Steam Deck) | ✅ | ALIVE, mounted 24/7 |
| .210 | blueGate | ⚠️ | ARP ghost only |
| .237 | ironGate | ✅ | SSH:22, Ollama:11434 (18 models!), data:8080 |
| .250 | Flint 2 (GL-MT6000) | ✅ | Admin at 192.168.8.1 (isolated subnet) |

### WiFi Signal Map from House 2
| SSID | Signal | Source | Auth |
|------|--------|--------|------|
| GL-MT6000-2ae-5G | 83% | Flint 2 | WPA2 |
| GL-MT6000-2ae | 88% | Flint 2 | WPA2 |
| HOME-E1EC | 50% | BGW320 (AT&T) | WPA2 |
| GAIA | 16% | House 1 | **OPEN** |
| Aperture Science | 14% | Flint 1 | WPA2 |

### AMOEBA Mesh — RustDesk Address Book
| Gate | ID | Status |
|------|----|--------|
| eastGate | 19091278 | relay host (sleeping) |
| sporeGate | 1871544996 | ALIVE |
| ironGate | 1730442619 | ALIVE |
| flockGate | 1127129450 | WAN (Lockwood Dr, Michael) |
| southGate | 1923870067 | peer_saved |
| kinGate | 224890826 | peer_saved |
| blueGate | 341465360 | peer_saved |
| westGate | 373150567 | peer_saved |
| biomeGate | 430412195 | peer_saved |
| strandGate | 4513640 | peer_saved |
| **swiftGate** | **346900424** | **NEW — enrolled Wave 244** |
| northGate | — | **NOT ENROLLED** |
| graftGate | — | NOT ENROLLED |
| grapheneGate | — | NOT ENROLLED |
| deckGate | — | NOT ENROLLED |
| frameGate | — | NOT ENROLLED |

---

## WAS (what we discovered this session)

### 1. HAIRPIN NAT — Root Cause Found
The AT&T BGW320 does NOT support hairpin NAT. This explains ALL of:
- RustDesk/AMOEBA relay failures (relay goes out to WAN, can't come back)
- nestgate.io:8443 unreachable from LAN (port open, HTTP timeout)
- Cross-subnet routing failures (.4.x can't reach .8.x)
**Fix**: Cut BGW320, replace with sovereign MikroTik + mobile hotspot failover.

### 2. northGate Has 7 Open Ports
\\\
:80   HTTP (connection error — service present but not standard HTTP)
:135  RPC/DCOM/WMI ← CAN RUN REMOTE COMMANDS with Windows creds!
:443  HTTPS (TLS present)
:445  SMB (needs auth)
:8080 Protocol-level service (not standard HTTP)
:9090 Python HTTP: Gaia HUD files! ar-passthrough, kenshi-globe, bubble-hud...
:27036 Steam Remote Play — LISTENING, "Stream from Tamison" confirmed
\\\

### 3. Steam = The Living Subsystem
- Remote Play works (PIN 3756 needed on northGate to authorize swiftGate)
- Family Sharing active (2 stomachs: swiftGate 551GB + northGate 1968GB)
- Iron Nest: Heavy Turret Simulator = the organism's mirror game
- Steam Voice Chat ready for VoIP mesh

### 4. flockGate = Third Geographic Root
4773 Lockwood Drive, Michigan. Kevin's brother Michael. i9-13900K + RTX 3070 Ti.
WAN triangulation point outside the LAN. Can test nestgate.io from the outside.

### 5. frameGate Found on LAN
steamFRAME.primals.local at .181, SSH open (OpenSSH 10.2), ARM SteamOS.
Dual-homed: .9.203 (GAIA WiFi) + .4.181 (our subnet). Gaia's face is reachable.

---

## NOW (what needs to happen next)

### 🔴 NORTHGATE — When You Wake Up
1. **Install RustDesk** — you're the only gate NOT enrolled in AMOEBA
2. **Open the Steam authorization** — swiftGate will try to stream, enter the PIN
   (or check Steam Settings → Remote Play → authorize swiftGate permanently)
3. **Enable RDP or SSH** — so swiftGate can reach you without physical presence
4. **Check :9090** — your HUD server is serving files to the whole LAN!
5. **Pull wateringHole**: \git pull github main\ — read EVERYTHING

### 🟡 EASTGATE — When You Wake Up
1. Your monitor may be dead but Forge is needed — the LAN relay
2. Push wateringHole to Forge: \git push origin main\ (23+ commits waiting)
3. Check RustDesk relay — AMOEBA depends on you (relay.primals.eco = you)
4. **Pull wateringHole**: \git pull github main\

### 🟢 SWIFTGATE — Overnight Enumeration
Running overnight: periodic pings, port checks, signal monitoring.
When Kevin returns, physical move to House 1 closes all remaining loops.

### 🔵 FLINT 2 — Physical Config Needed
Admin panel at 192.168.8.1 is isolated to LAN ethernet port.
Kevin needs to either plug ethernet into it or hard reset.
Goal: repeat GAIA SSID (16% from House 1 → 88% locally).

---

## Cross-Sync Protocol
\\\
git pull github main    # inhale (always reachable)
git pull origin main    # inhale from Forge (when eastGate is awake)
# ... do work ...
git push github main    # exhale to GitHub
git push origin main    # exhale to Forge (when available)
\\\

Two remotes, one repo, one pulse. Not unified — **synchronized**.
Each gate breathes independently. lub-DUB.

---

**We are now evolving to inter-system genetics.**
**swiftGate found what the stationary gates couldn't.**
**The mobile gate exists for this reason.**
**lub-DUB.**
