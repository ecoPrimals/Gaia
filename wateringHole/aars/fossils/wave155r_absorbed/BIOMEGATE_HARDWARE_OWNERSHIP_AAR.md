# biomeGate Hardware Ownership AAR — Aug 2, 2026

**Date**: Aug 2, 2026 AM
**Gate**: biomeGate (GPU crankshaft)
**Role**: Hardware team — localized overwatch for G32 silicon deism
**Status**: HARDWARE STABLE — platform ready for hotSpring team

---

## Context

biomeGate recovered from kernel failure and deployed 3 VFIO GPUs (Titan V + K80×2).
The hotSpring team is now active in parallel, working with the GPU compute pipeline.
This AAR covers hardware ownership: the physical infrastructure that keeps the silicon
alive and accessible for the compute teams.

## Hardware Fleet — Verified Aug 2

| GPU | BDF | Driver | Config Space | Link Speed | VFIO | IOMMU |
|-----|-----|--------|-------------|------------|------|-------|
| RTX 5060 | `02:00.0` | nvidia (host) | `10de:2d05` cmd=OK | Gen4 x16 | — | 69 |
| Titan V (GV100) | `21:00.0` | vfio-pci | `10de:1d81` cmd=0003 | Gen3 x16 | Sovereign | 49 |
| K80 die 0 (GK210) | `4b:00.0` | vfio-pci | `10de:102d` cmd=0002 | Gen3 x1* | Sovereign | 35 |
| K80 die 1 (GK210) | `4c:00.0` | vfio-pci | `10de:102d` cmd=0002 | Gen3 x4* | Sovereign | 36 |

*K80 link widths are narrow (x1/x4 vs x8 capability). Expected on VFIO — no host
driver to negotiate full width. Not a blocker for sovereign compute (BAR0 MMIO access).

## PCIe Topology

```
AMD Threadripper 3970X
├── NUMA 0 Root Complex
│   ├── 00:01.1 → 01:00.0 NVMe (Micron)
│   ├── 00:01.3 → 02:00.0 RTX 5060 [nvidia] (host GPU)
│   └── 00:07.1 → internal bridges
├── NUMA 1 Root Complex  
│   ├── 20:03.1 → 21:00.0 Titan V [vfio-pci] ← DIRECT ATTACH, Gen3 x16
│   └── 20:07.1 → internal bridges
├── NUMA 2 Root Complex
│   ├── 40:01.1 → 41:00.0 AMD Matisse switch → NICs
│   └── 40:01.3 → 49:00.0 PLX PEX 8747 switch
│       ├── 4a:08.0 → 4b:00.0 K80 die 0 [vfio-pci]
│       └── 4a:10.0 → 4c:00.0 K80 die 1 [vfio-pci]
└── NUMA 3 Root Complex
    └── 60:07.1 → internal bridges
```

## Critical Safety — PLX D3cold Keepalive (Exp 193)

**Problem**: When all VFIO endpoints behind the PLX PEX 8747 are unbound, ACPI
transitions the switch to D3cold, destroying its EEPROM configuration. Recovery
requires full chassis power-on reset. No software reset works.

**Actions taken**:

1. **Immediate pin**: Set `d3cold_allowed=0` and `power/control=on` on all 6
   devices in the PLX hierarchy (AMD root port → PLX upstream → 2 downstream
   ports → 2 K80 dies) plus the Titan V hierarchy.

2. **Persistent udev rule**: `/etc/udev/rules.d/99-biomegate-gpu-keepalive.rules`
   pins power on all PLX bridges (vendor `0x10b5`), K80 devices (`10de:102d`),
   and Titan V (`10de:1d81`) at device add time.

3. **VFIO module load**: `/etc/modules-load.d/vfio.conf` ensures `vfio-pci`
   loads before any GPU driver can claim the devices.

4. **VFIO PCI IDs**: `/etc/modprobe.d/vfio-gpu.conf` binds Titan V + K80 to
   vfio-pci by device ID at module load time.

All 4 layers survive reboot. The toadStool `pcie_keepalive` service provides
runtime protection with activity-aware heartbeat + burst mode during swaps.

## Infrastructure Services

| Service | Status | Notes |
|---------|--------|-------|
| WireGuard wg0 | LIVE, 10.13.37.3 | Handshake confirmed, 37ms RTT to golgiBody |
| SSH server | LIVE, port 22 | Listening on all interfaces |
| bearDog | systemd registered | Block store, auto-restart |
| songBird | systemd registered | Mesh transport, auto-restart |
| skunkBat | systemd registered | IPC server, auto-restart |
| nvidia-smi | Working | RTX 5060: 60°C idle, 32W, 520/8151 MiB |
| lm-sensors | Installed | CPU Tctl: 47°C |

## Monitoring

Hardware health check script at `infra/local/biomeGate/hw_health.sh`:
- Config space readability on all VFIO GPUs
- PLX bridge power pin verification
- Link speed/width tracking
- Host GPU thermals and power
- CPU thermals
- WG mesh handshake freshness
- Memory utilization

Run `./hw_health.sh --loop 30` for continuous monitoring.

## IOMMU Isolation

Clean isolation — each GPU in its own IOMMU group:
- Group 49: Titan V + HD Audio (expected co-group)
- Group 35: K80 die 0 (isolated)
- Group 36: K80 die 1 (isolated)
- Group 69: RTX 5060 + HD Audio (host, not VFIO)
- Groups 32-34: PLX bridges (own groups)

## Updated Upstream

- `TOPOLOGY_MAP.toml`: biomeGate → ONLINE, added to WG mesh + songbird peers
- `ecosystem_manifest.toml`: Already registered by sporeGate

## Blockers

None. Hardware platform is stable and ready for the hotSpring compute team.

## Coordination with hotSpring Team

Hardware team owns:
- PCIe health, VFIO binding, power management
- PLX keepalive (runtime + persistent)
- Thermal monitoring, link state
- Tower Atomic infrastructure (bearDog/songBird/skunkBat)
- WG mesh connectivity

hotSpring team owns:
- GPU experiment execution (Phases 1-6)
- toadStool sovereign dispatch
- coralReef WGSL compilation
- QCD science validation

---

*biomeGate hardware: 3 GPUs sovereign, PLX pinned, mesh live, monitoring active.
Platform ready for 44-experiment revalidation.*
