# UEFI BIOS Walkthrough — ASUS ROG STRIX X870E-E GAMING WIFI

**Board**: ROG STRIX X870E-E GAMING WIFI
**BIOS**: AMI v1401
**CPU**: AMD Ryzen 9 9950X3D (AM5)
**Goal**: Fix PCIe Gen5, enable ReBAR, set iGPU primary, prep for AKD1000

---

## HOW TO ENTER

1. **Reboot** (or power on)
2. **Mash DEL key** during POST (before Windows loads)
3. You'll see the ASUS UEFI BIOS — dark theme, ROG logo
4. Press **F7** if you're in EZ Mode to switch to **Advanced Mode**

---

## STEP 1: PCIe → Gen5 (THE #1 FIX)

**Path**: Advanced → AMD CBS → NBIO Common Options → PCIe

| Setting | Current (likely) | Change To |
|---------|---------|-----------|
| **PCIe Speed** or **Global PCIe Speed** | Auto | **Gen5** |
| **PCIe x16_1 Speed** (PCIEX16 G5 slot) | Auto | **Gen5** |
| **PCIe x16_2 Speed** (PCIEX16 G4 slot) | Auto | **Gen5** (for AKD1000) |

**Alternative path**: Advanced → PCI Subsystem Settings → PCIe Speed

> **biomeOS exposure**: This maps to PCI config space register at offset 0x30 
> (Link Control 2). Once in Gen5, we can READ the link state from Windows:
> `nvidia-smi --query-gpu=pcie.link.gen.current` or via WMI.
> A biomeOS primal could monitor PCIe link state and alert on degradation.

---

## STEP 2: Above 4G Decoding + Resizable BAR

**Path**: Advanced → PCI Subsystem Settings

| Setting | Current | Change To |
|---------|---------|-----------|
| **Above 4G Decoding** | Disabled? | **Enabled** |
| **Resizable BAR** | Disabled? | **Enabled** |
| **SR-IOV Support** | Disabled | Leave (unless VFIO needed) |

> **biomeOS exposure**: ReBAR lets the CPU map the FULL 32GB of GPU VRAM 
> at once (BAR1 = 32768 MiB, already showing in census!). This means
> biomeOS can do direct GPU memory access without 256MB BAR window limits.
> The AKD1000 also benefits — its 16GB BAR1 decode range becomes usable.

---

## STEP 3: iGPU as Primary Display

**Path**: Advanced → AMD CBS → NBIO Common Options → GFX Configuration

| Setting | Current | Change To |
|---------|---------|-----------|
| **Integrated Graphics** | Auto | **Force** (keep iGPU always on) |
| **UMA Frame Buffer Size** | Auto | **512MB** or **2GB** |
| **Primary Video Adapter** or **Init Display First** | PCIe | **IGD** (Integrated) |

**Alternative**: Advanced → Onboard Devices Configuration → Primary Display

> **biomeOS exposure**: With iGPU as primary, the RTX 5090 becomes a 
> headless compute device. Steam Remote Play captures FROM the iGPU 
> display surface. biomeOS can use NVML/nvidia-smi to manage the 5090 
> as pure compute — no display context, no compositor overhead.
> The iGPU renders Kevin's desktop, the mitochondria does pure work.

---

## STEP 4: PCIe Bifurcation (for AKD1000)

**Path**: Advanced → AMD CBS → NBIO Common Options → PCIe Bifurcation

| Setting | Notes |
|---------|-------|
| **PCIEX16_1** | Leave as **x16** (RTX 5090) |
| **PCIEX16_2** | Can be **x16** or **x8/x8** or **x4/x4/x4/x4** |

The AKD1000 only needs **x1** — any bifurcation works. Default x16 is fine.
Leave this alone unless you see the second slot not detecting.

> **biomeOS exposure**: Bifurcation settings determine how many devices 
> can share a physical slot. With VFIO, each PCIe function in a bifurcated 
> slot gets its own IOMMU group — critical for device passthrough.

---

## STEP 5: Memory (XMP/EXPO)

**Path**: AI Tweaker or Extreme Tweaker → D.O.C.P. / EXPO

