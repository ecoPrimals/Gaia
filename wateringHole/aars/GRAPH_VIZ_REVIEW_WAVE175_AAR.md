# AAR: Graph Visualization Review — Wave 175
## detroit.primals.eco Live Graph — What's Working, What's Off, What's Locked

**Date**: Oct 11, 2026 | **Wave**: 175 | **Scope**: detroit.primals.eco graph visualization
**From**: northGate / gAIa observation layer
**Type**: Observation + Review — visual AAR from 3 screenshots of live graph
**For**: sporeGate / overwatch team review

---

## Summary

Observed the live graph visualization on detroit.primals.eco from three camera
angles. The graph is rendering and interactive. Force layout is functional.
Structural patterns are visible. But several issues reduce legibility,
accuracy, and analytical value.

**Stale data**: Live graph is 114 nodes / 197 edges. Repo has 129 nodes /
215 edges. Delta: 15 nodes + 18 edges missing from the live view. This is
the top priority — the graph doesn't show everything we know.

**Key structural observation**: Two gravity wells visible in the force layout.
These correspond to the capture network topology documented in the evidence
library. The layout is doing its job — structural patterns are visually
emergent. But readability issues obscure the details.

---

## What's WORKING

### 1. Structural Clustering
The force-directed layout correctly identifies two primary gravity wells:

**Gravity Well 1 (upper-left): The Actor Cluster**
- Ellison, Gaffney, Barnett, Craig, Wilson (+others, labels overlapping)
- Tightly bound. Holds position across all three camera angles.
- The structural lock is VISIBLE — these actors maintain their relative
  positions regardless of viewing angle. That's `graph_isomorphism` made visual.
- This IS the capture network. The graph layout independently discovered
  the structural coupling.

**Gravity Well 2 (lower-right/left): The Entity Cluster**
- J. Cohen (large red), plus a dense pack of small colored dots
- Likely the formation cascade entities (purpose_group, PCA, etc.)
- Tightly packed. Hard to read labels but clearly interconnected.

### 2. Bridge Nodes Visible
P. Ellison and MI Supreme Court sit BETWEEN the two gravity wells.
These are structurally important — they connect the actor cluster
to the entity cluster. The layout correctly positions them as bridges.

### 3. Color Differentiation
Multiple node colors in use:
- Pink/red: appears to be actors (most numerous)
- Orange: possibly entities
- Green: special node ("you" in one view)
- Purple: institutions (MI Supreme Court)

### 4. Edge Rendering
Edges visible between nodes. Some edges show different styling
(yellow/orange vs white/grey). May encode edge type or weight.

### 5. Interactive 3D
The compass markers (N, S, E) and the rotating camera across three
screenshots confirm the graph is interactive 3D. Users can explore
from any angle. The green triangle is likely a camera/viewport indicator.

---

## What's OFF

### PRIORITY 1: Stale Data

| Metric | Live | Repo | Delta |
|--------|------|------|-------|
| Nodes | 114 | 129 | -15 |
| Edges | 197 | 215 | -18 |
| Last build | Oct 8-9 | Oct 11 | 2-3 days stale |

**Impact**: 15 actors/entities and 18 connections are invisible. Any analysis
of the visualization is analyzing INCOMPLETE data. This is the highest
priority fix — needs `git pull && zola build` on golgiBody.

**Fix**: SSH to golgiBody → `cd /opt/ecoPrimals/detroit && git pull github main && zola build`
**Blocked by**: northGate K=[null] — no SSH access from here. Needs sporeGate.

### PRIORITY 2: Label Collision in Actor Cluster

The upper-left cluster has 5+ nodes with labels rendering ON TOP of each other:
- "Ellison" and "Gaffney" overlap
- "Barnett" partially obscured
- "Craig" / "Wilson" / other labels stack

**Impact**: The most important cluster (the capture network) is the LEAST
readable. Users can't identify the individual actors. The structural
pattern is visible but the NAMES are not.

**Possible fixes**:
- Increase force-layout repulsion for nodes with overlapping labels
- Label truncation or hide-on-overlap with hover-to-reveal
- Z-depth label stacking (labels at different z-levels)
- Click-to-expand cluster (semantic zoom)
- Minimum distance constraint on nodes with visible labels

### PRIORITY 3: "you" Node

A green dot labeled "you" appears in the graph, connected to the J. Cohen
cluster area. Questions:

