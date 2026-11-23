# ToadStool S337–S339 Deep Debt Resolution

**Date**: Jul 21, 2026 | **Wave**: 150t | **Primal**: toadStool | **Gate**: eastGate

## Summary

Three sessions of deep debt resolution: hot-path allocation elimination, structural
refactoring of the 5 largest remaining production files, and a comprehensive Rust 1.96
clippy lint sweep across 251 files.

## S337 — Hot-Path Allocation Elimination + Structural Splits

- `detect_dispatch_mode` returns `Cow<'a, str>` instead of `String` — eliminates
  2–3 heap allocations per `compute.dispatch.submit` call
- `warm.rs` split (681L → mod.rs 110L + warm_steps.rs 584L)
- `operations.rs` split (654L → mod.rs 251L + encryption_ops 83L + key_ops 130L + permission_ops 229L)

## S338 — Structural Splits: 3 Large Files

- `rm_object_tree.rs` split (738→349L + channel_tree.rs 403L)
- `pmu_investigate/mod.rs` split (664→331L + phase_a.rs 126L + ungating.rs 276L)
- `opcodes.rs` split (658→62L dispatcher + 5 family modules)
- All `// Pending:` markers verified as legitimate active blockers

## S339 — Rust 1.96 Clippy Sweep

- 251 files modified for MSRV-safe lint resolution
- `duration_suboptimal_units` allowed workspace-wide (from_mins/from_hours require
  Rust 1.91+, MSRV is 1.85)
- `map_unwrap_or` → `is_ok_and`, `used_underscore_binding`, `suboptimal_flops` → `mul_add`,
  `needless_borrows_for_generic_args`, `unused_async`
- Dead features removed: `specialty/native-bindings`, `specialty/cross-compilation`,
  `examples/pure-ecosystem`, `examples/full-ecosystem`, `sandbox/macos-sandbox`
- Orphan `benches/` directory removed (3 files, no Cargo.toml refs)
- 5 fossil-marked docs removed (completed migrations, superseded specs)

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo clippy --workspace --all-targets -- -D warnings` | **CLEAN** (Rust 1.96) |
| `cargo fmt --all -- --check` | **0 diffs** |
| `cargo test --workspace --lib` | **9,252 tests, 0 failures** |
| Largest production file | **713L** (target <750L) |
| Production TODO/FIXME/HACK | **0** |

## Upstream Notes

- **Squirrel IPC (SQUIRREL_IPC_AAR_WAVE150d.md)**: Squirrel's `compute_client` still
  needs toadStool/barraCuda JSON-RPC method signatures for endpoint resolution. Action
  remains with compute primal teams to document/publish signatures.
- **Wave 150t `.unwrap()` count (3,657)**: Confirmed in prior sessions — these are
  all test-code unwraps. Production code has 0 unwraps by `clippy::unwrap_used` standard.
