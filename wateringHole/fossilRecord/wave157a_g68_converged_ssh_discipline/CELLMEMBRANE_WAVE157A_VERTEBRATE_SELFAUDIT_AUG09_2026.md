# cellMembrane Wave 157a — Vertebrate Self-Audit

**Date:** 2026-08-09  
**Commit:** `dcdc6c7`  
**From:** eastGate overwatch  
**Pushed to:** golgiBody (git.primals.eco)

---

## Summary

Response to Wave 157a VERTEBRATE EVOLUTION blurb — self-audit of cellMembrane's
dispatch surface vs capability registry, plus P1 FD exhaustion fix.

## Changes

### P1: LimitNOFILE=65536 (FD exhaustion prevention)

- New `DEFAULT_LIMIT_NOFILE: u64 = 65536` constant in `cellmembrane-types`
- New `limit_nofile: Option<u64>` field on `ServiceSpec`
- `to_systemd_unit()` renders `LimitNOFILE=65536` in all generated units
- Both `from_membrane_service()` and `generate_unit_content()` set the default
- **Impact**: All gates deploying with regenerated units will have the FD limit.
  Addresses biomeOS FD leak (P0-C) at the systemd level as a safety net.

### Dispatch/Registry Convergence

**5 missing dispatch commands wired:**

| Command | Handler | Function |
|---------|---------|----------|
| `freshness.check` | `dispatch_freshness` | Compares installed binary provenance against source HEAD |
| `freshness.publish` | `dispatch_freshness` | Publishes gate HEAD SHAs to `heads/<gate>.toml` |
| `topology.service` | `dispatch_topology` | Resolves primal binary for a capability wire name |
| `topology.roles` | `dispatch_topology` | Lists all gate→roles mappings from manifest |
| `topology.endpoint` | `dispatch_topology` | Resolves transport endpoint (UDS/TCP/relay) for gate+capability |

**New: `ServiceCapability::from_wire()`**

Parses wire-format capability names (e.g. `"crypto_signer"`) back into the
enum. Enables the `topology.service` and `topology.endpoint` CLI commands.

### capability_registry.toml — 75 → 103 entries

**28 new entries** covering previously unregistered dispatch namespaces:

| Namespace | Count | Key entries |
|-----------|-------|-------------|
| Mirror | 3 | `mirror_sync`, `mirror_sync_all`, `mirror_status` |
| Gateway | 4 | `gateway_health`, `gateway_config_generate`, `gateway_deploy_check`, `gateway_sporeprint_check` |
| Tower | 3 | `tower_status`, `tower_shadow`, `tower_benchmark` |
| Sovereign CI | 2 | `sovereign_ci_trigger`, `sovereign_ci_status` |
| Sign/provenance | 3 | `sign_activate`, `sign_verify`, `sign_status` |
| Deploy/lifecycle | 3 | `deploy_composition`, `deploy_graph`, `lifecycle_status` |
| Manifest | 3 | `manifest_info`, `manifest_repos`, `manifest_validate` |
| Harvest queue | 2 | `harvest_ingest`, `harvest_request` |
| Crash-loop | 1 | `gate_crash_loop` |
| Potential field | 2 | `potential_sense`, `potential_check` |
| Plasmid extended | 3 | `plasmid_staleness`, `plasmid_composition`, `plasmid_depot_sync` |
| Forgejo | 1 | `forgejo_version` |

## Metrics

- **1329 tests** passing (zero regressions)
- **0 clippy warnings**
- **103 registered capabilities** (up from 75)
- **Net: +196/-7 lines**

## Upstream Notes

- **biomeOS P0-C**: `LimitNOFILE=65536` is a systemd safety net, not a fix.
  biomeOS team must still fix the socket leak in the auto-discovery loop.
- **Remaining registry gap**: ~50 operational commands still unregistered
  (caddy sub-commands, relay internals, context.clear, etc.). These are
  operational internals rather than advertised capabilities.
- **native_braid.py → Rust**: Not started this session (1171L orchestrator,
  requires significant design work for parallel chunk architecture).
