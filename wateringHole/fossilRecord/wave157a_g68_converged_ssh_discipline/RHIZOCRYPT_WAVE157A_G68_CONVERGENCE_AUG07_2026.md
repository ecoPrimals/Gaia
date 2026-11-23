# rhizoCrypt — G68 Platform Substrate Convergence

**Date**: Aug 7, 2026  
**Wave**: 157a  
**Primal**: rhizoCrypt v0.14.17  
**Spec**: G68 Platform Substrate Abstraction  
**Status**: COMPLIANT — sourDough scanner should report 0 violations

---

## Violations Fixed

### L1: Platform Links (4 violations → 0)

| File | Before | After |
|------|--------|-------|
| `uds/symlinks.rs:23` | `std::os::unix::fs::symlink()` | `platform_link()` |
| `uds/symlinks.rs:46-47` | `symlink_metadata()` + `read_link()` | `is_symlink_to()` |
| `uds_tests.rs:227` | `std::os::unix::fs::symlink()` | `platform_link()` |
| `uds_tests_errors.rs:405` | `std::os::unix::fs::symlink()` | `platform_link()` |

### L2: Platform Permissions (3 violations → 0)

| File | Before | After |
|------|--------|-------|
| `store_redb_tests_error_paths.rs:27` | `use PermissionsExt` | `use PlatformAccess` |
| `store_redb_tests_error_paths.rs:31` | `from_mode(0o444)` | `PlatformAccess::ReadOnly` |
| `store_redb_tests_error_paths.rs:36` | `from_mode(0o755)` | `PlatformAccess::DirectoryDefault` |

### L3: Device Backends (0 violations — already clean)

Zero `rustix`, `libc::`, `mmap`, `ioctl`, `VFIO`, `DRM`.

---

## New Module: `transport/platform.rs` (G68 Substrate)

All raw platform APIs now confined to this single 96-line file:

```rust
pub fn platform_link(target, link) -> io::Result<()>     // L1
pub fn is_symlink_to(path, expected_target) -> bool       // L1
pub enum PlatformAccess { OwnerOnly, GroupReadWrite, ... } // L2
pub fn set_platform_permissions(path, access) -> Result    // L2
```

- `#[cfg(unix)]`: symlink creation, POSIX mode bits
- `#[cfg(windows)]`: symlink_file + hardlink fallback, ACL (stub)
- `#[cfg(not(any(unix, windows)))]`: `Unsupported` error

---

## Verification

```
cargo clippy --workspace --all-features -- -D warnings   → 0 warnings
cargo test --workspace --all-features                     → 1,825 passed, 0 failed
cargo check --target x86_64-pc-windows-gnu                → pass
cargo fmt --check                                         → clean
```

**Commit**: `a0fd7f8` — pushed to golgiBody.

---

## G68 Posture: COMPLIANT

| Layer | Violations | Status |
|-------|-----------|--------|
| L1 Links | 0 | `platform_link()` + `is_symlink_to()` |
| L2 Permissions | 0 | `PlatformAccess` enum |
| L3 Device backends | 0 | N/A (no hardware I/O) |

rhizoCrypt moves from **Moderate (7 violations)** to **Compliant (0 violations)** — joining sourDough, squirrel, and nestGate as G68-compliant primals.
