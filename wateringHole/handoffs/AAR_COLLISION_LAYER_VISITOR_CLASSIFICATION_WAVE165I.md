# AAR: Collision Layer Visitor Classification — From N Bins to Behavioral Merkle Trie

**Date**: Oct 7, 2026
**Wave**: 165i
**From**: eastGate overwatch
**To**: sporeGate — bloom classifier evolution, loamSpine collision integration, bingoCube projection learning
**Status**: Architecture identified. Three systems converge on one design.

---

## The Problem

The bloom monitor currently classifies visitors into 2 bins: fleet / human. The salesman triage (AAR_SALESMAN_SIGNAL_TRIAGE_WAVE165I) identified at least 4 distinct populations:

1. **Fleet** — known IP ranges, bot UAs (12,358 req today, 99.8%)
2. **Residential proxy fleet** — coordinated timing, all 404, residential IPs (20 IPs)
3. **Agentic readers** — human+agent pairs, single deep hit, 200 (20 IPs)
4. **Genuine curiosity** — multi-page browser sessions with asset loading (2 IPs)

The obvious next step: add more bins. 4 bins, 8 bins, N bins.

**But the question is: why N? Why not M? Why not a continuous spectrum?**

The answer was already in the codebase.

---

## The Collision Layer Insight

loamSpine's COLLISION_LAYER_ARCHITECTURE.md (March 2026) describes exactly this problem in a different domain:

> *"A collision layer introduces a third lens: similarity grouping via intentional hash collisions. By applying progressively weaker hash functions to the same content-addressed entries, we create collision classes that reveal hidden structural relationships."*

The collision layer doesn't predefine categories. It hashes data through progressively weaker projections and lets the **collisions themselves** be the classification. Entries that collide at a given resolution are "similar" under that lens. No labels needed.

Applied to visitor classification:

```
Instead of:  fleet | proxy | agentic | human    (N bins, chosen by us)
We get:      behavioral Merkle trie              (classes emerge from data)
```

---

## Architecture: Behavioral Vector → Collision Hierarchy

### Step 1: Compute Behavioral Vector per IP

Each IP in a bloom window produces a vector:

```
B(ip) = (
  hit_count,                    # 1 hit vs 154 hits
  status_distribution,          # [200_ratio, 404_ratio, 502_ratio]
  timing_entropy,               # uniform vs bursty
  coordination_score,           # same-path-same-time with other IPs
  asset_loading,                # loads CSS/JS after page?
  sec_fetch_present,            # browser context headers?
  domain_diversity,             # 1 domain vs 5 domains
  path_depth,                   # /foo vs /org/repo/src/commit/hash
  referer_chain_depth,          # no referer vs self-referencing chain
  language_header_present,      # yes/no
  language_header_value,        # en-US vs zh-CN vs none
)
```

### Step 2: Hash Through Resolution Hierarchy

From the collision layer spec:

```
Level 0: Full behavioral fingerprint → every IP unique (identity)
Level 1: Drop timing, keep structure → coordination clusters appear
Level 2: Drop path specifics         → fleet/reader/browser emerge
Level 3: Keep only status + hit_count → binary fleet/not-fleet
```

This is a **Merkle trie** where each level is a valid classification on its own:

```
Level 3 (coarsest):
  Bucket A: [all fleet + proxy fleet]  — high hit count OR all-404
  Bucket B: [all readers + genuine]    — low hit count AND some-200

Level 2 (medium):
  Bucket A1: [fleet]         — known IPs, bot UAs
  Bucket A2: [proxy fleet]   — residential IPs, coordinated timing, 404
  Bucket B1: [agentic]       — single hit, 200, sec-fetch, no assets
  Bucket B2: [genuine]       — multi-hit, 200, loads assets, referer

Level 1 (fine):
  Bucket A2a: [LATAM proxy cluster]   — Brazil/Chile/Paraguay exits
  Bucket A2b: [MENA proxy cluster]    — Oman/Turkey/UAE exits  
  Bucket B1a: [zh-CN agentic]         — Tencent/Huawei DC, thesis readers
  Bucket B1b: [en-US agentic]         — residential, code browsers
  Bucket B2a: [asset-loading browser] — full CSS/JS/search_index

Level 0 (identity):
  Every IP unique
```

### Step 3: Collision Density = Natural Boundaries

