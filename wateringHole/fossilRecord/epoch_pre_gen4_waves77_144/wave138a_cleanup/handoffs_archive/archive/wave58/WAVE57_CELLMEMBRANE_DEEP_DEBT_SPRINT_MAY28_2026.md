# Wave 57 — cellMembrane Deep Debt Sprint

**Date:** 2026-05-28
**Repo:** `gardens/cellMembrane`
**Crate:** `cellmembrane-types` v0.1.0

---

## What Was Done

Full ecosystem-standard compliance sprint on `cellmembrane-types`:

### Code Quality

- `clippy::pedantic` + `clippy::nursery` enforced at workspace level — **zero warnings**
- `cargo fmt` enforced with `rustfmt.toml` (edition 2024, max_width 100)
- `#[must_use]` on all pure functions (~40 methods)
- `const fn` on all eligible methods (~30 methods)
- `use_self`, `doc_markdown`, `redundant_closure_for_method_calls` all resolved
- Zero `TODO`/`FIXME`/`HACK` — confirmed clean

### Typed Errors

- Added `thiserror` dependency (workspace-centralized)
- Created `error.rs` with `ConfigError` enum (Read + Parse variants)
- `MembraneConfig::load()` now returns `Result<Self, ConfigError>` instead of `String`

### Coverage

- Before: **77.5%** (identity 0%, channels 37%, provider 38%)
- After: **95.8%** (all modules ≥ 90%, most at 100%)
- 67 new tests in `tests/coverage.rs` + expanded integration tests
- 4 doc-tests added to `lib.rs`, `Report`, `EnvelopeTopology`
- Total: **160 tests** (was 93)

### Architecture Evolution

- `DeployPaths` config type — substrate-agnostic path resolution (`[membrane.paths]`)
- `iter_binaries()` zero-copy iterator alongside existing `all_binaries()`
- SSH port inconsistency fixed — `SSH_PORT` constant used everywhere
- `sort_unstable()` where stability irrelevant

### Licensing

- scyBorg triple license files added at root: `LICENSE`, `LICENSE-ORC`, `LICENSE-CC-BY-SA`
- SPDX headers confirmed on all 12 source + 8 test files

### Dependency Governance

- `deny.toml` added — bans `openssl-sys`, `ring`, `native-tls`, vendor SDKs
- Workspace deps: `serde` + `toml` + `thiserror` only (all pure Rust)

### Build Performance

- Release build (cold): 4.0s
- Test execution (warm): 0.23s
- Incremental clippy: 0.4s

---

## What's Left / Upstream

### For primalSpring audit

- `cellmembrane-types` is now audit-ready per ecosystem standards
- All quality gates pass: pedantic clippy, fmt, doc, 95.8% coverage
- No unsafe, no C deps, no mocks in production, no TODOs

### Gaps for upstream primal teams

| Gap | Owner | Note |
|-----|-------|------|
| `composition.rs` ~12 lines uncovered | cellMembrane | UDP-only port paths — forward compat, never fires for current registry |
| `envelope.rs` Display impls ~16 lines | cellMembrane | Low value — only human-readable output |
| No CI in-repo | cellMembrane / infra | Relies on Forgejo hooks; should add `.forgejo/workflows/` |
| No property/fuzz testing | cellMembrane | Could add proptest for serde roundtrips |
| `deploy_membrane.sh` integration | projectNUCLEUS | Should consume `DeployPaths` from config |

### Sovereignty

- Zero violations detected
- No phoning-home, no vendor SDKs, no tracking
- All paths now configurable via `[membrane.paths]`

---

## Files Changed

```
M  Cargo.toml                         (workspace lints + thiserror dep)
M  crates/cellmembrane-types/Cargo.toml
M  crates/cellmembrane-types/src/*.rs  (all 11 source modules)
M  crates/cellmembrane-types/tests/*.rs (4 test files reformatted)
A  crates/cellmembrane-types/src/error.rs
A  crates/cellmembrane-types/tests/coverage.rs
A  LICENSE, LICENSE-ORC, LICENSE-CC-BY-SA
A  rustfmt.toml
A  deny.toml
M  README.md
```

---

## Next Session

- Push to Forgejo via SSH
- primalSpring upstream audit
- Consider `.forgejo/workflows/ci.yml` for automated quality gate
- Wave 58: evaluate whether `cellmembrane-types` is ready for crates.io
