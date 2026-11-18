# barraCuda — Wave 157a Deep Debt + ComputeDispatch + G68 (strandGate)

**Date**: Aug 7, 2026
**Gate**: strandGate
**Team**: Compute Trio — barraCuda
**Wave**: 157a

---

## Summary

Six commits this wave:
1. Error constructor helper migration Phase 3 + magic number centralization +
   protocol negotiation zero-alloc + G68 Platform Substrate audit (20 files).
2. Deprecated batch unwiring + pool2d dedup + env var centralization (9 files).
3. **ComputeDispatch P0 migration** — all 92 `*_wgsl.rs` ops migrated from manual
   BGL→pipeline boilerplate to `ComputeDispatch` builder (92 files, −10,771 LOC).
4. **ComputeDispatch P1 migration** — all 225 remaining non-WGSL ops migrated
   (301 files, −26,373 LOC). Combined P0+P1: 317 ops, −37,144 LOC.
5. **G68 Platform Substrate compliance** — `platform_substrate` module added,
   raw `std::os::unix::fs::symlink` → `platform_link()`. 0 L2 violations.
6. Doc updates — WHATS_NEXT trimmed, test counts updated, handoff refreshed.
7. **Vertebrate self-audit** (Wave 157a, Aug 9) — 3-way RPC surface cross-reference
   (`REGISTERED_METHODS` ↔ `capability_registry.toml` ↔ dispatch arms). 2 gaps
   fixed (`method.describe`, `stats.eigh` alias). Zero phantom APIs. 2 new tests.
8. **Silicon Fold absorption** (Wave 157d, Aug 9) — 5 new device abstractions from
   strandGate Silicon Fold AAR: `NegotiatedLimits` (buffer negotiation),
   `SiliconRouter` trait (cache/vendor-aware routing), `TileDecomposer` (N-D
   cache-aligned decomposition), `RiverScheduler` (bandwidth scheduling),
   `VideoCodec` trait + `device.video_codecs` IPC (101 methods). Release profile
   added (`lto + strip`). +1,769 LOC across 4 new files + 14 modified.

Total: 323+ files changed. 5,031 tests pass. Zero clippy warnings.
G68 compliant. 15/15 cross-arch. Zero files over 800 lines.

9. **Pattern Abstraction evolution** (Wave 157d, Aug 9) — 3 "by design" patterns
   abstracted: DF64 source centralized (21 `include_str!` deduped), deprecated
   batch functions moved to `#[cfg(test)]`, `env_with_deprecated_fallback()` helper,
   `CachedPipeline` abstraction (4 bio ops migrated).
10. **Node Atomic Trio wiring** (Wave 157d, Aug 9) — Compiler-aware coralReef
    routing: `compiler_prefers_coral()` detects NAK/PTXAS/RADV codegen defects,
    `should_bypass_local_compiler()` bridges workaround detection to compilation
    path selection. `shader.compile.gemm` IPC client for tensor-core MMA kernels.
    Registry cleanup (spirv added, dead module removed).
11. **Deep debt evolution** (Wave 157d, Aug 9) — 17 GPU dispatch `.expect()`
    evolved to `?`/`Result` (bio 14, MD 2, RK45 1). `method_descriptor()` 512L
    match decomposed into 10 per-namespace helpers. 3 `#[allow]` → `#[expect]`.
    5 AKIDA env vars centralized. Zero production panics.
12. **Sovereign GEMM executor bridge** (Wave 157e, Aug 10) —
    `SovereignDevice::compile_gemm(m, n, k, precision)` → `GLOBAL_CORAL.compile_gemm()`
    IPC with binary caching. `dispatch_gemm()` combines compilation +
    `submit_dispatch()` with `HardwareHint::TensorCore`. Completes
    `KernelRouter::Sovereign` → `shader.compile.gemm` → dispatch pipeline.
13. **Gossip injection points** (Wave 157e, Aug 10) — 20 events documented in
    `capability_registry.toml` across 6 categories (device lifecycle, shader
    compilation, health state, capacity/load, precision routing, systemic errors).
14. **Gossip client wired** (Wave 157g, Aug 10) — Fire-and-forget `gossip.inject`
    client in `barracuda-core/src/ipc/gossip.rs`. 5 public injection helpers:
    `inject_device_created`, `inject_device_lost`, `inject_endpoint_alive`,
    `inject_readiness_changed`, `inject_capacity`. Wired at primal `start()`.
    Socket discovery: `SWARMVINE_SOCKET` → `$XDG_RUNTIME_DIR/biomeos/swarmvine.sock`.
    7 new tests (5,038 total). G72 Tier 1 audit: already clean (zero pollster,
    tokio trimmed, all deps active, wgpu 28 canonical, deny.toml enforced).

