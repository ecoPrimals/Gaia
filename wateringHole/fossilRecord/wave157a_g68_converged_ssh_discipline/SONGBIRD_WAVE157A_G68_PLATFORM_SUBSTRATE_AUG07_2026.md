# Handoff: songBird G68 Platform Substrate — Wave 157a

**Date**: August 7, 2026  
**Wave**: 157a  
**Author**: overwatch  
**Primal**: songBird  
**Status**: G68 COMPLIANT

---

## Summary

songBird is now G68 compliant. All filesystem permission operations route through the `platform_substrate` module's `PlatformAccess::apply()` abstraction. Symlink creation uses `platform_link()`. Zero raw `PermissionsExt` imports remain in IPC or deployment business logic.

## What Was Done

### New Module: `platform_substrate.rs` (songbird-types)

- **L1 Links**: `platform_link()` — symlink on Unix, hard-link/symlink on Windows
- **L2 Permissions**: `PlatformAccess` enum with 6 variants:
  - `OwnerReadWrite` (0o600) — sockets, secrets
  - `GroupReadWrite` (0o660) — shared sockets (tarpc UDS)
  - `OwnerFull` (0o700) — private directories
  - `PublicExecute` (0o755) — deployed binaries
  - `PublicRead` (0o644) — config files
  - `Readonly` (0o400) — immutable secrets
- `is_unix_socket()` — platform-aware socket file detection
- `is_symlink()` — portable symlink detection
- 8 unit tests

### Violations Fixed (6 L2 + 1 L1 = 7 total)

| File | Before | After |
|------|--------|-------|
| `tarpc_server/accept.rs` | `Permissions::from_mode(0o660)` | `PlatformAccess::GroupReadWrite.apply()` |
| `deployment_api/mod.rs` | `perms.set_mode(0o755)` | `PlatformAccess::PublicExecute.apply()` |
| `platform/unix.rs` | `Permissions::from_mode(0o600)` | `PlatformAccess::OwnerReadWrite.apply()` |
| `pure_rust_server/connection.rs` | `Permissions::from_mode(0o600)` | `PlatformAccess::OwnerReadWrite.apply()` |
| `chunked_upload.rs` | `perms.set_mode(0o755)` | `PlatformAccess::PublicExecute.apply()` |
| `deployment_api/binary.rs` | `perms.set_mode(0o755)` | `PlatformAccess::PublicExecute.apply()` |
| `env_config/socket.rs` | `std::os::unix::fs::symlink()` | `songbird_types::platform_link()` |

### `PermissionsExt` now confined to:

- `platform_substrate.rs` (the L2 implementation — the only correct location per G68)
- `tcp_biomeos.rs` `FileTypeExt::is_socket()` (inside `#[cfg(unix)]` discovery module)

## Verification

```bash
cargo clippy --workspace --all-targets -- -D warnings     # ZERO warnings
cargo check --target x86_64-pc-windows-gnu                # CLEAN
cargo test -p songbird-types platform_substrate           # 8/8 pass
```

## G68 Compliance Status

songBird moves from "Moderate (5 L2)" to **COMPLIANT** per the sourDough G68 audit criteria:
- L1: `platform_link()` ✓
- L2: All permissions via `PlatformAccess::apply()` ✓
- L3: N/A (songBird has no device I/O)

## Reference

- sourDough `platform_substrate` module — G68 reference implementation
- `specs/PLATFORM_SUBSTRATE_SPEC.md` — G68 standard
- `sourdough validate platform-substrate /path/to/primal` — ecosystem scanner

---

*Wave 157a — songBird G68 COMPLIANT. 7 violations fixed. PlatformAccess::apply() for permissions, platform_link() for symlinks. Windows cross-compile clean. 4/15 G68 compliant (sourDough, squirrel, nestGate, songBird).*
