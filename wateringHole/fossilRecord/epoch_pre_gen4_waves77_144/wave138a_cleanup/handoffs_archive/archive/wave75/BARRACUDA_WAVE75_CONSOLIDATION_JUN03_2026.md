# barraCuda Wave 75 Consolidation — Debt Hygiene Pass

**Date**: 2026-06-03  
**Commit**: `0b76fb76`  
**Gate**: strandGate  
**Status**: Complete — 533 IPC tests passing, clippy clean

---

## What Was Done

### 1. Clippy Hygiene (barracuda-core)

All `cargo clippy -p barracuda-core --all-targets -- -D warnings` errors resolved:

| Lint | Count | Fix |
|------|-------|-----|
| `cast_lossless` (i32→f64) | 9 | `f64::from(i)` with typed ranges |
| `manual_mul_add` | 2 | `f64::from(i).mul_add(...)` |
| `len_zero` comparison | 1 | `!.is_empty()` |
| `case_sensitive_file_extension_comparisons` | 1 | `Path::extension().eq_ignore_ascii_case()` |
| `manual_is_multiple_of` | 1 | `.is_multiple_of()` |
| `unwrap_used` in integration test | 1 | `#![allow(clippy::unwrap_used)]` in test file |

### 2. Broken Test Fix (Critical)

**`btsp_is_protected` test was FAILING** since Wave 75 added `"btsp."` to `PUBLIC_METHOD_PREFIXES`. 
- Renamed to `btsp_and_mesh_are_public` with correct assertions
- Added `ml_pipeline_methods_are_protected` test verifying Dark Forest Invariant 3

### 3. P3 Model Versioning Design

Created `specs/MODEL_SERIALIZATION_DESIGN.md`:
- Recommends **bincode** format (aligned with plasmidBin precedent)
- Defines 44-byte file header with magic, version, format tag, BLAKE3 checksum
- Wire contract evolution: `"format": "bincode"` param (backward-compat default: JSON)
- BTSP Ed25519 signing slot for Phase 3+
- Implementation checklist for when promoted to P2

### 4. Production Code Status

| Area | Unwrap Sites | Status |
|------|-------------|--------|
| `ml.rs` (production paths) | 0 | Clean |
| `mesh.rs` (production paths) | 0 | Clean |
| `method_gate.rs` | 0 | Clean |
| `btsp.rs` / `btsp_negotiate.rs` / `btsp_wire.rs` | 0 | Clean |

All `unwrap_or()` / `map_or()` usage in production code has safe defaults.

---

## Pre-existing Debt (Not Addressed — Out of Scope)

- `barracuda` crate: 8 `mul_add` lints in molecular dynamics force kernels (`dihedral_f64.rs`, `harmonic_angle_f64.rs`). These are physics numerics and need careful review — not Wave 75 code.
- Full `cargo test` SIGSEGV from Mesa `llvmpipe` in GPU-dependent tests on software-only environment. Pre-existing, unrelated to ML/mesh code.

---

## Ecosystem Position

barraCuda is **Tier 1 (HOT)** per Wave 76 remaining work doc. 
Pipeline complete: `ml.mlp_train → ml.mlp_save → ml.mlp_load → ml.mlp_infer`.
Waiting on: biomeOS consumer readiness + primalSpring training data for L5 integration.
