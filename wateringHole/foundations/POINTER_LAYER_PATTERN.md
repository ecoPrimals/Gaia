# Pointer Layer Pattern

**Date**: Oct 5, 2026 | **Wave**: 161+ | **From**: sporeGate
**Status**: PATTERN EXTRACTED — proven in Forgejo DAG evolution
**Upstream**: FORGEJO_DAG_POINTER_LAYER_SPEC.md, PROVENANCE_CONTRACT.md, THREE_DOMAIN_TOPOLOGY_SPEC.md

---

## Abstract

A **pointer layer** is a thin relay node that tracks references to data
without storing the data itself. It maps content-addressed identifiers to
the mesh nodes that hold the actual blobs, providing a single query surface
for a distributed data mesh.

This pattern was extracted from the Forgejo DAG pointer evolution on
golgiBody, where a 1.8GB git forge was reduced to a 562MB reference-tracking
surface. The pattern generalizes to P2P crypto data federation, scientific
dataset distribution, and any system where data lives on heterogeneous mesh
nodes but needs a unified discovery layer.

---

## The Pattern

```
┌──────────────────────────────────────────────────────┐
│                 POINTER LAYER                         │
│            (thin relay, small disk)                   │
│                                                       │
│  ┌───────────────┐  ┌────────────┐  ┌──────────────┐│
│  │  DAG Index     │  │  Location  │  │  Integrity   ││
│  │  (what exists) │  │  Ledger    │  │  Proof       ││
│  │                │  │  (where it │  │  (chain is   ││
│  │  content hash  │  │  lives)    │  │  unbroken)   ││
│  │  → DAG node    │  │            │  │              ││
│  └───────────────┘  └────────────┘  └──────────────┘│
│        ↕                  ↕                ↕         │
│     rhizoCrypt        loamSpine       sweetGrass     │
│     (Merkle DAG)    (append ledger)  (PROV-O braid) │
└──────────────────────────────────────────────────────┘
         │                  │                │
         ▼                  ▼                ▼
┌──────────────────────────────────────────────────────┐
│                  DATA LAYER                           │
│           (mesh nodes, large disk)                    │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Node A  │  │  Node B  │  │  Node C  │  ...      │
│  │  (blobs) │  │  (blobs) │  │  (blobs) │           │
│  └──────────┘  └──────────┘  └──────────┘           │
└──────────────────────────────────────────────────────┘
```

### Core Invariants

1. **The pointer layer never stores blobs.** It holds identifiers (hashes,
   refs, DAG nodes) and location metadata. If the pointer layer stores
   data, it's no longer a pointer — it's a cache at best, a bottleneck
   at worst.

2. **Data is identified by content hash, not location.** When data moves
   between nodes, only the location ledger updates. The hash (identity)
   is immutable. Consumers address data by hash; the pointer layer
   resolves hash → location.

3. **The pointer layer includes integrity proof.** Without proof, the
   pointer layer is a single point of trust. With proof (Merkle tree,
   braid, DNSSEC chain), any consumer can independently verify the data
   they received matches the pointer.

4. **Failure is graceful.** If a data node goes offline, the pointer
   layer still knows what exists (DAG) and where else to find it (ledger
   mirrors). If the pointer layer goes offline, data nodes still hold
   their data — only discovery is degraded.

---

## Components

### 1. DAG Index (rhizoCrypt role)

Tracks **what exists** as a directed acyclic graph of content-addressed
nodes.

| Property | Description |
|----------|-------------|
| **Node** | A content hash (BLAKE3, SHA-256, git commit) |
| **Edge** | Parent/child relationship (derivation, lineage) |
| **Metadata** | Timestamp, author, context (repo, dataset, etc.) |
| **Immutability** | Once anchored, a DAG node never changes |

**Git analogy**: The commit graph. Each commit is a DAG node with a SHA-1
hash, pointing to parent commits.

**CAS analogy**: The content-addressed store index. Each object has a
BLAKE3 hash linking to its provenance chain.

### 2. Location Ledger (loamSpine role)

Tracks **where data lives now** as an append-only ledger.

| Property | Description |
|----------|-------------|
| **Entry** | {content_hash, node_id, timestamp, status} |
| **Append-only** | Entries are never deleted, only superseded |
| **Current view** | Latest entry per content_hash = current location |
| **Replication** | Multiple entries per hash = data on multiple nodes |

**Git analogy**: Branch refs + remote tracking. `refs/heads/main → abc123`
is a location pointer. `canonical_gates.toml` maps repo → gate.

**DNS analogy**: NS records. `example.com → ns1.provider.com` is a
location pointer resolved by the root/TLD hierarchy.

### 3. Integrity Proof (sweetGrass role)

