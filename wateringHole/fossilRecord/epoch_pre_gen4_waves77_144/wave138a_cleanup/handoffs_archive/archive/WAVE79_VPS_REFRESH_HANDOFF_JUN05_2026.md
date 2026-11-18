# Wave 79 VPS Binary Refresh — Handoff to cellMembrane

**Date**: 2026-06-05  
**From**: eastGate overwatch  
**To**: cellMembrane team (ironGate)  
**Status**: 10/13 binaries refreshed, 3 need repo-level fixes  

---

## What Was Done (eastGate)

### Full Pipeline Validation
- Built all 13 primal binaries from HEAD of their repos (musl-static, x86_64)
- Harvested into `plasmidBin/primals/` with blake3 checksums updated
- Deployed `nucleus_launcher` v0.9.31 (Wave 79, UDS-first default)
- Updated all 13 systemd units on golgiBody to UDS-only / localhost-bound
- Created `membrane-socket-bridge.service` for `/run/membrane/` → `/run/biomeos/` alignment
- Created `songbird-mesh.service` for federation (was previously an unmanaged process)
- Removed legacy Nest TCP firewall rules (9500, 9601, 9700, 9850)

### Binaries Successfully Refreshed (10/13)
| Primal | Old Version | New Version | Status |
|--------|-------------|-------------|--------|
| beardog | 0.9.0 | 0.9.0 (latest HEAD) | LIVE |
| songbird | 0.2.1 | 0.2.1 (Wave 81 deep debt) | LIVE |
| skunkbat | 0.2.0-dev | 0.2.5 | LIVE |
| barracuda | 0.4.0 | 0.4.0 (latest HEAD) | LIVE |
| nestgate | 2.1.0 | 0.5.0 (latest HEAD) | LIVE |
| rhizocrypt | 0.14.0-dev | 0.14.2 | LIVE |
| loamspine | 0.9.16 | 0.9.16 (latest HEAD) | LIVE |
| sweetgrass | 0.7.34 | 0.7.50 | LIVE |
| biomeos | 0.1.0 | 0.1.0 (latest HEAD) | LIVE |
| petaltongue | 1.6.6 | 1.6.6 (latest HEAD) | LIVE |

### Binaries Rolled Back (3/13) — Need Repo Fixes
| Primal | Issue | Required Fix |
|--------|-------|--------------|
| toadstool | `Error: Setup("No Akida devices found")` — new binary requires NPU hardware to start | Add `--headless` or `--no-akida` flag for VPS deployment without GPU/NPU |
| coralreef | `Error: Cannot read ./specs/amd/amdgpu_isa_rdna2.xml` — hard dependency on GPU ISA spec file at startup | Add `--headless` flag or lazy-load GPU specs only when compilation is requested |
| squirrel | No `server` subcommand — new binary is CLI-only, no IPC server mode | Restore `server` subcommand for UDS IPC service mode |

Backups of pre-refresh binaries are at `/opt/membrane/backup-pre-wave79/` on golgiBody.

---

## Current VPS State (golgiBody — [RELAY_PUBLIC])

- **13/13 systemd services**: active
- **10/12 UDS ALIVE** via `nucleus_launcher status` (skunkBat TCP-only, squirrel/petaltongue health probe silent)
- **Zero externally-exposed primal TCP ports** (ufw default deny incoming)
- **Sovereign infrastructure**: knot (DNS), caddy (TLS), songbird (TURN :3478, federation :7700), RustDesk — all LIVE
- `nucleus_launcher` v0.9.31 deployed (Wave 79 code)
- `songbird-mesh.service` managing federation (new — was previously unmanaged PID)
- `membrane-socket-bridge.service` for socket path alignment

---

## Remaining Work for cellMembrane

### P0: Fix 3 Primal Binaries for Headless VPS

1. **toadstool** — File issue on `ecoPrimals/toadStool`: binary should not hard-fail without Akida NPU. Add `--headless` or `--no-hardware` flag that skips NPU probe and runs IPC-only.

2. **coralreef** — File issue on `ecoPrimals/coralReef`: binary should not require GPU spec XML at startup. Lazy-load specs on first compile request, or add `--headless` flag.

3. **squirrel** — File issue on `ecoPrimals/squirrel`: binary lost `server` subcommand. Either restore it or add `ipc` subcommand for UDS JSON-RPC service mode.

### ~~P0: sweetgrass `--http-address` Default~~ — RESOLVED

~~sweetgrass defaults `--http-address` to `0.0.0.0:0`~~ Fixed in v0.7.51 — defaults to `127.0.0.1:0`.

### ~~P1: `deploy_membrane.sh` Bug — `build-primal.sh` Empty Release Dir~~ — RESOLVED

~~Root cause unclear~~ Fixed in commit `4c5f08d` — explicit `--target-dir` to cargo build.
Harvest pipeline also evolved to Rust-canonical (`plasmidbin harvest`).

### P1: mesh.init

Once all 13 binaries are fully refreshed (including the 3 rolled back), call:
```bash
ssh root@[RELAY_PUBLIC] "/opt/membrane/songbird mesh.init --peers <eastGate-IP>,<strandGate-IP>"
```
This will trigger BD-TRUST-01 auto trust seeding via `auth.exchange_trust`.

---

## Files Changed

- `plasmidBin/deploy_membrane.sh` — UDS-only unit generation, firewall hardening
- `plasmidBin/membrane/skunkbat-membrane.service` — localhost TCP (UDS pending binary fix)
- `plasmidBin/checksums.toml` — 13 fresh blake3 hashes
- `wateringHole/handoffs/WAVE78_REMAINING_WORK_JUN05_2026.md` — Track 4/4b updated

---

*"The glacier's edge advances. Ten primals renewed, three need the warmth of their home teams."*
