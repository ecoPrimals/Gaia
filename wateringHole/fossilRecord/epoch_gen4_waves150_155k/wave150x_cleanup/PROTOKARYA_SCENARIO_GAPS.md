# protoKarya primalSpring Scenario Gaps — Wave 140a

**Date**: Jul 15, 2026 | **From**: eastGate overwatch
**Owner**: primalSpring team
**Priority**: P2 (required before Track 3 compositions can be declared "proven")
**Status**: **4/5 RESOLVED** — `protokarya-wan-deploy` remains (blocked on Caddy config)

---

## Context

primalSpring has 166 scenarios. protoKarya compositions are now covered
both **structurally** and at the **composition routing** level. 4 of the 5
identified gaps were closed on Jul 15 (Wave 140a sprint, eastGate).
Remaining gap: live WAN deployment validation (`protokarya-wan-deploy`).

## Existing Coverage (GREEN)

| Scenario | Tier | What |
|----------|------|------|
| `protokarya-composition-routing` | Rust | Capability routing for footPrint/tideGlass deps |
| `fp-api-proxy` | Rust | Drawbridge port, songBird ownership, capability.call chain |
| `drawbridge-bonds` | Rust | Bond tier semantics, bonding methods |
| `drawbridge-bond-registry` | Rust | Schema, ≥16 bonds, science API hosts |
| `drawbridge-weak-bond-ingestion` | Rust | Bond lifecycle → NestGate CAS → provenance chain |
| `drawbridge-http-routing` | Both | :7780 drawbridge vs :7700 federation, route schema |
| `science-drawbridge-parity` | Rust | songBird science bonds ↔ registry ↔ Caddy (3-way) |
| `depot-wan-serving` | Both | WAN depot HTTPS, checksums, signatures |

## 5 Identified Scenarios (4 RESOLVED, 1 REMAINING)

### 1. `footprint-drawbridge-live` — **RESOLVED** (ba18f738)

**What it proves**: USGS EPQS + FEMA NFHL fetch through songBird drawbridge
→ NestGate CAS hash stored → provenance chain verified.

**Phases**:
1. Structural: verify `drawbridge_bonds.toml` has footPrint consumer entries
2. Live: curl USGS EPQS elevation endpoint through `:7780/footprint/ext/epqs/`
3. Live: verify response stored in NestGate CAS (content.get returns same hash)
4. Live: verify provenance chain (sweetGrass attribution)

**Blocks on**: footPrint server composition deployed on sporeGate.

### 2. `tideglass-composition-routing` — **RESOLVED** (ba18f738)

**What it proves**: tideGlass deploy graph parses, capability deps resolve
(compute.submit, math.matvec, content.resolve), routing table routes all methods.

**Phases**:
1. Structural: parse tideGlass deploy graph TOML
2. Structural: all 7 validation module capabilities routable
3. Structural: drawbridge bonds (LINCS L1000, GEO, ChEMBL, NF Data Portal)
4. Structural: cross-feed with footPrint (if GIS overlay needed)

**Blocks on**: tideGlass cloned into `protists/` and deploy graph created.

### 3. `protokarya-cross-feed` — **RESOLVED** (ba18f738)

**What it proves**: Data ingested by footPrint (e.g. terrain tile) can be
consumed by tideGlass via `capability.call` across composition boundaries.

**Phases**:
1. Structural: both compositions register in capability registry
2. Live: footPrint stores a content hash via nestGate
3. Live: tideGlass resolves same hash via `content.resolve`

**Blocks on**: Both compositions deployed.

### 4. `drawbridge-consumer-parity` — **RESOLVED** (ba18f738)

**What it proves**: songBird `SCIENCE_BONDS` + `FOOTPRINT_BONDS` allowlists
exactly match `drawbridge_bonds.toml` consumer entries. No stale or missing
routes.

**Phases**:
1. Parse songBird route config for `:7780` consumer lists
2. Parse `drawbridge_bonds.toml` consumer entries
3. Assert exact bidirectional match (no surplus, no deficit)

**Blocks on**: Nothing — can be implemented now.

### 5. `protokarya-wan-deploy` — **REMAINING** (blocked on Caddy config)

**What it proves**: Caddy route on `*.primals.eco` serves a live composition.
HTTP 200 from `primals.eco/footprint/`, 200 from TOPO-VIS, correct
Content-Type, security headers present.

**Phases**:
1. Structural: Caddy config has blocks for all registered compositions
2. Live: curl each registered composition URL, assert HTTP 200
3. Live: verify security headers (HSTS, CSP, X-Frame-Options)

**Blocks on**: Nothing for existing surfaces — can validate footPrint now.

---

## Implementation Notes

- All 4 resolved scenarios follow standard pattern, registered in `mod.rs`
- `EXPECTED_SCENARIO_COUNT` = 166 (verified green on eastGate)
- Scenario #5 (`protokarya-wan-deploy`) requires `footprint_composition.toml`
  and Caddy block configuration from cellMembrane team

---

*4/5 gaps closed by primalSpring team (eastGate, Jul 15 2026, Wave 140a).
166 scenarios, 1199 tests, 0 failures. Remaining gap requires upstream
cellMembrane + footPrint server deploy.*
