<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Node Atomic Capability AAR

**Date**: Aug 9, 2026  
**Wave**: 157d  
**From**: coralReef code team (strandGate)  
**For**: overwatch (eastGate), barraCuda team, toadStool team

---

## PURPOSE

Honest assessment of remaining Node Atomic integration capabilities.
Identifies what coralReef delivers, what the trio partners still need to wire
on their end, and what coralReef work remains.

Overwatch should blurb barraCuda and toadStool with their action items.

---

## NODE ATOMIC ROLES

| Primal | Role | Analogy |
|--------|------|---------|
| **coralReef** | HOW — GPU compiler | WGSL/SPIR-V/GLSL → native binary |
| **toadStool** | WHERE — hardware dispatch | Device abstraction, WASM, platform |
| **barraCuda** | WHAT — math/physics compute | Workload orchestration, dispatch routing |

---

## coralReef DELIVERS (LIVE IPC surface — 18 methods)

### Compilation API (consumed by barraCuda + toadStool)

| Method | Status | Wire Contract |
|--------|--------|---------------|
| `shader.compile.wgsl` | **LIVE** | WGSL source → `CompileResponse` with `binary_b64`, `target`, `shader_info` (GPR count, shared mem, barrier count, wave size, local memory), `compile_time_ms`, `dispatch_hints` |
| `shader.compile.spirv` | **LIVE** | SPIR-V bytecode → same response |
| `shader.compile.wgsl.multi` | **LIVE** | Single WGSL → multiple targets simultaneously |
| `shader.compile.multi` | **LIVE** | Batch compile across targets |
| `shader.compile.gemm` | **LIVE** (scaffold) | Tensor-core GEMM kernel for SM80+ (f16, f16→f32, TF32). Correct opcodes, scaffold kernel. |
| `shader.compile.status` | **LIVE** | Compiler health + supported arch list |
| `shader.compile.capabilities` | **LIVE** | Structured capability report (archs, f64, math ops, subgroup features) |

### Precision Routing (consumed by barraCuda)

`CompileOptions` includes `Fp64Strategy` — barraCuda passes this via IPC params:

| Strategy | Behavior | Use case |
|----------|----------|----------|
| `Native` (default) | Hardware f64 + software transcendentals | HPC GPUs (A100, MI250, Titan V) |
| `DoubleFloat` | df64 pair arithmetic on f32 cores | Consumer GPUs (RTX 3090, 4070) |
| `F32Only` | No f64, compile error on f64 ops | Pure f32 workloads |

**This was listed as "PrecisionRoutingAdvice" in WHATS_NEXT — it's already delivered.**

### Compute Trio Wire Contract (consumed by toadStool for dispatch)

Every `CompileResponse` includes:

```
{
  "binary_b64": "<base64 native binary>",
  "target": "nvidia_sm86",
  "format": "cubin",
  "size": 8192,
  "shader_info": {
    "gpr_count": 32,
    "shared_mem_bytes": 0,
    "barrier_count": 0,
    "wave_size": 32,
    "local_memory": 0,
    "workgroup_size": [64, 1, 1]
  },
  "compile_time_ms": 42.0,
  "dispatch_hints": {
    "unit": "tensor_core"  // or "alu", "tex", etc.
  }
}
```

toadStool uses `shader_info` to configure QMD/PM4 dispatch descriptors.
barraCuda uses `dispatch_hints` for routing decisions.

---

## WHAT barraCuda NEEDS TO DO (their side)

These items are listed as open in coralReef's WHATS_NEXT but the work is
**barraCuda-side** — coralReef's IPC is live and tested.

### 1. `CoralReefDevice` wiring

barraCuda has a `CoralReefDevice` stub that needs to call `shader.compile.wgsl`
via JSON-RPC or tarpc instead of importing coralReef crates directly.