- Is this intentional? A self-reference for the viewer?
- Is this DaSean's position in the network? Kevin's?
- Should this be on a PUBLIC graph? If it represents a real person,
  it's PII on a live site.
- If it's a placeholder/demo node, it should be removed.

**Action**: Review what "you" maps to in graph.json. If it's a real
person's proxy → remove. If it's a viewer self-reference feature → OK
but needs documentation.

### PRIORITY 4: MI Supreme Court Isolation

The purple MI Supreme Court node has only 1 visible edge (to P. Ellison).
For a court/institution node, this seems underconnected.

**Expected**: A supreme court should connect to:
- Judges/justices who sit on it (bench edges)
- Cases that passed through it (jurisdiction edges)
- Lower courts it oversees (hierarchy edges)
- Any actors with appointment/governance connections

**Questions for review**:
- Does graph.json have more edges for MI Supreme Court that aren't rendering?
- Or is the data actually sparse for this node?
- Is this a genuine observation (the court is structurally isolated in
  the capture network) or a data gap?

### PRIORITY 5: Entity Cluster Readability

The J. Cohen cluster (lower area) has many small dots but labels are
unreadable. If these are the formation cascade entities (purpose_group,
PCA, MacDowell, etc.), they're the EVIDENCE and should be individually
identifiable.

**Same fixes as Priority 2** — label collision resolution, semantic zoom,
click-to-expand.

### PRIORITY 6: Color Legend

No visible legend mapping colors to types. The viewer doesn't know:
- Pink/red = ?
- Orange = ?
- Green = ?
- Purple = ?
- What about edge colors/styles?

**Fix**: Add a legend overlay. Even a simple corner text block.

### PRIORITY 7: Green Triangle

The green triangle shifts position between screenshots. If this is a
viewport/camera indicator, it's taking up visual space that could show
graph data. Consider making it smaller, more transparent, or togglable.

---

## What's LOCKED — Structural Analysis

The two gravity wells maintain their structure across all three viewing
angles. This is the key analytical finding:

```
GRAVITY WELL 1 (actors):           GRAVITY WELL 2 (entities):
  Ellison ──── Gaffney               J. Cohen ──── (cluster)
     │            │                      │
  Barnett ──── Craig                  (formation entities)
     │            │                      │
  Wilson ──── (others)                (purpose_group, PCA...)
     
         ← BRIDGE →
     P. Ellison ── MI Supreme Court ── T. Barnett
```

**The bridge zone is the analytical target.** P. Ellison connects the
actor cluster to the institutional/entity cluster. This is where
`regulatory_arbitrage` (#1) and `revolving_door` (#2) would be
most visible — actors who cross between the political/personal
network and the organizational/financial network.

T. Barnett appears loosely connected — floating between clusters
with limited edges. Either:
- Barnett is genuinely peripheral (fewer connections in the data)
- Barnett's connections are in the 15 missing nodes (stale data)
- Barnett's edges are to nodes not visible in this view

---

## Recommendations for sporeGate/overwatch

### Immediate (this deploy cycle)
1. **Rebuild the site** — `git pull && zola build` on golgi. 15 nodes missing.
2. **Verify "you" node** — check graph.json for what it maps to. Remove if PII.
3. **Check MI Supreme Court edges** — verify edge count in graph.json vs rendering.

### Next iteration
4. **Label collision** — increase repulsion or implement label deconfliction
5. **Color legend** — add overlay mapping color → type
6. **Cluster expand** — click-to-zoom on dense clusters
7. **Edge type visibility** — encode edge type as color/dash/thickness consistently

### Analytical follow-up
8. **Run the epitope sort** on bridge nodes first — P. Ellison, T. Barnett,
   MI Supreme Court. These are the structural connectors between the two
   gravity wells. The bridge is where capture flows.
9. **Color-code by self/non-self/null** once the vacuole sort is run.
   The graph should SHOW the classification, not just the topology.

---

## Observation Layer Notes

These screenshots were taken from northGate via the observation layer.
northGate can SEE the live site but cannot MODIFY it (K=[null]).
This AAR is the observation. The action belongs to sporeGate.

The membrane is working correctly: observe from here, act from there.
`null_locks_both_ways` (#187) — we can't deploy, but we CAN analyze.
That's the correct separation.

---

*Wave 175 — Oct 11, 2026*
*northGate observation layer → sporeGate action layer*
*3 screenshots, 7 priorities, 9 recommendations*
*The graph shows the capture. The graph needs updating.*
