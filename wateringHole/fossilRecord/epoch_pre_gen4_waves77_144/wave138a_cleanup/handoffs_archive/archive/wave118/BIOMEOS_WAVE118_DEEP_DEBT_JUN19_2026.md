<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- Copyright 2025-2026 ecoPrimals Project -->

# biomeOS — Wave 118 Deep Debt Evolution Sprint

**Date**: June 19, 2026
**Gate**: eastGate
**Version**: v4.30
**Status**: All quality gates passing

---

## Summary

Comprehensive deep debt sprint covering coverage expansion, dependency modernization, production file refactoring, and test isolation. All quality gates green — ready for upstream overwatch audit.

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | ~7,983 | **8,351** |
| Line coverage | 85.55% | **88.28%** |
| Branch coverage | — | **89.84%** |
| Clippy warnings | 0 | **0** |
| cargo deny | pass | **pass** (advisories/bans/licenses/sources) |
| TODO/FIXME in .rs | 0 | **0** |
| Files >800 LOC | 3 | **0** (all refactored to <400 LOC modules) |

## Changes

### Dependency Modernization
- axum 0.7 → 0.8 (route syntax migration `:param` → `{param}`)
- tokio-tungstenite 0.24 → 0.29
- etcetera 0.8 → 0.11
- mdns-sd 0.11 → 0.20
- Eliminated: thiserror 1 (now 2 only), windows-sys 0.48 (now 0.61 only)
- Documented: tarpc@0.37 skip-tree (upstream pinned to rand 0.8)

### Coverage Expansion (+2.73%)
New test suites for 16 previously-uncovered modules:
- `nucleus_ingest/mod.rs`: 0% → 95%
- `vm_federation.rs`: 41% → 97%
- `neural_router/mod.rs`: 44% → 99%
- `btsp_client_phase3.rs`: 11% → 98%
- `ai_advisor_core.rs`: 27% → 100%
- `neural_executor_rollback.rs`: 12% → 99%
- `routing.rs`: 48% → 98%
- Plus: graph_ops, nucleus, discovery_init, announce, enrichment, signal, server_lifecycle, btsp_client/{provider,server,client}, capability/call/{dispatch,gate,mesh}

### Production File Refactoring
- `handlers/capability.rs` (753L) → semantic `capability/` module tree (12 files)
- `error/core.rs` (745L) → `core/` directory (5 files)
- `btsp_client.rs` (739L) → `btsp_client/` directory (6 files)

### Test Isolation
- `temp-env` with `async_closure` feature for deterministic socket discovery
- 8 previously-flaky tests now fully isolated from host environment
- All tests run without host socket leakage

## Coverage Gap Analysis

Remaining 1.7% to 90% target is concentrated in binary entry points:
- `tower.rs` (215 missed), `init.rs` (266 missed), `biomeos-cli/main.rs` (294 missed)
- These are `main()` dispatch functions — require integration/e2e test harness
- **Library code effective coverage exceeds 90%**

## Upstream Audit Points

1. **tarpc rand 0.8**: Waiting on upstream `tarpc` release for rand 0.9 — skip-tree'd
2. **Binary entry point testing**: Needs `primalSpring` e2e scenarios or dedicated integration crate
3. **SemVer alignment**: Cargo.toml still 0.1.0 vs docs v4.30 — clarify versioning strategy

## For Upstream Primal Teams

This sprint did **not** change any IPC contracts or capability semantics. All primals connecting to biomeOS via JSON-RPC 2.0 over UDS are unaffected. The axum upgrade only affects the HTTP API (genome dist, trust, topology endpoints) — all existing route paths preserved.

---

**Next**: Commit, push via cascade, await overwatch audit.
