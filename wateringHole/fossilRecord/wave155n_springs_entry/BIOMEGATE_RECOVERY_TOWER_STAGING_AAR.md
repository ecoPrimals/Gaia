# AAR: biomeGate Recovery — Kernel Failure to Full Sync + Tower Atomic

**Date**: Aug 1, 2026 21:00 EDT
**Gate**: biomeGate
**Wave**: 155n (springs+gardens phase)
**Author**: biomeGate overwatch (agent-assisted)
**Status**: RECOVERED → SYNCED → TOWER STAGED

---

## TL;DR

biomeGate recovered from kernel failure to full workspace sync in a single session.
Fresh Ubuntu 24.04.3 LTS install. 39/40 repos cloned from Forgejo via HTTPS. Tower
Atomic binaries (beardog 0.9.0 + songbird 0.2.1 + skunkbat 0.2.18) downloaded from
depot and verified. WireGuard keys generated. Rust 1.97.1 + NVIDIA 595.84 (CUDA 13.2)
confirmed live. Hardware: Threadripper 3970X (32c/64t), RTX 5060 (8GB), 128GB RAM,
ZFS 886GB free. Gate is ready for mesh enrollment and diesel engine work.

---

## Hardware Inventory

| Component | Detail |
|-----------|--------|
| CPU | AMD Ryzen Threadripper 3970X (32-core / 64-thread) |
| GPU | NVIDIA GeForce RTX 5060 (8GB VRAM) — CUDA 13.2, Driver 595.84 |
| RAM | 128 GB DDR4 |
| Storage | ZFS rpool — 891 GB total, 886 GB free |
| Network | Pending mesh enrollment |
| OS | Ubuntu 24.04.3 LTS (Noble Numbat), kernel 7.0.0-28-generic |

**Planned additions**: Tesla + Titan V test cards for coralReef diesel engine
multi-vendor GPU validation.

---

## What Was Done

### Phase 0: Connectivity

- Forgejo HTTPS access verified — all public repos reachable at `git.primals.eco`
- SSH host key scanned and added to `~/.ssh/known_hosts`
- SSH keypair generated: `~/.ssh/id_ed25519_ecoPrimal`
- SSH config written for `git.primals.eco:2222`
- **Pending**: SSH key registration on Forgejo for push access

### Phase 1: Sync

| Category | Expected | Cloned | Notes |
|----------|----------|--------|-------|
| Primals | 15 | 15 | All 15 including dormant (sourDough, bingoCube) |
| Gardens | 9 | 9 | cellMembrane, esotericWebb, lithoSpore, projectFOUNDATION, projectNUCLEUS, helixVision, initioChem, metalForge, blueFish |
| Springs | 9 | 9 | hotSpring (2,647 files — largest), primalSpring, wetSpring, airSpring, groundSpring, healthSpring, ludoSpring, neuralSpring, rustChip |
| Infra | 7 | 6 | sporePrint FAILED (private/empty — `could not read Username`) |
| **Total** | **40** | **39** | All on `main` branch. Zero dirty files. Zero naming divergences. |

No naming fixes needed (fresh clone = canonical camelCase from the start).
No remote repointing needed (all cloned from Forgejo, not GitHub).

### Phase 2: Enrollment (Staged)

- Hostname set to `biomeGate` via `hostnamectl`
- WireGuard keypair generated, config template installed to `/etc/wireguard/`
- WG public key: `ZRbD3VDxzxhQ3gbNzLoIIP5MYMvF7gVM7G9AmIRLEnY=`
- **Pending**: WG IP assignment from eastGate overwatch
- **Pending**: golgiBody peer registration

### Tower Atomic

| Binary | Version | Size | Status |
|--------|---------|------|--------|
| beardog | 0.9.0 | 8.3 MB | `--version` OK |
| songbird | 0.2.1 | 19 MB | `--version` OK |
| skunkbat | 0.2.18 | 3.0 MB | `--version` OK |

Downloaded from `depot.primals.eco`, installed to `~/.local/bin/`.

### Toolchain

| Tool | Version |
|------|---------|
| rustc | 1.97.1 (stable, 2026-07-14) |
| cargo | 1.97.1 |
| gcc | 13.3.0 |
| git | 2.43.0 |
| nvidia-smi | 595.84 / CUDA 13.2 |

---

## biomeGate Mission (from eastGate overwatch)

1. **coralReef diesel engine** — Vendor-agnostic GPU solve. WGSL→native compilation
   for all GPU vendors. The strandGate PRNG polyfill root-cause AAR proves this is
   critical. biomeGate has multi-vendor GPU hardware to test and validate.

2. **hotSpring GPU dispatch** — Cross-gate compute where strandGate does the science
   and biomeGate does heavy GPU solving via songBird mesh. Dual-gate assignment:
   strandGate (RTX 3090) + biomeGate (RTX 5060 + Tesla + Titan V).

3. **toadStool compute orchestration** — 128GB RAM allows full 4-layer pipeline
   (brain architecture from Exp 028-030).

---

## Blockers

| # | Blocker | Owner | Impact |
|---|---------|-------|--------|
| 1 | SSH key not registered on Forgejo | biomeGate (self-register) | Can't push handoffs. Using HTTPS read-only. |
| 2 | WG IP not assigned | eastGate overwatch | Can't join mesh. Tower services can't do primal IPC. |
| 3 | sporePrint clone failed | Low priority | Empty placeholder per blurb. |

---

## Observations

- The gate recovery from kernel failure to full sync took ~15 minutes wall time.
  The blurb bootstrap flow (Phases 0→2) works cleanly on a fresh Ubuntu install.
- NVIDIA drivers were already present from the Ubuntu install (595.84). No manual
  driver installation was needed — the Ubuntu 24.04.3 HWE kernel ships with
  functioning NVIDIA support for RTX 5060.
- ZFS rpool came through the reinstall intact (886 GB free).
- RustDesk was already running (outer membrane access confirmed).
- The `sporePrint` repo appears to require authentication even for clone, unlike
  all other ecoPrimals repos. May need a Forgejo visibility toggle.

---

*biomeGate RECOVERED. 39/40 synced. Tower Atomic staged. Diesel engine crankshaft
role assigned. Awaiting mesh enrollment to close the loop.*
