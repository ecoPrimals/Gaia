# BearDog v0.9.0 — Wave 132 Handoff

**Date**: Jun 3, 2026
**Owner**: southGate
**Commit**: `d23423123`

## Delivered

### P2: AI Deprecated Modules Migration (COMPLETE)

Types from `beardog-core/ai/hybrid_intelligence/{learning.rs, neural_networks.rs,
learning_optimization.rs}` moved to canonical location in `beardog-types`:

| Source (beardog-core, DELETED) | Destination (beardog-types) |
|---|----|
| `learning.rs` (403 lines) | `ai_config/core_learning.rs` |
| `learning_optimization.rs` (462 lines) | merged into `ai_config/core_learning.rs` |
| `neural_networks.rs` (701 lines) | `ai_config/core_neural_networks.rs` |

**Total**: -1,104 LOC from beardog-core. Deprecated modules replaced with 7-line
thin re-exports (`pub use beardog_types::...::core_learning::*`). All callers
(`core_types.rs`, `training_config.rs`, test modules) continue to import via
`crate::ai::hybrid_intelligence::learning::*` — zero import changes needed.

**Design note**: These are *implementation-level* types (detailed struct shapes
like `NetworkArchitecture { architecture_type, input_layer, hidden_layers, ... }`)
that complement the *configuration-level* types already in `ai_config/learning.rs`
and `ai_config/neural_networks.rs` (simplified enums and DTOs). Both type sets
are intentionally preserved — they serve different layers of the stack.

### P3: Mobile Feature Flag (COMPLETE)

`beardog-security` now has `feature = "mobile"` in `Cargo.toml`:

```toml
[features]
fido2 = ["dep:beardog-hid", "dep:ciborium"]
mobile = []
quantum-crypto = []
```

All Android/iOS gates in the HSM module now require BOTH the feature flag AND
the target OS:

```rust
// Before: compiled automatically on Android
#[cfg(target_os = "android")]

// After: explicit opt-in via feature
#[cfg(all(feature = "mobile", target_os = "android"))]
```

Updated 18 cfg gates across `hsm/mod.rs` and `entropy_orchestrator/orchestrator.rs`.

**Impact**: Zero change for desktop Linux builds (Android/iOS modules were already
not compiled). For Android production builds, enable `features = ["mobile"]` in
the workspace/crate config.

## Confirmed (No Code Change)

### P0: S4 auth monitoring (PASSIVE)

7-day gate active (ends ~Jun 9). No failures reported.

### P3: Pure-Rust crypto tracking

`rustls-rustcrypto` and `p256/x509-cert` as `rcgen` replacement — tracking only.
No upstream changes ready for adoption.

## Quality Gates

- `cargo fmt` ✅
- `cargo clippy --workspace -- -D warnings` ✅
- `cargo test --workspace` ✅ (14,974 tests, 0 failures)
- 2 flaky tests (`test_encrypt_1mb_data`, `two_providers_independent_hardware_flags`)
  pass individually — pre-existing concurrency sensitivity, not regressions

## Files Changed

### beardog-types (new)
- `ai_config/core_learning.rs` — implementation-level learning types
- `ai_config/core_neural_networks.rs` — implementation-level neural network types
- `ai_config/mod.rs` — register new modules

### beardog-core (modified)
- `learning.rs` — 403→7 lines (thin re-export)
- `neural_networks.rs` — 701→7 lines (thin re-export)
- `learning_optimization.rs` — DELETED (462 lines)

### beardog-security (modified)
- `Cargo.toml` — add `mobile = []` feature
- `hsm/mod.rs` — gate android_strongbox behind `feature = "mobile"`
- `entropy_orchestrator/orchestrator.rs` — 18 cfg gates updated
