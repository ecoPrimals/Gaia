# AAR: Cross-Gate Provenance Convergence — Data × Compute Braiding

**Date**: Aug 6, 2026 | **Wave**: 156e
**Gates**: strandGate (Compute) × westGate (Data) → ironGate (Product CAS)
**Operator**: Claude (overwatch session from eastGate)
**Scope**: Synthesis of westGate's 700× braiding breakthrough with strandGate's
compute memoization pattern. Architecture convergence toward unified provenance
chain: raw observation → computation → published result.

---

## Executive Summary

westGate discovered that once on UDS (Unix Domain Sockets) with properly
ordered braiding, throughput jumped from 0.3/s to 217/s — a ~700×
improvement. The critical finding was that the **primals were never the
bottleneck** (~5 ms/file). The bottleneck was glue code (socat subprocess
spawns) and storage topology (spinner writes under ZFS COW).

strandGate's compute provenance operates on the same trio infrastructure
but with a fundamentally different access pattern: fewer, larger objects
(thermalized lattice configs at ~6 MB each vs millions of small files)
with expensive generation cost (~37 min/config at 16⁴). The compute side
is CPU-bound, not I/O-bound.

**Architectural convergence**: Both sides use identical BLAKE3 content
addressing, the same CAS put/get pattern, the same braid structure. A
westGate data braid can reference a strandGate compute braid via hash,
forming a complete provenance chain. ironGate (12.7 TB CAS) serves both
as the product store.

---

## westGate Findings — What Dropped the Braiding Time

### The Architecture Fix (122×)

The scripts were calling `loamSpine entry.append` per file. At 187K spine
entries, each append deserializes the entire spine (O(n)), modifies, and
reserializes — 3.5 seconds per file, scaling worse than linearly.

The canonical architecture calls `entry.append` once per *dataset* (after
DAG dehydration), not per file:

```
Per file:     BLAKE3 → nestGate CAS → rhizoCrypt dag.event.append  (4 ms, O(1))
Per dataset:  dehydrate → session.commit → bearDog.sign → sweetGrass.braid
```

This alone yielded 122×: 0.3/s → 37.6/s.

### The UDS Fix (4×)

Replacing socat subprocess spawns with native `socket.AF_UNIX` connections:
- socat: ~10 ms overhead per RPC call × 4 RPCs/file = 40 ms/file wasted
- Native UDS: 16,352 RPCs/s capacity, ~0.06 ms per call
- Combined with Python `blake3` (replacing `b3sum` subprocess): 37.6 → 145.5/s

### The Storage Fix (1.5–2.7×)

NVMe hot tier for CAS writes (`NESTGATE_STORAGE_PATH=/mnt/cas-hot`):
- Spinner random write: ~36 ms/file (ZFS COW amplifies to 3× IOPS)
- NVMe random write: ~0.02 ms/file
- 145.5/s → 217/s on NVMe, 265/s for inline braiding (warm data)

### Composite Result

| Fix | Multiplier | Cumulative |
|-----|-----------|------------|
| Architecture (no per-file spine) | 122× | 122× |
| Native UDS + in-process BLAKE3 | 3.9× | 460× |
| NVMe hot tier | 1.5× | ~700× |

---

## strandGate Compute Pattern — How It Differs

| Dimension | westGate (Data) | strandGate (Compute) |
|-----------|----------------|---------------------|
| **Object count** | 11M+ files (AlphaFold alone) | ~100 configs (SU(N) memo table) |
| **Object size** | Bytes to MBs (mixed) | 6.1 MB per SU(3) 16⁴ config |
| **Generation cost** | Download: ~50 ms/file | Thermalization: ~37 min/config (16⁴) |
| **Bottleneck** | I/O (spinner writes) | CPU (HMC integration) |
| **Throughput target** | 217/s sustained | ~0.05/s (one config every 20 min) |
| **CAS volume** | 452–529 GB (153 datasets) | ~30 GB (87 configs projected) |
| **Braid frequency** | Per dataset (~153 braids) | Per config + per experiment run |
| **Provenance overhead** | ~5 ms/file (negligible at 217/s) | ~12 ms/config (~2% of HMC trajectory) |

### Why westGate's Fixes Matter for strandGate

1. **Native UDS is already correct for compute**. strandGate's NFT pattern
   (`prov_inline.py` canonical flow) already uses native sockets. No socat
   technical debt on the compute side.

2. **Per-session commit is natural for compute**. Each thermalization run
   produces one config — one CAS put, one DAG event, one braid. The
   pathological per-file spine scaling that killed westGate throughput
   cannot occur.

3. **NVMe recommendation applies directly**. ironGate's 12.7 TB CAS should
   stage compute braids on NVMe before cold migration. At strandGate's
   low throughput (~0.05/s), even spinners wouldn't bottleneck — but the
   principle of flash-backed braiding is sound for future scaling.

4. **Inline braiding is the canonical pattern for both**. westGate's
   discovery (process provenance while data is in memory) directly maps
   to strandGate's existing pattern (braid immediately after thermalization,
   while the config is still in RAM).

---

## Cross-Gate Provenance Chain

The full chain from raw observation to published physics result:

```
westGate (Data CAS)                    strandGate (Compute CAS)
─────────────────                      ────────────────────────
Download raw data                      Thermalize lattice configs
  │                                      │
  ▼                                      ▼
BLAKE3 → CAS                          BLAKE3(params) → cache key
  │                                      │
  ▼                                      ▼
DAG event (per file)                   DAG event (per config)
  │                                      │
  ▼                                      ▼
session.commit → braid                 session.commit → braid (NFT)
  │                                      │
  └──── stored on westGate NAS ──────────┘
                    │
                    ▼
              ironGate (Product CAS, 12.7 TB)
                    │
                    ▼
              songBird mesh federation
                    │
                    ▼
         petalTongue / downstream consumers
```