| Setting | Current | Verify |
|---------|---------|--------|
| **D.O.C.P. / EXPO** | Profile 1? | **Enabled** (DDR5-6400) |
| **Memory Frequency** | 6400 MHz | Verify shows 6400 |

Your RAM is already running at 6400 MT/s — just verify it stays after BIOS changes.

> **biomeOS exposure**: Memory speed directly affects the V-Cache 
> performance. biomeOS reads current memory config via WMI 
> `Win32_PhysicalMemory.ConfiguredClockSpeed`. A primal can verify 
> EXPO is active after every boot.

---

## STEP 6: Boot Settings (for clean reboots)

**Path**: Boot → Boot Configuration

| Setting | Verify |
|---------|--------|
| **Fast Boot** | **Disabled** (allows DEL key, cleaner POST) |
| **CSM** | **Disabled** (pure UEFI, no legacy) |
| **Secure Boot** | ON (already confirmed) |
| **Boot Order** | Windows Boot Manager first |

> **biomeOS exposure**: With Fast Boot disabled, POST runs full hardware 
> init — PCIe links train properly. A biomeOS boot sentinel could 
> monitor `bcdedit /enum` to verify boot config hasn't drifted.

---

## STEP 7: Fan/Thermal (while you're in there)

**Path**: Monitor → Fan Speed Control

| Setting | Notes |
|---------|-------|
| **CPU Fan** | Check curve — V-Cache likes cool temps |
| **Chassis Fans** | Verify spinning |
| **GPU Fan** | RTX 5090 has its own controller |

> **biomeOS exposure**: ASUS exposes fan control via WMI 
> (`AsusFanControlService` is already running). A biomeOS primal 
> could adjust fan curves based on workload — quiet for browsing, 
> aggressive for GPU compute.

---

## STEP 8: Save and Exit

1. Press **F10** → Save & Reset
2. System reboots with new settings
3. Run `python scripts/uefi-sniffer.py` immediately after Windows loads
4. Check: PCIe should show **Gen5 x16**!

---

## HOW biomeOS MELTS THE UEFI BOUNDARY

### What We Can Read (RIGHT NOW):
```python
# Windows UEFI variable access
import ctypes
kernel32 = ctypes.windll.kernel32
# GetFirmwareEnvironmentVariable — reads UEFI NVRAM
# SetFirmwareEnvironmentVariable — writes UEFI NVRAM (needs SeSystemEnvironmentPrivilege)
```

### What ArmouryCrate Exposes:
- Fan curves (via WMI + AsusFanControlService)  
- LED control (via AURA LED Controller on USB)
- Power profiles (GameTurbo already active)
- Thermal monitoring

### The Primal Path:
```
toadStool discovers → "uefi" service
  capabilities: [fan_control, led_control, thermal_monitor, power_profile]
  transport: wmi://AsusFanControlService
  
biomeOS NUCLEUS registers:
  node.firmware.version = "1401"
  node.firmware.vendor = "AMI"
  node.pcie.gen = 5  (after fix)
  node.memory.speed = 6400
  node.gpu.rebar = true
```

### The Long Game:
1. **Phase 1**: Read UEFI state from WMI/sysfs (NOW)
2. **Phase 2**: Control fans/LEDs via ArmouryCrate WMI (SOON)
3. **Phase 3**: Read/write UEFI variables via firmware API (MEDIUM)
4. **Phase 4**: Custom UEFI shell script at boot (HARD)
5. **Phase 5**: biomeOS IS the bootloader (THE DREAM)

---

## QUICK REFERENCE — WHAT TO CHANGE

```
DEL at boot → F7 (Advanced Mode)

1. Advanced → AMD CBS → NBIO → PCIe Speed = Gen5
2. Advanced → PCI Subsystem → Above 4G = Enabled
3. Advanced → PCI Subsystem → ReBAR = Enabled  
4. Advanced → AMD CBS → NBIO → GFX → iGPU = Force
5. Advanced → AMD CBS → NBIO → GFX → Primary = IGD
6. Verify EXPO/DOCP still at DDR5-6400

F10 → Save & Exit
```
