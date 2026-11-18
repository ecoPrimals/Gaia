# AAR: petalTongue Cross-Site Wiring — Grammar-of-Graphics Across the Ecosystem

**Wave 167 — October 8, 2026**
**Observer**: sporeGate (Artisan session)
**Duration**: ~90 minutes
**Companion subGen**: `BIOMEOS_HUD_PETALTONGUE_LIVE_WAVE167.md`

---

## Summary

petalTongue's server-side rendering engine is now wired into **4 independent sites** plus sporePrint's existing client-side WASM path. Each site has its own bridge JS that fetches local or cross-origin data, sends DataBindings over WebSocket to `wss://hud.primals.eco/ws`, and injects the returned SVG into the DOM. Total: **40 new visualization panels** across the ecosystem, all rendered by the same Rust grammar-of-graphics compiler. Sites remain architecturally independent — no shared state, no HUD unification.

---

## What Was Done

### Phase 1: Survey (5 parallel explorer agents)

Surveyed all 8 primals.eco sites for petalTongue wiring viability:

| Site | JS files | Data sources | petalTongue status | Decision |
|------|----------|-------------|-------------------|----------|
| **signal.primals.eco** | 4 files | dashboard.json, topology.json | ✅ 10 panels (prior session) | Already wired |
| **hud.primals.eco** | 3 files | Cross-origin signal data | ✅ 10 panels (prior session) | Already wired |
| **detroit.primals.eco** | 9 files (3,700 LOC) | DETROIT_NETWORK (91 nodes, 140 edges), graph.json, timeline API | ✅ **12 panels — wired this session** | Rich graph data → bar, heatmap, scatter, gauge |
| **thesis.primals.eco** | 0 files | None local — pulls from signal cross-origin | ✅ **8 panels — wired this session** | Live fleet metrics for the research paper |
| **sporeprint.primals.eco** | 1 file (viz-hydrate.js, 294 LOC) | Scene JSON via `data-viz-src` | ✅ Client-side WASM | Already wired — different rendering path |
| **clutch.primals.eco** | 1 file (graph-walker.js, 555 LOC) | graph.json (109 nodes, 157 edges) | ❌ Not wired | Repo is remote only (GitHub), not local |
| **barry/tuebor** | 0 files | No JSON endpoints | ❌ Not wired | Pure static text, no data to render |

### Phase 2: Detroit Wiring — `detroit-pt.js` (12 panels)

Created `/static/js/detroit-pt.js` — reads `window.DETROIT_NETWORK` (loaded by `network-data.js` on the `/network/` page) and renders 12 panels through petalTongue:

| Panel | Channel | Data source |
|-------|---------|-------------|
| Node Types | bar | `NODES` type distribution (actor, judge, political, institutional, enforcement) |
| Flow Types | bar | Edge flow counts (money, power, influence, position) |
| Communities | bar | Community detection cluster sizes |
| Nexus Coverage | bar | Cross-sector reach (education, political, enforcement, weaponization, legislative) |
| Tier Structure | bar | Enterprise hierarchy (Tier 1 principals → Tier 5 historical) |
| Dynasties | bar | Political family/faction clusters (Kilpatrick, Sabree, Banks-Flenory, mayoral) |
| Degree Distribution | scatter | In-degree vs out-degree per node |
| Geographic × Flow | heatmap | Regions × flow types — extraction geography |
| Bench Capture | gauge | Anderson disorder — captured judges ÷ total judges |
| Ownership Groups | bar | Shell entity cluster sizes |
| Money Trail | bar | Documented dollar flows through the network |
| Oversight Cycles | gauge | Closed loops of oversight failure |

**Mount point**: `/network/_index.md` — after the convergence box, before the footer.

### Phase 3: Thesis Wiring — `thesis-pt.js` (8 panels)

Created `/static/js/thesis-pt.js` — fetches `dashboard.json` + `topology.json` from `signal.primals.eco` and renders 8 panels through petalTongue:

| Panel | Channel | Data source |
|-------|---------|-------------|
| Fleet vs Human | gauge | `fleet_pct` — the paper's core finding |
| Machine Confidence | gauge | Timing CV — CV < 0.15 = machine |
| Entity Volume | bar | Classified entities ranked by request volume |
| Honest vs Deceptive | bar | Traffic split by header honesty |
| Infrastructure Type | bar | ASN types — datacenter vs cloud vs residential |
| Epitope Organisms | bar | Behavioral fingerprint clusters by IP count |
| Epitope Matrix | heatmap | Organisms × features (IPs, UA pool, blame%, has_lang) |
| Anderson Selectivity | gauge | S = max(P) − min(P) — Paper 43 |

**Mount point**: `content/_index.md` — before the footer, after the "Note to Fleet Engineers" section.

### Phase 4: CSP Update

Thesis used `csp_static` (`connect-src 'self'`) which blocked cross-origin fetch to signal and WSS to hud. Updated golgiBody Caddyfile:

```
# Before:
import csp_static

# After:
header Content-Security-Policy "default-src 'none'; script-src 'self' 'unsafe-inline' https://hud.primals.eco; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://signal.primals.eco wss://hud.primals.eco; form-action 'none'; frame-ancestors 'none'; base-uri 'self'; manifest-src 'self'"
```

Caddy reloaded via `/opt/membrane/caddy reload --config /etc/membrane/Caddyfile`.

### Phase 5: HUD Wiring — `hud-pt.js` (10 panels)

Created `/static/js/hud-pt.js` — same 10 panels as signal but rendered through same-origin WS. The HUD already fetches signal data via `hud-core.js`; the petalTongue bridge adds grammar-of-graphics deep analysis panels below the existing dashboard.

