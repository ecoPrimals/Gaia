# barraCuda — Wave 155n Deep Debt Sweep (strandGate)

**Date**: Aug 3, 2026
**Gate**: strandGate
**Team**: Compute Trio — barraCuda
**Wave**: 155n
**Commit**: `d1716714`

---

## Summary

Full 12-axis deep debt sweep on strandGate. Codebase confirmed clean on all
axes. Two idiom evolution fixes applied: RK4 ODE solver zero-alloc inner loop
and MD force dead-code collapse.

---

## Work Completed

### RK4 ODE Solver — Zero-Alloc Inner Loop

`math.ode_solve_rk4` derivative evaluation closure previously cloned the bias
vector `b` on every call (4× per RK step × n_steps). Pre-allocated k1/k2/k3/k4
and y_tmp buffers once outside the loop, eliminating 7·n_steps heap allocations
per solve call.

**File**: `crates/barracuda-core/src/ipc/methods/math.rs`

### MD Force Dead-Code Collapse

4 molecular dynamics force modules had identical `Fp64Strategy` match arms —
all variants returned the same shader source. Collapsed to direct call, removed
unused `DeviceCapabilities` and `Fp64Strategy` imports.

**Files**:
- `crates/barracuda/src/ops/md/forces/harmonic_bond_f64.rs`
- `crates/barracuda/src/ops/md/forces/harmonic_angle_f64.rs`
- `crates/barracuda/src/ops/md/forces/dihedral_f64.rs`
- `crates/barracuda/src/ops/md/forces/improper_f64.rs`

Note: `lennard_jones_f64`, `morse_f64`, `born_mayer_f64` correctly use different
Hybrid paths (DF64 transcendentals) — left unchanged.

### Root Docs Updated

- README: Wave 155n entry, method count 98→99
- STATUS.md: date refresh
- CONTEXT.md: device.pool added to method table
- WHATS_NEXT.md: Wave 155n section
- capability_registry.toml: 98→99 methods
- .cursor/rules: 98→99 methods

---

## 12-Axis Deep Debt Audit

| Axis | Finding |
|------|---------|
| Files >800L | **0** (max 783L) |
| Production unsafe | **1** (barracuda-spirv passthrough) |
| Production unwrap | **0** in library src/ |
| todo/unimplemented | **0** |
| Bare `#[allow(` | **0** |
| Hardcoded primal names | **0** |
| Production mocks | **0** |
| Cross-primal deps | **0** |
| `Result<T, String>` | **0** |
| println in lib | **0** |
| Hardcoded paths/ports | **0** |
| External C deps | **1** (wgpu — required for GPU) |

---

## Evolution Opportunity Tracked

~70 `LazyLock<String>` shader statics heap-allocate `include_str!` via
`.to_string()`. Systematic evolution to `&'static str` / `Cow<'static, str>`
tracked for when the pipeline dispatch API can accept `&str` directly.

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 5,037 pass |
| Clippy warnings | 0 |
| IPC methods | 99 |
| WGSL shaders | 859 |
| Rust source files | 1,208 |
| Max file size | 783L |

---

## For Overwatch

- barraCuda codebase is at deep debt **zero** across all 12 axes.
- Only structural evolution remaining is the LazyLock<String> → &'static str
  shader source optimization (~70 sites), which requires pipeline API changes.
- Hardware validated on RTX 3090 + RX 6950 XT (strandGate dual discrete GPU).
- Ready for Node Atomic expansion to westGate or blueGate.
