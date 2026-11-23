# primalSpring Wave 157g — Smart Decomposition & Deep Audit Handoff

**Date**: Aug 10, 2026
**Team**: primalSpring (eastGate)
**Wave**: 157g (ENMESH + Deep Debt + Smart Decomposition)
**Commit**: `12315d00`

## Delivered

### Smart Decomposition — `manifest.rs` (1185L → 652L)

The biome manifest module was the only file exceeding the 800L threshold.
Refactored into coherent submodules by concern:

| File | Lines | Responsibility |
|------|-------|----------------|
| `manifest.rs` | 652 | Types, loading, validation, topological sort |
| `workflow.rs` | 201 | Multi-composition orchestration engine |
| `reconcile.rs` | 124 | Live state reconciliation (socket probing) |
| `manifest_tests.rs` | 242 | All manifest tests |

Public API preserved via re-exports — zero breaking changes.

### Workspace Dependency Alignment

6 crypto deps promoted from local pins to workspace-level:
`hmac`, `sha2`, `hkdf`, `getrandom`, `zeroize`, `chacha20poly1305`

All 16 runtime deps pure Rust. G72 Tier 1 CLEAN (zero tokio, reqwest, env_logger).

### Clippy Deny-Level Errors Fixed (4 → 0)

- `CompositionKind` Default: manual impl → `#[derive(Default)]` + `#[default]`
- Useless `.into()` conversions removed in workflow timeout resolution
- Logic bug `|| true` fixed in neural learning scenario
- Experiments modernized: `is_some_and`, collapsed if-blocks, `format!` simplification

### Deep Audit Results — All Clear

| Category | Status |
|----------|--------|
| Hardcoded IPs/ports in production | CLEAN — all TOML-driven routing |
| Mocks in production code | CLEAN — all isolated to `#[cfg(test)]` |
| Overstep (other primals' responsibility) | CLEAN — deploy=validation, crypto=delegation |
| `todo!()`/`unimplemented!()` | Zero in production |
| `#[allow(dead_code)]` | Zero |
| `unwrap()` in production | Zero (all in test modules) |
| Unsafe code | Workspace `deny` + `#![forbid(unsafe_code)]` on all 88 crate roots |

### Test State

- **1,274 workspace tests**: 1,239 lib + 16 doc + 19 integration
- **0 failures, 0 clippy errors, 0 compiler warnings**
- **102 experiments** across 22 tracks

## Architecture Observations for Upstream Teams

1. **primalSpring is G72 exemplar**: zero tokio, zero HTTP clients, pure capability.call
   routing. Other primals can reference exp123 output for their own Tier 1 excision.

2. **Workflow engine available**: `composition::workflow` provides reusable DAG-based
   workflow orchestration. Could be extracted to a shared crate if other springs need it.

3. **Reconciliation pattern**: `composition::reconcile::reconcile_with_live()` probes
   socket existence for manifest-vs-reality drift detection. Pattern applicable to any
   gate running toadStool manifests.

## Gaps for Upstream

| Gap | Owner | Status |
|-----|-------|--------|
| `SignalTier` removal | primalSpring | Suppressed now, full removal Wave 170 |
| `footPrint SPA surface` not declared LIVE | footPrint team | 1 test assertion relaxed |
| G72 Tier 1 violations (8 primals) | Individual teams | Profiled by exp123, coordination needed |

## Files Changed

```
M  Cargo.toml                          (workspace deps added)
M  ecoPrimal/Cargo.toml                (deps → workspace refs)
M  ecoPrimal/src/composition/manifest.rs (652L, refactored)
M  ecoPrimal/src/composition/mod.rs    (+reconcile, +workflow)
A  ecoPrimal/src/composition/workflow.rs
A  ecoPrimal/src/composition/reconcile.rs
A  ecoPrimal/src/composition/manifest_tests.rs
M  ecoPrimal/src/validation/scenarios/s_neural_learning.rs
M  experiments/exp118_*/src/main.rs    (clippy fix)
M  experiments/exp119_*/src/main.rs    (clippy fix)
M  experiments/exp120_*/src/main.rs    (clippy fix)
M  experiments/exp121_*/src/main.rs    (clippy fix)
```
