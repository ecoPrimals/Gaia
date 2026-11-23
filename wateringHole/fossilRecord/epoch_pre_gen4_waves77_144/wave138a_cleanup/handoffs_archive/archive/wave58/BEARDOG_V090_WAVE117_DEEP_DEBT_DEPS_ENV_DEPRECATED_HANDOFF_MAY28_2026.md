# BearDog v0.9.0 — Wave 117: Deep Debt — Dependencies, Env Migration, Deprecated Types

**Date**: May 28, 2026
**Commit**: `36148bc42`
**Quality Gates**: `cargo fmt` ✓ | `cargo clippy -D warnings` ✓ | `cargo test --workspace` ✓ (14,987 tests, 0 failures)

---

## Summary

Wave 117 executes three high-impact debt cleanup passes: unused dependency pruning, environment variable centralization migration, and deprecated type elimination.

## 1. Dead Code & Dependency Pruning

### Deleted Files
| File | LOC | Reason |
|------|-----|--------|
| `crates/beardog-tunnel/src/main.rs` | 198 | Stale CLI duplicate — not wired as `[[bin]]` target |
| `crates/beardog-security/src/hsm/fido2/operations.rs` | 107 | Dead Phase-2 stubs (never called); `Ctap2Command` enum duplicated `ctap2::types` |

### Pruned Dependencies (10 workspace deps, 20+ per-crate entries)
| Dependency | Crate(s) | Reason |
|------------|----------|--------|
| `tokio-tungstenite` | beardog-tunnel | Zero `.rs` references |
| `tokio-serde` | beardog-tunnel | Zero `.rs` references |
| `mockito` | beardog-client, beardog-integration | Zero `.rs` references |
| `wiremock` | beardog-integration | Zero `.rs` references |
| `tokio-test` | 12 crates | Zero `.rs` references |
| `validator` | beardog-config | Only local `beardog_installer::validator` used |
| `urlencoding` | beardog-core | Zero `.rs` references |
| `local-ip-address` | beardog-discovery | Zero `.rs` references |
| `clap` | beardog-tunnel | Only used by deleted `main.rs` |
| `tracing-subscriber` | beardog-tunnel | Only used by deleted `main.rs` |

**Net effect**: −609 lines deleted, reduced dependency tree.

## 2. Env Var Centralization (100+ sites migrated)

Extended `beardog-config::env_keys` from 65 to 107 constants. Migrated all 17 domain files in `beardog-config/src/domains/`:

| Domain file | Sites migrated |
|-------------|---------------|
| `paths.rs` | 5 |
| `network_ports.rs` | 10 |
| `network_addresses.rs` | 16 |
| `network_hosts.rs` | 8 |
| `network.rs` | 9 |
| `monitoring.rs` | 5 |
| `crypto.rs` | 5 |
| `hsm.rs` | 7 |
| `security.rs` | 8 |
| `timeouts_new/builder.rs` | 9 |
| `timeouts_new/database.rs` | 6 |
| `timeouts_new/health.rs` | 2 |
| `timeouts_new/hsm.rs` | 4 |
| `timeouts_new/ai.rs` | 6 |
| `timeouts_new/network.rs` | 28 |
| `port_discovery/discoverer.rs` | 4 |
| `port_discovery/config.rs` | 4 |
| `limits.rs` | 16 |
| `capacity.rs` | 9 |

**Result**: `beardog-config/src/domains/` is now fully centralized on `env_keys::ENV_*` constants.

## 3. Deprecated Type Cleanup

| Deprecated symbol | Replacement | Files fixed |
|-------------------|-------------|-------------|
| `LoggingConfiguration` | `LoggingConfig` | `providers/base/configuration.rs`, `providers/base/defaults.rs` |
| `RegistryConfig` (providers) | `ProviderRegistryConfig` | `ecosystem_integration.rs`, `consolidated_registry.rs` |
| `BiomeOSPaths` | `PlatformPaths` | `installer/lib.rs` (public re-export removed) |

## Remaining Items (Low Priority)

| Item | Status | Notes |
|------|--------|-------|
| AI `RegistryConfig` re-export | Low | `ai/types/mod.rs` — kept for backward compat |
| `BootstrapConfig` migration shims | Low | Internal-only; external callers use `UnifiedBootstrapConfig` |
| Monitoring migration stubs | Low | `monitoring_migration.rs`, `hsm_unified/migration.rs` |
| Test-only deprecated constant aliases | Low | `limits.rs:511+`, `buffers.rs:305+`, `timeouts.rs:471+` |
| Env migration outside `domains/` | Medium | ~300+ sites across other crates |

---

*Prepared for downstream primalSpring audit.*
