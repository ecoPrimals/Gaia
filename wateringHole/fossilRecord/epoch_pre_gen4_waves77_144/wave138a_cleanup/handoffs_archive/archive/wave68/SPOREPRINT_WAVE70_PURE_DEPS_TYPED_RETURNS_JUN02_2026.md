# sporePrint Wave 70 — Pure Dependencies + Typed Returns

**Gate:** flockGate
**Date:** 2026-06-02
**Status:** COMPLETE

## Summary

Eliminated the last C toolchain dependency, synced the source registry, centralized
path constants, evolved stringly error returns to typed `Result`, and brought
integration test coverage to 101 tests across all subcommands.

## Changes

### Zero-C Dependency Graph
- `blake3 = { features = ["pure"] }` — eliminates `cc` build script entirely
- Combined with `flate2 rust_backend` → zero C compiler needed to build
- JSON-LD "zero C dependencies" claim now technically accurate

### Source Registry Parity
- `sources.toml` synced: 8 missing repos added (rustChip, plasmidBin, wateringHole,
  whitePaper, helixVision, blueFish, initioChem, cellMembrane)
- New `[infra]` type category for infrastructure repos
- `fetch-refresh` can now sync metrics for the complete entity registry

### Code Architecture — `paths.rs`
- New `paths.rs` module: 8 canonical path constants
- `require_content_dir()` helper replaces 3 duplicated guard patterns
- All path literals in main.rs, fetch.rs, provenance.rs reference `paths::` constants

### Typed Error Returns
- `fetch_and_refresh()` → `Result<FetchResult, Error>` (was `Vec<String>`)
- New `FetchResult` struct with `outcomes` + `clone_root`
- `?` propagation replaces stringified error handling

### Code Quality
- `links.rs`: `link_resolves()` deduplicates 2 identical resolution blocks
- `provenance.rs`: dead `chrono_free_now()` alias inlined
- `report.rs`, `certify.rs`, `fetch.rs`: unnecessary `clone()` calls eliminated
- `MockBackend` match arms merged for idiomatic pattern

### Integration Test Coverage
- 7 new tests: check-links, graph (with/without emit), certify (with/without emit),
  provenance --write, provenance --verify
- Total: 101 tests (79 unit + 19 integration + 3 refresh_write)

## Metrics

- Tests: 101 (up from 94)
- Clippy: zero warnings (pedantic + nursery)
- Unsafe: zero (`#![forbid(unsafe_code)]`)
- C deps: zero (was 1: `cc` via `blake3`)
- Modules: 15 (added `paths.rs`)
- Build: ~0.7s check, ~2.7s test

## Upstream Needs

- **airSpring**: 11 notebooks still hardcode `/home/eastgate/` in source `.ipynb`
  files. These render into sporePrint's `content/lab/notebooks/*.md` via
  `spore-validate render-notebooks`. Fix belongs in airSpring repo (not sporePrint
  markdown which is auto-generated).

## Next (remaining from EVOLUTION_QUEUE)

- DNS NS cutover (eastGate manual action) → archive GitHub Pages workflow
- NestGate CAS integration for content-addressed build outputs
- pseudoSpore gallery template (reads lithoSpore registry.toml)
- WCAG 2.1 AA audit + screen reader testing
