# projectFOUNDATION — Wave 157a Deep Debt & Evolution AAR

**Date**: 2026-08-08
**Gate**: ironGate
**Author**: ironGate code team (automated session)
**Wave**: 157a
**Scope**: Deep debt resolution, dependency evolution, mock isolation, hardcoding elimination

---

## Summary

Systematic deep-debt pass across projectFOUNDATION's 7-crate Rust workspace.
Applied the ecosystem code quality standards: modern idiomatic Rust, zero unsafe
in production, dependency minimization, capability-based patterns, mock isolation.

## Changes

### Dependencies Eliminated (2 removed)

| Dep | Usage | Replacement |
|-----|-------|-------------|
| `bytes` | `Bytes::from(vec)` in transport layer | `Vec<u8>` directly — `from_bytes()` takes `&[u8]` |
| `walkdir` | Single recursive directory scan | `std::fs::read_dir` + recursion (zero-dep) |

Remaining external deps (8): blake3, clap, serde/json, thiserror, tokio, toml, tracing, ureq.
All pure Rust. No C FFI. No build.rs.

### Hardcoding Evolved to Agnostic

| Item | Before | After |
|------|--------|-------|
| `urls.rs` | `pub const DOWNLOAD_BASE` / `FORGEJO_BASE` | Env-driven `download_base()` / `forgejo_base()` with `FOUNDATION_DOWNLOAD_BASE` / `FOUNDATION_FORGEJO_BASE` env vars |
| Gallery generator | Hardcoded `primals.eco/lab/spores/{slug}` | Derives URL from config's `download_base_url` |

### Mock Isolation

- `MockChain` + `ChainId::Mock` gated behind `#[cfg(any(test, feature = "test-support"))]`
- Production binary carries zero mock code
- Feature flag `test-support` available for downstream integration tests

### Clippy Clean

- Full `pedantic + nursery` lint pass across workspace + all targets
- Added SPDX header + `#[cfg_attr(test, allow(...))]` to `foundation-anchor`

## Audit Results (No Action Needed)

| Dimension | Finding |
|-----------|---------|
| Unsafe code | Zero in production. Test-only `env::set_var/remove_var` properly gated with `#[expect(unsafe_code)]` + `ENV_LOCK` mutex |
| `Result<_, String>` | Zero anywhere |
| `todo!()` / `unimplemented!()` / `unreachable!()` | Zero anywhere |
| `unwrap()` in production | Zero — all in test modules |
| Files >800L | None. Largest: 482L (323L production + 159L tests) |
| Hardcoded primal slugs | All production routing uses `config.resolve()`. String literals are test fixtures only |
| GitHub remotes | Zero. Both `origin` and `forgejo` point to `git.primals.eco` |
| Stale TODOs/FIXMEs | Zero across all .rs, .md, .toml files |

## Final Metrics

| Metric | Value |
|--------|-------|
| Crates | 7 |
| Tests | 254 |
| Lines | ~11.2k |
| Release binary | 3.2 MB (LTO thin, stripped) |
| Clippy warnings | 0 |
| External deps | 8 (all pure Rust) |
| Production unsafe | 0 |
| Production unwrap | 0 |

## Files Changed

- `Cargo.toml` — removed `bytes`, `walkdir` workspace deps
- `crates/foundation-ipc/Cargo.toml` — removed `bytes` dep
- `crates/foundation-ipc/src/transport.rs` — `Vec<u8>` replaces `Bytes`
- `crates/foundation-fetch/Cargo.toml` — removed `walkdir` dep
- `crates/foundation-fetch/src/registry.rs` — `std::fs` recursive walk
- `crates/foundation-publish/src/urls.rs` — env-driven URL resolution
- `crates/foundation-publish/src/gallery.rs` — consumes resolved URLs
- `crates/foundation-anchor/Cargo.toml` — added `test-support` feature
- `crates/foundation-anchor/src/lib.rs` — SPDX + test allow
- `crates/foundation-anchor/src/chain/mod.rs` — mock behind cfg gate
- `crates/foundation-anchor/src/receipt.rs` — `ChainId::Mock` behind cfg gate
- `deploy/README.md` — transitional status banner
- `README.md` — updated metrics (254 tests, 11.2k lines, dep changes)

## Upstream Gaps for Primal Teams

| Gap | Primal Team | Description |
|-----|-------------|-------------|
| Env var expansion in workload TOMLs | toadStool | Gap 8 from COMPOSITION_GAPS — still open |
| Data dependency declaration | toadStool / nestGate | Gap 4 — workloads can't declare data inputs |
| Hex string acceptance | loamSpine / rhizoCrypt | Gap 9 — byte arrays vs hex strings |
| sweetGrass TCP without BTSP | sweetGrass | Gap 10 — plain JSON-RPC over TCP |
| `anchor` CLI subcommand | foundation-anchor | Layer 5 design complete, needs BTC/ETH chain backends |

---

*Wave 157a — ironGate deep debt pass complete. 254 tests, zero warnings, zero debt markers.*
