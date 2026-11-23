# Pure Rust Sovereign Stack — Cross-Primal Guidance

**Date**: May 11, 2026 (updated — ALL 3 GPUs sovereign via warm-catch, pure Rust pipeline)
**Type**: Ecosystem Standard (Evolution)
**From**: barraCuda (Layer 1 complete) + hotSpring (hardware validation) + coralReef (warm-catch)
**To**: coralReef, toadStool, all primals
**Status**: Active — Layers 1-2 done, Layer 3 partial, **Layer 4 ALL 3 GPUs sovereign**

> **March 12 update (hotSpring hardware validation)**: Three DRM bugs fixed
> in coral-driver (`eb4b4eb`). The nouveau sovereign pipeline is now
> **proven on hardware**: VM_INIT → CHANNEL_ALLOC → VM_BIND → GEM alloc →
> upload → readback all pass on both Titan V and RTX 3090. 9/11 hardware
> tests pass. The deprecation path for naga, NVK, and wgpu is now open.
> Root cause: ioctl number off-by-two for CHANNEL_ALLOC (was calling
> GETPARAM instead). See breakthrough handoff for details.
>
> **March 12 update (barraCuda)**: Sovereign GSP Phase 2 complete. 22 chip
> firmware parsed, cross-architecture learning operational. Six wiring gaps
> remain — see `fossilRecord/SOVEREIGN_COMPUTE_TRIO_WIRING_GAPS_HANDOFF_MAR12_2026.md`.

---

## Principle

Math is universal. A shader is just math expressed in a compute language.
The execution substrate — GPU, CPU, NPU, Android ARM core, browser WASM —
is a hardware implementation detail, not a difference in universal algebra.

Three primals each solve their portion of the sovereign compute stack:

| Primal | Solves | Layer |
|--------|--------|-------|
| **barraCuda** | The math — WGSL shaders, naga IR optimisation, precision strategy | 1 |
| **coralReef** | The compiler — SPIR-V/WGSL → native GPU binary (SASS, RDNA ISA) | 2-3 |
| **toadStool** | The hardware — GPU driver, DMA, command submission, device discovery | 3-4 |

Each primal contributes its portion. Together they produce a stable,
sovereign, pure Rust compute stack where hardware is interchangeable
and the math runs forever.

---

## Current Status (March 10, 2026)

### Layer 0 — Infrastructure C Elimination: toadStool COMPLETE

**Zero sysinfo. Zero direct libc.** toadStool S137-S141 eliminated the largest C
surface in any primal by replacing `sysinfo` (15 transitive crates → libc FFI)
with `toadstool-sysmon` — pure Rust `/proc` parsing + `rustix` `statvfs`.

22+ call sites migrated across 18 files. `cargo tree --workspace | grep sysinfo`
returns nothing. Cross-compilation verified: `cargo check --target aarch64-unknown-linux-gnu`
succeeds without musl-tools or any C toolchain.

Remaining libc paths are all ecosystem transitive deps (mio, tokio, wgpu-hal) —
tracked for upstream evolution. toadStool's own code has zero C.

**Pattern**: This follows the same evolution as Ring → RustCrypto (Tower Atomic).
Where bearDog/songBird eliminated C crypto, toadStool eliminated C system monitoring.
The pattern is reusable: any crate pulling libc for `/proc` info can be replaced
with direct parsing.

**Upstream candidate**: `toadstool-sysmon` is being extracted as a standalone
crate for crates.io contribution. See `UPSTREAM_CONTRIBUTIONS.md`.

### Layer 1 — barraCuda: COMPLETE

**Zero `unsafe` blocks.** Zero application C dependencies. `GpuBackend` trait abstraction.

barraCuda achieved this by:
- Evolving SPIR-V passthrough (`unsafe`) to safe WGSL roundtrip via
  naga `wgsl-out`. The sovereign compiler (FMA fusion, dead expression
  elimination) now runs on **all backends** (Vulkan, Metal, DX12, WebGPU).
- Introducing `GpuBackend` trait (`device::backend`) — backend-agnostic compute
  interface. `ComputeDispatch<B: GpuBackend>` is generic over backend (defaults
  to `WgpuDevice`). `CoralReefDevice` scaffold behind `sovereign-dispatch` feature
  flag, ready for `coral-gpu` crate. See `SOVEREIGN_PIPELINE_TRACKER.md`.
- Deferring pipeline caching until wgpu provides a safe creation API.
- Evolving test env manipulation to pure-function testing patterns.
- Evolving all production `expect`/`unwrap` to `Result` propagation.

