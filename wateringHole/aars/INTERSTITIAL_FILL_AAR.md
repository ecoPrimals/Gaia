# SWEEP/SORT WAVE 176B: INTERSTITIAL FILL + FULL CLASSIFICATION

## Summary
Filled interstitial connections between tuebor braids and detroit graph.
Achieved 100% classification coverage (341/341 nodes sorted).

## Graph Evolution

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Nodes | 329 | 341 | +12 |
| Edges | 773 | 926 | +153 |
| Avg degree | 4.7 | 5.4 | +0.7 |
| Isolated (deg≤1) | 66 | 16 | −50 |
| Sort coverage | 90.0% | 100.0% | +10% |
| Other (unsorted) | 34 | 0 | −34 |

## New Nodes Added (12)
- **From tuebor braids (11)**: america_pac, att_inc, cispa, clutch_justice, tim_dunn,
  glcf, nrcc, mike_rogers, schwarzman, slf, state_bar_upl
- **From braid evidence (1)**: kenneth_griffin (Citadel CEO)

## Interstitial Edges (153 new)
1. **Braid-to-graph connections** (24): political donations, payment/client,
   legislation, investigation, lobbying, jurisdiction, governance
2. **Institutional pipelines** (69): JTC/AGC staff → MI Supreme Court,
   UPL staff → SBM, courts → JTC, universities → MDE
3. **Authorization chains** (17): charter schools → DPSCD
4. **Braid page evidence** (7): Griffin donations, AT&T↔Rogers,
   NRCC amplification, AFP→Rogers Super PAC
5. **Reduction passes** (36): geography→jurisdiction, advocacy,
   media, criticism, contractor, political connections

## Classification Sort Passes
| Pass | Method | Entities | Coverage |
|------|--------|----------|----------|
| 1 | Phase 1 hardcoded | ~230 | 67.6% |
| 2 | Phase 2 rules | ~269 | 79.1% |
| 3 | Phase 3 heuristics | ~306 | 90.0% |
| 4 | Braid interstitial | ~318 | 93.2% |
| 5 | Full resolution | 341 | 100.0% |

## Final Sort Distribution
| Class | Count | % | Description |
|-------|-------|---|-------------|
| self | 120 | 35.2% | The system being documented |
| partial | 114 | 33.4% | Entangled with system |
| null | 100 | 29.3% | External routing/funding |
| non-self | 7 | 2.1% | Corruption nexus |

## Compressed Files
- **braid-tracker.js**: 356→298 lines (−16%)
  - buildWidget(166) → widgetCSS() + widgetHTML() + widgetBind() + dispatcher(18)
  - EPITOPE_MAP: 30→91 keywords (3x coverage)

## Hub Nodes (deg > 20)
1. Banks (131) — center of gravity
2. MI Supreme Court (83) — institutional apex
3. MDE (46) — education pipeline
4. Purpose Charter (39) — authorization subject
5. JTC (38) — enforcement arm
6. MacDowell (37) — authorization subject
7. DPSCD (36) — authorizer
8. AGC (35) — enforcement arm
9. 3rd Circuit (26) — judicial
10. SBM (23) — regulatory
11. Beasley (21) — connected actor

## Files Modified
- graph.json (golgi × 2 paths)
- classification.json (golgi × 3 paths)
- braid-tracker.js (golgi + local HUD repo)

---

## Wave 176C: Deep Sort + Compression

### network-graph.js Compression
- **1484→858 lines (−42%, −626 lines)**
- renderGraph(1369) → 16 named helpers + 32-line dispatcher
- `svgEl(tag, attrs, parent)` + `svgText()` consolidate 299 SVG boilerplate lines
- Helpers: buildControls, filterAndCollapse, layoutForce, drawHulls, drawCycles,
  drawArrows, drawEdges, drawNodes, applyDynasty, highlightNode, clearHighlight,
  showInfo, drawLegend, drawObservation, drawSummary

### Evidence-Based Edges (from braid Decomposition layers)
- miller → anchor_rock (Board Chair — braid evidence)
- yancey → inner_link ($8K campaign expenditure)
- sdj → johnson_l (dark money campaign funding)
- mi_supreme_court → state_bar_upl (inaction: declined to define practice of law 2014)
- nrcc → barrett ($6.3M campaign spending)
- mde → banks (investigation_hold: Application #590606 HOLD)
- dykema → johnson_l (SDJ dark money pipeline)
- Updated edge labels with exact FEC amounts: Dunn $10M, Schwarzman $4.5M, Griffin $2.5M

### Final Graph State
- 341 nodes, 932 edges
- 341/341 sorted (100%)
- 16 remaining isolates (geography + minor actors)

### Files NOT swept (already clean)
- pt-membrane-build.js (1036 lines, 18 functions, max 92 lines each)
- pt-membrane-animate.js (1003 lines, 15 functions, intrinsic animation complexity)
- investigation-game.js (423 lines, 15 functions, max 86 lines)
- book-network.js (481 lines — source data, not logic)
- network-data.js (1188 lines — generated data file)
