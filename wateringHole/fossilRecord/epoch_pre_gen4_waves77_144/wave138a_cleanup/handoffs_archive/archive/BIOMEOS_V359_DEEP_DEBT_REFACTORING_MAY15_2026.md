# biomeOS v3.59 — Deep Debt Refactoring Handoff

**Date**: May 15, 2026
**Version**: v3.57 → v3.59 (three commits: v3.59, v3.59b, v3.59c)
**Scope**: Smart module refactoring, dead code removal, capability-based evolution, federation diagnostics
**Tests**: 7,915 passing (0 failures)
**Commit**: `0f1d07fa`

---

## Changes

### v3.59 — method_gate modularization + dead code removal

**method_gate.rs** (1319L → 4 focused modules, net -683 lines):
- `classify.rs`: MethodAccessLevel enum, public method tables, classify_method()
- `ionic.rs`: ResourceEnvelope, IonicTokenClaims, scope_covers_method()
- `verifier.rs`: TokenVerifier trait, LocalClaimsVerifier, NoopVerifier, BearDogVerifier
- `mod.rs`: PeerCredentials, CallerContext, EnforcementMode, MethodGate + all 38 tests

Refactored `MethodGate::check()` from 95 lines of repeated enforcement-mode branching into
`mode_gate()` and `validate_claims()` helpers — single point of policy enforcement.

**Dead code**: Removed orphaned `biomeos-graph/src/neural_executor.rs` (720L). File was
never wired into the module tree (`lib.rs` has no `mod neural_executor`). Live executor
is `executor/core.rs` via `executor.rs`.

**Socket hardcoding**: Evolved `capability_translation/socket.rs` from hardcoded
`match primal { "toadstool" => "compute", "nestgate" => "storage" }` to data-driven
`DOMAIN_SOCKET_ALIASES` table with `dual_socket_primals()` helper.

**Env safety**: Fixed `std::env::remove_var` in test `fault_injector.rs` to save/restore
original values with explicit unsafe blocks and safety documentation.

### v3.59b — graph handler + lifecycle extraction

**graph/mod.rs** (830L → 578L): Extracted `shadow_deploy` (203L) and `verify_graph` (48L)
into `validation.rs` submodule. Same `impl GraphHandler { }` pattern as existing
`execute.rs`, `continuous.rs`, `pipeline.rs`.

**lifecycle.rs** (886L → 831L): Extracted `binary_search_dirs`, `probe_binary`,
`state_to_string` into `spring_status.rs`.

**constants/mod.rs** (852L): Analyzed — 537L production, 315L tests. Inline `pub mod`
structure (version, endpoints, timeouts, limits, ports, security, runtime_paths, files,
events) is already optimal. No split needed.

### v3.59c — federation health diagnostics

Evolved federation manifest health_check logging from generic "completed on N/M gate(s)"
to structured diagnostics with tracing fields: `federation`, `healthy`, `total`,
`not_implemented`. Distinguishes all-healthy / partial-coverage / all-down states.

---

## Deep Debt Audit Results

Comprehensive codebase scan confirmed:

| Category | Status |
|----------|--------|
| `unsafe` blocks in production | **0** (workspace `deny`, per-crate `forbid`) |
| Production mocks/stubs | **0** (all behind `#[cfg(test)]`) |
| `todo!()` / `unimplemented!()` | **0** |
| `TODO` / `FIXME` / `HACK` markers | **0** in `.rs` files |
| `unwrap()` in production paths | **0** (all in test code) |
| C/FFI dependencies | **0** (except `rtnetlink` → `netlink-sys`, documented) |
| Hardcoded primal names in routing | **0** (env-var-first, const fallback) |
| Production files >800 LOC | **0** |

## Architecture Observations

- `capability_domains.rs` uses correct two-tier design: TOML config primary, compiled-in
  const fallback. No action needed.
- `primal_names` constants used correctly as shared vocabulary with env-var-first
  resolution pattern throughout production code.
- `CapabilityRegistry::from_toml()` loads `config/capability_registry.toml` at runtime;
  `CAPABILITY_DOMAINS` const serves zero-config environments only.

---

## For primalSpring Audit

- All v3.57–v3.59 changes maintain backward compatibility
- No new JSON-RPC methods added (existing surfaces refined)
- `CompositionModel::Membrane` is recognized but not yet enforced at spawn time
- method_gate modularization preserves identical public API (re-exports unchanged)
- Test count delta: 7,924 (v3.50) → 7,915 (v3.59) due to orphaned neural_executor.rs
  removal (dead tests that were never compiled)

---

*Handoff for primalSpring evolution audit. Ship fixes, push to plasmidBin,
and we'll pull + validate on next evolution pass.*
