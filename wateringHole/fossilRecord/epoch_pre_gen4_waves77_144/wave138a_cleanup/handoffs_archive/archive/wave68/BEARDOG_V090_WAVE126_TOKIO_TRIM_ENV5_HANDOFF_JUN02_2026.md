# bearDog v0.9.0 — Wave 126 Handoff
## Tokio Feature Trimming + Env Migration Wave 5
**Date:** Jun 2, 2026
**Commit:** `99e0fe46a`
**Gate:** southGate

---

## 1. Tokio Feature Trimming

Replaced workspace `tokio = { features = ["full", "tracing"] }` with per-crate feature sets.

### Workspace default
```toml
tokio = { version = "1.35", default-features = false, features = ["tracing"] }
```

### Per-crate features (key crates)
| Crate | Features |
|-------|----------|
| beardog-cli | `rt`, `rt-multi-thread`, `macros`, `net`, `io-util`, `io-std` |
| beardog-tunnel | `rt`, `macros`, `net`, `io-util`, `sync`, `time`, `fs`, `signal` |
| beardog-acme | `rt`, `macros`, `net`, `io-util`, `sync`, `time` |
| beardog-core | `rt`, `macros`, `sync`, `time`, `net`, `io-util`, `fs`, `process` |
| beardog-security | `rt`, `macros`, `sync`, `time` |
| beardog-types | optional `sync`; dev: `rt`, `macros`, `sync` |
| Test-only libs | `rt`, `macros` |

### Impact
- `process`, `signal`, `io-std` no longer compiled into crates that don't use them
- Binary size and compile time reduced for leaf crates
- `rt-multi-thread` restricted to actual binary entrypoints only

---

## 2. Env Key Centralization — Wave 5 (~90 strings)

Added ~90 new constants to `env_keys.rs` covering:
- Runtime configuration (worker threads, batch sizes)
- Network bind/listen (ports, addresses, gRPC, WebSocket)
- Monitoring and alerting thresholds
- HSM audit, discovery, manager keys
- Provider registry and consolidated providers
- IPC/discovery sockets and dev overrides
- Kubernetes service discovery
- Vault and cloud auth detection
- Primal discovery and ZK bootstrap

### Files migrated
beardog-ipc (lib.rs, registry_client.rs), beardog-production (runtime.rs), beardog-tunnel (btsp_provider, HSM manager/audit/discovery, platform files), beardog-types (~15 canonical config files), beardog-core (~10 discovery/bootstrap/adapter files), beardog-config internal domains, beardog-adapters, beardog-acme storage

---

## 3. Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt` | ✓ clean |
| `cargo clippy -- -D warnings` | ✓ zero warnings |
| `cargo test` | ✓ 1159 passed, 0 failed |

---

## Cumulative Waves 120-126 Progress

| Metric | Total |
|--------|-------|
| Env vars centralized | ~463 across 6 waves |
| Dependencies evolved | ring eliminated, rustls-pemfile removed, x509-parser/rcgen bumped, 3 unused pruned, rcgen added |
| Production stubs resolved | ACME CSR (PKCS#10), Android mock honesty, quantum stubs removed |
| Test files restructured | 2 monoliths → 20 focused modules |
| Security advisories resolved | RUSTSEC-2025-0134 (rustls-pemfile) |
| Build optimization | tokio features trimmed to per-crate |
| Dead code/debris removed | disabled test, stale comments, false doc claims |
