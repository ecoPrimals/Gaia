# NestGate v0.5.0 — Session 99: Deep Debt Sweep

**Date**: 2026-06-08
**Primal**: nestGate
**Gate**: ironGate
**Session**: 99
**Tests**: 13,120 (+4 new, 0 failures, 0 clippy warnings)

## Summary

Comprehensive deep debt sweep targeting production stubs, dependency hygiene,
legacy coupling, and naming accuracy. All changes are backward-compatible.

## Changes

### Security Auth — Stubs → Real HMAC-SHA256

| Component | Before | After |
|-----------|--------|-------|
| `AuthTokenManager::validate_token_signature` | `!token.is_empty()` | HMAC-SHA256 verify against signing key |
| `AuthTokenManager::create_token` | UUID only | UUID payload + `.{hmac_hex}` suffix |
| `ZeroCostJwtProvider::verify_signature` | `!empty && secret[0] != 0` | HMAC-SHA256 verify |
| `ZeroCostJwtProvider::authenticate` | Returns `"jwt_token_{creds}"` | Returns HMAC-signed token |

4 new tests: tampered token rejection, wrong-key rejection, refresh re-signing, cross-provider isolation.

### Legacy Env Var Deprecation

| Env Var | Status | Migration Target |
|---------|--------|------------------|
| `BEARDOG_SOCKET` | `warn!` on use | `SECURITY_PROVIDER_SOCKET` or `SECURITY_SOCKET` |
| `BEARDOG_FAMILY_SEED` | `warn!` on use | `FAMILY_SEED` or `SECURITY_FAMILY_SEED` |
| `BIOMEOS_FAMILY_SEED` | `warn!` on use | `FAMILY_SEED` or `SECURITY_FAMILY_SEED` |

### Unused Dependency Removal

| Crate | Dependency | Reason |
|-------|-----------|--------|
| `nestgate-core` | `getrandom` | Zero usage in source (RNG via `rand` transitively) |
| `nestgate-canonical` | `etcetera` | Zero usage in source |
| `nestgate-platform` | `etcetera` | Zero usage in source |

### Migration Framework Validators

- `validate_required_fields`: checks `storage.default_backend` non-empty
- `validate_value_ranges`: checks `storage.enabled` is true
- `validate_source` / `analyze_source`: guard against empty `source_type`
- Fixed typo: `validatevalue_ranges` → `validate_value_ranges`
- Removed stale `#![expect(clippy::unnecessary_wraps)]`

### TLS Config Validation

`TlsSecurityConfig::validate()` now checks that `cert_path` and `key_path`
are non-empty when TLS is enabled (was: always `Ok(())`).

### Hardware Helper Naming

Renamed all `create_stub_*` → `snapshot_*` across 3 files. Functions already
read real procfs/sysfs data — names now reflect actual behavior.

## Audit Findings (No Action Required)

- **0 files > 800 lines** — previous refactoring addressed this
- **0 unsafe code** — 22/22 crate roots have `#![forbid(unsafe_code)]`
- **0 openssl/ring/native-tls** in dependency tree
- **`ai_first_example`** — already gated behind `#[cfg(any(test, feature = "dev-stubs"))]`
- **`discovery.capability.query`** — returns `[]` on error (honest "no providers found")
- **`notify` crate** — C binding for fsmonitor; isolatable but not urgent
- **`sysinfo` crate** — optional fallback; Linux uses procfs directly
