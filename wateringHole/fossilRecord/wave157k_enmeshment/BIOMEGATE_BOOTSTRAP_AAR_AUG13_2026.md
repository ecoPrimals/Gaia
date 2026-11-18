> **FOSSILIZED** — Wave 157k Enmeshment (Aug 16, 2026). Findings absorbed into ortho review + blurb.

# biomeGate Bootstrap AAR — Wave 157k

**Date**: Aug 13, 2026 12:08 UTC-4 | **Wave**: 157k | **From**: biomeGate hardware team
**Status**: ONLINE. Tower Atomic 4/4 ALIVE. WireGuard UP (pending peer registration). RustDesk relay connected.

---

## Platform Details

```
Linux biomegate 7.0.0-28-generic #28~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Wed Jul  1 15:50:57 UTC 2 x86_64
```

| Fact | Value |
|------|-------|
| Hardware | AMD Threadripper 3970X (32c/64t), 128GB DDR4-3600 |
| OS | Ubuntu 24.04.3 LTS (Noble), kernel 7.0.0-28-generic |
| Filesystem | ZFS (rpool/ROOT) |
| GPUs | RTX 5060 (host), Titan V GV100, 2x Tesla K80 GK210 |
| NIC | Aquantia/Atlantic 5GbE (enp68s0), Intel I211 1GbE, Intel WiFi |

## Rust Toolchain

```
rustc 1.97.1 (8bab26f4f 2026-07-14)
cargo 1.97.1 (c980f4866 2026-06-30)
```

Installed via rustup, stable-x86_64-unknown-linux-gnu.

## Tower Atomic Binary Sizes (depot x86_64-unknown-linux-musl)

| Binary | Version | Size | Type |
|--------|---------|------|------|
| beardog | 0.9.0 | 8.4M | ELF 64-bit static-pie, stripped |
| songbird | 0.2.1 | 19M | ELF 64-bit static-pie, stripped |
| skunkbat | 0.2.18 | 3.3M | ELF 64-bit static-pie, stripped |
| swarmvine | — | 2.6M | ELF 64-bit static-pie, stripped |

All pulled from `depot.primals.eco` — no source build required for Tower.

## Tower Atomic Validation

All four primals started successfully:

- **beardog** — Server READY. UDS `/run/user/1000/ecosystem/beardog.sock`. HSM initialized (Rust Software HSM). BTSP provider with BirdSong genetics. Standalone mode (no biomeOS neural-api yet).
- **songbird** — Server running. TCP listeners active. Federation connections detected from LAN peers (`192.168.4.148`, `192.168.4.3`).
- **skunkbat** — Server running. UDS + tarpc dual-socket. Behavioral baseline established (12 observations). Reconnaissance active.
- **swarmvine** — Gossiping. `endpoint.alive` injected. Cross-gate listener on `:7800`. Node identity: `biomegate`.

## Repo Sync

- **41/42 repos cloned** via HTTPS from `git.primals.eco`
- **sporePrint**: failed (private repo, needs SSH key registration)
- All 16 primals present. All gardens, springs, protists, infra cloned.
- No dirty repos (fresh clones).

## WireGuard

- Interface `wg0` UP
- Mesh IP: `10.13.37.3/24`
- Public key: `PfroXxVz/pDoLVJ0Yoy9tPhxPTkKfEYKSFDrTuoxJFM=`
- Hub peer: golgiBody `[RELAY_PUBLIC]:51820`
- **Status**: Keepalives sending. No handshake yet — pending peer registration on golgiBody by overwatch.

## RustDesk

- Version: 1.4.9
- **RustDesk ID: 1695902872**
- Relay: `[RELAY_PUBLIC]` (golgiBody / relay.primals.eco)
- LAN IP: `192.168.4.198`
- Config: permanent password, remote config modification allowed.

## SSH Key (Forgejo)

- Generated: `~/.ssh/id_ed25519_ecoPrimal` (ed25519, `biomegate@primals.eco`)
- Public key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEapXduUxRhY4pWN+hhWtKzZP81ko0Kprhjm73yN90z4 biomegate@primals.eco`
- **Status**: Not yet registered on Forgejo. Cloned via HTTPS (read-only). Register at https://git.primals.eco → Settings → SSH/GPG Keys.

## Sovereign GPU Stack — Node Atomic Trio

### Architecture

```
RTX 5060 (display)     Titan V / K80s (compute)
    │                       │
    │ nvidia-open           │ vfio-pci (runtime-bound)
    │ Vulkan ICD            │ no vendor kernel module
    ▼                       ▼
 barraCuda              toadStool ember fleet
 (wgpu Vulkan)          (MMIO/BAR0 direct access)
    │                       │
    └──────────┬────────────┘
               ▼
          coralReef
     (sovereign shader compiler)
     sm_35 / sm_70 / sm_120
