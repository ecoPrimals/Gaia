# Songbird Wave 200 — Deep Debt Cleanup & Evolution

**Date**: May 12, 2026  
**Primal**: Songbird v0.2.1  
**Wave**: 200  
**From**: Songbird team  
**For**: All primal teams (reference patterns), primalSpring (validation)

---

## Summary

Wave 200 is a comprehensive deep debt cleanup pass targeting modern idiomatic Rust,
structural refactoring, stub evolution, hardcoding elimination, and dependency hygiene.

---

## Deliverables

### 1. method_gate.rs (944L) → Directory Module

The monolithic `method_gate.rs` was refactored into a focused directory module:

```
crates/songbird-orchestrator/src/ipc/pure_rust_server/method_gate/
├── mod.rs            — Re-exports, error_codes module
├── caller.rs         — PeerCredentials, CallerContext, ConnectionOrigin
├── classification.rs — MethodAccessLevel, scope matching, bearer extraction
├── gate.rs           — EnforcementMode, MethodGate::check, auth dispatch
├── token.rs          — TokenVerifier trait, NoopVerifier, BearDogVerifier
└── tests.rs          — 45 unit tests (all passing)
```

### 2. BearDogVerifier Evolution (Stub → Real IPC)

The `BearDogVerifier` previously returned "Unavailable (JH-11 not resolved)". Now that
BearDog has shipped `auth.public_key` (JH-11), the verifier makes live IPC calls:

- New: `SecurityRpcClient::verify_ionic(token)` in `songbird-http-client`
- `BearDogVerifier::verify()` calls `auth.verify_ionic` and parses claims
- Falls back to `TokenVerifyError::Unavailable` on IPC failure (graceful degradation)

### 3. Hardcoding Elimination

7 instances of literal `"0.0.0.0:0"` replaced with `songbird_types::constants::EPHEMERAL_BIND_ADDR`:
- `songbird-stun/src/turn_server.rs`
- `songbird-lineage-relay/src/multi_tier_coordinator.rs` (2×)
- `songbird-universal-ipc/src/handlers/stun_handler/client.rs`
- `songbird-universal-ipc/src/handlers/udp_peer_connector.rs`
- `songbird-universal-ipc/src/handlers/punch_handler/coordinate.rs`

### 4. Dependency Audit

- `ring`: Confirmed absent from compiled tree (deny.toml ban effective)
- `hickory-resolver`: Upgrade from 0.24 → 0.26 attempted, reverted (API breaking)
- `RUSTSEC-2026-0119` (hickory-proto): Added to deny.toml ignore with stadial migration note
- `cargo deny check`: Fully passing

### 5. Files >800L Deferred (with rationale)

- `bin_interface/server.rs` (878L) — Tightly coupled startup orchestration; splitting adds indirection without clarity
- `turn_server.rs` (836L) — Newly written (Wave 199); natural growth point for directory module later

---

## Patterns for Adoption

| Pattern | Location | Adopt |
|---------|----------|-------|
| Directory module refactoring | `method_gate/` | Files >800L with distinct concerns |
| `TokenVerifier` trait | `method_gate/token.rs` | Abstract verification for test/prod |
| `BearDogVerifier` real IPC | `method_gate/token.rs` | Live `auth.verify_ionic` calls |
| Centralized constants | `songbird_types::constants` | Replace string literals |

---

## Verification

- `cargo fmt --check` — clean
- `cargo clippy --workspace -- -D warnings` — zero warnings
- `cargo deny check` — fully passing
- `cargo test --workspace --lib` — 7,803 tests pass (excluding pre-existing songbird-types flaky test)

---

## What This Unblocks

- primalSpring contract tests can validate `BearDogVerifier` end-to-end (exp108 token federation)
- Scope enforcement is now live when BearDog is reachable
- Pattern reference for other primals doing stub-to-implementation evolution
