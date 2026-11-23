# SweetGrass — Wave 151b: BTSP ClientHello SHIPPED

**Date**: Jul 26, 2026  
**Wave**: 151b  
**Commit**: `1502b49`  
**Version**: v0.7.63  
**Status**: **SHIPPED**

---

## Summary

sweetGrass now implements the consumer-side BTSP 4-step handshake per the
songBird reference (`btsp_client.rs`). When `BEARDOG_UDS_REQUIRE_BTSP=1`,
the `CryptoDelegate` performs ClientHello authentication before delegating
`crypto.sign` requests to bearDog.

Compatible with sporeGate's deployed strict mode. Legacy plaintext fallback
when strict mode is inactive (backward compatible).

---

## What Shipped

### `btsp_client.rs` (new module)
- `ClientHello { protocol: "btsp", version: 1, client_ephemeral_pub }`
- `ServerHello` parsing (version, challenge, session_id)
- `ChallengeResponse { HMAC-SHA256(FAMILY_SEED, challenge), preferred_cipher }`
- `HandshakeComplete` parsing (cipher, session_id)
- `BtspClientError` enum (NoFamilySeed, Io, Rejected, Protocol, Hmac)
- `btsp_strict_mode_expected()` — checks `BEARDOG_UDS_REQUIRE_BTSP` or `BTSP_STRICT_MODE`
- `perform_client_handshake(&mut UnixStream)` — full 4-step handshake
- Family seed resolution: `FAMILY_SEED` → `BEARDOG_FAMILY_SEED` fallback

### `crypto_delegate.rs` (evolved)
- `call_jsonrpc` now performs BTSP handshake before JSON-RPC when strict mode active
- Zero API changes to consumers (`CryptoDelegate::sign` unchanged)

### Dependencies Added
- `hmac = "0.12"` — pure Rust HMAC
- `getrandom = "0.3"` — secure random for ephemeral keys

---

## Verification

```
cargo clippy --all-features --all-targets -- -D warnings   OK (0 warnings)
cargo test --all-features                                   OK (1,618 tests)
cargo check --target x86_64-pc-windows-gnu                  OK (0 warnings)
cargo fmt --all -- --check                                  OK
```

---

## Deployment

sweetGrass is ready for strict-mode gates. Set `FAMILY_SEED` and
`BEARDOG_UDS_REQUIRE_BTSP=1` to activate. No code changes needed by
consumers of `CryptoDelegate` — handshake is transparent.
