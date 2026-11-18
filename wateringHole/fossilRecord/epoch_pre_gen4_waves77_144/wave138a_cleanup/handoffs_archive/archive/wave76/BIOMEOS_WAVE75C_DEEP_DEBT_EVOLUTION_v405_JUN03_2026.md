# biomeOS — Wave 75c Handoff: Deep Debt Evolution Sprint (v4.05)

**Date**: June 3, 2026
**From**: biomeOS (southGate)
**To**: primalSpring (eastGate) — upstream audit
**Version**: v4.04 → v4.05

---

## Summary

Comprehensive deep debt evolution sprint following v4.04 consolidation. Five
production files had their inline tests extracted (~1,989 lines), six hardcoded
`"biomeos"` string literals were replaced with `primal_names::BIOMEOS`, and
several idiomatic Rust improvements were applied. Full codebase audit confirmed
zero unsafe code, zero production mocks, zero `#[allow]`, zero `Result<_, String>`,
and zero `&Box<T>` parameters.

## Changes

### Test extraction wave 5 (~1,989 lines extracted)

| File | Before | After | Tests | Lines |
|------|--------|-------|-------|-------|
| `cap_probe.rs` | 694L | 230L | 21 | 464L |
| `registry_queries.rs` | 533L | 209L | 16 | 328L |
| `enroll.rs` | 680L | 247L | 25 | 435L |
| `trust.rs` | 505L | 181L | 26 | 325L |
| `haptic_feedback.rs` | 583L | 149L | 19 | 437L |

All use `#[path = "*_tests.rs"]` pattern. 107 tests verified passing.

### Hardcoded primal names → constants

Replaced 6 production `"biomeos"` string literals with `primal_names::BIOMEOS`:
- `universal_biomeos_manager/ai.rs` — JSON response `"source"` field
- `config/system.rs` — `SystemConfig::default()` name
- `config/observability/tracing.rs` — `TracingResourceConfig::default()` service_name
- `rootfs/config.rs` — default hostname
- `genome-factory/replicate.rs` — `GenomeManifest::new()`
- `handlers/genome/build.rs` — `GenomeManifest::new()`

Remaining `"biomeos"` literals are filesystem paths/directory names (intentional).

### Idiomatic Rust fixes

- `param.rs::as_array()`: `&Vec<Self>` → `&[Self]` (clippy::ptr_arg)
- `service.rs`: `map_err(|_| anyhow!(...))` → `.with_context(|| ...)`
- `perceptron.rs`: doc comment `"mock weights"` → `"neutral default weights"`

### Root docs updated

- `START_HERE.md`, `CONTEXT.md`: v4.02 → v4.05
- `SECURITY.md`: Supported versions table updated (v4.x current)
- `DOCUMENTATION.md`: Handoff range v2.43–v4.05, date updated
- `sporeprint/validation-summary.md`: Added v4.03–v4.05 entries
- `CHANGELOG.md`, `CURRENT_STATUS.md`, `README.md`: Already updated to v4.05

## Full Audit Results (verified clean)

| Check | Result |
|-------|--------|
| `unsafe` in production | **Zero** — all crates `#![forbid(unsafe_code)]` |
| Mocks in production | **Zero** — all in test modules |
| `#[allow(...)]` in production | **Zero** — all migrated to `#[expect(...)]` |
| `Result<_, String>` in production | **Zero** — v4.04 goal maintained |
| `&Box<T>` params | **Zero** |
| `&Vec<T>` params | **Zero** (1 fixed this sprint) |
| `TODO`/`FIXME`/`HACK` in production | **Zero** |
| `.unwrap()` in production | **Zero** |
| Production `.expect()` | 24 with `#[expect(clippy::expect_used)]` (all audited) |

## Remaining Debt (documented, not blocking)

- **76 `map_err` stringification sites** (format!, to_string) in beacon/dark-forest,
  BTSP, family_credentials, graph/parser — all inside thiserror enum mappings,
  not stringly-typed errors
- **2 `map_err(|e| anyhow!(...))` sites** — lz4_flex (no Error impl) and env var
  chain (legitimate `.with_context()` now)
- **`graphs/BONDING_TESTS_README.md`** — orphaned: references 5 test graphs
  that were never created (aspirational bonding model design)

## Test Status

- **4,979 tests** passing (4,458 lib + 521 bin), 0 failures
- Pre-existing: 2 doctest failures in `http_client.rs` (private module, not from changes)
- Clippy: 0 new warnings (pre-existing: `is_multiple_of`, `Drop` scrutinee)

## Blocked / Waiting

- **A/B shadow milestone**: counter accumulating, not yet at 1000
- **Perceptron Phase 2**: waiting primalSpring training data + `neural_routing_perceptron.bin`
- **Cross-gate mesh**: waiting Songbird capability propagation for end-to-end test

## Upstream Gaps for primalSpring

1. Training data generation for perceptron (primalSpring → biomeOS)
2. Songbird capability propagation verification (eastGate cross-gate test)
3. `http_client.rs` doctest: module is `pub(crate)` but doc examples use public path — minor