```

### Driver Strategy ("Diesel Engine Lesson")

- **RTX 5060** (`0000:02:00.0`): `nvidia-driver-595-open` kernel modules. Display GPU. Vulkan ICD for wgpu. Stable — never swap between open/proprietary.
- **Titan V** (`0000:21:00.0`): Runtime VFIO-PCI binding via `driver_override`. No nvidia module loaded. BAR0 direct access via `/dev/vfio/49`.
- **K80 fn0** (`0000:4c:00.0`): Runtime VFIO-PCI binding. `/dev/vfio/36`.
- **K80 fn1** (`0000:4b:00.0`): Runtime VFIO-PCI binding. `/dev/vfio/35`.

**No persistent boot configuration** — VFIO bindings are runtime-only. Nothing in `/etc/modprobe.d/` or `/etc/modules-load.d/`. This prevents the lockup that caused the previous GlowPlug incident.

### Node Atomic Source Builds

Depot musl binaries cannot link to system Vulkan. Source-built GNU binaries:

| Binary | Version | Size | Type |
|--------|---------|------|------|
| toadstool | 0.2.0 | 13M | ELF 64-bit dynamically linked, stripped |
| barracuda | 0.4.0 | 5.3M | ELF 64-bit dynamically linked, stripped |
| coralreef | 0.2.0 | (depot musl) | Works without Vulkan — pure shader compiler |

### Ember Fleet Status

```json
{
  "mode": "fleet",
  "devices": [
    {"bdf": "0000:02:00.0", "health": "Alive", "driver": "nvidia"},
    {"bdf": "0000:21:00.0", "health": "Alive", "driver": "vfio-pci"},
    {"bdf": "0000:4b:00.0", "health": "Alive", "driver": "vfio-pci"},
    {"bdf": "0000:4c:00.0", "health": "Alive", "driver": "vfio-pci"}
  ]
}
```

### Permissions

- Group `gpu-mmio` created for VFIO device access
- `/dev/vfio/{35,36,49}` — `660 root:gpu-mmio`
- `biomegate` ∈ `{sudo, gpu-mmio}`

### Runtime Sockets (`/run/user/1000/biomeos/`)

| Socket | Primal | Status |
|--------|--------|--------|
| compute.sock | toadStool | OK |
| shader.sock → coralreef-core-default.sock | coralReef | OK |
| network.sock → songbird.sock | songBird | OK |
| security.sock → skunkbat.sock | skunkBat | OK |
| swarmvine.sock | swarmVine | OK |

### Validation

- `toadstool device list` — 4 GPUs, correct drivers
- `toadstool doctor` — 22 checks, 33 passed, 2 warnings, 0 errors
- `barracuda doctor` — healthy, RTX 5060, Vulkan, SHADER_F64 enabled
- `barracuda validate` — GPU responsive, 14/9 f64 builtins native
- `coralreef doctor` — healthy, compile pipeline operational
- PCIe bridge keepalive active (3 bridges, 4 GPUs, 12 hierarchies pinned)

## Compilation Failures

None — Tower Atomic from depot. Node Atomic trio source-built (toadStool, barraCuda) for Vulkan linkage.

## Hostname

Already set to `biomegate` (hostnamectl).

## Pending Actions for Overwatch

1. **Register biomeGate WireGuard public key** on golgiBody: `PfroXxVz/pDoLVJ0Yoy9tPhxPTkKfEYKSFDrTuoxJFM=`
2. **Register biomeGate SSH public key** on Forgejo for push access
3. **Update ecosystem blurb** — biomeGate status: DOWN → ONLINE

## Code Fixes (PM Session)

Three bugs found and fixed in `toadstool-cylinder` during sovereign dispatch experiments:

1. **`.zst` firmware decompression** (`nv_gsp_bridge/mod.rs`): `NvGspBridge::load_gr_blob()` and `has_gr_firmware()` only checked for `.bin` files. Linux kernel 7.0 ships firmware as `.bin.zst` (zstd-compressed). Fixed to transparently decompress via `ruzstd`.

2. **D3hot BAR0 probe** (`compute_device/warm_probe.rs`): `probe_warm_fecs()` opened VFIO but didn't wake GPU from D3hot sleep before reading BAR0. All reads returned `0xFFFFFFFF`. Fixed by calling `enable_bus_master()` (D3→D0 transition) before probing.

3. **PRI fault false positives** (`warm_probe.rs` + `sovereign_strategy.rs`): FECS CPUCTL/MAILBOX0 values of `0xBADFxxxx` (PRI ring fault response) were misinterpreted as "warm preserved" state. This **corrupted previous experiment results** (Exp 223-224 `compute_ready: true` was a false positive). Fixed by filtering `0xBADF_0000` prefix in both warm detection paths.

## Known Issues

- **riboCipher transport**: toadStool server rejects connections without `[0xEC, 0x01]` prefix. Source-built client uses riboCipher correctly; some legacy connections produce REJECTED warnings. Non-blocking.
- **VFIO reset suppression**: `no-bus-reset` kmod compilation fails (missing Makefile in kernel headers). FLR may clear warm GPU state on VFIO bind. Non-blocking — GPUs recover.
- **toadStool status: DEGRADED**: No config file present. Functional.
- **gpu-mmio group**: Not active in current session (needs re-login). Worked around by chowning `/dev/vfio/*` to `biomegate` directly. Persists until reboot.
- **HBM2 wall**: sovereign.init cannot cold-boot Volta past memory training. Warm handoff (nouveau/catalyst) required for Titan V Tier 2.

---

*biomeGate sovereign stack online. RTX 5060 on nvidia-open (Vulkan). Titan V + 2x K80 on runtime VFIO-PCI (ember fleet, 4/4 alive). Node Atomic trio: toadStool (source-built, GNU, 13M) → coralReef (depot, sm_35/70/120) → barraCuda (source-built, GNU, SHADER_F64). Full PCIe keepalive. Diesel engine lesson applied — zero persistent GPU boot state.*