Proves **the chain is unbroken** via Merkle trees or hash braids.

| Property | Description |
|----------|-------------|
| **Braid** | Merkle root covering a batch of DAG+ledger entries |
| **Verification** | Any consumer can recompute the Merkle root |
| **Non-repudiation** | The pointer layer can't silently alter history |
| **PROV-O** | W3C provenance ontology for auditable chains |

**Git analogy**: The commit hash itself is a Merkle node — it includes
the tree hash (content) and parent hash (history). You can verify any
commit's integrity by recomputing the hash.

**DNSSEC analogy**: DS records chain from root → TLD → zone, proving
each delegation is authorized.

---

## Instances

### Instance 1: Forgejo on golgiBody (LIVE)

```
Pointer Layer: golgi Forgejo (depth-1 shallow repos, 562MB)
Data Layer:    eastGate + sporeGate (full git repos, ~5GB)
DAG Index:     git commit graph (SHA-1 hash DAG)
Location:      canonical_gates.toml (repo → gate mapping)
Integrity:     git commit hash chain + sweetGrass braids
Discovery:     Forgejo web UI + git smart HTTP refs
```

**How it works**: A user browses `git.primals.eco` and sees repo READMEs,
branches, recent commits (served from shallow clones). When they `git clone`,
the git-proxy-shim routes the object transfer to the canonical LAN gate.
Push events trigger provenance logging (DAG anchor + ledger append).

### Instance 2: nestgate.io CAS Federation (SPECCED)

```
Pointer Layer: golgi CAS index (hash → gate mapping)
Data Layer:    westGate (519GB), strandGate (compute), ironGate (consumer)
DAG Index:     rhizoCrypt (BLAKE3 hash DAG)
Location:      songBird content.locate (mesh discovery)
Integrity:     sweetGrass braids (Merkle root per batch)
Discovery:     nestgate.io/cas/{hash} (HTTP API)
```

**How it works**: A researcher requests `nestgate.io/cas/{hash}`. The
petalTongue frontend queries local CAS → miss → songBird mesh broadcast →
westGate responds "I have it" → petalTongue proxies the response.

### Instance 3: Binary Depot (OPERATIONAL)

```
Pointer Layer: depot.primals.eco (architecture index, BLAKE3 checksums)
Data Layer:    LAN plasmidBin directories on each gate
DAG Index:     BLAKE3 hashes of each binary
Location:      depot manifest (arch → binary → path)
Integrity:     checksums.toml + BLAKE3SUMS files
Discovery:     depot.primals.eco web UI + /api/hashes endpoint
```

### Instance 4: P2P Crypto Data Federation (DESIGNED)

```
Pointer Layer: golgi DAG index (transaction/block hash → peer)
Data Layer:    Mesh peers holding blockchain/mempool data
DAG Index:     Transaction DAG (hash-linked, like git commits)
Location:      Peer location map (hash → which peer has it)
Integrity:     Chain proof (block hash chain = built-in Merkle)
Discovery:     Query API on golgi (hash → peer → data)
```

**How it works**: A P2P data federation system where golgi tracks which
mesh peers hold which blockchain data. Peers contribute data segments;
golgi maintains the index. Consumers query golgi for a transaction by hash,
get pointed to the peer holding it, and fetch directly. The blockchain's
own hash chain serves as the integrity proof.

**Key difference from traditional blockchain nodes**: Traditional nodes
store the full chain locally. In this pattern, each peer holds a subset
and golgi's pointer layer enables discovery across the mesh.

### Instance 5: Scientific Dataset Distribution (DESIGNED)

```
Pointer Layer: nestgate.io dataset index (name → hash → gate)
Data Layer:    westGate (primary), compute gates (cached copies)
DAG Index:     Dataset provenance graph (raw → processed → published)
Location:      nestgate.io/cas/{hash}/replicate
Integrity:     Provenance chain (paper → hash → raw data → instrument)
Discovery:     nestgate.io/validate/dataset/{name}
```

**How it works**: A reviewer checks a paper's data claims by hitting
`nestgate.io/validate/dataset/abg_phylogeny`. The system resolves all
referenced hashes, checks they exist in the mesh, verifies the provenance
chain (data → computation → published result), and returns a validation
report. The reviewer can independently reproduce the result using the
published parameters and verify the hash matches.

---

## Design Decisions

### Why Not Just Use a CDN?

A CDN caches content at edge nodes but doesn't track provenance or
verify integrity. It's a performance optimization, not a trust surface.
The pointer layer provides:
- **Content addressing** — data identified by hash, not URL
- **Provenance** — full derivation chain (raw → processed → published)
- **Integrity proof** — Merkle/braid verification, not just HTTPS
- **Mesh awareness** — knows which node holds what, routes intelligently

