# hotSpring Pipeline Intelligence — Sovereign Compute Trio

**Date**: June 1, 2026 — Session S284 (late)
**Origin**: hotSpring validation pass after coralReef + barraCuda upstream sync
**Wave**: 67 alignment

---

## Executive Summary

The sovereign compute trio pipeline (coralReef compile → toadStool dispatch → barraCuda orchestrate) is **partially operational**. WGSL → SPIR-V compilation and VFIO bare-metal dispatch succeed end-to-end on Volta (Titan V). Three critical pipeline gaps block full sovereignty: (1) VFIO readback not implemented, (2) DRM dispatch has no execution provider, (3) barraCuda cross-gate method mismatch. Blackwell (RTX 5060) is non-viable for sovereign compute due to missing firmware.

---

## Pipeline Validation Matrix

| Stage | Component | Status | Notes |
|-------|-----------|--------|-------|
| Compile WGSL → SPIR-V | coralReef | **PASS** | sm_70 target, new hyperbolic/float decomp ops working |
| NUCLEUS Discovery | songbird | **PASS** | coralReef resolved for shader/compile/visualization/wgsl |
| VFIO Dispatch (Titan V) | toadStool/cylinder | **PASS** | Both `0000:02:00.0` and `0000:49:00.0` — ~1s dispatch |
| VFIO Readback | toadStool/cylinder | **FAIL** | 0 buffers returned, 0ms readback — not implemented |
| DRM Dispatch (Blackwell) | toadStool | **FAIL** | "visualization/shader service not available" |
| barraCuda Cross-Gate | barraCuda → toadStool | **FAIL** | Calls `compute.dispatch.execute` — method doesn't exist |
| Blackwell Firmware | toadStool/ember | **FAIL** | `compute_viable: false` — gr, pmu/gsp missing |

---

## Team-Specific Handbacks

### toadStool Team — P0

**GAP-TS-001: VFIO Cylinder Readback Not Implemented**
- **Impact**: Dispatch succeeds (`status: completed`) but output buffers are always empty
- **Evidence**: `"buffers": [], "readback_ms": 0` on every dispatch with `readback: true`
- **Recommendation**: Implement DMA readback in the local_cylinder dispatch path. The kernel binary is loaded and executed correctly — the missing piece is reading GPU memory back to host after dispatch completes.
- **Severity**: P0 — blocks all end-to-end compute validation

**GAP-TS-002: DRM Dispatch Requires Visualization Provider**
- **Impact**: All DRM-path GPUs (nvidia driver) cannot dispatch
- **Error**: `"visualization/shader service not available — sovereign GPU dispatch requires a running shader provider"`
- **Evidence**: Fails even with coralReef registered in songbird discovery
- **Root Cause**: toadStool's DRM dispatch path uses its own internal provider registry, not songbird's `ipc.resolve`. toadStool doesn't query songbird for providers.
- **Recommendation**: Either (a) wire toadStool's DRM dispatch to use songbird `ipc.resolve` for provider discovery, or (b) implement a built-in Vulkan compute context in toadStool's DRM path that can execute SPIR-V directly via `renderD128`.
- **Severity**: P0 — blocks all DRM-path GPUs including Blackwell

**GAP-TS-003: Blackwell Firmware Inventory Empty**
- **Impact**: `compute_viable: false` for RTX 5060 (`0x2d05`)
- **Evidence**: `gpu.query_info` returns chip `unknown-2d05`, all firmware fields `Missing` (gr, pmu, gsp, acr, sec2, nvdec)
- **Compute Blockers**: `["gr", "pmu/gsp"]`
- **Additional**: `f64_transcendentals_safe: false`, `nvvm_poisoning_risk: "transcendental_only"`
- **Recommendation**: Add sm_120/Blackwell firmware images to toadStool's firmware inventory. Until available, the DRM path (GAP-TS-002) is the only viable dispatch path for Blackwell.
- **Severity**: P1 — blocks VFIO sovereignty on Blackwell

**GAP-TS-004: `sovereign.warm_handoff` Hard Lockup Vector**
- **Impact**: System hard-locks during `rm_trigger → nv_open → rm_init_adapter` on cold VFIO GPU
- **Forensics**: See `experiments/234_CATALYST_MINIMAL_NOP.md` Run #6
- **Contributing Factors**:
  - Double RPC race (two `warm_handoff` calls ~500ms apart)
  - PCI I/O error before module load (`PCI disable failed: Input/output error`)
  - RM init deadlock inside nvidia-470 kernel module on cold GPU
- **Mitigation Deployed**: Safe caller with file lock, NMI watchdog (nmi_watchdog=1, softlockup_panic=1, hardlockup_panic=1)
- **Recommendation**: (a) Add server-side RPC dedup/mutex for `warm_handoff`, (b) Add PCI config health pre-check before `rm_trigger`, (c) Consider `no_bus_reset` awareness in the catalyst lifecycle
- **Severity**: P1 — can crash the entire machine

**GAP-TS-005: Wire Format Inconsistency**
- **Impact**: Different methods use different field names for the same data
- **Evidence**: `shader.dispatch` expects `binary`, `compute.dispatch.submit` expects `binary_b64`, `compile_result` expects `binary`
- **Recommendation**: Normalize to accept both `binary` and `binary_b64` on all dispatch endpoints
- **Severity**: P2 — developer friction

### coralReef Team — P1

