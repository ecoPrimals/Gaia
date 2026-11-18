# swarmVine — Wave 157g G72 DEPENDENCY TRIM

**Date**: August 10, 2026
**Wave**: 157g (G72 Dependency Pandemic Tier 1)
**From**: eastGate overwatch
**Primal**: swarmVine (#16)
**Commit**: `7e080d0`

---

## Summary

G72 Tier 1 compliance: audit and trim swarmVine's dependency graph.
swarmVine was already called out as lean (113 transitive deps) in the
stadial shift blurb. This commit makes it leaner.

## Changes

### Dead dependency removed
- **`toml`** — declared in workspace `Cargo.toml` but never imported in
  any `.rs` file. Removed entirely.

### Umbrella crate narrowed
- **`futures` → `futures-util`** — only `StreamExt` was used (in
  `tarpc_server.rs`). Replaced the full `futures` umbrella (which pulls
  `futures-executor`, `futures-channel`, `futures-sink`, `futures-task`,
  `futures-io`) with `futures-util` alone. `futures-util` is already a
  transitive dep via tarpc, so net zero new crates.

### Already compliant
- **tokio features**: `["macros", "rt-multi-thread", "signal", "net", "io-util", "time"]`
  — specific, not `["full"]`.
- **No C-backed crates** — pure Rust dependency tree.
- **No duplicate deps** — `hostname` only in core, not duplicated in server.
- **Zero dead deps** after this commit.

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Workspace deps | 13 | 12 (toml removed) |
| Server direct deps | 11 (futures) | 11 (futures-util, lighter) |
| Tests | 137 | 137 |
| Clippy | 0 | 0 |

## G72 assessment for swarmVine

swarmVine is G72-clean at Tier 1:
- No `tokio["full"]`
- No dead deps
- No umbrella crates where a sub-crate suffices
- No C-backed deps
- No duplicate deps across crates
- Specific feature flags throughout

No Tier 2 or Tier 3 actions needed (no HTTP deps, no axum, no wgpu,
no archaic patterns to excise).

---

*G72 Tier 1 clean. Dead dep removed, umbrella narrowed. swarmVine
remains the lean exemplar: 12 workspace deps, specific tokio features,
pure Rust, zero dead weight. 137 tests. Primal #16.*
