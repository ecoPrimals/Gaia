# BearDog v0.9.0 — Wave 119: S4 Auth Config (Wave 67 Response)

**Date**: Jun 1, 2026
**Commit**: `5e6b5a5e6` (bearDog main)
**Owner**: southGate
**Priority**: P0 — Glacial critical path

---

## Summary

Wave 67 identified **bearDog S4 auth config** as P0: "ensure BTSP auth services
are configured so ironGate can begin the formal 7-day shadow validation." This
wave resolves all bearDog-side blockers.

## Changes

### 1. `SO_PEERCRED` Extraction (auth.peer_info)

Previously, `auth.peer_info` always returned `available: false` because the code
incorrectly documented `peer_cred()` as unstable (`peer_credentials_unix_socket`
feature gate). It has been stable since **Rust 1.75** (Dec 2023).

- `PlatformStream` trait extended with `peer_credentials()` method (default `None`)
- `UnixPlatformStream`: extracts `uid`/`pid` via `tokio::net::UnixStream::peer_cred()`
- `AndroidPlatformStream`: same implementation
- `PrefixedStream`: delegates to inner stream
- All 4 connection handlers now populate `CallerContext` with live peer credentials
- `auth.peer_info` returns `{ "available": true, "uid": <u32>, "pid": <u32> }`

### 2. `BEARDOG_AUTH_MODE` Centralization

- Added `ENV_AUTH_MODE` to `beardog-config/src/env_keys.rs`
- Replaced inline `"BEARDOG_AUTH_MODE"` string in `method_gate.rs`
- Added `ENV_BTSP_BIRDSONG_KEY_LABEL`, `ENV_BTSP_LINEAGE_ROOT_PREFIX`,
  `ENV_BTSP_LINEAGE_MAX_DEPTH` to centralized env_keys
- Migrated `domains/btsp.rs` from local duplicate constants to `env_keys::*`

### 3. S4 Shadow Deployment Documentation

- `ENVIRONMENT_VARIABLES.md`: documented `BEARDOG_AUTH_MODE` in Security & Trust
- Added "S4 Shadow Validation" example configuration section
- Updated summary table to include `BEARDOG_AUTH_MODE`

## S4 Auth Readiness for ironGate

| Requirement | Status |
|-------------|--------|
| Auth IPC surface (`auth.verify_ionic`, `auth.public_key`, `auth.issue_session`, `auth.peer_info`) | **COMPLETE** |
| BTSP transport auth (production mode) | **COMPLETE** — env-gated via `FAMILY_ID` + `FAMILY_SEED` |
| `MethodGate` enforcement | **COMPLETE** — opt-in via `BEARDOG_AUTH_MODE=enforced` |
| `SO_PEERCRED` peer credential extraction | **COMPLETE** — live uid/pid returned by `auth.peer_info` |
| Socket discoverable by ironGate | **COMPLETE** — `BEARDOG_SOCKET`, capability symlinks, port 9100 |
| S4 shadow deployment documented | **COMPLETE** — `ENVIRONMENT_VARIABLES.md` |
| Forgejo `auth.token.*` | **N/A** — cellMembrane responsibility |
| JupyterHub `BearDogAuthenticator` | **N/A** — ironGate responsibility |

### Minimum ironGate config

```bash
export FAMILY_ID=<family>
export FAMILY_SEED=<32+-byte-seed>
export BEARDOG_SOCKET=/run/beardog/beardog.sock
export BEARDOG_TCP_IPC_PORT=9100
export BEARDOG_AUTH_MODE=enforced
./beardog server
```

ironGate validates by calling:
- `auth.verify_ionic` — Ed25519 token verification
- `auth.public_key` — cache verifying key for offline validation
- `auth.issue_session` — issue tokens with `purpose: "jupyterhub"`
- `auth.peer_info` — peer credential introspection

## Quality Gates

- `cargo fmt` — PASS
- `cargo clippy -- -D warnings` — PASS
- `cargo test --workspace` — PASS (all tests, 0 failures)

## Wave 67 bearDog Status: RESOLVED

S4 is the last sovereignty shadow blocking stadial entry.
bearDog auth services are now configured and documented for ironGate
to begin the formal 7-day shadow validation.
