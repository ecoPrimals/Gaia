# BearDog Wave 145 — Pure Rust Crypto + Crypto Dedup + Debris Cleanup

**Date**: Jun 9, 2026  
**Version**: 0.9.0  
**Wave**: 145  
**Quality Gates**: `cargo fmt` clean, `cargo clippy --workspace -D warnings` clean, full workspace `cargo check` clean, 1013 beardog-security tests passing, 1302 beardog-core tests passing

---

## P1: Pure Rust Crypto Completion

### Problem

`aws-lc-rs` (C FFI via rustls) and `rcgen` (C-linked CSR) blocked cross-compilation to musl targets and violated ecoBin zero-C-dependency mandate.

### Changes

| Component | Before | After |
|-----------|--------|-------|
| TLS `CryptoProvider` | `aws-lc-rs` (C) | `rustls-rustcrypto` (Pure Rust) |
| CSR generation | `rcgen` (C-linked) | `p256` + `x509-cert` (Pure Rust) |
| `deny.toml` bans | `ring` only | 19 C-crypto crates: `ring`, `aws-lc-rs`, `aws-lc-sys`, `openssl`, `openssl-sys`, `boring`, `native-tls`, `rcgen`, `bindgen`, etc. |
| Advisory ignores | 1 (RSA Marvin) | 2 (RSA Marvin + `paste` unmaintained) |
| Allowed licenses | Standard permissive | + `ISC`, `CDLA-Permissive-2.0` (RustCrypto deps) |
| Allowed git sources | none | `rustls-rustcrypto` (pre-release) |

### Files changed

- `Cargo.toml` (root) — workspace deps updated
- `crates/beardog-acme/Cargo.toml` — `rcgen` → `p256` + `x509-cert` + `rustls-rustcrypto`
- `crates/beardog-acme/src/client/config.rs` — `rustls_rustcrypto::provider()` replaces `aws_lc_rs::default_provider()`
- `crates/beardog-acme/src/client/issuance.rs` — CSR generation rewritten with `p256::ecdsa::SigningKey` + `x509_cert::builder::RequestBuilder`
- `deny.toml` — comprehensive C-crypto ban list, skip list for RustCrypto RC version splits

---

## P2: Crypto Wrapper Dedup

### Problem

5 parallel crypto wrapper stacks had overlapping implementations of the same primitives (Ed25519, AES-GCM, HMAC-SHA256, ChaCha20-Poly1305).

### Audit findings

| Stack | Location | Role | Production callers |
|-------|----------|------|--------------------|
| `BearDogCrypto` | `beardog-security/src/crypto_utils.rs` | Sync utility struct | `safe_ffi`, `encryption.rs` |
| `algorithms::*` | `beardog-core/src/crypto_service/algorithms/` | Async service primitives | Tunnel IPC handlers |
| `RustCryptoProvider` | `beardog-tunnel/hsm/crypto/providers/` | `UniversalCryptoProvider` | HSM encrypt/decrypt/sign/verify |
| `SoftwareHsmCryptoProvider` | `beardog-tunnel/hsm/software_hsm/crypto_providers/` | `CryptoProvider<KeyType>` | HSM key gen/derivation |
| `GeneticCryptoProvider` | `beardog-tunnel/hsm/software_hsm/crypto_providers/` | `CryptoProvider<KeyType>` + lineage | IPC genetic handlers |

### Consolidation decision

**Option A chosen**: BearDog stays as orchestration layer over RustCrypto primitives. Dedup at wrapper level, not primitive level.

### Changes

| Change | Detail |
|--------|--------|
| ChaCha20-Poly1305 consolidated | `encryption.rs` local functions → `BearDogCrypto::encrypt_chacha20_poly1305` / `decrypt_chacha20_poly1305` |
| `lib.rs` free functions delegated | `compute_sha256_hash` → `BearDogCrypto::sha256_hash_bytes`, `generate_secure_random_bytes` → `BearDogCrypto::generate_secure_random`, `constant_time_compare` → `BearDogCrypto::constant_time_compare`, `secure_zero_memory` → `BearDogCrypto::zero_memory` |
| `SoftwareHsmCryptoProvider` renamed | Resolved naming collision with universal `RustCryptoProvider` |
| KDF gaps filled | `derive_pbkdf2`, `derive_argon2`, `derive_scrypt` implemented on `UniversalCryptoProvider` |
| ECDSA P-384 implemented | `sign_ecdsa_p384` / `verify_ecdsa_p384` on `UniversalCryptoProvider` |

### Dead code removed (4 files, ~37KB from prior wave + 15 files, ~157KB this wave)

#### Crypto orphans (prior wave)

| File | Size | Reason |
|------|------|--------|
| `crypto_utils/unified.rs` | 20KB | Abandoned consolidation draft; never `mod`'d |
| `crypto_service/service.rs` | 2KB | Superseded by `implementation/` |
| `crypto_service/config.rs` | 2KB | Superseded by `types.rs` |
| `tests/crypto_edge_cases_tests.rs` | 13KB | Never wired in test tree; calls non-existent API |

#### General debris (this wave)

