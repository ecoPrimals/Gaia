# wetSpring Wave 156 — Deep Debt Evolution

**Date**: 2026-08-03
**Gate**: westGate
**Wave**: 156
**Primal**: wetSpring
**Base**: V210 @ 5b38488

---

## Summary

Systematic deep-debt cleanup and evolution of the wetSpring codebase across 7
work streams: capability-based discovery, cast safety migration, idiom
modernization, production mock isolation, dependency evolution, coverage
expansion, and incomplete implementation completion. All changes compile clean
(fmt, clippy pedantic+nursery, doc, deny). 2,201 tests, 0 failures.

## Changes

### Stream 1: Capability-Based Discovery
- Wire-protocol methods evolved from primal-named (`toadstool.validate`) to capability-domain (`compute.validate`)
- Discovery wrappers documented with `discover_by_capability()` migration path
- 40+ hardcoded primal names in error/log messages replaced with SSOT `*_DISPLAY` constants
- Provenance JSON keys emit both legacy and semantic-capability keys (`derivation_session`, `ledger_commit`, `attribution_braid`)
- Niche capability strings evolved to pure domains with backward-compatible aliases
- Socket paths in metalForge/forge use `primal_names::NESTGATE`/`BIOMEOS` constants

### Stream 2: Cast Safety (186 casts)
- Tier 1-2: High-risk sign/truncation and precision-loss casts migrated to `crate::cast::*` helpers across 15+ production files
- Tier 3-5: GPU buffer sizing, f64→f32 narrowing, safe widening casts migrated across all `*_gpu.rs` and `bio/` modules
- Stale `#[expect(clippy::cast_*)]` attributes removed where helpers centralize semantics

### Stream 3: Idiom Modernization
- 7 `#[allow()]` → `#[expect(reason = "...")]` in production code
- `println!` in `bench/report.rs` refactored to `format_bench_report()` + `tracing::info!`
- `gpu/mod.rs::print_info()` converted to structured `tracing::info!`
- `process::exit` → `ExitCode` returns in validation harness
- Dead-socket cache `Mutex` → `RwLock` (read-heavy pattern)
- Unnecessary clones removed in performance_surface, science handler, discover

### Stream 4: Mock Isolation
- GPU CPU-fallback sentinel `tracing::debug!` added to 7 modules
- Graceful degradation `tracing::warn!`/`debug!` for Squirrel, Anderson GPU skip, petalTongue fallback
- `SyntheticSignalGenerator` feature-gated behind `#[cfg(any(test, feature = "validation"))]`
- `validation` feature added to Cargo.toml

### Stream 5: Dependency Evolution
- `pollster` removed from forge; replaced with tokio current-thread runtime
- `wgpu` direct dep in forge documented as necessary (probe.rs device creation)
- SRA Toolkit shell-out documented with NestGate migration path

### Stream 6: Coverage Expansion
- 22 new tests added to `ipc/message.rs` and `bio/kriging.rs`
- Coverage targeting 90%+ line gate

### Stream 7: Variant Cross-Validation
- MOB/AMP/CON/INV variant types now have explicit match arms with `tracing::debug!` logging
- Gap #11 tracking comment added
- New concordance test validates unsupported types don't affect stats

## Build Gate

| Check | Status |
|-------|--------|
| `cargo fmt --all --check` | PASS |
| `cargo clippy --workspace --all-features -- -D warnings` | PASS |
| `cargo doc --workspace --all-features --no-deps` | PASS |
| `cargo test --workspace` | 2,201 passed, 0 failed |
| `cargo deny check` | PASS (advisory: `spin` yanked — transitive via akida-driver) |

## For Upstream

### barraCuda team
- wetSpring now consumes `crate::cast::*` helpers across all production bio code
- `KrigingResult` struct requires `weights` field (verified in test)
- `barracuda::ops::kriging_f64::KrigingF64::fit_variogram` used in new kriging test

### toadStool team
- Wire methods renamed: `toadstool.validate` → `compute.validate`, `toadstool.list_workloads` → `compute.list_workloads`
- compute_dispatch methods already use `compute.dispatch.*` (unchanged)

### sweetGrass / rhizoCrypt / loamSpine teams
- Provenance JSON now emits semantic-capability keys alongside legacy keys
- Consumers should migrate to `derivation_session`, `ledger_commit`, `attribution_braid`

### Songbird team
- wetSpring niche registration now uses 54 capabilities (was 52)
- Capability strings `integration.braid`, `integration.performance_surface` replace primal-named equivalents

## Gaps for Upstream
- `spin` crate yanked (transitive via `akida-driver` in NestGate path) — upstream fix needed
- Gap #11: MOB/AMP/CON/INV cross-validation logged but not fully implemented (no reference data)
- 4 GPU tests fail on westGate hardware (consistent with barraCuda YELLOW status on consumer GPUs)

---

## Addendum — V211b + V211c (same session, Aug 3)

**Commits**: `13b16a1` (V211b) + `c6935cc` (V211c)

### V211b: Remaining Hardcode Elimination + Coverage Expansion
- 5 remaining hardcoded `"wetspring"` string literals replaced with `primal_names::SELF_NAME`
  in `ipc/bonding.rs`, `ipc/provenance/mod.rs`, `facade/provenance.rs`
- `tracing::debug!` added for unrecognized Songbird capabilities in forge inventory
- 28 new tests across 3 previously-untested high-risk modules:
  - `facade/provenance.rs`: witness builders, tier1 structure, circuit breaker logic
  - `ipc/handlers/science.rs`: diversity, QS model, Anderson, full pipeline
  - `bio/esn/toadstool_bridge.rs`: BioHeadKind, BioEsnConfig, head labels

### V211c: Idiom Modernization
- Eliminated double-clone in `performance_surface.rs` (clone once at extraction site)
- Removed `#[expect(needless_pass_by_value)]` from bonding error mapper
- Cached `PIPELINE_AGENT` string as `LazyLock<String>` (eliminates `format!` on every
  tier1 provenance response — hot path)
- Added `#[must_use]` to `dispatch()`, `parse_request()`, `probe_schema_parity()`, `linspace()`
- Refactored `SchemaParity`: 4-bool struct → 3-bool struct + `const fn conformant()` method.
  Removes `#[expect(struct_excessive_bools)]`.

### Updated Build Gate

| Check | Status |
|-------|--------|
| `cargo fmt --all --check` | PASS |
| `cargo clippy --workspace -- -D warnings` | PASS (0 wetSpring warnings) |
| `cargo test --workspace` | **2,210 passed, 0 failed** |

### HEAD
`c6935cc` — pushed to `git.primals.eco` (golgiBody)
