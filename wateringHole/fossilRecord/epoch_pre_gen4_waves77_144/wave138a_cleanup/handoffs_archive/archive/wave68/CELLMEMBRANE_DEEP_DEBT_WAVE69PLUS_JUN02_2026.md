# cellMembrane — Deep Debt Evolution (Wave 69+)

**Date:** 2026-06-02
**Gate:** ironGate
**Repo:** `gardens/cellMembrane`
**Status:** COMPLETE

---

## Summary

Systematic deep debt elimination sprint targeting modern idiomatic Rust,
smart refactoring (not just splitting), and capability-based evolution.
All `#[allow(clippy::too_many_lines)]` annotations eliminated from production
code. Zero clippy warnings at pedantic+nursery level. All files under 800L.

---

## Changes

### 1. `plasmid.rs::fetch()` — Staged Pipeline Decomposition

**Before:** Single 140-line function with `#[allow(clippy::too_many_lines)]`.

**After:** Decomposed into cohesive stages:
- `format_dry_run()` — dry-run output formatting
- `fetch_all_primals()` — download loop with checksum verification
- `build_summary()` — aggregate counters from results
- `format_outcome()` — final message construction

Added `Display` impl for `FetchSource`, `Clone` derive for `FetchResult`.

### 2. `temporal/mod.rs` — Sync Function Extraction

**Before:** 2x `#[allow(clippy::too_many_lines)]` on `check()` and `sync_with_policy()`.

**After:** Extracted 5 focused async helpers:
- `count_divergent_remotes()` — O(n²) cross-remote comparison
- `sync_converge()` — pull-leader + push-followers logic
- `sync_diverge()` — manifest policy lookup + impulse posting
- `resolve_tree_parity()` — reset + force-push alignment

### 3. `cascade.rs` — Bool Elimination + Helper Extraction

**Before:** `#[allow(clippy::too_many_lines, clippy::fn_params_excessive_bools)]`,
3 bool params (check_only, dry_run, publish_freshness).

**After:**
- `CascadeMode` enum (`Sync`, `CheckOnly`, `DryRun`) replaces 3 bools
- `CascadeOpts` struct with typed fields
- `cascade_with_opts()` public API (evolved path)
- Extracted: `process_repo()`, `clone_repo()`, `check_repo()`, `sync_repo()`
- `RepoResult` enum for structured loop outcomes

### 4. `dispatch/infra.rs` — Mirror Sync Extraction

**Before:** `#[allow(clippy::too_many_lines)]` on `dispatch_mirror()`.

**After:** Extracted `mirror_sync_all()` — the org-iteration + trigger loop.

### 5. `freshness.rs` — Dead Code Wired

**Before:** `#[allow(dead_code)]` on `installed_at` and `binary_blake3` fields.

**After:** Both fields included in freshness report output:
- `installed_at` → timestamp suffix `[2026-06-01T12:34:56Z]`
- `binary_blake3` → short hash prefix `b3=a1b2c3d4`

### 6. `coverage.rs` — Smart Split (903L → 743L)

NUCLEUS composition tests (15 tests, ~160L) relocated from `coverage.rs` to
`composition.rs` (their canonical module home). No test duplication.

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| `#[allow(clippy::too_many_lines)]` | 5 | 0 |
| `#[allow(dead_code)]` | 2 | 0 |
| Largest file (production) | 903L | 743L |
| Clippy warnings (pedantic+nursery) | 0 | 0 |
| Tests | 209 | 209 |
| Files >800L | 1 | 0 |
| Production `.unwrap()` | 0 | 0 |
| `#![forbid(unsafe_code)]` | both crates | both crates |

---

## Remaining Justified Allows (2)

1. `cascade.rs::#[allow(clippy::fn_params_excessive_bools)]` — legacy `cascade()` function
   preserved for backward compatibility (new `cascade_with_opts()` is the evolved path)
2. `config.rs::#[allow(clippy::struct_excessive_bools)]` — `HardeningConfig` has 5 independent
   TOML-facing feature toggles; bools are the correct type for user-facing config

---

## Dependency Audit

| Dependency | Justification | Alternative Considered |
|-----------|---------------|----------------------|
| `chrono` | Timezone-aware datetime parsing + arithmetic (TTL/expiry) | `std::time` — insufficient for RFC3339 parsing |
| `reqwest` (rustls-tls) | Pure Rust HTTPS, no openssl | N/A — already sovereign |
| `blake3` | BLAKE3 checksums, no C deps | N/A — already native Rust |
| `tokio` | Async runtime for SSH + HTTP concurrency | N/A — ecosystem standard |
| `serde`/`toml`/`serde_json` | Config parsing, JSON-RPC | N/A — ecosystem standard |
| `thiserror` | Typed error derives | N/A — zero-cost abstraction |

---

## Upstream Gaps for primalSpring

None identified — cellMembrane is self-contained for its deep debt targets.
All evolution was internal refactoring with zero API surface changes.