**coralReef provides**: Live IPC on Unix socket + TCP. Capability discovery
via `shader.compile.capabilities`. The `primal-rpc-client` crate exists as
a reference (used internally by coralReef's own tests).

**barraCuda action**: Wire `CoralReefDevice::compile()` to call
`shader.compile.wgsl` via IPC. Use `primal-rpc-client` or direct JSON-RPC.

### 2. SovereignCompiler routing

barraCuda currently calls PTXAS/NAK for some compilation paths. These should
route through coralReef's `shader.compile.wgsl` instead.

**coralReef provides**: All 46 WGSL compute ops, f64 transcendentals on
NVIDIA (SM70-SM120) + AMD (RDNA2+), 3 input languages (WGSL primary,
SPIR-V, GLSL 450).

**barraCuda action**: Replace direct PTXAS/NAK calls with
`shader.compile.wgsl` IPC calls. coralReef handles arch detection,
optimization, and binary emission.

### 3. Tensor dispatch integration

barraCuda's `ComputeDispatch` (92 WGSL ops unified, P0 shipped) routes to
`shader.compile.gemm` for tensor-core workloads.

**coralReef provides**: `shader.compile.gemm` with `dispatch_hints.unit = "tensor_core"`.
**Limitation**: Emitted kernel is single-tile scaffold (see below).
**barraCuda action**: Wire tensor dispatch router to `shader.compile.gemm`.
Accept that GEMM is scaffold until Phase 1 tiling ships.

---

## WHAT toadStool NEEDS TO DO (their side)

### 1. `silicon_capability_registry` absorption

The strandGate silicon fold AAR says toadStool absorbs the
`silicon_capability_registry` — hardware feature detection for the fleet.

**coralReef provides**: `shader.compile.capabilities` returns supported
architectures, f64 modes, math ops, and subgroup features.
toadStool can query this at startup to build a hardware↔compiler
capability matrix.

**toadStool action**: Query `shader.compile.capabilities` during Node Atomic
initialization. Use response to populate silicon capability registry.

### 2. Dispatch descriptor wiring

toadStool uses `shader_info` from `CompileResponse` to configure QMD (NVIDIA)
or PM4 (AMD) dispatch descriptors: GPR count, shared memory, barrier count,
workgroup size, wave size.

**coralReef provides**: All fields in `shader_info`. Tested via Compute Trio
wire contract tests.
**toadStool status**: Already consuming this — no new work unless fields change.

---

## REMAINING coralReef WORK (our side)

| Item | Priority | Effort | Blocks |
|------|----------|--------|--------|
| **GEMM tiling Phase 1** | P2 | 2-3 weeks | Functional tensor-core GEMM for barraCuda |
| **Vertex/Fragment shaders** | P3 | 8-12 weeks | Graphics pipeline (esotericWebb, petalTongue) |
| **Coverage push 84→90%** | P3 | Ongoing | Quality |
| **SM80+ `OpRedux` scheduler fix** | P3 | 1-2 days | Integer subgroup reduce on SM73+ via hardware `redux.sync` (workaround: SM70 shfl path works) |

### GEMM Tiling Phase 1 — Details

`compile_gemm()` emits correct `mma.sync.aligned` PTX for SM80+ but the
kernel has no thread indexing. Phase 1 adds:

1. `%tid` / `%ctaid` block/warp mapping
2. `.reqntid` from computed thread count
3. Strided global loads with correct A/B/C addressing
4. Shared-memory tile buffers + `ldmatrix`
5. `bar.sync` between pipeline stages
6. M/N output-tile loops

After Phase 1, `shader.compile.gemm` produces functional dense GEMM kernels
that barraCuda's tensor dispatch can use for real workloads.

---

## COMPUTE GOSSIP (swarmVine integration — deferred)

The blurb notes toadStool/coralReef → compute gossip via swarmVine.
swarmVine Windows port is pending (handoff filed). Integration deferred
until swarmVine Phase 3.

**coralReef readiness**: `primal.announce` already includes cost_hints and
latency_estimates for compute capability advertising.

---

## METRICS

| Metric | Value |
|--------|-------|
| coralReef tests | 3,702 (3,698 pass, 4 ignored) |
| IPC methods served | 18/18 verified (registry-vs-dispatch self-audit) |
| Compute Trio wire contract | LIVE + tested |
| Precision routing (`Fp64Strategy`) | LIVE (Native / DoubleFloat / F32Only) |
| Cross-arch targets | NVIDIA SM70-SM120 + AMD RDNA2+ |
| P0s | 0 |

---

## ACTION SUMMARY

| Team | Action | Effort |
|------|--------|--------|
| **barraCuda** | Wire `CoralReefDevice` stub → `shader.compile.wgsl` IPC | Days |
| **barraCuda** | Route PTXAS/NAK calls → coralReef IPC | Days |
| **barraCuda** | Wire tensor dispatch → `shader.compile.gemm` | Hours |
| **toadStool** | Query `shader.compile.capabilities` for silicon registry | Hours |
| **toadStool** | Absorb `silicon_capability_registry` from silicon fold | Days-weeks |
| **coralReef** | GEMM tiling Phase 1 (thread mapping, shared mem, ldmatrix) | 2-3 weeks |
| **coralReef** | Vertex/Fragment shader compilation | 8-12 weeks |

---

*Wave 157d — Node Atomic capability AAR. coralReef's IPC obligations are
largely complete: 18 methods live, Compute Trio wire contract tested,
precision routing delivered as `Fp64Strategy`. Remaining trio integration
is barraCuda-side wiring (IPC stub, PTXAS routing) and toadStool-side
silicon registry absorption. coralReef's remaining work: GEMM tiling Phase 1
(2-3 weeks) and Vertex/Fragment shaders (8-12 weeks). 3,702 tests.*
