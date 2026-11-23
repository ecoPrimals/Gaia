# barraCuda — Wave 155p Deep Debt + PRNG + Shader Evolution (strandGate)

**Date**: Aug 3, 2026
**Gate**: strandGate
**Team**: Compute Trio — barraCuda
**Wave**: 155p
**Commits**: `ebbc526f` (PRNG), `0343cc7b` (shader evolution), `e0552352` (docs)

---

## Summary

PRNG YELLOW → GREEN. Two half-range bugs found and fixed via statistical
validation harness. 51 `LazyLock<String>` shader statics evolved to
`const &str` (-182 LOC). Protocol version inconsistency unified. Magic
numbers centralized. Full dependency analysis confirmed 100% RustCrypto,
no C deps. 12-axis deep debt scan confirmed clean.

---

## Bugs Fixed

### CPU `state_to_f64()` Half-Range ([0, 0.5) → [0, 1))

`rng::state_to_f64()` extracted 31 bits (`state >> 33`) but divided by
`u32::MAX` (2^32-1 = 4,294,967,295). Maximum output was ~0.5, not ~1.0.

**Impact**: `rng.uniform` IPC method returned values in [min, (min+max)/2)
instead of [min, max). All CPU consumers of `uniform_f64_sequence()` affected.

**Fix**: Changed to 53-bit extraction (`state >> 11`) divided by 2^53,
matching `LcgRng::uniform()` and lattice `lcg_uniform_f64()`.

**File**: `crates/barracuda/src/rng.rs`

### GPU `prng_xoshiro_f64.wgsl` Half-Range ([0, 0.5) → [0, 1))

`to_uniform_f64()` combined two xoshiro draws: `hi >> 6u` (26 bits) and
`lo >> 6u` (26 bits) = 52 bits total, divided by 2^53. Maximum combined
value was 2^52-1, giving max output ~0.5.

**Fix**: Changed to `hi >> 5u` (27 bits) + `lo >> 6u` (26 bits) = 53 bits,
matching 2^53 divisor. Now produces full [0, 1) range.

**File**: `crates/barracuda/src/shaders/misc/prng_xoshiro_f64.wgsl`

### Confirmed Correct (no bugs)

- **Lattice PCG** (`prng_pcg_f64.wgsl`): Uses `(v + 0.5) / 2^32` with full
  u32 range. Correct [~0, ~1).
- **xoshiro f32** (`prng_xoshiro.wgsl`): Uses IEEE 754 bit manipulation.
  Correct [0, 1).
- **xoshiro128ss f64** (`xoshiro128ss_f64.wgsl`): Uses `f64(raw) / 2^32`
  with full u32 range. Correct [0, 1).
- **CPU `LcgRng::uniform()`**: Uses 53-bit extraction. Correct [0, 1).
- **Lattice `lcg_uniform_f64()`**: Uses 53-bit extraction. Correct [0, 1).

---

## Statistical Validation Harness Added

11 new tests covering all CPU and GPU PRNG paths:

| Test | What it validates |
|------|-------------------|
| `uniform_f64_mean_variance` | U(0,1) mean ≈ 0.5, var ≈ 1/12 (100K samples) |
| `uniform_f32_mean_variance` | U(0,1) f32 mean ≈ 0.5, var ≈ 1/12 (100K samples) |
| `uniform_f64_chi_squared_bins` | 10-bin chi-squared < 30 (df=9, p<0.001) |
| `lcg_rng_mean_variance` | LcgRng struct mean ≈ 0.5, var ≈ 1/12 |
| `cpu_box_muller_gaussian_moments` | N(0,1) mean, variance, skewness, kurtosis |
| `cpu_box_muller_chi_squared` | 20-bin Gaussian chi-squared vs N(0,1) CDF |
| `multiple_seeds_independent` | 10 different seeds produce different sequences |
| `test_prng_xoshiro_statistical_validation` | GPU xoshiro mean, var, chi-squared (10K samples) |
| `test_prng_xoshiro_seed_independence` | GPU: different seeds → different output |
| `lcg_uniform_mean_variance` | Lattice LCG uniform moments |
| `lcg_gaussian_moments` | Lattice Box-Muller Gaussian moments |

---

## 12-Axis Deep Debt Audit

| Axis | Finding |
|------|---------|
| Files >800L | **0** (max 783L) |
| Production unsafe | **0** (`#![forbid(unsafe_code)]` on both crates) |
| Production unwrap | **0** in library src/ |
| todo/unimplemented | **0** |
| Bare `#[allow(` | **0** in production |
| Hardcoded primal names | **0** functional coupling |
| Production mocks | **0** |
| Cross-primal deps | **0** |
| `Result<T, String>` | **0** |
| println in lib | **0** |
| Hardcoded paths/ports | **0** debt |
| External C deps | **0** direct |

---

## Shader Static Evolution (-182 LOC)

51 `LazyLock<String>` shader statics converted to `const &str` across 18 files.
Eliminates heap allocations and `LazyLock` synchronization on the shader
compilation hot path. `format!` concatenation instances (DF64 stitching)
intentionally preserved.

Top files: `layer_norm_wgsl.rs` (8→0), `session/pipelines.rs` (6→0),
`batch_norm.rs` (5→0), `matmul.rs` (4→0), `attention/mod.rs` (4→0).

~340 remaining instances tracked for future mechanical migration.

## Magic Number Centralization

| Constant | Was | Now |
|----------|-----|-----|
| `PROTOCOL_ID` | `"json-rpc-2.0"` / `"jsonrpc-2.0"` (inconsistent) | Single constant |
| `BTSP_WIRE_VERSION` | Inline `1` in 3 locations | Single constant |
| `IPC_PROBE_TIMEOUT` | `Duration::from_secs(5)` inline | Single constant |

## Dependency Analysis

- 100% RustCrypto (chacha20poly1305, hkdf, hmac, sha2, base64ct)
- No openssl, ring, or native-tls
- blake3 `pure` feature enabled (no C SIMD)
- No build.rs in workspace
- tarpc optional (default-on for binary, opt-out for library consumers)
- `rand` 0.8/0.9 duplication from tarpc (awaiting tarpc 0.38+ for unification)

---

## Remaining PRNG Notes

- **GPU Box-Muller polyfill precision**: The AAR-identified 9.5% variance
  deficit in lattice HMC momenta is from WGSL `log`/`cos` polyfill precision,
  not PRNG range bugs. The `cpu_mom` workaround (CPU LCG + Box-Muller, GPU
  does MD) remains the certified production HMC path.
- **TMU-accelerated path**: `su3_random_momenta_tmu_f64.wgsl` uses hardware
  texture-lookup transcendentals. Needs cross-vendor validation.
- **Ziggurat alternative**: Pure WGSL Ziggurat (avoids log/cos entirely)
  tracked as P3 evolution.

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 4,970 pass |
| New PRNG tests | +11 |
| Clippy warnings | 0 |
| IPC methods | 99 |
| WGSL shaders | 859 |
| Rust source files | 1,208 |
| Max file size | 783L |
| Health | **GREEN** |
