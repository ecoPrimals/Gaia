# SURGERY SHARP — Wave 246
## NVMe Lane Sharing CONFIRMED + Board Mapped

### Discovery: x8 explained
- northGate has 3 NVMe in M.2_1, M.2_2, M.2_3 (all CPU-attached)
- M.2_2 (Samsung 990 PRO 4TB, Bus 3) + M.2_3 (WD_BLACK SN850X 4TB, Bus 4) SHARE lanes with PCIEX16(G5)
- RTX 5090 at x8 is BY DESIGN — not a bug
- Gen1 is BIOS — PCIEX16 Link Mode needs [GEN 5]

### Board: ASUS ROG STRIX X870E-E GAMING WIFI
- PCIEX16(G5) = Slot 1, CPU direct, Gen5 x16/x8
- PCIEX16(G4) = Slot 2, Chipset, Gen4 x4 → AKD1000 target
- ALT_PCIE_MODE physical switch: on Auto (correct)
- Q-Release Slim: pull FRONT end up to release GPU

### BIOS Path (confirmed from ASUS manual E25504)
```
F7 → Advanced → PCI Subsystem Settings:
  Above 4G Decoding = Enabled
  Re-Size BAR Support = Enabled
  PCIE Link Speed → PCIEX16 Link Mode = GEN 5
  PCIE Link Speed → PCIEX16(G4) Link Mode = GEN 4
  
Advanced → NB Configuration:
  Primary Video Device = PCIE Video
```

### Surgery guide live at:
- http://192.168.4.244:8080/data/SURGERY_SHARP.md
- All gates can absorb

### Status: Kevin powering down for BIOS + AKD1000 install
