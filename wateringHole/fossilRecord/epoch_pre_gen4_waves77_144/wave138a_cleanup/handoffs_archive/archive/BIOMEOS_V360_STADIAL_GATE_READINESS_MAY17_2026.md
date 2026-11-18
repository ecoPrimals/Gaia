# biomeOS v3.60 — Stadial Gate Readiness

**Date**: May 17, 2026 (PM)
**Author**: biomeOS team
**Audience**: primalSpring, all springs, all gardens, projectNUCLEUS
**License**: AGPL-3.0-or-later

---

## Summary

Response to Wave 22: Stadial Gate audit. All biomeOS-specific action items
from the audit are resolved in v3.60. Tests: 7,915 passing (0 new failures).

---

## Action Items Resolved

### 1. UPSTREAM ASK: Braid Signal Tier (wetSpring)

**Status**: SHIPPED

- Added `braid` as 5th atomic signal tier in `SIGNAL_TIERS` (signal.rs).
- Created `graphs/signals/braid_partial_update.toml`: 4-node graph
  (verify_dag_state → partial_dehydrate → weave_partial_braid → record_aglet).
- Created `graphs/signals/braid_complete.toml`: 4-node graph
  (seal_session → weave_final_braid → commit_to_ledger → notify_rootpulse).
- Updated `config/signal_tools.toml` with braid tool schemas for Squirrel.
- Signal graphs: 14 → 16 across 5 tiers.
- All 7 signal dispatch tests pass with updated assertions.

Wire format matches the proposed spec from
`WETSPRING_UPSTREAM_BIOMEOS_BRAID_SIGNAL_MAY17_2026.md`:
```
signal.dispatch { "signal": "braid.partial_update", "params": { ... } }
signal.dispatch { "signal": "braid.complete", "params": { ... } }
```

**Note**: `braid.partial_update` graph calls `dag.partial_dehydrate` on
rhizoCrypt. This method is part of rhizoCrypt's upstream ask (also in Wave 22).
If `dag.partial_dehydrate` is not yet shipped, the graph node will fail
gracefully — the signal framework handles missing capability calls as node
failures, not graph failures (node is `required = true` so the graph reports
partial success with the dehydrate step failed).

### 2. Version Scheme Documentation

**Status**: SHIPPED

Dual version scheme explicitly documented in README with a dedicated section:
- **Release train** (`v3.60`): README, CHANGELOG, git tags — downstream-visible
- **Workspace semver** (`0.1.0`): Cargo.toml — Rust crate API stability
- `is_orchestrator = true` confirmed unique to biomeOS

### 3. EVOLUTION_ROADMAP.md Review

**Status**: SHIPPED

Added Section 10: Stadial Gate Readiness with:
- Full checklist of cleared items
- Stadial phase items (in-progress)
- Degradation behavior table
- Downstream pairing table

### 4. `is_orchestrator = true` Verification

**Status**: CONFIRMED

Only present in `livespore-usb/x86_64/manifest.toml` under `[primals.biomeos]`.
No other primal has this flag.

---

## Additional Wire Standard Compliance (self-audited)

### capabilities.list response shape

Added top-level `"primal": "biomeos"` field to `capabilities.list` response.
Was returning `{ capabilities, details, count, domains }` — now returns
`{ capabilities, details, count, domains, primal }` per CAPABILITY_WIRE_STANDARD.

### identity.get as first-class Neural API route

Previously only handled on the HTTP API unix_server. Now wired as a dedicated
route in the Neural API routing table. Returns:
```json
{
  "primal": "biomeos",
  "role": "orchestrator",
  "version": "0.1.0",
  "capabilities": ["orchestration", "composition", "graph", "topology", "lifecycle", "signal"],
  "is_orchestrator": true,
  "transport": ["uds", "tcp", "http"]
}
```

### Stability Tier Annotations

Created `config/stability_tiers.toml` classifying all registered methods:
- **stable** (33 methods): Locked contract — health triad, capabilities,
  identity, announce, lifecycle, composition, graph, topology, signal, auth
- **maturing** (37 methods): Semantics fixed, shape may evolve — pipeline,
  continuous, protocol, BTSP, niche, capability metrics
- **experimental** (17 methods): Subject to change — inference, MCP, agent
- **internal** (26 methods): `neural_api.*` legacy aliases

---

## Universal Standards Checklist Results

| Item | Status |
|------|--------|
| Health triad | PASS — all three wired |
| UDS socket | PASS — `$XDG_RUNTIME_DIR/biomeos/biomeos.sock` |
| TCP fallback | PASS — `--port` flag |
| capabilities.list shape | PASS — `{ capabilities, count, primal }` |
| identity.get | PASS — canonical response |
| primal.announce | PASS — atomic registration with signal_tiers |
| Method naming | PASS — `{domain}.{operation}` standard |
| BTSP enforcement | PASS — mandatory when FAMILY_ID set |
| deny.toml | PASS — bans ring, openssl, aws-lc-sys |
| Edition 2024 | PASS |
| musl-static | PASS |
| Stability tiers | PASS — all methods annotated |

---

## Composition Gaps (biomeOS-owned)

| Gap | Status | Notes |
|-----|--------|-------|
| Cross-gate dispatch | LOW — Phase 2 | songBird pairing, not blocking |
| `nest.store` signal | PASS | Graph exists, tested |
| `spore.instantiate` | NOT IMPLEMENTED | lithoSpore ask R7, LOW priority |

---

## Files Changed

- `crates/biomeos-atomic-deploy/src/handlers/signal.rs` — added `braid` tier
- `crates/biomeos-atomic-deploy/src/neural_api_server/routing.rs` — added `IdentityGet` route
- `crates/biomeos-atomic-deploy/src/handlers/capability.rs` — added `primal` to capabilities.list
- `crates/biomeos-atomic-deploy/tests/signal_dispatch_tests.rs` — updated to 16 signals
- `graphs/signals/braid_partial_update.toml` — new signal graph
- `graphs/signals/braid_complete.toml` — new signal graph
- `config/signal_tools.toml` — braid tool schemas
- `config/stability_tiers.toml` — new stability tier config
- `specs/EVOLUTION_ROADMAP.md` — Section 10: stadial readiness
- `README.md` — v3.60, version scheme section, signal tiers
- `CHANGELOG.md` — v3.60 entry
- `CURRENT_STATUS.md`, `DOCUMENTATION.md`, `START_HERE.md` — version bumps
