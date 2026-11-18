# SWEEP + SORT — Wave 176 AAR

**Date**: 2026-10-12
**Duration**: ~45 min
**Sites**: detroit, clutch, hud, signal

---

## 1. COMPRESSION SWEEP (4 files, 3 sites)

| File | Site | Before | After | Δ | Method |
|------|------|--------|-------|---|--------|
| detroit-pt.js | detroit | 467 | 311 | −33% | tryRender(394) → bind() + counts() + sorted() + 6 section helpers |
| graph-walker.js | clutch | 555 | 340 | −39% | renderGraph(375) → svgEl + div + 5 section helpers |
| desk-weave.js | hud/desk | 725 | 409 | −44% | bindWeaveHandlers(466) → btn() + buildPiTable + buildLocalPi + 9 helpers |
| timeline-graph.js | detroit | 273 | 171 | −37% | renderTimeline(179) → el() + 3 builders + inline filter |
| **Total** | | **2020** | **1231** | **−39%** | **−789 lines** |

### Patterns Applied
- `bind(type, id, label, props)` — wrapper for pt.renderBinding (detroit-pt)
- `svgEl(tag, attrs, parent)` — SVG element factory (graph-walker)
- `el(tag, cls, parent)` — DOM element factory (timeline-graph)
- `btn(id, fn)` — event binding shorthand (desk-weave)
- `sect(title, body)` / `roundHtml(num, title, body)` — HTML section wrappers (desk-weave)
- `counts(arr, key)` / `sorted(obj)` — data aggregation helpers (detroit-pt)
- `buildPiTable()` / `buildLocalPi()` — extracted π computation (desk-weave)

## 2. STALE COPY SYNC

signal-exploration.js (swept to 481 lines in prior session) synced to 7 stale locations:
- signal/site/public/js/
- signal-repo/site/static/js/ + site/public/js/
- detroit/worktree/site/static/js/ + site/public/js/
- detroit/public/js/

nanowire.js synced from golgi→local (676→916 lines, newer version).

## 3. DETROIT ENTITY SORT — Phase 3

Phase 3 classified 67 new entities using broader heuristics:

| Rule | New Classifications | Target Class |
|------|-------------------|--------------|
| Universities (EMU, MSU, Wayne State, etc.) | institution → self | self |
| State oversight (prosecutors, RESA, board of ed) | oversight → self | self |
| Charter ecosystem (AFC, DeVos, Mackinac) | ecosystem → partial | partial |
| Political actors | political edges → partial | partial |
| Employed actors | employment edges → partial | partial |
| Funding entities | funding edges → null | null |
| Media entities | media keywords → null | null |
| Religious orgs | church/rev keywords → partial | partial |
| Family-connected actors | family edges → partial | partial |
| Governed entities | oversight/governance → self | self |
| Academic actors | education edges → partial | partial |
| Authorized entities | authorization edges → self | self |

### Sort Progression
| Pass | Classified | % | Method |
|------|-----------|---|--------|
| Phase 1 | 10 | 3.0% | Manual expert classification |
| Phase 2 | 228 | 69.3% | Structural cascade (edge-type propagation) |
| **Phase 3** | **295** | **89.7%** | Broad heuristic (entity type + edge patterns) |

### Final Classification
```
  self:     114 (35%) — institutions, courts, oversight  
  partial:   98 (30%) — captured personnel, ecosystem
  null:      78 (24%) — routing, vendors, shells
  non-self:   5 ( 2%) — core captured entities
  other:     34 (10%) — truly insufficient data
```

**π ratio: 0.897** (target 1/π = 0.318) — 2.82× the threshold.

## 4. INFRA SORT

14 scripts in /opt/membrane/ classified by epitope:
- **MEMBRANE** (4): antidote.py, uv-lamp.py, tower-observer.sh, ops-status.sh
- **OBSERVE** (4): ingestion-observer.py, presence-observer.sh, mirror-receiver.py, chipmunk-bridge.py
- **SIGNAL** (4): plasmid-federation.sh, relay-membrane-probe.sh, forge-push.sh, watch-chorus.sh
- **SORT** (2): phase2_sort.py, classification-persist.py

No monolith compression needed — largest method is UVLamp (303 lines class, but all methods <60 lines).

## 5. EPITOPE SORT — ALL JS (14 files, 9524 lines)

| Epitope | Files | Lines | % |
|---------|-------|-------|---|
| MEMBRANE | 5 | 3916 | 41% |
| SIGNAL | 5 | 3176 | 33% |
| OBSERVE | 4 | 2023 | 21% |
| generated/data | — | 409 | 5% |

## 6. CLASSIFICATION PERSISTENCE FIX

- Updated classification-persist.py to use classification.json as canonical source (no more Phase 1 hardcoding)
- Fixed /opt/ecoPrimals/detroit/public/classification.json (was serving phase2 metadata instead of per-node data)
- Workflow: northGate pushes → run classification-persist.py → classification survives

## 7. LIVE NUMBERS

- IS: 352 | NEARBY: 1,526 | WAS: 2,953
- Tower: 11/11 alive
- Detroit: 295/329 sorted (π=0.897)
- Sites: 4/4 serving (hud, detroit, clutch, signal)
