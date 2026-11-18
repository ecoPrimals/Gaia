<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 120 Deep Debt Evolution Handoff

**Date**: June 21, 2026
**Wave**: 120
**Gate**: ironGate (Node Atomic — compute trio)
**Status**: READY for deployment (blocked on ironGate SSH enrollment)

---

## Changes Shipped (Wave 119–120)

### Wave 120: Full Ecosystem Name Scrub + Named Constants

#### Name Scrub (15 files, zero hardcoded primal names in any .rs file)
- All test provenance evolved from component names (hotSpring, neuralSpring, groundSpring, healthSpring, barraCuda) to capability-domain language (tensor-dispatch, neural-compute, materials-compute, health-domain, compute-pipeline)
- Test fixtures evolved: discovery data uses `compute-dispatch`, `security-provider`, `storage-provider`
- Test function names evolved: `_songbird_compatible` → `_discovery_compatible`, `_toadstool_compute_dispatch` → `_compute_dispatch_provider`
- Production doc: `sourdough_core::TransportEndpoint` → "ecosystem canonical", `primalSpring naming` → "legacy ecosystem naming"

#### Named Constants (6 files)
- `gemm.rs`: MIN_HMMA_SM, TILE_K_F16/TF32, MMA_TILE_ROWS/COLS, THREADS_PER_WARP, MAX_WORKGROUP_SIZE, GEMM_DEFAULT_GPR_COUNT
- `opt_instr_sched_common.rs`: `sched_latency` module with 11 named constants (MUFU, F64_ALU, F64_FMA, MEMORY, TENSOR_CORE, etc.)
- `shader_io.rs`: IO_SYSVALS_AB_END, IO_GENERIC_ATTR_END, IO_FF_COLOR_END, IO_SYSVALS_C_END, IO_SYSVALS_D_START/END
- `op_conv.rs`: PrmtSel::PASSTHROUGH_A / PASSTHROUGH_B

#### Manifest
- `primal.announce` added to `genomebin/manifest.toml` consumed capabilities

### Wave 119: Health Readiness + Derived Capabilities
- `health.readiness` evolved from stub to track startup state via `STARTUP_INSTANT` OnceLock
- `sm_target` derived from `NvArch::ALL.last()` instead of hardcoded `"sm_120"`
- `ecosystem.rs` refactored to directory module (343 LOC production + extracted tests)

---

## Current Metrics

| Metric | Value |
|--------|-------|
| Tests | 3577 passing, 0 failed |
| Coverage | 84% line (llvm-cov) |
| Clippy | Zero warnings (pedantic + nursery) |
| Unsafe | Zero (`#![forbid(unsafe_code)]` all crates) |
| `.unwrap()` in library | Zero |
| `todo!()`/`unimplemented!()` | Zero |
| TODO/FIXME/HACK | Zero |
| SPDX compliance | 440/440 .rs files |
| Hardcoded primal names | Zero in any .rs file |

---

## Remaining Debt (P2/P3 — not blocking deployment)

| Item | Priority | Notes |
|------|----------|-------|
| Coverage push to 90% | P2 | 84% → 90%; compiler backend paths are main gap |
| Deprecated env aliases | P2 | `BEARDOG_SOCKET`, `PRIMALSPRING_AUTH_MODE` — `#[deprecated]` with v0.3.0 removal target |
| Artifact provenance signing | P2 | `signature` field always `None` — needs runtime `crypto.sign` capability |
| Ray tracing (inline RT) | P3 | All paths return `CompileError::NotImplemented` — vendor ISA undocumented |
| Intel/CPU/NPU backends | P3 | Type stubs exist; returns `UnsupportedArch` |

---

## Upstream Dependencies

| Dependency | Status |
|------------|--------|
| ironGate SSH enrollment | P0 — operator task (RustDesk) |
| NUCLEUS deployment to ironGate | Blocked on SSH enrollment |
| Tensor-core GEMM E2E | Blocked on ironGate + barraCuda coordination |
| Sovereign CI | ✅ sporeGate builds coralReef (musl, 13/13 depot) |

---

## Commits

| SHA | Message |
|-----|---------|
| `0482097` | Wave 120: named constants — GEMM tiling, scheduling latencies, shader I/O, PrmtSel |
| `e47ffd8` | Wave 120: full ecosystem name scrub — zero hardcoded primal names in any .rs file |
| `52a2eb6` | Wave 119: deep debt — health readiness evolution, primal name scrub, derived capabilities |
| `abdd545` | Wave 119: ecosystem.rs refactor, manifest accuracy, doc alignment |
| `b020f9f` | Wave 118: deep debt evolution — primal self-knowledge, ray-query honesty |
