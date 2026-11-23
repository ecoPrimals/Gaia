# barraCuda Wave 151b — Doc Refresh + BTSP Summary

**Date**: Jul 26, 2026
**Gate**: eastGate
**Wave**: 151b
**Primal**: barraCuda
**Commit**: (pending)

---

## Summary

Root docs refreshed with post-BTSP-client metrics. CHANGELOG [Unreleased]
extended from Wave 129 → 151b. Deep debt audit re-confirmed clean.

## Metrics Reconciliation

| Metric | Previous | Current | Delta |
|--------|----------|---------|-------|
| Test attrs | 5,035 | **5,044** | +9 (BTSP client tests) |
| Rust files | 1,211 | **1,213** | +2 (btsp_client.rs + integration test) |
| Integration test files | 48 | **49** | +1 |
| WGSL shaders | 860 | 860 | — |
| IPC methods | 98 | 98 | — |

## Files Updated

1. `README.md` — test count, rust files, integration files
2. `CONTEXT.md` — test count, rust files
3. `STATUS.md` — test count (3 locations)
4. `CONTRIBUTING.md` — integration files
5. `PURE_RUST_EVOLUTION.md` — test count
6. `sporeprint/validation-summary.md` — test count, rust files
7. `CHANGELOG.md` — [Unreleased] extended to Wave 151b with 12 new entries
8. `specs/TENSOR_WIRE_CONTRACT.md` — "Sprint 73, 90 methods" → "Active, 98 methods"

## Debris Scan Results (clean)

| Category | Result |
|----------|--------|
| Empty directories | **0** |
| Temp/backup files | **0** |
| TODO/FIXME in code | **0** |
| Stale scripts | **0** — `test-tiered.sh` is active |

## Deep Debt Status (re-confirmed)

| Axis | Status |
|------|--------|
| Files >800L | **CLEAN** (max 783) |
| `#[allow]` | **0** |
| `unsafe` (prod) | **1** (barracuda-spirv, annotated) |
| FFI/-sys deps | **0** |
| Production mocks | **0** (all in `#[cfg(test)]`) |
| Hardcoded primals | **0** (last 2 doc examples fixed this wave) |
| `#[expect]` without reason | **0** |
| Production `.unwrap()` | **~0** (overwhelmingly test-local) |

## For Upstream

- BTSP client status: **DONE** (both bootstrap + delegated modes)
- barraCuda is ready for Nest Atomic BTSP strict enforcement
