# biomeOS v3.93 — Wave 70b Handoff

**Date**: 2026-06-02
**Commit**: 183b39ae
**Author**: southGate

## Summary

Wave 70b evolved the cross-primal hardcoding pattern from direct name-based
defaults to taxonomy-first capability resolution, and collapsed the `rustix`
dependency duplicate via a `which` crate major bump.

## Changes

### 1. Taxonomy-First Provider Resolution (8 production sites)
All security/discovery provider fallbacks now follow a 3-tier pattern:
`env::var(PROVIDER)` → `CapabilityTaxonomy::resolve_to_primal("capability")` → last-resort primal constant

**Before**: `env::var("SECURITY_PROVIDER").unwrap_or_else(|| BEARDOG.to_string())`
**After**: `env::var(...).ok().or_else(|| taxonomy.resolve_to_primal("security")...).unwrap_or_else(|| BEARDOG.to_string())`

Fixed sites:
- `bootstrap.rs` (security + discovery, now also checks "encryption" + "networking")
- `btsp_client.rs` (security provider)
- `config/mod.rs` (discovery provider)
- `mode.rs` (both security and network)
- `http_client.rs` (discovery provider)
- `primal_communication.rs` (security for BTSP tunnel)
- `plasmodium/peers.rs` (discovery for mesh.peers)
- `plasmodium/remote.rs` (discovery for status synthesis)
- `security_client.rs` (both `from_discovery` and `from_primal_discovery`)

### 2. Squirrel-Specific Logic Eliminated
`primal_spawner.rs`: Removed `eq_ignore_ascii_case(SQUIRREL)` gate on
`AI_DEFAULT_MODEL` injection. Now passes the env var to ALL child primals
(each primal decides whether to consume it — capability-agnostic).

### 3. Dependency Evolution
- `which` 6 → 8: collapses transitive `rustix` 0.38 / `linux-raw-sys` 0.4
  duplicate. Workspace now has single `rustix` 1.1.4.

## Verification
- `cargo check --workspace`: PASS
- `cargo clippy --workspace`: 0 warnings
- `cargo test --workspace`: 1316 pass, 4 known flaky (neural_router::discovery)
- `cargo tree -d | grep rustix`: single version confirmed
