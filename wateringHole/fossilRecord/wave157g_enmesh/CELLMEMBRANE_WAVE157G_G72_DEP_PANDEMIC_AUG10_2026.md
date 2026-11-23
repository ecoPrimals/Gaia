# cellMembrane — Wave 157g G72 Dependency Pandemic + Socket Dedup

**Date:** 2026-08-10
**Commit:** `1f5ef19`
**Wave:** 157g (STADIAL SHIFT)
**Gate:** eastGate overwatch

---

## What Changed

### 1. G72 Dependency Pandemic — Tier 1 Excision

cellMembrane already lean (93 transitive deps, 0 dead direct deps). Three optimizations:

**`time/macros` feature removed:**
- `time = { features = ["formatting", "parsing", "macros", "local-offset"] }` → remove `"macros"`
- Zero usage of `time::offset!`, `time::date!`, or `time::time!` compile-time macros
- Eliminates `time-macros` proc-macro dependency entirely
- 93 → 92 transitive deps

**`rt-multi-thread` split to dev-deps:**
- Production binary uses `#[tokio::main(flavor = "current_thread")]`
- 68 `#[tokio::test]` use the default multi-thread runtime (test-only need)
- Split: production `tokio` drops `rt-multi-thread`, dev-deps re-adds it
- Release binary no longer links the multi-thread scheduler

**`serde_json` promoted to workspace dep:**
- Used in both `cellmembrane-types` (52 prod sites) and `membrane-shadow` (446 prod sites)
- Now managed via `[workspace.dependencies]` instead of duplicate version pins

### 2. Socket Name Deduplication

**3 copies of `signer_socket_name()`** consolidated:
- `impulse/primal.rs` (original, had wrong `-default.sock` suffix)
- `dispatch/sign_dispatch.rs` (correct `socket_filename()`)
- `plasmid/signing_crypto.rs` (correct `socket_filename()`)

Single canonical in `impulse/primal.rs` with `pub(crate)` visibility. Others delegate to it.

**`-default.sock` vestigial pattern purged:**
- No gate has `-default.sock` files on disk (verified on eastGate)
- `relay_socket_name()` and `signer_socket_name()` now both use `socket_filename()` producing `{binary}.sock`
- Tests updated to assert canonical naming

### 3. Cargo Update

| Crate | Before | After |
|-------|--------|-------|
| blake3 | 1.8.5 | 1.8.6 |
| thiserror | 2.0.19 | 2.0.20 |
| aho-corasick | 1.1.4 | 1.1.5 |
| cc | 1.4.0 | 1.4.2 |
| regex-automata | 0.4.16 | 0.4.18 |
| hybrid-array | 0.4.13 | 0.4.14 |

---

## G72 Audit Summary (cellMembrane posture)

| Metric | Value |
|--------|-------|
| Direct deps (types) | 4 (serde, serde_json, thiserror, toml) |
| Direct deps (shadow) | 14 (+ 3 optional behind `http` feature) |
| Transitive deps | **92** (down from 93) |
| Dead deps | **0** |
| Tokio features | 7 production + 1 dev-only (`rt-multi-thread`) |
| `tokio["full"]` | **Never used** — explicit feature list since inception |
| Unused features | **0** (after `time/macros` removal) |
| Version drift | **0** (all at latest compatible with MSRV 1.85) |

cellMembrane is already lean. No Tier 2 (HTTP→capability.call) or Tier 3 (sourDough dep validator) work needed — no external HTTP client in production deps (reqwest already purged).

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 1,353 | **1,353** |
| Clippy warnings | 0 | **0** |
| Transitive deps | 93 | **92** |
| Duplicated functions | 3 (`signer_socket_name`) | **1** |
| Vestigial `-default.sock` | 2 functions | **0** |
