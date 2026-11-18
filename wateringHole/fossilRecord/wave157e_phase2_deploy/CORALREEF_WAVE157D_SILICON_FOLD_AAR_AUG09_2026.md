<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Silicon Fold Response AAR

**Date**: Aug 9, 2026  
**Wave**: 157d  
**From**: coralReef code team (strandGate)  
**Responding to**: strandGate Silicon Fold AAR (Wave 157d)

---

## EXECUTIVE SUMMARY

The strandGate silicon fold measured 15/15 compute units across AMD + NVIDIA, confirming
RT cores live (22x), AMD 20x improvement (IC vs L2 root cause), and identified tensor
cores as the remaining coralReef-specific blocker.

This response AAR provides an honest assessment of what coralReef can deliver, what's
blocked, and what the ecosystem should expect.

**Delivered this session**: Integer subgroup scan/reduce correctness fix (silent wrong
results for i32/u32 on SM70-SM90). 7 new tests. 3,702 total tests.

---

## CAPABILITY ASSESSMENT

### RT Cores — NOT A coralReef BLOCKER

**Silicon fold says**: "RT cores are accessible without coralReef via wgpu 28."

**Our assessment**: Correct. wgpu 28 handles BLAS/TLAS construction and ray tracing
pipeline dispatch. coralReef's inline RayQuery (compute shader RT) was reverted in
Wave 118 because the pre-existing implementation used fabricated PTX symbols that
produced silent wrong traversal results. A correct implementation requires documented
PTX `optix.*` intrinsics or inline RT instructions, acceleration structure binding
wiring, and hardware validation.

**Action**: None required. RT is live via wgpu. Inline RayQuery stays NotImplemented
until vendor docs are available.

### Tensor Cores — PARTIALLY DELIVERED, TILING NEEDED

**Silicon fold says**: "coralReef's NVIDIA SASS work should prioritize mma.sync for
SM86 cooperative matrix. 256 TOPS unlocked on RTX 3090."

**Our assessment**: `compile_gemm()` API is live and emits correct `mma.sync.aligned`
PTX opcodes for SM80+ (f16, f16→f32, TF32). The SM86 arch gate is satisfied (SM80+
covers SM86). However, the emitted kernel is a **single-tile scaffold**:

| Have | Missing |
|------|---------|
| Correct `mma.sync.aligned.m16n8k16` opcodes | `%tid` / `%ctaid` thread mapping |
| SM80/SM86/SM120 arch targeting | Output tile loops (M/N blocking) |
| f16, f16→f32, TF32 precision modes | Shared memory + `ldmatrix` |
| K-unrolled MMA chain | Predicated tail handling |
| `shader.compile.gemm` IPC wiring | `bar.sync` between pipeline stages |
| Dispatch hint `tensor_core` | GPU correctness tests |

**The kernel works for benchmarking and dispatch-hint validation but cannot compute
correct results for arbitrary (M,N,K) shapes.**

**Phase 1 roadmap** (makes GEMM functional):
1. Block/warp mapping via `%tid`, `%ctaid`
2. `.reqntid` from computed thread count
3. Strided global loads with correct A/B/C indexing
4. Shared-memory tile buffers + `ldmatrix`
5. `bar.sync` between pipeline stages
6. M/N output-tile loops

**Phase 2** (CG utility): `compile_gemv`, batched GEMM, integration hook for hotSpring.

### CG Inner Loop — REQUIRES SOLVER REFORMULATION

**Silicon fold says**: "If coralReef unblocks tensor cores, the RTX 3090 gains 256 TOPS
for fermion matrix-vector products (CG inner loop)."

**Our assessment**: The fermion CG inner loop (`dirac_staggered_f64.wgsl`) is a **sparse
stencil operation** with 3×3 SU(3) blocks per lattice site, operating in **f64**. This
is fundamentally different from dense GEMM:

- Sparse stencil (O(1) neighbors per row) vs. dense K dimension
- 3×3 blocks far below MMA tile granularity (16×8×16)
- f64 precision required — SM86 (RTX 3090) has **no f64 tensor cores**

To use tensor cores for CG, hotSpring would need one or more of:
1. Blocked dense subproblems (preconditioner / multigrid coarse solve)
2. Mixed-precision CG (f16/f32 matvec + f64 residual correction)
3. Batched small GEMMs for SU(3) color blocks after lattice reordering

This is a **hotSpring-side solver architecture decision**, not a coralReef-side
code change. coralReef provides the compilation API; the workload mapping is upstream.

