# songBird — Wave 156d: ironGate Downstream Readiness

**Date**: August 4, 2026 | **Wave**: 156d | **From**: eastGate overwatch  
**Status**: GREEN | **Tests**: 14,840+ | **Clippy**: Zero warnings (pedantic + nursery)

---

## What Was Done

### 1. GIS Bond Expansion (footPrint Phase 2 Readiness)

Added missing external proxy bonds to `songbird-types/src/defaults/bonds.rs`:

| Bond | URL | Consumer |
|------|-----|----------|
| `arcgis` | `https://services.arcgis.com` | footPrint — primary ArcGIS FeatureServer endpoint |
| `usgs_eq` | `https://earthquake.usgs.gov` | footPrint — seismic hazard layer |

GIS bonds total: **13** (was 11). ALL_BONDS total: **22** (was 20).

These join the existing bonds: `osm`, `overpass`, `fema`, `arcgis1`, `arcgis2`, `nominatim`, `usgs`, `nrcs`, `michigan`, `mcgi`, `eastlansing`.

### 2. Inter-Gate Content Routing Path Verification

Audited and confirmed the `content.get` cross-gate dispatch path is fully operational:

```
Consumer (footPrint/tideGlass) calls:
  capability.call { capability: "content", operation: "get", routing: "any" }
    │
    ▼
songBird: local registry → no content provider found
    │
    ▼
forward_to_remote_gate():
  1. Fast path: cached peer_capabilities → best-path peer → direct TCP POST
  2. Slow path: iterate reachable peers, probe capabilities.list, dispatch
  3. TURN relay fallback: CGNAT/double-NAT scenarios
    │
    ▼
Remote gate songBird receives { routing: "local" } → prevents relay loops
  → resolves local nestGate content provider → UDS forward → response
```

Components involved:
- `remote_dispatch.rs` — full priority-sorted peer dispatch with TCP + TURN
- `ContentAnnouncementStore` + `discovery.content_peers` — "first-responder-serves" pattern
- `peer_has_capability()` — probes before dispatch (eliminates blind fan-out)
- `relay.forward` — cellMembrane integration point for mesh relay

### 3. REMAINING_WORK.md Cleanup

- Marked Windows IPC P1 stubs as RESOLVED (Wave 155i fixed both)
- Updated wave/version/date to 156d
- Documented ironGate downstream readiness status

---

## songBird Readiness for ironGate 5-Phase Execution

| Phase | songBird Role | Status |
|-------|---------------|--------|
| **Phase 1** (esotericWebb) | Mesh + federation for game networking IPC | READY |
| **Phase 2** (footPrint) | Drawbridge external proxy for GIS APIs (13 bonds allowlisted) | **READY** (this wave) |
| **Phase 3** (squirrel) | `capability.call` dispatch routing for signal.dispatch consumers | READY |
| **Phase 4** (westGate springs) | No songBird mesh needed (local compositions) | N/A |
| **Phase 5** (inter-gate mesh) | `mesh.connectivity_check` + `mesh.throughput` (shipped 155n) | READY |

---

## What Remains (songBird → ironGate)

All ops, not code:

1. **Phase 2 env config**: Set `SONGBIRD_DRAWBRIDGE_EXTERNAL_ALLOWLIST` with GIS bonds on ironGate
2. **Phase 5 live test**: Run `mesh.connectivity_check` between ironGate ↔ westGate once nestGate registers `capabilities: ["content"]`
3. **`content.get` E2E**: Requires nestGate on westGate to announce content capability + mesh peer connectivity

---

## Upstream Impact

| Team | Impact |
|------|--------|
| **biomeOS** | Can route `capability.call(content, ...)` to songBird UDS for cross-gate dispatch |
| **nestGate** | Must call `ipc.register` with `capabilities: ["content"]` + `mesh.capabilities_announce` for remote discovery |
| **footPrint** | Configure drawbridge external proxy (env vars) for GIS source access |
| **cellMembrane** | `relay.forward` integration point for mesh-routed envelopes is ready |

---

---

## Doc & Spec Hygiene (Wave 156d cleanup pass)

| Action | Count | Detail |
|--------|-------|--------|
| Specs archived | 11 | Stale Jan 2025 "Week X" specs, completed impl specs, superseded designs → `specs/archived/` |
| Specs remaining (active) | 20 | Production-relevant protocol/architecture specs |
| Root docs updated | 4 | README, REMAINING_WORK, CONTEXT, CONTRIBUTING — dates, versions, metrics |
| Crate READMEs fixed | 1 | `songbird-universal-ipc/README.md` — Windows Named Pipes marked implemented |
| Specs index rebuilt | 1 | `00_SPECIFICATIONS_INDEX.md` — reflects archival |
| TODO/FIXME in Rust source | 0 | Confirmed zero |
| Temp/backup debris | 0 | Clean workspace |
| `cargo clean` | 60.8 GiB | 54,083 build artifacts removed |

---

*songBird Wave 156d — ironGate downstream READY. GIS bonds expanded. content.get cross-gate path VERIFIED. Phase 5 mesh probes SHIPPED. 11 stale specs archived. 60.8 GiB cleaned. Zero P0s. 14,840+ tests, 31/31 crates clippy-clean.*
