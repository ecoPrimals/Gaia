<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 118: Deep Debt Evolution

**Date**: June 19, 2026  
**Version**: 0.2.0  
**Sprint**: 14  
**Wave**: 118  
**Tests**: 3577 passing, 0 failed  
**Coverage**: 84% line / 88% function / 85% region  
**Clippy**: Zero warnings (`clippy::pedantic` + `clippy::nursery`)  
**Unsafe**: Zero (`#![forbid(unsafe_code)]` on all 9 crate roots)

---

## Summary

Comprehensive deep debt evolution wave targeting primal self-knowledge compliance,
production mock elimination, capability-domain language, and code quality evolution.

## Changes

### Primal Self-Knowledge Compliance
- Scrubbed 14 production doc comments across 8 files of other primal names
- `barraCuda` → "caller's precision routing layer" / "compute.dispatch provider"
- `bearDog` → "crypto-domain provider"
- `toadStool` → "compute.dispatch provider"
- `Songbird` → "ecosystem's mesh discovery relay"
- `sourDough` → "ecosystem health/lifecycle patterns"
- `primalSpring` → removed from standard references
- Zero production `match` arms or routing on peer primal names

### Ray-Query Honesty (Production Mock Elimination)
- `ray_query.rs`: All 5 `RayQueryFunction` variants now return `CompileError::NotImplemented`
  instead of silently emitting wrong PTX (always-false predicates, comment-only RT instructions)
- `expr_eval.rs`: `RayQueryProceedResult` and `RayQueryGetIntersection` also return `NotImplemented`
- Removed dead `RayIntersectionRegs` struct
- Shaders using `rayQuery*` now fail at compile time with clear error rather than
  producing incorrect traversal results

### Large File Refactoring
- `btsp.rs` test extraction: 1086 → 779 LOC (tests moved to `btsp/tests/tests_btsp_session.rs`)
- All files remain under 1000 LOC limit (max: 929 — auto-generated AMD ISA)

### Code Quality
- Named constants: `NONCE_BYTES`, `MIN_CLIENT_NONCE_BYTES`, `POLY1305_TAG_BYTES`,
  `MIN_FRAME_BYTES`, `NVIDIA_DEFAULT_WARP_SIZE`
- Dead code gating: `save_graphviz()` → `#[cfg(test)]`
- Documented WGSL double-compile optimization opportunity for `emit_spirv` path

### Audit Results (All Clear)
- **Dependencies**: Pure Rust throughout. No openssl/ring/cc/cmake. `deny.toml` enforces.
  Transitive `libc` via tokio/mio documented and accepted.
- **Unsafe**: Zero in production. Only in `test_env.rs` RAII guard (integration test infra).
- **Mocks**: Zero in production. `coral-reef-stubs` is legitimate pure-Rust dependency
  replacements (not mocks). ~80 `CompileError::NotImplemented` sites are honest gaps.
- **Hardcoding**: Zero runtime routing by peer primal name. Deprecated env aliases
  (`BEARDOG_SOCKET`, `PRIMALSPRING_AUTH_MODE`) have v0.3.0 removal timeline.

## Files Modified

### coralreef-core
- `src/ipc/btsp.rs` — test extraction, LOC reduction
- `src/ipc/btsp/tests/tests_btsp_session.rs` — extracted BTSP session tests (new)
- `src/ipc/btsp_negotiate.rs` — named constants (NONCE_BYTES, etc.)
- `src/ipc/method_gate.rs` — doc scrub
- `src/ipc/transport.rs` — doc scrub
- `src/ipc/tarpc_transport.rs` — doc scrub
- `src/service/types.rs` — doc scrub (6 changes)
- `src/service/compile.rs` — named constants, double-compile doc
- `src/ecosystem.rs` — doc scrub
- `src/config.rs` — doc scrub
- `src/discovery.rs` — doc scrub
- `src/health.rs` — doc scrub
- `src/lifecycle.rs` — doc scrub
- `src/or_exit.rs` — doc scrub

### coral-reef
- `src/codegen/nv/ptx_emit/ray_query.rs` — NotImplemented evolution
- `src/codegen/nv/ptx_emit/expr_eval.rs` — NotImplemented for RT expressions
- `src/codegen/nv/ptx_emit/types.rs` — removed dead RayIntersectionRegs
- `src/codegen/nv/ptx_emit/tests_image.rs` — updated ray-query tests
- `src/codegen/opt_instr_sched_common.rs` — cfg(test) gating for save_graphviz

### Docs & Manifests
- `README.md`, `STATUS.md`, `WHATS_NEXT.md`, `EVOLUTION.md`, `ABSORPTION.md`,
  `START_HERE.md`, `sporeprint/validation-summary.md` — updated to Wave 118 / 3577 tests
- `genomebin/manifest.toml` — updated test count

## Coverage Breakdown

| Area | Line Coverage |
|------|--------------|
| coralreef-core (service/IPC/BTSP) | 85-100% |
| coral-reef (compiler pipeline) | ~75-90% (backends are main gap) |
| Workspace total | 84% line / 88% function |

**Main coverage gap**: NVIDIA SM20-SM50 encoders and AMD ISA tables — exercised via
end-to-end shader compilation but individual encoding functions are hard to unit-test
without hardware.

## Upstream Gaps for Primal Teams

1. **Deprecated env aliases** — `BEARDOG_SOCKET` and `PRIMALSPRING_AUTH_MODE` have v0.3.0
   removal timeline. Composition launchers should migrate to `BTSP_PROVIDER_SOCKET` and
   `ECOSYSTEM_AUTH_MODE`.

2. **Artifact provenance signing** — `ArtifactProvenance.signature` is always `None`.
   Needs crypto-domain provider with `crypto.sign` capability to be discoverable at runtime.

3. **Inline RT emission** — SM75+ `RayQuery` now returns `NotImplemented`. Requires vendor
   RT core ISA documentation for proper implementation. Use OptiX/Vulkan RT pipelines
   for RT workloads.

4. **WGSL double-parse** — When `emit_spirv` is true, WGSL is parsed twice. Optimization
   opportunity to share `naga::Module` between native and SPIR-V emission paths.

---

**Next wave focus**: Coverage push toward 90% (compiler backends), vertex/fragment shader
compilation, sovereign WGSL parser evolution.
