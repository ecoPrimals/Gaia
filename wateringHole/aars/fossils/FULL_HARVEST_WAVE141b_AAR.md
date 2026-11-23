# AAR: Full Multi-Architecture Harvest — Wave 141b

**Date**: 2026-07-15 20:25 EDT | **Gate**: eastGate → sporeGate (builder)
**Wave**: 141b | **Operator**: sporeGate hardware team

---

## Summary

Executed full 14-primal harvest for Windows (`x86_64-pc-windows-gnu`) and Android
(`aarch64-linux-android`) following the "ALL 14 PRIMALS CROSS-ARCHITECTURE COMPLETE"
milestone. Combined with existing musl harvests, depot now holds **55 binaries across
4 architectures**, all signed and pushed to VPS.

## Results

### Windows Harvest: 11/14

| Primal | Status | Size | Notes |
|--------|--------|------|-------|
| songBird | OK | 23M | |
| nestGate | OK | 8.0M | |
| biomeOS | OK | 19M | |
| rhizoCrypt | OK | 5.9M | |
| sweetGrass | OK | 15M | |
| loamSpine | OK | 3.9M | |
| skunkBat | OK | 2.5M | |
| coralReef | OK | 6.9M | |
| barraCuda | OK | 4.9M | |
| toadStool | OK | 8.9M | |
| sourDough | OK | 2.8M | |
| **bearDog** | **FAILED** | — | `UnixStream` in `beardog-core` (UDS not abstracted) |
| **squirrel** | **FAILED** | — | `universal-patterns` crate: 3 compile errors |
| **petalTongue** | **FAILED** | — | `petal-tongue-ipc`: 12 errors (UDS deps) |

### Android Harvest: 11/14

| Primal | Status | Size | Notes |
|--------|--------|------|-------|
| bearDog | OK | 9.1M | |
| songBird | OK | 22M | |
| nestGate | OK | 7.7M | |
| biomeOS | OK | 19M | |
| rhizoCrypt | OK | 6.1M | |
| squirrel | OK | 3.6M | |
| sweetGrass | OK | 11M | |
| loamSpine | OK | 3.8M | |
| skunkBat | OK | 2.5M | |
| coralReef | OK | 6.6M | |
| barraCuda | OK | 4.4M | |
| **petalTongue** | **FAILED** | — | `petal-tongue-ipc`: UDS/platform deps |
| **toadStool** | **FAILED** | — | `akida-driver`: platform-specific errors |
| **sourDough** | **FAILED** | — | `sourdough-genomebin`: platform cfg fallback |

### Full Depot Summary

| Architecture | Binaries | Status |
|--------------|----------|--------|
| x86_64-unknown-linux-musl | 16/16 | COMPLETE |
| aarch64-unknown-linux-musl | 16/16 | COMPLETE |
| x86_64-pc-windows-gnu | 11/14 | 3 parity gaps |
| aarch64-linux-android | 11/14 | 3 parity gaps |
| **Total** | **55** | **Signed + VPS-live** |

## Root Cause Analysis — Failures

### Common Pattern: Unconditional UDS (Unix Domain Socket)

- **bearDog** (Windows): `beardog-core` directly uses `tokio::net::UnixStream` without
  `#[cfg(unix)]` gating. The FIDO2 IPC layer goes through a UDS listener that has no
  Windows fallback to Named Pipes yet.

- **petalTongue** (Windows + Android): `petal-tongue-ipc` has 12 compile errors — all
  UDS-related. This is the most UDS-coupled primal.

- **squirrel** (Windows): `universal-patterns` crate has 3 errors — likely UDS or signal
  handling deps that haven't been cfg-gated.

### Android-Specific

- **toadStool** (Android): `akida-driver` crate has platform-specific dependencies (likely
  kernel/device-driver interfaces).

- **sourDough** (Android): `sourdough-genomebin` hits a cfg fallback for unsupported platforms.

## Actions Taken

1. Added Windows target to all 11 toolchain overrides (1.93.0, 1.94.0, 1.94.1, stable)
2. Built all 14 primals for both Windows and Android
3. Regenerated BLAKE3 `checksums.toml` for 55 binaries
4. Signed with Ed25519 via `membrane sign.activate`
5. Rsync'd full depot to golgi VPS
6. Verified WAN serving (membrane.primals.eco/depot/ — all 200)
7. Updated `plasmidBin` repo with fresh checksums + signatures
8. Updated eastGate heads

## Handoffs

| Team | Action | Priority |
|------|--------|----------|
| bearDog team | Abstract UDS in `beardog-core` to use `primal-transport` | P1 |
| petalTongue team | Replace all UDS in `petal-tongue-ipc` with transport layer | P1 |
| squirrel team | Fix `universal-patterns` Windows compile errors | P1 |
| toadStool team | Gate `akida-driver` platform deps | P2 |
| sourDough team | Fix `sourdough-genomebin` platform cfg | P2 |
| cellMembrane team | Add sporePrint health check to cascade post-sync | P3 |

## Metrics

- Build time: ~22 min Windows, ~29 min Android (sequential, on sporeGate)
- Depot size: 513 MB total across 4 architectures
- VPS sync: 72 MB transferred (delta), 3.4s
