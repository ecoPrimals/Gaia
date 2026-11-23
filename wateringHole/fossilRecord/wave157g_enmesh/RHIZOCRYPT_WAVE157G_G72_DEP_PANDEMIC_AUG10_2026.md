# rhizoCrypt — Wave 157g G72 Dependency Pandemic Tier 1

**Date**: Aug 10, 2026
**Wave**: 157g — Stadial Shift (G72 Dependency Pandemic)
**Primal**: rhizoCrypt v0.14.17

## Audit Summary

Systematic dependency audit across 3 workspace Cargo.toml files.

### Already Compliant

| Area | Status | Detail |
|------|--------|--------|
| tokio features | **CLEAN** | Explicit features since genesis: `["rt-multi-thread", "macros", "net", "sync", "time", "io-util", "signal", "fs"]`. No `"full"`. |
| tarpc features | **CLEAN** | `["serde-transport-bincode", "tcp", "unix"]`. No `"full"`. |
| Feature-gated optionals | **CLEAN** | redb, http-clients, live-clients all behind feature flags |
| cargo deny | **CLEAN** | advisories ok, bans ok, licenses ok, sources ok |

### Dead Dependency Found: `wiremock`

- **Crate**: `wiremock = "0.6"` in workspace + rhizo-crypt-core dev-deps
- **Usage**: 0 matches in 226 `.rs` files (searched `wiremock` across all crate sources)
- **Origin**: Likely added speculatively for HTTP mock testing during early development
- **Impact**: Single removal cascaded to **46 crates removed** (14.6% reduction)

### Removal Cascade

```
wiremock → assert-json-diff, deadpool, deadpool-runtime
wiremock → url → idna → idna_adapter
         → icu_collections, icu_locale_core, icu_normalizer, icu_properties
         → icu_normalizer_data, icu_properties_data
         → icu_provider, litemap, potential_utf, stable_deref_trait
         → tinystr, utf8_iter, writeable, yoke, yoke-derive
         → zerofrom, zerofrom-derive, zerotrie, zerovec, zerovec-derive
         → synstructure, displaydoc
wiremock → num_cpus (via deadpool)
indexmap → hashbrown 0.17.1 (duplicate resolved — now only 0.14.5)
h2 (no longer needed without wiremock's hyper usage)
```

### Duplicate Crate Versions — Status

| Duplicate | Cause | Tier |
|-----------|-------|------|
| ~~hashbrown 0.14 + 0.17~~ | ~~wiremock → h2 → indexmap~~ | **RESOLVED** |
| cpufeatures 0.2 + 0.3 | Crypto libs vs blake3 | Transitive, not actionable |
| getrandom 0.2 + 0.3 + 0.4 | rand 0.8 vs direct vs uuid/tempfile | Tier 2 (rand 0.8→0.9) |
| rand 0.8 + 0.9 | Direct dep (BTSP) vs proptest/tarpc transitive | Tier 2 (breaking API) |
| syn 2 + 3 | Proc-macro versions | Transitive, not actionable |

### Patch Alignment

`cargo update` bumped 6 crates: async-trait (0.1.91→0.1.92), cc (1.4.0→1.4.2), find-msvc-tools (0.1.9→0.1.10), thiserror (2.0.19→2.0.20), wasm-bindgen (0.2.126→0.2.127), web-sys (0.3.103→0.3.104).

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Unique dependencies | 316 | **270** |
| Dead deps | 1 (wiremock) | **0** |
| Duplicate crate pairs | 7 | **6** (hashbrown resolved) |
| cargo deny | clean | clean |
| tokio features | explicit (8) | explicit (8) |
| Tests | 1,835 | 1,835 (all pass) |

## Verification

```
cargo clippy --workspace --all-features -- -D warnings  # clean
cargo test --workspace --all-features                    # 1,835 pass, 0 fail
cargo fmt --check                                        # clean
cargo check --target x86_64-pc-windows-gnu               # clean
cargo deny check                                         # advisories ok, bans ok, licenses ok, sources ok
```

## Tier 2 Targets (future)

- `rand 0.8 → 0.9`: Would eliminate rand/rand_core/rand_chacha/getrandom 0.2 duplicates. Breaking API change (needs BTSP audit).
- `axum 0.7 → 0.8`: Ecosystem-wide Tier 2 item per G72 spec.
- `getrandom 0.3 → 0.4`: Would align with uuid/tempfile. Minor API diff.
