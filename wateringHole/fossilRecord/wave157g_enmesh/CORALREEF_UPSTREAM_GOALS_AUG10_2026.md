<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef — Upstream Goals & Remaining Long-Term Work

**Date**: Aug 10, 2026
**Primal**: coralReef (GPU compiler)
**Wave**: 157i (current)
**Author**: coralReef on strandGate

---

## Purpose

This document captures coralReef's remaining long-term work as upstream
ecosystem goals. These items require coordination with other primals or
represent multi-wave efforts that should be tracked at the ecosystem level.

## Current Status

- **Tests**: 3,963 passed, 4 ignored, 0 failures
- **Clippy**: zero warnings (pedantic + nursery)
- **Unsafe**: zero (`#![forbid(unsafe_code)]` on all crates)
- **IPC**: 19 served methods, 5 consumed
- **Coverage**: ~84% workspace line coverage (compiler backends are gap)
- **Files**: all hand-written files < 800 LOC
- **Deep debt**: zero TODO/FIXME/HACK in committed code

---

## Long-Term Upstream Goals

### 1. Vertex/Fragment Shader Compilation (Phase C — 8-12 weeks)

**Priority**: High
**Dependencies**: None (self-contained)
**Scope**: coralReef only

NAK heritage exists for SPH emission, attribute ops, interpolation, and
encoder support. The gap is:
- naga → codegen IR translation for graphics stages
- IO address mapping (vertex attributes, interpolation qualifiers)
- Graphics builtins (`dpdx`/`dpdy`, `discard`, `gl_Position`)
- Public API for graphics shader compilation
- Integration tests with vertex+fragment pipeline

This activates the rasterizer + ROPs + full TMU pipeline in the ecosystem.

### 2. Coverage Push: 84% → 90% (Ongoing)

**Priority**: Medium
**Dependencies**: None
**Scope**: coralReef only

Compiler backends (SM20/SM32/SM50/SM70+ encoding) are the main coverage
gap. Systematic encoder test expansion per shader model.

### 3. Gossip Integration (Blocked on swarmVine)

**Priority**: Medium
**Dependencies**: swarmVine gossip mesh enmeshment
**Scope**: coralReef + swarmVine

Three gossip injection points defined (Wave 157e):
- `shader.compiled` — gates learn what this node can compile
- `silicon.targets` — toadStool/barraCuda discover compiler reach
- `compiler.health` — mesh detects compiler availability changes

Announced via `gossip.spread` when TCP 7800 cross-gate reachability exists.
Currently planned, not implemented.

### 4. EVOLUTION Markers (9 Deferred Items)

All require hardware modeling or IR extension work:

| Marker | Complexity | Category |
|--------|-----------|----------|
| SM32 `.s` peephole | High | IR extension + scheduler |
| Dual-issue support | High | Instruction scheduler |
| Co-issue modeling | High | Instruction scheduler |
| Reserved GPR model | Medium | Register allocator |
| PrmtSel non-Index modes | Low | IR extension |
| CBuf ALU encoding (`set_src_cx`) | Medium | Encoder evolution |
| OpBra `.u` form | Low | IR + encoder |
| Jump threading non-uniform | Medium | Optimization pass |
| Functional unit tracking | High | Instruction scheduler |

### 5. PTX Emitter Structural Refactor (Deferred)

**Priority**: Low
**Scope**: coralReef only

Split `PtxEmitter` into separate "IR view" and "emit state" structs to
eliminate borrow-checker-motivated `.clone()` calls. These clones are
cached/amortized and are not performance bottlenecks — this is a code
quality improvement, not a performance fix.

### 6. GEMM Evolution (Phase 3-4)

**Priority**: Medium
**Dependencies**: barraCuda for dispatch validation
**Scope**: coralReef + barraCuda

- Phase 3: GEMV / batched APIs for CG solvers
- Phase 4: hotSpring integration for blocked Dirac tiles
- f64 tensor cores require SM90+ (Hopper), not available on-site

Phase 1 (global memory) and Phase 2 (shared memory + ldmatrix) are complete.

### 7. Mesh/Task Shaders (Phase D — Far Horizon)

**Priority**: Low
**Dependencies**: Vertex/Fragment completion (Phase C)
**Scope**: coralReef only

Modern graphics pipeline without vendor SDK.

### 8. Sovereign WGSL Parser (Far Horizon)

**Priority**: Low
**Scope**: coralReef only

Reduce naga dependency by evolving toward a sovereign WGSL parser.
Currently naga handles WGSL/SPIR-V/GLSL parsing.

---

## Ecosystem Coordination Needs

| Need | Provider | Status |
|------|----------|--------|
| Gossip mesh | swarmVine | Blocked on enmeshment |
| Hardware validation | toadStool + barraCuda | Compute Trio LIVE |
| GEMM dispatch | barraCuda | Phase 2 IPC wired |
| Security provider | bearDog → BTSP | Phase 3 complete |
| Depot distribution | golgiBody | 4-arch unified |

---

## What Is NOT Remaining

coralReef has no outstanding blocking work for ecosystem operation:
- All IPC methods are wired and tested
- Compute Trio wire contract is complete
- BTSP Phase 3 authentication is complete
- Depot is 4-arch unified with BLAKE3SUMS
- Zero technical debt markers in committed code
- All files under size limits
- All lints clean

The items above are evolutionary improvements, not blockers.
