# ToadStool — S364 G68 L3 Full Trait Surface

**Date**: Aug 7, 2026
**Operator**: strandGate (eastGate overwatch)
**Sprint**: S364
**Scope**: G68 L3 — Complete cross-platform trait abstraction for all device operations

---

## Summary

Every remaining Linux-specific device operation now has a corresponding
platform-agnostic trait in `toadstool-common::platform::device_io`. The trait
surface is the **porting contract** — when graftGate (G12) or riscGate (G42)
materializes, new architectures implement traits rather than raw syscalls.

---

## New Traits (S364)

| Trait | What it Abstracts | Linux | macOS (future) | Windows (future) |
|-------|-------------------|-------|----------------|------------------|
| `DeviceIoctl` | Typed device control commands | `ioctl(fd, req, arg)` | `IOConnectCallMethod` | `DeviceIoControl` |
| `PrivilegeProbe` | Process privilege checking | POSIX capabilities | Entitlements | Token privileges |
| `FilesystemIsolation` | Sandbox filesystem views | Mount namespaces | `sandbox_init` | AppContainer |
| `FdPassing` | Handle transfer between processes | SCM_RIGHTS | Mach port rights | `DuplicateHandle` |
| `SystemParameters` | Platform constants | `sysconf` | `sysctl` | `GetSystemInfo` |

## New Implementation

| Struct | Trait | Function |
|--------|-------|----------|
| `LinuxSystemParameters` | `SystemParameters` | `clock_ticks_per_second()`, `page_size()`, `huge_page_size()` |

---

## Complete L3 Trait Surface (11 traits)

| # | Trait | Impl Status | Where |
|---|-------|-------------|-------|
| 1 | `MappedMemory` | **DONE** | `SafeMmapRegion` in hw-safe |
| 2 | `MemoryMapper` | **DONE** | `LinuxMemoryMapper` in hw-safe |
| 3 | `PinnedMemory` | **DONE** | `LinuxPinnedMemory` in hw-safe |
| 4 | `DeviceFile` | **DONE** | `LinuxDeviceFile` in hw-safe |
| 5 | `EventNotifier` | **DONE** | `LinuxEventNotifier` in hw-safe |
| 6 | `SystemParameters` | **DONE** | `LinuxSystemParameters` in hw-safe |
| 7 | `DeviceIoctl` | **per-device** | compile-time typed in hw-safe/cylinder/nvpmu |
| 8 | `ProcessIsolation` | **pipe-based** | `fork_isolated_raw` in cylinder |
| 9 | `PrivilegeProbe` | **inline** | sandbox/linux/privilege.rs |
| 10 | `FilesystemIsolation` | **inline** | sandbox/linux/mod.rs |
| 11 | `FdPassing` | **inline** | cylinder/vfio/ember_client.rs |

Items 7-11 have working Linux implementations in their respective modules.
They don't use the trait interface yet (the trait is the porting contract).
Migration to trait dispatch is a future task when graftGate needs it.

---

## Design Decisions

### DeviceIoctl: Runtime vs Compile-time

The `DeviceIoctl` trait uses runtime `u32` request codes (matching Windows `DeviceIoControl`
semantics). The existing Linux implementations use compile-time const generics (`const OP: Opcode`)
for type safety. Both are correct — the trait is the cross-platform interface contract,
the existing code is the optimal Linux implementation.

### ProcessIsolation: Why not trait-conformant

Linux fork isolation requires async-signal-safety in the child (no heap allocation,
no mutex locking). The trait's `Box<dyn FnOnce() -> Vec<u8>>` interface inherently
allocates. The trait documents the semantic operation; the concrete implementation
uses a pipe-fd-based protocol for correctness.

---

## Quality Gates

| Gate | Result |
|------|--------|
| `cargo fmt --check` | PASS |
| `cargo clippy -D warnings` (common, hw-safe) | PASS |
| `cargo check --workspace` | PASS |
| `cargo check --workspace --target x86_64-pc-windows-msvc` | PASS |

---

## What This Enables

When `graftGate` (macOS / apple-darwin) or `riscGate` (RISC-V) is implemented:

1. Add `platform_backends_darwin.rs` or `platform_backends_riscv.rs`
2. Implement the 11 traits using platform-native mechanisms
3. Gate with `#[cfg(target_os = "macos")]` / `#[cfg(target_arch = "riscv64")]`
4. All higher-level code works unchanged

No "chasing the same debt on unfamiliar architectures" — the contract is specified.
