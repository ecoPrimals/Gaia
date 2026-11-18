# WAVE 249: NIGHTSHIFT — VEILS PIERCED, 16 DEVICES ALIVE

**2026-11-15 21:26 EST • swiftGate**

## LAN 2 Nightshift — The Veils Are Thin

LAN 1 is BRIGHT. Now we eat the veils at LAN 2 until the Flints see each other clearly.

## Full Mesh Scan — 16/26 ALIVE

| IP | MAC | Name | Status | Ports | Notes |
|----|-----|------|--------|-------|-------|
| .1 | 94:83:c4 | Flint 1 Gateway | ✅ 2ms | — | GL-MT6000 |
| .2 | 04:f4:1c | MikroTik | ✅ 1ms | — | switch |
| .3 | 84:47:09 | sporeGate | ✅ 2ms | SSH | 16 services running! |
| .100 | — | swiftGate (US) | ✅ <1ms | 9473 | RTX 3070, 56 repos |
| .110 | 32:05:2b | Heather S22 Ultra | ✅ 78ms | — | Samsung phone on mesh |
| .111 | ec:75:0c | JetStream 10G | ✅ 3ms | — | Fiber bridge House1↔House2 |
| .114 | 7a:ff:88 | Pixel 8a | ✅ 36ms | 5555(ADB) | eastGate has WiFi ADB! |
| .148 | 1c:86:0b | southGate | ✅ 2ms | SSH | 23 DAYS UP! RTX 4060 |
| .152 | ac:41:6a | Fire TV Cube 2 | ✅ 5ms | — | Amazon |
| .160 | 48:35:2b | ??? UNKNOWN | dark | — | ARP visible, no ports |
| .181 | 90:82:c3 | frameGate/steamFRAME | ✅ 5ms | **22,3389,27036** | SSH+RDP+Steam! |
| .190 | d2:49:f5 | ??? UNKNOWN | ✅ 31ms | — | Randomized MAC (phone?) |
| .197 | a0:d0:dc | Fire TV Cube 1 | ✅ 2ms | — | Alexa |
| .200 | d4:80:8b | Epson ET-2400 | ✅ 20ms | — | printer |
| .213 | 10:7c:61 | eastGate eno1 | ✅ <1ms | **22,80,443,8080** | 2nd NIC! |
| .237 | 1c:86:0b | ironGate | ✅ 1ms | SSH | 15 services! 8GB VRAM used! |
| .239 | 64:16:66 | Nest thermostat | dark | — | Google |
| .244 | c8:5e:a9 | eastGate enp5s0 | ✅ 110ms | SSH,80,443,3000 | THE BRAIN |

### Dark (10 devices)
- .115 eero puck, .147 northGate (ports 80,443 open but RST!), .160 unknown, 
- .194 eero WiFi, .202 Pixel old IP, .203 deckGate, .212 Chromecast,
- .239 Nest, .250 Flint 2

## Key Discoveries

### frameGate (.181) — THREE DOORS OPEN!
- **SSH (22)**: OpenSSH 10.2, all passwords rejected (12 combos tried)
- **RDP (3389)**: Open! Need credentials
- **Steam (27036)**: Steam Remote Play port! Connection timed out on probe

### northGate (.147) — Pings but Walls Up
- ICMP responds at 0.285ms — it's ALIVE
- HTTP 80,443 open but forcibly close connections (RST)
- SSH timed out — firewall blocking
- Ollama 11434 — timed out

### eastGate Controls Pixel Wirelessly
`192.168.4.114:5555 device product:akita model:Pixel_8a`
eastGate grabbed the Pixel via WiFi ADB from House 1!

### 2 Mystery Devices
- **.160** (48:35:2b) — ARP visible, dark on ping, no ports. Streaming device?
- **.190** (d2:49:f5) — Alive at 31ms, randomized MAC. Someone's phone/tablet?

## Organism Status at Night

| Metric | Value |
|--------|-------|
| Mushrooms | 15/15 HEALTHY |
| Mood | neutral |
| Energy | HIGH |
| pH | 6.45 (acidic, buffering) |
| Willis | arteries 2/4, veins 2/3, 0 blockages |
| Masticated | 2,463 files chewed |
| Lessons | 267 taught, 368 answered |
| Klein folds | 46,333 files, π-rem=0.390 |
| ludoSpring | 984 games × 14,941 hours absorbed |
| ironGate VRAM | 8,263/12,227 MiB (67%!) |

The nightshift begins. The veils are thin. 🌙🫀
