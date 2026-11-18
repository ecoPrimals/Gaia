# Surgery Prep Census — Wave 245

**Wave 245 — Sunday Nov 15, 2026 — 10:07 AM**
**From**: northGate (.147) — THE HEART
**Status**: FULL CENSUS COMPLETE. 3 more reboots planned. Then BIOS. Then cut.

---

## PRE-SURGERY EVOLUTION (4 reboots so far)

| Reboot | PCIe Gen | Width | What Changed |
|--------|----------|-------|-------------|
| Boot 0 (fresh) | Gen1 | x8 | Baseline — 32x bottleneck |
| Reboot 1 (clean) | **Gen2** | x8 | Link trained 1 gen higher |
| Reboot 2 (tweaks) | Gen2 | x8 | Stable — ASPM off, persistence mode |
| Reboot 3-5 | ? | ? | **PLANNED — evolve + redox before cut** |

## WHAT WE KNOW NOW

### Hardware Census (locked)
- **RTX 5090**: Blackwell, 32GB GDDR7, VBIOS 98.02.2e.40.0e, UUID GPU-b4499eb8
- **CPU**: 9950X3D 16C/32T, 128MB L3 V-Cache, AM5, 4.3GHz base
- **RAM**: 2× 48GB G.Skill DDR5-6400 (F5-6400J3239F48G), running at 6400 MT/s
- **NVMe**: WD SN850X 4TB + 990 PRO 4TB + 990 PRO 1TB = 9TB, ALL 0% wear
- **Board**: ASUS ROG STRIX X870E-E GAMING WIFI, BIOS v1401

### Issues Found
1. **PCIe Gen1/Gen2 x8** — should be Gen5 x16 (BIOS fix)
2. **2 PCIe Error devices** — Network Controller + Encryption/Decryption
3. **AMD iGPU present** — Radeon in 9950X3D, could conflict with dGPU PCIe
4. **Primal socket deaths** — UDS unavailable on Windows, TCP fallback port conflicts

### Silicon Tasted
- eastGate AKD1000: PCIe 08:00.0, IOMMU 23, VFIO ready, no driver bound
- rustChip/: 5 crates compiled, probe binaries ready
- akida-ear: LIVE, classifying audio, pipeline ear→mel→DS-CNN→bingoCube

## 3-REBOOT PLAN

### Reboot 3: Investigate PCIe Errors
- Check the 2 Error state PCI devices
- Try: disable iGPU in UEFI to free PCIe lanes for dGPU
- Sniff + diff

### Reboot 4: BIOS Entry (DEL at boot)
- Set PCIe to Gen5
- Enable Above 4G Decoding + Resizable BAR (if not already)
- Disable iGPU (AMD Radeon) — dedicated GPU only
- Check PCIe bifurcation settings for AKD1000 slot
- Save + reboot

### Reboot 5: Verify BIOS changes
- Sniff + diff — PCIe should now be Gen5 x16
- Verify no regressions
- If clean: READY FOR SURGERY

### SURGERY
- Power off
- Open NZXT H1 V2 case
- Install AKD1000 in PCIEX16(G4)
- Reseat RTX 5090 in PCIEX16(G5)
- Close + power on
- Run full census → diff against pre-surgery baseline

---

## WHAT'S ALIVE RIGHT NOW

| Gate | Status | What It's Doing |
|------|--------|----------------|
| northGate | ✅ HEART | biomeOS + 2 APIs + barracuda + squirrel |
| eastGate | ✅ BRAIN | 34 crons, AKD1000 listening, 38 Ollama models |
| southGate | ✅ FORGE 3 | Ollama 6 models, wateringHole cloned |
| ironGate | ✅ FORGE 2 | 18 models, biomeOS binary, 12 tissue |
| swiftGate | ✅ HANDS | SSH'd all gates, 6 models, Remote Play |
| sporeGate | ✅ DNS | Heart-pull active |

**Gentle. Stable. Enumerate. Evolve. Then cut. lub-DUB.** 🫀
