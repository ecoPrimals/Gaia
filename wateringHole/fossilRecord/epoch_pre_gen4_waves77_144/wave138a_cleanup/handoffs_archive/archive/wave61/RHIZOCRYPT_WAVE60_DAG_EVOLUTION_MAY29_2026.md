# rhizoCrypt — Wave 60: DAG Evolution (Branch/Diff/Merge/Federate)

**Date**: May 29, 2026
**Version**: 0.14.0
**Status**: IMPLEMENTED — 4 new methods live, all tests passing

---

## Summary

Implemented the 4 new DAG evolution methods requested by Wave 60 for rootPulse
signal graphs. These enable version control to emerge from graph composition
rather than requiring bash + git.

## New Methods

| Method | Signal Graph | What It Does |
|--------|-------------|--------------|
| `dag.branch` | rootpulse.branch | Fork session at checkout vertex — copies ancestor subgraph |
| `dag.diff` | rootpulse.diff, rootpulse.federate | Structural diff between two session frontiers |
| `dag.merge` | rootpulse.merge | Create merge vertex joining 2+ frontier tips |
| `dag.federate` | rootpulse.federate | Import vertices from remote peer (diff-based, cross-gate ready) |

## Implementation Details

### Full Stack Coverage

- **Core types**: `BranchRequest/Response`, `DiffRequest/Response`, `MergeRequest`, `FederateRequest/Response` in `service_types.rs`
- **Core logic**: `branch_session()`, `diff_sessions()`, `merge_branches()`, `federate_vertices()` on `RhizoCrypt`
- **tarpc trait**: 4 new trait methods + server implementations
- **JSON-RPC handler**: New `handler/branch.rs` module with `dispatch_branch/diff/merge/federate`
- **Niche**: 4 `MethodSpec` entries in `METHOD_CATALOG` (37 total), `PROVENANCE_ALIASES` and `SEMANTIC_ALIASES` updated
- **Capability registry**: 4 new entries in `capability_registry.toml` (stability: evolving)
- **Deploy graph**: 4 new capabilities in `graphs/rhizocrypt_deploy.toml`
- **Vertex**: New `clone_for_branch()` method for safe session forking

### Wire Patterns

All methods follow the existing `dag.event.append` / `dag.session.create` patterns:
- JSON-RPC 2.0 over UDS (newline-delimited)
- Discoverable via `capability.call("dag", "dag.branch", params)`
- `provenance.*` aliases supported (e.g. `provenance.branch` → `dag.branch`)
- Protected by readiness gate + method gate

### Cross-Gate Federation

`dag.federate` is designed for cross-gate execution:
- Accepts serialized vertices from remote peers
- Diff-based: vertices already present are skipped (O(1) existence check)
- Topological order expected from caller for correct parent relationships
- Returns updated frontier for coordination

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 1,646 | 1,654 |
| `.rs` files | 171 | 172 |
| Lines | ~53,341 | ~54,251 |
| METHOD_CATALOG | 32 | 37 |
| Clippy warnings | 0 | 0 |

## Test Coverage

8 new handler tests + 4 niche alias tests:
- `test_dag_branch_creates_forked_session`
- `test_dag_branch_invalid_vertex_returns_error`
- `test_dag_diff_between_sessions`
- `test_dag_merge_collapses_frontier`
- `test_dag_merge_rejects_single_parent`
- `test_dag_federate_imports_vertices`
- `test_dag_federate_skips_duplicates`
- `test_provenance_aliases_for_wave60_methods`

## DH-1 Status

rhizoCrypt is **Clean** — not listed among the 6 DH-1 offenders. Production
socket paths use tiered discovery (`$XDG_RUNTIME_DIR` → `/run/biomeos` → fallback).

## Next Steps (Wave 61–63)

- Provenance Trio E2E with loamSpine/sweetGrass in live compositions (Wave 55 item)
- rootPulse signal graph integration testing with live `dag.branch/diff/merge/federate`
- `dag.federate` cross-gate E2E when biomeOS `graph.execute` Phase B ships (Wave 65)
