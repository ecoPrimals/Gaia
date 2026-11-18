# sporePrint Overwatch AAR — Wave 148b

**Date**: Jul 18, 2026 | **From**: eastGate overwatch (primalSpring perspective)
**Scope**: 2 LIVE products, registry refresh, maturity evolution, debt calibration

---

## What Happened

The Wave 148b blurb reported 2 products LIVE on the sovereign mesh
(footPrint on sporeGate, esotericWebb on flockGate). sporePrint did not
reflect this — product pages said "scaffold"/"architectural", entity
registry lacked test counts for 4 entities, and primalSpring KNOWN_DEBT
was over-calibrated for eastGate. Overwatch sweep fixed all of these.

### sporePrint commit `351c6cd`

| Area | Change |
|---|---|
| **New maturity level** | `live` added to shortcode, CSS (green badge), spore-validate `MaturityLevel` enum |
| **footPrint** | scaffold → LIVE; PROXY_PATH marked done (songBird drawbridge shipped); tests=266 in registry |
| **esotericWebb** | architectural → LIVE on gate; 472 tests, 6/9 primals, live surfaces table added |
| **cellMembrane** | Added tests=1100, updated description (gate.enroll 7-phase) |
| **primalSpring** | tests 1273→1203 (calibrated), totals adjusted (spring -70, total -70) |
| **living-systems** | Added footPrint + esotericWebb to deploying table, northGate to gate table |
| **products/_index** | footPrint: "LIVE" not "Partially live"; esotericWebb added under Creative Products |
| **llms.txt** | footPrint LIVE, esotericWebb LIVE on flockGate |
| **CONTEXT.md** | Wave 148b, 2 LIVE products milestone |

### primalSpring commit `3c766161`

| Change | Detail |
|---|---|
| `sporeprint-pure-primal-parity` | Removed from KNOWN_DEBT (passes on eastGate — composition graph present) |
| `graphenegate-readiness` | 2→1 (only aarch64 depot absent; deploy_pixel now present) |

---

## What Went Well

- **primalSpring overwatch drove concrete fixes**: entity registry gaps,
  stale product pages, over-calibrated KNOWN_DEBT all found and resolved
  in a single session
- **Maturity model evolved**: new `live` level provides clear visual
  signal for deployed products — green badge distinguishes from
  blue/orange development badges
- **Validation chain clean**: spore-validate 289 tests pass, totals
  validated, Zola 302 pages / 0 orphan, primalSpring `registry_all_rust_tier_pass` passes

## What Didn't Go Well

- **KNOWN_DEBT drift**: upstream `3c70240c` re-added `sporeprint-pure-primal-parity`
  after we'd removed it in `863e28b3`. The composition graph exists on
  eastGate at `gardens/projectNUCLEUS/graphs/` — the upstream gate may
  lack it. Gate-specific debt calibration remains fragile.

## Metrics Post-AAR

| Metric | Value |
|--------|-------|
| sporePrint pages | 302 |
| sporePrint entities | 79 |
| spore-validate tests | 289 |
| Maturity levels | 8 (added: live) |
| LIVE products | 2 (footPrint, esotericWebb) |
| primalSpring KNOWN_DEBT | 1 (graphenegate only) |
| Ecosystem total tests | 116,402 |

---

## Upstream Gaps Remaining

| Gap | Owner | Priority |
|-----|-------|----------|
| `zone = "house1"` in cellMembrane topology enum | cellMembrane | P1 (blocks cascade) |
| esotericWebb systemd + Caddy `/webb/` route on golgi | sporeGate ops | P1 |
| E2E tutorial standard: known locations (footPrint) + demo scenario (esotericWebb) | product teams | P1 |
| `PROJECTS_PATH` CAS wiring | nestGate | P1 |
| `WS_PATH` agent bridge | petalTongue | P1 |
| squirrel: accept `null` params on health | squirrel | P1 |
| KNOWN_DEBT gate-specificity (passes eastGate, may fail other gates) | primalSpring | P2 |

---

*sporePrint `351c6cd` + primalSpring `3c766161`, both pushed to GitHub + Forgejo.*
