# Handoff: Diesel Engine Evolution — FLR-First Anchor Release (Exp 225)

**From**: hotSpring (GPU sovereign compute team)
**To**: primalSpring / upstream primals teams
**Date**: 2026-05-26
**Experiment**: 225 (Catalyst TPC Persistence Test) + Diesel Engine Evolution
**toadStool crates modified**: `cylinder`, `ember`, `server`

## Summary

Experiment 225 tested whether TPC PRI stations survive the nvidia-470
catalyst unbind → vfio-pci rebind cycle. **Result: GPU went cold.**

Root cause: `vfio_pci_core_release()` performs a device reset when the
last VFIO fd closes. The handoff pipeline called `disable_flr()` in
step 5 of `execute_handoff` — but by then, the `VfioAnchor` had already
been dropped in the RPC handler, triggering the reset.

PMC_ENABLE dropped from `0x5fecdff1` (23 engines, warm) to `0x40000020`
(2 engines, cold). nvidia RM bound to the cold GPU but could not complete
DEVINIT.

## Fix Applied: FLR-First Anchor Release

The diesel engine now suppresses FLR **before** dropping the anchor:

```
BEFORE (broken):
  anchor_store.remove(bdf)  →  kernel resets GPU  →  disable_flr()  ← TOO LATE

AFTER (fixed):
  prepare_anchor_release(bdf)  →  anchor.release_prepared()  →  no reset
```

### New APIs

1. **`guarded_sysfs::prepare_anchor_release(bdf)`** — pins bridges,
   disables FLR on target + all IOMMU siblings (HD Audio function).
   Must be called before `VfioAnchor` drop.

2. **`VfioAnchor::release_prepared(self)`** — self-consuming drop with
   debug assertion that `reset_method` is empty. Catches callers that
   skip `prepare_anchor_release()`.

3. **Step 0e anchor release guard** — in `execute_handoff`, reads
   PMC_ENABLE immediately. If GPU went cold (popcount < 10), halts with
   clear diagnostic instead of wasting 60s on doomed catalyst settle.

4. **Post-settle RM health check** — after seeder settle, verifies
   nvidia RM completed DEVINIT. Logs failure but continues for forensics.

### RPC Integration

Both `sovereign.warm_handoff` and `sovereign.catalyst_boot` now call
`prepare_anchor_release()` before the anchor store removal, and use
`release_prepared()` instead of implicit drop.

Step 5 `disable_flr` in `execute_handoff` is now documented as an
idempotent safety belt for direct callers.

## Test Results

- `cargo check`: clean
- `toadstool-cylinder`: 121 tests pass
- `toadstool-ember`: all tests pass
- `toadstool-server` (lib): 861 tests pass
- Pre-existing test failures in server integration tests (unrelated
  `start_servers_with_fallback` signature mismatch) unchanged

## Key Files Changed

| File | Change |
|------|--------|
| `cylinder/src/vfio/guarded_sysfs/` (was `guarded_sysfs.rs` — split S276) | `prepare_anchor_release()` in `driver_ops.rs` |
| `ember/src/vfio_anchor.rs` | `release_prepared()` |
| `server/src/pure_jsonrpc/handler/dispatch/sovereign.rs` | FLR-first wiring in both RPCs |
| `cylinder/src/vfio/sovereign_handoff/` (was `sovereign_handoff.rs` — split S276) | Step 0e guard in `runtime_probe.rs`, post-settle check, early `is_catalyst` in `pipeline.rs` |

## Upstream Impact

- **toadStool**: Direct — all changes are in toadStool crates
- **Other primals**: None — no API surface changes for IPC consumers
- **hotSpring**: Exp 225 documented, root docs updated

## Next Steps (post power cycle)

1. Re-run catalyst pipeline with FLR-first fix — RM should see warm GPU
2. If RM completes DEVINIT, capture golden state with TPC stations alive
3. Validate TPC persistence through vfio-pci rebind
