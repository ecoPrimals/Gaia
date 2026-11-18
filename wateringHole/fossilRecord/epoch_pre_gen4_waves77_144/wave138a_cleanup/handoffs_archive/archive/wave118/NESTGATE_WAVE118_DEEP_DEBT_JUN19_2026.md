# nestGate — Wave 118 Deep Debt Evolution

**Date**: Jun 19, 2026
**Version**: 0.5.0
**Author**: sporeGate automation (primalSpring overwatch)

---

## Summary

Comprehensive audit and deep debt sweep across the full nestGate codebase (22 crates, 340k+ source lines). All items verified against wateringHole standards.

## Final Verification

| Check | Result |
|-------|--------|
| `cargo fmt --all -- --check` | CLEAN (0 diffs) |
| `cargo clippy --all-features -- -D warnings` | PASS (0 warnings) |
| `cargo doc --workspace --no-deps --all-features` `-D warnings` | PASS (0 errors) |
| `cargo test --workspace --all-features` | 12,941 passed, 0 failed, 427 ignored |
| `cargo deny check bans/advisories/licenses` | All OK |

## Changes

### Hardcoding Evolution (self-knowledge principle)

- **BEARDOG_\* env aliases removed** from production — `BEARDOG_SOCKET`, `BEARDOG_FAMILY_SEED`, `BIOMEOS_FAMILY_SEED` eliminated; canonical `SECURITY_PROVIDER_SOCKET`, `FAMILY_SEED`, `SECURITY_FAMILY_SEED` only
- **ZFS constants** evolved from compile-time `const` to `LazyLock`-cached runtime values with `NESTGATE_ZFS_*` env overrides
- **Port fallbacks** evolved from compile-time `const` to `LazyLock`-cached runtime values with `NESTGATE_FALLBACK_PORT_*` env overrides
- **Hardcoded primal names** in test assertions replaced with self-knowledge checks

### Mock Isolation

- `dev_environment` module fully gated behind `#[cfg(any(test, feature = "dev-stubs"))]`
- Production paths return `NestGateError::not_implemented(...)` instead of mock data
- Cloud storage detection returns proper error without `dev-stubs` feature
- Removed commented-out example impls from storage trait files

### Semantic Naming Alignment

- jsonrpsee method names aligned with ecosystem standard (`storage.object.store` → `storage.store`)
- Legacy RPC aliases emit `tracing::warn!` deprecation guidance
- `normalize_method()` warns on deprecated `nestgate.` prefix

### Code Quality

- Fixed 282+ rustfmt violations
- Fixed 7+ broken intra-doc links across workspace (safe_migration.rs, content_ops.rs, semantic_router, streams.rs, launcher.rs, auth_token_manager.rs, hardware_tuning)
- Removed all commented-out code blocks from test files
- Refactored 880-line `operations.rs` → 434-line production + 448-line test module
- Updated stale `specs/` references to `config/capability_registry.toml`
- Reconciled test counts across 7 root docs and sporeprint

### Fossil Cleanup

- **24 fossil/historical-bannered docs** moved to `ecoPrimals/infra/fossilRecord/nestgate/historical-docs-jun2026/`
- `docs/` reduced from 35 files to 11 current files
- Removed archived `infant_discovery_demo.rs` stub
- Removed empty `benches/` root directory (benchmarks are crate-level)
- Cleaned stale references in `tests/DISABLED_TESTS_REFERENCE.md`, `tests/SLEEP_MIGRATION_GUIDE.md`, `tests/README.md`
- Updated `DOCUMENTATION_INDEX.md` with fossil record pointer

## Upstream Gaps for Overwatch

### nestGate-specific (for next wave)

1. **tarpc not ecosystem-first**: tarpc activates only in HTTP standalone mode, not socket-only/ecosystem mode — needs wiring into `IsomorphicIpcServer`
2. **3 parallel handler stacks**: UDS dispatch, jsonrpsee HTTP, tarpc service are separate implementations — isomorphic unification pending
3. **Coverage at 84%** vs 90% target — CI enforces 80% floor only; workspace-wide llvm-cov not in CI
4. **No tarpc socket-level E2E test** — only in-process unit tests exist
5. **Real E2E tests `#[ignore]`d** — service_tests.rs, biomeos/template integration suites
6. **Fuzz targets don't cover RPC dispatch** — only parsing/validation fuzzed
7. **aarch64 musl CI** configured but not wired

### Cross-primal (for upstream teams)

- Legacy `BEARDOG_SOCKET` / `BEARDOG_FAMILY_SEED` env vars now rejected — any composition using these names will fail; migrate to `SECURITY_PROVIDER_SOCKET` / `FAMILY_SEED`
- jsonrpsee method names changed: `storage.object.store` → `storage.store`, `storage.object.retrieve` → `storage.retrieve`, etc. — clients targeting HTTP JSON-RPC must update
- primalSpring Nest Atomic tests should verify with updated nestGate
- `dev-stubs` feature no longer defaults on — compositions depending on mock ZFS paths need `--features dev-stubs`

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Clippy warnings | 0 | 0 |
| Fmt violations | 282 | 0 |
| Doc errors | 6+ | 0 |
| Tests passed | 12,943 | 12,941 |
| Files > 800L (src/) | 1 | 0 |
| Fossil docs in-tree | 24 | 0 |
| BEARDOG env aliases | 3 | 0 |
| Compile-time-only constants | 20+ | 0 (all env-configurable) |
| Legacy RPC aliases (silent) | 9+ | 0 (all warn on use) |
| Commented-out code blocks | 6 | 0 |
