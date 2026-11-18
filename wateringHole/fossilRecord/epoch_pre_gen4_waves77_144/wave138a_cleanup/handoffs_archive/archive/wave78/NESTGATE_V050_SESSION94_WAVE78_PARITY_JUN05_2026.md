# NestGate v0.5.0 — Session 94: Wave 78 Parity + Deep Debt Sweep

**Date**: 2026-06-05  
**Wave**: 78  
**Gate**: ironGate  

## Deliverables

### 1. `config/capability_registry.toml` (Wave 78 ecosystem convention)
- Moved existing root `capability_registry.toml` (294 lines, 18 capability sections, 81+ methods) to `config/` per ecosystem convention (matches biomeOS, petalTongue, sweetGrass)
- Root file retained as backward-compat pointer

### 2. Coverage sprint: 46 new tests (content pipeline + HTTP API handlers)

| Area | New Tests | Coverage Target |
|------|-----------|-----------------|
| Content dispatch routing (`dispatch_coverage_tests.rs`) | 10 | Every `content.*` through UDS dispatch |
| Storage path builders (`storage_path_tests.rs`) | 19 | `content_key_path`, `manifest_path`, `dataset_key_path`, `blob_key_path`, `extract_namespace`, `resolve_family_id`, `ensure_parent_dirs` |
| Content stream edge cases (`content_stream.rs`) | 9 | Missing params, oversized total, unknown stream_id, bad offset, size exceed, invalid base64, missing family_id, invalid hash |
| Transport handler content dispatch (`handler_tests.rs`) | 8 | Every `content.*` through HTTP transport layer |

### 3. Deep debt sweep

| Category | Change | Impact |
|----------|--------|--------|
| **File size** | `transport/handlers.rs` 833→384 lines (tests extracted to `handler_tests.rs`) | Zero files >800L |
| **Primal coupling** | `discover_biomeos_socket` → `discover_coordinator_socket`, `announce_to_biomeos` → `announce_to_coordinator`; `BEARDOG_SOCKET` documented as deprecated legacy | Self-knowledge only |
| **ZFS placeholders** | `convert_engine_to_placeholder_dataset` → `convert_engine_entry_to_dataset` with real JSON parsing | No fabricated data in prod |
| **Production stubs** | Hardware tuning + migration restore → `NestGateError::not_implemented` | No silent success stubs |
| **Async correctness** | `std::sync::Mutex` → `tokio::sync::Mutex` in `native_real/core.rs` | No runtime blocking |
| **Idiomatic Rust** | 32 `.to_string()` → `String::from()` in nestgate-zfs | Workspace style consistency |

### 4. Metrics

| Metric | Session 93 | Session 94 | Delta |
|--------|-----------|-----------|-------|
| Total tests | 12,574 | 13,035 | +461 |
| Lib tests | 9,101 | 9,212 | +111 |
| Clippy warnings | 0 | 0 | — |
| Test failures | 0 | 0 | — |
| Net lines | — | -213 | 402 added, 615 removed |

## Wave 78 Status

- [x] Zero clippy (pedantic + nursery)
- [x] Zero `#[allow]` in production
- [x] `config/capability_registry.toml` (machine-readable, TOML)
- [x] `forbid(unsafe_code)` on every crate root
- [x] Zero `unsafe` in production
- [x] Zero production mocks (all evolved to real impls or honest errors)
- [ ] Coverage 84% → 90% (46 tests added, continuing)
