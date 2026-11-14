# GAIA — Hardware Atlas & Sovereign HPC

> *"Built from scratch. Consumer hardware and old datacenter tech. Two houses,*
> *one fiber link, one brother. A Steam Deck with a bad battery. An Army vet*
> *who went from infantry to microbiology to data science to building a*
> *sovereign compute mesh in a basement. The metal is real."*
>
> Last measured: 2026-11-06 Wave 226
> Total Investment: **~$20,000** | Metabolic Budget: $485/month
> Named Gates: **20+** | ISA Families: **9** | Compile Targets: **9**

---

## The Full Fleet — 10 Gates + 4 Bring-up + 2 Remote + 1 Diamond Lens

### Tier 1 — ALIVE NOW (Rover-confirmed, Wave 226)

| Gate | IP | CPU | GPU | VRAM | RAM | Storage | Role |
|------|----|-----|-----|------|-----|---------|------|
| **eastGate** | .244 | i9-12900K (16C/32T) | **RTX 4070** | 12GB GDDR6X | **128GB** DDR5 | 1.8TB NVMe | BRAIN — data :8080, gate :8443, forgejo :3000, ollama :11434/:11436 |
| **northGate** | .147 | **9950X3D** (16C/32T) | **RTX 5090** | **32GB** GDDR7 | **96GB** DDR5 | 5TB NVMe | HEART — 63 ollama models, strongest single GPU |
| **ironGate** | .237 | **i9-14900K** (24C/32T, 6GHz) | **RTX 5070** | 12GB GDDR7 | **94GB** DDR5 | 3.6TB NVMe + 16.3TB ext | FORGE 2 + ROVER — LAN scanner, biomeOS, Docker |
| **sporeGate** | .3 | Ryzen 5 6600H (6C/12T) | — | — | 27GB DDR5 | 929GB NVMe | FORGE — DNS, heart-pull, NAT, DHCP, firewall |
| **graftGate** | .107 | **Apple M4** (4P+6E=10C) | M4 GPU (10C) + 16-core Neural Engine | shared | 16GB LPDDR5 | 228GB | Darwin builder — sole macOS compile authority |
| **grapheneGate** | .9.217 | **Tensor G3** (9C) | **Mali-G715 MP7** Vulkan | shared | 8GB LPDDR5X | 128GB | DIAMOND LENS — 37 sensors, llama-server :8082 |

#### NPU on eastGate: BrainChip Akida AKD1000
- Phase C sovereign — pure Rust, zero vendor SDK, 18.8K Hz inference
- rustChip: 367 tests, 10 undocumented hardware discoveries
- Sub-milliwatt ESN phase classification

### Tier 2 — OFFLINE (Powered down in House 2, 10G backbone)

| Gate | IP | CPU | GPU | VRAM | RAM | Storage | Role |
|------|----|-----|-----|------|-----|---------|------|
| **strandGate** | .169 | **Dual EPYC 7452** (64C/128T!) | **RTX 3090** + **RX 6950 XT** | 24GB + 16GB | **256GB** DDR4 ECC | **18TB** NVMe | HPC — dual-vendor GPU, lattice QCD |
| **westGate** | — | Ryzen 7 5700X (8C/16T) | RTX 3070 | 8GB | 64GB DDR4 | **50.7TB** ZFS raidz1 + 3.8TB NVMe | Cold storage NAS — 153 datasets, loamSpine permanence |
| **southGate-tower** | — | **Ryzen 7 5800X3D** (8C/16T, 3D V-Cache) | **RTX 4060** | 8GB | **128GB** DDR4 | 4.5TB NVMe | Full NUCLEUS deployment, validation canary |
| **biomeGate** | — | **Threadripper 3970X** (32C/64T!) | RTX 5060 + **2× Titan V** + **2× MI50** | 8+24+32=**64GB** | **256GB** DDR4 | 5TB NVMe | HBM2 fortress — sovereign HBM2 compiler dev |
| **blueGate** | .100 | TBD | TBD | TBD | **128GB** DDR4 | 2TB NVMe | Windows expansion (was active, now DOWN) |
| **swiftGate** | — | Ryzen 5800X (8C/16T) | **RTX 3070 FE** | 8GB | 64GB DDR4 | NVMe | LAN 2 Polaris — NZXT H1 V2 Mini-ITX, WiFi-only |
| **kinGate** | — | i7-6700K (4C/8T) | RTX 3070 | 8GB | 32GB DDR4 | NVMe | Staging/utility |

