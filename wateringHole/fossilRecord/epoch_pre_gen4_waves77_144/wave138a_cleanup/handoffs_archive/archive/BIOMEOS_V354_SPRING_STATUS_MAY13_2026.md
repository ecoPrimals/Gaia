# biomeOS v3.54 — `biomeos.spring_status` for Tier 2 Notebook Integration

**Date**: May 13, 2026
**Commit**: `5d78a449`
**Trigger**: projectNUCLEUS deep debt audit — minor flag for biomeOS

## Context

projectNUCLEUS proposed `biomeos.spring_status` (which springs have binaries
available, workload counts, last validated timestamp). `composition.status`
partially covers this (primal health + resource pressure) but lacks binary
discovery and workload counts.

**Decision**: Add `biomeos.spring_status` as a dedicated method for notebook
integration, keeping `composition.status` focused on adaptive daemons.

## New Method

### `biomeos.spring_status`

**Parameters**: `{}` (no params required)

**Response**:
```json
{
  "primals": [
    {
      "name": "beardog",
      "display_name": "BearDog",
      "binary_available": true,
      "binary_path": "/opt/plasmidBin/primals/beardog",
      "runtime_state": "active",
      "capabilities": ["security", "crypto"],
      "last_health_check": "2026-05-13T17:00:00Z"
    },
    {
      "name": "songbird",
      "display_name": "SongBird",
      "binary_available": false,
      "binary_path": null,
      "runtime_state": null,
      "capabilities": [],
      "last_health_check": null
    }
  ],
  "workload_count": 5,
  "workloads_running": 1,
  "topology_version": 7
}
```

### Field Semantics

| Field | Source | Description |
|-------|--------|-------------|
| `name` | `primal_names::CORE/PROVENANCE/SPRING/AUXILIARY_PRIMALS` | Lowercase primal ID |
| `display_name` | `primal_names::display::for_id()` | Human-readable name |
| `binary_available` | Disk scan of plasmidBin directories | Whether a binary exists |
| `binary_path` | Same scan | Resolved path, or null |
| `runtime_state` | `LifecycleManager::get_status()` | active/degraded/dead, or null if unregistered |
| `capabilities` | `ManagedPrimal::deployment_node` | Declared capability domains |
| `last_health_check` | Lifecycle state | RFC 3339 timestamp for active primals, null otherwise |
| `workload_count` | `GraphHandler::executions` | Total graph executions (all states) |
| `workloads_running` | Same, filtered | Executions with state == "running" |
| `topology_version` | `LifecycleHandler::topology_version` | Monotonic composition counter |

### Binary Discovery

Uses the same search order as `primal_spawner::discover_primal_binary`:
1. `$ECOPRIMALS_PLASMID_BIN`
2. `$BIOMEOS_PLASMID_BIN_DIR`
3. `./plasmidBin`
4. `../plasmidBin`
5. `../../plasmidBin`

With architecture-aware patterns (`{name}_{arch}_{os}_musl/{name}`, etc.)

### Relationship to `composition.status`

| Method | Purpose | Consumers |
|--------|---------|-----------|
| `composition.status` | Runtime health for adaptive daemons | pappusCast, projectNUCLEUS infra |
| `biomeos.spring_status` | Binary + runtime availability for notebooks | JupyterHub Tier 2, UI dashboards |

Both share the `topology_version` counter and lifecycle state. `spring_status`
adds binary discovery and workload counts; `composition.status` adds
`resource_pressure` and `active_users`.

## Tests Added

3 new tests:

1. `test_spring_status_returns_expected_shape` — Validates response structure
2. `test_spring_status_includes_core_primals` — Core + provenance primals present
3. `test_spring_status_has_display_names` — Display name mapping correct

## Files Changed

| File | Change |
|------|--------|
| `handlers/lifecycle.rs` | +164 — `spring_status()`, `binary_search_dirs()`, `probe_binary()`, `with_executions()` |
| `neural_api_server/mod.rs` | +2 — Wire executions into lifecycle handler |
| `routing.rs` | +5 — `SpringStatus` route + dispatch |
| `routing_tests.rs` | +98 — 3 tests |

## Codebase Health

- `cargo fmt --check` ✅
- `cargo check` ✅
- `cargo clippy -D warnings` ✅
- `cargo test --workspace` ✅ (0 failures)
