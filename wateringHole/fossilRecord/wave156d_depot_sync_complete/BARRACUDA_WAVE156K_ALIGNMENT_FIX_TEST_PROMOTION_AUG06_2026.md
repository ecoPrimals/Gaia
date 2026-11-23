# barraCuda Wave 156k — GPU Buffer Alignment Fix + Test Promotion

**Date**: 2026-08-06
**Gate**: eastGate
**Primal**: barraCuda v0.4.0
**Wave**: 156k

## Summary

Root-caused 3 persistent test failures to a single deep bug in the canonical
GPU readback path. Promoted 13 tests from `#[ignore]` to active. Dead code
cleanup. Full 12-axis deep debt audit clean.

## Changes

### Critical Fix: GPU Buffer Alignment Panic

`bytemuck::cast_slice` in `map_staging_buffer` and `submit_and_map` panicked
with `TargetAlignmentGreaterAndInputNotAligned` when GPU mapped memory wasn't
aligned to `T`'s requirement. For f64 (8-byte alignment), the GPU can return
4-byte aligned memory via `get_mapped_range()`.

**Fix**: `aligned_copy_from_mapped<T>()` copies through byte slices into a
correctly-aligned `Vec<T>`, avoiding the alignment requirement entirely.

**Impact**: All f64 GPU readback operations were vulnerable. Three tests
exposed it: `test_peak_detect_edge_endpoints`, `test_symplectic_energy_conservation`,
`test_sparsity_sampler_rosenbrock`.

### 13 Tests Promoted from `#[ignore]` to Active

All 13 had a double-gating anti-pattern: `#[ignore = "requires GPU hardware"]`
AND `get_test_device_if_f64_gpu_available()` early-return. The early-return
already handles non-GPU environments. The `#[ignore]` was redundant.

Affected:
- `max_abs_diff_f64` (7 tests)
- `spin_orbit_f64` (2 tests)
- `pppm_gpu` (3 tests)
- `boltzmann_sampling_f64` (1 test)
- `three_springs` edge case (1 test — "GPU memory-intensive" was 0.26s)

### Dead Code + Idiom Evolution

- `OdeFunction` type alias removed (orphaned after `RkIntegrator` → `&impl Fn`)
- `mul_add` evolution in `rng.rs` (2 FMA precision improvements)
- Zero clippy warnings (`--workspace --all-features --all-targets`)

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests passing | 4,970 | 4,984 |
| Test failures | 3 | 0 |
| Ignored (unit/integration) | 13 | 0 |
| IPC methods | 99→100 | 100 |
| Clippy warnings | 0 | 0 |
| `#[allow]` | 0 | 0 |
| Production `unwrap()` | 0 | 0 |

## Files Changed

- `crates/barracuda/src/device/wgpu_device/buffers.rs` — alignment-safe readback
- `crates/barracuda/src/ops/max_abs_diff_f64.rs` — 7× `#[ignore]` removed
- `crates/barracuda/src/ops/grid/spin_orbit_f64_tests.rs` — 2× `#[ignore]` removed
- `crates/barracuda/src/ops/boltzmann_sampling_f64.rs` — `#[ignore]` removed
- `crates/barracuda/src/ops/md/electrostatics/pppm_gpu/mod.rs` — 3× `#[ignore]` removed
- `crates/barracuda/tests/three_springs/edge_case_tests.rs` — `#[ignore]` removed
- `crates/barracuda/src/ops/rk_stage.rs` — `OdeFunction` alias removed
- `crates/barracuda/src/ops/mod.rs` — re-export cleanup
- `crates/barracuda/src/rng.rs` — `mul_add` evolution
- 12 documentation files — metrics refresh (4,984 tests, 100 methods)

## Quality Gates

- `cargo check --workspace --all-features`: pass
- `cargo test --workspace`: 4,984 passed, 0 failed
- `cargo clippy --workspace --all-features --all-targets`: 0 warnings
- `cargo fmt --check`: no drift