**GAP-CR-001: No sm_120 (Blackwell) Codegen Target**
- **Impact**: All compilations targeting Blackwell fall back to sm_70
- **Evidence**: `shader.compile.wgsl` returns `target: "sm_70"` regardless of requested target
- **Recommendation**: Add sm_120 SASS or PTX codegen target for Blackwell (GB202/GB206)
- **Severity**: P1 — performance loss from arch mismatch, potential correctness issues

**GAP-CR-002: `opt_copy_prop` Panic on Subgroup Shaders**
- **Impact**: coralReef crashes when compiling `sum_reduce_subgroup_f64.wgsl`
- **Error**: `assertion: entry_ssa.comps() == 1` on `SubgroupBallotResult`
- **Recommendation**: Fix subgroup ballot result component count handling in the copy propagation pass
- **Severity**: P1 — blocks subgroup-accelerated kernels
- **Filed**: GAP-HS-116

**GAP-CR-003: f64 `pow()` Not Implemented**
- **Impact**: WGSL shaders using `pow()` with f64 arguments fail to parse
- **Workaround**: Deployed — replaced with integer-power loops where exponent is known-integer
- **Recommendation**: Implement `pow(f64, f64)` in WGSL frontend or emit polyfill
- **Severity**: P2 — workaround exists
- **Filed**: GAP-HS-117 (resolved locally)

### barraCuda Team — P1

**GAP-BC-001: Cross-Gate Dispatch Calls Wrong Method**
- **Impact**: `compute.dispatch.submit` routes to toadStool but calls `compute.dispatch.execute` which doesn't exist
- **Evidence**: `"error": "Workload 'unknown' failed: JSON-RPC error (code -32601): [Dispatch] method not found: compute.dispatch.execute"`
- **Recommendation**: Change the cross-gate dispatch to call `compute.dispatch.submit` or `shader.dispatch` on the toadStool endpoint
- **Severity**: P0 — blocks the entire cross-gate dispatch pipeline

**GAP-BC-002: VFIO Device Visibility**
- **Impact**: `compute.dispatch.capabilities` shows `vfio_status.device_count: 0` even though 2 Titan Vs are bound to vfio-pci
- **Evidence**: barraCuda only sees the DRM GPU (`0000:21:00.0`), not the VFIO GPUs
- **Recommendation**: Wire barraCuda's device enumeration to either query toadStool's `compute.hardware.vfio_devices` or scan `/sys/bus/pci/drivers/vfio-pci` directly
- **Severity**: P1 — barraCuda can't route workloads to sovereign GPUs

### songbird/NUCLEUS Team — P2

**GAP-SB-001: Provider Registration Not Auto-Propagated to toadStool**
- **Impact**: Registering coralReef with songbird (`ipc.register`) doesn't propagate to toadStool's internal provider registry
- **Evidence**: toadStool still returns "visualization/shader service not available" after songbird resolves coralReef correctly
- **Recommendation**: Either (a) add a push notification mechanism so songbird informs toadStool when a new provider registers, or (b) have toadStool periodically poll songbird for provider updates
- **Severity**: P2 — manual wiring is possible, but breaks the NUCLEUS auto-discovery contract

**GAP-SB-002: Circular Symlink for barraCuda Socket**
- **Impact**: `barracuda-hotspring-validate.sock` symlinks to itself on launcher
- **Evidence**: `lrwxrwxrwx barracuda-hotspring-validate.sock -> barracuda-hotspring-validate.sock`
- **Recommendation**: Fix the symlink creation logic in `nucleus_launcher.sh` — should point to the actual socket created by the barraCuda process
- **Severity**: P2 — causes barraCuda IPC failures until manually fixed

---

## Hardware State at Validation Time

| GPU | BDF | Driver | VFIO | MMIO BAR0 | PCI Status | Dispatch |
|-----|-----|--------|------|-----------|------------|----------|
| Titan V #1 | 0000:02:00.0 | vfio-pci | Yes | 0x14000121 | 0x0010 (clean) | PASS (cylinder) |
| Titan V #2 | 0000:49:00.0 | vfio-pci | Yes | 0x14000121 | 0x0010 (clean) | PASS (cylinder) |
| RTX 5060 | 0000:21:00.0 | nvidia | No | N/A | 0x0010 (clean) | FAIL (no provider) |

## Kernel Defense Matrix

| Parameter | Value | Purpose |
|-----------|-------|---------|
| kernel.nmi_watchdog | 1 | Hardware NMI watchdog for hard lockup detection |
| kernel.softlockup_panic | 1 | Panic on soft lockup → kdump stack trace |
| kernel.hardlockup_panic | 1 | Panic on hard lockup → NMI stack trace |
| Persistent config | /etc/sysctl.d/99-hotspring-watchdog.conf | Survives reboot |

## coralReef Math Ops Validated

The latest coralReef push (1d9452c) adds hyperbolic trig and float decomposition. Validated:
- `sinh()`, `cosh()`, `tanh()` → compiles to sm_70 SPIR-V ✓
- `fract()`, `floor()` → compiles to sm_70 SPIR-V ✓
- Shared-memory tree reduction → compiles to sm_70 SPIR-V ✓
- Vector multiply (vec4<f32>) → compiles and dispatches on Titan V ✓

## Next Evolution Targets

1. **toadStool readback** — Unblock end-to-end validation with actual result verification
2. **barraCuda method fix** — `compute.dispatch.execute` → `compute.dispatch.submit`
3. **DRM compute provider** — Vulkan compute context for nvidia-driver GPUs
4. **sm_120 codegen** — Native Blackwell shader compilation
5. **songbird → toadStool provider push** — Auto-discovery propagation

---

*Generated by hotSpring sovereign compute validation pipeline — S284*
*ecoPrimals Wave 67 — June 1, 2026*
