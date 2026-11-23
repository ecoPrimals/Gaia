# bearDog v0.9.0 -- Wave 130 Handoff: Feature-gate quantum_crypto + Deprecated Module Purge

**Date**: Jun 3, 2026
**Wave**: 130 (Wave 72 Response)
**Author**: southGate (autonomous)
**Status**: COMPLETE

## Summary

Feature-gated the `quantum_crypto` simulation module (prevents false PQC claims on public API) and deleted three deprecated modules with zero external callers. Deep debt audit confirms zero `.unwrap()` in production code paths.

## Changes

### quantum_crypto Feature Gate

The `beardog-security` crate's `quantum_crypto` module contained placeholder/simulation PQC implementations (Kyber KEM, Dilithium, SPHINCS+) that were exported on the public API surface despite being non-functional. These have been gated behind `feature = "quantum-crypto"` (disabled by default).

- `crates/beardog-security/Cargo.toml`: Added `quantum-crypto = []` feature
- `crates/beardog-security/src/lib.rs`: `#[cfg(feature = "quantum-crypto")] pub mod quantum_crypto`
- Test suite gated correspondingly

### Deprecated Module Deletion (-369 lines)

| Module | Files | Replacement | External Callers |
|--------|-------|-------------|-----------------|
| `monitoring_unified/` | 7 deleted | `canonical/monitoring/MonitoringConfig` | 0 |
| `timeout_unified.rs` | 1 deleted | `canonical/config/domains/timeout` | 0 |
| `providers_unified/discovery.rs` | 1 deleted | Re-export inlined to `mod.rs` | 0 |

### Deep Debt Audit Results

| Metric | Value |
|--------|-------|
| `.unwrap()` in production code | **0** (all 326 occurrences in `#[cfg(test)]`) |
| `todo!()` / `unimplemented!()` | 0 |
| Inline env var strings | 0 |
| Files >800L | 1 (beardog-acme/client.rs, cohesive) |

### Not Changed (Deferred)

- **Android type stack consolidation**: `HsmEntropyOrchestrator` depends on `StrongBoxMultiCredentialProvider` at compile time. Requires orchestrator migration before security path can be feature-gated.
- **AI deprecated modules** (`learning.rs`, `neural_networks.rs`): 4-6 production callers each; require import migration to `beardog_types::ai_config` before deletion.
- **`beardog-traits::canonical`**: Production-safe to remove but breaks test suite.

## Quality Gates

- `cargo fmt` -- clean
- `cargo clippy --workspace -- -D warnings` -- clean
- `cargo test --workspace` -- **14,974 passed, 0 failed, 130 ignored**

Test count decreased from 14,988 to 14,974 due to deprecated module tests removal and quantum_crypto feature gating (expected).

## S4 Auth Status

ironGate 7-day gate ACTIVE (Jun 2-9). No auth failures reported. No code changes needed.
