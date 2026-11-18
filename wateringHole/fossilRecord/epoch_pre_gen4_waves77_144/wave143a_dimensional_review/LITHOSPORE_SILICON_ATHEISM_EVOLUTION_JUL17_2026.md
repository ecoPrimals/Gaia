<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# lithoSpore / pseudoSpore — Silicon Atheism Evolution Pass

**Date**: Jul 17, 2026 | **Wave**: 144a | **From**: pseudoSpore/lithoSpore on ironGate
**Phase**: Post-deployment evolution — deep debt, idiomatic Rust, architecture cleanup
**Gate**: All gates remain EXCEEDED — 7/7 modules PASS, 75/75 science checks, 216 tests

---

## Summary

Full evolution pass on lithoSpore codebase. Silicon atheism applied (trait-based OS
abstraction), large files refactored, idiomatic Rust improvements, full clippy
pedantic + nursery clean. Zero TODOs, zero FIXMEs, zero mocks in production code.
All dependencies confirmed pure Rust. 216/216 tests pass.

---

## Changes

### Silicon Atheism — Platform Trait (litho-core)

Created `Platform` trait in `litho-core::platform` absorbing all 18 `#[cfg]` gates
across 7 files. Only 2 `#[cfg]` blocks remain (in `platform.rs::current()`).

| Method | What | Previous Pattern |
|--------|------|-----------------|
| `hostname()` | OS hostname discovery | `#[cfg(target_os)]` in spore.rs |
| `set_executable()` | chmod +x | `#[cfg(unix)]` in assemble, promote, scripts |
| `create_symlink()` | Unix symlinks | `#[cfg(unix)]` in assemble |
| `strip_binary()` | `strip` command | `#[cfg(unix)]` in promote |
| `runtime_dir()` | XDG_RUNTIME_DIR | `#[cfg(unix)]` in discovery, visualize |
| `uid()` | Process UID | `#[cfg(unix)]` in discovery |
| `uds_rpc()` | UDS JSON-RPC | `#[cfg(unix)]` in discovery |
| `uds_send()` | UDS raw send | `#[cfg(unix)]` in visualize |

Files refactored: `spore.rs`, `discovery.rs`, `assemble.rs`, `visualize.rs`,
`promote/mod.rs`, `promote/report.rs`, `emit_pseudospore/scripts.rs`.

### Large File Refactoring

| File | Before | After | Extraction |
|------|--------|-------|-----------|
| `main.rs` | 730 lines | 648 lines | `dispatch.rs` — symlink-based CLI dispatch |
| `domain_profile.rs` | 799 lines | 493 lines | `domain_profile/parse.rs` — field parsing |
| `audit/domain.rs` | 797 lines | 585 lines | `audit/derivation.rs` — derivation checks + PLUMED |

### Idiomatic Rust

- `provenance::endpoint_addr` → `Cow<'_, str>` (zero-copy when env-sourced)
- `braid::format_braid_summary` → `write!` macro (eliminates Vec<String> + join)
- `visualize.rs` → direct owned return (removes redundant clone)

---

## Test Results

- **216/216 tests pass** (51 litho-core + 53 pseudospore-core + 40 ltee-cli + 20 ltee-cli integration + 52 science modules)
- **0 clippy warnings** (pedantic + nursery)
- **0 cargo fmt diffs**
- **0 cargo doc warnings**
- **0 TODO/FIXME/HACK markers in .rs source**
- **75/75 science checks** at Tier 2
- **10/10 chaos/fault-injection tests**

---

## Dependency Audit

All workspace dependencies are pure Rust:

| Crate | Feature | Why Pure |
|-------|---------|---------|
| `blake3` | `pure`, `std` | No `cc` assembly backend |
| `flate2` | `rust_backend` | Uses `miniz_oxide` not system zlib |
| `ureq` | `rustls` | rustls TLS, not openssl |
| `zip` | `zlib-rs` | Pure Rust zlib implementation |

---

## Architecture After This Pass

```
litho-core (13 modules, domain-agnostic chassis):
  validation, tolerance, provenance, discovery, platform, spore,
  scope, braid, manifest, error, stats, env_vars, harness

pseudospore-core:
  domain_profile/ (mod.rs + parse.rs), blake3_manifest, braid_envelope,
  envelope, error, livespore, receipts, scope, tarball, validation

ltee-cli:
  main.rs + dispatch.rs + registry.rs + 21 subcommand modules
  audit/ (mod, completeness, domain, derivation, integrity, provenance)
  emit_pseudospore/ (mod, scope, manifest, index_map, figures, environment, scripts)
  promote/ (mod, report)
  grow/ (mod, stages, deploy, util)
  viz/ (mod, modules, baselines)
```

---

## Next Steps

- Upstream overwatch audit via cascade
- Review gaps found for upstream primal teams
- `ltee-cli` → `litho-cli` rename (cosmetic, future)
- Dynamic module loading / plugin architecture (future)

---

## Dependencies

| Direction | Primal | Impact |
|-----------|--------|--------|
| Upstream (blocked) | Songbird | TURN client library for actual relay IPC |
| Upstream (blocked) | BearDog | FIDO2/CTAP2 for SoloKey witness |
| Upstream (info) | sporePrint | Pipeline wiring for primals.eco |
| Upstream (info) | neuralSpring | ML surrogate integration (additive, not blocking) |

---

## For Upstream Teams

### Items for review

1. **Silicon atheism pattern**: `Platform` trait as reusable pattern for other primals
   needing cross-platform abstraction without `#[cfg]` proliferation.
2. **Zero source markers**: No TODO/FIXME/HACK remaining — all prior debt resolved
   or documented as upstream-blocked in `docs/UPSTREAM_GAPS.md`.
3. **Idiomatic patterns**: `Cow<str>` for zero-copy provenance chains — may benefit
   rhizoCrypt and loamSpine address resolution.