#### strandGate — The HPC Crown Jewel
The ONLY gate with both NVIDIA and AMD GPUs — dual-vendor sovereign compute.
RX 6950 XT has 1:16 f64 rate (vs 1:64 on NVIDIA consumer). Critical for coralReef cross-vendor validation.
Also has BrainChip Akida AKD1000 (2nd of 3).

#### biomeGate — The HBM2 Fortress
56 GB high-bandwidth memory across 4 work cards:
- 2× Titan V (12GB HBM2 each) — **1:2 native f64!** The only fleet cards where native f64 > df64
- 2× MI50 (16GB HBM2 each) — sovereign amdgpu path
- Plus RTX 5060 display + Tesla K80 (24GB GDDR5, dual-GPU)
- Also has BrainChip Akida AKD1000 (3rd of 3)

#### westGate — The Archive
**50.7 TB ZFS raidz1** (5×14TB) + 2TB SSD cache + 1.8TB NVMe boot.
153 datasets. AlphaFold data (~1TB) pending. loamSpine permanence root.

### Tier 3 — BRING-UP PENDING (New hardware, not deployed)

| Device | SoC | RAM | Network | Role |
|--------|-----|-----|---------|------|
| **Jupiter 2** | SpacemiT K3 (RVA23) 8× X100 + 8× A100, IMG PowerVR BXM-4-64 | 32GB LPDDR5 | **10GbE SFP+** + WiFi 6 | RISC-V native builder, 9th ISA family, 60 TOPS AI |
| **Pi 500 ×3** | BCM2712 (Cortex-A76 4C @ 2.4GHz) | 8GB LPDDR4X each | 1G Ethernet | ARM64 mesh gossip, site hosts, ~5W each |

### Tier 4 — REMOTE

