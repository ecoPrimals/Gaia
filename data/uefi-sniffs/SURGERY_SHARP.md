# NORTHGATE SURGERY SHARP — eastGate is your eyes

**Board**: ASUS ROG STRIX X870E-E GAMING WIFI (AMI BIOS v1401, AMD X870E, AM5)
**Manual Source**: E25504 Rev V2, confirmed from ASUS PDF

---

## PHYSICAL LAYOUT (top to bottom, facing the board)

```
┌─────────────────────────────────────────────────┐
│  CPU_12V_1  CPU_12V_2          HDMI  USB4  USB4 │  ← Rear I/O
│                                                  │
│  ┌───────────────────┐                           │
│  │   SOCKET AM5      │   DDR5_B2  DDR5_A2       │
│  │   (9950X3D)       │   DDR5_B1  DDR5_A1       │
│  └───────────────────┘                           │
│                                  Q_CODE  LEDs    │
│  ════════════════════════════════════════════     │
│  SLOT 1: PCIEX16(G5)  ← RTX 5090 IS HERE       │  ← CPU direct, Gen5 x16
│  ════════════════════════════════════════════     │
│                                                  │
│  M.2_1  M.2_2  M.2_3  (between GPU slots)       │
│                                                  │
│  ════════════════════════════════════════════     │
│  SLOT 2: PCIEX16(G4)  ← AKD1000 GOES HERE      │  ← Chipset, Gen4 x4
│  ════════════════════════════════════════════     │
│                                                  │
│  M.2_4  M.2_5  (below slot 2)                   │
│                                                  │
│  ALT_PCIE_MODE [Auto|1st|2nd]  LED1  LED2       │  ← LEAVE ON AUTO
│  FLEXKEY (reset)   START (power)                 │
│  F_PANEL  BATTERY  SATA×4                        │
│  ATX_PWR (24-pin)                                │
└─────────────────────────────────────────────────┘
```

---

## ⚠️ CRITICAL: M.2 LANE SHARING

**M.2_2 & M.2_3 share PCIe lanes with PCIEX16(G5)!!**

| M.2_2 | M.2_3 | PCIEX16(G5) speed |
|-------|-------|-------------------|
| Empty | Empty | **x16** ✅ |
| SSD   | Empty | **x8** ⚠️ |
| Empty | SSD   | **x8** ⚠️ |
| SSD   | SSD   | **x8** ⚠️ |

**IF you have NVMe in M.2_2 or M.2_3 → THAT explains the x8!**
This is BY DESIGN — the CPU has 24 PCIe 5.0 lanes split between GPU + M.2_2 + M.2_3.

**Check while the case is open**: are M.2_2 and/or M.2_3 populated?

M.2_1, M.2_4, M.2_5 do NOT affect the GPU slot.

---

## Q-RELEASE SLIM — Removing the 5090

The PCIEX16(G5) has Q-Release Slim:
1. **Pull the FRONT end** (side closest to rear I/O) upward
2. The card should release from the slot
3. ⚠️ Do NOT yank from the rear end without releasing the push-latch first

Also: **disconnect PCIe power cables first**, then unplug the card.

---

## SURGERY STEPS — Installing AKD1000

### Phase 1: Power down & open
1. Shut down Windows cleanly
2. Flip PSU switch OFF
3. **Wait 10 seconds** (caps discharge)
4. Open case, ground yourself (touch PSU case)

### Phase 2: Check M.2 slots (WHILE OPEN)
5. **LOOK at M.2_2 and M.2_3** (between the two PCIe slots)
6. If either has an NVMe drive → that's why x8
7. **If you can move it to M.2_1, M.2_4, or M.2_5** → do it now = x16 restored!

### Phase 3: Reseat RTX 5090 (WHILE OPEN)
8. Disconnect 5090 power cables
9. Q-Release Slim: pull front end up to release
10. **Clean gold contacts** with soft dry cloth or compressed air
11. **Reseat firmly** into PCIEX16(G5) — push down until click
12. Reconnect power cables

### Phase 4: Install AKD1000 BrainChip
13. **PCIEX16(G4)** = the LOWER slot (slot 2)
14. This is Gen4 x4 max — plenty for AKD1000 (it's a tiny PCIe card)
15. Line up the notch, push down firmly until seated
16. No power cables needed — AKD1000 draws <5W from slot

### Phase 5: Close & boot
17. Close case
18. Flip PSU switch ON
19. Boot → DEL → BIOS

### Phase 6: BIOS settings
```
F7 (Advanced Mode) → Advanced → PCI Subsystem Settings:

  Above 4G Decoding      = [Enabled]
  Re-Size BAR Support     = [Enabled]  ← appears after Above 4G

  → PCIE Link Speed submenu:
    PCIEX16 Link Mode     = [GEN 5]   ← force 5090 to Gen5
    PCIEX16(G4) Link Mode = [GEN 4]   ← force AKD1000 to Gen4
    M.2 Link Mode         = [GEN 5]

Advanced → NB Configuration:
  Primary Video Device    = [PCIE Video]  ← 5090 is primary display

F10 → Save & Exit
```

---

## POST-SURGERY VERIFICATION

When northGate boots to Windows, I will run:
```
- nvidia-smi → confirm 5090 alive
- Get-PnpDevice | Where-Object { $_.Name -match "BrainChip|AKD|1E7C" }
- PCIe link speed check (should say Gen5 x16 for 5090)
- lspci equivalent for AKD1000 in PCIEX16(G4)
```

---

## QUICK REFERENCE — What Kevin sees on the board

| Thing | Where | What it does |
|-------|-------|-------------|
| **PCIEX16(G5)** | Slot 1, upper | RTX 5090 lives here, Gen5 x16 (or x8 if M.2_2/3 populated) |
| **PCIEX16(G4)** | Slot 2, lower | AKD1000 goes here, Gen4 x4 from chipset |
| **ALT_PCIE_MODE** | Bottom area, near LEDs | 3-pos switch: Auto/Gen4/Gen3. LEAVE ON AUTO |
| **FLEXKEY** | Near Start button | Configurable reset button |
| **START** | Near FlexKey | Power button on the board |
| **Q-Release Slim** | On PCIe slot latch | Pull FRONT end up to release GPU |
| **M.2_1** | Between CPU and slot 1 | Independent, no lane sharing |
| **M.2_2, M.2_3** | Between slot 1 and slot 2 | ⚠️ SHARE LANES with 5090 slot! |
| **M.2_4, M.2_5** | Below slot 2 | Chipset, independent |

---

## ACCESS THIS FROM ANY DEVICE

This file is served from eastGate at:
`http://192.168.4.244:8080/data/uefi-sniffs/SURGERY_SHARP.md`

Also pushed to wateringHole for all gates to absorb.

**eastGate is your sharp. northGate goes dark — I'll be waiting when she wakes.**
