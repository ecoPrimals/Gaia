# sweetGrass v0.7.49 — Env Var Constant Consolidation (Wave 78c)

**Date**: June 5, 2026
**From**: strandGate / sweetGrass
**Version**: v0.7.48 → v0.7.49

## Summary

Deep debt audit and execution: eliminated all bare env var string literals
from production code by consolidating into `primal_names::env_vars` constants.

## What Changed

**26 new constants** added to `sweet_grass_core::primal_names::env_vars`:

| Constant | Used In |
|----------|---------|
| `DISCOVERY_ADDRESS` | `state.rs`, `discovery/registry.rs` |
| `UNIVERSAL_ADAPTER_ADDRESS` | `discovery/registry.rs` |
| `DISCOVERY_BOOTSTRAP` | `discovery/registry.rs` |
| `PRIMAL_INSTANCE_ID` | `primal_info.rs` |
| `TARPC_PORT` | `primal_info.rs` |
| `REST_PORT` | `primal_info.rs` |
| `PRIMAL_CAPABILITIES` | `primal_info.rs` |
| `SWEETGRASS_CONFIG` | `config/mod.rs` |
| `XDG_CONFIG_HOME` | `config/mod.rs` |
| `SWEETGRASS_NAME` | `config/mod.rs` |
| `SWEETGRASS_TARPC_LISTEN` | `config/mod.rs` |
| `SWEETGRASS_REST_LISTEN` | `config/mod.rs` |
| `SWEETGRASS_DISCOVERY_BOOTSTRAP` | `config/mod.rs` |
| `ECOP_VOCAB_URI` | `braid/context.rs` |
| `ECOP_BASE_URI` | `braid/context.rs` |
| `NEURAL_API_SOCKET` | `neural_announce.rs` |
| `ECOPRIMALS_FAMILY_ID` | `neural_announce.rs` |
| `STORAGE_PATH` | `bin/service.rs` |
| `SWEETGRASS_RETRY_MAX` | `resilience/mod.rs` |
| `SWEETGRASS_RETRY_INITIAL_MS` | `resilience/mod.rs` |
| `SWEETGRASS_RETRY_MAX_MS` | `resilience/mod.rs` |
| `SWEETGRASS_AGENT_DID` | `bootstrap.rs` |
| `SWEETGRASS_HTTP_PORT` | `bin/service.rs` |
| `SWEETGRASS_HTTP_ADDRESS` | `bin/service.rs` |
| `SWEETGRASS_TARPC_ADDRESS` | `bin/service.rs` |
| `STORAGE_BACKEND` | `bin/service.rs` |

## Deep Debt Audit Results

| Category | Production Code | Status |
|----------|----------------|--------|
| `unsafe` code | 0 | `forbid(unsafe_code)` all 10 crates |
| `unwrap()`/`expect()` | 0 in production | All in `#[cfg(test)]` |
| `#[allow]` | 0 | Zero |
| `println!`/`eprintln!` | 0 | Only in `examples/` |
| `Box<dyn Error>` | 0 | Only in doc comments |
| `std::sync::Mutex` | 0 | — |
| `Rc<` | 0 | — |
| `async_trait` | 0 | RPITIT throughout |
| Bare env var strings | 0 | All use `env_vars::` constants |
| Hardcoded primal names | Self-knowledge only | `identity::PRIMAL_NAME` constant |
| Mocks in production | 0 | All `#[cfg(any(test, feature = "test"))]` |
| `TODO`/`FIXME`/`HACK` | 0 | — |
| `todo!()`/`unimplemented!()` | 0 | — |
| Files > 800L | 0 | Max 783L (`tests.rs`) |

## Metric Deltas

| Metric | v0.7.48 | v0.7.49 | Delta |
|--------|---------|---------|-------|
| Tests | 1,623 | 1,623 | 0 |
| LOC | ~60,650 | ~60,780 | +130 |
| Source files | 209 | 209 | 0 |
| Methods | 40 | 40 | 0 |
| Env var constants | ~27 | 53 | +26 |

## Forward Targets

- **Holding steady** per strandGate directive: no new feature work until
  bearDog delivers `auth.events.subscribe` and rhizoCrypt wires DAG append
- **btsp/server.rs (766L), btsp/transport.rs (763L)** — approaching 800L;
  test extraction candidate if they grow
