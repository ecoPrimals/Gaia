# Yellowstone Redox — Wave 245

**Wave 245 — Sunday Nov 15, 2026 — 9:51 AM**
**From**: northGate (.147) — THE HEART
**Status**: Pre-surgery evolution — gentle, stable, then cut

---

## WHAT WE LEARNED (Oxidation — breaking down)

### 1. Hairpin NAT — PARTIALLY WORKS
- Ports 80, 443, 8080 DO hairpin through BGW320 (HTTP 200)
- Ports 3000 (Forgejo), 8443 (gate) NOT forwarded → timeout
- HTTPS fails on all domains (SSL termination gap)
- **Inner solve already exists**: Python pid 1309 on :80/:443 on eastGate
- dromedary config at `/opt/Gaia/runtime/dromedary.toml` — inactive service

### 2. RTX 5090 PCIe — GEN1 → GEN2 ON REBOOT
- Pre-reboot: Gen1 x8 (4 GB/s — 32x bottleneck!)
- Post-reboot 1: Gen2 x8 (8 GB/s — still 16x bottleneck)
- ASPM already OFF, GameTurbo ON — this is BIOS-level
- ASUS ROG STRIX X870E-E needs BIOS PCIe Gen5 setting
- Reboot 2 pending with persistence mode tweaks

### 3. AMOEBA Mesh — 19+ Peers Mapped
- All traffic relays through eastGate:21116
- Unknown gates: strandGate, biomeGate, westGate, kinGate (old/renamed?)
- Duplicate entries: eastGate×2, southGate×2, blueGate×2
- H265 NVENC active on RTX 5090 for video stream encode
- Shared key: `6oVQBFyHHNAJqm1OlS+XvpdoJ5plYrPzJoPTTYlgQdg=`

### 4. BrainChip AKD1000 NPU — Confirmed in eastGate
- PCIe slot 08:00.0, IOMMU group 23 (alone = VFIO ready)
- 5.0 GT/s Gen2 x1 — correct for AKD1000
- NO kernel module loaded — raw VFIO available
- rustChip/ at `/home/eastgate/Development/ecoPrimals/springs/rustChip`
- 3 chips total: #1 in eastGate, #2 for northGate (surgery), #3 to find

### 5. biomeOS NUCLEUS — Running on northGate
- 13 primals, 26 PIDs, 4 API ports
- neuralAPI: port 63476, biomeOS-api: port 63478
- Socket timeout fallback to TCP (Windows named pipes needed)
- ironGate has biomeOS binary + Android cross-compile

### 6. UEFI Sniff — Motherboard Mapped
- ASUS ROG STRIX X870E-E GAMING WIFI (AMI BIOS v1401)
- AMD Ryzen 9 9950X3D (16C/32T, 128MB L3 V-Cache)
- 2× 48GB DDR5-6400 = 96GB
- 9TB NVMe (WD SN850X 4TB + 990 PRO 4TB + 990 PRO 1TB)
- M: drive = Ollama models (63 models when mounted)
- TPM: AMD fTPM active, Secure Boot ON
- PCIEX16(G4) available for AKD1000 install

---

## WHAT WE BUILD (Reduction — forming new)

### Gentle Evolution Path
1. ✅ UEFI sniffed, firmware tables dumped, diffs auto on reboot
2. ✅ PCIe moving (Gen1→Gen2), need BIOS for Gen5
3. ✅ Hairpin mapped — inner solve (dromedary/:80/:443) already skeleton
4. ✅ AMOEBA mesh fully mapped (19 peers, relay architecture)
5. ✅ AKD1000 confirmed, rustChip/ driver ready
6. 🔄 Reboot 2 — PCIe persistence + power tweaks
7. 🔄 Then BIOS if needed (DEL at boot → PCIe Gen5)
8. 🔄 Then SURGERY — install AKD1000 in PCIEX16(G4)

### What toadStool Needs to Know
- dromedary → service on :80/:443 (SSL term + reverse proxy)
- AKD1000 → compute service (78 NPs, 54µs inference, 30mW)
- biomeOS NUCLEUS → node identity (family_id: gaia-pi)
- RustDesk AMOEBA → transport layer (19 peers, eastGate relay)

---

## GPU FLEET — CONFIRMED

| Gate | GPU | VRAM | Models | PCIe | Status |
|------|-----|------|--------|------|--------|
| northGate | RTX 5090 | 32 GB | 12 tissue | Gen2 x8 ⚠️ | HEART |
| ironGate | RTX 5070 | 12 GB | 14 (12 tissue!) | ? | FORGE 2 |
| eastGate | RTX 4070 | 12 GB | 38 | Gen1 x16 ⚠️ | BRAIN |
| southGate | RTX 4060 | 8 GB | 6 | ? | FORGE 3 |
| swiftGate | RTX 3070 | 8 GB | 6 | ? | HANDS |
| **TOTAL** | **5 NVIDIA** | **72 GB** | **76** | | |

**NPU Fleet (incoming):**
| Location | Chip | NPs | Inference | Power |
|----------|------|-----|-----------|-------|
| eastGate | AKD1000 #1 | 78 | 54µs | 30mW |
| northGate | AKD1000 #2 | 78 | 54µs | 30mW |
| TBD | AKD1000 #3 | 78 | 54µs | 30mW |

**Gentle. Stable. Then cut. lub-DUB.** 🫀