Transitive C boundaries (wgpu → ash → libvulkan.so, tokio → libc) are
system-level and evolve via Layers 2-4, not Layer 1.

### Layer 2 — coralReef: Phase 10+, Sovereign Compile Parity

coralReef is a sovereign Rust GPU shader compiler. NVIDIA backend (SM35–SM120)
and AMD backend (RDNA2 GFX1030) operational with E2E dispatch verified on
both AMD RX 6950 XT and NVIDIA RTX 3090 (via DRM probing).

> **April 18, 2026 update (hotSpring Exp 176)**: Full HMC pipeline (10 QCD
> shaders) compiles to native SASS on SM35 (Kepler), SM70 (Volta), SM120
> (Blackwell). f64 transcendental lowering fixed for all NVIDIA generations —
> MUFU seed + Newton-Raphson sequences now emit SM-aware ops (IAdd2/OpShl
> for SM32, IAdd3/OpShf for SM70+). QMD v5.0 implemented for Blackwell.
> `compile_ir()` Naga bypass operational. 1,314 coral-reef tests pass.

**Iteration 24 milestone — Hardware Parity & Driver Sovereignty**:
- **Multi-GPU discovery**: `enumerate_render_nodes()` scans all `/dev/dri/renderD*`
  nodes, returns `DrmDeviceInfo` per device. `GpuContext::enumerate_all()` creates
  one context per GPU. Both AMD (amdgpu) and NVIDIA (nvidia-drm, nouveau) detected.
- **Driver sovereignty**: `DriverPreference` type with sovereign default
  (`nouveau` > `amdgpu` > `nvidia-drm`). Compile everything, prefer open-source
  at runtime. Override via `CORALREEF_DRIVER_PREFERENCE` env var.
- **NVIDIA proprietary compatibility**: `NvDrmDevice` probes `nvidia-drm` DRM
  module. Compute dispatch pending UVM integration — probing works, dispatch
  returns explicit "requires UVM" errors (not silent failure).
- **toadStool discovery integration**: `coralreef-core::discovery` reads ecosystem
  capability files (`gpu.dispatch`, `gpu-*`). Falls back to direct DRM scan.
  `GpuContext::from_descriptor()` creates contexts from discovered devices.
- **Cross-vendor parity tests**: Compilation parity for SM86 vs RDNA2. Known
  RDNA2 limitations documented (global_invocation_id, VOP2 VSRC1, buffer reads).
- **Showcase**: *(fossilized)* 8 progressive demos archived — hardware dispatch
  demos moved to toadStool domain. Cross-primal compute triangle now demonstrated
  by barraCuda `showcase/02-cross-primal-compute/` and primalSpring exp050.

**Stack**: 1804 tests (0 failed, 61 ignored), 66.43% line coverage, 75.15% function coverage, 0 DEBT markers.
93 cross-spring WGSL shaders (84 compiling SM70). Three input languages
(WGSL, SPIR-V, GLSL 450). JSON-RPC 2.0 + tarpc (bincode) IPC.
`#[deny(unsafe_code)]` on 8/9 crates. VFIO PFIFO channel + V2 MMU page tables.

### Layer 3 — Standalone Compilation: OPERATIONAL

coralReef compiles WGSL/SPIR-V/GLSL to native GPU binaries as a standalone
primal. `coralreef-core` provides JSON-RPC 2.0 + tarpc servers, capability-based
self-description (`shader.compile`, `shader.health`), and zero-knowledge startup.
UniBin CLI: `server`, `compile`, `doctor`. No dependency on toadStool or barraCuda
for compilation — they are discovered at runtime via capability files.

### Layer 4 — Sovereign Hardware: IN PROGRESS

`coral-driver` provides userspace GPU dispatch via DRM ioctl. AMD amdgpu is
fully wired (GEM, PM4, CS submit, fence sync) with E2E verified. **NVIDIA nouveau
is now hardware-validated** (`eb4b4eb`): VM_INIT, CHANNEL_ALLOC (all 5 variants),
GEM alloc, VM_BIND, upload, readback all pass on both Titan V (GV100) and RTX 3090
(GA102). Three DRM bugs were found and fixed by hotSpring hardware testing:
ioctl number off-by-two for CHANNEL_ALLOC, VA space collision with kernel-managed
region, and broken gem_info query. 9/11 hardware tests pass — remaining 2 are
QMD compute execution tuning (dispatch completes without error, kernel output
needs field alignment). NVIDIA `nvidia-drm` has UVM infrastructure (Iter 36).
All drivers compile by default, selected at runtime via `DriverPreference`.