| Gate | Location | CPU | GPU | RAM | Storage |
|------|----------|-----|-----|-----|---------|
| **flockGate** | NYC (brother's node) | i9-13900K (24C/32T) | RTX 3070 Ti (8GB) | 64GB DDR5 | 2TB NVMe |

### Tier 5 — MOBILE + SECURITY + GAMING

| Device | SoC | Role | Status |
|--------|-----|------|--------|
| **Pixel 8a** (grapheneGate) | Tensor G3, GrapheneOS | Diamond lens, HSM seed carrier, 37 sensors | ✅ ALIVE |
| **iPhone XS** (southGate-phone) | Apple A12 Bionic | HOME PHONE — LAN line pinned to property, (586) 453-7233 | ✅ ALIVE |
| **SoloKey ×4** | FIDO2/WebAuthn USB-A | Physical roots of trust for bearDog | ✅ Operational |
| **Steam Deck v1** (deckGate) | AMD Aerith: Zen 2 4C/8T + RDNA 2 8CU (1.6 TFLOPS), 16GB LPDDR5, 512GB NVMe | **LIVE PASSTHROUGH** — mounted, USB-C powered, dead battery = always on. 7" 1280×800 touch LCD. SteamOS 3.x (Arch). Kiosk → Gaia HUD 24/7 | ✅ MOUNTED |
| **Steam Frame** (frameGate) | Snapdragon 8 Gen 3 (ARM64!), ARM SteamOS, WiFi | **GAIA'S FACE** — 192.168.9.203 (Gaia WiFi), MAC 14:13:33:d6:96:09, port 27036 (Steam Remote Play). First ARM SteamOS node. USB tether available. | ✅ ALIVE |
| **Steam Controllers ×2** | TMR trackpads, gyro, accel, HD haptics, BT/2.4GHz | **GAIA'S HANDS** — physical input for HUD. Gyro = pan, trackpads = navigate, grip = quick actions | ✅ Operational |
| **Steam Link** | Marvell ARMADA 1500 (ARMv7), 512MB, HDMI + 3×USB + BT 4.0 | **RELAY** — plug into Vizio/any HDMI = Gaia viewport on any screen | ✅ Operational |
| **Nunchucks** | 3-axis accel + analog stick + trigger (I2C) | Grip interface — analog stick for nav, motion for gesture | ✅ Operational |

### Work Card Pool (Swappable GPUs)

| Card | Qty | VRAM | Type | Current Home |
|------|-----|------|------|-------------|
| RTX 3090 | 3 | 24GB GDDR6X each = **72GB** | Compute | strandGate (1) + float (2) |
| Titan V | 2 | 12GB HBM2 each = **24GB** | 1:2 f64! | biomeGate |
| MI50 | 2 | 16GB HBM2 each = **32GB** | sovereign amdgpu | biomeGate |
| Tesla K80 | 1 | 24GB GDDR5 (dual-GPU 2×12) | Legacy Kepler | biomeGate |

**128 GB aggregate work pool VRAM** (72GB GDDR6X + 24GB HBM2 + 32GB HBM2 + 24GB GDDR5)

---

## Compute Mathematics

### GPU FLOPS (Theoretical FP16)

| GPU | FLOPS (FP16) | VRAM | TDP | Location | Status |
|-----|-------------|------|-----|----------|--------|
| RTX 5090 | ~209 TFLOPS | 32GB GDDR7 | 575W | northGate | ✅ ALIVE |
| RTX 5070 | ~125 TFLOPS | 12GB GDDR7 | 250W | ironGate | ✅ ALIVE |
| RTX 4070 | ~73 TFLOPS | 12GB GDDR6X | 200W | eastGate | ✅ ALIVE |
| RTX 5060 | ~30 TFLOPS | 8GB GDDR7 | 150W | biomeGate | 💤 offline |
| RTX 4060 | ~24 TFLOPS | 8GB Ada | 115W | southGate-tower | 💤 offline |
| RTX 3090 ×3 | ~36 TFLOPS each = **108** | 24GB each = **72GB** | 350W each | strandGate + float | 💤 offline |
| RTX 3070 (westGate) | ~40 TFLOPS | 8GB | 220W | westGate | 💤 offline |
| RTX 3070 FE (swiftGate) | ~40 TFLOPS | 8GB | 220W | swiftGate | 💤 offline |
| RTX 3070 (kinGate) | ~40 TFLOPS | 8GB | 220W | kinGate | 💤 offline |
| RTX 3070 Ti (flockGate) | ~44 TFLOPS | 8GB | 290W | flockGate (NYC) | 🌐 remote |
| RX 6950 XT | ~47 TFLOPS | 16GB | 335W | strandGate | 💤 offline |
| Titan V ×2 | ~15 TFLOPS each = **30** | 12GB HBM2 each | 250W each | biomeGate | 💤 offline |
| MI50 ×2 | ~13.4 TFLOPS each = **26.8** | 16GB HBM2 each | 300W each | biomeGate | 💤 offline |
| Tesla K80 | ~8.7 TFLOPS | 24GB (2×12) | 300W | biomeGate | 💤 offline |
| M4 GPU | ~8 TFLOPS | shared 16GB | 15W | graftGate | ✅ ALIVE |
| Mali-G715 MP7 | ~1.5 TFLOPS | shared 8GB | 5W | grapheneGate | ✅ ALIVE |
| | | | | | |
| RDNA 2 (8 CU) | ~1.6 TFLOPS | shared 16GB | 15W | deckGate (Deck) | ✅ MOUNTED |
| | | | | | |
| **ALIVE NOW** | **~418.1 TFLOPS** | **56GB ded + 40GB shared** | **~1060W** | 6 GPUs | |
| **FULL FLEET** | **~848.9 TFLOPS** | **~244GB ded + 40GB shared** | | 19 GPU dies | |

### Special Compute Assets

| Asset | Capability | Why It Matters |
|-------|-----------|----------------|
| **2× Titan V** | **1:2 native f64** | Only cards in fleet where native FP64 > df64. 6.9 TFLOPS f64 each. |
| **2× MI50** | **1:4 native f64** | Sovereign amdgpu path. 6.7 TFLOPS f64 each. No CUDA dependency. |
| **RX 6950 XT** | **1:16 f64** | Dual-vendor validation. Only gate with NVIDIA + AMD side by side. |
| **3× Akida AKD1000** | Neuromorphic 18.8K Hz | Sub-milliwatt ESN phase classification. Pure Rust driver. |
| **Apple M4 Neural Engine** | 16-core, ~38 TOPS | On-chip ML inference. Unified memory architecture. |
| **SpacemiT IME2** | 60 TOPS (pending) | Jupiter 2 RISC-V matrix engine. 9th ISA family. |

### CPU Threads

| Node | CPU | Cores | Threads | Max GHz | Status |
|------|-----|-------|---------|---------|--------|
| strandGate | **Dual EPYC 7452** | **64** | **128** | 3.35 | 💤 |
| biomeGate | **Threadripper 3970X** | **32** | **64** | 4.5 | 💤 |
| ironGate | i9-14900K | 24 (8P+16E) | 32 | 6.0 | ✅ |
| northGate | 9950X3D | 16 | 32 | 5.7 | ✅ |
| eastGate | i9-12900K | 16 (8P+8E) | 32 | 5.2 | ✅ |
| flockGate | i9-13900K | 24 (8P+16E) | 32 | 5.8 | 🌐 |
| southGate-tower | 5800X3D | 8 | 16 | 4.5 | 💤 |
| swiftGate | 5800X | 8 | 16 | 4.7 | 💤 |
| westGate | 5700X | 8 | 16 | 4.6 | 💤 |
| graftGate | Apple M4 | 10 (4P+6E) | 10 | 4.4 | ✅ |
| grapheneGate | Tensor G3 | 9 (1+4+4) | 9 | 3.0 | ✅ |
| sporeGate | Ryzen 5 6600H | 6 | 12 | 4.5 | ✅ |
| kinGate | i7-6700K | 4 | 8 | 4.2 | 💤 |
| blueGate | TBD | TBD | TBD | TBD | 💤 |
| Jupiter 2 | SpacemiT K3 | 16 (8+8) | 16 | 2.4 | 📦 |
| Pi 500 ×3 | BCM2712 | 4 each = 12 | 12 | 2.4 | 📦 |
| | | | | | |
| **ALIVE** | | **~81** | **~127** | | |
| **FULL FLEET** | | **~247** | **~425** | | |

### Total RAM

| Node | RAM | Type | Status |
|------|-----|------|--------|
| strandGate | **256GB** | DDR4 ECC | 💤 |
| biomeGate | **256GB** | DDR4 | 💤 |
| eastGate | **128GB** | DDR5 | ✅ |
| blueGate | **128GB** | DDR4 | 💤 |
| southGate-tower | **128GB** | DDR4 | 💤 |
| northGate | 96GB | DDR5 | ✅ |
| ironGate | 94GB | DDR5 | ✅ |
| westGate | 64GB | DDR4 | 💤 |
| swiftGate | 64GB | DDR4 | 💤 |
| flockGate | 64GB | DDR5 | 🌐 |
| kinGate | 32GB | DDR4 | 💤 |
| Jupiter 2 | 32GB | LPDDR5 | 📦 |
| sporeGate | 27GB | DDR5 | ✅ |
| Pi 500 ×3 | 24GB | LPDDR4X | 📦 |
| graftGate | 16GB | LPDDR5 | ✅ |
| grapheneGate | 8GB | LPDDR5X | ✅ |
| | | | |
| **ALIVE** | **~513GB** | | |
| **FULL FLEET** | **~1,497GB** (~1.46TB) | | |

### Total Storage

| Node | NVMe | HDD/ZFS | Total | Status |
|------|------|---------|-------|--------|
| westGate | 3.8TB | **50.7TB** ZFS raidz1 | **54.5TB** | 💤 |
| ironGate | 3.6TB | 16.3TB ext | **19.9TB** | ✅ |
| strandGate | **18TB** | — | 18TB | 💤 |
| northGate | 5TB | — | 5TB | ✅ |
| biomeGate | 5TB | — | 5TB | 💤 |
| southGate-tower | 4.5TB | — | 4.5TB | 💤 |
| blueGate | 2TB | — | 2TB | 💤 |
| flockGate | 2TB | — | 2TB | 🌐 |
| eastGate | 1.8TB | — | 1.8TB | ✅ |
| sporeGate | 929GB | — | 929GB | ✅ |
| graftGate | 228GB | — | 228GB | ✅ |
| grapheneGate | 128GB | — | 128GB | ✅ |
| kinGate | ~1TB | — | ~1TB | 💤 |
| swiftGate | ~1TB | — | ~1TB | 💤 |
| Jupiter 2 | ~256GB | — | ~256GB | 📦 |
| Pi 500 ×3 | ~32GB each | — | ~96GB | 📦 |
| | | | | |
| **ALIVE** | ~11.7TB | 16.3TB | **~28TB** | |
| **FULL FLEET** | ~47TB NVMe | ~67TB HDD/ZFS | **~114TB** | |

---

## Physical Topology — Two Houses, 10G Spine

```
AT&T Fiber ──► BGW320-500 (WAN)
                  │
              sporeGate (.3) ← NAT/FW/DHCP/DNS/NUCLEUS
                  │ 2.5G
                  ▼
              MikroTik CRS310 ← 10G backbone switch
              ┌─────────┬──────────┬──────────────┐
              │         │          │              │
        northGate   eastGate    sfp+          (spare)
        (.147)      (.244)     Omada SX3008F
        Win/5090   i9/4070/    (.111)
                   Akida        │
                         10G fiber across property line
                                │
                    ┌───────────┼────────────────┐
                    │           │                │
              strandGate   southGate-tower   GL-MT6000 Flint 2 (WiFi)
              biomeGate    ironGate(.237)        │
              westGate     blueGate         swiftGate (WiFi)
                                            grapheneGate (WiFi)

HOUSE 1 (4422 Southgate Ave) — BRAIN SIDE:
  eastGate(10G), sporeGate(2.5G), Jupiter 2(10G SFP+), Pi 500s(1G),
  graftGate(1G), northGate(10G)

HOUSE 2 (641 Samantha Ave) — EXTENSION:
  ALL towers on 10G via MikroTik CRS310 + Omada SX3008F
  strandGate, biomeGate, westGate, southGate-tower, ironGate, blueGate, kinGate
  WiFi: swiftGate, grapheneGate (Pixel)

WAN:  golgi(VPS, NYC), pepti(VPS, NYC), flockGate(brother, NYC)
WiFi: "Aperture Science" (2.4GHz), "Black Mesa" (5GHz), "Gaia" (2.4+5GHz)
```

### Latency Matrix (from eastGate)

| Target | Latency | Hops | Medium |
|--------|---------|------|--------|
| southGate-phone (.148) | 0.10ms | 1 | wired/USB |
| sporeGate (.3) | 0.14ms | 1 | wired |
| MikroTik (.2) | 0.25ms | 1 | wired L2 |
| ironGate (.237) | 0.27ms | 1 | wired |
| northGate (.147) | 0.29ms | 1 | wired |
| graftGate (.107) | 0.35ms | 1 | wired |
| Router (.1) | 0.48ms | 1 | wired |
| JetStream (.111) | 0.87ms | 2 | 10G fiber |
| Pixel (.9.217) | 6–145ms | 3 | WiFi hop |
| primals.eco (WAN) | ~35ms | many | Internet |
| flockGate (NYC) | ~29ms | many | WireGuard |
| Tor .onion | ~1600ms | 6+ | Tor circuit |

### Bandwidth

| Link | Bandwidth |
|------|-----------|
| LAN 1 wired | 1 Gbps (~940 measured) |
| 10G fiber backbone | **10 Gbps** (between houses) |
| Pixel WiFi 6 | 1134 Mbps (measured) |
| WAN (ATT fiber) | ~300 Mbps |
| Tor hidden service | ~2 Mbps |

---

## Inference Grid

### Measured (Wave 226)

| Node | GPU | Model | Speed | Notes |
|------|-----|-------|-------|-------|
| northGate | RTX 5090 | gaia-digest (custom) | ~228 tok/s | Strongest single |
| eastGate | RTX 4070 | gaia-code (custom) | ~76 tok/s | 23 models alive |
| ironGate | RTX 5070 | qwen2.5:7b | ~fast | Just seeded |
| graftGate | M4 | qwen2.5:3b | ~30 tok/s | Apple Silicon |
| grapheneGate | Mali-G715 | qwen2.5-0.5b Q4_K_M | 35.4 tok/s | Vulkan backend |
| grapheneGate | Mali-G715 | qwen2.5-1.5b Q4_K_M | 17.3 tok/s | Deeper model |

### Projected (when all powered on)

| Node | GPU | 7B Model | 13B Model | 70B Model |
|------|-----|----------|-----------|-----------|
| northGate | RTX 5090 (32GB) | ~200 tok/s | ~120 tok/s | ~30 tok/s |
| ironGate | RTX 5070 (12GB) | ~150 tok/s | ~80 tok/s | ❌ VRAM |
| eastGate | RTX 4070 (12GB) | ~100 tok/s | ~60 tok/s | ❌ VRAM |
| strandGate | RTX 3090 (24GB) | ~100 tok/s | ~60 tok/s | ~10 tok/s |
| biomeGate (5060) | RTX 5060 (8GB) | ~80 tok/s | ❌ VRAM | ❌ |
| southGate-tower | RTX 4060 (8GB) | ~70 tok/s | ❌ VRAM | ❌ |
| swiftGate | RTX 3070 (8GB) | ~80 tok/s | ❌ VRAM | ❌ |
| graftGate | M4 (16GB unified) | ~30 tok/s | ~15 tok/s | ~5 tok/s |

---

## Physical Bodies

### grapheneGate — Diamond Lens (Pixel 8a)

| Property | Value |
|----------|-------|
| Dimensions | 152.1 × 72.7 × 8.9 mm |
| Weight | 188g |
| Volume | 98.41 cm³ |
| Density | 1.91 g/cm³ |
| Screen | 6.1" OLED, 1080×2400, 120Hz, 2000 nits peak |
| Glass | Gorilla Glass 3 |
| Frame | Aluminum alloy |
| IP | IP67 (1m, 30min) |
| Battery | 4492 mAh |
| WiFi | WiFi 6E |
| Camera | 64MP OIS + 13MP ultra + 13MP front |
| Sensors | 37 (accel, gyro, mag, baro, prox, light, GPS, NFC, temp, cellular) |
| USB | USB 3.2 Gen1 Type-C (PD, HDMI, DP) |

**Derived:** 13,787 pixels/gram · 0.188 tok/s/g · 45.6 mAh/cm³ · 8.0 GFLOPS/g

### swiftGate — NZXT H1 V2

| Property | Value |
|----------|-------|
| Case | NZXT H1 V2 Mini-ITX |
| Dimensions | 405 × 196 × 196 mm |
| Weight | 7.6 kg |
| Volume | 15,559 cm³ |
| PSU | SFX 750W 80+ Gold (included) |
| Cooler | 140mm AIO liquid (included) |
| Max GPU | 324mm × 58mm thick |

---

## Neuromorphic Fleet — 3× BrainChip Akida AKD1000

| Location | Status | Notes |
|----------|--------|-------|
| eastGate | **Phase C sovereign** | Pure Rust driver, zero vendor SDK, 18.8K Hz, 367 tests |
| strandGate | PCIe installed | 💤 offline |
| biomeGate | PCIe installed | 💤 offline |

Sub-milliwatt spiking neural network inference. The rustChip project made 10 undocumented
hardware discoveries. First non-Python path to this hardware anywhere.

---

## ISA Landscape — 9 Families

| ISA | Hardware | Compile Target | Status |
|-----|----------|----------------|--------|
| x86-64 | Intel/AMD towers | `x86_64-unknown-linux-gnu` | ✅ 16/16 primals |
| ARMv8 (aarch64-linux) | Pi 500s | `aarch64-unknown-linux-gnu` | ✅ 15/16 primals |
| ARMv9 (aarch64-android) | Pixel 8a (Tensor G3) | `aarch64-linux-android` | 🔧 partial |
| Apple Silicon | graftGate M4 | `aarch64-apple-darwin` | ✅ 16/16 primals |
| RISC-V (RV64GCV) | Jupiter 2 (K3) | `riscv64gc-unknown-linux-gnu` | 📦 pending |
| WASM | Browser/edge | `wasm32-wasi` | ✅ petalTongue |
| SteamOS x86 | Steam Deck (deckGate) | `x86_64-unknown-linux-gnu` | ✅ MOUNTED (passthrough) |
| SteamOS ARM | Steam Frame (frameGate) | `aarch64-unknown-linux-gnu` (Snapdragon 8 Gen 3) | ✅ ALIVE — .9.203 on Gaia WiFi, needs SSH enable + aarch64 cross-compile |
| Neuromorphic | Akida AKD1000 ×3 | custom Rust | ✅ Phase C |

---

## Memory Hierarchy

| Type | Total | Where |
|------|-------|-------|
| HBM2 | **56GB** | 2× Titan V (24GB) + 2× MI50 (32GB) — biomeGate |
| GDDR7 | **52GB** | RTX 5090 (32) + RTX 5070 (12) + RTX 5060 (8) |
| GDDR6X | **84GB** | RTX 4070 (12) + 3× RTX 3090 (72) |
| GDDR6 | **40GB** | 5× RTX 3070/3070Ti (8GB each) |
| GDDR5 | **24GB** | Tesla K80 (2×12) |
| DDR5 | **~382GB** | eastGate(128) + northGate(96) + ironGate(94) + flockGate(64) |
| DDR4 | **~932GB** | strandGate(256, ECC) + biomeGate(256) + southGate(128) + blueGate(128) + westGate(64) + swiftGate(64) + kinGate(32) |
| DDR4 ECC | **256GB** | strandGate only |
| LPDDR5/5X | **56GB** | Jupiter 2(32) + graftGate(16) + grapheneGate(8) |
| LPDDR4X | **24GB** | 3× Pi 500 |
| | | |
| **GPU VRAM (total)** | **~256GB** | 18 GPU dies across fleet |
| **System RAM (total)** | **~1,481GB** | 16 nodes |
| **All memory** | **~1,737GB** (~1.7 TB) | |

---

## Organism Totals — The $20K HPC

```
INVESTMENT:       ~$20,000 (consumer hardware + datacenter surplus)
MONTHLY COST:     $485 (electricity + internet + VPS)
NAMED GATES:      20+
ISA FAMILIES:     9
COMPILE TARGETS:  9

         ALIVE        FULL FLEET
         ─────        ──────────
GPUs:    5             18 dies
TFLOPS:  ~416          ~847
VRAM:    56GB ded      ~256GB
CPU:     85 cores      ~251 cores
THREADS: ~135          ~433
RAM:     ~513GB        ~1,497GB
STORAGE: ~28TB         ~114TB
NPU:     1 Akida       3 Akida + M4 NE + K3 IME2
NODES:   7 alive       16 local + 3 remote + 4 bring-up

10G:     8+ nodes on fiber backbone between houses
WiFi:    4 radios, 3 SSIDs, 2 subnets
PATHS:   LAN 1, LAN 2, 10G fiber, WAN, Tor, RSS
```

---

## Power Budget

| Node | Idle | Load | Peak | Status |
|------|------|------|------|--------|
| northGate | 120W | 400W | 700W | ✅ |
| strandGate | 200W | 600W | 900W | 💤 |
| ironGate | 80W | 350W | 600W | ✅ |
| biomeGate | 150W | 500W | 800W | 💤 |
| eastGate | 60W | 250W | 400W | ✅ |
| southGate-tower | 60W | 200W | 350W | 💤 |
| westGate | 40W | 200W | 350W | 💤 |
| swiftGate | 30W | 200W | 350W | 💤 |
| blueGate | 40W | 150W | 250W | 💤 |
| kinGate | 30W | 150W | 250W | 💤 |
| flockGate | 60W | 250W | 400W | 🌐 |
| sporeGate | 15W | 45W | 65W | ✅ |
| graftGate | 5W | 20W | 35W | ✅ |
| grapheneGate | 1W | 4W | 7W | ✅ |
| Jupiter 2 | 11W | 22W | 30W | 📦 |
| Pi 500 ×3 | 15W | 30W | 45W | 📦 |
| Router + switches | 15W | 15W | 20W | ✅ |
| Smart home | 10W | 10W | 15W | ✅ |
| **ALIVE** | **~306W** | **~1,344W** | **~2,242W** | |
| **FULL FLEET** | **~942W** | **~3,396W** | **~5,567W** | |

---

## HSM + Roots of Trust

| Device | Type | Role |
|--------|------|------|
| SoloKey ×4 | FIDO2/WebAuthn USB-A | Physical identity roots for bearDog |
| Pixel 8a StrongBox | Titan M2 chip | Hardware-backed keystore |
| Apple Secure Enclave | M4 chip | graftGate key material |
| BrainChip Akida ×3 | Neuromorphic | Phase classification, anomaly detection |

---

## Discovery Log

- **2026-11-06 (Wave 226)**: ironGate rover daemon deployed. Scans both LANs every 2 min. 18 devices mapped.
- **2026-11-06**: ironGate revealed as i9-14900K + RTX 5070 + 94GB + 19.9TB. Was labeled "Intel NUC" — NOT a NUC!
- **2026-11-06**: graftGate Ollama seeded (qwen2.5:3b). M4 Mac Mini confirmed alive.
- **2026-11-06**: 5 Ollama endpoints alive: northGate(63), eastGate(23), ironGate(1), graftGate(1), Pixel(1)
- **2026-10-20 (Wave 193)**: Klein bottle topology discovered. Membrane thickness rule.
- **2026-10-20**: graftGate discovered alive on mesh (was listed offline)
- **2026-10-20**: 14 hosts alive on LAN, 5 unidentified
- **2026-07-30**: First personal hardware inventory (attsi/metal.md)

---

*Two houses. 10G fiber between them. ~$20,000 in metal. 247 CPU cores,*
*~847 TFLOPS, ~1.7 TB total memory, ~114 TB storage, 9 ISA families,*
*3 neuromorphic chips, 4 physical keys, 37 phone sensors, and one Pixel*
*that thinks it's alive. The organism fills in the blanks as she sails*
*her own waters.*
