<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef Diesel Engine Migration Handoff — May 13, 2026

**Date**: May 13, 2026
**From**: coralReef (compiler primal)
**For**: toadStool (hardware primal), hotSpring (validation spring), barracuda (compute layer)
**Signal**: Feature freeze on diesel stack; E1/E2 upstream reference; E3 shipped.

---

## Context

hotSpring audited barracuda's compute layer and found 15+ source files wired to
coralReef's diesel engine stack (`coral-ember`, `coral-glowplug`, `coral-driver`
hardware runtime). This handoff documents what toadStool needs to replicate and
where to find the reference implementations.

## coralReef Action Items — Status

| Item | What | Status |
|------|------|--------|
| **Feature freeze** | No new features in coral-ember/coral-glowplug/coral-driver hardware paths | **DONE** — soft-deprecated since Sprint 6, feature freeze markers added Sprint 8 |
| **E1: Cylinder translation** | Document subprocess isolation pattern for toadStool reference | **DONE** — see §Reference below |
| **E2: Warm API** | Document warm handoff/capture API for toadStool reference | **DONE** — see §Reference below |
| **E3: FECS cold silicon init** | Compiler-domain work that stays in coralReef | **SHIPPED** (Sprint 7) — `boot_gr_falcons_with_recovery()`, PMC GR reset, `GrBootOutcome` |

## E1: Cylinder Subprocess Model (toadStool reference)

The "cylinder" pattern in coral-glowplug isolates per-GPU-domain work in child
processes. Key files:

| File | What it does |
|------|-------------|
| `coral-glowplug/src/sovereign.rs` | Boot orchestration: detect→warm→swap→init sequence, `BootResult`/`BootStep` structs |
| `coral-glowplug/src/socket/mod.rs` | ECU routing: dispatches JSON-RPC to per-device handlers ("diesel mode") |
| `coral-glowplug/src/observer/vfio.rs` | VFIO device observation — monitors device state during subprocess lifecycle |
| `coral-glowplug/src/device/health.rs` | Per-device health monitoring within cylinder context |

toadStool C1 should implement `toadstool-cylinder` with per-PCIe-domain process
isolation. The glowplug pattern spawns a handler per BDF that owns the device
lifecycle. ECU routing dispatches incoming RPCs to the correct cylinder by BDF.

## E2: Warm Handoff/Capture API (toadStool reference)

The warm API orchestrates cold→warm→capture→diff→save for sovereign GPU boot.
Key files:

| File | What it does |
|------|-------------|
| `coral-glowplug/src/capture.rs` | Full capture flow: cold BAR0 snapshot → swap to warm driver → settle → warm BAR0 snapshot → diff → save recipe JSON |
| `coral-ember/src/vendor_lifecycle/nvidia.rs` | NVIDIA-specific warm handoff validation (PCIe link check before vfio-pci bind) |
| `coral-driver/src/vfio/channel/hbm2_training/` | HBM2 domain capture/diff engine (register-level cold vs warm comparison) |
| `coral-driver/src/nv/vfio_compute/boot_sequence.rs` | `SovereignBootSequence` trait — `cold_init` uses `boot_gr_falcons_with_recovery()` |

toadStool C5 (warm-fecs pipeline) should reference the capture flow in
`capture.rs` and the HBM2 training diff in `hbm2_training/`. The recipe JSON
format (`TrainingRecipe` struct) is the interchange contract.

## Socket Paths (barracuda dependency)

barracuda's `fleet_client.rs` depends on coralReef socket paths. Current layout:

| Path | Resolution | Env Override |
|------|-----------|-------------|
| ember socket | `$XDG_RUNTIME_DIR/coral-ember-{family}.sock` | `$CORALREEF_EMBER_SOCKET` |
| glowplug socket | `$XDG_RUNTIME_DIR/coral-glowplug-{family}.sock` | `$CORALREEF_GLOWPLUG_SOCKET` |
| coralreef IPC | `$XDG_RUNTIME_DIR/coralreef.sock` | `$CORALREEF_SOCKET` |

