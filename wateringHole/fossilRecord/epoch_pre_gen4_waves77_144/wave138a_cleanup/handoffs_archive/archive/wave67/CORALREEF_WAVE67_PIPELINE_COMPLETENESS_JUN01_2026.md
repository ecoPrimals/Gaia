# Handoff: coralReef Wave 67 — Pipeline Completeness

**Date**: June 1, 2026
**From**: strandGate (coralReef team)
**To**: hotSpring/biomeGate team, primalSpring coordination
**Wave**: 67 (Glacial Cutover — pipeline gap closure)

---

## Summary

Closed compilation pipeline gaps identified during Wave 67 cross-gate compute
dispatch wiring. hotSpring's `validate_sovereign_compile` and trio pipeline
scenarios now have a compiler backend covering all WGSL math builtins used in
physics workloads, plus the full hyperbolic and float decomposition families.

---

## What Was Done

| Item | Detail |
|------|--------|
| **Hyperbolic trig** | `sinh`, `cosh` via PTX `ex2.approx` (exp ± exp) |
| **Inverse hyperbolic** | `asinh`, `acosh`, `atanh` via log identities (`lg2.approx` + algebraic) |
| **Float decomposition** | `modf` (trunc + sub), `frexp` (lg2 + normalize), `ldexp` (ex2 scale) |
| **Bit scan** | `firstTrailingBit` (brev.b32 + clz.b32), `firstLeadingBit` (clz.b32 + sub) |
| **`/tmp` elimination** | Last `std::env::temp_dir()` in dead debug path replaced with `XDG_RUNTIME_DIR` / `/run/biomeos` |
| **Capabilities report** | `shader.compile.capabilities` `math_ops` updated: 25 → 34 |

---

## Pipeline Gap Analysis (Pre-Fix)

hotSpring's compute trio pipeline exercises `shader.compile.wgsl` with physics
shaders (nuclear, lattice QCD, MD). While current shaders compiled cleanly,
the following WGSL builtins would have returned `NotImplemented` if encountered:

- `sinh`, `cosh` — thermal physics, Boltzmann distributions
- `asinh`, `acosh`, `atanh` — coordinate transforms, Lorentz boosts
- `modf`, `frexp`, `ldexp` — precision control in numerical algorithms
- `firstTrailingBit`, `firstLeadingBit` — bit manipulation in packing/hashing

These are now fully implemented with PTX lowering.

---

## Remaining NotImplemented (Defensive)

Items still behind `NotImplemented` that are unlikely to appear in compute
shader physics pipelines:

| Category | Functions | Risk |
|----------|-----------|------|
| Matrix ops | `Transpose`, `Determinant`, `Inverse` | Low — naga decomposes these for compute |
| Refraction | `Refract` | Zero — graphics only |
| Outer product | `Outer` | Low — naga decomposes |
| Packed dots | `Dot4I8Packed`, `Dot4U8Packed` | Low — ML inference only |
| Data packing | `Pack/Unpack*` variants | Low — used in graphics format conversion |
| Quantize | `QuantizeToF16` | Low — ML inference |

If hotSpring encounters any of these in future shaders, they can be
implemented on demand with known PTX mappings.

---

## Wire Alignment Verified

| Field | coralReef Serves | hotSpring Expects | Status |
|-------|-----------------|-------------------|--------|
| Request: `wgsl_source` | `#[serde(alias = "source")]` | `{ "wgsl_source": ... }` | ✅ |
| Response: `binary_b64` | `#[serde(rename = "binary_b64")]` | `.get("binary_b64").or(.get("binary"))` | ✅ |
| Response: `shader_info` | `#[serde(rename = "shader_info")]` | `.get("shader_info")` | ✅ |
| `shader_info.gprs` | `#[serde(rename = "gprs")]` | `.gprs` | ✅ |
| `shader_info.shared_memory` | `#[serde(rename = "shared_memory")]` | `.shared_memory` | ✅ |
| `shader_info.barriers` | `#[serde(rename = "barriers")]` | `.barriers` | ✅ |
| `shader_info.workgroup` | `#[serde(rename = "workgroup")]` | `.workgroup` | ✅ |
| `shader_info.wave_size` | direct | `.wave_size` | ✅ |
| `shader_info.local_memory` | direct | `.local_memory` | ✅ |

Cross-gate dispatch (`capability.call` → Songbird → strandGate coralReef)
wire format fully aligned.

---

## Metrics

- **Tests**: 3242 (up from 3234)
- **Clippy**: zero warnings
- **Unsafe**: zero (`#![forbid(unsafe_code)]` on all crates)
- **`/tmp` writes**: zero
- **File sizes**: `math.rs` 803 LOC, `math_ext.rs` 896 LOC (under 1000)

---

## Cross-References

- hotSpring AAR: `handoffs/hotSpring/AAR_STRANDGATE_WAVE67_GLACIAL_CUTOVER_JUN01_2026.md`
- hotSpring PRIMAL_GAPS: GAP-HS-098 (Compute Trio Pipeline Rewire — RESOLVED)
- primalSpring: `graphs/spring_validation/compute_trio_smoke.toml`
- Previous: `CORALREEF_WAVE67_GATE_READINESS_ACK_JUN01_2026.md`
