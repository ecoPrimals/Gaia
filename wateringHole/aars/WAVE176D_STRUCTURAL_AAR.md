# SWEEP/SORT WAVE 176D: STRUCTURAL COMPLETION

## Graph: Zero Isolates + 2-Connected

| Metric | Start of session | End |
|--------|-----------------|-----|
| Nodes | 329 | **341** |
| Edges | 773 | **957** |
| Avg degree | 4.7 | **5.6** |
| Min degree | 0 | **2** |
| Isolates | 66 | **0** |
| Components | unknown | **1** |
| Articulation points | 1 (Banks) | **0** |
| Sort coverage | 90% | **100%** |
| Diameter | — | **7** |
| Avg path length | — | **3.08** |

## Structural Properties
- **Fully connected**: single component, all 341 nodes reachable
- **2-connected**: no single node removal disconnects the graph
- **Small world**: avg path 3.08, diameter 7

## Betweenness Centrality (structural bridges)
1. Banks (15187) — capture center, deg 120
2. MI Supreme Court (7070) — institutional apex, deg 86
3. **Dykema (4183)** — structural chokepoint, only deg 17 but bridges political↔legal
4. MDE (3863) — education pipeline, deg 43
5. Purpose Charter (2053) — authorization nexus
6. DPSCD (1928) — authorization authority
7. JTC (1771) — enforcement arm
8. **Dennis Archer (1624)** — political bridge, only deg 9
9. SCBC Tour (1392) — charter money conduit
10. Walton Foundation (1367) — external funding bridge

## Compression: All Sweepable Code Compressed
- **network-graph.js**: 1484→858 (−42%) — renderGraph(1369)→16 helpers
- **braid-tracker.js**: 356→298 (−16%) — EPITOPE_MAP 30→91 keywords
- **Files scanned, already clean**: pt-membrane-build, pt-membrane-animate,
  investigation-game, hud-pt, hud-core, pt-membrane, pt-ionosphere, 
  desk-core, hud-widget, footer-ring, signal-button, signal-live

## Remaining JS (clean, no sweep needed)
| File | Lines | Why clean |
|------|-------|-----------|
| network-data.js | 1188 | Generated data |
| pt-membrane-build.js | 1036 | 18 functions, max 92 |
| pt-membrane-animate.js | 1003 | 15 functions, animation |
| book-network.js | 481 | Source evidence data |
| hud-pt.js | 375 | Semi-minified bindings |
| hud-core.js | 315 | Coherent render blocks |
| pt-membrane.js | 311 | 13 functions, max 117 |