toadStool should define equivalent `$TOADSTOOL_*` env vars. During transition,
barracuda can point env vars at toadStool sockets without code changes.

## What Stays in coralReef Permanently

- Compiler pipeline: `coral-reef/` (WGSL/SPIR-V/GLSL → native GPU binary)
- ISA tables, stubs, bitview: `coral-reef-isa/`, `coral-reef-stubs/`, `coral-reef-bitview/`
- `naga::Module` direct ingest: `coral-reef/src/lib.rs` (`compile_module`/`compile_module_full`)
- IPC service: `coralreef-core/` (JSON-RPC + tarpc `shader.compile.*`)
- RPC client: `primal-rpc-client/`

**Note**: Items previously listed here (`coral-gpu/`, `coral-driver/src/gsp/`,
`fecs_boot.rs`, `linux_paths.rs`) were included in the Sprint 9 excision below.
They exist only in git history. toadStool owns all hardware-facing code.

## Excision Complete (Sprint 9, May 13 2026)

The following were **deleted** from coralReef in Sprint 9:
- `coral-ember` crate (52 .rs files)
- `coral-glowplug` crate (70 .rs files)
- `coral-driver` crate (367 .rs files — entire crate, including compiler-adjacent modules)
- `coral-gpu` crate (unified compile+dispatch)
- `showcase/` directory (hardware dispatch demos)

Total: 153K lines deleted. coralReef is now a pure compiler primal with zero unsafe.
toadStool should reference this handoff for E1/E2 patterns before the code was excised.
Git history preserves the full implementation for reference (`git log --all -- crates/coral-driver/`).

## Post-Excision Capability Alignment (hotSpring audit response)

hotSpring's post-excision trio alignment (May 13, 2026) confirmed coralReef is
operational for `shader.compile.wgsl/spirv`. One gap identified and resolved:

- **Discovery filter evolved**: coralReef's ecosystem discovery now matches
  toadStool's capability names (`compute.dispatch.*`, `gpu.*`, `compute.hardware.*`)
  in addition to legacy `gpu.dispatch`. This ensures coralReef finds toadStool's
  discovery JSON when determining available GPU targets for compilation.
- **Requires declaration updated**: `gpu.dispatch` → `compute.dispatch` with
  `legacy_id` metadata for backward compatibility.
- **3117 tests passing** at time of this fix, including 2 new tests for toadStool-style discovery JSON. (Current total: 3130.)

No remaining coralReef action items from the hotSpring audit.

## Glacial Debt Escalation — H2 Resolution (primalSpring audit response)

primalSpring's "Upstream Primal Evolution — Glacial Debt Escalation" (May 13, 2026)
listed two remaining coralReef niche tasks. Both are now resolved:

### `naga::Module` direct ingest (H2) — RESOLVED

The `compile_module` / `compile_module_full` APIs now support:

1. **Entry point selection** — `CompileOptions::entry_point: Option<String>` allows
   callers to target a specific entry point by name. When `None` (default), the first
   compute-stage entry point is selected automatically. Error messages list available
   entry points on mismatch.
2. **Module validation** — `CompileOptions::validate: bool` (default `true`) runs
   `naga::valid::Validator` on the module before compilation, catching malformed IR
   with clear diagnostics before it reaches codegen. Can be disabled for trusted
   modules where validation overhead is unwanted.
3. **PTX path integration** — Entry point selection propagates through the SM100+
   PTX emit path (`emit_compute_ptx_module`).
4. **8 new tests** covering entry point selection, missing EP errors, compute-stage
   preference, validation rejection of corrupted modules, and validation bypass.

Total test count: 3129 (up from 3121).

### `bind_stat` timeout — RESOLVED (since Sprint 5)

All `shader.compile.*` methods are wrapped in `tokio::time::timeout`:
- Default: 120 seconds
- Override: `CORALREEF_COMPILE_TIMEOUT_SECS` environment variable
- Applied to both JSON-RPC and tarpc transport handlers
- Compile tasks run on `spawn_blocking` to avoid blocking the IPC reactor
- Panics in compile tasks are caught and returned as `CompileError::Internal`

No code changes needed — this was shipped in Sprint 5 and remains fully operational.