**Sovereign GSP** (March 12): `coral-driver::gsp` provides a learned GPU
initialization system that parses firmware from 22 NVIDIA chips (Maxwell through
Ampere), builds cross-architecture register transfer maps, and produces dispatch
hints. The system identified that GV100 (Volta) can be initialized using Pascal
(gp10b) firmware patterns at 98.2% register coverage. BAR0 pre-init applicator
is operational (dry-run + verify). FECS channel submission is the remaining gap
for full Volta bring-up.

**nvPmu + hw-learn** (toadStool): BAR0 MMIO access, thermal watchdog, mmiotrace
parser, recipe distiller and store are all operational. The `RegisterAccess` trait
bridge to coral-driver is the remaining integration gap.

**Contrast vs CUDA/Kokkos**: coralReef compiles to the same SASS binary that
CUDA's `ptxas` produces (SM35–SM120), and the same GCN/RDNA binary that AMD's
ROCm compiler produces — but in pure Rust, with no vendor SDK, no C toolchain,
and no runtime library dependency. Where CUDA locks you to NVIDIA and Kokkos
abstracts over vendor SDKs (still requiring CUDA/ROCm/SYCL underneath),
coralReef generates native GPU instructions directly from Rust.

---

## Dependency Evolution Status (March 14, 2026)

### ring Removal
| Primal | Status | Notes |
|--------|--------|-------|
| biomeOS | REMOVED from production | ureq default-features=false, Songbird delegation |
| Songbird | EVOLVED — rustls-rustcrypto default | ring still transitive via quinn (QUIC) |
| BearDog | USES ring via rustls/quinn | BearDog is the crypto provider; ring here is acceptable |
| rhizoCrypt | FEATURE-GATED | Only via http-clients feature (not default) |
| loamSpine | FEATURE-GATED | Only via discovery-http feature (not default) |
| sweetGrass | DEV-DEPS ONLY | testcontainers → ring (not in production) |
| Squirrel | NEEDS EVOLUTION | sqlx → rustls → ring |

### sled → redb Evolution
| Primal | Status | Notes |
|--------|--------|-------|
| rhizoCrypt | DONE | redb default since v0.12 |
| LoamSpine | DONE | redb default, sled optional (sled-storage feature) |
| sweetGrass | DONE | redb default, sled **eliminated** (crate archived, zero lockfile entries) |
| biomeOS | DONE | biomeos-graph migrated to redb |
| Songbird | PENDING | sled in orchestrator, tor-protocol, sovereign-onion |
| BearDog | PENDING | sled in workspace |

### NestGate Unsafe Evolution
- 6 unsafe blocks replaced with safe alternatives (zero_cost_evolution, safe_ring_buffer, async_optimization)
- 8 unsafe blocks kept with SAFETY justification (lock-free data structures, FFI, SIMD)
- pin-project adopted for safe async pin projection

### Production Mock Isolation
- rhizoCrypt mocks behind `#[cfg(test)]` / testing feature
- Squirrel mocks isolated to testing modules

---

## coralReef — Layer 2 Evolution Guidance

### Eliminating the 2 Remaining Unsafe Blocks

The `nak-ir-proc` derive macro generates `AsSlice<Src>` and `AsSlice<Dst>`
implementations for instruction op structs. For multi-field structs, it uses
`unsafe { std::slice::from_raw_parts }` on `#[repr(C)]` fields after
compile-time contiguity proofs via `offset_of!`.

**Recommended safe evolution paths** (in order of preference):

#### Option A: Array-field pattern (cleanest)
Change the generated struct to store matched fields in a `[Src; N]` array
with named accessor methods. The proc macro generates:

```rust
#[repr(C)]
struct OpFoo {
    srcs: [Src; 3],  // was: src0, src1, src2
    flags: u32,
}

impl OpFoo {
    fn src0(&self) -> &Src { &self.srcs[0] }
    fn src1(&self) -> &Src { &self.srcs[1] }
    fn src2(&self) -> &Src { &self.srcs[2] }
}

impl AsSlice<Src> for OpFoo {
    fn as_slice(&self) -> &[Src] { &self.srcs }        // safe
    fn as_mut_slice(&mut self) -> &mut [Src] { &mut self.srcs }  // safe
}
```

This is the deepest evolution — it changes the struct layout but
eliminates unsafe entirely. Named accessors preserve the field-name API.

