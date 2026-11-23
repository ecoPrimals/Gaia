# biomeOS Wave 128 — Mega-Test Split + primalSpring Evolution

**Date**: 2026-06-28
**Gate**: eastGate (Overwatch)
**Repos**: biomeOS, primalSpring

---

## Summary

All four biomeOS test files exceeding 800 LOC have been split into domain-focused
submodules. In parallel, primalSpring received SSOT slug migration, ipc/error.rs
test extraction, and scenario thickening.

---

## biomeOS (v4.32 → v4.33)

### Mega-Test Splits (4 files → 16 domain modules)

| Original File | LOC | Hub | Submodules |
|--------------|-----|-----|------------|
| `neural_executor_rollback_tests.rs` | 1237 | 371 | lifecycle (210), capability (274), order (444) |
| `btsp_client_tests.rs` | 1215 | 168 | family (110), types (128), provider (220), server (387), client (304) |
| `p2p_coordination/tests.rs` | 1074 | 144 | coordinator (346), status (379), types (227) |
| `nucleus_tests.rs` | 1061 | 16 | config (372), startup (358), lifecycle (355) |

**Tests preserved**: 193 (35+49+46+63), zero failures.

### Quality Gates
- `cargo check --tests --workspace` → 0 errors
- `cargo fmt --check` → clean
- `cargo clippy --workspace -- -D warnings` → clean
- Zero production or test files over 450 LOC

---

## primalSpring (1014 lib tests)

### SSOT Slug Migration
- `tolerances/ports.rs`: all 13 PORT_REGISTRY slug literals replaced with
  `primal_names::BEARDOG`, `primal_names::SONGBIRD`, etc.
- Prevents ecosystem drift on future primal rename operations.

### Test Extraction
- `ipc/error.rs` (719L) → `error.rs` (282L) + `error_tests.rs` (441L)
- All 40 IPC error tests pass unchanged from new location.

### Scenario Thickening (+8 unit tests)
- `s_cascade_drift`: intentional_fail_exists, checks_remotes
- `s_nucleus_integration`: primal_count, service_naming
- `s_gate_readiness`: active_gates, readiness_ordering
- `s_neural_routing`: all_primals_have_routes, capability_domain_coverage

### Final State
- 1014 lib tests, 0 failures
- 103 registered scenarios (EXPECTED_SCENARIO_COUNT aligned)
- KNOWN_DEBT: `("cascade-drift", 2)` — depot staleness (sporeGate rebuild pending)

---

## Cascaded To
- [x] GitHub (origin)
- [x] Forgejo (sovereign)
- [ ] Upstream overwatch audit pending

---

## Gaps for Upstream Teams

| Gap | Owner | Notes |
|-----|-------|-------|
| `cascade-drift` depot staleness | sporeGate | Binary depot ~309h stale; needs `cargo install` refresh |
| 68 single-test scenarios | primalSpring | Thickened 4 priority scenarios; 64 remain at 1 test |
| `covalent_mesh_trust.rs` (712L) | primalSpring | Approaching 800L; candidate for phase-based split |
| AI advisor flaky test | biomeOS | `ai_advisor::tests::test_check_availability_graceful_failure` — transient race |