## hotSpring Compute Trio Audit — Resolution (May 13, 2026)

hotSpring audited coralReef's compile path and surfaced remaining items.
All resolved:

### PTX SM120/Blackwell texture ops — IMPLEMENTED

The PTX emitter (`codegen/nv/ptx_emit/`) now supports:
- `ImageStore` → `sust.b.{1d,2d,3d}.{format}.zero` (surface store)
- `ImageLoad` → `suld.b.{1d,2d,3d}.{format}.zero` (surface load)
- Surface binding detection from `AddressSpace::Handle` + `TypeInner::Image`
- `.surfref` declarations in PTX output
- Format classification: rgba8/rgba16/rgba32/r32

2 new tests: `ptx_image_store_2d_rgba8`, `ptx_image_load_2d_rgba32`.

### `EVOLUTION.md` narrative — WRITTEN

Sprint 9 excision narrative added. "Current Position" rewritten to reflect
pure compiler status. Historical sections (Titan V, iterations 37-80)
annotated as fossil record.

### USERD_TARGET encoding fix — toadStool domain (no coralReef action)

This is purely driver-side (PBDMA runlist DW0 bits [3:2]). Was in excised
`coral-driver`. Moves entirely with toadStool absorption. Zero compiler
component.

### HMMA codegen for tensor-core GEMM — IMPLEMENTED (May 13, 2026)

hotSpring's second Compute Trio audit listed "HMMA codegen" as the remaining
coralReef-side item. Now shipped:

- `compile_gemm()` public API: generates PTX `mma.sync.aligned` kernels for SM80+
- Precision modes: `F16` (f16→f16), `F16F32` (f16→f32 mixed-precision), `Tf32` (TF32→f32)
- MMA tile shapes: `m16n8k16` (f16/f16f32), `m16n8k8` (TF32)
- K-loop unrolling with accumulator zeroing, fragment load/store
- New types: `GemmShape`, `GemmPrecision`
- New module: `codegen/nv/ptx_emit/gemm.rs`
- 12 new tests (5 unit + 7 integration): SM80 f16f32, SM120 Blackwell, pre-SM80
  rejection, AMD rejection, misaligned K, zero dimensions, TF32 K-alignment

hotSpring's `bench_sovereign_parity` can now consume tensor-core GEMM output once
toadStool FECS context init ships.

### Deep debt cleanup — COMPLETE (May 13, 2026)

Comprehensive deep debt audit and resolution:

- **Large file refactoring**: `lib.rs` 868→630 lines (GEMM→`gemm.rs`, preamble→`preamble.rs`). `newton.rs` 849→568 lines (tests→`newton_tests.rs`). Zero production files >800 lines.
- **Hardcoded primal names eliminated**: `service/types.rs` (removed "coralDriver", "barraCuda, toadStool"), `shader_model.rs`, `func_builtins.rs`, `discovery.rs` — all genericized to capability-based references.
- **`ECOSYSTEM_AUTH_MODE`** env var added as primary for method gate enforcement; `PRIMALSPRING_AUTH_MODE` retained as legacy fallback; `CORALREEF_AUTH_MODE` is primal-specific override.
- **Verified clean**: Zero `unsafe` in production (all `#![forbid(unsafe_code)]`), zero `.unwrap()` in library code, zero `TODO`/`FIXME`/`HACK`, zero `todo!()`/`unimplemented!()`, zero C dependencies, zero production mocks. `coral-reef-stubs` confirmed as real pure-Rust implementations (not mocks).

### IPC wire-compat aliases — IMPLEMENTED (May 13, 2026)

hotSpring caught `"source"` vs `"wgsl_source"` mismatch on `shader.compile.wgsl`.
Resolved with serde aliases:

- `CompileWgslRequest::wgsl_source`: accepts `"source"` alias
- `MultiDeviceCompileRequest::wgsl_source`: accepts `"source"` alias
- `CompileResponse::binary`: serializes as `"binary_b64"`, accepts `"binary"` alias
- `CompileResponse::info`: serializes as `"shader_info"`, accepts `"info"` alias

