# BearDog v0.9.0 — Wave 120: Deep Debt Cleanup

**Date**: Jun 2, 2026
**Commit**: `e1d96d09b` (bearDog main)
**Owner**: southGate

---

## Summary

Comprehensive deep debt pass across dependency hygiene, timeout hardcoding,
env var centralization, unsafe policy, and deprecated type cleanup.

## Changes

### 1. Unused Dependency Pruning

Removed 3 workspace dependencies with zero source references:

| Dependency | Crate | Reason |
|------------|-------|--------|
| `dotenvy` | beardog-config | Config reads env directly |
| `tokio-stream` | beardog-security | Not imported anywhere |
| `arrayref` | beardog-tunnel | Not imported anywhere |

### 2. Timeout Centralization

Replaced 5 hardcoded `Duration::from_secs(N)` constants with `LazyLock`-based
env-driven values (read once at first use):

| Constant | File | Env Key | Default |
|----------|------|---------|---------|
| `IPC_READ_TIMEOUT` | unix_socket_ipc/server.rs | `BEARDOG_READ_TIMEOUT_SECS` | 30s |
| `TCP_READ_TIMEOUT` | tcp_ipc/server.rs | `BEARDOG_READ_TIMEOUT_SECS` | 30s |
| `IPC_PEEK_TIMEOUT` | unix_socket_ipc/server.rs | `BEARDOG_HANDSHAKE_TIMEOUT_SECS` | 5s |
| `TCP_HANDSHAKE_DETECT_TIMEOUT` | tcp_ipc/server.rs | `BEARDOG_HANDSHAKE_TIMEOUT_SECS` | 5s |
| `BTSP_JSONLINE_READ_TIMEOUT` | btsp_handshake/handshake.rs | `BEARDOG_HANDSHAKE_TIMEOUT_SECS` | 30s |

### 3. Env Key Migration

Migrated 13 raw `"BEARDOG_*"` string literals to centralized `env_keys::ENV_*`:

- **beardog-acme**: 5 keys (DIRECTORY, DOMAINS, EMAIL, CHALLENGE_PORT, RENEWAL_DAYS)
- **beardog-cli**: 1 key (TLS_MODE)
- **beardog-tunnel/tls**: 2 keys (TLS_CERT_PATH, TLS_KEY_PATH)
- **beardog-tunnel/rate_limiter**: 3 keys (RATE_LIMIT_MAX_CONN, WINDOW_SECS, MAX_TOTAL)

Fixed ACME naming drift: `ENV_ACME_HTTP_PORT` → `ENV_ACME_CHALLENGE_PORT`,
`ENV_ACME_RENEWAL_HOURS` → `ENV_ACME_RENEWAL_DAYS`.

### 4. Unsafe Policy

Added `#![forbid(unsafe_code)]` to `beardog-cli/src/main.rs`.
All 29 library crates + 2 binary roots now forbid unsafe code.

### 5. Deprecated Type Cleanup

Removed stale `pub use` re-exports of deprecated `monitoring_unified` types
from `beardog-types/src/metrics.rs` and `health_status.rs`.

## Audit Findings (Not Addressed — Future Waves)

| Item | Priority | Notes |
|------|----------|-------|
| Android `MemoryKeystoreTransport` in prod | P0 | Requires JNI wiring for real Keymaster |
| ACME CSR not valid PKCS#10 DER | P0 | Needs `rcgen` integration |
| DNS-SD/K8s discovery return empty | P1 | Stub implementations |
| Ed448 handlers stubbed | P1 | Not announced; handlers return errors |
| ~130+ remaining raw env strings | P2 | Systematic migration ongoing |
| Windows/iOS platform stubs | P3 | Platform-specific |

## Quality Gates

- `cargo fmt` — PASS
- `cargo clippy -- -D warnings` — PASS
- `cargo test --workspace` — PASS (1 pre-existing env-dependent test skipped)
