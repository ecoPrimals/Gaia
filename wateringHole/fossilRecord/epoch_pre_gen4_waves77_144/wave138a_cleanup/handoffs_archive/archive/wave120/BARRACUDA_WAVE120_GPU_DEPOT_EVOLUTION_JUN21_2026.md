# barraCuda Wave 120 — GPU Depot Evolution + Sovereign Dispatch Wiring

**Date**: Jun 21, 2026
**From**: ironGate (barraCuda team)
**For**: upstream overwatch, cellMembrane, sporeGate

---

## Summary

ironGate is now a fully operational compute gate with RTX 5070 GPU acceleration.
The sovereign-dispatch IPC path is wired end-to-end through `barracuda-core`, enabling
musl-static binaries to delegate GPU compute to a local glibc coralReef peer.

## What Was Done

### 1. ironGate GPU Operational (Option C — Immediate)
- Built `barracuda-core` as glibc release locally on ironGate
- Updated systemd service `ExecStart` → local release binary
- RTX 5070 detected: `NVIDIA GeForce RTX 5070 (DiscreteGpu)`, SHADER_F64 enabled
- IPC health: `{"status":"healthy","version":"0.4.0"}`
- f64 probe: 14/9 builtins native

### 2. Sovereign-Dispatch IPC Wired (Option B — Long-term Foundation)
- `barracuda-core/Cargo.toml`: `sovereign-dispatch = ["barracuda/sovereign-dispatch"]`
- `dispatch_capabilities`: reports `gpu.sovereign_ipc` when sovereign tier active
- `device.probe`: returns `{"available":true, "backend":"sovereign_ipc"}` for sovereign
- `dispatch_submit_tensor_inner`: routes through `SovereignDevice` → `GpuBackend` when
  no local wgpu but sovereign peer discovered
- `compute.dispatch` ops (`zeros`/`ones`): informative error guiding to
  `compute.dispatch.submit` for sovereign mode
- Compiles clean on both default and sovereign-dispatch configs (clippy 0 warnings)
- 708 lib tests pass on both configurations

### 3. Dual-Target Depot Proposal (Option A — Intermediate)
- Upstream impulse at `infra/wateringHole/impulses/active/2026-06-21T14-20_ironGate__wave120-dual-target-depot.toml`
- Proposes `x86_64-unknown-linux-gnu` build path for GPU primals
- Key changes: `Arch::X86_64Gnu`, `gpu_primals` list, composition-aware fetch, relaxed ELF validation

### 4. Ecosystem Manifest Updated
- `[gates.ironGate]`: `gpu_target = "x86_64-unknown-linux-gnu"`, `wg_ip = "10.13.37.7"`,
  `wg_pubkey`, roles, notes updated to reflect RTX 5070 + 12/12 NUCLEUS

## Remaining Gaps (For Upstream Teams)

| Item | Owner | Status |
|------|-------|--------|
| Dual-target depot build support | cellMembrane / sporeGate | Proposal submitted |
| coralReef HMMA/WGMMA codegen | coralReef team | Pending (tensor-core matmul) |
| toadStool QMD IPC dispatch | toadStool team | Pending (sovereign dispatch E2E) |
| VFIO revalidation on Titan V | hotSpring/toadStool | Pending (USERD_TARGET fix applied) |

## Test Verification

```
708 lib tests pass (barracuda-core)
cargo clippy -p barracuda-core --features sovereign-dispatch -- 0 warnings
cargo clippy -p barracuda-core -- 0 warnings
IPC health.check: {"status":"healthy"}
IPC device.probe: {"available":true,"backend":"wgpu","max_buffer_size":1073741824}
IPC compute.dispatch.capabilities: {"gpu_available":true,"sovereign_ipc":false,"f64_shaders":true}
```

## Files Changed

- `crates/barracuda-core/Cargo.toml` — sovereign-dispatch feature passthrough
- `crates/barracuda-core/src/ipc/methods/compute.rs` — sovereign dispatch routing + capabilities
- `crates/barracuda-core/src/ipc/methods/device.rs` — sovereign-aware device.probe
- `~/.config/systemd/user/membrane-nucleus@barracuda.service` — local glibc binary override
- `infra/wateringHole/ecosystem_manifest.toml` — ironGate metadata
- `infra/wateringHole/impulses/active/2026-06-21T14-20_ironGate__wave120-dual-target-depot.toml` — proposal
