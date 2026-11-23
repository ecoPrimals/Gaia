<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef Wave 126 — SM120 Blackwell Edge Cases

**Date**: 2026-06-28 | **Wave**: 126 | **From**: ironGate agent
**Commit**: `b56b192a281d4af5ce6043414502587b6354b70e`

---

## Summary

Fixed three P0 SM120 PTX emitter codegen bugs that would produce incorrect
or invalid PTX on real Blackwell hardware. Added 11 new tests (6 SM120-specific,
5 batch compile SPIR-V coverage). Cleaned stale documentation footers.

## Fixes

### 1. Loop Break/Continue Control Flow (P0)

**Before**: `break` emitted `ret;` (exits kernel instead of loop). `continue`
was a no-op (infinite loop on Blackwell).

**After**: Loop emission pushes break/continue labels onto a stack. `break`
emits `bra $Lend;`, `continue` emits `bra $Lcont;`. Fallback (break outside
loop) adds `membar.sys; ret;` for GAP-HS-115 Blackwell readback safety.

Files: `statements.rs`, `mod.rs`, `emitter.rs`

### 2. Subgroup Reduce Multiply (P0)

**Before**: `SubgroupOperation::Mul` in `CollectiveOperation::Reduce` fell
through to `_ => "add"`, emitting `redux.sync.add` — wrong opcode for multiply.

**After**: Explicit match for all `SubgroupOperation` variants. `Mul` uses
shuffle-based warp reduction (same path as scan operations) since PTX
`redux.sync` has no `.mul` variant.

Files: `subgroup.rs`

### 3. NumSubgroups / SubgroupId Multi-Dimensional Workgroups (P0)

**Before**: `NumSubgroups` computed `ntid.x / WARP_SZ` (wrong for 2D/3D
workgroups). `SubgroupId` used `tid.x / WARP_SZ` (wrong linearization).
Both referenced undefined `WARP_SZ` symbol.

**After**: `NumSubgroups` = `ceil(ntid.x * ntid.y * ntid.z / 32)` via
shift-right-by-5. `SubgroupId` linearizes `tid.x + tid.y * ntid.x +
tid.z * ntid.x * ntid.y` then divides by 32. `SubgroupSize` uses literal
`mov.u32 r, 32` instead of `WARP_SZ`.

Files: `builtins.rs`

## New Tests

| Category | Count | Description |
|----------|-------|-------------|
| SM120 PTX emitter | 6 | break-label, break-outside-loop-membar, subgroup-size-literal, num-subgroups-all-dims, subgroup-id-linearized, loop-break-no-bare-ret |
| Batch compile | 5 | single SPIR-V, mixed WGSL/SPIR-V/GLSL, invalid base64 SPIR-V, SM120 batch, SPIR-V helper |

Total: 3648 tests (3644 passing, 4 ignored hardware-gated)

## Documentation Debt Cleared

- Stale footers updated: 3284/Wave 68 → 3648/Wave 126 in WHATS_NEXT, ABSORPTION
- Sporeprint "0 ignored" corrected to "4 ignored (hardware-gated)"
- EVOLUTION "iter 80 (current)" marked as historical
- Spec Phase 10 row updated: Sprint 13/3220 → Sprint 14/3648
- All 13 root docs aligned to Wave 126 / 3648 tests

## Upstream Impact

- No wire contract changes — existing `shader.compile.*` methods unchanged
- PTX output changes are semantically correct (better control flow, accurate builtins)
- No new dependencies

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --check` | PASS |
| `cargo clippy --all-features -- -D warnings` | PASS (zero warnings) |
| `cargo test --all-features` | PASS (3644 ok, 0 fail, 4 ignored) |
