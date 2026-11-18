# loamSpine — Wave 157g: G72 Dependency Pandemic

**Date**: August 10, 2026  
**Primal**: loamSpine  
**Wave**: 157g  
**Commit**: `0d9459e`

---

## Summary

loamSpine's G72 dependency pandemic audit is complete. Two dependencies excised/consolidated, crypto stack unified, tokio features verified lean.

---

## Changes

### Tier 1: Dead Dep Removal

| Dep | Action | Impact |
|-----|--------|--------|
| `url` (direct) | **REMOVED** — single `Url::parse().port()` replaced with manual parse | Eliminates `url` + entire ICU chain (`icu_collections`, `icu_normalizer`, `icu_properties`, `idna`, `idna_adapter`) from default `loam-spine-core` build. Still available transitively when `discovery-http` enables `ureq`. |
| `chacha20poly1305` | **UPGRADED** 0.10 → 0.11 | Eliminates duplicate `cpufeatures` (v0.2+v0.3→v0.3), duplicate `crypto-common` (v0.1+v0.2→v0.2). `Nonce::from_slice` deprecation fixed. |

### Tier 1: Feature Audit

| Feature | Status | Detail |
|---------|--------|--------|
| `tokio` features | **ALREADY LEAN** | 8 specific features (`macros`, `rt`, `rt-multi-thread`, `net`, `io-util`, `sync`, `time`, `signal`). NOT `["full"]`. |
| `tokio::sync` vs `std::sync` | **CORRECT** | All 6 `tokio::sync::RwLock` usages hold locks across `.await` — `std::sync` would deadlock. |
| Dead workspace deps | **ZERO** | All workspace entries have live consumers. |

### Tier 2: Version Alignment

| Stack | Before | After |
|-------|--------|-------|
| `cpufeatures` | v0.2.17 + v0.3.0 | **v0.3.0 only** |
| `crypto-common` | v0.1.7 + v0.2.2 | **v0.2.2 only** |
| `rand_core` | v0.6 + v0.9 + v0.10 | v0.6 + v0.9 + v0.10 (transitive — tarpc/proptest/our crypto) |

### Remaining Duplicates (unfixable without upstream)

| Crate | Versions | Source |
|-------|----------|--------|
| `getrandom` | v0.2, v0.3, v0.4 | tarpc transitive, proptest transitive, our direct |
| `rand` | v0.8, v0.9 | tarpc, proptest |
| `syn` | v2, v3 | clap v4 uses syn v3, all other derives use syn v2 |

---

## Test Results

| Metric | Value |
|--------|-------|
| Tests | **1,820** (unchanged) |
| Unique deps (default) | **197** |
| Clippy | PASS (zero warnings) |
| Fmt | PASS |
| Doc | PASS |
