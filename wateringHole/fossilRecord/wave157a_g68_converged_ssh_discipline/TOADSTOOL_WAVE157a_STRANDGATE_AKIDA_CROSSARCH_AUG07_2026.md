# Handoff: toadStool akida-driver Cross-Arch Fix (S357)

**Date**: Aug 7, 2026 | **Wave**: 157a | **Author**: strandGate | **Sprint**: S357

---

## Summary

Applied `#[cfg(unix)]` gating to all hardware-dependent modules in `akida-driver` crate.
This is the **bandaid** fix referenced in Wave 157a deployment sequence step 3.
Proper platform abstraction is tracked under **G68 PLATFORM SUBSTRATE ABSTRACTION**.

## What Changed

### Module-level gating in `crates/neuromorphic/akida-driver/src/lib.rs`

**Gated with `#[cfg(unix)]`** (hardware-only):
- `device`, `io`, `mmio`, `vfio` — direct unix API usage (rustix, libc, std::os::unix)
- `discovery`, `inference`, `loading` — transitively depend on `device`
- `sram`, `puf`, `tenancy` — depend on `backends::mmap`
- `glowplug`, `setup` — VFIO lifecycle, sysfs operations

**Always available** (platform-agnostic):
- `backend` (NpuBackend trait, BackendSelection enum)
- `backends::software` (pure Rust software simulation)
- `capabilities` (data structures, no hardware access)
- `error` (error types)
- `hybrid` (ESN algorithms — software path always available)
- `sentinel` (drift detection — pure math)
- `evolution` (weight evolution — trait-level)
- `pcie_ids` (constants from akida-chip)

### Additional gating

- `Capabilities::from_bar0()` and `MeshTopology::from_bar0()` — `#[cfg(unix)]`
- `HybridEsn::with_hardware_linear()` / `with_hardware_native()` — `#[cfg(unix)]`
- `HybridEsn.hw_backend` field — `#[cfg(unix)]`
- `select_backend()` function — `#[cfg(unix)]`
- `backends/mod.rs`: `kernel`, `mmap`, `userspace` submodules — `#[cfg(unix)]`

### Formatting

`cargo fmt` applied to crate (pre-existing formatting drift in absorbed akida-chip code).

## Verification

| Gate | Result |
|------|--------|
| `cargo check -p akida-driver` (unix) | PASS |
| `cargo check -p akida-driver --target x86_64-pc-windows-msvc` | PASS |
| `cargo check -p toadstool-cli --target x86_64-pc-windows-msvc` | PASS |
| `cargo test -p akida-driver` | PASS (171 tests) |
| `cargo fmt --check` | PASS |

## G68 Relationship

This is explicitly a **bandaid** — silicon deism wearing a mask. The test from G68:

> "Does this primal do *less* on Windows, or the *same thing differently*?"

Answer: **Less**. On Windows, akida-driver exposes traits + software backend + algorithms but no hardware access. G68's proper fix would provide platform-specific backend implementations (Windows WHQL driver path, or remote-device proxy) so the primal does the same thing differently.

## Divergences Noted (from blurb)

- **DIV-2**: toadStool socket permissions (B1/B2) — biomeGate owns, P2
  - Not addressed in this sprint (biomeGate's responsibility)

## Pushed To

- `golgiBody`: `6cfa74b3e` on `main`

## Upstream Notes

- **sporeGate**: Depot rebuild can now include toadStool Windows binary (15/15 cross-arch)
- **G68 team**: Audit shows `akida-driver` has 8 files with direct unix API imports — these are the L3 (device backend) candidates for trait abstraction
