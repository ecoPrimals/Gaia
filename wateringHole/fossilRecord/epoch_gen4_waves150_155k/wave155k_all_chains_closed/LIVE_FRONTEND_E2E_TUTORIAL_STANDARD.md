# Live Frontend E2E Tutorial Standard — Wave 148a

**Date**: Jul 18, 2026 | **From**: eastGate overwatch
**Applies to**: All live frontends (footPrint, esotericWebb, future)
**Priority**: P1 — required for each frontend going live

---

## Principle

Every live frontend must have a **guided experience** that doubles as an
**end-to-end verification suite**. Users get a tutorial. Operators get a
test harness. Same artifact, two audiences.

A "known location" (for GIS) or "demo scenario" (for composition) is a
curated entry point where all data sources, primal connections, and UI
features are verified working. If a known location fails to load its
expected data, that's an E2E failure — not just a UX gap.

---

## Pattern: Known Locations (footPrint)

### Implementation

Add `KNOWN_LOCATIONS` to `src/constants.ts`:

```typescript
export interface KnownLocation {
  readonly id: string;
  readonly name: string;
  readonly center: readonly [number, number];
  readonly zoom: number;
  readonly description: string;
  readonly expectedSources: readonly string[];
}

export const KNOWN_LOCATIONS: readonly KnownLocation[] = [
  {
    id: 'msu-campus',
    name: 'MSU Campus',
    center: [42.7249, -84.4815],
    zoom: 17,
    description: 'Michigan State University — buildings, parcels, power infrastructure',
    expectedSources: ['osm-buildings', 'osm-power', 'parcels', 'osm-fences'],
  },
  {
    id: 'el-downtown',
    name: 'Downtown East Lansing',
    center: [42.7369, -84.4838],
    zoom: 18,
    description: 'East Lansing downtown — zoning, parcels, dense OSM coverage',
    expectedSources: ['osm-buildings', 'parcels', 'zoning'],
  },
  {
    id: 'red-cedar',
    name: 'Red Cedar River',
    center: [42.7271, -84.4747],
    zoom: 17,
    description: 'Red Cedar floodplain — FEMA flood zones, water features, terrain',
    expectedSources: ['fema-flood', 'osm-water', 'elevation'],
  },
  {
    id: 'meridian-twp',
    name: 'Meridian Township',
    center: [42.7120, -84.4230],
    zoom: 17,
    description: 'Suburban residential — parcels, soils, road network',
    expectedSources: ['parcels', 'soils', 'mi-roads'],
  },
  {
    id: 'haslett-farms',
    name: 'Haslett Agriculture',
    center: [42.7480, -84.3960],
    zoom: 16,
    description: 'Agricultural area — soil types, terrain contours, large parcels',
    expectedSources: ['soils', 'elevation', 'parcels'],
  },
];
```

### UI: Location Dropdown

Add a `<select>` next to the geocoder input in `index.html`:

```html
<select id="location-picker" title="Jump to known location">
  <option value="">Known Locations…</option>
</select>
```

Wire it in `map.ts`:

```typescript
import { KNOWN_LOCATIONS } from '../constants.js';

function initLocationPicker(): void {
  const picker = document.getElementById('location-picker');
  if (!(picker instanceof HTMLSelectElement)) return;

  for (const loc of KNOWN_LOCATIONS) {
    const opt = document.createElement('option');
    opt.value = loc.id;
    opt.textContent = loc.name;
    picker.appendChild(opt);
  }

  picker.addEventListener('change', () => {
    const loc = KNOWN_LOCATIONS.find(l => l.id === picker.value);
    if (loc) {
      map.setView([...loc.center] as L.LatLngTuple, loc.zoom);
      picker.value = '';
    }
  });
}
```

Call `initLocationPicker()` from `initMap()`.

### E2E Verification

Each known location has `expectedSources`. A test can:

1. Navigate to the location
2. Draw a property boundary
3. Trigger discovery
4. Assert that each `expectedSource` returns data (not empty)
5. Assert terrain contours render (for elevation locations)
6. Assert FEMA flood zone loads (for flood locations)

This can be a primalSpring scenario (`footprint-known-locations-e2e`) or a
standalone Playwright/Puppeteer test in the footPrint repo.

---

## Pattern: Demo Scenarios (esotericWebb)

### Implementation

esotericWebb's equivalent is a **guided demo scenario** — a curated game
session that exercises composition with each connected primal.

Add `content/demos/` with YAML scenarios:

```yaml
# content/demos/parlor-walkthrough.yaml
id: parlor-walkthrough
name: "The Weaver's Parlor — Guided Tour"
description: "Meet the NPCs, use abilities, navigate scenes"
steps:
  - action: session.start
    expect: { status: "active" }
  - action: navigate
    target: "parlor-entrance"
    expect: { scene: "The Weaver's Parlor" }
  - action: examine
    target: "weaver"
    expect: { npc: true, dialogue: true }
  - action: use_ability
    ability: "perception"
    expect: { enrichment: true, flow_score_increase: true }
  - action: navigate
    target: "garden"
    expect: { scene_count_gte: 2 }
```

### E2E: Each step is verifiable

| Step | Primal exercised | What it proves |
|------|-----------------|----------------|
| `session.start` | nestGate (state) | State persistence works |
| `navigate` | petalTongue (rendering) | Scene rendering works |
| `examine` | sweetGrass (provenance) | Attribution chain works |
| `use_ability` | bearDog (crypto) | Signed action works |
| enrichment fires | songBird (mesh) | Mesh data flows |
| flow score | loamSpine (lineage) | Lineage tracking works |

---

## Standard Requirements (all live frontends)

| Requirement | Detail |
|-------------|--------|
| At least 3 known locations / demo scenarios | Enough to test different data sources / composition paths |
| Each location/scenario has `expectedSources` or `expect` | Machine-verifiable assertions |
| Dropdown or menu in the UI | Users can discover and use them |
| Works without address search | New users can explore immediately |
| E2E test runner | Either primalSpring scenario or in-repo test suite |
| First location loads on startup | Default should be a known location, not blank |

---

## Action Items

### footPrint team

1. Add `KNOWN_LOCATIONS` to `constants.ts` (5 locations as specified above)
2. Add `<select>` picker to toolbar
3. Wire picker in `map.ts`
4. Add E2E test (Playwright or primalSpring scenario)
5. Consider: URL hash support (`#msu-campus`) for deep linking

### esotericWebb team

1. Create `content/demos/` with at least 1 guided scenario
2. Add `demo` or `walkthrough` CLI subcommand
3. Wire demo playback in the session system
4. Add E2E test that runs the demo scenario and asserts each step

---

*Every live frontend is both a product and a test harness. Known locations
and demo scenarios serve users AND operators. If a known location breaks,
that's a deployment failure — not a feature request.*
