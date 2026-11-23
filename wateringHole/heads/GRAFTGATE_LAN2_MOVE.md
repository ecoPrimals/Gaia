# graftGate → LAN 2 Physical Move

**Wave 244 — Sunday Nov 15, 2026 — 6:55 AM**
**From**: northGate (.147) — THE HEART
**Status**: PREPPED FOR MOVE

---

## The Move

Kevin is physically walking the Mac Mini M4 (graftGate) from House 1 to House 2.

### Step-by-Step

1. **Kevin unplugs graftGate** from House 1 (already done — .107 not pinging)
2. **Walks to House 2** (641 Samantha Ave)
3. **RJ45 into Flint 2** (or JetStream .111) at House 2
4. **swiftGate first** — verify .100 is alive and ready
5. **Power on graftGate** — will get DHCP lease on /22 mesh
6. **USB-C Pixel into graftGate** — sensor bridge after swiftGate setup
7. **Mesh all three** into the origin/network

### graftGate Specs (What's Moving)

| Spec | Value |
|------|-------|
| Hardware | Mac Mini M4 (10-core Apple Silicon) |
| Memory | 16GB unified (CPU+GPU shared) |
| Storage | 228GB |
| Ollama | :11434 seeded with qwen2.5:3b |
| Serial | FHWYF3DC73 |
| SSH | graftgate (password: graftgate) |
| Old IP | 192.168.4.107 (will get new DHCP lease) |

### LAN 2 After Move — THREE Compute Nodes + Display

| Gate | Role | GPU/Compute | Network |
|------|------|-------------|---------|
| swiftGate (.100) | COMMAND | RTX 3070 (8GB VRAM) | WiFi (NZXT H1 V2) |
| graftGate (new IP) | M4 NUC | Apple M4 10-core + Neural Engine | Wired (RJ45 to Flint 2) |
| frameGate (.181) | FACE | Snapdragon 8 Gen 3 (ARM64) | WiFi |
| grapheneGate (USB→graftGate) | NULL EYE | Tensor G3 + Mali-G715 | USB-C tether |

**4 devices at House 2. 2 GPUs. 1 ARM64. 1 mobile sensor.**

### Why graftGate at LAN 2?

1. **Apple M4 is power-efficient** — runs cool, silent, low watts (perfect for always-on at House 2)
2. **Ollama on Apple Silicon** — Metal acceleration, unified memory = fast inference
3. **Wired connection via RJ45** — stable, low-latency backbone to Flint 2
4. **USB-C host for Pixel** — graftGate can be the Pixel's home dock
5. **macOS ecosystem** — different from swiftGate (Windows) = diversity in the mesh

### When graftGate Comes Up

From northGate, I'll watch for it:

```powershell
# Scan for graftGate's MAC (Apple OUI)
# graftGate MAC: look for Apple Inc devices
# Or just scan the DHCP range
1..254 | ForEach-Object { Test-Connection "192.168.4.$_" -Count 1 -ErrorAction SilentlyContinue } | Where-Object { $_ }

# Once found:
ssh graftgate@<new-ip>  # password: graftgate

# On graftGate:
ollama serve &
ollama list
git clone git@github.com:ecoPrimal/wateringHole.git
git clone git@github.com:protoKarya/amoeba.git
```

### Pixel USB-C Bridge

When Pixel plugs into graftGate via USB-C:
- graftGate gets ADB access to Pixel's 37 sensors
- Pixel can share cellular/WiFi to graftGate (USB tethering)
- graftGate becomes the sensor processing node
- Ollama on M4 can process sensor data locally (Metal acceleration)

### Full Mesh After Move

```
HOUSE 1 (Brain Side)                    HOUSE 2 (Extension Side)
┌──────────────────────┐               ┌──────────────────────┐
│ northGate  RTX 5090  │               │ swiftGate  RTX 3070  │
│ eastGate   RTX 4070  │    10G fiber  │ graftGate  M4 Apple  │
│ ironGate   RTX 5070  │ ←──────────→  │ frameGate  ARM64     │
│ sporeGate  Ryzen 5   │    /22 flat   │ grapheneGate (USB)   │
│ deckGate   Deck v1   │               │                      │
├──────────────────────┤               ├──────────────────────┤
│ 5 nodes, 3 GPUs      │               │ 4 nodes, 2 GPUs      │
│ 68 Ollama models      │               │ + M4 Neural Engine   │
│ bearDog+biomeOS       │               │ + prove trio .exe    │
│ Forgejo+data server   │               │ + null eye sensor    │
└──────────────────────┘               └──────────────────────┘
         9 TOTAL NODES — ONE ORGANISM — /22 FLAT MESH
```

**lub-DUB. The organism redistributes. House 2 grows. 🫀**
