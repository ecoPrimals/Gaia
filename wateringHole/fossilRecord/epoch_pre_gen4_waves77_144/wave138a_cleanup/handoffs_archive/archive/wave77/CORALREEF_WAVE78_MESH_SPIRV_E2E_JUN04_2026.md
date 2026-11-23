<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# coralReef — Wave 78: Mesh Propagation & SPIR-V End-to-End

**Gate**: strandGate  
**Date**: June 4, 2026  
**Type**: Forward evolution / verification  

---

## Summary

Verified mesh capability propagation for `shader.compile` and added a
full SPIR-V end-to-end integration test proving the compile → provenance
→ output → re-validation pipeline. Import hygiene cleanup.

## Changes

### Mesh Capability Propagation (verified)

- `mesh_registration_payload_is_songbird_compatible`: validates that the
  `capability.register` JSON-RPC payload serializes correctly with all
  required fields (`name`, `version`, `provides`, `requires`, `transports`)
  and that `shader.compile` capability includes SPIR-V metadata
- `discovery_peers_response_matches_shader_compile_schema`: verifies the
  schema peers receive includes correct `output_formats`, `spirv_output`
  configuration, and provenance flag
- Confirms Songbird can pick up and propagate our capabilities

### SPIR-V End-to-End Pipeline Test

`test_spirv_end_to_end_compile_provenance_output`:
1. Compiles non-trivial WGSL (compute shader with storage buffer ops)
2. Verifies native binary produced (non-empty, status=success)
3. Verifies SPIR-V binary emitted (word-aligned, correct magic, v1.5)
4. Attaches provenance (SHA-256 hash, gate identity, compiler version)
5. Re-parses emitted SPIR-V through naga frontend
6. Re-validates through naga validator (full validation + all capabilities)
7. Asserts compute entry point preserved

Added `spv-in` feature to naga dev-dependency for roundtrip validation.

### Hygiene

- Removed 7 unused imports from `service/tests.rs`
- Removed 2 unused imports from `service/tests_serde.rs`

## Metrics

- **3307 tests**, 0 failures
- **0 clippy warnings** (pedantic + nursery)
- **0 unsafe blocks** in production
- All 57 test suites passing

## Remaining Gaps (upstream)

| Gap | Owner | Status |
|-----|-------|--------|
| GAP-HS-124: IR-to-SPIR-V emitter (beyond naga wrapper) | coralReef | Future — naga backend sufficient |
| SM120 hardware validation | biomeGate | Blocked on hardware recovery |
| `capability.call` cross-gate live test | Songbird + mesh | Awaiting eastGate rebuild |

## Upstream Asks

None. Wire protocol and capability metadata unchanged.

---

*Filed by strandGate coralReef team, Wave 78.*
