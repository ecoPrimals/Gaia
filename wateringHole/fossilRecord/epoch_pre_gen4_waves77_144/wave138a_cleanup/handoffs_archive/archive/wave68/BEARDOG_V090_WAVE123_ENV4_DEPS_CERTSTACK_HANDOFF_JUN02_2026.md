# bearDog v0.9.0 — Wave 123 Handoff
## Env Migration Wave 4, Dependency Evolution, Cert Stack Upgrade
**Date:** Jun 2, 2026
**Commit:** `2307e5373`
**Gate:** southGate

---

## 1. Env Key Centralization — Wave 4 (~200 strings)

Migrated raw env var strings across 20 production files, adding ~200 new constants to `env_keys.rs`.

### New constant categories
- **XDG / paths** — `ENV_XDG_RUNTIME_DIR`, `ENV_HOME`, `ENV_CACHE_DIR`
- **Discovery / registry** — `ENV_CONSUL_HTTP_ADDR`, `ENV_DISCOVERY_HOST`, unified config keys
- **Bootstrap / testing / AI training** — timeout, benchmark, and training configuration
- **Provider / monitoring / HSM** — performance, retention, batch, operational config
- **Production resources** — production-profile and resource-pool keys
- **Mobile HSM** — Android (`ENV_ANDROID_*`) and iOS (`ENV_IOS_*`, `ENV_HAS_*`) device detection
- **Capabilities / IPC** — self-knowledge flags, legacy socket names

### Files migrated (20)
`beardog-types`: config_impls, performance, defaults, monitoring/core, system constants, bootstrap, operational_config, testing, training, infrastructure, hsm/config, production/resources
`beardog-tunnel`: android_strongbox/mod, safe_android_provider, ios_secure_enclave/capability
`beardog-core`: primal_self_knowledge, ecosystem_listener/env, universal_discovery/types
`beardog-ipc`: neural_registration, isomorphic

---

## 2. Security: rustls-pemfile Removal (P0 Resolved)

Replaced unmaintained `rustls-pemfile` (RUSTSEC-2025-0134) with `rustls-pki-types` `PemObject` API.

| File | Migration |
|------|-----------|
| `acme/client.rs` | `certs()` → `CertificateDer::pem_slice_iter()` |
| `acme/hot_reload.rs` | `certs()` + `read_all()` → `CertificateDer::pem_slice_iter()` + `PrivateKeyDer::from_pem_slice()` |
| `tunnel/tcp_ipc/tls.rs` | `certs()` + `read_all()` → `CertificateDer::pem_file_iter()` + `PrivateKeyDer::from_pem_file()` |

`rustls-pki-types 1.14.1` now resolves as direct dep; `rustls-pemfile` removed from lockfile.

---

## 3. Cert Stack Upgrade

| Dep | Old | New | Impact |
|-----|-----|-----|--------|
| `x509-parser` | 0.16.0 | **0.18.1** | Resolves transitive `thiserror` 1.x from asn1-rs chain |
| `rcgen` | 0.13.2 | **0.14.8** | Compatible with x509-parser 0.18 |

No source code changes required — both upgrades were API-compatible. `beardog-acme` x509-parser unified to `{ workspace = true }`.

---

## 4. Dependency Analysis Summary (read-only)

Full analysis completed across all workspace dependencies. Key findings beyond what was fixed:

| Priority | Item | Status |
|----------|------|--------|
| P0 | `rustls-pemfile` unmaintained | **Resolved this wave** |
| P0 | `rsa` Marvin timing (RUSTSEC-2023-0071) | Acknowledged in deny.toml; no upstream fix; Ed25519/X25519 primary |
| P1 | `mdns-sd` 0.11 → 0.20 (9 minor versions behind) | Planned — API review needed |
| P1 | `tokio features = ["full"]` workspace-wide | Planned — per-crate feature trimming |
| P2 | `dashmap` 5 → 6, `toml` 0.8 → 1.x, `hkdf`/`pbkdf2` 0.12 → 0.13 | Queued |
| P2 | `dirs` + `directories` overlap | Consolidation candidate |
| P3 | `criterion` 0.5 → 0.8, `bcrypt`/`scrypt` patch bumps | Low urgency |

---

## 5. Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt` | ✓ clean |
| `cargo clippy -- -D warnings` | ✓ zero warnings |
| `cargo test` | ✓ 1159 passed, 0 failed |

---

## Cumulative Waves 120-123 Progress

| Metric | Count |
|--------|-------|
| Env vars centralized | ~373 across 4 waves |
| Raw env string sites remaining | ~250-350 (mostly beardog-types secondary files) |
| Dependencies evolved | `rcgen` added, `rustls-pemfile` removed, `x509-parser`+`rcgen` bumped, 3 unused pruned |
| Production stubs resolved | ACME CSR, Android honesty, quantum stubs |
| Test files restructured | 2 monoliths → 20 focused modules |
| Security advisories addressed | RUSTSEC-2025-0134 resolved |
