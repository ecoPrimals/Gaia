<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Wave 125: shader.compile.multi — Mixed-Input Batch Compilation

**Date**: June 23, 2026
**Primal**: coralReef
**Tests**: 3631 passing, 0 failed
**Coverage**: 84% line
**Quality**: fmt ✅, clippy (pedantic+nursery) ✅, doc ✅, test ✅

---

## Summary

Implemented `shader.compile.multi` JSON-RPC method: mixed-input batch
compilation accepting WGSL, SPIR-V (base64), and GLSL jobs in a single
RPC call. Each job carries its own input type, source, target arch,
and optimization settings. Failures per-job; does not abort the batch.

Also verified SM120 Blackwell codegen — 17 dedicated tests confirm
proper `.target sm_120` PTX emission via sovereign PTX emitter. No
fallback to SM70.

## Changes

### New IPC Method: `shader.compile.multi`

**Semantic name**: `{domain}.{operation}` — `shader.compile.multi`

**Wire types**:

| Type | Purpose |
|------|---------|
| `BatchCompileRequest` | Array of `BatchCompileJob` items |
| `BatchCompileJob` | `input_type` (wgsl/spirv/glsl), `source`, `arch`, `opt_level`, `fp64_software`, `fma_policy`, `label` |
| `BatchCompileJobResult` | `index`, `label`, `binary_b64`, `size`, `arch`, `input_type`, `error`, `shader_info`, `compile_time_ms` |
| `BatchCompileResponse` | `results[]`, `success_count`, `total_count` |

**Transport**: JSON-RPC 2.0 + tarpc (bincode)

**Key design decisions**:
- Per-job independence: each job has its own `input_type` and `arch` (unlike `wgsl.multi` which shares source)
- SPIR-V input is base64-encoded string in the `source` field
- Caller-provided `label` echoed in response for job correlation
- Case-insensitive `input_type` matching
- Unsupported input types return per-job error, not request-level error

### Tests Added (17 new)

**Handler tests** (12):
- Single WGSL, single GLSL
- Mixed WGSL+GLSL batch
- Cross-vendor (sm_80 + rdna2)
- Partial failure (valid + unsupported arch)
- Unsupported input type (hlsl)
- Empty jobs rejected
- Labels echoed back
- Index order preserved
- Serde roundtrip
- FMA policy forwarded
- Case-insensitive input_type

**Dispatch tests** (5):
- WGSL job via JSON-RPC dispatch
- GLSL job via JSON-RPC dispatch
- Mixed jobs via JSON-RPC dispatch
- Empty jobs rejected at dispatch
- Invalid params type rejected

### SM120 Verification

17 existing SM120/Blackwell tests confirmed passing:
- PTX emission with `.target sm_120`
- GEMM tensor-core kernel generation
- f64 transcendental lowering (RCP, sqrt Newton-Raphson)
- Instruction latency tables
- Multi-backend determinism

## Upstream Impact

New capability exposed: `shader.compile.multi` added to:
- `SERVED_METHODS` config
- `genomebin/manifest.toml` provided methods
- `capability.rs` self-description (already advertised)
- JSON-RPC dispatch table
- tarpc service trait and implementation

No breaking changes. Existing methods unchanged.

## For Overwatch

- All quality gates green: fmt, clippy (pedantic+nursery -D warnings), test (3631), doc
- `shader.compile.multi` now matches advertised capability
- SM120 codegen confirmed functional (PTX path, no SM70 fallback)
- Zero TODO/FIXME in committed `.rs` code
- Zero unsafe in workspace
