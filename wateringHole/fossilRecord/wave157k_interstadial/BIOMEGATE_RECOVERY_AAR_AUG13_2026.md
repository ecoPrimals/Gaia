# biomeGate Recovery AAR — Wave 157k

**Date**: Aug 13, 2026 | **Wave**: 157k | **From**: overwatch (eastGate)
**Gate**: biomeGate (Threadripper 3970X, 128GB DDR4, Ubuntu 24.04.3/ZFS)
**Status**: WIPE + REINSTALL IN PROGRESS. Root cause documented. Recovery deferred to next session.

---

## What Happened

biomeGate has been DOWN since mid-Wave 157k. Normal boot hangs on blank screen. Ubuntu recovery mode works. The failure was caused by ecoPrimals GlowPlug/coral-ember VFIO driver orchestration leaving persistent boot-affecting state.

### Hardware

- AMD Threadripper 3970X (32c/64t)
- 128GB DDR4-3600 (reduced from 256GB during earlier debugging, 4x32GB in A2/B2/C2/D2)
- Gigabyte TRX40 AORUS MASTER, BIOS F8h (2025-11-21), AGESA CastlePeakPI 1.0.0.F
- GPUs: RTX 5060 (host/display, `02:00.0`), Titan V GV100 (`21:00.0`), 2x Tesla K80 GK210 (`4b:00.0`, `4c:00.0`)
- ZFS root filesystem (`rpool/ROOT`)
- Kernel: `7.0.0-28-generic`

### Root Cause

GlowPlug's VFIO driver orchestration persisted boot-affecting configuration:

1. `/etc/modules-load.d/vfio.conf` — forced `vfio-pci` module load at boot
2. `/etc/modprobe.d/vfio.conf` — bound Titan V (`10de:1d81`) + K80 (`10de:102d`) to vfio-pci at boot
3. These configs were embedded into initramfs via `update-initramfs`
4. The bind/unbind/reset lifecycle left kernel driver state inconsistent
5. Display manager (GDM) attempted to initialize GPU on boot → hang

**Previous remediation attempted (by earlier agent)**:
- VFIO config files removed and backed up to `/root/glowplug-recovery/`
- `update-initramfs -u -k all` and `update-grub` run
- Normal boot still failed → damage was deeper than config files (likely driver state in initramfs or NVIDIA/VFIO module interaction)

**Observed kernel traces** (from earlier agent sessions):
- `rcu_note_context_switch`, `schedule`, `vprintk`, `do_task_dead`
- `Code: Unable to access opcode bytes`
- `coral-glowplug` tasks blocked for hundreds of seconds
- Mutex ownership involving `coral-ember`
- AMD GPU `amdgpu: trn=2 ACK should not assert!`
- VFIO device reset sequences during shutdown

### A/B Evidence

```
128 GB + clean Ubuntu → stable
128 GB + ecoPrimals GlowPlug driver experimentation → broken
```

RAM and BIOS are not suspects. The failure is persistent software/driver state.

---

## Recovery Attempt (Aug 13, 2026)

### What Worked
- Booted into Ubuntu recovery mode (root shell)
- Remounted writable (`mount -o remount,rw /`)
- Started `systemd-networkd` and `ssh`
- Brought up `enp68s0` (5GbE Atlantic NIC) with static IP `192.168.4.200/22`
- Confirmed ping to eastGate (`192.168.4.244`) — 0% loss, 0.43ms
- Established direct cable link eastGate `eno1` ↔ biomeGate `enp68s0` on `10.99.0.0/24`
- Ping over direct cable confirmed (0.7ms)
- SSH port 22 reachable via `nc` on direct cable

### What Failed
- SSH via switch (192.168.4.200:22) — "Connection refused" despite sshd listening on 0.0.0.0:22
- UFW disabled but iptables/nftables rules likely still blocking
- SSH via direct cable (10.99.0.2:22) — "Connection timed out" initially (IP dropped from eastGate eno1), then "Permission denied" (key auth not configured, root password login disabled)
- Recovery console too painful for multi-line SSH config commands

### Decision: Wipe + Reinstall

Attempting to fix the broken install via recovery console is slower than a clean reinstall because:
1. No DHCP client installed (recovery mode minimal)
2. Firewall rules persisted despite `ufw disable` (likely nftables)
3. SSH key enrollment requires too much manual typing on recovery TTY
4. Root cause is already documented — fixing forward is better than archaeology

---

## The Diesel Engine Lesson

The GlowPlug/coral-ember system is the "diesel engine" — it manages GPU lifecycle (VFIO bind/unbind/reset) for sovereign GPU compute. Like a diesel engine, it works well once running but the startup sequence is critical. If startup fails partway through, the machine is left in an unrecoverable state.

### What Must Change

1. **Never persist boot-affecting GPU state.** No `/etc/modprobe.d/` modifications, no `/etc/modules-load.d/` entries, no initramfs embedding for VFIO. All VFIO binding must be dynamic, at runtime only.

2. **Explicit state machine with rollback.** The GlowPlug lifecycle must follow:
   ```
   discover → verify ownership → quiesce userspace → detach → reset → bind → verify → rollback/fail closed
   ```
   Every transition must have a hard timeout and a defined rollback path.

3. **Device-specific reset awareness.** Not all GPU reset paths are equal. A "successful" VFIO reset doesn't mean the underlying device is healthy. GlowPlug must verify device health post-reset.

4. **Boot independence.** The machine must always boot cleanly to `multi-user.target` with SSH accessible, regardless of GPU state. GPU orchestration starts after boot, not during.

5. **Agentic recovery model.** Co-located gates can recover each other over LAN SSH. The recovery agent needs:
   - Direct cable capability (bypass switch firewall issues)
   - Pre-enrolled SSH keys (before the gate goes down)
   - Static IP fallback (no DHCP dependency)

### Prevention Checklist for Future GPU Gates

- [ ] Default boot target is `multi-user.target` (no display manager dependency)
- [ ] SSH keys pre-enrolled from overwatch gate
- [ ] LAN IP registered in `ecosystem_manifest.toml`
- [ ] No persistent VFIO config in `/etc/modprobe.d/` or `/etc/modules-load.d/`
- [ ] GlowPlug state machine has timeout-guarded rollback at every transition
- [ ] `builder.serve` deployed on `:9800` for remote management
- [ ] UFW configured to allow LAN subnet on port 22

---

## Next Steps (Post-Reinstall)

1. Fresh Ubuntu 24.04 install with SSH enabled during setup
2. Set default to `multi-user.target` (no GDM)
3. Pre-enroll eastGate SSH key
4. Register `lan_ip` in ecosystem manifest
5. Pull from depot, deploy Tower Atomic, start biomeOS
6. Redesign GlowPlug with runtime-only VFIO binding (no boot persistence)
7. Validate on single GPU (RTX 5060 only) before adding Titan V / K80 back

---

## NIC Reference

| Interface | Hardware | Speed | Cable |
|-----------|----------|-------|-------|
| `enp67s0` | Intel I211 | 1GbE | Did not link |
| `enp68s0` | Aquantia/Atlantic | 5GbE | Linked — used for recovery |
| `wlo2` | Intel WiFi | WiFi | Available as fallback |

---

*biomeGate recovery attempt documented. Wipe + reinstall is the forward path. Diesel engine lesson: never persist boot-affecting GPU state. Pre-enroll SSH keys. Boot to multi-user.target. GlowPlug must have runtime-only VFIO with rollback.*

---
*FOSSILIZED Wave 157k interstadial (Aug 14, 2026). Content absorbed into ortho/blurb or implemented in code.*
