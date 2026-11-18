# biomeOS v3.53 — Shadow Deploy for projectNUCLEUS H2

**Date**: May 13, 2026
**Commit**: `8e3f8307`
**Scope**: `composition.deploy.shadow` dry-run validation

## Summary

Implements `composition.deploy.shadow` — a read-only dry-run mode for
`composition.deploy` that validates deployment graphs without executing them.
No process spawning, no capability registration, no IPC side effects.

Designed for projectNUCLEUS H2 to pre-validate deployment configurations
before committing to a live deploy.

## New Method

### `composition.deploy.shadow`

**Parameters**: `{ "graph_id": "<id>" }`

**Response**:
```json
{
  "valid": true,
  "graph_id": "nucleus_complete",
  "version": "1.0",
  "node_count": 13,
  "coordination": "sequential",
  "phases": [["beardog"], ["songbird", "nestgate"], ["squirrel"]],
  "phase_count": 3,
  "capability_resolution": [
    {
      "node": "beardog",
      "capabilities": ["security"],
      "resolved_provider": "beardog",
      "resolvable": true
    }
  ],
  "integrity": {
    "content_hash": "abc...",
    "hash_match": true,
    "signature_valid": null,
    "genetics_tier": null,
    "acceptable": true
  },
  "validation_errors": [],
  "warnings": []
}
```

### Validation Pipeline

1. **Parse** — Loads graph from TOML (both neural `[[nodes]]` and deployment `[[graph.nodes]]` formats)
2. **Structural validation** — Unique node IDs, dependency existence, cycle detection (hard errors)
3. **Capability format** — `namespace.operation` lint on DeploymentGraph capabilities (soft warnings)
4. **Topological sort** — Kahn's algorithm produces execution phases (parallelism plan)
5. **Capability resolution** — Each node's capability checked against the live router
6. **Integrity** — Content hash, signature verification, genetics tier check

### Error Classification

- `validation_errors` → Hard failures (cycles, missing deps, duplicate IDs, parse errors)
- `warnings` → Soft advisories (unresolvable capabilities, format lints)

## GAP-34 Confirmed

`content.*` (CAS) and `storage.*` (blob) are intentionally distinct domains in
`capability_registry.toml`. Both route to NestGate but serve different purposes:

- `storage.*` — Key-value blob persistence (store, retrieve, delete, list, streaming)
- `content.*` — Hash-addressed immutable CAS with publishing semantics (put, get, publish, resolve, promote, collections)

This boundary is correct by design.

## biomeos-graph: Exposed Granular Validation

`GraphValidator` now exposes individual validation steps as public methods:

- `validate_unique_ids()` — Check node ID uniqueness
- `validate_deps_exist()` — Check dependency references resolve
- `validate_acyclic()` — Check for dependency cycles
- `validate_caps()` — Check capability namespace format (soft lint)

This enables consumers (like shadow deploy) to separate hard structural errors
from soft capability format lints.

## Tests Added

3 new tests (total workspace: 7,943+):

1. `test_shadow_deploy_nonexistent_graph_returns_error` — Error on missing graph
2. `test_shadow_deploy_valid_graph_returns_plan` — Validates response shape (phases, resolution, integrity)
3. `test_shadow_deploy_does_not_register_capabilities` — Confirms zero side effects

## Files Changed

| File | Change |
|------|--------|
| `crates/biomeos-atomic-deploy/src/handlers/graph/mod.rs` | +203 — `shadow_deploy()` method |
| `crates/biomeos-atomic-deploy/src/neural_api_server/routing.rs` | +7 — `CompositionDeployShadow` route + dispatch |
| `crates/biomeos-atomic-deploy/src/neural_api_server/routing_tests.rs` | +120 — 3 shadow deploy tests |
| `crates/biomeos-graph/src/validation.rs` | +20 — Granular public validation methods |

## Codebase Health

- `cargo fmt --check` ✅
- `cargo check` ✅
- `cargo clippy -D warnings` ✅
- `cargo test --workspace` ✅ (0 failures)

## biomeOS Meta-Tier Status

biomeOS remains **CLEAN** per the Glacial Debt Escalation audit (May 13, 2026).
No blocking gaps from spring compositions. Shadow deploy is the H2 niche
evolution target — now shipped.