#### Option B: bytemuck safe cast
If `Src` and `Dst` implement `Pod` (or `NoUninit` + `AnyBitPattern`),
use `bytemuck` for safe reinterpretation:

```rust
// Given contiguity is proven by const assertions:
let bytes = bytemuck::bytes_of(&self.src0);  // or bytes_of_mut
// Safe cast to &[Src; N] if layout is proven
```

Requires `Src`/`Dst` to be `Pod`-compatible. Less invasive than Option A.

#### Option C: Copy-based fallback
Generate code that copies fields into a stack array:

```rust
fn as_slice(&self) -> [Src; 3] {  // returns owned array, not slice
    [self.src0, self.src1, self.src2]
}
```

Simplest but changes the return type from `&[Src]` to `[Src; N]`.
Acceptable if Src/Dst are small and Copy.

### coralReef Layer 2 — Remaining Work

| Item | Status | Notes |
|------|--------|-------|
| `nak-ir-proc` unsafe → safe | Remaining | Options A/B/C above |
| f64 transcendental codegen (DFMA sequences) | Done (Phase 10) | NVIDIA + AMD |
| SM70–SM89 instruction scheduling | Done | ISA tables complete |
| AMD RDNA2 E2E dispatch | Done | GFX1030, PM4, DRM ioctl verified |
| df64 preamble auto-prepend | Done (Iteration 13) | `Fp64Strategy::DoubleFloat` |
| IR-level df64 lowering (Phase 2) | Planned | `lower_f64_to_df64.rs` pass |
| Upstream Mesa NAK contribution | Planned | Goodwill + wider testing |

---

## coralReef — Layer 3 Evolution Guidance

Layer 3 makes coralReef a standalone Rust crate, independent of Mesa's
build system, with a clean public API.

### Target Architecture

```
barraCuda WGSL
  → naga IR (pure Rust, we use upstream or fork)
    → coralReef compile(spirv, target_arch) → native binary
      Targets:
        NVIDIA: SM35 (Kepler), SM70 (Volta), SM75 (Turing), SM80/86 (Ampere), SM89 (Ada), SM120 (Blackwell)
        AMD: GFX10 (RDNA1), GFX10.3 (RDNA2), GFX11 (RDNA3)  [future]
        Intel: Xe (DG2)  [future]
```

### Concrete Tasks

1. **Standalone crate**: `coral-reef` as a `cargo add` dependency with
   no Mesa C build system, no cmake, no meson. Pure `cargo build`.

2. **Clean public API**:
   ```rust
   pub fn compile(spirv: &[u32], target: GpuArch) -> Result<Vec<u8>, CompileError>
   pub fn compile_wgsl(wgsl: &str, target: GpuArch) -> Result<Vec<u8>, CompileError>
   ```

3. **Direct naga → coralReef path**: Accept `naga::Module` directly,
   skip SPIR-V serialization/deserialization. barraCuda's sovereign compiler
   produces naga IR — coralReef can consume it directly.

4. **Multi-vendor ISA**: Factor the backend so NVIDIA, AMD, and Intel
   targets share the common IR → scheduling → encoding pipeline.

5. **Feature-gated in barraCuda**: Optional `sovereign-compiler` feature
   flag in barraCuda's `Cargo.toml` enables in-process compilation
   (no IPC round-trip). IPC path remains the default for decoupled
   deployment.

### coralReef Layer 3 — What This Enables

- barraCuda compiles shaders to native GPU binaries without Vulkan
- Compile server: coralReef runs on a separate machine, barraCuda
  discovers it via capability scan
- CI integration: compile and cache native binaries in CI, ship
  pre-compiled shaders with the application
- Cross-compilation: compile on x86 for ARM GPU targets (Android)

---

## toadStool — Layer 3-4 Evolution Guidance

toadStool owns the hardware abstraction and runtime. Its sovereign
evolution replaces the Vulkan loader and GPU driver with pure Rust.

### Layer 3: Minimal Vulkan-compatible Dispatch

Replace `ash` (Vulkan FFI bindings) with a minimal Rust-native dispatch
layer that talks directly to the GPU driver (or coralDriver).

| Task | Description |
|------|-------------|
| Compute-only Vulkan subset | Only implement VkQueue, VkCommandBuffer, VkBuffer, VkShaderModule for compute |
| Skip validation layers | Production compute doesn't need Vulkan validation overhead |
| Feature-gate in wgpu | toadStool could provide a wgpu backend that uses coralDriver instead of Vulkan |

