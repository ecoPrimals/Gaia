# cellMembrane Wave 147c — footPrint Caddy Blocks + Typed Composition Roles

**Date**: Jul 17, 2026 | **From**: eastGate overwatch
**Wave**: 147c | **Priority**: P1 (upstream gap delivery)
**Status**: SHIPPED — Caddy path-based routing for footPrint, typed GateRole variants

---

## Summary

Delivered the "Caddy blocks for footPrint API endpoints" upstream gap from
footPrint 145b. Also promoted `GateRole::FootPrint` and `GateRole::TideGlass`
from stringly-typed `Other(String)` fallbacks to first-class typed enum variants.

## Changes

### 1. Caddy Sub-Route Support

New `CaddySubRoute` type in `cellmembrane-types/src/caddy.rs`:
- Supports multiple path-based routes within a single Caddy domain block
- Renders as Caddy `handle` blocks (most-specific path first)
- `CaddyVhost.sub_routes` field (serde-defaulted, skipped when empty)

### 2. footPrint Caddy Block Generation

`caddy.generate` now produces path-based routing for `footprint.primals.eco`:

```
footprint.primals.eco {
    handle /api/* {
        reverse_proxy <inner>:8090    # footPrint server (CAS)
    }
    handle /ws {
        reverse_proxy <inner>:8080    # petalTongue WebSocket (agent bridge)
    }
    handle {
        reverse_proxy <inner>:8080    # petalTongue static (drawbridge)
    }
    header { ... security ... }
}
```

### 3. Typed Composition Roles

- `GateRole::FootPrint` — replaces `GateRole::Other("footprint")`
- `GateRole::TideGlass` — replaces `GateRole::Other("tideglass")`
- Full trait chain: `From<&str>`, `Display`, `Serialize/Deserialize`, `PartialEq`
- `as_capability()` maps both to `ServiceCapability::ContentServing`
- Gateway `default_routes_for_roles` updated to use typed matching

### 4. Constants

- `DEFAULT_PETALTONGUE_PORT: u16 = 8080` — parallel to existing bind address
- tideGlass Caddy upstream corrected from `DEFAULT_FOOTPRINT_PORT` to `DEFAULT_PETALTONGUE_PORT`

### 5. Helper Extraction

- `resolve_upstream_ip()` extracted from inline closure in `dispatch_caddy_generate`

## Test Impact

- 7 new tests (3 caddy sub-route, 4 gateway role)
- Total: 1,096 tests (up from 1,089)
- 0 clippy warnings, 0 unsafe, 0 debt markers

## Upstream Gaps (Remaining)

| Gap | Owner | Status |
|-----|-------|--------|
| `PROXY_PATH` drawbridge wiring | songBird | NOT STARTED |
| `PROJECTS_PATH` CAS wiring | nestGate | NOT STARTED |
| `WS_PATH` agent bridge | petalTongue | NOT STARTED |
| songBird BTSP → `gate.enroll` integration | cellMembrane | NEAR-TERM |
| `protokarya-wan-deploy` scenario | primalSpring | BLOCKED on deploy |

## Files Changed

- `crates/cellmembrane-types/src/identity.rs` — `GateRole::{FootPrint, TideGlass}` variants
- `crates/cellmembrane-types/src/service/constants.rs` — `DEFAULT_PETALTONGUE_PORT`
- `crates/cellmembrane-types/src/caddy.rs` — `CaddySubRoute`, `sub_routes` field, handle rendering
- `crates/membrane-shadow/src/caddy/mod.rs` — footPrint sub-routes, `resolve_upstream_ip`
- `crates/membrane-shadow/src/gateway/config.rs` — typed `GateRole::FootPrint`/`TideGlass` matching
- `README.md`, `GLACIAL_SHIFT_TRACKER.md` — wave 147c updates

---

*Closes upstream gap: "Caddy blocks for footPrint API endpoints" (footPrint 145b).
Partially closes: `protokarya-wan-deploy` Caddy config dependency.*
