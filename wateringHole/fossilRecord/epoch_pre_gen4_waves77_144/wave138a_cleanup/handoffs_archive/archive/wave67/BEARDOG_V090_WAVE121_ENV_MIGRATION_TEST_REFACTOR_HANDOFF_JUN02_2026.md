# bearDog v0.9.0 — Wave 121 Handoff
## Env Key Migration Wave 2, Quantum Stub Removal, Test Refactoring
**Date:** Jun 2, 2026
**Commit:** `3c1c2083d`
**Gate:** southGate

---

## 1. Environment Key Centralization — Wave 2

Migrated ~30 raw env var string literals to `beardog_config::env_keys::` constants across 5 core files.

### New constants added to `env_keys.rs`

| Constant | Value | Category |
|----------|-------|----------|
| `ENV_FAMILY_ID` | `FAMILY_ID` | Identity |
| `ENV_FAMILY_ID_PREFIXED` | `BEARDOG_FAMILY_ID` | Identity |
| `ENV_FAMILY_SEED` | `FAMILY_SEED` | Identity |
| `ENV_FAMILY_SEED_PREFIXED` | `BEARDOG_FAMILY_SEED` | Identity |
| `ENV_NODE_ID` | `NODE_ID` | Identity |
| `ENV_NODE_ID_PREFIXED` | `BEARDOG_NODE_ID` | Identity |
| `ENV_PRIMAL_NAME` | `PRIMAL_NAME` | Identity |
| `ENV_PRIMAL_NAME_PREFIXED` | `BEARDOG_PRIMAL_NAME` | Identity |
| `ENV_PRIMAL_TYPE` | `PRIMAL_TYPE` | Identity |
| `ENV_PRIMAL_TYPE_PREFIXED` | `BEARDOG_PRIMAL_TYPE` | Identity |
| `ENV_ORCHESTRATOR_ID` | `ORCHESTRATOR_ID` | Identity |
| `ENV_HOSTNAME` | `HOSTNAME` | Identity |
| `ENV_UID` / `ENV_EUID` | `UID` / `EUID` | Identity |
| `ENV_SOCKET` | `BEARDOG_SOCKET` | Socket/IPC |
| `ENV_SOCKET_TMP_DIR` | `BEARDOG_SOCKET_TMP_DIR` | Socket/IPC |
| `ENV_IPC_CAPABILITY_STEMS` | `BEARDOG_IPC_CAPABILITY_STEMS` | Socket/IPC |
| `ENV_PIPE` | `BEARDOG_PIPE` | Socket/IPC |
| `ENV_NEURAL_REGISTRATION_INSTANCE` | `BEARDOG_NEURAL_REGISTRATION_INSTANCE` | Socket/IPC |
| `ENV_NEURAL_API_SOCKET_NAME` | `BEARDOG_NEURAL_API_SOCKET_NAME` | Socket/IPC |
| `ENV_NEURAL_API_SOCKET_LEGACY` | `NEURALS_SOCKET` | Socket/IPC |
| `ENV_BIOMEOS_INSECURE` | `BIOMEOS_INSECURE` | Ecosystem |
| `ENV_BIOMEOS_FAMILY` | `BIOMEOS_FAMILY` | Ecosystem |
| `ENV_BIOMEOS_SOCKET_PATH` | `BIOMEOS_SOCKET_PATH` | Ecosystem |
| `ENV_BIOMEOS_SOCKET_DIR` | `BIOMEOS_SOCKET_DIR` | Ecosystem |
| `ENV_BIOMEOS_PIPE_DIR` | `BIOMEOS_PIPE_DIR` | Ecosystem |

### Files updated

| File | Raw strings removed |
|------|-------------------|
| `btsp_handshake/mod.rs` | `FAMILY_ID`, `BEARDOG_FAMILY_ID`, `FAMILY_SEED`, `BEARDOG_FAMILY_SEED`, `BIOMEOS_INSECURE` |
| `unix_socket_ipc/handlers/utils.rs` | `BEARDOG_FAMILY_ID`, `BEARDOG_NODE_ID`, `BEARDOG_PRIMAL_NAME`, `HOSTNAME`, etc. |
| `modes/server.rs` | `BEARDOG_PRIMAL_TYPE`, `BEARDOG_FAMILY_SEED`, neural registration params |
| `socket_config.rs` | `BEARDOG_FAMILY_ID`, `BEARDOG_NODE_ID`, `BEARDOG_SOCKET`, `BEARDOG_SOCKET_TMP_DIR`, `BEARDOG_IPC_CAPABILITY_STEMS` |
| `platform/mod.rs` | `BEARDOG_PRIMAL_NAME`, `BEARDOG_PIPE`, `BIOMEOS_PIPE_DIR` |
| `neural_registration.rs` | `NEURAL_API_SOCKET`, `NEURALS_SOCKET`, `neural-api.sock` filename |

---

## 2. Neural API Socket Abstraction

`discover_neural_api_socket()` now reads the socket filename from `BEARDOG_NEURAL_API_SOCKET_NAME` (default: `neural-api.sock`), eliminating the hardcoded filename across all discovery tiers. Legacy `NEURALS_SOCKET` env var also centralized.

---

## 3. Quantum Discovery Stub Removal

Removed dead code from `quantum_discovery.rs`:
- `create_quantum_entanglement()` — stub returning `not_implemented`
- `quantum_anneal_selection()` — stub returning `not_implemented`
- `OptimizationCriterion` enum — only used by removed stubs

No callers existed. The module retains its working `quantum_discover_capabilities()` path and types.

---

## 4. Test File Refactoring

Split two monolithic test files (1746 lines total) into focused module directories:

### `crypto_operations_comprehensive_tests/` (was 866L → 8 files)
`mod.rs` · `helpers.rs` · `ed25519.rs` · `aes_gcm.rs` · `chacha20.rs` · `blake3.rs` · `key_derivation.rs` · `key_rotation.rs`

### `security_edge_cases/` (was 880L → 12 files)
`mod.rs` · `helpers.rs` · `encryption.rs` · `key_management.rs` · `hashing.rs` · `constant_time.rs` · `secure_zero.rs` · `auth.rs` · `signature.rs` · `random.rs` · `config.rs` · `error_recovery.rs`

Module declarations in `tests/mod.rs` unchanged — Rust resolves directory modules automatically.

---

## 5. Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt` | ✓ clean |
| `cargo clippy -- -D warnings` | ✓ zero warnings |
| `cargo test` | ✓ 1159 passed, 0 failed |

---

## Remaining Deep Debt

| Priority | Item | Status |
|----------|------|--------|
| P0 | Android `MemoryKeystoreTransport` production mock | Pending — requires JNI bridge design |
| P0 | ACME CSR placeholder in `client.rs` | Pending — needs proper X.509 CSR generation |
| P1 | Remaining raw env strings (estimated 10-15 across less-critical paths) | Pending |
| P1 | Large file analysis (any new >800L files post-split) | Pending |
| P2 | Evaluate external dependency evolution to pure Rust | Pending |
