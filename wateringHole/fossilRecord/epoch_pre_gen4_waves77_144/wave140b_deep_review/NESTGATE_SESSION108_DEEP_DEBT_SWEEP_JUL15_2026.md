# NestGate Session 108 — Deep Debt Sweep (Wave 140a)

**Date**: Jul 15, 2026 | **Wave**: 140a | **Commit**: e05001e9

## Changes

### Root Documentation Refresh
- All 12 root docs synchronized to ground-truth test counts (3,790/73/1)
  replacing stale 12,885/420/0 split that persisted since Session 101b
- Wave/session/date stamps updated: 136b→140a, Session 106→108, Jul 11→Jul 15
- Capability domain count corrected: 18/19→20 (matches actual registry)
- `footprint.*` methods added to STATUS IPC route listing
- `.gitignore`: removed misleading `Cargo.lock` entry (file is tracked per binary crate convention)
- `cargo clean`: reclaimed 41 GiB (159K files)

### Test Fixture Gating (cert/utils.rs)
- `create_test_certificate()` and `create_expired_certificate()` gated with `#[cfg(test)]`
- These test-only factory functions no longer leak into the production binary
- `CertificateType` import moved from module scope into cfg-gated function scope
- Eliminates ~2KB of dead test code from release builds

### Platform FS Audit (Cross-Platform Parity Phase 3)
- Audited all `PermissionsExt`, `std::os::unix`, and `rustix::fs` usage
- **Result**: All 3 sites (nestgate-installer `download.rs`, `platform.rs`) already behind `#[cfg(unix)]`
- **No Phase 3 blockers** — nestGate is ready for cross-platform parity when transport (Phase 2) ships
- socket_config, isomorphic_ipc: UDS references are transport-level (Phase 2 territory)

### String::from Round 4
- 63 production `String::from("literal")` → `"literal".into()` conversions
  - `pools.rs`: 31
  - `knowledge.rs`: 13
  - `system_config.rs`: 9
  - `cert/utils.rs`: 10

## Test Results
- **3,790 passed** / 1 pre-existing failure / 73 ignored / 0 clippy warnings

## Remaining Debt (diminishing returns)
- Production `String::from`: mostly exhausted in production code; remaining are test-only
- `map_err(format!)` → context helpers: ~200 sites (deferred — individual analysis needed)
- `NestGateError`/`ValidationError` thiserror: deferred (conditional Option Display)
- Production mock evolution: `ai_first_example.rs` hardcoded confidence values
- Cert `modern` module (feature-gated dev-stubs): contains `String::from` but appropriately gated
