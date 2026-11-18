# NUCLEUS Deployment Lessons — hotSpring Sovereign Compute

**Date**: June 1, 2026 — Session S284
**Origin**: hotSpring pipeline revalidation on 3-GPU workstation
**Wave**: 67 alignment

---

## Context

hotSpring deployed a full NUCLEUS composition (`niche-hotspring`, 9 primals) to validate
the sovereign compute trio pipeline. This document captures what worked, what didn't, and
specific lessons for upstream primal teams.

## What Worked

### 1. nucleus_launcher.sh Composition Deployment
The launcher successfully started and registered all 9 primals (beardog, songbird, coralreef,
barracuda, nestgate, rhizocrypt, loamspine, sweetgrass, plus toadstool via TCP). Composition
startup was ~80 seconds. The `niche-hotspring` composition definition was sufficient.

### 2. songbird Discovery + ipc.register
Manually registering coralReef's capabilities with songbird via `ipc.register` worked
correctly. All 7 capabilities (shader, spirv, wgsl, glsl, naga, compile, visualization)
resolved successfully via `ipc.resolve`. The virtual endpoint
(`/primal/coralreef-core-hotspring-validate`) was created correctly.

### 3. toadStool TCP Interop
toadStool on TCP:33709 accepted JSON-RPC from both direct `socat` connections and from
barraCuda's cross-gate routing. The `capability.list` endpoint was invaluable for
debugging — it returns the complete method surface, cost estimates, and dependency graph.

### 4. coralReef WGSL Compilation
coralReef compiled every shader correctly: simple add kernels, vector multiply,
tree reduction with shared memory, hyperbolic trig functions, float decomposition.
Target architecture auto-detection worked (sm_70 for Volta). The new math ops from
commit `1d9452c` (sinh/cosh/tanh, fract/floor) were immediately usable.

### 5. VFIO Dispatch Through local_cylinder
toadStool's VFIO dispatch path (`local_cylinder`) worked on both Titan V GPUs.
Compiled SPIR-V binaries from coralReef were accepted and executed. The dispatch
took 1-4 seconds (acceptable for sovereign bare-metal cold path).

## What Didn't Work

### 1. barraCuda Circular Symlink (P2)
**Problem**: `barracuda-hotspring-validate.sock` was a circular symlink pointing to itself.
**Root cause**: The `nucleus_launcher.sh` symlink creation logic creates the symlink before
barraCuda creates the actual socket, resulting in a self-referencing link.
**Workaround**: Delete the symlink, wait for barraCuda to create the actual socket, then
manually create the correct symlink or use `compute-hotspring-validate.sock` directly.
**Fix**: Launcher should wait for the socket file to exist before creating capability symlinks.

### 2. songbird → toadStool Provider Discovery Gap (P1)
**Problem**: Registering coralReef with songbird doesn't propagate to toadStool's internal
provider registry. toadStool's DRM dispatch path requires a "visualization/shader provider"
that it discovers internally, not through songbird.
**Impact**: DRM-path GPUs (nvidia driver) cannot dispatch. The NUCLEUS discovery contract
is incomplete — primals should discover each other through songbird, not maintain separate
internal registries.
**Workaround**: Use VFIO path (where toadStool doesn't need a provider) or pass pre-compiled
binaries directly to `shader.dispatch`.

### 3. barraCuda Cross-Gate Method Mismatch (P0)
**Problem**: barraCuda's `compute.dispatch.submit` routes workloads to toadStool but calls
`compute.dispatch.execute`, which doesn't exist. The actual method is `compute.dispatch.submit`.
**Impact**: The entire barraCuda → toadStool cross-gate dispatch pipeline fails.
**Fix**: One-line change in barraCuda's cross-gate router to call the correct method name.

### 4. VFIO Readback Not Implemented (P0)
**Problem**: toadStool's `local_cylinder` dispatch always returns empty buffers (`[]`) and
`readback_ms: 0`, even when `readback: true` is specified in binding descriptors.
**Impact**: Dispatch succeeds but results cannot be verified. Blocks all compute validation.
**Root cause**: The VFIO dispatch engine loads and executes SPIR-V but lacks DMA readback.

### 5. Wire Format Inconsistency (P2)
**Problem**: Different toadStool methods use different field names for the same binary data:
- `shader.dispatch` expects `binary`
- `compute.dispatch.submit` expects `binary_b64`
- `compile_result` expects `binary`
**Impact**: IPC callers must know which variant to use per endpoint.
**Fix**: Normalize all endpoints to accept both `binary` and `binary_b64`.

### 6. BTSP Tarpc Plaintext Warnings
**Problem**: Every 30 seconds, toadStool logs `"BTSP tarpc: plaintext first line is not
JSON-line BTSP — closing"` followed by `"Plain-text connection on BTSP socket"`. This is
the launcher's health check connecting over plain JSON-RPC to a socket that expects BTSP
framing.
**Impact**: Log noise. Not a functional issue.
**Fix**: Have the health checker use BTSP framing, or have the socket gracefully handle
both without warning.

## Deployment Topology That Worked

```
                    ┌─ beardog (UDS) ─ security
                    ├─ songbird (UDS) ─ discovery, network
  launcher ─────────┼─ coralreef (UDS) ─ shader, compile
  (81s startup)     ├─ nestgate (UDS) ─ storage
                    ├─ rhizocrypt (UDS) ─ dag, session
                    ├─ loamspine (UDS) ─ ledger
                    └─ sweetgrass (UDS) ─ attribution

  toadStool ────── TCP:33709 (3 GPUs, 140+ methods)
  (separate)       ├─ 0000:02:00.0 Titan V (VFIO) ✅
                   ├─ 0000:49:00.0 Titan V (VFIO) ✅
                   └─ 0000:21:00.0 RTX 5060 (nvidia/DRM) ❌ provider gap

  barraCuda ────── UDS: compute-hotspring-validate.sock
  (compute gate)   └─ cross-gate → toadStool (❌ method mismatch)
```

## Recommendations for Upstream

### nucleus_launcher.sh
1. Wait for socket creation before creating capability symlinks
2. Use `--liveness-check` flag to verify sockets are responsive (not just present)
3. Add a `--register-capabilities` phase that auto-registers each primal's capabilities
   with songbird after all primals are started

### toadStool
1. **P0**: Implement DMA readback in local_cylinder
2. **P0**: Query songbird for providers instead of maintaining internal registry
3. Normalize wire format (`binary`/`binary_b64` accepted everywhere)
4. Add `compute.dispatch.execute` as alias for `compute.dispatch.submit` (prevents breakage)

### barraCuda
1. **P0**: Fix `compute.dispatch.execute` → `compute.dispatch.submit` in cross-gate router
2. Wire VFIO device discovery via toadStool's `compute.hardware.vfio_devices`

### coralReef
1. **P1**: Add sm_120 (Blackwell) codegen target
2. **P1**: Fix `opt_copy_prop` panic on subgroup shaders

---

*Generated from hotSpring S284 deployment — ecoPrimals Wave 67*
