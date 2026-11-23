# barraCuda — Deep Debt Remediation Handoff

**Date**: 2026-06-03
**Gate**: strandGate (192.168.1.132)
**Status**: COMPLETE — debt pass delivered, ready for upstream audit

---

## Summary

Post-Wave 74 deep debt remediation pass. Focus: modularity, error evolution,
visibility tightening, dependency freshness, test coverage expansion.

---

## Changes Delivered

### 1. btsp.rs Split (750L → 582L)

Extracted two cohesive modules from the monolithic BTSP implementation:

| Module | Lines | Responsibility |
|--------|-------|----------------|
| `btsp_negotiate.rs` | 138 | Phase 3 cipher negotiation, hex helpers |
| `btsp_wire.rs` | 44 | NDJSON read/write async helpers |
| `btsp.rs` (remaining) | 582 | Handshake, session, stream encryption |

### 2. thiserror Evolution

`HandshakeError` enum converted from bare `Debug`-only to `#[derive(thiserror::Error)]`
with structured `#[error("...")]` messages. Enables `Display` downstream without
manual `impl`.

### 3. Visibility Tightening

- `f_distribution_sf` in `stats.rs`: `pub(super)` → `fn` (private, only used internally)

### 4. btsp_wire Unit Tests

4 new async tests for NDJSON framing:
- `read_ndjson_valid_line` / `read_ndjson_empty_stream` / `read_ndjson_invalid_utf8`
- `write_ndjson_roundtrip`

### 5. Dependency Freshness

`cargo update` applied 26 transitive patches (Rust 1.87 compat). Zero breaking changes.

### 6. Lint Gate

`cargo clippy --workspace -D warnings` — zero warnings across all crates.

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| `btsp.rs` lines | 750 | 582 |
| IPC methods | 90 | 91 |
| Coverage tests | 255 | 261 |
| Clippy warnings | 0 | 0 |
| `cargo update` patches | — | 26 |

---

## Known Pre-existing Issues

- **Full `cargo test -p barracuda-core --lib` SIGSEGV**: Mesa `llvmpipe` crashes
  on software-only GPU path. Affected tests pass when filtered individually.
  Not a regression — hardware nodes are unaffected.

---

## Remaining Debt (P3 — no urgency)

| Item | Location | Notes |
|------|----------|-------|
| `ops/mod.rs` (764L) | barrel module | Large due to re-exports, not logic |
| `bin/barracuda.rs` (749L) | CLI entry | Approaching limit, watch on growth |
| Tensor clone optimization | `tensor.rs:304,399` | Arc-aware dispatch |
| `showcase/` fossilization | root | Inert, already gitignored targets |

---

## For Upstream Audit

- Method count: 91 (was 90 pre-debt)
- All root docs updated (README, CONTEXT, REMAINING_WORK, STATUS, sporeprint)
- Zero TODOs in production code referencing completed work
- No mocks in production — all isolated to `#[cfg(test)]`
