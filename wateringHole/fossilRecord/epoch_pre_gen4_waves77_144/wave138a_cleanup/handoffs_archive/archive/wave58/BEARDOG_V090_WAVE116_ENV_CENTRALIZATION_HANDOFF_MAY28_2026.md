# BearDog Wave 116 — Env Var Centralization Foundation

**Date**: May 28, 2026  
**Version**: 0.9.0  
**Wave**: 116 (response to primalSpring Wave 58)  
**Quality Gates**: `cargo fmt` clean, `cargo clippy -D warnings` clean, all tests passing

---

## Wave 58 Audit Items — bearDog Response

### Item 1: ~550 env sites / 130 files — enforce `zero_hardcoding.rs` pattern

**Investigation findings**: Actual scope is ~420+ hardcoded `env::var("BEARDOG_*")` calls across ~186 files. Only ~14 `ENV_*` constants existed before this wave. The `zero_hardcoding.rs` module centralizes behavior but not key name constants.

**Action taken — foundation layer**:

1. **Created `beardog_config::env_keys`** — 65 centralized `pub const ENV_*: &str` constants organized by domain:
   - Paths (3): config/data/log dirs
   - Network addresses (7): host/bind/external/multicast
   - Network hosts (6): client/discovery/database/redis/metrics
   - Network ports (8): API/discovery/admin/HTTPS/metrics/health/TCP-IPC/UPA
   - Network misc (4): max connections, discovery interval, admin
   - Port discovery (4): discovered ports, probe, timeout, exclusion
   - Monitoring (3): log level/format, tracing
   - Health checks (12): timeouts, thresholds, recovery
   - Timeouts (8): HSM/database/discovery/AI
   - Security (2): TLS version/mode
   - Crypto (4): RSA/EC/AES/hash
   - HSM (7): auto-detect, prefer-hardware, backend enables, connector
   - ACME (5): directory/email/domains/port/renewal

2. **Migrated `health.rs`** — 12 inline env reads → `env_keys::ENV_*` constants (highest-density canonical config file)

3. **Migrated `multi_transport_server.rs`** — TCP IPC port read → `env_keys::ENV_TCP_IPC_PORT`

**Remaining migration scope**: ~400+ sites across ~180 files. Pattern is established; migration can proceed incrementally by domain. Highest-ROI targets:
- `canonical/config/network_discovery.rs` (~35 sites)
- `canonical/config/domains/security/mod.rs` (~32 sites)
- `canonical/config/network.rs` (~25 sites)
- `canonical/config/runtime_config.rs` (~19 sites)
- `beardog-config/src/domains/*` (~90 sites, semi-centralized)

### Item 2: NC-3.5 — `auth.issue_session` scope for sporePrint

**Status: RESOLVED (Wave 108, May 20)**

`content.*` scope is already included in session tokens for all non-admin purposes:
- `jupyterhub`/`notebook`: `crypto.*`, `health.*`, `capabilities.*`, `identity.*`, **`content.*`**
- `desktop`: above + `secrets.*`
- `research`/default: `crypto.*`, `health.*`, `capabilities.*`, `identity.*`, **`content.*`**
- `admin`: `*` (wildcard)

The glob matcher at `scope_covers_method()` handles `content.*` → `content.put` matching correctly. Tests verify scope presence (`issue_session_jupyterhub_scopes`, `issue_session_desktop_scope`, `issue_session_default_purpose_includes_content_scope`).

**No further bearDog code changes needed.** Remaining integration is downstream: sporePrint/petalTongue calling `auth.issue_session` and passing tokens to NestGate `content.put`.

---

## Audit state

| Dimension | Status |
|-----------|--------|
| Env key constants | 65 centralized (foundation) |
| Env sites migrated | 13 / ~420+ (3%) |
| NC-3.5 content scope | Resolved (Wave 108) |
| Quality gates | All pass |
