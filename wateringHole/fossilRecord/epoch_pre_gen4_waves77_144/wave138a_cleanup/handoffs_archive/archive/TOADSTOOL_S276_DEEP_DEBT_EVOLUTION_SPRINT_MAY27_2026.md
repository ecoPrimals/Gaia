# toadStool S276 — Deep Debt Evolution Sprint: Module Extraction + C→Rust + ABI Absorption

**Date**: May 27, 2026
**Session**: S276
**From**: toadStool team (hotSpring hardware lab)
**To**: primalSpring (downstream audit), coralReef (coral-kmod fossilized)

## Summary

Systematic deep debt reduction across the primal ecosystem. All planned items from `deep_debt_evolution_6fb63adf.plan.md` completed:

- **7 oversized files split** into focused module directories (~12,500L refactored)
- **4 userspace C tools ported** to Rust (zero C remaining in primal codebases)
- **Register constant consolidation** (`nv/registers/` — 12 domain submodules)
- **RM ABI absorption** from fossilized coral-kmod (`nv/rm_abi.rs`)
- **Production stub evolution** (NoopGspBridge, AMD feature gate)

## Module Splits

| Original file | Lines | New structure | Tests |
|----------------|-------|---------------|-------|
| `sovereign_handoff.rs` | 2,860 | `sovereign_handoff/` (11 modules) | 20/20 |
| `module_patch.rs` | 2,020 | `module_patch/` (11 modules + elf/ + patch_sets/) | 16/16 |
| `compute_device.rs` | 2,072 | `compute_device/` (11 modules, deduped gr_ungating/pbdma) | 12/12 |
| `sovereign_stages.rs` | 1,861 | `sovereign_stages/` (7 modules by stage) | pass |
| `guarded_sysfs.rs` | 1,561 | `guarded_sysfs/` (5 modules) | 15/15 |
| `channel/mod.rs` | 1,117 | Slimmed mod.rs + pfifo, mmu, devinit_ops | pass |
| `handler/sovereign.rs` | 1,004 | `handler/sovereign/` (6 modules by RPC group) | pass |

## C → Rust Port

| C file (deleted) | Rust binary | Crate |
|-------------------|------------|-------|
| `tools/rm_trigger.c` | `src/bin/rm_trigger.rs` | toadstool-cylinder |
| `sovereign_acr_boot.c` | `src/bin/sovereign_acr_boot.rs` | toadstool-cylinder |
| `sovereign_pmu_boot.c` | `src/bin/sovereign_pmu_boot.rs` | toadstool-cylinder |
| `capture_pmu_falcon.c` | `src/bin/capture_pmu_falcon.rs` | toadstool-cylinder |

Build: `cargo build -p toadstool-cylinder --bin rm_trigger` (etc.)

## New Modules

| Module | Purpose |
|--------|---------|
| `nv/registers/` | 12 submodules (pmc, pbus, pramin, ptimer, pgraph, falcon, pmu, pfb, pri, gpc, ce, usermode) — GPU-wide BAR0 register constants |
| `nv/rm_abi.rs` | Canonical NVIDIA RM ABI: 22 `#[repr(C)]` structs, ioctl escapes, class IDs (Volta→Blackwell), status codes |

## Stub Evolution

| Before | After | Change |
|--------|-------|--------|
| `StubGspBridge` | `NoopGspBridge` | Capability-guided Unsupported errors with generation-specific guidance |
| `amd_metal` (unconditional) | `#[cfg(feature = "amd")]` | Dead code gated behind feature |
| `InMemoryAuthBackend` | (unchanged) | Already correctly gated behind `#[cfg(any(test, feature = "test-mocks"))]` |

## Fossilization

- `primals/coralReef/crates/coral-kmod/` → `fossilRecord/primals/coralReef/coral-kmod/`
- Includes `FOSSILIZED.md` documenting Sprint 9 excision, ABI absorption target

## Metrics

- **705** cylinder tests pass (0 failures)
- **0** clippy warnings
- **0** userspace C files in primal codebases
- **88** JSON-RPC methods
- All public API paths preserved via `mod.rs` re-exports

## Upstream Impact

- `sovereign_handoff::*` import paths unchanged (mod.rs re-exports)
- `module_patch::*` import paths unchanged
- `compute_device::NvVfioComputeDevice` path unchanged
- `gsp_bridge::StubGspBridge` has `#[deprecated]` type alias → `NoopGspBridge`
- `amd_metal` requires `--features amd` to compile AMD boot pipeline

## Follow-up Debt

- Deduplicate RM ABI structs from `rm_trigger.rs` (local copies) into `rm_abi.rs` imports
- `sovereign_stages/mod.rs` (~846L) and `pipeline.rs` (~1,700L) remain above 800L target — future split candidates
- `pmu_investigate.rs` (1,034L) not split in this sprint — lower priority
