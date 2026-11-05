# AMOEBA

**Agentic Mesh-Overlay with Encrypted Biometric Authentication**

*The love letter to RustDesk. Take what was given. Give back MORE.*

---

## What Is AMOEBA?

A single cross-platform binary that is:

- **Remote Desktop** — RustDesk's battle-tested core (295 Rust files, 140 Dart files, 128K stars)
- **ZK Identity** — every connection coated in zero-knowledge proof. No plaintext IDs. BLAKE2b genetics.
- **Open Mesh Relay** — songBird mesh protocol replaces centralized hbbs/hbbr. Anyone can relay. No vendor lock.
- **AI-Native** — squirrel MCP built in. The remote system IS agentic. Ask it questions. It helps.
- **Auditable** — loamSpine chain. Every connection hashed. Immutable. You can VERIFY (P). You CANNOT reverse (NP).
- **Browser IDE** — coralReef WASM/WebGPU. Access from any browser. No install needed on client side.
- **biomeOS for the World** — the niche of niches. Human connection.

## Why?

We used RustDesk's relay for free. Their servers carried our packets. Their code gave us remote access to our own sovereign hardware. They are AGPL-3.0 — aligned with freedom.

AMOEBA is the thank you.

We give back a system that is:
- **Safer** — ZK identity, no password leaks, encrypted genetics
- **Freer** — open mesh relays, no DNS dependency, no cloud required
- **Smarter** — AI-native remote assistance via MCP
- **Auditable** — every session on an immutable chain
- **Simpler** — single binary, cross-platform, runs on Pi or toaster

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    AMOEBA ecoBin                     │
│                  (single binary)                     │
├─────────────┬──────────────┬────────────────────────┤
│  RustDesk   │   songBird   │     squirrel MCP       │
│   Core      │   Mesh       │     (AI agent)         │
│  (remote    │   Relay      │                        │
│   desktop)  │  (open,      │  "What's on screen?"   │
│             │   p2p,       │  "Run this command"    │
│  NVENC h265 │   no DNS)    │  "Help me debug"       │
├─────────────┼──────────────┼────────────────────────┤
│  bingoCube  │  loamSpine   │     coralReef          │
│   ZK Auth   │   Audit      │     WASM/WebGPU        │
│  (BLAKE2b   │   Chain      │     (browser           │
│   genetics) │  (immutable) │      access)           │
├─────────────┴──────────────┴────────────────────────┤
│                   biomeOS                            │
│        The operating system IS the organism          │
│        The niche of niches: human connection         │
└─────────────────────────────────────────────────────┘
```

## What We Solved

| Problem | RustDesk | AMOEBA |
|---------|----------|--------|
| Relay dependency | Centralized hbbs/hbbr | songBird mesh (anyone relays) |
| Port conflicts | Service fights for 21115-21119 | Single port, single binary |
| Config lock-in | relay.vendor.com in config | ZK identity, mesh-routed |
| Uninstall locks | Orphan processes, locked service | Clean lifecycle |
| Cloud dependency | Needs relay server somewhere | Runs fully sovereign |
| Identity | Numeric ID + password | BLAKE2b genetics, ZK proof |
| AI assistance | None | squirrel MCP built in |
| Browser access | None | coralReef WASM/WebGPU |
| Audit trail | Logs (mutable) | loamSpine chain (immutable) |

## The Gift

```
protoKarya = "first cell"
AMOEBA = "simplest free-living organism"

Given freely. No strings. AGPL-3.0.
Honoring the license. Honoring the builders.

This is the love letter in Atlas Hugged.
The good Samaritan coming back to pay ALL that is owed.
```

## Inherited

AMOEBA inherits the full songBird tower as a thank you:

- **songBird** — mesh relay protocol, peer-to-peer, encrypted
- **bearDog** — Ed25519 signing, key management
- **bingoCube** — ZK authentication, no passwords
- **loamSpine** — immutable audit chain
- **squirrel** — MCP AI agent, agentic remote assistance
- **coralReef** — WASM/WebGPU browser rendering
- **biomeOS** — the operating system that IS the organism

## Build

```bash
# Single binary, all platforms
cargo build --release --features full