Callers using either old or new field names will deserialize correctly.
3 new serde roundtrip tests validate both canonical and alias paths.

### Texture format coverage expanded — IMPLEMENTED (May 13, 2026)

`TexelFormat` enum expanded from 4 to 10 variants covering all practical
naga `StorageFormat` categories:

- Added: `R8`, `R16`, `Rg8`, `Rg16`, `Rg32`, `Bgra8`
- Existing: `R32`, `Rgba8`, `Rgba16`, `Rgba32`
- `emitter.rs` format classifier now explicitly handles all naga variants instead
  of silently lumping unrecognized formats into Rgba32
- 5 new texture format tests (rg32float, r32uint, rgba16float, r32float, bgra8unorm)

Remaining texture gaps: `ImageSample` (sampled textures) and `ImageQuery`
(dimension queries) are not yet in the PTX emitter.

### HMMA codegen status note — WGSL→HMMA automatic lowering

`compile_gemm()` API is the practical HMMA path. WGSL→HMMA automatic lowering
(detecting matmul patterns in arbitrary WGSL and replacing with tensor-core ops)
is not currently feasible: WGSL lacks cooperative matrix primitives, and naga
does not expose `OpCooperativeMatrixMulAdd`. Pattern detection in IR is
research-level. barraCuda's GEMM router should target `compile_gemm` directly.

### Subgroup operations — hotSpring barrier shader compilation

**RESOLVED** (May 13, 2026). WGSL subgroup ops (`subgroupAdd`, `subgroupBroadcast`,
`subgroupBallot`) now compile through `naga_translate` for SM70+ targets.

Root cause: `naga_translate/func.rs` had no handlers for naga `SubgroupBallot`,
`SubgroupCollectiveOperation`, or `SubgroupGather` statements — they fell to
the catch-all `_ => NotImplemented(Discriminant(20))`.

Fix: Added full statement handling mapping to existing coral IR ops:
- `SubgroupBallot` → `OpVote` (ballot instruction)
- `SubgroupCollectiveOperation/Reduce` → `OpRedux` (SM73+) or butterfly
  `OpShfl` chain (SM70 fallback — `redux` instruction requires SM73)
- `SubgroupCollectiveOperation/Scan` → iterated `shfl.up` with predicated
  accumulation (works on all SM70+ targets)
- `SubgroupGather` → `OpShfl` with appropriate mode (Idx/Up/Down/Bfly)

Also: `enable subgroups;` directive stripped during preprocessing (naga 28
recognizes but rejects it — subgroup builtins work without the directive).

### f64 type resolution at function call boundaries

**RESOLVED** (May 13, 2026). Math functions (`sqrt`, `pow`, `exp`) applied to
f64 return values from user-defined functions now correctly use the f64 path.

Root cause: `resolve_expr_type_handle` in `expr.rs` had no explicit handler for
`CallResult` expressions. They fell to `_ => any_type_handle()` which returned
the first type in the module arena (almost never f64). This caused `is_f64_expr`
to return `false` for f64 function results, routing them through the f32 math path.

Fix: Added `CallResult(func_handle) → module.functions[func_handle].result.ty`
resolution so the return type is correctly identified.

### Deep debt audit — all categories clear (May 13, 2026)

Full ecosystem debt sweep completed. Results:

| Category | Status |
|----------|--------|
| Files >800L (production) | 3 only — all generated ISA tables (data, not logic) |
| Unsafe code | Zero in production. `#![forbid(unsafe_code)]` all crate roots |
| External deps | All pure Rust. `libc` only transitive via Tokio/Mio |
| Mocks in production | None. `coral-reef-stubs` is complete implementations |
| Cross-primal knowledge | Deprecated with runtime warnings. No `use` imports |
| TODO/FIXME/HACK | Zero in committed `.rs` code |
| Empty/temp files | Zero |
| Commented-out code | Zero |

Legacy env vars evolved to deprecation path:
- `BEARDOG_SOCKET` → `#[deprecated]`, runtime `tracing::warn`, canonical `BTSP_PROVIDER_SOCKET`
- `PRIMALSPRING_AUTH_MODE` → runtime `tracing::warn`, canonical `ECOSYSTEM_AUTH_MODE`

