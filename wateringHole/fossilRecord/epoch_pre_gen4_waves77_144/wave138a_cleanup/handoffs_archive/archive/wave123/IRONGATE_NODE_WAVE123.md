# ironGate Node Team — Wave 123 Dispatch

**Date**: Jun 22, 2026 | **From**: eastGate overwatch
**Gate**: ironGate (.7, LAN Hub 2) | **Composition**: 12/12 NUCLEUS + RTX 5070
**Primals**: ToadStool, BarraCuda, CoralReef

---

## Objective: GPU Compute Pipeline Live

You have the only GPU in the mesh (RTX 5070, CUDA 12.8). The dual-target depot is shipped (gnu binaries for GPU primals). Your job is to make the **compute pipeline operational** — train, infer, dispatch, and prove GPU sovereignty.

---

## P1 Tasks

### 1. BarraCuda LSTM Zero-Copy (RTX 5070)

- Validate `gnu` binary fetched from depot runs correctly on ironGate
- LSTM zero-copy inference: model loaded directly to GPU memory
- Vulkan/WGSL shader dispatch for math operations
- f64 native precision (not f32 downcast)

**Test**: `barraCuda ml.train` → `ml.save` → `ml.load` → `ml.infer` pipeline on RTX 5070.

### 2. CoralReef Shader Pipelines

- SPIR-V compilation via sovereign-dispatch IPC
- Artifact provenance headers (sporePrint hash + gate + signature)
- GPU dispatch for compiled shaders
- Validate FECS stability proofs still hold on gnu binary

### 3. ToadStool Fleet Dispatch

- 9,074 tests, S323 submit split
- Coordinate GPU workload distribution via `dispatch.verify_trust`
- Telemetry schema includes `gate-of-origin` field for cross-gate audit
- Fleet management: multiple workloads queued on single GPU

### 4. Dual-Target Depot Integration

- Confirm ironGate fetches `x86_64-unknown-linux-gnu` for GPU primals
- Confirm `x86_64-unknown-linux-musl` still used for non-GPU primals
- Validate `is_static_elf()` accepts dynamic ELF for gnu directory
- Report any depot fetch issues upstream to sporeGate

---

## P2 Tasks

### HPC VLAN Participant

- When VLAN 10 activates (blocked on MikroTik creds), ironGate joins as compute node
- `192.168.10.0/24` — gate-to-gate compute over 10G SFP+ trunk
- ironGate will be primary GPU consumer on HPC VLAN

---

## Context

- ironGate is **cytoplasm** in K-Derm topology — internal heavy compute
- Node atomic (ToadStool + BarraCuda + CoralReef) = fleet + GPU + shaders
- Dual-target depot shipped Wave 121: `primals/x86_64-unknown-linux-gnu/` exists
- All `ml.*` methods are behind BTSP MethodGate (bearDog w75) — auth required when enforced
- barraCuda has full ML pipeline (train→save→load→infer) from Wave 76

## Coordination

- sporeGate builds gnu binaries and rsyncs to golgi depot
- eastGate primalSpring will add GPU compute scenarios once pipeline is validated
- Report LSTM benchmarks and any gnu binary issues as impulse

---

*You have the GPU. Make it compute sovereign science.*
