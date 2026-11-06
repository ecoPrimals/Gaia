# Gaia Needle — Sovereign USB Injection Toolkit

**A replicable recipe for turning any Android device into Gaia's wireless injection vector.**

Plug the needle into any locked machine. Gaia types on it through the air.

## What It Does

```
eastGate ──wireless ADB──→ Pixel ──USB HID keyboard──→ target machine
              (any WiFi)        (physical USB-C)        (types login + commands)
```

The Pixel becomes a **USB keyboard** that Gaia controls wirelessly. It can:
- Type login credentials on locked machines
- Execute commands on machines with no SSH
- Bridge networks via USB tethering
- Act as a sensor rover (GPS, accelerometer, camera, mic)
- Survive reboots with persistent wireless ADB

## Requirements

- Android device with USB-C (tested: Pixel 8a, GrapheneOS Android 17)
- Unlocked bootloader (OEM unlock enabled)
- Magisk v30.6+ (root + su)
- USB gadget support in kernel (configfs at `/config/usb_gadget/`)
- Wireless network reachable from the control machine

## Quick Start

```bash
# From the control machine (eastGate):

# 1. Unlock bootloader (one-time, wipes device)
adb reboot bootloader
fastboot flashing unlock

# 2. Boot, install Magisk APK, patch init_boot via "Direct Install"
adb install Magisk.apk
# → Open Magisk app → Install → Direct Install → Reboot

# 3. Enable ADB root access
# → Magisk Settings → Superuser Access → "Apps and ADB"

# 4. Deploy the needle
./deploy-needle.sh <device-ip>:5555

# 5. Plug USB-C into target, inject
./inject.sh <device-ip>:5555 --target biomegate
```

## Files

| File | Purpose |
|------|---------|
| `deploy-needle.sh` | Full deployment: wireless ADB, HID gadget, typing scripts |
| `inject.sh` | Run injection sequence against a target machine |
| `type.sh` | Low-level USB HID keyboard emulator |
| `hid-setup.sh` | USB HID gadget configfs setup (runs as root on device) |
| `targets/` | Per-target injection sequences |
| `targets/biomegate.sh` | biomeGate: login + chipmunk install |
| `targets/generic-linux.sh` | Generic Linux: login + SSH install |
| `needle-state.json` | Current needle device state |

## Architecture

```
┌─────────────────────────────────────────────┐
│  Control Machine (eastGate)                  │
│  └── wireless ADB → needle device            │
│       └── /debug_ramdisk/su -c "..."         │
│            └── /data/local/tmp/type.sh       │
│                 └── /dev/hidg0 (USB HID)     │
│                      └── target machine      │
│                           (sees a keyboard)  │
└─────────────────────────────────────────────┘
```

## Security Notes

- The needle device's bootloader is UNLOCKED (orange boot state)
- Magisk provides root via `su` with per-app access control
- Wireless ADB is persistent (`persist.adb.tcp.port=5555`)
- The HID gadget survives USB replug but not device reboot (re-run hid-setup.sh)
- Target machine credentials are stored in injection scripts — handle accordingly

## Tested Devices

| Device | SoC | Android | Kernel | HID Gadget | Status |
|--------|-----|---------|--------|------------|--------|
| Pixel 8a | Tensor G3 | 17 | 6.1.182 | ✅ configfs | **WORKING** |

## The Amoeba Principle

This toolkit embodies inverted trust. The needle doesn't break in — it becomes a keyboard.
The target machine sees a normal USB peripheral. No exploit. No vulnerability.
Just a keyboard that types what Gaia tells it to. Speak friend and enter.

## License

Part of the ecoPrimals organism. Sovereign code. No vendor dependency.