### May 14, 2026 — hotSpring audit resolutions

**f64 nested struct member type error** (`deformed_wavefunction_f64.wgsl`):
RESOLVED. `is_f64_expr` for `AccessIndex`/`Access` expressions was using
`element_scalar(base)` which has no `Struct` arm — f64 struct member accesses
were misclassified as non-f64, routing through the f32 lowering path. Fix:
use `resolve_expr_type_handle(handle)` directly (same path as other expression
types). Dead `element_scalar` helper removed. Same fix applied to `is_float_expr`
and `is_signed_int_expr`. All 9/9 hotSpring barrier shaders should now compile.

**`health.version` RPC**: Implemented. Returns `{ session, build_hash, version,
name }`. Build hash injected via `CORALREEF_BUILD_HASH` env var at compile time.
Session via `CORALREEF_SESSION`. Both fall back to version/`"dev"` for local builds.

**`shader.compile.gemm` IPC wiring**: The `compile_gemm` library API is now
exposed as JSON-RPC endpoint with `GemmCompileRequest` type (`{ m, n, k,
precision, arch }`). Dispatched through blocking pool with compile timeout.

**HMMA GEMM tensor layout constraints documented**: Wire contract updated with
full constraint table (row-major A, col-major B, K alignment, precision modes,
tile shapes, pointer ABI). Ready for barraCuda integration.

### Live compile→dispatch CI test — shared toadStool Phase C blocker

Not actionable until toadStool Phase C lands. coralReef compile path is
ready (`shader.compile.*` IPC surface operational, including `shader.compile.gemm`).

Total test count: 3181 (as of Sprint 12, May 14 2026).

### Sprint 11 — hotSpring Audit Resolutions (May 14, 2026)

**`shader.compile.gemm` on tarpc transport**: The `ShaderCompileTarpc` trait now
exposes the `gemm(GemmCompileRequest)` method. tarpc consumers (bincode-over-TCP
and bincode-over-Unix-socket) can now invoke tensor-core GEMM compilation without
falling back to JSON-RPC. Includes deadline timeout and spawn-blocking panic recovery
matching all other compile endpoints.

**Subgroup multiply reduction documented**: The `subgroup_op_to_redux` function
now returns an explicit error stating "no redux hardware op (SM70-SM120)". NVIDIA's
`redux.sync` instruction supports `.add`, `.min`, `.max`, `.and`, `.or`, `.xor` but
not `.mul`. No SM generation from SM70 through SM120 provides a hardware multiply
reduction. A shfl-based emulation is theoretically possible but non-trivial for
overflow-correct integer multiply — callers should decompose manually.

**`ImageSample` PTX emission**: Tracked as next evolution focus (WHATS_NEXT). This
is the next frontier operation after `ImageQuery`/`suq` and requires `.texref`
texture descriptor + `tex.*` sampled-texture instructions.

### Sprint 12 — RayQuery PTX Emission (May 14, 2026)

**Phase B — RT core activation** is now wired. `Statement::RayQuery` compiles
for SM75+ targets with all five operations: `Initialize`, `Proceed`,
`GenerateIntersection`, `ConfirmIntersection`, `Terminate`.
`Expression::RayQueryGetIntersection` returns the full 10-field
`RayIntersection` struct (kind, t, instance data, barycentrics, front_face).

The emitted PTX uses RT comment stubs (`// rt.trace.*`) marking hardware
insertion points. toadStool's acceleration structure dispatch will activate
these paths on live hardware. The compiler wiring is complete — WGSL ray query
shaders compile end-to-end for SM75+ targets.

4 new tests: Initialize+Proceed, GetIntersection, Terminate, SM70 rejection.

### Sprint 10 — hotSpring Audit Resolutions (May 15, 2026)

**SubgroupSize/NumSubgroups builtins (naga_translate)**:
`func_builtins.rs` `resolve_builtin()` now handles `SubgroupSize` (constant 32),
`NumSubgroups` (compile-time `ceil(flat_workgroup_size / 32)`), `WorkGroupSize`
(compile-time constants), and `SubgroupId` (runtime `local_index >> 5`). Unblocks
hotSpring's `sum_reduce_subgroup_f64.wgsl` shader.

