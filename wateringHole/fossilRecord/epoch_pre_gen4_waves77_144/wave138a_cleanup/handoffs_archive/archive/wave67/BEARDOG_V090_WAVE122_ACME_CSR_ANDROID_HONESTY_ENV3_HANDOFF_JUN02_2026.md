# bearDog v0.9.0 — Wave 122 Handoff
## ACME CSR Evolution, Android Mock Honesty, Env Migration Wave 3
**Date:** Jun 2, 2026
**Commit:** `1780ff1d1`
**Gate:** southGate

---

## 1. ACME CSR — Proper PKCS#10 Generation (P0 Resolved)

The placeholder `build_csr()` that concatenated subject + NUL + signature bytes has been replaced with standards-compliant CSR generation via `rcgen 0.13`.

### Changes
- **Key pair**: ECDSA P-256 (broad ACME CA compatibility) — separate from Ed25519 account key
- **CSR format**: Proper PKCS#10 DER with CN + SAN extension for all configured domains
- **PEM export**: `cert_private_key_pem()` now produces real PKCS#8 via `key_pair.serialize_pem()`
- **Return type**: `build_csr()` now returns `(Vec<u8>, rcgen::KeyPair)` — CSR bytes and cert key pair
- **Test**: New `build_csr_produces_valid_pkcs10` test validates CSR parsing via `x509-parser`

### Dependencies
- Added `rcgen = { version = "0.13", default-features = false, features = ["ring", "pem"] }` to workspace

---

## 2. Android Keystore Mock Honesty (P0 Resolved)

`MemoryKeystoreTransport` no longer falsely claims hardware backing.

### Changes
- `KeystoreTransportBackend::is_hardware_backed()` — returns `false` for all stub/in-memory variants
- `AttestationTransportBackend::is_hardware_backed()` — same pattern for attestation
- `AndroidKeystore::new()` derives `AndroidDeviceCapabilities` from `transport.is_hardware_backed()`:
  - `strongbox_available` = `hardware_backed && config.strongbox_enabled`
  - `hardware_backed_keystore` = `hardware_backed`
  - `key_attestation_available` = `hardware_backed`
- `AndroidStrongBoxHsm::with_defaults()` — runtime `tracing::warn!` when StrongBox requested but transport isn't hardware-backed
- `hsm_key_provider.rs` — capabilities and `KeyHandle.hardware_backed` read actual transport state
- `manager_hsm.rs` — `get_key_info()` reports actual hardware backing

### Impact
Host/CI stubs correctly report `strongbox_available: false`. Android production also reports `false` until real JNI Keymaster is wired — honest degradation.

---

## 3. Env Key Centralization — Wave 3

Migrated ~130 raw env var strings across the highest-density files.

### New constants added (~120)
Categories: Network endpoints/ports/URLs, Database, Timeouts, Security/compliance, HSM/runtime, Identity

### Files migrated
| File | Strings migrated |
|------|-----------------|
| `network_discovery.rs` | ~40 |
| `domains/security/mod.rs` | ~32 |
| `network.rs` | ~25 |
| `runtime_config.rs` | ~19 |
| `self_discovery.rs` | ~13 |

---

## 4. Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt` | ✓ clean |
| `cargo clippy -- -D warnings` | ✓ zero warnings |
| `cargo test` | ✓ 1159 passed, 0 failed |

---

## Cumulative Wave 120-122 Progress

| Category | Wave 120 | Wave 121 | Wave 122 | Total |
|----------|----------|----------|----------|-------|
| Env vars centralized | 13 | ~30 | ~130 | ~173 |
| Dead code removed | deprecated re-exports | quantum stubs | — | ✓ |
| Stubs evolved | — | — | ACME CSR, Android honesty | 2 P0 resolved |
| Test files split | — | 2 monoliths → 20 files | — | ✓ |
| Dependencies | 3 pruned, `rcgen` added | — | — | net -2 |

## Remaining Debt

| Priority | Item | Est. sites |
|----------|------|-----------|
| P1 | Env migration wave 4: remaining `beardog-types` files | ~200-300 |
| P1 | Env migration wave 5: `beardog-tunnel` HSM/platform | ~50 |
| P2 | External dep analysis for Rust evolution | — |
| P2 | Proactive file size monitoring (730L files approaching threshold) | — |
