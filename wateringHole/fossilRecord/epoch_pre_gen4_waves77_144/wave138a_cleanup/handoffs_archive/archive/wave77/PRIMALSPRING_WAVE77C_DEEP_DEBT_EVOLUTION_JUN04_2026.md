# primalSpring Wave 77c — NUCLEUS Deep Debt Evolution

**Gate**: eastGate | **Date**: 2026-06-04 | **Status**: DELIVERED
**Plan**: `nucleus_deep_debt_evolution_ba57410c.plan.md`

## What Shipped

Systematic deep debt resolution across primalSpring — 7 phases, all complete.

### Phase 1: `ring` C dependency eliminated
- Feature-gated `ureq` (HTTPS client) behind `cross-membrane` feature
- Default builds have zero C dependencies (ecoBin compliant)
- `s_cross_membrane_integrity` gracefully degrades when feature is off

### Phase 2: Routing table consolidation (biggest debt)
- 6+ duplicated capability-to-primal mapping tables → single TOML-driven `DOMAIN_OWNER_MAP`
- Added 7 alias sections to `capability_registry.toml` (orchestration, commit, ledger, merkle, recon, threat, audit)
- Deleted `static_capability_fallback()` — all routing from TOML
- `tcp_fallback_table()` now dynamic from `DOMAIN_OWNER_MAP` + `tolerances::port_entry_for`
- `CompositionTier::from_domain` derives from TOML compositions via `primal_home_tier_priority()`

### Phase 3: Profile-driven `nucleus_launcher`
- Removed Songbird-specific `if`-block from `orchestrator/spawn.rs`
- Generic profile loading from `primal_launch_profiles.toml` for all primals
- Registry seeding uses dynamic `capability_to_primal("discovery")` instead of hardcoded Songbird
- Startup ordering prefers graph-driven topological waves with capability-based fallback

### Phase 4: File refactoring (3 near-threshold splits)
- `s_deployment_pipeline.rs` (776L) → `mod.rs` + 6 stage modules (build, harvest, provenance, compose, deploy, verify)
- `context.rs` (775L) → extracted discovery escalation into `context_discovery.rs`
- `exp096 phases.rs` (756L) → 3 per-concern modules (tower_genetics, btsp_hsm, beacon_bonding_stun)
- All files now well under 800-line threshold

### Phase 5: Certification test coverage
- 33 new unit tests across all 8 `certification/` modules (was zero coverage)
- Tests: bonding policies, BTSP cipher minima, enforcer decisions, cell graph validation, entropy/seed resolution, hex encoding, fingerprinting, bare properties, certify(0)

### Phase 6: Hardcoded values cleanup
- Fixed `tcp://127.0.0.1:{port}` in `ipc.register` → uses `PRIMALSPRING_HOST` env
- Removed hardcoded `192.168.1.132:7700` / `192.168.1.238:7700` gate IPs from `live_mesh.rs`
- Replaced `/run/user/1000/biomeos` → `tolerances::runtime_dir()` in `covalent_mesh_trust.rs`
- Derived `PRIMAL_SLUGS` from `Primal::ALL` in perceptron feature extraction

### Phase 7: Deprecation cleanup
- `leak_or_match` no longer returns `"unknown"` — warns + leaks for truly unknown owners
- Harness `capability_to_primal` zip-lookup replaced with TOML-driven routing table

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Lib tests | 837+ | 889 |
| Certification tests | 0 | 33 |
| Static routing tables | 6+ | 1 (TOML-driven) |
| C dependencies (default) | 1 (ring via ureq) | 0 |
| Hardcoded IPs in code | 4 locations | 0 |
| Files near 800L threshold | 3 | 0 (all split) |

## Files Changed

- `ecoPrimal/Cargo.toml` — `ureq` optional, `cross-membrane` feature
- `config/capability_registry.toml` — 7 new alias sections
- `ecoPrimal/src/composition/routing.rs` — `static_capability_fallback` deleted, `PRIMAL_HOME_TIER` added
- `ecoPrimal/src/composition/btsp.rs` — `tcp_fallback_table` dynamic
- `ecoPrimal/src/composition/neural_routing.rs` — `from_owner_tier` delegates to TOML
- `ecoPrimal/src/composition/context.rs` — discovery delegated to `context_discovery.rs`
- `ecoPrimal/src/composition/context_discovery.rs` — new discovery module
- `ecoPrimal/src/bin/nucleus_launcher/orchestrator/spawn.rs` — profile-driven
- `ecoPrimal/src/bin/nucleus_launcher/orchestrator/mod.rs` — dynamic discovery, graph ordering, bind host fix
- `ecoPrimal/src/validation/scenarios/s_deployment_pipeline/` — new module directory (6 stage files)
- `ecoPrimal/src/validation/scenarios/covalent_mesh_trust.rs` — runtime_dir fix
- `ecoPrimal/src/validation/live_mesh.rs` — removed hardcoded IPs
- `ecoPrimal/src/composition/neural_dispatch/perceptron.rs` — `PRIMAL_SLUGS` from `Primal::ALL`
- `ecoPrimal/src/certification/*.rs` — tests added to all 8 modules
- `experiments/exp096_pixel_cross_arch_bonding/src/phases/` — split into 3 modules

## Next

- Inner membrane (`primal.eco`) deployment across gates — DNS propagation, Caddy vhosts
- Songbird TLS (blocked on bearDog `CryptoProvider` Ed25519)
- westGate enrollment (FRAGO pending)
- 3-gate plasmodium collective validation
