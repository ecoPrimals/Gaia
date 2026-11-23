<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Compiler Evolution (May 20, 2026)

**Sprint**: 12  
**Primal**: coralReef  
**Author**: coralReef team  
**Status**: Complete — all 3 phases shipped, tests green, clippy clean

---

## Summary

Three-phase compiler evolution proving idempotency, generalizing the target
architecture, and establishing dependency sovereignty through feature gating.

| Phase | Title | Outcome |
|-------|-------|---------|
| A | IR-to-IR Idempotency | 21 new tests proving the compiler is a pure function |
| B | `CompileTarget` Generalization | GPU/CPU/NPU type hierarchy, `execution_model` in dispatch_hints |
| C | tarpc Feature Gate | `tarpc-transport` feature (default ON), dependency sovereignty documented |

---

## Phase A: IR-to-IR Idempotency Proof

**File**: `crates/coral-reef/tests/idempotency.rs` (21 tests)

**What was proven:**

1. **WGSL roundtrip**: WGSL → naga → WGSL text → naga → compile produces
   identical binary to direct compilation (4 shader patterns)
2. **SPIR-V roundtrip determinism**: WGSL → SPIR-V → compile twice produces
   identical binary (4 shader patterns)
3. **Multi-backend determinism**: compile(x) == compile(x) for SM70, SM80,
   SM89, SM120 (NVIDIA) and RDNA2, RDNA3, RDNA4 (AMD) — 13 tests

**Significance**: Proves coralReef is a pure function of its inputs (no hidden
state, no randomness, no timestamp embedding). IR stages are
semantics-preserving transformations.

**Dep change**: `naga` dev-dependency gained `wgsl-out` + `spv-in` features.

---

## Phase B: `CompileTarget` Generalization

**File**: `crates/coral-reef/src/gpu_arch.rs`

New type hierarchy:

```
CompileTarget (non_exhaustive)
├── Gpu(GpuTarget)      — existing NVIDIA/AMD/Intel backends
├── Cpu(CpuArch)        — x86_64, aarch64 (host validation stubs)
└── Npu(NpuTarget)      — Akida, GenericDataflow (future backends)
```

Each variant exposes `execution_model()`: `"simt"` | `"sequential"` | `"dataflow"`.

**Wire contract change** (`docs/SHADER_COMPILE_WIRE_CONTRACT.md`):

- `dispatch_hints.execution_model` field added (string, optional)
- `dispatch_hints.hardware_hint` values extended: `"npu"`, `"cpu"`
- `dispatch_hints.binary_format` values extended: `"cranelift"`, `"dataflow_graph"`

All `CompileResponse` objects now include `execution_model: "simt"` for GPU targets.

**Backward compatibility**: `GpuTarget` unchanged. `NvArch.into()` still works
(now goes through `CompileTarget::from(NvArch)` → `CompileTarget::Gpu(GpuTarget::Nvidia(...))`).

---

## Phase C: tarpc Feature Gate

**Crate**: `coralreef-core`

- `tarpc` and `tokio-serde` are now `optional = true`
- Feature `tarpc-transport` (default ON) gates them
- `TarpcCompileError`, `CompileSpirvRequestTarpc`, tarpc module, tarpc tests all `cfg`-gated
- `cmd_server` has dual paths: full (with tarpc) and JSON-RPC-only (without)
- Building `--no-default-features` produces a pure JSON-RPC binary

**Sovereignty documentation** added to `STADIAL_READINESS.md`:
- `naga` documented as "external sovereign" (pure Rust, no FFI, acceptable permanent dep)
- `tarpc` feature gate rationale documented
- Disabling `tarpc-transport` eliminates: tarpc, tokio-serde, bincode 1.x, opentelemetry, duplicate rand 0.8

---

## Impact on Downstream Primals

### barraCuda
- `dispatch_hints.execution_model` now present in all `CompileResponse` — can be used for routing decisions
- No breaking changes (field is `Option<String>` with `#[serde(default)]`)

### toadStool
- `CompileTarget::Npu` / `CompileTarget::Cpu` are stubs — will return `NotImplemented` if used
- When NPU backends arrive, toadStool will receive `execution_model: "dataflow"` in hints

### primalSpring
- Test count: 3181 → 3202
- Wire contract version bump (execution_model field)
- Feature gate means `cargo build --no-default-features` is a valid minimal build

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 3181 | 3202 |
| New test file | — | `tests/idempotency.rs` |
| New types | — | `CompileTarget`, `CpuArch`, `NpuTarget` |
| Wire fields | 2 | 3 (+ `execution_model`) |
| tarpc deps | mandatory | feature-gated (default ON) |

---

## Open Items

None. All three phases complete. No deferred work.
