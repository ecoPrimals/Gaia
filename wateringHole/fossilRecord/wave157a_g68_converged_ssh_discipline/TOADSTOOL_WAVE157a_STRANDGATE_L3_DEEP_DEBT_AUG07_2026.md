# Handoff: toadStool G68 L3 Backend Traits + Deep Debt Audit (S360)

**Date**: Aug 7, 2026 | **Sprint**: S360 | **Wave**: 157a
**Author**: strandGate | **Primal**: toadStool
**Commit**: `2b2273822` on `main`

---

## Summary

G68 L3 trait definitions shipped. Full deep debt audit completed. `akida-driver` hybrid module refactored from monolith (995L) into focused submodules. Comprehensive sweep confirms no remaining evolution gaps in production code.

## Changes

### G68 L3 — Device I/O Backend Traits

New module `toadstool-common::platform::device_io` defines trait abstractions for all hardware device I/O operations:

| Trait | Abstraction | Use |
|-------|------------|-----|
| `MappedMemory` | Memory-mapped I/O region lifecycle | BAR access, DMA buffers |
| `MemoryMapper` | Create mappings from files or anonymous | MMIO, huge pages |
| `PinnedMemory` | mlock/munlock for DMA stability | Cylinder, hw-safe DMA |
| `DeviceFile` | Device node open/read/write | akida-driver, cylinder |
| `EventNotifier` | Interrupt notification (eventfd+poll) | VFIO IRQ, nvpmu |
| `ProcessIsolation` | Fork-and-exec for untrusted ops | Guarded sysfs writes |

**Design principle**: Safe trait API surface; unsafe contained in hardware crate implementations. Enables mockability for testing without `#[cfg(test)]` pollution.

### Smart Refactor — akida-driver hybrid (995L → 4 modules)

| Module | Content | Lines |
|--------|---------|-------|
| `weights.rs` | `EsnWeights` struct + spectral radius | 115 |
| `substrate.rs` | `SubstrateMode`, `EsnSubstrate` trait, `SubstrateInfo` | 130 |
| `selector.rs` | `SubstrateSelector` runtime dispatch | 90 |
| `mod.rs` | `HybridEsn` core + tests | ~580 |

All 14 unit tests + 4 doctests pass unchanged.

### Deep Debt Audit Results

| Category | Finding |
|----------|---------|
| **Unsafe code** | All in designated crates (cylinder, hw-safe, nvpmu, akida-driver, display, ffi_loader). Hardware-mandated. SAFETY-justified. |
| **External C deps** | Zero. All evolved to `rustix` (pure Rust syscalls). Only `drm` crate external. |
| **Production stubs** | All fail-closed. `glowplug_client_stub` (non-Linux), `unix_jsonrpc_client_stub` (non-Unix), `StubRuntimeEngine` (probes backends, reports status). |
| **Mocks in production** | Zero. `InMemoryBackend` gated behind `#[cfg(test)]`. |
| **Overstep** | Eliminated in S355. Remaining primal names are in deprecated interned constants and serde backward-compat aliases. |
| **Hardcoding** | Centralized in `constants/network.rs` and `constants/ecosystem.rs`. No inline literals in production dispatch. |
| **Large files** | Only 2 remain >800L: `capabilities.rs` (922) and `vfio/mod.rs` (877) in akida-driver — structurally coherent, splitting would fragment context. Both `#[cfg(unix)]` gated. |

## G68 Full Compliance Status

| Layer | Status | Remaining |
|-------|--------|-----------|
| **L1 (Links)** | COMPLIANT | 0 violations |
| **L2 (Access)** | COMPLIANT | 0 violations in production |
| **L3 (Device Backends)** | TRAITS DEFINED | 11 crate-level violations — implementations remain in hardware crates behind `#[cfg(unix)]`. Trait migration is incremental. |

## Quality Gates

- `cargo check --workspace`: 0 errors, 0 warnings
- `cargo fmt --check`: PASS
- `cargo clippy -p toadstool-common -p akida-setup`: PASS
- `cargo test` (affected crates): 1,807 tests, 0 failures
- `cargo check -p toadstool-cli --target x86_64-pc-windows-msvc`: PASS

## Notes for Upstream

- **sourDough**: L3 trait definitions can inform the G68 spec's "device backend abstraction" layer. Suggest `sourDough validate` add an L3 category that checks for trait impl presence.
- **All teams**: The trait layer in `toadstool-common::platform::device_io` is portable — other primals with device I/O (bearDog, biomeOS) could adopt these same interfaces.
- **hotSpring**: The hybrid ESN refactor doesn't change the public API. `HybridEsn`, `EsnSubstrate`, `SubstrateSelector` remain at the same crate-level paths.
