<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Squirrel — Wave 116: TRUE PRIMAL Evolution + Deep Debt Cleanup

**Date**: June 19, 2026
**Gate**: eastGate
**Primal**: squirrel
**Wave**: 116
**Commit range**: See `CHANGELOG.md [Unreleased]`

## Summary

Two-phase deep debt cleanup culminating in TRUE PRIMAL compliance:

1. **Wave 116a** — Provider registry wiring, BTSP Phase 3, auth service, hardcoding evolution, large file refactoring, dignity enforcement.
2. **Wave 116b** — TRUE PRIMAL capability-based architecture, real system metrics, doc/CI alignment, stale artifact cleanup.

## Gate Status

| Gate | Status |
|------|--------|
| `cargo fmt --all -- --check` | PASS |
| `cargo clippy --all-targets --all-features -- -D warnings` | PASS (0 warnings) |
| `cargo test --all` | 7,394 total (7,293 passed, 101 ignored, 0 failed) |
| `cargo doc --workspace --no-deps --all-features` | PASS |
| `cargo deny check` | PASS |
| Production files >800L | 0 (max: 796L) |
| TODO/FIXME/HACK | 0 |
| Production `unsafe` | 0 |
| Production `.unwrap()` | 0 |

## Key Changes

### TRUE PRIMAL Compliance

- `niche::DEPENDENCIES` (named primal IDs) → `niche::REQUIRED_CAPABILITIES` (capability-based)
- Squirrel now declares what it *needs* (security, service-mesh, compute, storage, coordination, ui) not *who* provides it
- `EcosystemServiceRegistration` gains `capability_id: Option<Arc<str>>` field
- All production `EcosystemPrimalType` uses annotated `#[expect(deprecated)]`
- New `COORDINATION_CAPABILITY` and `UI_CAPABILITY` in `universal-constants/capabilities.rs`

### Provider Registry LIVE

- `provider.register`, `provider.list`, `provider.deregister` fully wired via JSON-RPC dispatch
- Springs can register capabilities and socket paths with Squirrel at runtime

### BTSP Phase 3 LIVE

- `btsp.negotiate` handler wired to `btsp_encrypted_framing` module
- ChaCha20-Poly1305 AEAD session key derivation via HKDF-SHA256

### Real System Metrics

- `performance.rs`: `/proc/self/stat` (CPU), `/proc/self/statm` (memory), `/proc/self/io` (disk), `/proc/net/dev` (network)
- `security/health.rs`: Real capability-discovery probe replaces simulated endpoint check

### Doc + CI Alignment

- README, CONTEXT, CURRENT_STATUS synced to 7,394 tests / 42 methods / ~1,031 files
- CI workflow aligned with `just ci` (`--all-features`, integration tests, `cargo doc`)
- 8 stale migration comment artifacts removed
- Stale HTTP/REST/gRPC doc references updated to JSON-RPC/IPC

## Remaining Carry (upstream primal teams)

### Phase 2 Stubs (correctly gated, awaiting upstream providers)

- `integration/mcp_ai_tools` — streaming/generate_response (awaits MCP tools activation)
- `integration/ecosystem` — placeholder crate (awaits service mesh client)
- `core/plugins/default_manager` — dependency resolution, state persistence (Phase 2)
- `tools/rule-system/evaluator` — plugin architecture (Phase 2)
- Discovery `registry/discovery.rs:392` — JSON-RPC socket probe (socket scan exists; probe enhancement deferred)

### Deprecated Types (backward compat — can be removed when consumers migrate)

- `EcosystemPrimalType` enum — used in serde types; consumers need `capability_id` migration
- `BeardogSecurityCoordinator` re-export — aliased from `SecurityCoordinator`
- `BEARDOG_SECURITY_SERVICE_ID` — wire compat for legacy `service_id` comparison

### Observations for Upstream Audit

- `specs/SOCKET_REGISTRY_SPEC.md` examples still use primal names (Songbird, BearDog) — consider evolving to capability IDs
- `squirrel_deploy.toml` uses primal names for biomeOS BYOB graph — orchestrator convention, not runtime dependency
- `crates/universal-patterns/src/capabilities.rs:17,145,167` mentions HTTP/gRPC — update when transport module docs evolve
- `RetryFuture<T>` uses `Box<dyn StdError>` — legitimate for generic closure framework, not a typed-error violation

## Composition Role

Squirrel is the **intelligence router** for all compositions requiring AI inference:
- Meta-tier member (biomeOS + squirrel + petalTongue)
- Provides inference routing to any composition needing LLM/embedding access
- 42 IPC methods (39 in capability_registry.toml + 3 internal aliases)
- Human dignity evaluation with configurable enforcement