## Changes

### Error Constructor Migration (Phase 3)

Remaining verbose `BarracudaError` struct literal patterns → helper calls:

| Pattern | Files | Helper |
|---------|-------|--------|
| `InvalidOperation { op, reason }` | `snn.rs`, `esn_v2/model.rs`, `esn_v2/multi_head.rs`, `ops/mha/mod.rs` | `invalid_op()` |
| `InvalidInput { message }` | `cpu_executor/storage.rs`, `npu_executor.rs` | `invalid_input()` |
| `Device("...".into())` | `sovereign_device.rs`, `sovereign_dispatch_wire.rs`, `fhe_poly_add.rs`, `complex/div.rs` | `device()` |
| `Gpu("...".to_string())` | `gpu_executor/storage.rs`, `interpolate/cubic_spline.rs` | `gpu()` |
| `DeviceLost("...".into())` | `bipartition_encode.rs`, `vpc_simulate.rs`, `foce_gradient.rs` | `device_lost()` |

### New Error Helper: `device_ctx()`

Added `BarracudaError::device_ctx(context, err)` — mirrors existing `gpu_ctx()` for
the `Device` variant. Used in `sovereign_dispatch_wire.rs` for TCP connect wrapping.

### `gpu_ctx()` Bulk Migration

Migrated 40 `Gpu(format!("ctx: {e}"))` patterns in `dispatch/domain_ops.rs` to
`gpu_ctx("ctx", e)`. Eliminates per-call `format!` allocation when wrapping errors.

### Magic Number Centralization

| Constant | Value | File |
|----------|-------|------|
| `SOFTPLUS_UPPER_THRESHOLD` | `20.0` | `activations.rs` |
| `DEFAULT_FITTS_HICK_B` | `0.155` | `ipc/methods/math.rs` |

### Protocol Negotiation Zero-Alloc

Replaced `name.trim().to_ascii_lowercase().as_str()` (allocates `String` per connection)
with `trimmed.eq_ignore_ascii_case()` in `IpcProtocol::from_negotiation_name()`.

### G68 Platform Substrate Audit

barraCuda confirmed **CLEAN** for G68:
- All `#[cfg(unix)]` is in the transport layer (legacy symlinks, systemd notify, UDS)
- G66 provides `platform_default()` / `from_env_or_default()` for agnostic transport
- No L1 symlinks outside transport, no L2 permissions, no L3 raw device APIs
- Verdict: legitimate platform gating, not silicon deism

### ComputeDispatch P0 Migration (Commit 3)

All 92 `*_wgsl.rs` ops migrated from manual BGL→pipeline→encoder→submit
boilerplate to `ComputeDispatch::new().shader().storage_read().storage_rw()
.uniform().dispatch_1d().submit()` builder pattern:

- 12 simple unary math (sin, cos, tan, exp, sqrt, log, abs, sign, trunc,
  floor, ceil, round)
- 34 activation/special ops (bessels, erf, gamma, trig inverses, etc.)
- 16 parameterized ops (pow, clamp, pool1d, cumsum, norm, etc.)
- 16 multi-constructor ops (pad variants, interpolate, PRNG, polynomials)
- 14 complex multi-binding ops (gather, sparse_matvec, rnn_cell, trace)

All ops now use `create_uniform_buffer()` for shader parameter structs
(correct UNIFORM usage instead of STORAGE from `create_buffer_f32_init`).

92 files changed, −10,771 LOC net.

9. **Fmt cleanup + deep debt verification** (Wave 157d, Aug 9) — 142-file `cargo fmt`
   correction (−177 net). `sourdough validate ecobin` PASS. coralReef IPC wire
   verified complete.
10. **Pattern abstraction evolution** (Wave 157d, Aug 9) — Three "by design" items
    evolved into proper abstractions:
    - `DF64_CORE`/`DF64_TRANSCENDENTALS` centralized (21 `include_str!` dupes removed),
      `df64_source()`/`df64_f64_source()` helpers.
    - 10 `_batch()` functions → `#[cfg(test)]` (zero production callers).
      `env_with_deprecated_fallback()` replaces 3 BEARDOG fallback chains.
    - `CachedPipeline` + `BindingKind` abstraction: 4 bio ops migrated,
      6 ad-hoc `snp.rs` helpers deleted.

