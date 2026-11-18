# barraCuda — Wave 120 Handoff

**Date**: Jun 21, 2026  
**From**: ironGate (barraCuda)  
**Wave**: 120  

---

## Executed

### LSTM Zero-Copy Evolution
- `LstmReservoir::forward_into()` — writes output into caller-provided buffer,
  eliminating per-timestep `Vec<f64>` heap allocation
- `GateBuffers` pre-allocated scratch — eliminates 4×`Vec<f64>` gate allocations
  per layer per timestep in `lstm_gates_into()`
- `forward_core()` internal method shared by `forward_into` and `forward_sequence`
- `forward_sequence` now reuses single output buffer + gate buffers across all timesteps
- Original `forward()` preserved as convenience wrapper (allocates once)
- 1 new test (`test_lstm_forward_into_matches_forward`) verifying numerical parity

### mul_add Numerical Accuracy Evolution
- 5 manual multiply-accumulate patterns evolved to fused `mul_add`:
  - LSTM gate computation (2 sites: w*x + sum, w*h + sum)
  - Cosine similarity CPU reference (3 sites: dot, norm_a, norm_b)
  - Crank-Nicolson source contribution (1 site: dt*s + u)
- Complex64 lattice accumulations confirmed inapplicable (no f64 mul_add)

### Dependency Hygiene
- `cargo update` removes 12+ unused transitive deps (wasm-*, wit-*, prettyplease, etc.)
- `bytes` 1.11→1.12, `syn` 2.0.117→2.0.118, other patch bumps
- Zero duplicate direct deps; only `cpufeatures` 0.2/0.3 transitive (crypto crates)

### Lint Compliance Audit
- Full scan of all `#[expect()]` attributes across workspace
- 1 missing `reason` found and fixed (`spectral/stats.rs` dead_code)
- All 59+ `#[expect()]` across 4 crates now have documented `reason`

### Doc Cleanup
- 2-Gate Mesh Proof P1 item superseded — 4-node mesh now operational
  (golgi ↔ sporeGate ↔ eastGate ↔ flockGate, all 13/13 NUCLEUS)
- Zero-copy P3 item updated to reflect LSTM completion + domain_ops confirmation
- Wave 120 entries added to WHATS_NEXT, CHANGELOG, STATUS

---

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --check` | ✅ |
| `cargo clippy -D warnings` (4 crates) | ✅ |
| `cargo doc -D warnings` | ✅ |
| `cargo deny check` | ✅ |
| `cargo test` (LSTM module) | ✅ 4/4 |
| Files > 800L | 0 |

---

## Metrics

- Tests: 4,624+ (708 barracuda-core + 3,916 barracuda)
- JSON-RPC methods: 98
- MSRV: 1.92
- Zero deep debt (todo!, unimplemented!, production unwrap, hardcoded primals)

---

## Remaining (all externally blocked)

| Item | Blocker |
|------|---------|
| ironGate SSH enrollment | P0 operator (RustDesk → SSH key) |
| Multi-GPU primal startup wiring | ironGate hardware enrollment |
| DF64 NVK hardware verification | Physical GPU on ironGate |
| Tensor core GEMM codegen | coralReef cross-primal |
| Test coverage 80 → 90% | Real GPU hardware (GPU code paths untestable on llvmpipe) |
| Kokkos parity benchmarks | ironGate compute trio |
