# ToadStool — S362 G68 L3 Full Migration

**Date**: Aug 7, 2026
**Operator**: strandGate (eastGate overwatch)
**Sprint**: S362
**Scope**: G68 L3 Device Backend — full trait implementation + device open migration

---

## Summary

Completed the G68 L3 backend trait implementation cycle:
- All 5 trait concrete implementations live in `hw-safe/platform_backends.rs`
- Device open sites in `display/drm` and `display/v4l2` migrated away from raw `rustix::fs::open`
- L3 audit concluded: remaining 8 rustix call sites are irreducible (device driver ops)

---

## Changes

### New L3 Implementations (hw-safe/platform_backends.rs)

| Trait | Concrete Struct | Syscalls |
|-------|----------------|----------|
| `MappedMemory` | `SafeMmapRegion` | mmap/munmap (S361) |
| `MemoryMapper` | `LinuxMemoryMapper` | mmap/mmap_anonymous (S361) |
| `PinnedMemory` | `LinuxPinnedMemory` | mlock/munlock (S361) |
| `DeviceFile` | `LinuxDeviceFile` | open (RDWR/RDONLY + CLOEXEC + NONBLOCK) |
| `EventNotifier` | `LinuxEventNotifier` | eventfd + poll + read/write |

### Migrations

| File | Before | After |
|------|--------|-------|
| `display/drm/device.rs` | `rustix::fs::open(path, OFlags::RDWR \| CLOEXEC)` | `LinuxDeviceFile.open(path, true, false)` |
| `display/v4l2/device.rs` | `rustix::fs::open(path, OFlags::RDWR \| NONBLOCK \| CLOEXEC)` | `LinuxDeviceFile.open(path, true, true)` |

### Documentation Updates

- `platform/device_io.rs`: Added implementation status table, updated module docs
- `ProcessIsolation` trait: Added implementation note explaining why fork isolation cannot use the trait interface (async-signal-safety constraints)

---

## L3 Irreducible Sites (Audit Conclusion)

The following rustix call sites are **correctly placed** and cannot be further abstracted without loss of clarity or functionality:

| Module | Syscalls | Why Irreducible |
|--------|----------|----------------|
| `cylinder/vfio/dma.rs` | alloc_zeroed + mlock + munlock + dealloc | Raw allocation + page pinning for DMA; not a slice at mlock time |
| `cylinder/vfio/isolation.rs` | fork + pipe + waitpid + kill | Async-signal-safety requires pipe-based communication |
| `cylinder/vfio/irq.rs` | eventfd + poll + read | VFIO IRQ arming tightly coupled to device fd |
| `cylinder/vfio/ioctl.rs` | ioctl (VFIO ioctls) | Kernel ABI — no further abstraction possible |
| `v4l2/ioctl.rs` | ioctl (V4L2 ioctls) | Kernel ABI — type-safe rustix wrappers ARE the abstraction |
| `sandbox/linux/mod.rs` | mount + unmount | Namespace isolation — inherently Linux |
| `sandbox/linux/privilege.rs` | capabilities() | Capability probing — inherently Linux |
| `sandbox/linux/proc.rs` | clock_ticks_per_second() | Jiffies conversion — inherently Linux |
| `hw-safe/locked_memory.rs` | mlock + munlock + madvise | Already in containment crate |
| `hw-safe/huge_page.rs` | mmap_anonymous + mlock + munmap | Already in containment crate |

All sites have `// SAFETY:` documentation. All unsafe is in designated crates (`hw-safe`, `cylinder`).

---

## Quality Gates

| Gate | Result |
|------|--------|
| `cargo fmt --check` | PASS |
| `cargo clippy -D warnings` (hw-safe, display, cylinder) | PASS |
| `cargo check --workspace` | PASS |
| `cargo test -p toadstool-hw-safe -p toadstool-display -p toadstool-cylinder` | PASS |
| `cargo test --workspace` | 1 pre-existing failure (beardog integration, requires Tower) |

---

## G68 Compliance Status

| Level | Status |
|-------|--------|
| L1 (Links/Symlinks) | COMPLIANT (S358) |
| L2 (Permissions) | COMPLIANT (S359) |
| L3 (Device Backends) | **COMPLIANT** — all abstractable sites migrated, irreducible sites documented |

---

## Remaining Work (glacial)

- `ProcessIsolation` concrete struct: Would require redesigning the trait to accept a pipe fd instead of `Box<dyn FnOnce>`. Low value — the existing `fork_isolated_raw` works correctly.
- Narrow `display/Cargo.toml` rustix features from `all-apis` to just `ioctl` (cosmetic).
- Scanner false positive (`SubstrateMode::mode()`) still reported by sourdough.