### Layer 4: Sovereign GPU Driver (coralDriver) — ALL 3 GPUs SOVEREIGN (May 2026)

> **May 11, 2026 update**: ALL 3 local GPUs (RTX 5060 SM120, Titan V SM70,
> Tesla K80 SM37) are now sovereign via warm-catch pipeline. VFIO dispatch
> infrastructure implemented (`VfioChannel::create_warm`). Hardware E2E tests
> exist (`vfio_warm_write_42_readback`). The dispatch *gap* is now wiring
> (shader compile → sovereign dispatch → readback on warm GPUs), not hardware
> bring-up. Pure Rust `coralctl warm-catch` CLI replaces shell scripts.

The evolution from "replace NVK/RADV" to "sovereign hardware across 3 GPU
generations" is now complete at the hardware level:

| Component | Status | Notes |
|-----------|--------|-------|
| **coralDriver** | Operational | SM35/SM70/SM120 dispatch, DRM + VFIO backends, ELF patcher |
| **coralMem** | Operational | Buffer create/map/copy across all 3 GPUs |
| **coralQueue** | Operational | GPFIFO/pushbuf submission, semaphore fence |
| **vfio backend** | Proven | RTX 5060 full dispatch, warm-catch on Titan V + K80 |
| **warm-catch** | Pure Rust | ELF patcher + ember orchestrator + `coralctl warm-catch` CLI |

### What's Sovereign vs What's Still External (May 2026)

**Sovereign (we own, pure Rust):**

| Component | Status |
|-----------|--------|
| coral-reef SASS encoders (SM35/SM70/SM120) | Operational, 1314+ tests |
| coral-reef AMD GFX10/GFX11/GFX9 encoders | Operational |
| coral-driver DRM/VFIO dispatch | Operational, hardware-proven |
| ELF patcher (kernel module binary patching) | Operational, `object` crate |
| Warm-catch pipeline (orchestrator + CLI) | Operational, pure Rust |
| AMD PM4 dispatch path | Operational |
| coral-ember lifecycle + coral-glowplug fleet | Production-grade, 664+ tests |

**Still external (not yet sovereign):**

| Dependency | Owner | Path to Sovereignty |
|------------|-------|---------------------|
| naga (WGSL parser) | Mozilla / gfx-rs | Separate coral team owns IR-to-IR stability validation loop. Local team does not own. |
| wgpu (GPU compute in barracuda/toadStool) | gfx-rs | toadStool team evolves; `sovereign-dispatch` feature bypasses wgpu. |
| PTX for SM120 (requires `ptxas`) | NVIDIA | coralReef compiler team building native SM120 SASS encoder to eliminate. |
| cudarc (optional feature) | Rust CUDA community | Removed after sovereign dispatch is default path. |
| ~~`coral-kmod` C kernel modules~~ | ~~coralReef~~ | **FOSSILIZED S276** — RM ABI absorbed into `toadstool_cylinder::nv::rm_abi` (22 repr(C) structs). C sources archived to `fossilRecord/primals/coralReef/coral-kmod/`. |

**Upstream-owned evolution (not local team responsibility):**

| Work | Owner Team |
|------|-----------|
| naga WGSL parser evolution, IR-to-IR stability | coral naga team |
| wgpu elimination from default path | toadStool team |
| coral-ember/glowplug absorption into toadStool | toadStool team |
| coral-driver hardware access absorption into toadStool | toadStool team |
| SM120 native SASS encoder (replacing PTX emitter) | coralReef compiler team |
| ~~`coral-kmod` C → Rust evolution~~ | ~~coralReef kernel team~~ | **DONE S276** — absorbed into `nv/rm_abi.rs`, fossilized |

### toadStool Layer 4 — What This Enables

- **Hardware sovereignty**: GPUs usable indefinitely, regardless of vendor
  driver support lifecycle (Titan V, older Quadros, deprecated AMD cards)
- **No C FFI in compute path**: coralDriver talks to hardware via ioctl
  or vfio-pci, both accessible from Rust
- **Potentially faster**: No Vulkan state machine overhead for compute-only
  workloads; direct dispatch from Rust futures
- **Android / embedded**: Sovereign driver runs on any Linux-based system
  including Android with vfio or kernel module

---

## Cross-Primal Evolution Cycle

