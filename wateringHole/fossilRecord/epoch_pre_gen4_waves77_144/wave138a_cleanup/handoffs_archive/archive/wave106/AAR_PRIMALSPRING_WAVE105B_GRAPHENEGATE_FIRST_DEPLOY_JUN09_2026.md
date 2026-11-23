# AAR: grapheneGate First Deployment — Wave 105b

**Date**: 2026-06-09
**Team**: primalSpring (parallel team) on eastGate
**Device**: Pixel 8 (44251JEKB04957), GrapheneOS

---

## Summary

First deployment of NUCLEUS primals to grapheneGate (Pixel 8) via ADB. 13/13 aarch64-musl binaries built locally on eastGate. 6/13 primals running on device. bearDog BTSP production mode LIVE with family seed.

## What Worked

- **aarch64-unknown-linux-musl**: Correct target for initial GrapheneOS deployment. musl static binaries run natively without NDK.
- **deploy_pixel.sh**: Script correctly handles binary push, startup script generation, ADB port forwarding, and health probing. Only needed one fix (FAMILY_SEED export).
- **bearDog BTSP production mode**: Initialized successfully with BirdSong genetics and family seed on Pixel.
- **songbird**: Responds on HTTP with full federation capabilities (`service_registry`, `federation`, `compute_orchestration`, `task_management`).
- **USB ADB throughput**: 190-400 MB/s push speed. Full 13-primal depot (~130MB total) deploys in seconds.

## What Didn't Work

### NDK (aarch64-linux-android) — Blocked

bearDog's `beardog-tunnel/src/tunnel/hsm/android_strongbox/` module has 16 compilation errors:
- Missing type imports: `KeyGenerationSpec`, `KeyUsage`, `AttestationResponse`, `AuthorizationRequest`, `BackupInfo`, `HsmDeviceInfo`, `KeyBackupSpec`, `KeyInfo`, `SecurityContext`
- Unimplemented methods: `is_healthy()`, `check()`, `attest_device()`
- Type mismatches in `match` arms (8 instances)
- Partially moved `config` value

This is bearDog team debt. The NDK target activates `cfg(target_os = "android")` code paths that are incomplete stubs.

### UDS Path Adaptation — 7 Primals Failed

| Primal | Error | Root Cause |
|--------|-------|------------|
| skunkbat | `No such file or directory` | Expects `/run/user/2000/biomeos/` |
| barracuda | `Permission denied` | UDS socket creation fails |
| coralreef | CLI usage error | Startup args need review |
| nestgate | `Permission denied` (Unix socket bind) | `/tmp` socket creation restricted |
| biomeos | `No such file or directory` | UDS socket path missing |
| petaltongue | `Permission denied` (socket) | `/tmp/biomeos/` restricted |
| toadstool | N/A | Requires `biome.yaml` for server mode |

All failures are due to Android's restricted filesystem: ADB shell user cannot create sockets in `/run/user/` or bind to `/tmp/` paths.

### Build Notes

| Issue | Fix |
|-------|-----|
| `ld.lld` not found (nestGate, rhizoCrypt) | Symlinked `rust-lld` from Rust 1.94.1 toolchain to `~/.local/bin/ld.lld` |
| `aarch64-unknown-linux-musl` target missing for nestGate's pinned 1.94.1 | `rustup target add` to the specific toolchain |
| biomeOS binary not produced by default `cargo build` | Needs `-p biomeos-unibin` (workspace default is lib only) |
| skunkBat binary not produced by default | Needs `-p skunk-bat-server` |
| deploy_pixel.sh missing FAMILY_SEED export | Fixed: added `FAMILY_SEED` and `BEARDOG_FAMILY_SEED` env var export to startup script |

## Running Primals on Pixel 8

| Primal | PID | Transport | Status |
|--------|-----|-----------|--------|
| beardog | 13990 | TCP 9100 | LIVE — BTSP production, BirdSong genetics |
| songbird | 14003 | HTTP 9200 | LIVE — federation capabilities |
| rhizocrypt | 14150 | TCP 9601 | LIVE |
| loamspine | 14170 | TCP 9700 | LIVE |
| sweetgrass | 14190 | TCP 9850 | LIVE |
| squirrel | 14226 | HTTP 9300 | LIVE |

## Recommendations

1. **Android UDS adaptation**: Add `BIOMEOS_SOCKET_DIR` env var override to primals, defaulting to `$HOME/biomeos/` on Android. deploy_pixel.sh should set this.
2. **bearDog StrongBox**: Complete the android_strongbox type definitions. These are needed for Titan M2 HSM integration (Role 3).
3. **deploy_pixel.sh cleanup**: Kill stale processes by binary path before relaunch to avoid port conflicts.
4. **Role 1 beacon**: Requires Dark Forest mode with songbird running cleanly. Fix the port conflict (stale ADB forwards) to validate UDP beacon broadcast.

## Next Steps

- Android UDS path adaptation for remaining 7 primals
- Dark Forest beacon broadcast validation
- bearDog StrongBox NDK compilation (bearDog team)
- Role 2 relay bootstrap testing
