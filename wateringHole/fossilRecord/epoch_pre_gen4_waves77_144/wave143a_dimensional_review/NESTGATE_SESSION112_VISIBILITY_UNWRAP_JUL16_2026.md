# NestGate Session 112 — Deep Debt: Visibility Tightening, unwrap_or, Infallible Nonce

**Date**: Jul 16, 2026 | **Wave**: 142b | **From**: nestGate team
**Commit**: `5af785a9` | **Session**: 112

---

## Changes

### Visibility tightening (nestgate-rpc)

Three internal-only modules narrowed from `pub` to `pub(crate)`:
- `btsp_client` — BTSP session management client (only `resolve_security_socket_path` used
  crate-internally via `btsp_server_handshake`)
- `btsp_phase3` — Encrypted frame negotiation (only used within server/connection modules)
- `primal_announce` — Self-registration with ecosystem coordinator (only used by IPC server)

The visibility change exposed that `BtspClient` and its impl methods are entirely dead code
within the crate — they're the forward-looking client surface for security primal integration.
Justified `#[expect(dead_code)]` attributes added.

### Infallible nonce

`generate_server_nonce()` return type simplified from `Result<[u8; 32]>` to `[u8; 32]`.
`rand::rng().fill_bytes()` is infallible — the `Result` wrapper was unnecessary overhead
and forced callers to `?` or `.expect()` on an operation that cannot fail.

### `unwrap_or_else(|| String::from(...))` → `.into()`

31 conversions across 18 files. Idiomatic Rust: `.unwrap_or_else(|| "literal".into())`
is clearer and matches the `.into()` convention used throughout the codebase.

---

## Verification

| Check | Result |
|-------|--------|
| `cargo test --workspace` | 3,790 passed, 73 ignored, 1 pre-existing |
| `cargo clippy --workspace -- -D warnings` | 0 warnings |
| `cargo check --target x86_64-pc-windows-gnu` | PASS |

## Remaining deep debt

| Priority | Target | Notes |
|----------|--------|-------|
| P0 | `map_err` + `format!()` patterns (~264 sites) | Needs error helper infrastructure first |
| P1 | `json_rpc_handler.rs` `Result<_, String>` (17 sites) | Typed JSON-RPC error enum |
| P2 | `pub` → `pub(crate)` in nestgate-api (183 candidates) | Needs cross-crate import audit |
| P3 | Manual `impl Display` on label enums (17 sites) | `strum::Display` candidates |
