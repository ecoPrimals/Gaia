# CATHEDRAL Deep Evolution — Owned Code Pass

**Date**: 2026-05-15
**From**: CATHEDRAL (lithoSpore + foundation + petalTongue)
**For**: primalPing, upstream primal teams, petalTongue collaborators

## Summary

Three-repo deep debt pass completed: lithoSpore, petalTongue, and
foundation. Four monolithic files (4,253 combined lines) refactored,
hardcoding evolved to capability-based discovery, UDS RPC implemented,
21 tests added, workload skip patterns standardized.

## lithoSpore Changes

### Refactoring (Phase 1)

| File | Before | After |
|------|--------|-------|
| `litho-core/src/viz.rs` | 1248 lines, 7 module + 7 baseline adapters + dashboard + tests | `viz/mod.rs` (API), `viz/modules.rs` (m1–m7), `viz/baselines.rs` (Barrick tools) |
| `ltee-cli/src/main.rs` | 994 lines, CLI + 6 subcommands + socket discovery + types | `main.rs` (thin wiring), `validate.rs`, `visualize.rs`, `verify.rs`, `ops.rs` |

### Capability Evolution (Phase 2)

- `127.0.0.1` fallbacks → `$PRIMAL_HOST` with `resolve_primal_host()`
- Fixed primal env keys → `has_any_capability_env()` runtime enumeration
- Fixed socket paths → `resolve_xdg_runtime()` XDG-standard discovery
- Fixed connectivity hosts → `DEFAULT_CONNECTIVITY_HOSTS` constant + `$LITHO_CONNECTIVITY_HOSTS` override

### Discovery Completion (Phase 3)

- **UDS RPC transport implemented**: `rpc_uds()` via `UnixStream` — matches TCP `rpc_call()` pattern
- `parse_discovery_response` updated for UDS `socket` field
- 13 unit tests + 8 integration tests added to `ltee-cli`

## petalTongue Changes

### Refactoring (Phase 4)

| File | Before | After |
|------|--------|-------|
| `src/web_mode.rs` | 1167 lines | `web_mode/mod.rs` (Axum routing + handlers), `web_mode/nestgate.rs` (NestGate client) |
| `petal-tongue-ui/src/scene_viewer.rs` | 864 lines | `scene_viewer/mod.rs` (orchestration), `scene_viewer/interaction.rs` (camera/click/hover), `scene_viewer/parameters.rs` (parameter strip) |

### Capability Evolution (Phase 5)

- 6 `#[allow(dead_code)]` → `#[expect(dead_code, reason = "...")]` with
  SceneGraph supersession documented per-function:
  - `draw_heatmap`, `draw_genome_track`, `draw_circular_map`, `draw_fieldmap`, `draw_spectrum` (domain_charts)
  - `paint_scene` (scene_paint — superseded by scene_bridge::paint with hit-map tracking)

### For petalTongue Upstream Collaborators

The refactored module structure is clean:
- No leftover monolith files
- All exports through `mod.rs` public API
- Existing call sites in `app/panels.rs` and `main.rs` updated

Validation sketches from lithoSpore `litho-core::viz` provide `DataBinding`
adapters for all 7 LTEE modules and 7 Barrick Lab baseline tools. The
`litho visualize` command pushes live dashboards via UDS IPC. These can
serve as target patterns for further petalTongue visual evolution.

## foundation Changes

### Data Integrity (Phase 6)

| Item | Status |
|------|--------|
| `deploy/fetch_sources.sh` — Thread 5-ML | Added `fetch_thread05_ml()` + dispatch entry |
| Workload skip patterns | Added `[skip]` sections to 14 workloads (airspring, hotspring, groundspring) |
| WCM workload data checks | Changed `[FAIL]` → `[SKIP]` for missing data (not-yet-fetched ≠ failure) |
| `deploy/backfill_hashes.sh` | Confirmed operational (127 lines); awaits `.data/` population |
| Paper map dedup | Verified clean — no duplicate paper ID 10 |
| WCM targets | Reviewed `validation/wcm-20260509/` — 0/24 targets have validation evidence, all remain `validated = false` |
| README quick-start | Fixed stale `cd ../../` paths → env-var-based resolution |
| Validation summary | Fixed `sporeGarden/foundation` → `gardens/projectFOUNDATION` |

## Build Verification

All three workspaces pass:
- `cargo check --workspace` — clean
- `cargo test --workspace` — all pass
- `cargo clippy --workspace` — zero warnings
- Foundation deploy scripts — `bash -n` syntax valid

## Upstream Items Needing Attention

| Item | Owner | Priority |
|------|-------|----------|
| Songbird TURN client library | Songbird team | Medium — blocks actual TURN relay IPC |
| Module 5 BioBrick DOI | External (Nat Comms) | Medium — blocks scaffold → live |
| rhizoCrypt DAG RPC wire format | rhizoCrypt team | Medium — blocks foundation Phase 2 |
| ToadStool working_dir trust | ToadStool team | Low — blocks workload execution under orchestrator |
| python3 baseline gate for gs-python-baselines | groundSpring team | Low — workload now has `[skip]` guard |

## Files Modified (summary)

### lithoSpore
- `crates/litho-core/src/viz/` — new module tree (3 files)
- `crates/ltee-cli/src/{validate,visualize,verify,ops}.rs` — new subcommands
- `crates/litho-core/src/discovery.rs` — UDS RPC, capability evolution
- `crates/ltee-cli/tests/cli_integration.rs` — new integration tests
- `docs/UPSTREAM_GAPS.md` — updated with deep evolution pass
- `docs/ARCHITECTURE.md` — updated crate diagram

### petalTongue
- `src/web_mode/` — refactored module tree (2 files)
- `crates/petal-tongue-ui/src/scene_viewer/` — refactored module tree (3 files)
- `crates/petal-tongue-graph/src/chart_renderer/domain_charts/mod.rs` — dead_code annotations
- `crates/petal-tongue-graph/src/chart_renderer/scene_paint.rs` — dead_code annotation

### foundation
- `deploy/fetch_sources.sh` — Thread 5-ML function + dispatch
- `workloads/**/*.toml` — skip patterns (14 files)
- `validation/handbacks/UPSTREAM_AUDIT_PREP_MAY15_2026.md` — updated
- `validation/wcm-20260509/VALIDATION_SUMMARY.md` — path fix
- `README.md` — quick-start path fix
