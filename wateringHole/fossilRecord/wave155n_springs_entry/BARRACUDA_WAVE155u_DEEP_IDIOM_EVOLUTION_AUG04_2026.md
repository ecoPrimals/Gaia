# barraCuda — Wave 155u Deep Idiom Evolution (strandGate)

**Date**: Aug 4, 2026
**Gate**: strandGate
**Team**: Compute Trio — barraCuda
**Wave**: 155u
**Commits**: `46f4f164` (shader statics Phase 2), `0fef19d5` (error constructors + env_keys)

---

## Summary

Three idiom evolutions eliminating -1,488 LOC. LazyLock<String> → const &str
Phase 2 (323 statics across 310 files). Error constructor helpers migrating
518 verbose call sites to concise helpers. Environment variable centralization
(9 keys into env_keys.rs). 12-axis deep debt scan confirmed clean. 4,970 tests
pass. Zero clippy warnings. All quality gates green.

---

## Changes

### 1. LazyLock<String> → const &str Phase 2 (-478 LOC)

Converted remaining 323 shader statics across 310 files from heap-allocating
`LazyLock<String>` to zero-cost `const &str`. Combined with Phase 1 (Wave 155p,
51 statics across 18 files), all 374 shader statics are now zero-cost.

Only 5 `LazyLock<String>` remain — all genuine DF64 `format!` concatenation
(Pattern C) requiring runtime string assembly:
- `fused_map_reduce_f64.rs` — `format!("enable f64;\n{DF64_CORE}\n{SHADER_DF64}")`
- `pipeline/reduce.rs` — `format!("{DF64_CORE}\n{SHADER_DF64}")`
- `correlation_f64_wgsl.rs` — `format!("enable f64;\n{DF64_CORE}\n...")`
- `weighted_dot_f64.rs` — `format!("enable f64;\n{DF64_CORE}\n...")`
- `variance_f64_wgsl.rs` — `format!("enable f64;\n{DF64_CORE}\n...")`

### 2. Error Constructor Helpers (-1,010 LOC)

Added 5 constructor helpers to `BarracudaError`:
- `invalid_input(msg)` — replaces `InvalidInput { message: "...".to_string() }`
- `numerical(msg)` — replaces `Numerical { message: "...".to_string() }`
- `execution(msg)` — replaces `ExecutionError { message: "...".to_string() }`
- `internal(msg)` — replaces `Internal("...".to_string())`
- `not_implemented(feature)` — replaces `NotImplemented { feature: "...".to_string() }`

518 call sites migrated across 158 files. All take `impl Into<String>`, so
both `&str` and `format!(...)` work without `.to_string()` / `.into()`.

### 3. Environment Variable Centralization

Added 9 constants to `crates/barracuda/src/env_keys.rs`:

| Constant | Source File | Was |
|----------|------------|-----|
| `BARRACUDA_GPU_ADAPTER` | `wgpu_device/creation.rs` | Local `ADAPTER_ENV_VAR` |
| `BARRACUDA_CONCURRENCY_BUDGET` | `wgpu_device/dispatch.rs` | Local `CONCURRENCY_BUDGET_ENV` |
| `BARRACUDA_MATMUL_SMALL_THRESHOLD` | `session/types.rs` | Inline string literal |
| `BARRACUDA_MATMUL_GPU_THRESHOLD` | `session/types.rs` | Inline string literal |
| `BARRACUDA_SHADER_COMPILER_ADDR` | `coral_compiler/discovery.rs` | Local `COMPILER_ADDR_ENV` |
| `BARRACUDA_SHADER_COMPILER_PORT` | `coral_compiler/discovery.rs` | Local `COMPILER_PORT_ENV` |
| `XDG_CACHE_HOME` | `autotune.rs`, `ncbi_cache.rs` | Inline string literal |
| `XDG_DATA_HOME` | `akida.rs` | Inline string literal |
| `HOME` | `autotune.rs`, `ncbi_cache.rs`, `akida.rs` | Inline string literal |

All consumer files updated to reference centralized constants.

---

## 12-Axis Deep Debt Scan

| Axis | Result |
|------|--------|
| Files >800L | **0** (max 783L, test file) |
| Production unsafe | **1** (barracuda-spirv, feature-gated) |
| Production unwrap | **0** |
| todo/unimplemented | **0** |
| Bare `#[allow(` | **0** |
| Hardcoded primal names | **0** |
| Production mocks | **0** |
| Cross-primal deps | **0** |
| `Result<T, String>` | **0** |
| println in lib | **0** |
| Hardcoded env vars | **0** (all centralized) |
| `LazyLock<String>` | **5** (all Pattern C) |

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 4,970 pass, 0 fail |
| Clippy warnings | 0 |
| Net LOC | -1,488 |
| Files changed | 511 (316 shader statics + 195 error/env) |
| IPC methods | 99 |
| Health | GREEN |

---

## Tracked P2 Evolution Opportunities

These are lower-priority evolution targets identified but not yet executed:

1. **Elementwise op pipeline migration** — 69 `*_wgsl.rs` ops still use manual
   BGL/pipeline creation. Infrastructure exists (`GLOBAL_CACHE` + `record_operation`)
   but migration scope is large.
2. **Arc<WgpuDevice> API relaxation** — Constructor signatures force redundant
   `Arc::clone()` at call sites. `fn new(device: &Arc<WgpuDevice>)` would be cleaner.
3. **Cow<'static, str> for error messages** — ~200 remaining struct literal sites
   could avoid allocation with `Cow` field types.

---

*Wave 155u. barraCuda GREEN. 13/13 primal health. -1,488 LOC via three idiom
evolutions. All quality gates green. Deep debt scan confirmed clean across all
12 axes. Upstream overwatch: no action items.*
