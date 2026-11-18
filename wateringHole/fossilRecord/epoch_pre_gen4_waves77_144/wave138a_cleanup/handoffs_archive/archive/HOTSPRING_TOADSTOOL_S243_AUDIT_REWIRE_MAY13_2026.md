# hotSpring → toadStool: S243 Audit + Capability Rewire

**Date:** May 13, 2026
**Source:** hotSpring compute trio rewire + toadStool S237–S243 deep audit
**Context:** Post coralReef Sprint 9 excision. toadStool is sole critical
path for sovereign compute. Phase A+B absorption complete, Phase C planning.

---

## What we found (toadStool S237–S243)

### Completed — excellent work

| Sprint | Delivery |
|--------|----------|
| **S237** | Phase A ember absorption — `VfioResourceHandle`, vendor lifecycle, device pool, `ember.held_devices` in capabilities |
| **S238** | JH-2 envelope enforcement confirmed, magic-number consolidation, `println→tracing` |
| **S239** | Phase B glowplug absorption — `SwapOrchestrator` (7-step), `SysfsSwapExecutor` (real sysfs PCI unbind/rebind), `GpuPersonality` |
| **S240** | Test refactor, tracing, discovery timeout constants |
| **S241** | Phase C planning — `CudaBackend` removed, `SwapOrchestrator` coverage, `PHASE_C_CORAL_DRIVER_SPLIT_PLAN.md` |
| **S242** | Last `println!` → `tracing`, `ContiguousBytes` coverage, dep cleanup |
| **S243** | Legacy `swap_device()` removed, `reacquire()` orchestrated, `compute.dispatch.capabilities` gains `render_node` + `device_id` for coralReef cutover, coral-driver tree mapped |

**Stats:** 22,843+ tests, ~83.6% coverage, 67 live JSON-RPC methods.

### 67 live JSON-RPC methods verified by hotSpring audit

<details>
<summary>Full method list (grouped)</summary>

**Dispatch:** `compute.dispatch.submit`, `.status`, `.result`, `.forward`, `.capabilities`
**Pipeline:** `compute.dispatch.pipeline.submit`, `.status`
**Job queue:** `compute.execute`, `.submit`, `.status`, `.result`, `.cancel`, `.list`
**Shader:** `shader.dispatch`
**GPU:** `gpu.query_info`, `.info`, `.query_memory`, `.memory`, `.query_telemetry`, `.telemetry`
**HW learning:** `compute.hardware.observe`, `.distill`, `.apply`, `.share_recipe`, `.auto_init`, `.auto_init_all`, `.status`, `.vfio_devices`
**Performance:** `compute.performance_surface.report`, `.query`, `.list`, `compute.route.multi_unit`
**Ember:** `ember.list`, `ember.status`
**Gate:** `gate.update`, `.remove`, `.list`, `.route`
**Transport:** `transport.discover`, `.list`, `.route`, `.open`, `.stream`, `.status`
**Auth:** `auth.check`, `.mode`, `.peer_info`
**Health:** `health.check`, `.liveness`, `.readiness`, `compute.health`, `toadstool.health`
**Identity:** `identity.get`, `toadstool.version`, `compute.version`
**Capabilities:** `capabilities.list`, `capability.list`, `primal.capabilities`, `compute.capabilities`, `compute.discover_capabilities`
**Workload:** `toadstool.submit_workload`, `.query_status`, `.cancel_workload`, `.list_workloads`, `.query_capabilities`
**Resources:** `toadstool.resources.estimate`, `.validate_availability`, `.suggest_optimizations` (+ short aliases)
**AI:** `toadstool.ai.local_inference`, `.local_execute` (+ short aliases)
**Provenance:** `provenance.query`, `provenance.get`, `toadstool.provenance`
</details>

### Phase C gaps (confirmed NOT served as JSON-RPC)

| Gap | Detail |
|-----|--------|
| **`toadstool-cylinder`** | No crate in workspace. Per-device subprocess isolation not started. |
| **Coral-driver absorption** | 100+ files mapped (S243 recon), split plan written. No code move yet. |
| **Real VFIO fd holding** | `VfioResourceHandle` is metadata + optional fd number. Ember crate does not own ioctl/open path. |
| **`ember.swap` JSON-RPC** | Swap is internal only (`SwapOrchestrator`). No public RPC method. |
| **`sovereign.boot` JSON-RPC** | Rust API only (`SwapOrchestrator::execute_boot`). No public RPC. |
| **Warm pipeline** | Not a labeled deliverable in S237–S243. |
| **VFIO PBDMA dispatch** | Blocked on coralReef USERD_TARGET encoding fix. |

