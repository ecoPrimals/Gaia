# hotSpring → coralReef + barraCuda: Remaining Work Audit

**Date:** May 13, 2026
**Source:** hotSpring compute trio rewire + hardware validation
**Context:** Post coralReef Sprint 9 excision. toadStool Phase C is shared
blocker. coralReef and barraCuda have polish work but no structural gaps
left for the trio to function once toadStool delivers.

---

## coralReef — Remaining Work (pure compiler primal)

**State:** Sprint 9+, 3121 tests, `unsafe_code = "deny"` workspace-wide,
zero references to excised crates.

### Compiler completeness

| Item | Priority | Detail |
|------|----------|--------|
| **PTX SM120/Blackwell textures** | Medium | Texture ops + cooperative groups for Blackwell ISA. RTX 5060 DRM cracked, ISA codegen needed. |
| **`naga::Module` direct ingest** | Medium | Accept raw naga IR in addition to WGSL text. Enables pre-parsed input from springs that use naga directly. |
| **Coverage → 90%** | Low | Currently ~90% on compiler crates but some edge paths (error recovery, exotic WGSL extensions) untested. |

### Documentation

| Item | Priority | Detail |
|------|----------|--------|
| **`EVOLUTION.md` narrative** | Low | Sprint 9 excision is a landmark. Document the architectural decision and the boundary with toadStool. |

### Integration

| Item | Priority | Detail |
|------|----------|--------|
| **Live toadStool compile→dispatch CI** | High | Ecosystem integration test: coralReef compiles WGSL, toadStool dispatches on hardware, readback verifies. Requires toadStool Phase C. |
| **`capability.requires` compat** | Done | `compute.dispatch` with `legacy_id: gpu.dispatch` is already shipped. No action needed. |

### hotSpring asks (from hardware validation)

- None blocking. Compile IPC (`GLOBAL_CORAL` → `compile_wgsl_direct`) works
  correctly for all 44 WGSL shaders (nuclear, lattice, MD, CG) across SM70
  and SM86 targets. The compile path is clean.

---

## barraCuda — Remaining Work (v0.4.0, dispatch + precision)

**State:** 4393 tests, ~80.5% line coverage, `precision.route` wired with
15-tier ladder, `sovereign_dispatch_wire.rs` complete, `GLOBAL_CORAL` lazy
singleton for shader compile IPC.

### E2E integration

| Item | Priority | Detail |
|------|----------|--------|
| **PrecisionBrain → coralReef → sovereign dispatch CI** | High | End-to-end test: `precision.route` recommends tier → coralReef compiles → toadStool dispatches → readback validates. Requires toadStool Phase C. |
| **DF64 NVK validation** | High | NVK (Mesa Vulkan for NVIDIA) support: verify DF64 polyfill on real hardware. Known poison risk on proprietary driver; NVK may behave differently. |
| **Multi-GPU OOM recovery** | Medium | Fleet router needs OOM detection + fallback to next available GPU. Currently logs but doesn't recover. |

### Precision routing

| Item | Priority | Detail |
|------|----------|--------|
| **Sovereign path in `precision.route`** | Medium | Handler is wgpu-centric today — returns `hardware_hint: "compute"` but doesn't differentiate between wgpu dispatch and sovereign VFIO dispatch. When toadStool Phase C is live, `precision.route` should return a `dispatch_path: "sovereign"` field for VFIO-eligible GPUs. |
| **Tensor-core GEMM routing** | Medium | toadStool VFIO + coralReef HMMA/WGMMA codegen needed. `precision.route` should recommend tensor-core tier when available. |

### Coverage + testing

| Item | Priority | Detail |
|------|----------|--------|
| **Coverage 80% → 90% on GPU paths** | Low | GPU dispatch, precision brain, and sovereign wire modules need more edge-case coverage. |
| **Kokkos parity baseline** | Low | Establish parity benchmarks against Kokkos reference implementations for QCD kernels. |

### Method gate

| Item | Priority | Detail |
|------|----------|--------|
| **`METHOD_GATE_STANDARD` completeness** | Done | Sprint 61 already has method gate with Public/Protected classification. 72 IPC methods, Wire Standard L2. No action needed. |

### hotSpring asks (from hardware validation)

- `precision_advisory()` IPC client in hotSpring aligned with v0.4.0
  response format (`recommended_tier`, `fma_safe`, `requires_compiler`,
  `hardware_hint`, `rationale`, `needs_sovereign_compile`, `adapter`).
- `PrecisionAdvisory` struct matches. No compatibility issues.
- Fleet discovery in hotSpring already biases toward toadStool-first.

---

## Shared blocker: toadStool Phase C

Both primals' highest-priority remaining items (live CI integration tests)
require toadStool Phase C to be complete. The dependency chain is:

```
toadStool Phase C (VFIO dispatch daemon)
  ↓
coralReef (compile) + barraCuda (precision.route + dispatch wire)
  ↓
hotSpring (hardware validation on compute trio)
```

Neither coralReef nor barraCuda has structural work left to close for the
trio to function. Their remaining items are polish (coverage, docs, edge
cases) and integration testing that gates on toadStool.

---

## Summary for copy/paste to teams

### For coralReef team:

> **hotSpring compute trio audit (May 13, 2026):**
> Your compile path is clean — all 44 WGSL shaders compile correctly via
> `GLOBAL_CORAL` IPC to SM70/SM86. `capability.requires` with
> `compute.dispatch` (+ legacy compat) is correct. No blocking issues from
> hotSpring's side.
>
> Remaining items we see: PTX SM120/Blackwell texture ops, `naga::Module`
> direct ingest, `EVOLUTION.md` narrative for Sprint 9 excision, and the
> live compile→dispatch CI test (shared toadStool Phase C blocker).
>
> Coverage is solid at ~90% on compiler crates.

### For barraCuda team:

> **hotSpring compute trio audit (May 13, 2026):**
> `precision.route` IPC is aligned — hotSpring's `PrecisionAdvisory` struct
> matches v0.4.0's response format. `sovereign_dispatch_wire.rs` is complete.
> Fleet discovery biases toadStool-first. No compatibility issues.
>
> Remaining items we see: DF64 NVK hardware validation, sovereign path
> differentiation in `precision.route` (wgpu vs VFIO dispatch hint), tensor-core
> GEMM routing when coralReef HMMA codegen is ready, multi-GPU OOM recovery,
> and the E2E PrecisionBrain→coralReef→dispatch CI test (shared toadStool
> Phase C blocker).
>
> Coverage target: 80% → 90% on GPU paths. Method gate and wire standard are
> complete.

---

## References

| Topic | Location |
|-------|----------|
| hotSpring gap registry | `springs/hotSpring/docs/PRIMAL_GAPS.md` |
| Sovereign compute evolution pass | `infra/wateringHole/handoffs/HOTSPRING_SOVEREIGN_COMPUTE_EVOLUTION_PASS_MAY13_2026.md` |
| toadStool Phase C plan | `springs/hotSpring/wateringHole/handoffs/HOTSPRING_PHASE_C_EXECUTION_PLAN_MAY12_2026.md` |
| Upstream evolution pass | `infra/wateringHole/handoffs/UPSTREAM_PRIMAL_EVOLUTION_PASS_12_14_MAY12_2026.md` |
