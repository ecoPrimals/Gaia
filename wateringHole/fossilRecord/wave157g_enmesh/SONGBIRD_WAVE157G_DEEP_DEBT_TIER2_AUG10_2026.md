# Songbird Wave 157g — Deep Debt Tier 2 + Structural Refactoring

**Date**: August 10, 2026  
**Primal**: songBird  
**Gate**: eastGate  
**Version**: v0.2.1-wave157g  
**Commits**: `e6db4084` (file split + fixes), `eba8a41f` (Tier 2 + BTSP DRY)

---

## Summary

Deep debt execution focusing on G72 Dependency Pandemic Tier 2 (`tokio::sync` → `std::sync`),
file size refactoring, error type corrections, and architectural DRY extraction.

---

## Work Completed

### 1. File Refactoring: `http_server.rs` (854L → 4 modules)

Split monolithic file into focused modules:

| Module | Lines | Responsibility |
|--------|------:|----------------|
| `http_server/mod.rs` | ~240 | Public API, Axum router construction |
| `http_server/federation_dispatch.rs` | ~210 | riboCipher RPC dispatch + 7 unit tests |
| `http_server/tls_server.rs` | ~235 | TLS accept loop, protocol detection, riboCipher connection handler |
| `http_server/port_binding.rs` | ~110 | Sovereign socket binding with fallback |

Extracted `handle_ribocipher_connection()` and `serve_http_or_tls()` from the accept loop
for clarity and testability.

### 2. G72 Tier 2: `tokio::sync` → `std::sync` (51 sites)

Converted async locks to std::sync where guards are never held across `.await` points:

| Crate | Sites | Lock Type | Pattern |
|-------|------:|-----------|---------|
| songbird-quic | 13 | Mutex | Connection/stream buffer ops |
| songbird-registry | 36 | RwLock | Plugin registry, health, persistence, scaling |
| songbird-genesis | 2 | RwLock | WitnessVerifier trusted_witnesses |

**Pattern**: `.lock().unwrap_or_else(std::sync::PoisonError::into_inner)` — recovers
from poisoned locks without panicking.

**Scoping for Send compliance**: Guards in `tokio::spawn` contexts wrapped in `{ }` blocks
to prove drop-before-await to the compiler.

**Deferred**: 679 remaining sites across crates with mixed KEEP/CONVERT fields (requires
per-struct refactoring where some lock acquisitions ARE held across .await and some aren't,
but they're on the same field).

### 3. BTSP DRY Extraction: `connections/btsp_rpc.rs`

Created shared module consolidating identical tunnel RPC stubs from 3 BTSP connection files:
- `full_trust_btsp.rs`: 22 lines → 3 lines
- `limited_btsp.rs`: 37 lines → 3 lines
- `federated_btsp.rs`: 22 lines → 3 lines

Single integration point for Phase 2 tunnel transport when security provider v0.16.0+ ships.

### 4. Quick Fixes

- **STUN error type**: `not_implemented("stun_transport_already_running")` → `service("stun", "transport already running")` (semantic correctness)
- **Doc fix**: `virtual_relay.rs` UnavailableVerifier comment updated from "noop — accepts all" to accurately describe rejection behavior

---

## Verification

- `cargo clippy --workspace -- -D warnings`: Zero warnings
- `cargo test` on affected crates: 2,202 tests pass (orchestrator 1808, quic 96, registry 83, genesis 215)
- Full workspace clean compile

---

## Remaining for Future Sprints

1. **G72 Tier 2 mixed crates**: observability, network-federation, orchestrator, universal-ipc
   have struct fields where SOME lock sites are KEEP and SOME are CONVERT — needs field-level
   structural refactoring (split field into two, or extract sync-only fields into separate type)
2. **BTSP bidirectional RPC**: Blocked on security provider v0.16.0+ `send_data_over_tunnel` API
3. **ipc_registry.rs** (831L): 31L over threshold, moderate priority
4. **TLS consolidation**: 4 parallel rustls paths
5. **DNS-SD stubs**: `dns_sd_discovery`, `dns_sd_registration` remain not_implemented
6. **Coverage**: 313 production files with no obvious tests

---

## Upstream Dependencies

- Security provider v0.16.0+ needed for BTSP tunnel data plane
- biomeOS fleet-wide `LimitNOFILE=65536` for FD exhaustion P1

---

*Cascaded from eastGate via golgiBody for overwatch audit.*
