# bearDog v0.9.0 -- Wave 129 Handoff: grapheneGate Keystore Design + Pure-Rust Crypto Horizon

**Date**: Jun 2, 2026
**Wave**: 129 (Wave 71 Response)
**Author**: southGate (autonomous)
**Status**: COMPLETE

## Summary

Implemented the grapheneGate keystore architecture design for Pixel 8a (GrapheneOS, Titan M2). The codebase now has a clean transport-trait boundary with an explicit `AndroidKeymaster` variant ready for Phase 2 hardware wiring. Also documented the pure-Rust crypto horizon in `deny.toml`.

## Changes

### grapheneGate Keystore Design

**Architecture**: The `KeystoreTransport` trait in `android_transports.rs` remains the clean injection point. Three transport backends now exist:

| Variant | Platform | Hardware | Production |
|---------|----------|----------|------------|
| `Stub(MemoryKeystoreTransport)` | Non-Android | No | No |
| `AndroidJni(MemoryKeystoreTransport)` | Android dev | No | No |
| `AndroidKeymaster` | Android prod | **Yes** | **Yes** (Phase 2) |

**Rollout path**: Set `BEARDOG_KEYSTORE_BACKEND=keymaster` to activate hardware transport. Default remains in-memory mock with explicit warning.

**Device detection**:
- `AndroidDeviceInfo::pixel_8a()` — akita / Tensor G3 / Titan M2 / API 35
- `detect()` reads `ANDROID_MODEL` env var, branches to Pixel 8a when detected
- `safe_device_detection.rs` falls back to env vars instead of hardcoded values
- `detect_pixel_generation()` recognizes "Pixel 8a"

**Mobile setup**:
- `create_pixel8a_graphene_config()` (renamed from pixel8) — StrongBox-first, attestation enabled, GrapheneOS flags documented

### Pure-Rust Crypto Horizon (P3)

Documented in `deny.toml`:
- **Already pure-Rust**: ed25519-dalek, x25519-dalek, chacha20poly1305, blake3, argon2, hkdf, sha2, hmac, aes-gcm, rand
- **Remaining C (via aws-lc-rs)**: TLS handshake (rustls), CSR (rcgen), certificate verification (webpki)
- **Tracking**: rustls-rustcrypto maturity, p256+x509-cert as rcgen replacement

### Deep Debt Status

| Metric | Value |
|--------|-------|
| `todo!()` / `unimplemented!()` | 0 in production |
| Files >800L | 1 (beardog-acme/client.rs at 859L) |
| Inline env var strings | 0 (BEARDOG_* complete) |
| `.unwrap()` in prod | 326 (tracking baseline) |
| `anyhow` in excluded crate | 1 (crates/beardog/) |

## Quality Gates

- `cargo fmt` -- clean
- `cargo clippy --workspace -- -D warnings` -- clean
- `cargo test --workspace` -- **14,988 passed, 0 failed, 132 ignored**

## Coordination

- **S4 auth (P0)**: ironGate 7-day gate ACTIVE (Jun 2-9). No code changes needed. Monitoring.
- **grapheneGate Phase 2**: Wire real Keymaster JNI/Binder transport. Blocked on Android NDK build + device testing.
- **grapheneGate beacon test**: Requires keystore design (this wave) + Songbird virtual relay (shipped Wave 70).

## Next Steps (Phase 2 -- grapheneGate hardware wiring)

1. Implement `KeystoreTransport` for Android Keymaster via JNI or keystore2 Binder IPC
2. Wire `KeyGenParameterSpec` with `.setIsStrongBoxBacked(true)` for Titan M2
3. Implement `AttestationTransport` for key attestation certificate chain
4. Test on Pixel 8a with `BEARDOG_KEYSTORE_BACKEND=keymaster`
5. Consolidate `beardog-security/android_strongbox/` with `beardog-tunnel/android_strongbox/`
