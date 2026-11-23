# hotSpring ↔ Primal Deduplication Handoff

**Date**: Aug 7, 2026
**From**: strandGate (hotSpring)
**To**: overwatch → barraCuda, toadStool, biomeOS teams
**Context**: Audit of systems in hotSpring that overlap with upstream primals

---

## Status: Mid-Migration

barraCuda absorbed the *structure* of precision brain/calibration from
hotSpring v0.6.25, but hotSpring remains authoritative for **probe depth**
and spring-specific GPU/physics integration. The doc comments in hotSpring's
precision modules explicitly track this split. This handoff identifies the
next steps to complete the convergence.

---

## Priority 1: ABSORB Upstream (hotSpring → barraCuda)

These systems are MORE CAPABLE in hotSpring than their upstream counterparts
and should be pushed into barraCuda for all springs to benefit:

| System | hotSpring LOC | Upstream State | What's Missing Upstream |
|:-------|:-------------|:---------------|:------------------------|
| `hardware_calibration.rs` | 750 | 394 (synthesis only) | Real compile+dispatch+readback+ULP per-tier probes. barraCuda does `from_capabilities()` synthesis; hotSpring does actual GPU execution tests. |
| `precision_eval.rs` | 340 | None | Per-shader precision/throughput profiler across all tiers (compile time, dispatch latency, ULP error). No upstream equivalent exists. |
| `streaming_dispatch.rs` | ~200 | Partial (batched_encoder) | Command-encoder batching for HMC trajectories. Pattern should be in toadStool. |
| `transfer_eval.rs` | ~180 | Partial (probe_throughput) | PCIe upload/readback/dispatch overhead profiling. |

**Action for barraCuda team**: Accept `HardwareCalibration::probe()` and
`PrecisionEval` into `barracuda::device/`. This gives all springs (wet,
air, ground, neural, health, ludo) access to real per-tier GPU probing
instead of profile synthesis.

---

## Priority 2: WIRE to Primals (barraCuda → hotSpring)

These are already done or nearly done — hotSpring re-exports from primals:

| System | hotSpring | Primal | Status |
|:-------|:----------|:-------|:-------|
| `PrecisionTier` (15 tiers) | Re-exported | `barracuda::device::precision_tier` | ✓ WIRED |
| `PhysicsDomain` (15 variants) | Re-exported | `barracuda::device::precision_tier` | ✓ WIRED |
| `FmaPolicy` | Re-exported | `barracuda::device::fma_policy` | ✓ WIRED |
| `HwPrecisionAdvice` | Re-exported | `barracuda::device::PrecisionRoutingAdvice` | ✓ WIRED |
| Generic math tolerances | Parallel definitions | `barracuda::tolerances::precision` | WIRE incrementally |
| `spectral/` | Re-export wrapper | `barracuda::spectral` | ✓ WIRED |
| `production_support/` | Delegate | `barracuda::stats` | ✓ WIRED |

---

## Priority 3: KEEP Local (Legitimately Spring-Specific)

These should NOT move upstream — they are spring validation surfaces:

| System | Reason to Keep |
|:-------|:---------------|
| `tolerances/lattice.rs` | QCD-specific thresholds (plaquette, HMC, CG, Creutz, deconfinement) |
| `tolerances/md.rs` | Molecular dynamics validation (energy drift, transport, PPPM) |
| `tolerances/physics.rs` | Nuclear physics (HFB, BCS, NMP, screened Coulomb) |
| `tolerances/npu.rs` | NPU quantization parity thresholds |
| `provenance/` | Python baseline metadata traces |
| `composition.rs` | NUCLEUS atomic validation (Tower/Node/Nest physics probes) |
| `serve/` | hotSpring's own biomeOS capability surface |
| `niche/` | Spring self-knowledge (expected per-spring) |
| `validation/` | Spring pass/fail binaries |
| `precision_routing.rs` routing logic | Intersects HW advice with physics domains — spring-specific |
| `precision_brain.rs` probe logic | Uses `GpuF64`, sovereign detection, actual dispatch — spring-authoritative |

---

## Priority 4: WIRE Incrementally (Infrastructure)

| System | Current | Target | Blocker |
|:-------|:--------|:-------|:--------|
| `primal_bridge.rs` socket scanning | Local UDS scan | biomeOS `CapabilityClient` SDK | SDK needs socket resolution parity |
| `low_level/` (bar0, falcon) | Deprecated since 0.6.32 | toadStool ember/glowplug RPCs | Already marked; remove dead code |
| `fleet_client.rs`, `fleet_ember.rs` | Legacy fleet JSON | toadStool device management | Doc notes S244-S258 absorption |
| `ember_types.rs` | Typed MMIO structs | toadStool cylinder register maps | Shared types crate needed |

---

## Priority 5: ABSORB Pattern (Cross-Spring)

These patterns exist in multiple springs (hotSpring, wetSpring, healthSpring)
and should become a shared crate:

| Pattern | Springs Using It | Candidate Crate |
|:--------|:----------------|:----------------|
| DAG→Spine→Braid trio commit | hotSpring, wetSpring, healthSpring | `spring-provenance` |
| `WireWitnessRef` attestation | All springs | `attestation-types` |
| Compensated DF64 summation | hotSpring (new) | `barracuda::precision::compensated` |

---

## The Precision Brain Question

The `PrecisionBrain` specifically:
- **barraCuda** has: `PrecisionBrain::from_device()`, O(1) route table, 12 physics domains, `HardwareCalibration::from_device`, `FmaPolicy`, `brain.compile()` API
- **toadStool** has: simplified 4-tier compile-safety brain (BEHIND both)
- **hotSpring** has: `GpuF64`-based, sovereign detection via NucleusContext, actual GPU dispatch probes, circuit breaker

**Recommendation**: hotSpring's brain is the MOST CAPABLE version. The
upstream barraCuda brain is a synthesis (profile-based) while hotSpring's
is empirical (probe-based). The target state is:

1. **Absorb** hotSpring's probe methodology into barraCuda's brain
2. **Keep** hotSpring's brain as the local instance with spring-specific
   `GpuF64` integration
3. **Wire** the route table output format so all springs share the same
   `PrecisionRoute` type

This makes barraCuda the canonical precision brain implementation, with
hotSpring's empirical probes as the reference calibration source.

---

## Connection to DF64 Precision Folding Work

The deduplication directly enables the precision continuum study:
- Once `PrecisionEval` is upstream, ALL springs can run precision sweeps
- The tolerance ladder becomes a shared contract between springs
- DF64 compensated summation (new) should go to `barracuda::precision::compensated`
- DF32 (f16-pair) research stays in hotSpring until validated, then absorbs

---

*strandGate wateringHole — This handoff identifies 5 priority levels of
primal deduplication work. The key asymmetry: hotSpring is AHEAD on probe
depth (real GPU execution) while barraCuda is AHEAD on type abstraction
(15-tier enum, unified device). Convergence means absorbing hotSpring's
empirical probes into barraCuda's type system.*
