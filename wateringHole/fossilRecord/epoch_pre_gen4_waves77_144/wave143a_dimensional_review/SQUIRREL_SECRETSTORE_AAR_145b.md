# Squirrel SecretStore AAR — Wave 145b

**Date**: Jul 16, 2026 | **Wave**: 145b | **From**: squirrel team (eastGate)
**Type**: After Action Review — scope boundary check

---

## What We Did

Squirrel shipped `PlatformSecretStore` — a cross-platform credential storage
abstraction that auto-detects OS-appropriate file paths:

| OS | Path |
|----|------|
| Linux | `$XDG_DATA_HOME/squirrel/secrets.json` |
| Windows | `%APPDATA%\squirrel\secrets.json` |
| macOS | `~/Library/Application Support/squirrel/secrets.json` |
| Android | app-private file store |

The abstraction layer includes:
- `CredentialStorage::Platform` config variant
- `PlatformSecretStore` with `PlatformBackend` enum (extensible)
- `PlatformStoreInfo` metadata (backend name, OS encryption, hw-backed)
- `SecretStoreBackend::Platform` runtime dispatch via `from_config()`
- 6 new tests (7,177 total, 0 failures, clippy clean, Windows cross-compile green)

## What We Didn't Do (and Why)

Native OS credential store backends (Windows Credential Manager, Android
Keystore, macOS Keychain) were designed as extension points but **not
implemented**. Two blockers:

1. **`unsafe_code = "forbid"`**: Windows Credential Manager requires `unsafe`
   FFI calls (`CredWriteW`/`CredReadW` via `windows-sys`). Android Keystore
   requires JNI. Both violate the workspace safety posture.

2. **BearDog already owns this domain** (see below).

## Potential Overstep — BearDog Scope Review

**bearDog already has extensive HSM + credential infrastructure:**

```
beardog-tunnel/src/tunnel/hsm/
├── android_strongbox/          ← Android Keystore backend EXISTS
│   ├── core/
│   ├── safe_android_provider/
│   ├── safe_native_wrapper.rs
│   └── types.rs
├── software_hsm/               ← Software HSM with keystore
│   ├── keystore.rs
│   └── core/hsm_key_provider.rs
├── providers/
│   ├── android.rs              ← Android provider
│   └── registry.rs             ← Provider registry
├── hsm_key_provider_backend.rs
├── hsm_provider_backend.rs
└── manager/

beardog-tunnel/src/universal_hsm/providers/
├── android.rs                  ← Universal HSM Android backend
├── ios.rs
├── tpm.rs
├── software/
│   ├── keystore.rs
│   └── core.rs
└── real_implementation.rs

beardog-security/src/hsm/
├── android_strongbox/
│   ├── multi_credential_provider.rs
│   └── native_strongbox.rs
├── fido2/
│   └── multi_credential_provider/
└── mod.rs
```

Per `BEARDOG_SCOPE_AND_BOUNDARIES.md` v2.0:
- bearDog's PRIMARY SCOPE is "Security Provider"
- bearDog owns "Key management and HSM integration"
- HSM backends (Software, PKCS#11, StrongBox) are COMPLETE
- squirrel is explicitly listed under "AI/MCP Services (Squirrel's Domain)"

**Conclusion**: Native credential store backends (Android Keystore, Windows
Credential Manager, macOS Keychain) belong to bearDog. Squirrel's correct
path is `CredentialStorage::SecurityProvider` → bearDog IPC delegation.

## What Squirrel Should Own

Squirrel's `SecretStore` trait and `PlatformSecretStore` are valid as
**consumer-side local caches**. The layering should be:

```
Squirrel config                     Runtime
─────────────────────────────────────────────────
CredentialStorage::Memory        → InMemorySecretStore (volatile)
CredentialStorage::File{path}    → FileSecretStore (explicit path)
CredentialStorage::Platform      → PlatformSecretStore (OS-native path)
CredentialStorage::SecurityProvider → bearDog IPC (HSM-backed)
```

All four are valid squirrel-local backends. The first three handle local
caching and development. `SecurityProvider` delegates to bearDog for
production-grade HSM-backed credential storage.

## Action Items

| Item | Owner | Priority |
|------|-------|----------|
| Verify bearDog HSM backends are reachable via `SecurityProviderClient` RPC | squirrel + bearDog | P2 |
| Remove squirrel's "Android Keystore backend" and "Windows Credential Manager" from ecosystem blurb | overwatch | P1 |
| Update blurb: squirrel `SecretStore` COMPLETE (consumer-side); native backends are bearDog domain | overwatch | P1 |
| bearDog: confirm `HsmManager` exposes credential get/set/delete via JSON-RPC | bearDog team | P2 |

## Commit

`93d147bb` — `feat: PlatformSecretStore — cross-platform credential abstraction`

---

*Wave 145b: SecretStore abstraction shipped. Native credential backends are
bearDog's domain — squirrel delegates via SecurityProvider IPC. No scope
violation introduced; file-based PlatformSecretStore is valid consumer-side
local cache.*
