# biomeOS Wave 119 Handoff — Structural Refactoring + Coverage

**Date**: 2026-06-20
**Version**: v4.31
**Gate**: eastGate
**Author**: biomeOS orchestrator

---

## Sprint Summary

Continued deep debt evolution with focus on structural refactoring of all monolithic
production files, dependency modernization, and targeted coverage expansion.

## Metrics

| Metric | Before (v4.30) | After (v4.31) | Delta |
|--------|----------------|---------------|-------|
| Tests | 8,378 | 8,446 | +68 |
| Line coverage | 88.28% | 88.37% | +0.09% |
| Region coverage | 87.95% | 88.02% | +0.07% |
| Function coverage | 89.91% | 89.58% | -0.33%* |
| Production >800 LOC | 1 (nucleus.rs 965) | 0 | -1 |
| Clones (neural_executor) | 24 | 15 | -9 |

*Function coverage slightly down because new test helper functions added (lower per-function
density); total covered functions increased.

## Structural Refactoring

All monolithic production files have been split into semantic module trees:

1. **nucleus.rs** (965L) → `nucleus/` (mod 86, types 393, local 361, remote 216)
2. **neural_executor.rs** (677L) → `neural_executor/` (mod 362, phase 146, dispatch 173)
3. **lifecycle.rs** (652L) → `lifecycle/` (8 submodules by JSON-RPC concern)
4. **capability_registry.rs** (648L) → `capability_registry/` (types, registry, server)
5. **neural_graph.rs** (643L) → `neural_graph/` (types, parsing, convert)
6. **paths.rs** (630L) → stays monolithic (documented: tightly coupled XDG hub)

## Dependency Upgrades

- **dashmap** 5.5 → 6.2.1 (reduces hashbrown duplication)
- **toml** 0.8 → 0.9.12
- bincode 1.3.3: remains blocked by tarpc upstream (RUSTSEC-2025-0141 acknowledged)

## Coverage Expansion (68 new tests)

- `capability_heuristics`: 0% → 100% (pure functions, 20 tests)
- `plasmodium/remote`: HTTP mock integration (11 tests)
- `lifecycle/helpers`: state serialization (7 tests)
- `orchestrator_health`: tokio::time::pause mock (5 tests)
- `p2p_coordination`: btsp + birdsong + integration (40 tests)
- `tower_orchestration`: early-exit + edge cases (19 tests)

## Quality Gates (all green)

- `cargo clippy --workspace --all-targets -- -D warnings` → 0 errors
- `cargo deny check` → advisories ok, bans ok, licenses ok, sources ok
- `cargo fmt --check` → clean
- Zero TODO/FIXME in Rust source
- Zero unsafe blocks in production
- Zero production files >800 LOC

## Remaining Coverage Gap (88.37% → 90% target)

The remaining 1.63% gap is in:
- Binary entry points (`main.rs`, `init.rs`) — require integration testing
- Systemd interaction code (`nucleus/local.rs`) — requires live system
- rootfs builder (`nbd.rs`, `builder/types.rs`) — requires privileged CI

These are not addressable via unit tests alone; require:
- e2e test infrastructure (NUCLEUS integration)
- Privileged CI runner with `/dev/nbd*`
- primalSpring live scenario expansion

## Upstream Audit Points

1. **tarpc/bincode**: Monitor tarpc for bincode v2 support or evaluate JSON transport
2. **rtnetlink thiserror 1→2**: Monitor upstream for thiserror 2.x support
3. **paths.rs monolithic**: Accepted as-is (630 LOC, documented rationale)
4. **Coverage plateau**: Library code is >92%; remaining gap is binary/systemd

## For Primal Teams

- No API changes in this sprint (pure refactoring)
- dashmap 6 and toml 0.9 are workspace-level; no primal-facing changes
- If depending on `biomeos-core::capability_registry::*` — imports unchanged via re-exports
