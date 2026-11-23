<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Sprint 5: Pass 12 Sentinel Gaps

**Date**: May 12, 2026
**From**: coralReef
**Context**: primalSpring upstream audit — Passes 12-14 (Stadial Gate Remaining Work)

---

## Summary

Three Pass 12 sentinel escalation items resolved: `naga::Module` direct ingest API (skip text→parse round-trip for in-process callers), compile deadline on all IPC handlers (prevents unbounded blocking), Volta+/Blackwell cold init wired to attempt PIO FECS/GPCCS falcon boot. 4790 tests (+6), zero clippy warnings.

## Changes

### `naga::Module` Direct Ingest (`lib.rs`, `ptx_emit/mod.rs`)

- New public `compile_module()` and `compile_module_full()` — accept pre-parsed `naga::Module` directly
- New `emit_compute_ptx_module()` — PTX path for SM100+ targets accepts `&naga::Module`
- `pub use naga` re-export for downstream convenience
- 6 new tests: empty module rejection, minimal compute, full metadata, WGSL output parity, AMD target, Intel unsupported

### Compile Deadline (`newline_jsonrpc.rs`, `tarpc_transport.rs`)

- All `shader.compile.*` IPC handlers (JSON-RPC newline + Unix socket + tarpc) wrapped in `tokio::time::timeout`
- Default: 120s, configurable via `CORALREEF_COMPILE_TIMEOUT_SECS`
- Returns structured error on timeout instead of hanging

### FECS/GPCCS Cold Silicon Init (`boot_sequence.rs`, `fecs_boot.rs`)

- `VoltaBoot::cold_init` and `BlackwellBoot::cold_init` now attempt PIO falcon boot (`boot_gr_falcons`) when firmware available on disk
- Graceful fallback: clear tracing diagnostic when firmware missing or ACR/SEC2 required
- `firmware_available()` respects `CORALREEF_NVIDIA_FIRMWARE_ROOT` env var (aligns with GSP firmware parser)

### Deep Debt: Firmware Path Centralization (`linux_paths.rs`, 8 sites)

- New `nvidia_firmware_root()` / `nvidia_firmware_path(chip, tail)` in `linux_paths.rs` — single source of truth for `CORALREEF_NVIDIA_FIRMWARE_ROOT`
- 8 firmware loading sites migrated from hardcoded `/lib/firmware/nvidia/` to `linux_paths::nvidia_firmware_path()`:
  - `fecs_boot.rs` (FecsFirmware::load, GpccsFirmware::load, firmware_available)
  - `pri.rs` (apply_sw_nonctx)
  - `acr_boot/firmware.rs` (AcrFirmwareSet::load)
  - `sovereign_stages.rs` (gr init firmware load)
  - `kepler_fecs_boot/firmware.rs` (gk210-system search path)
  - `identity/firmware.rs` (firmware_inventory, check_nouveau_firmware)
  - `gsp/firmware_source.rs` (nvidia_firmware_base fallback)
  - `gsp/firmware_parser.rs` (delegated to linux_paths, removed redundant OnceLock)

### Deep Debt: ICE Consistency (11 sites)

- 11 `unreachable!()` in production codegen evolved to `ice!()`: register allocator, SM32 mem/tex encoders, SM20 integer ALU, surface addressing

### Deep Debt: `#[allow]` Reasons

- All bare `#[allow(deprecated)]` in coral-glowplug and coral-ember annotated with `reason = "..."`

### Sprint 6: Ecosystem Wave Sync — Phase D Markers, FECS Stability (May 12, 2026)

- **FECS stability**: `falcon_boot()` now returns `Err` on timeout/halt (was silently `Ok`)
- **Phase D markers**: Updated `context.rs`, `discovery.rs`, `coral-driver/lib.rs`, `qmd/mod.rs` — toadStool Phase C is COMPLETE (S245-S250)
- **IPC method name**: Aligned to `compute.dispatch.execute` (upstream contract)
- **Ember/glowplug**: Deprecation language updated from "until Phase C" to "Phase C COMPLETE — removal gated on Phase D"
- **coral-driver**: Added Phase D status module doc — hardware modules remain for backward compatibility

## Quality Gates

- `cargo clippy --all-features -- -D warnings`: **0 warnings**
- `cargo test --all-features`: **4790 passed, 0 failed, 181 ignored**
- `cargo fmt -- --check`: **clean**

## Coordination

### Pass 12 Status (coralReef items)

| Item | Audit description | Status |
|------|-------------------|--------|
| `bind_stat` timeout | Cold-path timeout handling for shader compilation | **RESOLVED** — compile deadline on all IPC handlers |
| FECS/GPCCS cold silicon init | Firmware command sequencing for sovereign GPU init | **RESOLVED** — PIO falcon boot wired in VoltaBoot + BlackwellBoot cold_init |
| `naga::Module` direct ingest | Accept naga IR without WGSL text round-trip | **RESOLVED** — `compile_module` + `compile_module_full` public API |

### Downstream Impact

- **hotSpring**: Titan V (SM70) cold VFIO path now attempts FECS/GPCCS PIO boot — unblocks sovereign GPU validation
- **barraCuda/springs**: `naga::Module` direct ingest available for in-process callers bypassing text round-trip
- **Composition graphs**: Compile deadline prevents IPC server stall on pathological inputs

### Remaining (Pass 14 / convergence)

- `toadstool.validate` wiring (toadStool upstream)
- `barracuda.precision.route` (barraCuda upstream)
- Songbird `capability.resolve` (Songbird upstream)

---

*Supersedes: CORALREEF_SPRINT4_PTX_SM120_SUBGROUP_SCANS_MAY12_2026.md (archived)*
