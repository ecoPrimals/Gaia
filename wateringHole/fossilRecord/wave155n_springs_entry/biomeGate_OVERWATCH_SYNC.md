# biomeGate Overwatch Sync Report

**Date**: Aug 1, 2026 | **Wave**: 155n | **From**: biomeGate
**Status**: RECOVERED FROM KERNEL FAILURE — fresh Ubuntu 24.04.3 LTS install

---

## Hardware

| Component | Detail |
|-----------|--------|
| CPU | AMD Ryzen Threadripper 3970X (32-core / 64-thread) |
| GPU | NVIDIA GeForce RTX 5060 (8GB VRAM) |
| RAM | 128 GB |
| Storage | ZFS rpool — 891 GB total, 886 GB free |
| NVIDIA Driver | 595.84 |
| CUDA | 13.2 |
| OS | Ubuntu 24.04.3 LTS (Noble Numbat), kernel 7.0.0-28-generic |

## Sync Summary

| Category | Expected | Cloned | Failed |
|----------|----------|--------|--------|
| Primals | 15 | 15 | 0 |
| Gardens | 9 | 9 | 0 |
| Springs | 9 | 9 | 0 |
| Infra | 7 | 6 | 1 |
| **Total** | **40** | **39** | **1** |

All repos cloned fresh from Forgejo via HTTPS. All on `main` branch. Zero dirty files.

### Failed Repos

| Repo | Org | Error | Notes |
|------|-----|-------|-------|
| `sporePrint` | ecoPrimals | `fatal: could not read Username` — requires auth | Blurb says "empty placeholder on Forgejo". May be private or nonexistent. |

### Naming / Divergences

None — fresh clone, all camelCase canonical names.

## Toolchain

| Tool | Version |
|------|---------|
| git | 2.43.0 |
| rustc | 1.97.1 (stable) |
| cargo | 1.97.1 |
| gcc | 13.3.0 |
| wireguard-tools | installed |
| nvidia-smi | 595.84 / CUDA 13.2 |

## Tower Atomic

Downloaded from `depot.primals.eco`:

| Binary | Version | Size |
|--------|---------|------|
| beardog | 0.9.0 | 8.3 MB |
| songbird | 0.2.1 | 19 MB |
| skunkbat | 0.2.18 | 3.0 MB |

Binaries in `~/.local/bin/`, all executable and responding to `--version`.

## WireGuard Enrollment

- Keys generated
- Public key: `ZRbD3VDxzxhQ3gbNzLoIIP5MYMvF7gVM7G9AmIRLEnY=`
- Config template prepared in `~/wireguard-keys/wg0.conf`
- **BLOCKED**: Needs WG IP assignment from eastGate overwatch
- **BLOCKED**: Public key must be registered on golgiBody

## SSH Key (Forgejo)

- Generated: `~/.ssh/id_ed25519_ecoPrimal`
- Public key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPnxJIzG134WkzUerZbThhIyrAIkpx8lKHEQBb4SzjxK biomegate@primals.eco`
- SSH config written for `git.primals.eco:2222`
- **BLOCKED**: Key not yet registered in Forgejo (using HTTPS read-only for now)

## Remaining Steps

1. **eastGate overwatch**: Assign WG IP for biomeGate (suggest 10.13.37.14 or next available)
2. **eastGate overwatch**: Register WG public key on golgiBody
3. **eastGate overwatch**: Register SSH public key in Forgejo (for push access to wateringHole)
4. Install WG config to `/etc/wireguard/wg0.conf` and bring up tunnel
5. Verify mesh connectivity: `ping 10.13.37.1`
6. Deploy full Tower Atomic services and validate `tower.health`
7. Decide composition target: Tower Atomic → Node Atomic → NUCLEUS

## Extra Directories

None — clean workspace, canonical layout only.

## Notes

- RustDesk is running (outer membrane access confirmed)
- This gate was previously "biomeGate OFFLINE (kernel recovery)" per ORTHOGONAL_DIMENSIONS_REVIEW.md
- GPU is RTX 5060 (8GB) — suitable for compute workloads but smaller VRAM than strandGate (RTX 3090) or northGate (RTX 5090)
- Threadripper 3970X gives 32 cores / 64 threads — strong for parallel Rust builds and multi-primal hosting

---

*biomeGate RECOVERED. 39/40 repos synced. Tower Atomic downloaded. WireGuard keys generated. Awaiting IP assignment + key registration from eastGate overwatch.*