A strandGate compute braid can **reference** a westGate data braid by
hash. Example: a lattice QCD calculation using AlphaFold-predicted hadron
masses would chain:

```
westGate braid (AlphaFold PDB, BLAKE3: abc123...)
  ↓ (referenced in compute DAG as input)
strandGate braid (HMC run, BLAKE3: def456...)
  ↓ (referenced in publication manifest)
arXiv preprint pseudoSpore (BLAKE3: ghi789...)
```

No trust required at any link. Any party with access to ironGate can
independently verify the entire chain.

---

## Lessons for Other Gates

### What westGate Proved

1. **Primals are fast.** rhizoCrypt: 4 ms. nestGate CAS: 0.5 ms.
   bearDog: 0.1 ms. The Rust primals never needed optimization.

2. **Glue code is the enemy.** socat spawns, per-file spine entries,
   spinner random writes — all outside the primals.

3. **Storage topology matters more than code optimization.** The same
   primals went from 80/s to 217/s by changing one environment variable.

4. **Monitor `zpool iostat -v` under load.** Write contention is invisible
   without per-vdev monitoring. Degradation from 145/s to 80/s on spinners
   looked like a primal bug but was pure I/O contention.

### What strandGate Extends

1. **Compute memoization is the dual of data acquisition.** Same CAS,
   same braids, but the bottleneck is generation cost, not I/O throughput.

2. **Dynamic programming via tiling.** A 16⁴ thermalized config tiles
   into 32⁴ with 75-trajectory burn-in instead of 300+ from scratch.
   The memo table acts as a dynamic programming cache.

3. **GPU accelerated measurement on CPU-cached configs.** CPU thermalizes
   (37 min/config at 16⁴). GPU measures (638 ms/trajectory at 16⁴).
   The GPU is 37× faster for measurement passes on cached configs.

4. **NFT as auditable scientific artifact.** Every computed result carries
   its full input lineage. Reproducing a result means reproducing the
   hash, not trusting the author.

---

## Architecture Convergence Points

| Pattern | westGate Implementation | strandGate Implementation | Unified |
|---------|------------------------|--------------------------|---------|
| Content addressing | BLAKE3(file_content) | BLAKE3(input_params) | Same library, same algorithm |
| CAS storage | nestGate on ZFS/NVMe | nestGate on local SSD | Same primal, different storage |
| DAG tracking | rhizoCrypt per-file event | rhizoCrypt per-config event | Same primal, different granularity |
| Spine commit | loamSpine session.commit per dataset | loamSpine session.commit per run | Same primal, same pattern |
| Signing | bearDog Ed25519 | bearDog Ed25519 | Identical |
| Attribution | sweetGrass W3C PROV-O braid | sweetGrass NFT braid | Same primal, different metadata schema |
| IPC | Native UDS (AF_UNIX) | Native UDS (AF_UNIX) | Identical |
| Product store | ironGate via songBird | ironGate via songBird | Same destination |

---

## Recommendations for Overwatch

1. **Team westGate and strandGate on cross-frontier braiding.** First live
   chain: westGate data braid → strandGate compute braid → ironGate product.
   This validates the full provenance architecture end-to-end.

2. **Standardize NVMe hot-tier for all gates.** westGate's convoy AAR
   proved flash-backed braiding is a universal pattern. Every gate should
   have dedicated NVMe for CAS writes.

3. **strandGate compute braids land on ironGate.** The product CAS
   (ironGate, 12.7 TB) serves both data and compute braids to downstream
   consumers. strandGate should push braided configs there via songBird.

4. **biomeOS signal dispatch replaces direct UDS calls.** Both gates
   still call primals via direct UDS. The biomeOS signal graph should
   mediate, enabling cross-gate event propagation (e.g., "westGate dataset
   CONVERGED → strandGate can now compute on it").

5. **Convergence sweep target.** westGate has 0/153 datasets CONVERGED
   (89 PARTIAL, 32 PRIMORDIAL). strandGate has 0/87 configs fully braided.
   Both need convergence sweeps before arXiv submission can cite complete
   provenance.

---

## Status

| Metric | westGate | strandGate |
|--------|----------|------------|
| Braiding throughput | 217/s (convoy), 265/s (inline) | ~0.05/s (CPU-bound generation) |
| Provenance overhead | ~5 ms/file (negligible) | ~12 ms/config (~2% of HMC) |
| CAS volume | 452–529 GB | ~30 GB projected |
| Datasets/configs | 153 datasets / 1.17M files | 87 configs / 6 gauge groups |
| Convergence | 0 CONVERGED / 89 PARTIAL / 32 PRIMORDIAL | 0 CONVERGED (NFT wired, not swept) |
| Architecture alignment | Canonical (post-fix) | Canonical (built correctly from start) |
| Key bottleneck | Storage I/O → solved with NVMe | CPU thermalization → solved with memoization |

---

*Cross-gate AAR for upstream dissemination. westGate's 700× braiding
breakthrough validates the provenance trio architecture at scale. strandGate's
compute memoization is the complementary dual — same primals, same braids,
different bottleneck. ironGate unifies both as the product CAS. The full
chain (data → compute → publication) is architecturally proven; convergence
sweeps and cross-frontier braiding remain to complete the wiring.*