Total: 500+ files changed. 5,025 tests pass. Zero clippy warnings.
G68 compliant. 15/15 cross-arch. Zero files over 800 lines.

## Quality Gates

- `cargo clippy --workspace`: 0 warnings
- `cargo fmt --check`: CLEAN
- `cargo test --workspace`: 5,025 passed, 0 failed, 191 ignored
- `sourdough validate ecobin`: PASS (advisory: no `[[bin]]` section)
- Files >800L: 0 (max 783L, test file)
- Production `unwrap()`: 0
- Production `unsafe`: 0 (all crates `#![forbid(unsafe_code)]`)
- `todo!/unimplemented!/FIXME/HACK`: 0
- Hardcoded primal names: 0
- `Result<T, String>`: 0
- `println!` in lib: 0
- `#[deprecated]`: 3 (env key migration shims only)
- G68 platform substrate: **COMPLIANT** (0 L2 violations)
- Cross-arch: **15/15 PASS** (Linux + Windows)

## Remaining Structural Debt

| Item | Scope | Priority |
|------|-------|----------|
| ~~Non-WGSL ComputeDispatch~~ | ~~225 ops~~ **DONE** — 317 total ops migrated, −37,144 LOC | ~~P1~~ COMPLETE |
| ~~DF64 source duplication~~ | **DONE** — centralized in `shaders/mod.rs`, 21 `include_str!` removed | ~~P2~~ COMPLETE |
| ~~Deprecated batch functions~~ | **DONE** — 10 moved to `#[cfg(test)]`, re-exports removed | ~~P3~~ COMPLETE |
| ~~BEARDOG env aliases~~ | **DONE** — `env_with_deprecated_fallback()` helper, 3 sites unified | ~~P3~~ COMPLETE |
| ~~CachedPipeline pattern~~ | **DONE** — 4 bio ops migrated, 6 ad-hoc helpers deleted | ~~P2~~ COMPLETE |
| 1 cached BGL op | `gemm_f64.rs` `GemmCached` — intentional perf struct (weight-matrix caching) | N/A (by design) |
| CPU executor `shader_unary/binary` | Migration scaffolding exists, not yet called | P2 |
| ~~`KernelRouter::Sovereign` executor~~ | **DONE** — `compile_gemm` + `dispatch_gemm` bridge wired (Wave 157e) | ~~P2~~ COMPLETE |
| 5 `LazyLock<String>` | DF64 `df64_source()` caching — irreducible (caches runtime concat) | N/A (by design) |

## Wave 157g — Full Gossip Enmeshment (Aug 11, 2026)

Runtime gossip injection wired across all critical code paths.
`barracuda/src/gossip.rs` (13 runtime APIs) + `barracuda-core/src/ipc/gossip.rs`
(6 startup APIs). 19 events fire at device-lost, OOM, compilation, precision
routing, quota exceeded, dispatch stall, and migration exhaustion sites. All
fire-and-forget via swarmVine UDS. 16 new tests (5,054 total). All gates green.

### Doc Refresh (Aug 11, 2026)

Root docs updated to reflect 5,054 test count and Wave 157g state:
`README.md`, `CONTEXT.md`, `STATUS.md`, `PURE_RUST_EVOLUTION.md`,
`sporeprint/validation-summary.md`. CONTEXT.md IPC method table updated
to 26 domains (was missing `method.*`, `protocols.*`, `mesh.*`,
`device.video_codecs`, `compute.dispatch.*`, `ml.mlp_infer/save/load`,
`linalg.batched_tridiag_eigh`). Zero debris, zero stale TODOs,
zero archive candidates — codebase clean.

## Wave 157i — Edge Gossip + Systemic Error Detection (Aug 12, 2026)

3 remaining edge gossip events wired, completing 22/22 spec'd events:
`compute.device.recovered` (device recreation), `compute.precision.tier_degraded`
(f64 probe failure + DF64 naga poisoning + IPC tier degradation),
`compute.error.systemic` (centralized post-dispatch classifier for non-retriable
errors at IPC boundary). Also fixed `inject_compile_success` type mismatch
(u64→impl Display) and partial move in sovereign_device live_compile.
3 new tests (5,057 total). All gates green.
