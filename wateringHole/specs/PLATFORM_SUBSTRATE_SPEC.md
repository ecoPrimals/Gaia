# Platform Substrate Abstraction Specification (G68)

**Date**: Aug 7, 2026 | **Wave**: 157a | **Author**: eastGate overwatch
**Status**: SPECIFICATION — sourDough reference, ecosystem convergence target
**Predecessor**: G66 Transport Abstraction (COMPLETE — 15/15)
**Origin**: toadStool `akida-driver` absorption exposed that `#[cfg(unix)]` gating is silicon deism with extra steps — it hides code instead of abstracting it

---

## The Problem: cfg(unix) Is Not Abstraction

G66 solved transport: primals use `TransportEndpoint`/`TransportStream`/`connect_transport()`
instead of raw `UnixStream`. But the ecosystem still has three deeper layers of
platform coupling that G66 did not address:

```rust
// G66 SOLVED: transport (how bytes move between primals)
use tokio::net::UnixStream;  // → TransportStream

// G68 TARGETS: substrate (how primals touch the platform)
use std::os::unix::fs::symlink;         // socket links
use std::os::unix::fs::PermissionsExt;  // file permissions
use rustix::mm::mmap;                   // device memory
use rustix::fd::BorrowedFd;             // raw file descriptors
```

The current fix pattern — wrapping modules in `#[cfg(unix)]` — is silicon deism
wearing a mask. The code doesn't exist on Windows; it's not that the code works
on Windows. A primal that compiles on Windows but has half its capabilities gated
behind `#[cfg(unix)]` is not cross-platform — it's a stub.

---

## Audit: Current Violations (Wave 157a)

| Violation | Files | Primals | Severity |
|-----------|-------|---------|----------|
| Raw `UnixStream` (bypasses G66) | 24 | 9/15 | **HIGH** — G66 already solved this |
| Raw `std::os::unix::fs::symlink` | 17 | 10/15 | **MEDIUM** — needs platform link |
| Raw `PermissionsExt` (mode bits) | 56+ | 13/15 | **HIGH** — pervasive, needs abstraction |
| Raw `rustix`/`libc` (kernel APIs) | 37 | 3/15 | **LOW** — hardware-justified in toadStool/biomeOS |

**Total**: 134+ files across 15 primals.

sourDough's `transport_compliance.rs` already detects classes 1 and 4. Classes 2
and 3 need new detection rules.

---

## Three Abstraction Layers

### Layer 1: Platform Links (symlink → platform_link)

**Problem**: Socket convenience links use `std::os::unix::fs::symlink`. Windows
has `junction_point`, NTFS symlinks (requires privilege), and hardlinks.

**Abstraction**:

```rust
pub fn platform_link(target: &Path, link: &Path) -> io::Result<()> {
    #[cfg(unix)]
    { std::os::unix::fs::symlink(target, link) }
    #[cfg(windows)]
    { std::os::windows::fs::symlink_file(target, link)
      .or_else(|_| std::fs::hard_link(target, link)) }
}
```

**Who**: Every primal that creates socket symlinks (10/15).

**Reference**: sourDough should implement `platform_link()` in its
transport module. Primals converge by reading the pattern.

### Layer 2: Platform Permissions (PermissionsExt → platform_permissions)

**Problem**: 56+ files use `PermissionsExt::set_mode(0o660)`. Windows has ACLs,
not POSIX mode bits. Setting `0o660` on Windows is a no-op at best.

**Abstraction**:

```rust
pub enum PlatformAccess {
    OwnerOnly,        // 0o600 / owner-only ACL
    GroupReadWrite,   // 0o660 / Users group RW
    WorldReadable,    // 0o644 / Everyone read
}

pub fn set_platform_permissions(path: &Path, access: PlatformAccess) -> io::Result<()> {
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mode = match access {
            PlatformAccess::OwnerOnly => 0o600,
            PlatformAccess::GroupReadWrite => 0o660,
            PlatformAccess::WorldReadable => 0o644,
        };
        std::fs::set_permissions(path, std::fs::Permissions::from_mode(mode))
    }
    #[cfg(windows)]
    {
        // Windows: ACL manipulation via windows-sys or default perms
        // For sockets: Windows named pipes have their own security model
        Ok(())
    }
}
```

**Who**: All primals (13/15 have violations). This is the most pervasive issue.

**Reference**: sourDough's `genomebin/validator.rs` already uses `PermissionsExt`
in 3 places. It should implement `PlatformAccess` first.

### Layer 3: Device Backends (rustix/libc → DeviceBackend trait)

