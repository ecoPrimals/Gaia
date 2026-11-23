<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Sprint 4: PTX SM120 Evolution + Coverage Push

**Date**: May 12, 2026
**From**: coralReef
**Context**: Compute Trio Evolution Sprint 4 — Phase C Execution + Convergence

---

## Summary

PTX emitter evolved for SM120/Blackwell readiness: subgroup inclusive/exclusive prefix scans implemented via `shfl.sync.up` butterfly accumulation, silent statement catch-all replaced with explicit error reporting, and expression evaluator extended for subgroup operation results. `coral-reef-isa` API expanded with `IsaTarget` methods and `Hash` derive. Coverage pushed to 4784 tests (+19). Comprehensive deep debt pass: 6 hardcoded sysfs/procfs paths evolved to `linux_paths` helpers with env var overrides. All root docs synchronized to Sprint 4 state.

## Changes

### PTX Emitter — Subgroup Scans (`statements.rs`)

- **Inclusive scan**: 5-iteration `shfl.sync.up.b32` butterfly with predicated accumulation
- **Exclusive scan**: Same as inclusive + lane shift via `selp` with type-appropriate identity element
- Supports all naga `SubgroupOperation` variants: Add, Mul, Min, Max, And, Or, Xor
- Identity elements: 0 (add/or/xor), 1 (mul), all-ones (and), +/-inf (min/max float), INT_MAX/INT_MIN (min/max int)

### PTX Emitter — Silent Catch-All Eliminated (`statements.rs`)

- `_ => Ok(())` replaced with exhaustive match
- `ImageStore`, `ImageAtomic`, `Call`, `RayQuery`, `WorkGroupUniformLoad` now return `CompileError::NotImplemented`
- Prevents silent code generation bugs when new naga statement types are added

### PTX Expression Evaluator (`expr_eval.rs`)

- `SubgroupOperationResult`: Pre-allocates typed register matching the result scalar type
- `SubgroupBallotResult`: Pre-allocates u32 register for ballot mask

### coral-reef-isa (`lib.rs`, `latency.rs`, `sph.rs`)

- `IsaTarget`: Added `Hash` derive, `ALL` constant, `sm_version()`, `has_independent_thread_scheduling()`, `has_uniform_datapath()`
- Latency and SPH test coverage expanded (edge cases, max values, format validation)

### Deep Debt — Hardcoded Path Evolution

- 6 hardcoded `/sys/` and `/proc/` paths in `coral-gpu/pcie.rs`, `nvidia_drm.rs`, `vfio_compute/pri.rs`, `mmu_oracle/capture.rs`, `intel/ioctl.rs`, `bin/coral_probe.rs` evolved to `sysfs_root()`/`proc_root()`/`dri_render_prefix()` helpers
- `dri_render_prefix()` promoted to `pub(crate)` for cross-module reuse
- All `#[allow]` attributes given reason strings

### Documentation Synchronization

- Batch update across all root docs: README, STATUS, CHANGELOG, CONTEXT, EVOLUTION, WHATS_NEXT, START_HERE, CONTRIBUTING, ABSORPTION, specs, genomebin/manifest.toml
- Test count 4765 → 4784 everywhere; EVOLUTION.md expression/statement checklists updated for Sprint 4 PTX work
- STATUS Sovereignty row updated (all 9 non-driver crates `#![forbid(unsafe_code)]`, sysfs helpers)
- CONTEXT 800/1000 LOC inconsistency resolved

## Quality Gates

- `cargo clippy --all-features -- -D warnings`: **0 warnings**
- `cargo test --all-features`: **4784 passed, 0 failed, 181 ignored**
- `cargo fmt -- --check`: **clean**

## Coordination

### QMD Split Boundary (Phase C)

Already documented in `coral-driver/src/nv/qmd/mod.rs` header:
- **toadStool absorbs**: QMD encoding (bitfield packing, version dispatch)
- **coralReef provides**: Values via `CompilationInfo` (gpr_count, shared_mem_bytes, barrier_count, local_size, local_mem_bytes)

### Remaining (blocked on hardware or external)

- **PTX texture/surface instructions**: Requires naga `Image`/`Sampler` compute support; medium-term
- **UVM hardware validation**: Code-complete for RTX 5060, needs on-site hardware
- **Falcon boot FBP=0**: Three parallel paths active (system-memory WPR, hybrid WPR, Nouveau warm handoff)
- **Phase C/D IPC cutover**: Waiting on toadStool Phase C completion

### Downstream

- ludoSpring GAP-01 (sovereign compile) and hotSpring cold-boot path both reference "SM rebuild" — the compiler pipeline is operational; these unblock when the full E2E dispatch path is wired (Phase D)

---

*Supersedes: CORALREEF_SPRINT3_CLEANUP_ICE_CONSISTENCY_MAY12_2026.md (archived)*
