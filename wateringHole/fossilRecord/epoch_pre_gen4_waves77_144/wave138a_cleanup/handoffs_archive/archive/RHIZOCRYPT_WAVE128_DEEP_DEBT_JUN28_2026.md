# rhizoCrypt — Wave 128 Deep Debt Evolution

**Date**: Jun 28, 2026
**Version**: v0.14.17
**Commit**: `f58ea03`
**From**: eastGate overwatch

---

## Deliverables

### Coverage expansion (1,825 → 1,866 tests, +41)

- **method_gate.rs** (+10 tests, ~87% → ~98%): Mock signing provider TCP server for `verify_with_provider` success path, transport error, invalid response, discovery failed fallback, cache TTL hit. Sync verify with/without Tokio runtime. `CallerContext::verify_token_async`. End-to-end gate with scoped claims and failed verification.
- **uds.rs** (+12 tests, ~85% → ~92%): Capability symlink create/remove/replace lifecycle, foreign-target skip, directory-as-symlink error. BTSP production mode serve with/without family seed. Connection rejection. Length-prefixed handshake success. EOF edge cases. Negotiate invalid client nonce fallback.
- **lib.rs service** (+19 tests, ~79% → ~89%): `resolve_bind_addr` production/dev defaults. Invalid host, host override TCP, BTSP family ID, transport endpoint env, default UDS path. TCP bind conflict → `ServiceError::Rpc`. Discovery register success/failure/rejection. UDS + TCP graceful shutdown via SIGINT/SIGTERM. Manifest publish failure (non-fatal). `run_client` invalid address, connection failure, health/sessions/metrics operations.

### CI coverage gate

- Wired `cargo-llvm-cov --fail-under-lines 90` into `.github/workflows/ci.yml`
- Added `llvm-tools-preview` to CI toolchain

### Clippy 1.94 compliance (5 fixes)

- `byte_str`: `&[b'X']` → `b"X"`
- `items_after_statements`: moved `use` before statements
- `expect_used`: added `clippy::expect_used` to `neural_api` test module
- `redundant_clone`: eliminated `sock_clone`
- `err_expect` + `cast_possible_wrap`: idiomatic fixes

### Adapter-agnostic messaging (Wave 120 gap)

- `connection.rs`: replaced `SongbirdConfig::with_address()` in error message with generic "discovery config via `with_address()`"

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,866 |
| Coverage | 93.7% lines |
| `.rs` files | 199 |
| Lines | ~60,921 |
| Max production file | 757 LOC (`method_gate.rs`) |
| Clippy | 0 warnings |
| `cargo doc` | 0 warnings |
| `cargo deny` | Clean |

## Gate Checks

- `cargo fmt --check` — pass
- `cargo clippy --workspace --all-features --tests -- -D warnings` — 0 warnings
- `RUSTDOCFLAGS="-D warnings" cargo doc` — 0 warnings
- `cargo test --workspace --all-features` — 1,866 pass, 0 fail
- `cargo deny check bans` — clean

## Remaining Deferred

| Item | Priority | Notes |
|------|----------|-------|
| JH-11 Ed25519 CapabilityVerifier | P1 | PresenceVerifier fallback remains; mock provider tests exercise the path |
| axum 0.7 → 0.8 | P3 | Breaking migration, schedule as dedicated wave |
| redb 2.x → 4.x | P3 | File format migration |
| hmac/sha2/hkdf 0.13 | P3 | Coupled RustCrypto bump |