### Why Not Just Replicate Everything Everywhere?

Full replication works for small datasets but doesn't scale:
- westGate holds 519GB of science data — replicating to every gate
  would require 519GB × N gates of storage
- Compute results are ephemeral — some are reproduced faster than copied
- The pointer layer enables **selective replication** — hot data gets
  copied to more nodes, cold data stays on one node, but all data is
  discoverable through the same interface

### Why Not Just Store Data on golgi?

golgi is a 10GB VPS on a 1Gbps shared network link. The mesh has 50+ TB
of local storage on 10Gbps LAN. Storing data on golgi means:
- Data competes with services for the 10GB disk
- Transfers go through the VPS's bandwidth limit instead of LAN
- golgi becomes a bottleneck instead of a router
- Failure of golgi loses data (instead of just losing discovery)

This was the original Forgejo problem: 1.8GB of git blobs on a 10GB VPS
where Forgejo's architectural role is to route, not store.

---

## Implementation Checklist

For any new system adopting the pointer-layer pattern:

- [ ] **Identify the pointer layer node** — which node has the smallest
      disk but the most public connectivity? That's your pointer layer.
- [ ] **Choose content addressing** — BLAKE3, SHA-256, or git SHA-1.
      All data must be identifiable by immutable hash.
- [ ] **Build the DAG index** — what are the relationships between data
      items? Linear sequence (blockchain), tree (git), or graph (CAS)?
- [ ] **Build the location ledger** — which node holds which hash?
      Static config (TOML) or dynamic discovery (songBird mesh)?
- [ ] **Add integrity proof** — how does a consumer verify the data
      matches the pointer? Built-in (git hash) or external (sweetGrass)?
- [ ] **Define the discovery API** — how does a consumer find data?
      HTTP (nestgate.io), git (smart HTTP), or mesh (songBird)?
- [ ] **Handle failure gracefully** — what happens when a data node is
      offline? Mirror fallback? Degraded response? Queue for retry?
- [ ] **Measure pointer layer size** — if it grows beyond 1% of data
      layer, you're storing blobs, not pointers. Investigate.

---

## Anti-Patterns

### 1. Pointer Bloat

**Symptom**: Pointer layer storage grows linearly with data volume.
**Cause**: Storing blobs alongside pointers (e.g., Forgejo holding full
git repos instead of shallow refs).
**Fix**: Strict separation — pointers are O(n) in number of items, not
in total data volume. A 50TB data mesh should have a <1GB pointer index.

### 2. Pointer-Data Coupling

**Symptom**: Pointer layer goes down and data becomes inaccessible.
**Cause**: Data nodes depend on pointer layer for their own operation
(e.g., data node queries pointer layer before serving).
**Fix**: Data nodes are self-sufficient. They serve data by hash from
local storage. The pointer layer is a discovery optimization, not a
dependency.

### 3. Trust Without Proof

**Symptom**: Consumers trust pointer layer without verifying integrity.
**Cause**: No Merkle chain, no braid, no DNSSEC — just "trust the index."
**Fix**: Every pointer includes enough information for independent
verification. Content hash is recomputable. Provenance chain is auditable.

### 4. Single-Copy Fragility

**Symptom**: One data node goes offline and data is lost.
**Cause**: Location ledger shows only one copy of critical data.
**Fix**: Replication policy — critical data must exist on N≥2 nodes.
The location ledger makes this visible (query: "which hashes have <2 copies?").

---

## Relationship to K-Derm Topology

The pointer layer maps directly to the K-Derm three-layer model:

| K-Derm Layer | Pointer Layer Role | Example |
|-------------|-------------------|---------|
| **Outer Membrane** | Public discovery surface | git.primals.eco, nestgate.io |
| **Peptidoglycan** | Structural mesh (LAN, WG) | songBird federation, WireGuard |
| **Inner Membrane** | Data nodes + integrity | Gate CAS stores, provenance trio |

golgiBody IS the outer membrane pointer layer — it processes and routes
requests from the public internet to the inner mesh where data lives.
This is the Golgi apparatus pattern: receive, label, route, ship.

---

## References

- [FORGEJO_DAG_POINTER_LAYER_SPEC.md](../specs/FORGEJO_DAG_POINTER_LAYER_SPEC.md) — Implementation spec
- [PROVENANCE_CONTRACT.md](../specs/PROVENANCE_CONTRACT.md) — Trio roles and pipeline
- [THREE_DOMAIN_TOPOLOGY_SPEC.md](../specs/THREE_DOMAIN_TOPOLOGY_SPEC.md) — Domain architecture
- [K_DERM_TOPOLOGY_STANDARD.md](K_DERM_TOPOLOGY_STANDARD.md) — Three-layer cell envelope model
