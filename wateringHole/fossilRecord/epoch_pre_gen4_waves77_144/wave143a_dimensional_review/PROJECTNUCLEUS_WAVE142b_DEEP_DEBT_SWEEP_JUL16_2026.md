# projectNUCLEUS Wave 142b — Deep Debt Sweep Handoff

**Date**: 2026-07-16
**Gate**: ironGate
**HEAD**: `42e5816` (debt: eliminate C deps, typed errors, idiomatic casts)
**primalSpring**: v0.9.39 (`8df6b3f`, 167 scenarios)
**Tests**: 245 (darkforest 149, tunnelKeeper 49, nucleus-deploy 47)

## Summary

Deep debt evolution sweep across all 4 projectNUCLEUS crates. Focus: eliminate
C dependencies, replace stringly-typed errors with enums, modernize numeric
casts, reduce unnecessary allocations, and harden lint annotations.

## Changes

### C Dependency Elimination (tunnelKeeper)
- `reqwest` feature `rustls` → `rustls-no-provider`
- Explicit `rustls = { version = "0.23", features = ["ring", "std", "tls12"] }`
- `rustls::crypto::ring::default_provider().install_default().ok()` at startup
- `cargo tree -i aws-lc-sys` → empty (verified zero C TLS deps)

### Typed Error Evolution (nucleus-deploy)
- New `JsonRpcError` enum: `Connect`, `Serialize`, `Write`, `Read`, `Utf8`
- `jsonrpc_uds` returns `Result<String, JsonRpcError>` (was `Result<_, String>`)
- `DeployError` derives `#[from] JsonRpcError` for ergonomic conversion
- All `deploy_graph` call sites consume `Result` by value

### Numeric Cast Modernization
- `darkforest/check.rs`: 3 civil date `as` casts → `try_from().unwrap_or()`
- `darkforest/crypto/mod.rs`: `b as usize` → `usize::from(b)`
- `nucleus-deploy/provenance/mod.rs`: `as_millis() as u64` → `u64::try_from().unwrap_or(u64::MAX)`

### Clone Reduction
- `darkforest/main.rs`: `cli.suite.clone()` → `&str` reference
- `nucleus-deploy/spore/mod.rs`: owned `Vec<PathBuf>` iteration, `s.to_owned()`

### Lint Hardening
- `#[allow(clippy::*)]` → `#[expect(clippy::*, reason = "...")]` in summary.rs, verify.rs
- Stale `#[expect]` annotations removed after cast modernization
- `summary.rs` percentile index: explicit 3-lint `#[expect]` with justification

### Production Safety
- `darkforest/net.rs`: `TLS_CONFIG` returns `Option<Arc<ClientConfig>>` (was `expect()`)
- Fallible initialization propagated through `tls_stream` callers

### deny.toml Harmonization
- `CDLA-Permissive-2.0` added to nucleus-deploy + nucleus-primals
- `Unicode-3.0`, `Unicode-DFS-2016`, `Apache-2.0 WITH LLVM-exception` added to nucleus-primals
- `unsafe-libyaml` ban added to nucleus-primals
- tunnelKeeper comment corrected: "aws-lc-rs" → "ring backend"

## Upstream Gaps Found

None. All changes are local to projectNUCLEUS.

## Test Counts (verified)

| Crate | Tests | Change |
|-------|-------|--------|
| darkforest | 149 | — |
| tunnelKeeper | 49 | +1 (ring backend unlocked test) |
| nucleus-deploy | 47 | — |
| nucleus-primals | 0 | corrected from stale "12" in docs |
| **Total** | **245** | was 244 passing + 1 ignored |

`cargo clippy -D warnings` PASS, `cargo fmt` clean, `cargo deny check` PASS 4/4.