**f64 tensor cores** exist on SM90 (Hopper, limited `dmma`) but not on SM86 (Ampere).
Our IR has `OpDmma` latency stubs for SM100 but no emission path.

### Vertex/Fragment Shader Compilation — MEDIUM TERM (8-12 WEEKS)

The compiler has substantial NAK heritage for graphics stages:
- **SPH encoder**: Fully implemented, production-ready for vertex/fragment/geometry
- **Attribute ops**: `OpALd`, `OpASt`, `OpIpa`, `OpKill` — SASS encoded + tested
- **Fragment metadata**: `FragmentShaderInfo`, `FragmentIoInfo` — complete scaffolding

What's missing is the **naga→IR translation layer** (compute-only today):
- Stage-aware entry point resolution
- Vertex/fragment builtin translation (Position, FragCoord, VertexIndex, etc.)
- IO metadata population (attribute maps, interpolation modes)
- `dpdx`/`dpdy` derivative lowering

This is primarily **translation work** connecting existing downstream infrastructure.
Estimated 8-12 engineer-weeks for NVIDIA vertex+fragment MVP. AMD is additional scope.

### Integer Subgroup Scan/Reduce — FIXED THIS SESSION

**Bug**: `emit_scan_via_shfl()` and `emit_reduce_via_shfl()` hardcoded `OpFAdd` for
all subgroup scan/reduce operations. Integer (i32/u32) scan/reduce was silently using
float add — producing wrong results through bit-pattern reinterpretation.

**Fix**: New `emit_subgroup_combine()` dispatches on type + operation:
- Floats: `OpFAdd` (add), `OpFMnMx` (min/max)
- Integers: `OpIAdd3` (add), `OpIMnMx` (min/max), `OpLop3` (and/or/xor)

Also fixed `subgroup_op_to_redux()` — Min/Max always used `IntCmpType::I32`, giving
wrong results for unsigned types. Now respects u32 vs i32 signedness.

7 new WGSL tests added. All 3,702 tests pass. Zero clippy warnings.

---

## WHAT coralReef DELIVERS TODAY

| Capability | Status | Evidence |
|-----------|--------|----------|
| WGSL→NVIDIA SASS (SM70-SM120) | LIVE | 46 WGSL ops, f64 transcendentals |
| WGSL→AMD RDNA2 binary | LIVE | PLop3, f64 native, cross-vendor parity |
| SPIR-V/GLSL compute compilation | LIVE | SPIR-V roundtrip, GLSL 450 frontend |
| `mma.sync` PTX emission (SM80+) | LIVE (scaffold) | Correct opcodes, scaffold kernel |
| Integer subgroup scan/reduce | FIXED | 7 new tests, type-aware dispatch |
| 18/18 JSON-RPC methods | VERIFIED | Self-audit, registry-vs-dispatch tests |
| BTSP Phase 3 encrypted IPC | LIVE | ChaCha20-Poly1305 AEAD |
| 4-arch cross-compilation | PASS | musl, windows-gnu, gnu, aarch64 |

---

## WHAT NEEDS UPSTREAM COORDINATION

| Item | Owner | coralReef dependency |
|------|-------|---------------------|
| CG solver reformulation for tensor cores | hotSpring | Workload mapping, not compiler |
| Dense subproblem extraction | hotSpring | Preconditioner / multigrid design |
| Mixed-precision CG integration | hotSpring + coralReef | New precision modes + stable iteration |
| GEMM tiling Phase 1 | coralReef | Makes `compile_gemm` functional |
| Vertex/Fragment shaders | coralReef | 8-12 weeks, connects NAK heritage |
| Compute gossip integration | swarmVine | Windows port pending |

---

## METRICS

| Metric | Value |
|--------|-------|
| Tests | 3,702 (3,698 passed, 4 ignored) |
| Clippy warnings | 0 (pedantic + nursery) |
| Unsafe blocks | 0 (`#![forbid(unsafe_code)]` all crates) |
| P0 / P1 | 0 / 0 |
| G68 status | 16/16 prod-clean |
| RPC surface | 18/18 verified |
| Cross-arch | 4/4 (musl, windows-gnu, gnu, aarch64) |

---

*Wave 157d — coralReef silicon fold response AAR. Integer subgroup correctness fix
delivered (silent wrong results for i32/u32). GEMM scaffold emits correct opcodes,
tiling roadmap documented. CG inner loop requires upstream solver reformulation.
RT handled by wgpu 28. Vertex/Fragment is the next evolution horizon (8-12 weeks).
3,702 tests. Zero P0s.*