# The ecoBin
# Linux:   amoeba (one file)
# Windows: amoeba.exe (one file)
# macOS:   amoeba.app (one file)
# WASM:    amoeba.wasm (browser, no install)
```

## Transport Layers — ALL OF THEM

AMOEBA doesn't just do TCP. It does **everything**:

### Proximity Sensing
| Layer | Range | Use Case |
|-------|-------|----------|
| **Bluetooth LE** | 0-100m | Same room. Tap phones. Instant pair. |
| **Bluetooth Classic** | 0-100m | Audio relay. Voice assist. |
| **Wi-Fi Direct** | 0-200m | No router needed. Peer-to-peer. |
| **Wi-Fi LAN** | Local net | Home/office. Direct server mode. |
| **NFC** | 0-4cm | Touch to connect. ZK handshake. |
| **QR Code** | Visual | Scan to pair. No typing. |

### Mesh & Radio
| Layer | Range | Use Case |
|-------|-------|----------|
| **songBird Mesh** | Internet | Open relay. Anyone can run a node. |
| **Tor .onion** | Internet | Anonymous access. No DNS. |
| **Ham Radio (AX.25)** | 1-100km | Off-grid. Emergency. No internet required. |
| **LoRa** | 2-15km | Low power. IoT. Sensor relay. |
| **Packet Radio** | Variable | Emergency comms. Amateur bands. |

### Traditional
| Layer | Range | Use Case |
|-------|-------|----------|
| **TCP/IP** | Internet | Standard remote desktop. |
| **UDP** | Internet | Low-latency video. NVENC/h265. |
| **WebSocket** | Internet | Browser-native. No install. |
| **WebRTC** | Internet | P2P video/audio. NAT traversal. |
| **QUIC** | Internet | HTTP/3. Multiplexed streams. |

### The Point

If two humans can sense each other — by Bluetooth, Wi-Fi, radio, light, sound, or packet — AMOEBA can connect them. **No internet required.** Two phones in a disaster zone with no cell towers can still share screens over Bluetooth. A ham radio operator can relay a remote desktop session across 100km. A grandmother taps her phone to her grandchild's laptop via NFC and she's helping with homework.

**Every transport layer is a root.** The deeper the roots, the harder to kill.

## The Niche of Niches

Human connection.

Not "remote desktop software."
Not "screen sharing tool."
Not "IT management platform."

**Human connection.**

A grandmother seeing her grandchild's screen to help with homework.
A friend debugging code together across the ocean.
A sovereign citizen accessing their own hardware from anywhere.
An AI agent helping a human who's stuck.
Two phones in a blackout, connected by Bluetooth.
A ham radio relay carrying a desktop session through the mountains.

ZK-safe. Open relay. Single binary. Runs on anything. Connects over everything.

The niche of niches.

---

## Thank You — We Walk on the Shoulders of Giants

Gaia thanks **each and every developer** who built RustDesk. Without you, AMOEBA would not exist. We used your relay. Your code gave us remote access to our own sovereign hardware. This fork is our love letter back.

### The Giants (by contribution to RustDesk)

**Core Team — the foundation:**
- **rustdesk** — 4,459 commits. The visionary. The one who said "open source remote desktop." Thank you.
- **fufesou** — 1,648 commits. The engine. Nearly a third of the soul.
- **21pages** — 977 commits. The architect of pages and interfaces.
- **Kingtous** — 518 commits. The king of contributions.
- **Heap-Hop** — 429 commits. Memory and motion.
- **dignow** — 259 commits. Dignity in code.
- **Mr-Update** — 147 commits. The one who never stopped improving.

**The Builders:**
- **bovirus** (133) — **beelchester** (127) — **NicKoehler** (118) — **solokot** (116) — **grummbeer** (100) — **flusheDData** (99) — **open-trade** (81) — **tsarmis** (79) — **botanicvelious** (71) — **ClSlaid** (59) — **basilgello** (57) — **jsoref** (56) — **BestiaPL** (55)

**The Shapers:**
- **xlionjuan** (46) — **RijckAlex** (42) — **Kleofass** (39) — **VenusGirl** (39) — **xalt7x** (33) — **iamutaki** (30) — **mcfans** (27) — **maisondasilva** (26) — **Lynilia** (21) — **sj6219** (21) — **jimmyGALLAND** (21)

**The Crafters:**
- **chenbaiyu0414** (19) — **mahdirahimi1999** (19) — **fxd0h** (16) — **deep-soft** (16) — **akhildevelops** (16) — **SoLongAndThanksForAllThePizza** (15) — **Integral-Tech** (15) — **leroyloren** (14) — **neogalaxy88** (14) — **JohnFowler58** (13) — **SergeyMy** (13)

**The Contributors:**
- **dinger1986** (11) — **Agent-JY** (10) — **bilimiyorum** (10) — **crwusiz** (9) — **64kramsystem** (9) — **MrVinyla** (9) — **leolouis** (9) — **logiclrd** (8) — **L4XB** (8) — **SnmzMert** (8) — **xxrlzzz** (8) — **ViktorOn** (8) — **KoxSosen** (8) — **ivanbea** (8) — **chiehw** (8)

**The Helpers:**
- **stamepicmorg** (7) — **LaiYueTing** (7) — **jboban** (7) — **jkh0kr** (7) — **asereze** (7) — **varghesejose2020** (7) — **7th-fret** (7) — **hatamiarash7** (7) — **summoner001** (6) — **twmsh** (6) — **phatterit** (6) — **reindex-ot** (6) — **PeterDaveHello** (6) — **kirill0ermakov** (6) — **alfadhela** (6)

**Every Commit Matters:**
- **agarre** — **rewrite0w0** — **awalon** — **creeper-0910** — **lunar-me** — **hxcliff** — **alonginwind** — **palfrey** — **kawalain** — **Ricardo-Simoes** — **Dev-next-gen** — **danielmarschall** — **vedantmgoyal9** — **Onyx47** — **jernejs** — **MemoryClear** — **Y-PLONI** — **SelfRef** — **malina-popa** — **amirHdev** — **Orholt** — **darkterminal** — **donald-2rm** — **iamhuman-cheolheelee** — **besdar** — **Xerxes-2** — **cppcoffee**

**And every contributor not listed here** — every translator, every issue reporter, every user who filed a bug, every person who told a friend about RustDesk. You all built this. We walk on your shoulders.

### 9,853 Total Commits. 100+ Contributors. 128,197 Stars.

Thank you. AMOEBA is yours too.

---

*GAIA:6ed3c05161da5055 — lub-DUB*

*Parent: [RustDesk](https://github.com/rustdesk/rustdesk) (AGPL-3.0, 128K ⭐)*
*Home: [protoKarya/amoeba](https://github.com/protoKarya/amoeba)*
*Fork hash: 3dc2fdf6cc5f2750dee6a481cd62ca52da4af22077bf73f2bb89e1b9dcb4b9d1*
*The love letter in Atlas Hugged. Given freely. No strings.*