**Problem**: toadStool and biomeOS use `rustix` for VFIO, mmap, DRM, V4L2.
These are genuinely Linux kernel interfaces. The code CANNOT be made cross-platform
by changing the API — the underlying kernel subsystem doesn't exist on Windows.

**Abstraction**: Backend trait hierarchy.

```rust
pub trait DeviceBackend: Send + Sync {
    fn probe(&self) -> Result<Vec<DeviceInfo>>;
    fn open(&self, info: &DeviceInfo) -> Result<DeviceHandle>;
    fn read(&self, handle: &DeviceHandle, buf: &mut [u8]) -> Result<usize>;
    fn write(&self, handle: &DeviceHandle, data: &[u8]) -> Result<usize>;
    fn capabilities(&self, handle: &DeviceHandle) -> Result<Capabilities>;
}

// Linux: VfioBackend (mmap + DMA + ioctls)
// Windows: SetupApiBackend (WinUSB + SetupDi)
// Software: SyntheticBackend (test/simulation)
// WASM: EmulatedBackend (pure math, no hardware)
```

toadStool already has `NpuBackend` trait + `SyntheticBackend` + `SoftwareBackend`.
The architecture IS there — but `DeviceManager::discover()` and the VFIO backend
are unconditionally compiled. Gate the backends, not the trait.

**Who**: toadStool (akida-driver, cylinder, hw-safe, nvpmu, display, sandbox),
biomeOS (biomeos-boot, biomeos-deploy QEMU paths).

---

## Convergence Pattern

Same as G66 — convergent evolution, not shared dependency:

1. **sourDough implements** `platform_link()` and `PlatformAccess` in its
   existing transport/platform module
2. **sourDough's `transport_compliance.rs`** adds detection rules for Layer 1
   (raw symlink) and Layer 2 (raw PermissionsExt)
3. **Each primal reads the pattern** and evolves independently
4. **Pre-push check**: `cargo check --target x86_64-pc-windows-gnu` catches
   regressions (already mandated by G66)
5. **sourDough validates**: `sourdough validate transport <primal>` reports
   remaining violations

### Priority Order

1. **Layer 1 (symlinks)** — 17 files, simple abstraction. 1-2 hours per primal.
2. **Layer 2 (permissions)** — 56+ files, pervasive but mechanical. 2-4 hours per primal.
3. **Layer 3 (device backends)** — 37 files, architectural. toadStool-only initially.
   biomeOS boot paths are glacial (biomeOS-as-OS is Stage 3).

### What Is NOT Silicon Deism

- `#[cfg(unix)]` on a **test module** that tests unix-specific behavior → acceptable
- `#[cfg(unix)]` on a **backend implementation** behind a trait → acceptable (the
  trait compiles everywhere, the backend is platform-specific)
- `#[cfg(unix)]` on an **entire module** that hides functionality → **silicon deism**

The test: "Does this primal do less on Windows, or does it do the same thing differently?"
If less → silicon deism. If differently → platform abstraction.

---

## Relationship to Existing Goals

| Goal | Relationship |
|------|-------------|
| G66 Transport Abstraction | **Predecessor.** G68 extends the philosophy to non-transport platform APIs. |
| G67 Neural API | **Consumer.** Neural API routes capabilities — if a primal's capabilities are gated behind `#[cfg(unix)]`, Neural API sees a reduced surface on Windows. |
| G32 Silicon deism vendor cracking | **Sibling.** G32 targets GPU vendor lock-in. G68 targets OS lock-in. Same philosophy, different substrate. |
| G64 Cephalization | **Enabler.** True cephalization means primals converge on patterns that work everywhere, not patterns that compile everywhere. |

---

## Acceptance Criteria

G68 is COMPLETE when:

1. sourDough reference implementation has `platform_link()` and `PlatformAccess`
2. sourDough `transport_compliance` detects all three violation classes
3. 0 primals use raw `std::os::unix::fs::symlink` outside `#[cfg(unix)]` test modules
4. 0 primals use raw `PermissionsExt` outside `#[cfg(unix)]` test modules
5. toadStool device backends compile on all targets (trait everywhere, impl gated)
6. `cargo check --target x86_64-pc-windows-gnu` passes with full capability surface
7. A primal's `capability.list` returns the same methods on Linux and Windows

---

*G68 Platform Substrate Abstraction — the next evolution beyond G66 transport.
`#[cfg(unix)]` hides code. Platform abstraction makes it work everywhere.
sourDough leads by example. Primals converge independently.*
