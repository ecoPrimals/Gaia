# cellMembrane Wave 147e — Zone Fix + esotericWebb Caddy + Composition Service Units

**Date**: Jul 17, 2026 | **From**: eastGate overwatch
**Wave**: 147e | **Priority**: P0/P1 (zone fix unblocks cascade, deploy infra)
**Status**: SHIPPED — 3 demand-signal items addressed

---

## Summary

Addressed 3 items from the 147e demand-signal blurb:
1. **P1 GAP FIX**: `ZoneLabel::House1` — unblocks cascade for northGate
2. **Caddy block**: esotericWebb at `primals.eco/webb/`
3. **Service units**: footPrint + esotericWebb NUCLEUS systemd units

## Changes

### 1. ZoneLabel::House1 (P1 — blocked cascade)

sporePrint AAR reported: `ecosystem_manifest.toml` has `zone = "house1"` for
northGate, but `ZoneLabel` only had `backbone, house2, garage, wan, unassigned`.
The unknown zone silently fell to `Unassigned`.

- Added `ZoneLabel::House1` variant with full serde roundtrip
- `from_manifest("house1")` → `House1`, `for_gate("northGate")` → `House1`
- `House1.requires_overlay()` → `true` (separate physical location, needs WG)
- `House1.has_l2_backbone()` → `false`
- northGate added to `KNOWN_MESH_GATES`, `KNOWN_GATES`, `mesh_address` (10.13.37.8)

### 2. GateRole::EsotericWebb + Caddy Block

- `GateRole::EsotericWebb` typed variant (same pattern as FootPrint/TideGlass)
- `SURFACE_DOMAIN = "primals.eco"` and `ESOTERICWEBB_PATH = "/webb/"` constants
- `caddy.generate` produces `primals.eco { handle /webb/* { ... } }` sub-route
- Gateway `default_routes_for_roles` includes Webb route on surface domain

### 3. NUCLEUS Service Units

- `deploy/systemd/footprint-server.service` — footPrint server on sporeGate
  - Binds on `:8090`, wires to NUCLEUS target, journal logging
- `deploy/systemd/esotericwebb-server.service` — esotericWebb on flockGate
  - Follows standard `server --socket` contract, wires to NUCLEUS target

## Test Impact

- 4 new tests (zone house1, mesh northgate, esotericwebb role/routes)
- Total: 1,100 tests (up from 1,096)
- 0 clippy warnings, 0 unsafe, 0 debt markers

## Upstream Gaps (Status After This Wave)

| Gap | Owner | Status |
|-----|-------|--------|
| `PROXY_PATH` drawbridge wiring | songBird | NOT STARTED |
| `PROJECTS_PATH` CAS wiring | nestGate | NOT STARTED |
| `WS_PATH` agent bridge | petalTongue | NOT STARTED |
| songBird BTSP → `gate.enroll` | cellMembrane | NEAR-TERM |
| songBird discovery schema | songBird | WAITING (esotericWebb) |
| bearDog crypto sigs | bearDog | WAITING (esotericWebb) |
| sweetGrass braid methods | sweetGrass | WAITING (esotericWebb) |

## Demand Signal Items Addressed

| Blurb Item | Status |
|-----------|--------|
| "Caddy blocks for footPrint API endpoints" | **SHIPPED** (Wave 147c) |
| "footPrint composition deploy — NUCLEUS unit" | **SHIPPED** (this wave) |
| "Caddy block for primals.eco/webb/" | **SHIPPED** (this wave) |
| "esotericWebb NUCLEUS service unit" | **SHIPPED** (this wave) |
| "zone = house1 variant" | **FIXED** (this wave) |

## Files Changed

- `crates/cellmembrane-types/src/cytoplasm.rs` — House1 zone, northGate mesh
- `crates/cellmembrane-types/src/identity.rs` — GateRole::EsotericWebb
- `crates/cellmembrane-types/src/service/constants.rs` — SURFACE_DOMAIN, ESOTERICWEBB_PATH
- `crates/membrane-shadow/src/caddy/mod.rs` — esotericWebb Caddy generation
- `crates/membrane-shadow/src/gateway/config.rs` — esotericWebb gateway routes
- `deploy/systemd/footprint-server.service` — NEW
- `deploy/systemd/esotericwebb-server.service` — NEW
- `README.md`, `GLACIAL_SHIFT_TRACKER.md` — wave 147e updates

---

*Closes: zone=house1 gap (sporePrint AAR), footPrint NUCLEUS unit (P0 demand),
esotericWebb Caddy + unit (critical path steps 2+3).*
