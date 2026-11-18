# FRAGO: barraCuda — Sovereign Compute Cascade

**From:** hotSpring (Exp 234 pipeline validation)
**To:** barraCuda team
**Priority:** P1/P2
**Date:** June 1, 2026
**Type:** Fragmentary Order — evolution targets for next cascade

---

## Context

hotSpring validated the sovereign compute pipeline. barraCuda's tensor operations
and WGSL shader library are working well — 16 naga-exec tests pass, GPU tensor
round-trips work. Two wire-contract items need attention.

## P1: compute.dispatch.submit wire contract clarification

barraCuda's `compute.dispatch.submit` handler (`compute.rs:203`) is currently a
tensor passthrough — it accepts `input.data`, creates a GPU tensor, reads it back.
It does NOT forward to toadStool or execute arbitrary shader binaries.

hotSpring's `compute_dispatch/mod.rs` sends compiled SPIR-V binaries with
`binary_b64`, `bindings`, and `shader_info` fields. These are silently ignored
by barraCuda's handler (it only looks for `input.data`).

**Ask:** Clarify the contract:
- If `compute.dispatch.submit` is meant to be tensor-only, document it and
  expose shader dispatch under a different method (or route to toadStool).
- If it should accept compiled binaries, evolve the handler to forward to
  toadStool via songbird capability resolution.

The method name collision creates confusion about which primal owns shader
dispatch vs tensor operations.

## P2: Cross-gate capability routing

barraCuda advertises `consumed_capabilities: ["compute.dispatch"]` in its
primal manifest. Consider using songbird's `ipc.resolve` to discover toadStool
when receiving workloads that need hardware dispatch, rather than handling
them locally or dropping unknown fields.

## What's working well

- `barracuda::tensor::Tensor` GPU round-trip: creates tensors, reads back correctly
- naga-exec CPU-simulated WGSL execution: all 16 tests pass
- `compute.dispatch` named ops (zeros, ones, read): clean and correct
- `compute.dispatch.capabilities`: properly reports GPU/CPU availability
- `compute.dispatch.result` job store: works for tensor workloads

## plasmidBin deployment note

barraCuda socket management had issues during NUCLEUS composition (circular
symlinks). This is documented in:
- `hotSpring/HOTSPRING_NUCLEUS_DEPLOYMENT_LESSONS_JUN01_2026.md`

NOT blocking — do not gate evolution on deployment. Focus on wire contract.

---

**Handback:** `docs/PRIMAL_GAPS.md`, plus `HOTSPRING_PIPELINE_INTELLIGENCE_JUN01_2026.md`
