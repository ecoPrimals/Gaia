<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# coralReef — Composition Gap 3: GPU API Alignment Resolution

**Date**: May 19, 2026
**Sprint**: 12
**Status**: RESOLVED (coralReef side) — awaiting barraCuda consumption
**Audit**: Upstream Gaps — Primal Teams (May 19, 2026)
**Gap ID**: CG-3

---

## Context

The `submit_and_map` API alignment gap between barraCuda's `TensorSession`
and coralReef's WGSL codegen output was identified as blocking the sovereign
HMMA execution path. Per barraCuda's `TENSOR_WIRE_CONTRACT.md` §Sovereign
Pipeline Status:

> The `submit_and_map` internal API is **not part of this cross-primal
> contract** — it is barraCuda's local GPU readback mechanism for
> wgpu-resident results. The sovereign path uses IPC-based readback via
> `compute.dispatch.submit` response.

The actual cross-primal gap was:
1. coralReef did not accept `precision_advice` from barraCuda's compile request
2. coralReef did not return `dispatch_hints` in compile responses for
   barraCuda to set `hardware_hint` on toadStool dispatch

---

## Resolution

### Wire Contract Changes (coralReef → barraCuda)

**`CompileWgslRequest`** — two new optional fields:

| Field | Type | Purpose |
|-------|------|---------|
| `precision_advice` | `PrecisionAdvice?` | Tier, lowering needs, domain context |
| `adapter` | `AdapterDescriptor?` | Hardware identity for arch-agnostic compilation |

**`CompileResponse`** — one new field:

| Field | Type | Purpose |
|-------|------|---------|
| `dispatch_hints` | `DispatchHints?` | `hardware_hint` + `binary_format` for dispatch routing |

### `DispatchHints` Schema

```json
{
  "hardware_hint": "tensor_core",
  "binary_format": "ptx"
}
```

Values for `hardware_hint`:
- `"compute"` — standard ALU path (default for all WGSL/SPIR-V compiles)
- `"tensor_core"` — HMMA/mma.sync path (returned for GEMM compiles and
  when `precision_advice.tier` is `F16`/`BF16`/`TF32`/`FP8*`)
- `"rt_core"` — RayQuery path (future, when RT compilation goes live)

### Routing Logic

coralReef now maps `precision_advice.tier` to dispatch hints:
- F16, BF16, TF32, FP8E4M3, FP8E5M2 → `"tensor_core"`
- All others (F32, F64, DF64, Binary, Q4, Q8) → `"compute"`
- `shader.compile.gemm` always returns `"tensor_core"` + `"ptx"`

### Backward Compatibility

- `precision_advice` and `adapter` are optional (`#[serde(default)]`)
- `dispatch_hints` is always present on new responses but gracefully
  absent on older servers (`#[serde(default)]` on barraCuda's side)
- All existing callers continue to work unchanged

---

## barraCuda Action Required

1. **Consume `dispatch_hints.hardware_hint`** in `ShaderDispatchInfo`
   construction — replace hardcoded `HardwareHint::TensorCore` inference
   with the compiler's authoritative signal.

2. **Send `precision_advice`** in `CompileWgslRequest` — barraCuda already
   has `PrecisionAdvice` in `coral_compiler/types.rs`; wire it into the
   request struct.

3. **Optional**: Send `adapter` for arch-agnostic compilation (currently
   barraCuda resolves arch locally; forwarding adapter info lets coralReef
   own the adapter→ISA mapping table).

---

## Testing

- 3181 tests passing, zero failures
- `cargo clippy --all-features -- -D warnings` clean
- tarpc binary serialization verified (removed `skip_serializing_if` from
  bincode-transported `Option` fields — incompatible with positional format)

---

## Files Changed

- `crates/coralreef-core/src/service/types.rs` — `PrecisionAdvice`,
  `AdapterDescriptor`, `DispatchHints` types; fields on request/response
- `crates/coralreef-core/src/service/compile.rs` —
  `dispatch_hint_from_precision_advice()`, `binary_format_for()`;
  all compile handlers return `dispatch_hints`
- `docs/SHADER_COMPILE_WIRE_CONTRACT.md` — updated wire contract

---

**License**: AGPL-3.0-or-later
