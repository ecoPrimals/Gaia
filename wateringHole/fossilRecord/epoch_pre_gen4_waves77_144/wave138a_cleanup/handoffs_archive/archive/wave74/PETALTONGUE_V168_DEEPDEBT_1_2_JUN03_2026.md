# petalTongue Deep Debt Passes 1 & 2 — TRUE PRIMAL + Typed Errors + Idiom Sweep

**Date**: June 3, 2026
**Version**: v1.6.8 deep-debt
**Tests**: 6,217 passed, 0 failed
**Clippy**: 0 warnings (first-party)

## Deep Debt Pass 1: TRUE PRIMAL + Typed Errors

### TRUE PRIMAL Compliance

| Target | Before | After |
|--------|--------|-------|
| `capability_registry.toml` content owner | `nestgate` | `content-provider` |
| `capability_registry.toml` discovery owner | `songbird` | `discovery-service` |
| `nucleus.rs` viz labels | Hardcoded primal names (Squirrel, NestGate, BearDog, Songbird) | Capability labels (AI inference, Content storage, Cryptographic security, Network mesh) |
| `kderm.rs` topology nodes | `golgiBody-ext`, `peptidoglycan`, `flockGate` | `outer-proxy`, `membrane-wall`, `gate-user` |
| `--backend` CLI help | `"content-provider" / "nestgate"` | `"content-provider"` only |

### Typed Content Backend Errors

`ContentBackendError` thiserror enum replaces `Result<String, String>`:

| Variant | Source |
|---------|--------|
| `Connect` | `std::io::Error` (socket/TCP connect) |
| `Write` | `std::io::Error` (stream write) |
| `Serialize` | `serde_json::Error` |
| `Base64` | `base64::DecodeError` |
| `Protocol` | JSON-RPC protocol violations |

### Idiom Sweep (Pass 1)

220+ `.to_string()` → `.to_owned()` on string literals across:
`network.rs`, `shader_lineage.rs`, `gpu_compute_provider.rs`,
`demo_device_provider.rs`, `direct.rs` (audio), `socket.rs` (audio)

## Deep Debt Pass 2: AppError Evolution + Async Safety

### AppError Typed Sources

5 new `#[from]` conversions added, eliminating 11 `AppError::Other(format!())` sites:

| Variant | From | Eliminated Sites |
|---------|------|------------------|
| `Config` | `ConfigError` | `main.rs` config load |
| `Ipc` | `IpcServerError` | `server_mode.rs`, `live_mode.rs` |
| `AddrParse` | `std::net::AddrParseError` | `web_mode/mod.rs` bind parse |
| `Json` | `serde_json::Error` | `cli_mode/mod.rs` serialize |
| `Join` | `tokio::task::JoinError` | `cli_mode/gather.rs` try_join |

Plus: `web_mode/mod.rs` bind error, `web_mode/mod.rs` serve error now use `?`.

### Async-Safe File I/O

`content_direct.rs`: `std::fs::read_to_string` → `tokio::fs::read_to_string`
in both `content_direct_index` and `content_direct_fallback` handlers.

### Idiom Sweep (Pass 2)

220+ additional `.to_string()` → `.to_owned()` across 7 files:
`gather.rs`, `scenario/convert.rs`, `tutorial_mode.rs`, `trust.rs`,
`ai_adapter.rs`, `status_reporter.rs`, `jsonrpc_provider.rs`

Surgical replacements where non-literal `Display::to_string()` was present.

### Clippy Cleanup

- Removed unfulfilled `#[expect(clippy::too_many_lines)]` from `main()`
- Fixed `to_owned()` → `clone_into` in `status_reporter`

## Quality Gates

- `cargo fmt --check`: clean
- `cargo clippy --workspace --all-targets`: 0 warnings
- `cargo test --workspace`: 6,217 passed, 0 failed
- `unsafe_code = "forbid"` enforced across all 18 crates + UniBin

## For primalSpring Audit

- **Zero `AppError::Other`**: All `Other(format!())` patterns eliminated from
  production code. Remaining `Other` variant available for truly unexpected cases.
- **No `Result<_, String>`**: `ContentBackendError` was the last holdout.
- **Async safety**: No blocking `std::fs` calls remain in async handlers.
- **TRUE PRIMAL**: Zero hardcoded primal names in production code.
  Test fixtures and provenance comments preserved (properly gated).

## Upstream Gaps Identified

| Gap | Status | Notes |
|-----|--------|-------|
| `AppError::Other` still exists as variant | Low priority | Fallback for truly unexpected paths; all known sites evolved |
| `.to_string()` on `Display` types | Acceptable | Not string literals — `Display::to_string()` is idiomatic |
| Audio backend stubs | Feature-gated | `audio-direct`/`audio-socket` not in default features |
| `DemoDeviceProvider` | Feature-gated | Behind `#[cfg(feature = "mock")]` |