```
Springs (hotSpring, wetSpring, airSpring, neuralSpring, groundSpring)
  │ find gaps, validate physics, benchmark against Kokkos/LAMMPS
  │ contribute domain-specific shaders + driver edge cases
  ▼
barraCuda (Layer 1 — DONE)
  │ WGSL shaders, naga IR optimisation, precision strategy
  │ Zero unsafe, zero C deps — the math layer is pure Rust today
  ▼
coralReef (Layers 2-3 — IN PROGRESS)
  │ SPIR-V/WGSL → native GPU binary (SASS, RDNA ISA)
  │ 9 unsafe (driver RAII + proc-macro), #[deny(unsafe_code)] on 6/8 crates
  │ Pure Rust compiler, no GPU FFI
  ▼
toadStool (Layers 3-4 — PLANNED)
  │ Hardware discovery, GPU driver, DMA, command submission
  │ Vulkan FFI → coralDriver (pure Rust)
  ▼
Springs ← absorb improved performance, validate again
```

Each primal ingests, evolves, and hands back. The physics never changes.
Only the infrastructure evolves. The cycle accelerates because every
improvement in one primal benefits all consumers.

---

## Contract Between Primals

### barraCuda guarantees to coralReef:
- WGSL shaders that parse correctly with naga
- `naga::Module` available via the sovereign compiler API for direct
  consumption (no SPIR-V serialization required)
- Precision strategy metadata (target arch, f64 rate, DF64 preference)
  available via IPC capability discovery

### coralReef guarantees to barraCuda:
- JSON-RPC 2.0 + tarpc IPC interface for shader compilation
- `compiler.compile(spirv, target_arch) → native_binary` endpoint
- Capability advertisement: `compiler.capabilities() → {architectures, features}`
- No dependency on barraCuda — coralReef is a standalone compiler

### toadStool guarantees to both:
- Hardware discovery and capability enumeration
- Device management (multi-GPU, NPU, thermal monitoring)
- Runtime transport: Unix socket, TCP, or in-process (feature-gated)
- No dependency on shader content — toadStool routes, doesn't compute

### All primals guarantee to each other:
- Primal autonomy: no shared IPC crate, no hardcoded primal names
- Capability-based discovery at runtime
- JSON-RPC 2.0 as primary protocol, tarpc (bincode) as high-performance binary channel
- AGPL-3.0 license
- Zero hardcoded ports, addresses, or primal identifiers

---

## Timeline Estimates

| Layer | Owner | Estimated Time | Risk | Depends On |
|:---:|---|---|---|---|
| 1 | barraCuda | **DONE** | — | — |
| 2 | coralReef | **DONE** — NVIDIA SM35-SM120 (Kepler→Blackwell), AMD RDNA2, 1314+ coral-reef tests, VFIO PFIFO + V2 MMU + QMD v5.0 | — | — |
| 3 | coralReef + barraCuda | **Partial** — coral-gpu API exists; `dispatch_binary` wiring needed | Low | — |
| 4 | coralReef + toadStool | **ALL 3 GPUs sovereign** — AMD done, nouveau done, warm-catch proven. Remaining: dispatch validation on warm GPUs, toadStool absorption of coral-driver hardware layer. | Low | Layer 3 |

The key accelerator: we are not writing from scratch. NAK is already Rust.
NVK has clear Rust-accessible patterns. The AI-dev loop (springs find gaps →
primals fix → springs validate) accelerates each layer.

---

## Validation Invariant

The same physics validates every layer:

| Test Suite | Validates |
|------------|-----------|
| hotSpring 9-case Yukawa OCP | Energy conservation, force accuracy |
| wetSpring 1,247 marine bio tests | Statistical correctness, FHE accuracy |
| neuralSpring 218/218 validate_all | ML op correctness, attention precision |
| groundSpring 85 delegations | Hydrology, ET₀, soil physics |
| airSpring 53 cross-spring benchmarks | Seasonal pipeline, kriging |

The physics doesn't change. The math is validated at every level.
Only the infrastructure evolves.

---

## Dual-Use Vision

The sovereign stack enables **dual-use hardware**: nvidia drivers for gaming,
VFIO for science, on the same machine, no reboot. toadStool manages the
GPU mode switch. See `SOVEREIGN_COMPUTE_EVOLUTION.md` and
`fossilRecord/SOVEREIGN_COMPUTE_BAR0_BREAKTHROUGH_DUAL_USE_HANDOFF_MAR12_2026.md`.

---

*The shaders are the mathematics. The driver is plumbing.*
*barraCuda owns the mathematics. coralReef evolves the compiler.*
*toadStool evolves the hardware. Together: sovereign compute.*
