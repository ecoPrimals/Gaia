# biomeOS v3.73 Handoff — Deep Debt: Capability-Based Composition + Routing Evolution

**Date**: May 24, 2026
**Versions**: v3.69–v3.73 (consolidated)
**Scope**: Adaptive routing weights, attestation verification, membrane composition model, health normalization, capability-domain composition discovery, weights/ refactor, port helper rename

---

## Summary

Waves 42–47 plus a comprehensive deep debt cleanup. The routing layer gained persistent weights and utilization tracking. The composition layer evolved from name-based to capability-domain-based discovery. The weights module was refactored from a monolithic 879-line file into focused submodules.

---

## v3.69 — Wave 42: Persistent Weights + Utilization Tracking

- `RoutingWeightTable::open(path)` — redb-backed persistence. Weights loaded from disk on startup, flushed after every mutation.
- `CapabilityUtilizationTracker` — method-level call frequency monitoring with EWMA decay.
- `NeuralRouter::with_persistent_weights()` constructor for persistent mode.
- `neural_api.utilization` introspection endpoint.
- Circuit breaker on 5 consecutive failures; automatic half-open probe.
- `neural_api.route_explain` explains routing decisions with confidence + utilization data.
- 8 new tests.

## v3.70 — Wave 45: Weight Health + Attestation + Persistent Startup

- `neural_api.weight_health` introspection endpoint: convergence diagnostics, healthy flag, persistence status, circuit details.
- `primal.announce` attestation verification via BearDog IPC (`auth.verify_ionic`), replacing field-presence stub. Graceful degradation when BearDog unavailable.
- `NeuralApiServer` now calls `NeuralRouter::with_persistent_weights()` at startup — weights survive restarts via `$XDG_DATA_HOME/biomeos/routing_weights.redb`.

## v3.71 — Wave 46: Membrane Composition Live Execution

- `composition.deploy(graph)` enforces membrane constraints when `composition_model = "membrane"`.
- `validate_membrane_graph()` — domain-level node validation for membrane topology.
- `membrane_tower` composition pattern registered (7th canonical pattern).
- `graphs/membrane_deploy.toml` — 5-node sequential graph (biomeOS → BearDog → Songbird → SkunkBat → NestGate cache-only).
- 3 new tests.

## v3.72 — Wave 47: Health Normalization

- `health.check` returns `"status": "alive"` instead of `"status": "healthy"`, aligning with `health.liveness` and DEPLOYMENT_BEHAVIOR_STANDARD.
- Consumer-side tolerance retained: accepts "alive", "healthy", or "ok" from external primals.

## v3.73 — Deep Debt: Capability-Domain Composition + weights/ Refactor

### Composition handlers → capability-domain discovery
- `composition.status` pipeline readiness checks use capability domains (`storage.`, `dag.`, `compute.`) instead of hardcoded primal names.
- `composition.health` subsystem detection uses `TOWER_DOMAINS`, `NODE_DOMAINS`, `NEST_DOMAINS`, `MESH_DOMAINS` constants instead of env-var primal name fallbacks.
- Mesh provider discovered by `discovery.*`/`relay.*` capability rather than `BIOMEOS_NETWORK_PROVIDER`.

### `weights.rs` (879L) → `weights/` submodule
- `weights/scoring.rs` — `ProviderWeight`, EWMA, circuit breaker.
- `weights/store.rs` — `RoutingWeightTable`, redb persistence, provider selection.
- `weights/utilization.rs` — `CapabilityUtilizationTracker`, method-level tracking.
- `weights/mod.rs` — re-exports + all 22 tests preserved.

### Port helpers renamed to capability-oriented
- `security_port()` / `relay_port()` replace `beardog_port()` / `songbird_port()`.
- `#[doc(hidden)]` backward-compatible aliases retained.

### Socket alias table evolved
- `DOMAIN_PRIMAL_BOOTSTRAP` replaces `DOMAIN_SOCKET_ALIASES`.

---

## Test Counts

| Version | Tests (biomeos-atomic-deploy) | Tests (workspace-wide) |
|---------|-------------------------------|------------------------|
| v3.69   | 1,311                         | ~4,290                 |
| v3.70   | 1,311                         | ~4,290                 |
| v3.71   | 1,314                         | ~4,303                 |
| v3.72   | 1,314                         | 4,303                  |
| v3.73   | 1,314                         | 4,303                  |

All: 0 failures, 0 clippy warnings, fmt PASS.

---

## Files Changed (key)

- `crates/biomeos-atomic-deploy/src/handlers/composition.rs`
- `crates/biomeos-atomic-deploy/src/handlers/graph/execute.rs`
- `crates/biomeos-atomic-deploy/src/neural_router/composition.rs`
- `crates/biomeos-atomic-deploy/src/neural_router/weights/` (new submodule)
- `crates/biomeos-atomic-deploy/src/neural_api_server/listeners.rs`
- `crates/biomeos-types/src/constants/network.rs`
- `crates/biomeos-core/src/discovery_modern.rs`
- `crates/biomeos-atomic-deploy/src/capability_translation/socket.rs`
- `graphs/membrane_deploy.toml` (new)

---

## Downstream Impact

- **primalSpring**: All Wave 42–47 audit items resolved. `primal.announce` attestation now verified cryptographically.
- **projectNUCLEUS**: `composition.health` subsystems now discovered by capability domain — primals can be renamed without breaking health checks.
- **cellMembrane**: `composition_model = "membrane"` is now a live execution path with proper node validation.
- **All primals**: `health.check` and `health.liveness` both return `"alive"` — uniform health sweep behavior.

---

**Committed**: v3.69–v3.73 on `main`, pushed via SSH.
