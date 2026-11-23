# BearDog v0.9.0 — Wave 134 Handoff

**Date**: Jun 3, 2026
**Owner**: southGate
**Commit**: `83f583715`
**Tests**: 14,974+ pass, 0 fail

## Summary

Smart ACME client refactor + production stub evolution + dead dependency cleanup.

## Changes

### ACME Client Smart Refactor (860 → 4 modules)

Split `crates/beardog-acme/src/client.rs` by lifecycle phase:

| Module | Lines | Responsibility |
|--------|-------|---------------|
| `client/mod.rs` | ~310 | Struct, constructor, protocol core (directory, nonce, account, order, challenges) |
| `client/config.rs` | ~115 | `AcmeConfig`, `from_env()`, HTTP client bootstrap, `Directory` type |
| `client/renewal.rs` | ~90 | Daemon loop, domain expiry checks, `needs_renewal()` |
| `client/issuance.rs` | ~270 | CSR generation, order finalization, polling, cert download |

All 36 ACME tests pass. Public API surface unchanged — `AcmeClient` and `AcmeConfig`
remain re-exported from `lib.rs`. Tests migrated to their natural modules
(CSR test → issuance, config test → config).

### Production Stub Evolution

Silent no-ops upgraded to structured `warn!` logging:

| File | Before | After |
|------|--------|-------|
| `primal_self_knowledge.rs:discover_via_registry` | Silent `Ok(Vec::new())` when URL set | `warn!` with registry URL and capability |
| `discovery.rs:discover_via_service_registry` | `debug!` + `info!` when URL set | `warn!` with structured fields |
| `trait_impl.rs:discover_capability` | `debug!` for unimplemented types | `warn!` for unimplemented capability types |

### Dead Dependency Removal

| Crate | Dep removed | Reason |
|-------|-------------|--------|
| `beardog-tunnel` | `hostname` | Zero usage in source |
| Root `beardog` binary | `hostname` | Zero usage in source |

`hostname` remains in `beardog-core` and `beardog-discovery` where it's actually used.

## File Summary

| File | Change |
|------|--------|
| `crates/beardog-acme/src/client.rs` | **Deleted** (860 lines) |
| `crates/beardog-acme/src/client/mod.rs` | **Created** (~310 lines) |
| `crates/beardog-acme/src/client/config.rs` | **Created** (~115 lines) |
| `crates/beardog-acme/src/client/renewal.rs` | **Created** (~90 lines) |
| `crates/beardog-acme/src/client/issuance.rs` | **Created** (~270 lines) |
| `crates/beardog-core/src/primal_self_knowledge.rs` | Stub → warn |
| `crates/beardog-core/src/ecosystem/primal_interface/trait_impl.rs` | Stub → warn |
| `crates/beardog-discovery/src/discovery.rs` | Stub → warn |
| `crates/beardog-tunnel/Cargo.toml` | Remove `hostname` |
| `Cargo.toml` (root) | Remove `hostname` |

## Quality Gates

| Check | Result |
|-------|--------|
| `cargo fmt` | Clean |
| `cargo clippy -D warnings` | Clean |
| `cargo test --workspace` | All pass, 0 fail |
