<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef Wave 126 — Full Convergence Pass

**Date**: 2026-06-28 | **Wave**: 126 | **From**: ironGate agent
**Commit**: `3078d0b6d6b99c3df5f404d25812f930a4b0fc3b`

---

## Summary

Full convergence pass across three commits: SM120 Blackwell edge case fixes,
convergence debt (file splits, dispatch refactor, error propagation), and
documentation cleanup (stale references, dead links, gate identity correction).

## Changes

### SM120 Blackwell Edge Cases (Wave 126)
- Loop break/continue: proper label-based control flow instead of ret/no-op
- Subgroup reduce mul: shuffle-based warp reduction (PTX has no redux.sync.mul)
- NumSubgroups/SubgroupId: full 3D workgroup linearization
- SubgroupSize: literal 32 instead of undefined WARP_SZ symbol

### Convergence Debt (Wave 126b)
- 3 files >800 LOC split into 6 files <500 LOC each
- dispatch_jsonrpc (125 lines) decomposed into 4 focused handlers
- wgsl_to_spirv().ok() → explicit tracing::warn on SPIR-V emission failure

### Documentation Cleanup (Wave 126c)
- Gate identity: biomeGate → ironGate across docs
- Dead links: specs/SOVEREIGN_MULTI_GPU → docs/archive/ (moved Sprint 9)
- STATUS.md Checks table: 4632/~65% → 3649/~84%
- WHATS_NEXT.md: trimmed excised-crate fossil sections
- Sporeprint: removed nonexistent shader.compile.glsl method
- cargo clean: 8.1 GiB build artifacts purged

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 3649 (3645 pass, 0 fail, 4 ignored) |
| Coverage | ~84% |
| Clippy | 0 warnings (pedantic + nursery) |
| Files >800 LOC | 0 (hand-authored) |
| Unsafe | 0 (forbid on all crates) |
| Served methods | 19 |

## Upstream Notes

- No wire contract changes
- SM120 PTX output is now semantically correct for loops and subgroup ops
- All root docs aligned to Wave 126 / 3649 tests / ironGate assignment
- BEARDOG_SOCKET deprecated but retained for v0.3.0 migration window