---

## What hotSpring rewired (this pass)

1. **Capability registry + niche:** +15 toadStool methods added (pipeline,
   performance surface, HW learning expanded, auth, provenance). Lockstep
   test passes.

2. **`ipc/tier2.rs`:** Added `dispatch_capabilities()` helper to query
   S243's enhanced `compute.dispatch.capabilities` (with `render_node`,
   `device_id`, `ember.phase`).

3. **`glowplug_client.rs`:** Phase C pending annotations on `device.swap`,
   `device.list`, `sovereign.boot`, `device.dispatch`. Doc notes that
   toadStool uses `compute.dispatch.submit` contract (not legacy
   `device.dispatch` shape).

4. **`fleet_client.rs`:** Ember Phase B documentation on `probe_ember_socket`.

5. **591/591** lib tests pass (up from 590).

---

## What toadStool needs to complete (from hotSpring's perspective)

### Critical path (C1–C4)

| Item | Why hotSpring needs it |
|------|------------------------|
| **C1: `toadstool-cylinder`** | Per-device isolation — hotSpring dispatches to multiple GPUs (Titan V, K80, RTX 5060). Cylinder provides fault isolation between them. |
| **C2: Coral-driver absorption** | VFIO open/ioctl/PBDMA/DRM dispatch code needs to live in toadStool so `compute.dispatch.submit` can actually run kernels on VFIO-bound GPUs. |
| **C3: `ember.swap` as JSON-RPC** | hotSpring's `GlowplugClient::device_swap()` calls `device.swap` via NUCLEUS. Currently gets `method_not_found`. |
| **C4: `sovereign.boot` as JSON-RPC** | hotSpring's `GlowplugClient::sovereign_boot()` calls `sovereign.boot`. Currently gets `method_not_found`. |

### Important but not blocking (C5–C7)

| Item | Why hotSpring needs it |
|------|------------------------|
| **C5: Warm pipeline** | Warm-catch/warm-fecs for GPU state preservation across driver swaps. Hardware validated on Titan V (3/4 tests pass). |
| **C6: CLI parity** | `toadstoolctl` equivalent of `coralctl` (~20 subcommands). Needed for operator workflows. |
| **C7: systemd service** | `toadstool daemon` as a system service for boot-time GPU management. |

### VFIO PBDMA blocker

toadStool's own docs note: "VFIO PBDMA dispatch — Blocked on coralReef
(USERD_TARGET encoding fix)". coralReef is now a pure compiler — if the
USERD_TARGET fix was in coral-driver code, it needs to move with the
coral-driver absorption (C2).

---

## Summary for toadStool team

> **hotSpring S243 audit (May 13, 2026):**
>
> Outstanding work on Phase A+B — ember and glowplug absorption are clean,
> `SwapOrchestrator` with real sysfs PCI swapping is exactly right, 67 live
> JSON-RPC methods, 22,843 tests. hotSpring is fully aligned.
>
> We've rewired our capability registry (+15 methods), added
> `dispatch_capabilities()` for your S243 `render_node`/`device_id` response,
> and annotated our client methods that will get `method_not_found` until
> Phase C wires them as JSON-RPC.
>
> **Critical blockers from our side:**
> 1. `toadstool-cylinder` for per-device subprocess isolation
> 2. Coral-driver absorption (VFIO ioctl/PBDMA/DRM dispatch)
> 3. `ember.swap` + `sovereign.boot` as JSON-RPC methods
> 4. The USERD_TARGET encoding fix (was in coral-driver, needs to move with absorption)
>
> We have the Titan V, Tesla K80, and RTX 5060 ready for hardware validation
> as each C-item lands. Warm-catch pipeline validated 3/4 on Titan V.

---

## References

| Topic | Location |
|-------|----------|
| hotSpring gap registry | `springs/hotSpring/docs/PRIMAL_GAPS.md` |
| Phase C execution plan | `springs/hotSpring/wateringHole/handoffs/HOTSPRING_PHASE_C_EXECUTION_PLAN_MAY12_2026.md` |
| Phase C coral-driver split plan | `primals/toadStool/infra/wateringHole/handoffs/PHASE_C_CORAL_DRIVER_SPLIT_PLAN.md` |
| coralReef + barraCuda remaining work | `infra/wateringHole/handoffs/HOTSPRING_CORALREEF_BARRACUDA_REMAINING_WORK_MAY13_2026.md` |
| Sovereign compute evolution pass | `infra/wateringHole/handoffs/HOTSPRING_SOVEREIGN_COMPUTE_EVOLUTION_PASS_MAY13_2026.md` |