**`deformed_wavefunction_f64.wgsl` type error**: Already resolved in Sprint 9
(f64 nested struct member fix + CallResult type resolution). Test
`deformed_wavefunction_f64_sm70` passes. hotSpring failure is plasmidBin harvest
lag — once ecoBin updates, their 9/9 shader barrier will be green.

## Full-GPU Silicon Exploitation — Future Horizons (May 14, 2026)

coralReef now compiles compute shaders, tensor-core GEMM, and image/texture
operations (ImageSample, textureGather, ImageAtomic, WorkGroupUniformLoad —
Sprint 11). This engages roughly 55% of GPU silicon. The vision going forward
is **full silicon exploitation** — every hardware unit doing useful work.

### Phased Roadmap

| Phase | Silicon | What Ships | Ecosystem Impact |
|-------|---------|-----------|-----------------|
| **A (current)** | ~55% (shader + tensor + TMU) | Compute shaders, HMMA GEMM, subgroups, image ops | hotSpring QCD, barraCuda math, ludoSpring GPU physics |
| **B (near)** | ~65% (+ RT cores) | `RayQuery` in compute: Initialize/Proceed/GetIntersection | ludoSpring `game.gpu.batch_raycast`, hotSpring BVH spatial, petalTongue shadow probes |
| **C (medium)** | ~85% (+ rasterizer + ROPs) | Vertex + Fragment shader compilation: SPH, graphics builtins, derivatives, discard | Full render pipeline, petalTongue sovereign 3D, ludoSpring game visuals |
| **D (far)** | ~95% (+ mesh/task) | Mesh shaders, task shaders | AAA-equivalent rendering without vendor SDK |

### toadStool Implications

- **Phase B (RayQuery)**: toadStool dispatch surface will need to support
  acceleration structure builds and RT core invocation. coralReef will emit
  the PTX; toadStool owns the BVH construction and dispatch path.
- **Phase C (Graphics)**: toadStool will need graphics pipeline state object
  management (blend, depth, stencil, viewport) and draw command submission.
  coralReef provides compiled vertex + fragment binaries; toadStool assembles
  the pipeline and dispatches draw calls.
- **Phase D (Mesh)**: toadStool will need mesh/task dispatch infrastructure.

### barraCuda Implications

- **Phase B**: barraCuda can route spatial queries (nearest-neighbor, collision
  detection) through RT cores instead of brute-force compute kernels. The
  `game.gpu.batch_raycast` capability maps directly to this.
- **Phase C**: Not directly relevant to barraCuda's math/tensor role.

### ludoSpring / petalTongue Implications

- **Phase B**: GPU raycasting for game visibility, pathfinding, line-of-sight.
- **Phase C**: Full sovereign game rendering — the Symphony Architecture becomes
  a reality. CPU game logic orchestrates; GPU compute handles physics; GPU
  graphics handles rendering. All compiled by coralReef, dispatched by toadStool.

### The Universal Principle

Real physics simulations and videogame physics are both math dispatched to
parallel hardware. The rasterizer is a special-purpose unit that answers
"which pixels does this triangle cover?" — a pure function. There is no
fundamental difference between a lattice QCD HMC trajectory and a game
physics frame: both are parallel math with a time budget. coralReef's role
is to compile that math — all of it — to every piece of silicon available.

---

## References

| Topic | Location |
|-------|----------|
| Diesel engine audit (hotSpring) | primalSpring downstream audit, May 13 2026 |
| Post-excision trio alignment (hotSpring) | hotSpring post-excision audit, May 13 2026 |
| Phase C completion | `handoffs/ECOSYSTEM_WAVE_SYNC_MAY12_2026.md` |
| FECS stability proof | `handoffs/ECOSYSTEM_WAVE_SYNC_MAY12_2026.md` (Sprint 7) |
| Interstadial exit criteria | `INTERSTADIAL_EXIT_CRITERIA.md` v1.4 |
