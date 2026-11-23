<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef Wave 157f — GEMM Phase 2 IPC Wiring

**Date**: 2026-08-10
**From**: coralReef @ strandGate
**To**: barraCuda, toadStool, ecosystem
**Type**: Capability delivery — P1 unblock

---

## Summary

`shader.compile.gemm` IPC now supports Phase 2 shared-memory HMMA kernels
via the new `tiling` request parameter. barraCuda's `dispatch_gemm()` is
unblocked.

## What Changed

### New `tiling` parameter on `shader.compile.gemm`

| Value | Phase | Threads/CTA | Shared Memory | Requirements |
|-------|-------|-------------|---------------|--------------|
| `"auto"` (default) | Auto-select | Depends | Depends | Selects smem when M%64==0 and N%16==0 |
| `"global"` | Phase 1 | 32 (1 warp) | None | M%16==0, N%8==0 |
| `"smem"` | Phase 2 | 128 (4 warps) | ~2.5 KB | M%64==0, N%16==0 |

Phase 2 uses `ldmatrix.sync.aligned` for warp-cooperative fragment loads and
`bar.sync` for shared-memory pipeline synchronization. Block tile: BM=64, BN=16.

### Example request (smem)

```json
{
  "jsonrpc": "2.0",
  "method": "shader.compile.gemm",
  "params": {
    "m": 256,
    "n": 128,
    "k": 64,
    "precision": "f16f32",
    "arch": "sm_80",
    "tiling": "smem"
  },
  "id": 42
}
```

### Response changes

When `tiling: "smem"` is used (or auto-selected):
- `shader_info.shared_mem_bytes` > 0 (was always 0 in Phase 1)
- `shader_info.workgroup_size` = `[128, 1, 1]` (was `[32, 1, 1]`)
- `shader_info.barriers` = 1 (was 0)

### Backward compatibility

The `tiling` field defaults to `"auto"`. Existing callers that omit it get
auto-selection behavior: Phase 2 for block-aligned dimensions, Phase 1
otherwise. No breaking changes to existing requests.

## Matrix layout contract (unchanged)

- A: row-major M×K
- B: column-major K×N
- C: row-major M×N, **output-only** (accumulators zeroed; C = A×B, not C += A×B)
- Pointer ABI: `.param .u64` — three bare pointers

## Verification

- 3,822 tests passing (6 new GEMM tiling tests)
- Zero clippy warnings (pedantic+nursery)
- Zero unsafe
- Wire contract doc (`SHADER_COMPILE_WIRE_CONTRACT.md`) updated

## What's next for GEMM

- Phase 3: GEMV/batched APIs for CG inner loop
- Phase 4: hotSpring integration for blocked Dirac tiles
- `cp.async` double-buffering (performance optimization, not blocking)
- SM90+ Hopper `wgmma` path (hardware-gated)
