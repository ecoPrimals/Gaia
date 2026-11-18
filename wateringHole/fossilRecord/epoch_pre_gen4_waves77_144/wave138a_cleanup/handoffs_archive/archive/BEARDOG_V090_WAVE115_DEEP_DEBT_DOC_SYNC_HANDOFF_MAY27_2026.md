# BearDog Wave 115 + 115b — Deep Debt Cleanup & Root Doc Sync

**Date**: May 27, 2026  
**Version**: 0.9.0  
**Waves**: 115, 115b  
**Quality Gates**: `cargo fmt` clean, `cargo clippy -D warnings` clean, 14,987 tests passing (0 failures)

---

## Wave 115: Deep Debt Cleanup

### Orphan modules deleted (net -857 LOC)

| File | LOC | Status |
|------|-----|--------|
| `tunnel/genetic_healing.rs` | 434 | No `mod` declaration anywhere — dead code |
| `tunnel/simplified_seed_tunnel.rs` | 21 | No `mod` declaration — dead code |
| `tunnel/key_manager.rs` (tunnel-level) | 316 | Not in `tunnel/mod.rs` — orphan (distinct from `hsm/key_manager.rs` stub) |
| `tunnel/security_provider.rs` | 268 | Not in `tunnel/mod.rs` — orphan |

### Ionic bond test refactored (1165 LOC monolith → 5 domain modules)

| Module | Tests | Domain |
|--------|-------|--------|
| `tests/helpers.rs` | 0 (shared) | `sign_as_acceptor`, `sign_as_countersigner`, `propose_bond`, `accept_bond` |
| `tests/lifecycle.rs` | 12 | Propose/accept/verify/list/revoke + signature tampering |
| `tests/seal.rs` | 5 | Seal lifecycle, auth, revoke |
| `tests/contract.rs` | 10 | Sign/verify contract, TTL, deterministic hashing |
| `tests/cross_family.rs` | 6 | Cross-family propose/countersign/verify lifecycle |

All 33 ionic bond tests pass. Zero test changes — pure structural refactor.

### Other cleanup

- **`#[allow]` without reason** — `benchmarks/src/utils_tests.rs` bare `#[allow(clippy::float_cmp)]` → `#[expect(…, reason = "benchmark stats assert exact default values")]`
- **Hardcoded primal names** — Production comments: `loamSpine` (ionic_bond handler ×2) and `skunkBat` (ACME shadow_metrics) replaced with capability-agnostic wording
- **HSM capability_detector** — Stub documented: explains role, fallback to software HSM, future platform gates
- **Empty `key_manager.rs`** (HSM level) — narrowed to private `mod`, doc comment explains reserved purpose

---

## Wave 115b: Root Doc Sync & Debris Purge

### Date alignment (May 25 → May 27)

Updated across: README.md, CONTEXT.md, ROADMAP.md, START_HERE.md, ARCHITECTURE.md (header + footer), SECURITY.md, docs/README.md (May 15→27), docs/PRIMAL_CONTRACTS.md (May 15→27)

### Metric drift fixed

| Metric | Before | After | Files |
|--------|--------|-------|-------|
| Method count | "100+" | "127" | ARCHITECTURE.md diagram, START_HERE.md |
| Test count | 12,610 | 14,980+ | START_HERE.md |
| Test count | 14,940+ | 14,980+ | README.md, ARCHITECTURE.md |

### Stale references cleaned

- **`entropy/collect.rs`** — referenced nonexistent `scripts/setup-hardware-testing.sh` → now points to `docs/references/RUN_ENTROPY_TEST.md`
- **`ROADMAP.md` Wave 69b** — removed pre-fossilization showcase references and stale method counts from historical summary

### HTTP-era config templates annotated

Added header notes to `development.env`, `production.env`, `network-discovery.env.template` clarifying Unix socket JSON-RPC is the primary transport era.

---

## Remaining items (not blocking, for future waves)

| Item | Priority | Notes |
|------|----------|-------|
| Unused deps (`tokio-tungstenite`, `tokio-serde`, `mockito`, `wiremock`, bulk `tokio-test`) | LOW | Run `cargo machete` in dedicated pass |
| ACME CSR placeholder → real PKCS#10 via `rcgen` | LOW | Requires new dep; functional as-is |
| K8s discovery empty `discover_services_impl()` | LOW | Returns empty; DNS fallback works |
| ~60 deprecated constants migration | LOW | Tracked per crate; in-progress |
| `PRIMAL_CONTRACTS.md` handler breakdown (103→106 crypto, 8→12 ionic bond) | LOW | Need full method census |
| `specs/` status field drift (HSM Phase 1, Graph Security) | LOW | Specs are design docs |
| `crates/beardog-tunnel/src/main.rs` duplicate UniBin | LOW | Archive candidate |
| HTTP-era config templates full cleanup | LOW | Headers added; full rewrite deferred |

---

## Audit dimensions (post-cleanup)

| Dimension | Status |
|-----------|--------|
| Production files > 800 LOC | 0 |
| Unsafe code | 0 (forbid on 30 crate roots) |
| TODO/FIXME/HACK/XXX in `.rs` | 0 |
| Orphan `.rs` modules | 0 |
| Bare `#[allow]` without reason | 0 |
| Hardcoded primal names in production | 0 |
| Production `.unwrap()`/`.expect()` | 1 (documented HKDF expand) |
| Test count | 14,987 |
| Quality gates | All pass |
