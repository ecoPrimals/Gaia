<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# coralReef Wave 157h — Deep Debt Audit + Rust 2024 Idiom Evolution

**Date**: Aug 10, 2026
**Primal**: coralReef
**Wave**: 157h
**Commit**: `bcd6c82c`

---

## Changes

### 1. `"health"` Method Wired in JSON-RPC Dispatch

`handle_health_standard()` existed but was dead code — the `"health"` method was in the
`method_gate.rs` public allowlist but had no dispatch handler in `newline_jsonrpc.rs`.
Now wired. 19 IPC methods live (was 18). `#[allow(dead_code)]` removed from the handler.

### 2. `#[allow]` → `#[expect]` Batch Migration (Rust 2024 Idiom)

7 safe conversions in `coral-reef` and `primal-rpc-client` where lints fire reliably:

| File | Lint |
|------|------|
| `ptx_emit/macros.rs` | `unused_macros` |
| `ptx_emit/types.rs` (2×) | `dead_code` on struct fields |
| `ptx_emit/subgroup.rs` | `clippy::too_many_arguments` |
| `amd/isa_generated/mod.rs` | `dead_code` on module |
| `primal-rpc-client/transport.rs` | `dead_code` on enum variant |
| `method_gate.rs` | `deprecated` on legacy env key read |

Items in `coralreef-core` retain `#[allow]` because dead_code status varies with
`--all-features` (e2e/tarpc feature gates change which items are considered live).
Reason strings improved on all remaining `#[allow]`s.

### 3. Deep Codebase Audit — Verified Clean

| Category | Status |
|----------|--------|
| `.unwrap()` in production | **Zero** — all `.expect("reason")` or `Result` propagation |
| Hardcoded primal names | **Zero** — `BEARDOG_SOCKET` is env-var-based, not primal routing |
| Hand-written files >800 LOC | **Zero** — 3 approaching (795, 770, 759), split candidates identified |
| `todo!()`/`unimplemented!()` in prod | **Zero** |
| EVOLUTION markers | **9** — 1 resolvable now (SM32 `.s` peephole), 3 partially, 5 deferred |
| Coverage gaps flagged | **All false positives** — SM75/SM80 GPR hazards, spiller, and generate_order already have comprehensive `_tests.rs` modules |

---

## Impact on Ecosystem

- **All primals**: `"health"` method now returns standard alive/version/uptime response —
  mesh health monitoring can use bare `"health"` (not just `"health.check"`).
- **No breaking changes**: Wire-compatible, backward-compatible.

## Tests

3,963 passed, 4 ignored, 0 failures (with `--all-features`).
`cargo clippy --all-features -- -D warnings`: zero warnings.
