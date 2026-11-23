# cellMembrane — riboCipher Mito-Tier + Dispatch SRP + Deep Debt Evolution

**Date:** 2026-06-13
**Wave:** 111
**Team:** cellMembrane (ironGate)
**Commit:** `35ad803`

---

## Summary

Complete implementation of the riboCipher Transport Signal Standard mito-tier,
SRP decomposition of the dispatch module, and modern Rust idiom evolution.

---

## Delivered

### 1. riboCipher Mito-Tier Complete

The riboCipher standard defines how primals declare their intended protocol over
IPC connections. cellMembrane now has a **fully operational mito-tier** (Tier 2):

- **HKDF-SHA256 key derivation**: `mito_key = HKDF(salt="ribocipher-v1", ikm=FAMILY_SEED, info="mito-signal")`
- **HMAC tag generation**: `tag = HMAC-SHA256(mito_key, [protocol_type])[0..4]`
- **Tag verification**: Reverse-lookup protocol type from a 4-byte tag
- **Wire format**: `[0xED, tag[0], tag[1], tag[2], tag[3]]` (5 bytes)
- **Environment integration**: Reads `FAMILY_SEED` (path to key file or inline)
- **Graceful fallback**: If no key material available, falls back to clear signal

All six UDS client functions prepend the signal before writing JSON-RPC requests.
Configuration via `[transport.ribocipher]` section in `membrane.toml`.

**15 tests** covering signal constants, HKDF derivation, tag roundtrip, protocol
distinctness, and configuration parsing.

### 2. Dispatch Module SRP Refactor

`dispatch/infra.rs` was 762 lines — a monolithic file handling 6 different domains.
Smart decomposition based on **local vs. remote** SRP boundary:

| Module | Lines | Responsibility |
|--------|-------|---------------|
| `infra.rs` | 264 | Remote VPS API: repo, mirror, service, token (Forgejo + SSH) |
| `gate.rs` | 518 | Local self-management: status, health, bootstrap, provision, audit |

The dispatch router (`mod.rs`) now routes `gate.*` and `health.audit` to the gate
module, keeping the VPS infrastructure concerns separate.

### 3. Modern Rust Idiom Evolution

- **Error propagation**: Removed 8 redundant `map_err(|e| Parse(e.to_string()))` calls
  on `serde_json` operations that have `#[from]` auto-conversion via thiserror
- **Shared constants**: `NEURAL_API_SOCKET_NAME` and `NEURAL_API_NAMESPACE` elevated
  from `bridge.rs` to `cellmembrane-types::service` for ecosystem-wide discovery
- **Edition 2024**: Codebase already uses `let-else`, `is_some_and`, and other modern patterns

### 4. External Dependency Analysis

| Dep | Justification | Verdict |
|-----|--------------|---------|
| `sha2` | Forgejo webhook HMAC-SHA256 (external protocol) + riboCipher mito-tier (ecosystem standard) | KEEP — protocol requirement |
| `hmac` | Same as sha2 | KEEP |
| `blake3` | Binary checksums, provenance verification | KEEP — primary hash |
| `reqwest` | Forgejo + Cloudflare + DigitalOcean APIs | KEEP — HTTP client |
| `tokio` | Async runtime, UDS, process, fs | KEEP — runtime |
| `chrono` | Timestamp formatting in freshness/cascade | KEEP — minimal |

No external dependencies are candidates for removal. All are justified by
external protocol requirements or core functionality.

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 384 | 391 |
| Clippy warnings | 0 | 0 |
| Unsafe code | 0 | 0 |
| Files > 800L (production) | 0 | 0 |
| `dispatch/infra.rs` | 762L | 264L |
| riboCipher coverage | clear-only | clear + mito + verify |

---

## For Upstream Teams

### bearDog / songBird / biomeOS / sweetGrass

riboCipher server-side detection should look for:
- **Clear (0xEC)**: Next byte is protocol type (1 byte total prefix = 2)
- **Mito (0xED)**: Next 4 bytes are HMAC tag, protocol inferred via brute-force over 8 known types
- **Nuclear (0xEE)**: Deferred — not yet specified

cellMembrane validates that mito tags generated with a shared `FAMILY_SEED` are
verifiable using `RiboCipherConfig::verify_mito_tag()`. This provides ecosystem-wide
interoperability testing for the standard.

### primalSpring / overwatch

The dispatch SRP refactor is a model for other primals with monolithic dispatch files.
SRP boundary: **local self-management** (gate.*) vs **remote infrastructure** (repo.*, mirror.*, service.*, token.*).

---

## Files Changed

```
crates/cellmembrane-types/src/service/mod.rs      (+6)    # NEURAL_API constants
crates/membrane-shadow/src/bridge.rs              (+4/-4) # Use shared constants
crates/membrane-shadow/src/caddy.rs               (-6)    # Modernized error propagation
crates/membrane-shadow/src/cloudflare.rs          (-10)   # Modernized error propagation
crates/membrane-shadow/src/dispatch/infra.rs      (-498)  # Gate domain extracted
crates/membrane-shadow/src/dispatch/gate.rs       (+518)  # NEW: local gate self-management
crates/membrane-shadow/src/dispatch/mod.rs        (+5/-3) # Route gate.* to new module
crates/membrane-shadow/src/ribocipher.rs          (+198)  # Mito-tier + HKDF + tests
```

---

## Status

- **riboCipher**: Clear tier LIVE in production, mito-tier READY (activates with FAMILY_SEED)
- **Dispatch**: Clean SRP decomposition, both modules under 800L threshold
- **Deep debt**: Zero remaining targets identified — codebase is modern idiomatic Rust 2024
