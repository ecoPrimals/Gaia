# BearDog v0.9.0 — Wave 118: PRIMAL_CONTRACTS Method Catalog Refresh

**Date**: May 28, 2026
**Commit**: `5ace09924`
**Responds to**: Wave 59 Mountain Blurb (bearDog residual items)

---

## Summary

Complete overhaul of `docs/PRIMAL_CONTRACTS.md` (v3.0.0 → v4.0.0) to align the documented API surface with the actual registered handler methods.

## Wave 59 bearDog Items — All Resolved

| Item | Status | Resolution |
|------|--------|------------|
| Env debt | **RESOLVED** | Waves 116-117: `env_keys` module (107 constants), all domain files migrated |
| NC-3.5: `auth.issue_session` scope | **RESOLVED** | Wave 108: `content.*` scope in session tokens |
| PRIMAL_CONTRACTS stale | **RESOLVED** | Wave 118: this handoff |

## Changes

### Method Catalog (largest change)

| Metric | Before (v3.0.0) | After (v4.0.0) |
|--------|-----------------|----------------|
| Total methods documented | 127 | **223** (215 registry + 8 gate) |
| Handler categories | 15 | **18** |
| CryptoHandler count | 103 | **106** |
| IonicBondHandler count | 8 | **12** |
| Auth gate methods | 5 | **7** |
| BtspHandler count | 6 | **36** |
| SecurityHandler count | 6 | **19** |
| Missing categories | Health, FIDO2, Graph, Encryption | **All documented** |
| Stale method names in index | 32 | **0** |

### Error Codes

| Code | Before | After |
|------|--------|-------|
| -32000 | HSM error | **UNAUTHORIZED** (invalid/expired token) |
| -32001 | Lineage error | **PERMISSION_DENIED** (missing scope) |
| -32002 | Secret not found | **NOT_READY** (primal uninitialized) |
| -32003 | Relay denied | *Removed (not in code)* |
| -32004 | Beacon error | *Removed (not in code)* |

### Other Fixes

| Section | Before | After |
|---------|--------|-------|
| TCP default port | 9190 (metrics) | **9100** (`DEFAULT_TCP_IPC_PORT`) |
| Auth model | Genetic lineage only | **Multi-layer**: genetic + ionic tokens + session tokens + `MethodGate` |
| Implementation paths | Stale (`crypto_handlers_genetic.rs`) | **Current** crate layout paths |
| `system.version` example | Referenced non-existent method | Replaced with `primal.info` / `rpc.methods` |
| Document version | 3.0.0 | **4.0.0** |

## SSOT Note

The method index in `PRIMAL_CONTRACTS.md` is a human-readable snapshot. The runtime SSOT is `rpc.methods` / `capabilities.list`, which reflect the exact set of registered handlers at any point.

---

*All Wave 59 bearDog items resolved. Ready for downstream primalSpring audit.*
