# coralReef — Wave 76: SPIR-V Portable Output & Mesh Capability

**From**: strandGate (coralReef)  
**Date**: 2026-06-03  
**Commit**: `47166992`  
**Type**: Evolution handoff — SPIR-V backend advancement + mesh readiness

---

## Summary

Evolved the SPIR-V compilation path from hardcoded naga defaults to a
fully configurable backend. Cross-gate callers can now request specific
SPIR-V versions, and SPIR-V output is opt-in for efficiency.

## Changes

### 1. `SpirVOptions` struct (coral-reef crate)
- Configurable `version: (u8, u8)` — supports 1.0, 1.3, 1.5, 1.6
- `zero_init_workgroup_memory: bool` — safety default true
- `force_loop_bounding: bool` — portability safeguard
- Wired into `CompileOptions.spirv: Option<SpirVOptions>`

### 2. JSON-RPC wire protocol extension
- `CompileWgslRequest.emit_spirv: bool` — opt-in portable SPIR-V output
- `CompileWgslRequest.spirv_version: Option<[u8; 2]>` — target version
- SPIR-V emission in `handle_compile_wgsl` is now conditional (was always-on)
- Both fields use `#[serde(default)]` — backward compatible

### 3. Capability metadata evolution
- `output_formats: ["native_binary", "spirv"]` in shader.compile capability
- `spirv_output` block: versions, default, provenance flag
- Enables cross-gate discovery of SPIR-V output capability

### 4. Provenance test coverage
- `test_provenance_attached_on_with_provenance` — verifies hash, algo, version
- `test_provenance_serde_roundtrip` — JSON serialization fidelity
- `test_provenance_hash_deterministic` — same binary → same hash

### 5. SPIR-V validation test coverage
- `test_wgsl_to_spirv_naga_validates_output` — naga re-parses + validates
- `test_wgsl_to_spirv_compute_preserves_entry_point` — stage + workgroup size
- `test_wgsl_to_spirv_version_targeting` — version word verified in binary
- `test_wgsl_to_spirv_f64_arithmetic` / `atomics` / `shared_memory_barrier` / `control_flow_complex`
- `test_compile_wgsl_no_spirv_when_emit_false` — conditional emission
- `test_compile_wgsl_spirv_version_targeting` — service-level version control

### 6. Mesh capability readiness
- Songbird propagation confirmed fixed upstream (push model)
- `capability.register` sends `shader.compile` with SPIR-V output metadata
- `primal.announce` includes full `SERVED_METHODS` (16 methods)
- Cross-gate dispatch ready when Songbird `capability.call` routing is live

## Metrics
- **3301 tests**, 0 failures
- Zero clippy warnings (`pedantic` + `nursery`)
- Zero unsafe blocks
- All files under 1000 lines

## Remaining Gaps
- `GAP-HS-124` (SPIR-V from coralReef IR): naga-passthrough path fully working.
  IR-to-SPIR-V emitter (bypassing naga backend) is a future optimization target.
- Songbird `capability.call` live cross-gate test: depends on Songbird team ship.
- SM120 hardware validation: waits for biomeGate recovery.

## Upstream Asks
- **Songbird team**: Verify `shader.compile` appears in `discovery.peers` capability
  list from eastGate's perspective after propagation.
- **primalSpring**: Run `capability.call("shader.compile.wgsl", {...})` from eastGate
  when ready for live mesh testing.

---

*Filed by strandGate cascade automation*
