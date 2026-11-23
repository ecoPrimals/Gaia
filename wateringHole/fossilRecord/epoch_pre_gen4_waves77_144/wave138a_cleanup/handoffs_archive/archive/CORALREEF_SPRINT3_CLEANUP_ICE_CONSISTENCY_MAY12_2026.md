# coralReef — Sprint 3 Cleanup + ICE Consistency (May 12, 2026)

## Summary

Post-Iteration-101 work driven by the Compute Trio Evolution Sprint 3 audit
from primalSpring. Focused on vestigial pattern cleanup, RDNA2 correctness,
Phase C/D coordination markers, and final `ice!()` consistency in PTX emitter.

## Changes

### Vestigial Deprecation (Phase C coordination)
- `coral-ember/src/lib.rs`: Crate-level deprecation doc — absorbed by toadStool Phase A
- `coral-glowplug/src/lib.rs`: Crate-level deprecation doc — absorbed by toadStool Phase B
- `coral-gpu/src/context.rs`: Phase D TODO for dispatch routing to toadStool IPC
- `coralreef-core/src/discovery.rs`: Phase C/D transition marker for IPC cutover
- `coral-driver/src/nv/qmd/mod.rs`: Documented as contested module (encoding → toadStool, values → coralReef)

### RDNA2 Atomics Correctness Fix
- `codegen/ops/memory.rs`: `atom_op_to_flat` now takes `AtomType` parameter
- Unsigned `AtomOp::Min`/`Max` on `U32`/`U64` → `FLAT_ATOMIC_UMIN`/`FLAT_ATOMIC_UMAX`
- Previously incorrectly mapped to signed `FLAT_ATOMIC_SMIN`/`SMAX`

### ICE Consistency (PTX Emitter)
- `ptx_emit/math.rs`: bare `unreachable!()` → `ice!()` with invariant context
- `ptx_emit/expr_arith.rs`: 2× bare `unreachable!()` → `ice!()` with invariant context
- All production `unreachable!()` now either have explanatory strings or use `ice!()`

### Deep Debt Audit (Comprehensive — Zero Remaining)
- `Box<dyn Error>`: All in test code (trait conformance)
- `.ok()` discarding: All in `Option`-returning discovery/sysfs functions (idiomatic)
- `.unwrap()`: Zero in production library code
- `todo!()`/`unimplemented!()`: Zero in production
- Hardcoded primal names: Zero
- Production mocks: Zero (all `#[cfg(test)]`)
- External deps: 100% pure Rust
- Files >800L: All justified (generated tables, bytecode interpreter, math+tests)

## Quality Gates
- `cargo fmt --check` ✅
- `cargo clippy --all-features -- -D warnings` ✅ (zero warnings)
- `cargo test --all-features` ✅ (4765 passed, 0 failed, 181 ignored)

## Coordination Notes

### For toadStool
- `coral-ember` and `coral-glowplug` now have explicit crate-level deprecation docs
- Phase C/D markers in `coral-gpu` and `coralreef-core` reference specific toadStool IPC endpoints
- QMD module documented: toadStool absorbs encoding, coralReef provides values via `ShaderDispatchInfo`

### For barraCuda
- RDNA2 unsigned atomics fix ensures correct codegen for `atomicMin`/`atomicMax` on unsigned types
- No wire contract changes — `shader_info` response unchanged

### Status
- Zero remaining actionable deep debt in production crates
- Deprecated crates (`coral-ember`, `coral-glowplug`) in maintenance mode — bug fixes only
- Next: PTX SM120 cooperative groups, texture instructions; UVM hardware validation