---

## Architecture Pattern

All bridges follow the same pattern:

```
[site]-pt.js                       Browser-side bridge
  │
  ├── fetch() ──→ data source      JSON data (local or cross-origin)
  │                                  signal: /dashboard.json, /topology.json
  │                                  detroit: window.DETROIT_NETWORK
  │                                  thesis: signal.primals.eco cross-origin
  │
  ├── transform() ──→ DataBinding  Channel-typed binding object
  │                                  {channel_type, id, label, values, ...}
  │
  └── rpc('pt.render_binding') ──→ wss://hud.primals.eco/ws
                                     │
                                     ▼
                                  petalTongue v1.7.0
                                  GrammarCompiler → SvgCompiler
                                     │
                                     ▼
                                  SVG response → DOM injection
```

**Key properties:**
- Each site is **independent** — no shared state, no HUD coupling
- The WS connection is to the **petalTongue rendering service**, not to the HUD's data layer
- Sites test individually; unification comes later
- Same Rust rendering engine serves all sites through one WS endpoint

---

## CSP Map After Changes

| Site | `connect-src` | WSS to hud? | Status |
|------|--------------|-------------|--------|
| signal | *(no CSP)* | ✅ | 10 panels live |
| hud | `'self' https://signal.primals.eco wss://hud.primals.eco` | ✅ (same-origin) | 10 panels live |
| detroit | *(no CSP)* | ✅ | 12 panels live |
| thesis | `'self' https://signal.primals.eco wss://hud.primals.eco` | ✅ (updated) | 8 panels live |
| sporePrint | `'self'` (csp_static) | ❌ | Uses WASM path (no WS needed) |
| clutch | *(no CSP)* | ✅ (not wired yet) | Remote repo |
| barry/tuebor | *(no CSP)* | ✅ (no data to render) | — |

---

## Files Created

| Path | Size | Purpose |
|------|------|---------|
| `infra/hud/site/static/js/hud-pt.js` | 10.8KB | HUD petalTongue bridge — 10 panels, same-origin WS |
| `infra/detroit/site/static/js/detroit-pt.js` | 12.1KB | Detroit petalTongue bridge — 12 panels from DETROIT_NETWORK |
| `infra/thesis/site/static/js/thesis-pt.js` | 8.1KB | Thesis petalTongue bridge — 8 panels from signal cross-origin |

## Files Modified

| Path | Change |
|------|--------|
| `infra/hud/site/content/_index.md` | Added `<div id="pt-panels">` mount + `hud-pt.js` script tag |
| `infra/hud/site/static/css/hud.css` | Added `.pt-viz` container styles |
| `infra/detroit/site/content/network/_index.md` | Added `<div id="pt-panels">` mount + `detroit-pt.js` script tag |
| `infra/detroit/site/static/css/main.css` | Added `.pt-*` panel/card/viz styles |
| `infra/thesis/site/content/_index.md` | Added `<div id="pt-panels">` mount point |
| `infra/thesis/site/templates/base.html` | Added `thesis-pt.js` script tag |
| `infra/thesis/site/static/css/thesis.css` | Added `.pt-*` panel styles |
| `infra/signal/site/content/_index.md` | Added "Maybe you are ecoPrimal" closing thought |
| `/etc/membrane/Caddyfile` (golgiBody) | Thesis CSP: `csp_static` → custom with signal + hud WS |

---

## Deployment Verification

All verified end-to-end on October 8, 2026:

```
detroit  → wss://hud.primals.eco/ws → bar chart:  4,625 bytes SVG ✅
thesis   → wss://hud.primals.eco/ws → gauge:      4,820 bytes SVG ✅
detroit  → wss://hud.primals.eco/ws → heatmap:    4,915 bytes SVG ✅
signal   → wss://hud.primals.eco/ws → (10 panels)              ✅
hud      → wss://hud.primals.eco/ws → (10 panels)              ✅
```

---

## What's Next — Incremental Wiring

The cross-site infrastructure is proven. Each site now has its own petalTongue bridge pattern. Next work is **incremental granularity** — drilling deeper into individual sections, types, or systems:

| Next target | What to add |
|-------------|-------------|
| **Detroit → Anderson lattice page** | Wire bench data through petalTongue — per-court capture gauges, localization length chart |
| **Detroit → Timeline page** | Wire timeline API through petalTongue timeseries |
| **Detroit → Funding flow page** | Wire money trail through petalTongue Sankey-style bars |
| **Signal → Per-epitope drilldown** | One petalTongue panel per organism — conserved feature bars |
| **Thesis → Live updating** | Wire SSE events for real-time panel refresh (no polling) |
| **Clutch → Clone + wire** | Clone from GitHub, add investigation graph stats through petalTongue |
| **sporePrint → Scene server mode** | Add WS CSP for server-side rendering alongside existing WASM |

---

## Lessons

1. **The bridge pattern scales** — same 3-part structure (fetch → transform → WS render) works for any data source
2. **CSP matters** — `csp_static` sites need explicit `connect-src` updates for cross-origin WS
3. **Caddy reload via CLI** — `systemctl reload caddy-tls` hits namespace mount issues; use `/opt/membrane/caddy reload --config` instead
4. **detroit's deploy path** — `/opt/ecoPrimals/detroit/public/` (no `site/` prefix), unlike signal which uses `/opt/ecoPrimals/signal/site/public/`
5. **Sites must stay independent during testing** — shared rendering service ≠ shared state. Each bridge is a standalone IIFE.
