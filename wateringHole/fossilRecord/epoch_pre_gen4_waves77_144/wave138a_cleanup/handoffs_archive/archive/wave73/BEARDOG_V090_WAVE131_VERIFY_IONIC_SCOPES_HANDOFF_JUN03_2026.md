# BearDog v0.9.0 — Wave 131 Handoff

**Date**: Jun 3, 2026
**Owner**: southGate
**Commit**: `8a18183ff`

## Delivered

### P1: auth.verify_ionic scopes fix (COMPLETE)

`handle_auth_verify_ionic` now always includes `"scopes"` at the top level of every
JSON-RPC response. primalSpring's SecurityVerifier in Enforced mode requires this field
to check permissions without navigating into the `claims` object.

**Before:**
- Valid token: `{ "valid": true, "scope_ok": true, "claims": { ..., "scopes": [...] } }`
- Error: `{ "valid": false, "error": "..." }`

**After:**
- Valid token: `{ "valid": true, "scope_ok": true, "scopes": ["crypto.*", ...], "claims": { ..., "scopes": [...] } }`
- Error: `{ "valid": false, "scopes": [], "error": "..." }`

The `scopes` field inside `claims` remains for backward compatibility. Three test
assertions added to verify the top-level `scopes` contract on valid, invalid, and
missing-token responses.

## Confirmed (No Code Change Needed)

### P3: health.liveness (ALREADY IMPLEMENTED)

`HealthHandler` already registers `health.liveness` and returns
`{"status":"alive","primal":"beardog","version":"..."}`. The primalSpring
report of `-32601 (Method not found)` is **stale** — this was implemented
in a prior wave. No change required.

### P2: Android type stack consolidation (FALSE POSITIVE)

`HsmEntropyOrchestrator`'s `StrongBoxMultiCredentialProvider` field is
already `#[cfg(target_os = "android")]` gated. On desktop Linux builds,
this field does not exist and there is zero compile-time coupling. The
Android NDK/JNI deps are only pulled for `cfg(target_os = "android")`.

Future work: consider introducing a `mobile` feature flag (mirroring
FIDO2's `fido2` feature pattern) for explicit opt-in on cross-compile.

### P2: AI deprecated modules migration (TYPE INCOMPATIBILITY)

`learning.rs` and `neural_networks.rs` in `beardog-core` CANNOT be
migrated to `beardog_types::ai_config` via simple import swap. The
canonical types have **different shapes** from the deprecated types:

| Type | Deprecated (beardog-core) | Canonical (beardog-types) |
|------|---------------------------|--------------------------|
| `NetworkArchitecture` | struct (fields: architecture_type, input_layer, hidden_layers, output_layer, skip_connections) | enum (Feedforward, Convolutional, Recurrent, ...) |
| `EntropyDistribution` | statistical distributions (Normal{mean,stddev}, Uniform{min,max}, Xavier) | entropy sources (HumanUniform, QuantumInspired, BiometricSeeded) |
| `EnsembleConfig` | struct with base_models, method, n_estimators | renamed to `EnsembleConfigLearning` with different fields |
| `NetworkOptimization` | struct | missing in canonical |
| `NetworkRegularization` | struct | missing in canonical |
| `PredictionModel` | struct | missing in canonical |

Migration requires type system redesign, not import substitution.
Marking as blocked on design decision.

### P0: S4 auth monitoring (PASSIVE)

7-day gate active (ends ~Jun 9). No auth failures reported. bearDog
BTSP auth operational on southGate.

## Quality Gates

- `cargo fmt` ✅
- `cargo clippy --workspace -- -D warnings` ✅
- `cargo test --workspace` ✅ (14,974 tests, 0 failures)

## Files Changed

- `crates/beardog-tunnel/src/ionic_token_handlers.rs` — scopes at response top level
- `CHANGELOG.md` — Wave 131 entry
