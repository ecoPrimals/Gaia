# BearDog Technical Stack & Plans (BTSP)

**Version**: 0.9.0 (Wave 104 — Deep Debt + FIDO2 IPC)
**Last Updated**: May 15, 2026
**Status**: Production Ready

---

## Purpose

BearDog is the **sovereign genetic cryptography primal** for the ecoPrimals ecosystem. It provides:

1. **Cryptographic Operations** — Ed25519, X25519, ChaCha20-Poly1305, AES-GCM, BLAKE3, SHA-256/384/512, SHA3-256, HMAC, HKDF, TLS key derivation, Tor onion/ntor/cell crypto, post-quantum (ML-KEM, ML-DSA, SPHINCS+)
2. **Identity & Lineage** — Family seed management, lineage key derivation, genetic entropy, trust evaluation
3. **Hardware Security** — HSM abstraction (RustCrypto software, PKCS#11, Android StrongBox, TPM Phase 2)
4. **Secret Storage** — Encrypted secrets with family-scoped ChaCha20-Poly1305 keys
5. **Dark Forest Beacon** — Zero metadata leakage discovery protocol

All primals delegate crypto to BearDog via the **Tower Atomic Pattern** (JSON-RPC 2.0 over NDJSON), keeping a single auditable crypto codebase across the ecosystem.

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Rust (edition 2024, MSRV 1.93.0, `rust-toolchain.toml` pinned) |
| **Crypto** | RustCrypto suite (100% pure Rust, zero C dependencies) |
| **IPC** | JSON-RPC 2.0 over NDJSON (Unix sockets / TCP / named pipes / abstract sockets) |
| **Optional IPC** | tarpc (feature-gated, Rust-to-Rust high-performance) |
| **Serialization** | serde_json (wire), postcard (binary), serde_yaml (config) |
| **Binary** | UniBin architecture — single `beardog` binary with subcommands |
| **License** | AGPL-3.0-or-later (SPDX headers on all source files) |

---

## Architecture

### Crate Organization (29 workspace crates)

**Core Runtime**: `beardog` (binary), `beardog-core`, `beardog-tunnel`, `beardog-ipc`, `beardog-cli`, `beardog-client`

**Type System**: `beardog-types`, `beardog-config`, `beardog-errors`, `beardog-traits`

**Security**: `beardog-security`, `beardog-genetics`, `beardog-hid`, `beardog-auth`, `beardog-threat`

**Infrastructure**: `beardog-monitoring`, `beardog-workflows`, `beardog-adapters`, `beardog-capabilities`, `beardog-discovery`, `beardog-utils`

**Deployment**: `beardog-production`, `beardog-installer`, `beardog-compliance`, `beardog-node-registry`, `beardog-tower-atomic`, `beardog-integration-tests`

**Excluded from workspace**: `beardog-integration` (HTTP overstep), `beardog-deploy` (tooling exception)

### Wire Protocol

All transports use **NDJSON** (newline-delimited JSON-RPC 2.0). Each request is a single JSON object terminated by `\n`. Idle connections time out after 30 seconds.

```
┌─────────────┐                    ┌─────────────┐
│  Any Primal │ ←─ JSON-RPC ────→ │  BearDog    │
│ (Protocol)  │  NDJSON framing    │  (Crypto)   │
└─────────────┘                    └─────────────┘
     Zero crypto code                 126 JSON-RPC methods
```

### JSON-RPC Method Domains (126 methods)

```
crypto.*       - Hash, sign, verify, encrypt, decrypt, key exchange
tls.*          - TLS 1.2/1.3 key derivation and handshake
tor.*          - Onion identity, ntor, cell crypto
genetic.*      - Lineage keys, beacon, challenge-response
secrets.*      - Store, retrieve, list, delete encrypted secrets
relay.*        - Lineage-gated relay authorization (coordinated punch)
beacon.*       - Dark Forest beacon generation, encryption, meeting exchange
btsp.*         - Secure tunnel config + session handshake-as-a-service
quantum.*      - Post-quantum cryptographic operations
```

Introspection: `discover_capabilities`, `primal.info`, `rpc.methods`, `capabilities.list`, `identity.get`

Canonical names use `domain.operation` form. Legacy flat aliases (`ping`, `capabilities`, `health`, `identity`) are deprecated.

### HSM Abstraction

```
HsmKeyProvider (beardog-traits::hsm)
├── RustSoftwareHsm         (RustCrypto, always available)
├── AndroidStrongBoxHsm     (JNI bridge, cfg(target_os = "android"))
├── Pkcs11Provider           (Phase 2: pure Rust pkcs11 crate)
└── TpmProvider              (Phase 2: pure Rust tss-esapi)

HsmProviderRegistry → discover() → select(PreferHardware | RequireHardware | SoftwareOnly)
```

### Multi-Family Isolation

```bash
./beardog server --family-id alpha   # beardog-alpha.sock, own key material
./beardog server --family-id bravo   # beardog-bravo.sock, fully isolated
```

---

## Platform Support

| Platform | Transport | Status |
|----------|-----------|--------|
| Linux (x86_64, ARM64) | Unix sockets | Production |
| macOS (Intel, M-series) | Unix sockets | Production |
| Android (ARM64) | Abstract sockets + TCP | Production |
| Windows (x86_64, ARM64) | Named pipes + TCP | Ready |
| iOS (ARM64) | TCP | Ready |

---

## Quality Metrics

| Metric | Value |
|--------|-------|
| **Build** | Clean, 0 errors |
| **Clippy** | 0 warnings (pedantic + nursery + all cast lints + `doc_markdown` + `missing_errors_doc` + unwrap/expect warn) |
| **Missing Docs** | 0 warnings |
| **Pure Rust** | 100% — zero C dependencies |
| **Unsafe Code** | 0 production blocks (`forbid(unsafe_code)` workspace-wide) |
| **Format** | `cargo fmt` clean |
| **Tests** | 14,940+ (concurrent; 35 `#[serial]` in `beardog-production`) |
| **Coverage** | 90.51% line (llvm-cov workspace) |
| **cargo deny** | 4/4 pass (1 advisory ignore: RSA Marvin, 15 transitive version-skips) |
| **License** | AGPL-3.0-or-later (SPDX headers on all .rs files) |
| **Files > 1000 LOC** | 0 (production) |
| **TODO/FIXME** | 0 |

---

## Security Posture

- **Zero unsafe code** — `forbid(unsafe_code)` workspace-wide
- **Zero panic paths** — No `unwrap()` in production; `expect()` only on documented invariants
- **Constant-time** — `subtle::ConstantTimeEq` for secrets
- **Zeroize** — Sensitive memory cleared on drop
- **Typed errors** — `BearDogError` throughout; no `Box<dyn Error>` in public APIs
- **Self-knowledge only** — BearDog discovers peers at runtime via capability registry; no hardcoded primal names
- **Dependency injection** — Pure `Default`, `from_env()` at boundaries

### Known Advisory

**RSA Timing Sidechannel (RUSTSEC-2023-0071)**: Acknowledged, monitoring for upstream fix. RSA operations use random blinding.

---

## Deployment

### Quick Start

```bash
# Build
cargo build --release

# Run (auto-detects platform transport)
./beardog server

# With family isolation
./beardog server --family-id alpha

# Custom socket path
./beardog server --socket /custom/path.sock

# TCP transport
./beardog server --listen 0.0.0.0:9900
```

### Binary Targets

| Binary | Purpose |
|--------|---------|
| `beardog` | Primary UniBin (server, client, key ops, doctor, capabilities) |
| `beardog-installer` | Tooling exception: deployment and validation on target devices |
| `deploy-pixel8` | Tooling exception: Android adb-based deployment helper |

### Docker

```bash
docker build -t beardog .
docker run -e PRIMAL_NAME=beardog beardog server
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `PRIMAL_NAME` | Primal identity | `beardog` |
| `FAMILY_ID` | Family identifier | (none) |
| `NODE_ID` | Node identifier | (random) |
| `BEARDOG_SOCKET` | Socket path override | auto-detected |
| `BEARDOG_PORT` | Listening port | OS-assigned |
| `BEARDOG_HSM_MODE` | HSM backend selection | `software` |

---

## Architectural Compliance

| Standard | Status |
|----------|--------|
| UniBin/ecoBin | Single binary, standalone identity fallback, cross-compilation ready |
| JSON-RPC 2.0 | Primary IPC with NDJSON framing and batch support |
| tarpc | Optional behind feature gate in `beardog-ipc` |
| Pure Rust | Zero C dependencies; `blake3` pure feature; ecoBin compliant |
| Self-Knowledge | Primals discover peers at runtime via capability registry |
| Zero Hardcoding | Named constants + env override + capability discovery |
| `forbid(unsafe_code)` | Workspace level + every crate `lib.rs` |
| Workspace Lints | Centralized clippy pedantic + nursery + all cast lints |
| AGPL-3.0-or-later | SPDX headers on all source files |

---

## Recent Evolution (April 2, 2026)

### Wave 28: Self-Knowledge, Error Typing, Hardcoding

- Removed deprecated `SongbirdClient` type alias; genericized cross-primal references
- `Box<dyn Error>` → `BearDogError` in AI hybrid intelligence public APIs
- Feature flag `advanced-nestgate` → `advanced-registry`

### Wave 27: License, Lint Migration, Deprecation

- License migrated from `AGPL-3.0-only` to `AGPL-3.0-or-later` across all files
- `#[allow()]` → `#[expect(reason)]` migration (49 non-test attributes)
- Legacy flat method aliases documented as deprecated

### Wave 26: Stub Completion, Dependency Alignment

- `handle_key_info` and client JSON-RPC dispatch evolved from stubs to real implementations
- Orphaned entropy modules compiled and fixed
- AI tree (11.9K LOC) feature-gated behind `ai` Cargo feature
- `deny.toml` skip-list reduced from 30 to 15

---

## Future Work

These are enhancements — nothing blocks production use.

- **Secret Storage Evolution** — Persistent NestGate-backed storage via capability discovery (pattern already implemented)
- **Graph Security Phase 2-3** — Public key infrastructure, signature verification chains
- **Semantic Method Naming Phase 3** — Generic `crypto.encrypt` + algorithm parameter (ecosystem coordination)
- **PKCS#11 / TPM Phase 2** — Full hardware crypto via pure Rust crates (`pkcs11`, `tss-esapi`)

---

**Status**: PRODUCTION READY