The collision density at each level tells us where the natural cluster boundaries are:

- **High density at Level 2, Bucket A1** = fleet is a tight cluster (good — we know what fleet looks like)
- **Sparse at Level 1 within B1** = agentic readers are diverse (each has a unique interest)
- **High density at Level 1, Bucket A2a** = LATAM proxy cluster is tight (same exit network)

When a new visitor type appears that we haven't imagined, it shows up as a **new collision group** at some level — no classifier update needed.

---

## Connection to Existing Architecture

### loamSpine: The Collision Layer IS the Index

From COLLISION_LAYER_ARCHITECTURE.md:

> *"The collision layer is always an index, not authoritative storage. Entries are stored once in the spine; the collision index provides alternative access patterns."*

The bloom monitor stores events (the spine). The collision hierarchy is an index over those events. Multiple views coexist:

- Horizontal: chronological event stream (current bloom output)
- Vertical: collision groups at each resolution level

Neither view is canonical. Both are valid simultaneously.

### Cross-Writing: Multiple Layers on Same Data

From the spec:

> *"Cross-writing: letters were written normally, then the page was rotated 90 degrees and overwritten with a second message. Both layers of information persisted because they used orthogonal encoding."*

The same visitor event participates in collision groups at ALL levels simultaneously. The Brazilian residential proxy IP is:
- Unique at Level 0
- Part of "LATAM proxy cluster" at Level 1  
- Part of "probing traffic" at Level 2
- Part of "all traffic" at Level 3

All four views coexist on the same data point. Reading direction (resolution level) determines which view you see.

### bingoCube: Evolve the Projections

Instead of hand-choosing "which features matter at Level 2", bingoCube's evolutionary reservoir can **learn the projection functions** that produce the most informative collision topology:

- Population of projection functions (hash truncations, feature weightings)
- Fitness: silhouette score of collision groups (tight clusters, well separated)
- Evolution: mutate projections, select for best clustering
- Result: data-driven hash levels that adapt as fleet evolves

This closes the loop: bloom monitor generates behavioral vectors → collision hierarchy indexes them → bingoCube evolves the hash projections → bloom uses the evolved projections. The classification evolves with the traffic.

---

## Convergence Tiering Connection

The CONVERGENCE_TIERING_MULTI_RESOLUTION_SPINE.md already describes this for CAS objects:

> *"The short spine doesn't avoid hash collisions — it uses them as the sharding mechanism. When you truncate a BLAKE3 hash to its first byte, all objects sharing that prefix 'collide' into the same bucket."*

Visitor classification is the same operation: truncate a behavioral hash to create collision buckets. The math is identical. The substrate differs (CAS objects vs HTTP requests) but the pattern is universal.

---

## Implementation Sketch

### Phase 0: Immediate (bloom classifier)

Add collision-based grouping to existing bloom output:
- Compute coordination_score per IP (same-path-same-10s with others)
- Compute status_only flag (all-404 IPs)
- Output: fleet / coordinated-404 / reader / genuine (4 collision groups at Level 2)

### Phase 1: Behavioral Vector (skunky-ingest)

Compute full behavioral vector per IP per window. Store in signal spine.

### Phase 2: Collision Hierarchy (loamSpine)

Build collision index over behavioral vectors. Multiple resolution levels. Query: "what collision group is this new IP in?"

### Phase 3: Evolved Projections (bingoCube)

bingoCube populations evolve projection functions. Fitness from collision topology quality. Deployed projections feed back into bloom.

---

## Action Items for sporeGate

- [ ] **Phase 0**: Add coordination_score to bloom — timestamp correlation across IPs hitting same path
- [ ] **Phase 0**: Add status_only classifier — IPs with only 404s are probing
- [ ] **Phase 1**: Design behavioral vector schema for skunky-ingest
- [ ] **Phase 2**: Wire collision layer index into loamSpine (COLLISION_LAYER_ARCHITECTURE.md Phase 1)
- [ ] **Phase 3**: bingoCube projection learning experiment in neuralSpring

---

*Not N bins. Not even a continuous spectrum. A Merkle trie of behavioral similarity where the collisions are the classes, the resolution is the zoom level, and the projections evolve with the traffic. The data tells us how many kinds of visitors there are. We just need the right lens.*

*eastGate overwatch — Wave 165i, Oct 7, 2026*