| File | Size | Reason |
|------|------|--------|
| `zero_knowledge_bootstrap/infant_patterns.rs` | 13KB | Never `mod`'d; comment says "planned for future" |
| `zero_knowledge_bootstrap/performance_optimization.rs` | 23KB | Never `mod`'d |
| `zero_knowledge_bootstrap/infant_patterns_tests.rs` | 11KB | Tests orphaned parent |
| `zero_knowledge_bootstrap/performance_optimization_tests.rs` | 16KB | Tests orphaned parent |
| `zero_knowledge_bootstrap/capability_registry_additional_tests.rs` | 11KB | Never `mod`'d |
| `software_hsm/implementations.rs` | 10KB | Superseded by `core/` split |
| `workflows/policy.rs` | 8KB | Corrupted; references deleted `canonical` module |
| `workflows/tests.rs` | 11KB | Never `mod`'d |
| `utils/config_utils.rs` | 8KB | Corrupted syntax; never `mod`'d |
| `utils/env_utils.rs` | 9KB | Superseded by `env_config` module |
| `utils/error_patterns.rs` | 5KB | Broken async syntax; never `mod`'d |
| `utils/safe_memory.rs` | 10KB | Superseded by `safe_memory_enhanced` |
| `utils/sovereign_crypto_utils.rs` | 8KB | Never `mod`'d |
| `zero_copy/string_constants.rs` | 4KB | Corrupted braces; never `mod`'d |
| `genetics/spawning/evolution.rs` | 10KB | Corrupted imports; never `mod`'d |

---

## P3: Doc Sync

### Stale references corrected

| Doc | Before | After |
|-----|--------|-------|
| `STATUS.md` | "TLS backend is `aws-lc-rs`" | "TLS backend is Pure Rust `rustls-rustcrypto`" |
| `SECURITY.md` | "`aws-lc-rs` via `rustls`" | "Pure Rust `rustls-rustcrypto` CryptoProvider" |
| `SECURITY.md` | "`rcgen` CSR generation" | "`p256` + `x509-cert`" |
| `ROADMAP.md` | "`aws-lc-rs` via `rustls` is C FFI; tracking `rustls-rustcrypto` for Phase 2" | "100% Pure Rust crypto achieved" |
| `ACME spec` | "`rcgen` — CSR generation" | "`p256` + `x509-cert`" |

---

## Ecosystem Position Update

BearDog is now a **100% Pure Rust cryptographic service provider** with:
- Zero C dependencies in the entire dependency graph (verified by `cargo deny check bans`)
- 19 C-crypto crates explicitly banned with documented rationale
- Full cross-compilation capability (musl, ARM, WASM targets unblocked)
- `BearDogCrypto` as the canonical single-source-of-truth for cryptographic primitives
- RustCrypto suite as underlying primitive layer (MIT/Apache-2.0 compatible with AGPL-3.0-or-later)

### Wider Rust ecosystem value

BearDog demonstrates a validated pattern for any Rust project seeking C-free crypto:
1. `rustls` + `rustls-rustcrypto` for TLS (replaces `aws-lc-rs`/`ring`)
2. `p256` + `x509-cert` for CSR/cert operations (replaces `rcgen`)
3. `cargo deny` ban list as purity contract enforcement
4. Single canonical wrapper (`BearDogCrypto`) consolidating primitives for consistent API

---

## Validation Pattern: Pure Rust Crypto Purity Gate

### For adoption across ecoPrimals

Any primal can enforce C-free crypto by adding to their `deny.toml`:

```toml
[[bans.deny]]
wrappers = []
name = "aws-lc-rs"
# ... (full ban list available in beardog/deny.toml)
```

### Validation command

```bash
cargo deny check bans 2>&1 | grep -c "DENIED"
# Expected: 0
```

### Upstream action items for primalSpring

1. **Audit other primals** for residual `aws-lc-rs` / `ring` / `rcgen` usage
2. **Propagate `deny.toml` ban list** to ecosystem standard in wateringHole
3. **Review `rustls-rustcrypto` RC status** — when it publishes to crates.io, switch from git dep to version dep
4. **Gap check**: BearDog `ios_secure_enclave/` directory exists but is not compiled (future iOS port scaffold) — needs wiring when iOS becomes active target

---

## Quality Summary

| Metric | Value |
|--------|-------|
| `cargo check --workspace` | Clean (0 errors) |
| `cargo clippy --workspace -D warnings` | 0 warnings |
| `cargo fmt --all` | Clean |
| `cargo deny check` | All 4 checks pass |
| beardog-security tests | 1013 passing |
| beardog-core tests | 1302 passing (1 pre-existing failure in unrelated `universal_compute_client`) |
| Dead code removed | ~194KB (19 orphaned files) |
| Docs updated | 5 files |

---

## Addendum: Wave 146 — Debris Sweep (Jun 10, 2026)

Follow-up pass after eastGate cascade pull. Fresh audit found 9 additional orphaned `.rs` files
missed in Wave 145 (~66KB, ~2,000 LOC):

- `beardog-utils/src/zero_copy/` — 4 files (`safe.rs`, `buffer_management.rs`,
  `advanced_patterns.rs`, `advanced_optimization.rs`) never declared in `mod.rs`
- `beardog-genetics/src/genetics/spawning/` — 2 files (`lineage.rs`, `workflows.rs`)
  with broken syntax, never declared in `mod.rs`
- `beardog-core/src/zero_knowledge_bootstrap/` — 3 test files (`tests.rs`, `tests/mod.rs`,
  `tests/discovery_comprehensive_tests.rs`) superseded by wired `zero_knowledge_bootstrap_tests.rs`

Also fixed: 7 root docs synced to ground-truth metrics (226 methods, 14,974+ tests, 2,125 `.rs`
files), 4 broken `docs/sessions/` links repaired in source code, `PRIMAL_CONTRACTS.md` method
count updated, CHANGELOG Waves 145+146 entries added.

**Cumulative debris removed (Waves 145+146)**: 28 orphaned files, ~260KB dead code.
