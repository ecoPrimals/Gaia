# Squirrel Credential Architecture — Guidance (Wave 145a)

**Date**: Jul 16, 2026 | **From**: eastGate overwatch
**To**: squirrel team
**Priority**: P1 — architectural boundary clarification

---

## What Shipped

squirrel Wave 144a delivered:
- `SecretStore` trait (get/set/delete/list_keys)
- `InMemorySecretStore` (volatile, dev/bootstrap)
- `FileSecretStore` (persistent JSON, base64, `0o600`)
- `PlatformSecretStore` (auto-detect OS path via `dirs` crate)
- `SecretStoreBackend` enum dispatch with `CredentialStorage::Platform` config
- `CredentialStorage::SecurityProvider` variant (delegates to bearDog via IPC)

## The Overstep

The trait design and file-based infrastructure are good — squirrel needs
local credential caching for MCP tokens when bearDog is unavailable.

**However**: squirrel's `PlatformSecretStore` doc comments describe a path
toward implementing native credential store backends (Windows Credential
Manager, Android Keystore, macOS Keychain). This is **bearDog's domain**.

bearDog is the HSM/credential primal. bearDog owns:
- Hardware-backed key storage (SoloKey, Android StrongBox, TPM)
- Platform-native credential APIs (Keystore, DPAPI, Keychain)
- Key derivation, rotation, and lifecycle
- BTSP authentication protocol

## Guidance

### 1. `SecurityProvider` is the primary path

When bearDog is running, squirrel MUST delegate credential operations to
bearDog via the `SecurityProvider` variant. squirrel's `SecretStore` is a
**cache** — bearDog is the **authority**.

### 2. `Platform` is the offline fallback

`PlatformSecretStore` with `FileSecretStore` backend is appropriate for:
- Bootstrap credentials before bearDog is available
- Non-sensitive config tokens (MCP session state, cache keys)
- Offline/disconnected operation

It is NOT appropriate for:
- Long-term secret storage
- HSM-grade credentials
- Cross-platform native credential store implementation

### 3. Do NOT implement native credential backends in squirrel

The `PlatformBackend` enum should NOT grow these variants:
```
// DO NOT add to squirrel:
WindowsCredentialManager(WindowsCredentialStore),
AndroidKeystore(AndroidKeystoreStore),
MacOSKeychain(KeychainStore),
```

These belong in bearDog. When bearDog ships Android Keystore / Windows
DPAPI backends, squirrel accesses them through the existing
`SecurityProvider` IPC path.

### 4. `dirs` crate is acceptable

The `dirs` dependency for XDG/AppData path resolution is fine — it's
lightweight and widely used. No action needed.

### 5. Rename the doc comments

Remove language suggesting squirrel will implement native credential
stores. The `PlatformSecretStore` extension points should say:

```
// Future: when bearDog ships native credential backends, squirrel
// can use them via the SecurityProvider IPC path. PlatformSecretStore
// remains a file-based fallback for offline/bootstrap scenarios.
```

---

## bearDog's Responsibilities (unchanged)

bearDog owns the native credential store evolution:
- HSM provider → Android Keystore backend (P2)
- HSM provider → Windows DPAPI backend (P2)
- Credential lifecycle management
- Key derivation and rotation

squirrel accesses bearDog's credential services via `SecurityProvider`
(IPC → `beardog_ipc::connect_transport`).

---

*The trait architecture is solid. The boundary just needs clarifying:
squirrel caches, bearDog stores.*
