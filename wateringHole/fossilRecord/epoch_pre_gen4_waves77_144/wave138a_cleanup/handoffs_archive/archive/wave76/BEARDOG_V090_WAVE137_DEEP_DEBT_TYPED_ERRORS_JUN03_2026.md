<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 137: Deep Debt — Typed Handler Errors, Zero-Hardcoding, Dashmap 6

**Date**: Jun 3, 2026
**Owner**: southGate
**Primal**: bearDog v0.9.0-wave137
**Commit**: `781df151f`
**Tests**: 169 suites, 0 failures
**Quality**: `cargo fmt` + `clippy --workspace -D warnings` clean

---

## Summary

Structural deep debt sweep across the bearDog codebase, focusing on the
`Result<_, String>` handler pattern (the single largest debt source), hardcoded
fallback values, dependency freshness, and stub evolution documentation.

---

## Changes

### 1. Typed Handler Errors (P2 → resolved)

Replaced `Result<serde_json::Value, String>` across the entire `MethodHandler`
trait, all 14 handler implementations, the `MethodHandlerKind` dispatch enum, and
`HandlerRegistry::route` with a typed `HandlerError` enum:

```rust
pub enum HandlerError {
    MethodNotFound(String),  // -32601
    InvalidParams(String),   // -32602
    Application(String),     // -32000 (legacy String bridge)
    Domain(BearDogError),    // -32000 (structured domain errors)
}
```

- `From<String>` bridge: existing `Err("msg".to_string())` compiles unchanged.
- `HandlerResult` type alias for clean handler signatures.
- `route_with_outcome` now derives error phase/code from enum variants,
  eliminating fragile `msg.contains("Method not found")` string matching.
- Backward-compat heuristic in `into_json_rpc_error()` detects legacy
  "Missing"/"Invalid params" strings in `Application` errors for `-32602` mapping.

### 2. Zero-Hardcoding Centralization

Added centralized constants in `env_keys.rs`:
- `DEFAULT_PRIMAL_NAME = "beardog"` — 7 inline fallback sites fixed.
- `DEFAULT_DISCOVERY_HOST = "discovery.ecosystem.internal"` — 4 sites fixed.
- `DEFAULT_REGISTRY_HOST = "consul.ecosystem.internal"` — 2 sites fixed.

All production code now references these constants instead of inline strings.

### 3. Dependency Upgrade

- **dashmap 5.5 → 6.2**: hashbrown 0.15, detached guards, `SharedValue` removed.
  Zero API breakage across `beardog-tunnel` and `beardog-utils`.
- **mdns-sd 0.11 → 0.19**: Deferred — 8 minor versions with breaking `ScopedIpV4`
  changes (interface_ids tracking). Feature-gated (`#[cfg(feature = "mdns")]`).
  Tracked for dedicated wave.

### 4. Stub Evolution

- Renamed `discover_by_capability(Vec<UniversalCapabilityType>)` to
  `discover_by_typed_capability` with documentation explaining the type-system
  convergence gap with the string-based `discover_by_capability(&str)` pipeline.
- Confirmed all production mocks are platform-appropriate (Android/iOS HSM stubs,
  Consul/etcd discovery stubs returning `BackendUnavailable`).

### 5. Audit Findings

- **Unsafe code**: Zero — `#![forbid(unsafe_code)]` in all 31 crate roots.
- **Large files**: 1 production file >800L (`env_keys.rs`, 1900L) — validated as
  well-organized constants registry with 63 domain sections; no split needed.
- **Production `.unwrap()`**: Zero in server/CLI hot paths.
- **Self-knowledge violations**: Zero cross-primal name routing in production.

---

## Files Changed (28 files, +221/-123)

| File | Change |
|------|--------|
| `handlers/mod.rs` | `HandlerError` enum, `HandlerResult` alias, trait signature |
| `handlers/{health,security,btsp,...}.rs` (14 files) | Return type → `HandlerResult` |
| `server.rs` | `route_jsonrpc` uses `into_json_rpc_error()` |
| `env_keys.rs` | 3 new `DEFAULT_*` constants |
| `capabilities.rs`, `doctor.rs`, `crypto.rs`, `server/*.rs` | Use `DEFAULT_PRIMAL_NAME` |
| `config_impls.rs`, `registry.rs`, `env.rs` | Use `DEFAULT_*_HOST` |
| `primal_self_knowledge.rs` | Renamed stub method |
| `Cargo.toml` / `Cargo.lock` | dashmap 5.5 → 6.2 |

---

## Remaining Work (for upstream audit)

| Priority | Item |
|----------|------|
| P2 | `mdns-sd` 0.11 → 0.19 upgrade (dedicated wave) |
| P2 | Migrate individual handlers from `HandlerError::Application` to `InvalidParams`/`Domain` |
| P3 | `UniversalCapabilityType` ↔ string-capability convergence layer |
| P3 | Service registry client (Consul/etcd) — currently documented stub |
| P3 | `toml` 0.8 → 1.x migration (breaking API) |

---

## Coordination

- S4 7-day gate active (ends ~Jun 9).
- Songbird Phase 3.5 design documented in Wave 136 handoff.
- Family seed fingerprint binding designed in Wave 136 handoff.
- primalSpring upstream will audit this wave.
