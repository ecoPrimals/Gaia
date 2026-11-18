# Depot Lineage Specification (G69)

**Date**: Aug 9, 2026 | **Wave**: 157d | **Author**: sporeGate topology
**Status**: SPECIFICATION — convergence target for cellMembrane + provenance trio
**Predecessor**: G66 Transport Abstraction (COMPLETE), G68 Platform Substrate (COMPLETE)
**Origin**: Depot rebuild pushed 108 binaries across 4 architectures with no history, no pruning policy, and no lineage tracking. The same content-addressed braiding pattern used by westGate data braids and ironGate QCD NFT archival applies directly to binary evolution.

---

## The Problem: Depot Is Amnesiac

The current depot (`golgi:/opt/ecoPrimals/depot/primals/{arch}/`) is a flat directory
of binaries. On every harvest push, the old binary is **overwritten** — its BLAKE3
existed momentarily in `checksums.toml` and `provenance.toml` but is gone after the
next generation. There is no record of what the previous binary was, when it was
replaced, or what commit produced it.

```
                     before harvest          after harvest
    depot/musl/      songbird  (42aba605)    songbird  (new-commit)
                     blake3: 8ddaf67...      blake3: a1b2c3d...

    history:         ???                     ???
```

Meanwhile, the provenance trio (rhizoCrypt + loamSpine + sweetGrass) already solves
exactly this problem for data files via CAS braids. And `rootpulse_harvest_commit`
already records build events to the trio — but as disconnected point events, not a
linked lineage chain.

Binary evolution is data evolution. The same pattern applies.

---

## The Pattern: Binary Lineage via Provenance Trio

Each binary is a **phenotype** — the expressed version of a primal for a given
architecture. Its **genotype** is the 4-tuple `(primal, arch, commit, blake3)`.

Evolution creates a lineage DAG: each generation links to its parent.

```
    songBird / x86_64-unknown-linux-musl

    Gen 0:  commit=af0d8fa8  blake3=old1...  (pre-seam)
       │
       ▼
    Gen 1:  commit=42aba605  blake3=8dda...  (seam fix)
       │
       ▼
    Gen 2:  commit=????????  blake3=a1b2...  (next evolution)
```

### Binary Identity (Genotype)

Each binary has an immutable identity:

```toml
# Conceptual — stored as DAG event metadata, not a separate file
[identity]
primal     = "songbird"
arch       = "x86_64-unknown-linux-musl"
commit     = "42aba605"
blake3     = "8ddaf67e3fb069c0a93a82031c336dc7f20a45ae74c32157fa429ea71f88a2cd"
size       = 22585408
builder    = "sporeGate"
rustc      = "rustc 1.96.1"
timestamp  = "2026-08-09T14:34:46Z"
```

### Lineage Chain (DAG Events)

Each harvest creates a DAG event in rhizoCrypt with:

```
session_type:  "harvest"
event_type:    "binary.evolve"
metadata:      { primal, arch, commit, blake3, size, builder }
parents:       [ previous_harvest_event_id ]   ← THIS IS THE LINEAGE LINK
payload_ref:   blake3 (CAS reference to the binary itself)
```

The `parent` field chains generations. For a new primal's first build,
`parents` is empty (genesis event).

### Three Storage Tiers

```
    ┌─────────────────────────┐
    │  Depot (golgi)          │  HEAD only — latest verified binary per (primal, arch)
    │  /opt/ecoPrimals/depot/ │  Overwritten on every harvest push
    │  checksums.toml         │  BLAKE3 of current HEAD
    │  provenance.toml        │  Source commit of current HEAD
    └────────────┬────────────┘
                 │ on replacement, old binary's BLAKE3 is already in CAS
                 ▼
    ┌─────────────────────────┐
    │  CAS (ironGate / golgi) │  Content-addressed storage by BLAKE3
    │  Deduplicated blobs     │  Every binary ever built lives here
    │  nestGate content.put   │  Same infrastructure as data braids
    └────────────┬────────────┘
                 │ spine entries link CAS blobs into lineage
                 ▼
    ┌─────────────────────────┐
    │  Spine (loamSpine)      │  Permanent lineage record
    │  One spine per primal   │  Each entry = one generation
    │  Merkle-linked          │  Tamper-evident history
    └─────────────────────────┘
```

**Depot = HEAD pointer.** CAS = full archive. Spine = linkage.

This is identical to the data braid pattern:
- Data braids: file content → CAS → DAG → spine → braid
- Binary braids: binary → CAS → DAG → spine → (optional braid for attribution)

---

## Integration with Existing Infrastructure

### rootpulse_harvest_commit (cellMembrane)

`sovereignty_ledger.rs` already records `HarvestProvenanceEntry {primal, commit, target, blake3}` via the `rootpulse_commit` graph. Extend with:

1. **parent_event_id**: Look up the previous harvest event for this `(primal, arch)` pair from the provenance spine before creating the new event
2. **cas_ref**: After building, `content.put` the binary blob to nestGate CAS — the BLAKE3 already computed during checksums generation is the CAS key
3. **spine_entry**: After DAG event, commit a spine entry per `(primal, arch)` so lineage is queryable

### provenance.toml

Extend the existing `provenance.toml` with lineage metadata:

```toml
# Current format (unchanged — backward compatible)
[songbird]
commit = "42aba605"

# New optional fields (G69)
blake3 = "8ddaf67e3fb069c0a93a82031c336dc7f20a45ae74c32157fa429ea71f88a2cd"
previous_blake3 = "old_hash_here"
generation = 2
harvest_event_id = "harvest-sporeGate-20260809T143446"
```

The `previous_blake3` and `generation` fields form a local HEAD pointer
with minimal backward reference. The full lineage lives in the spine.

### checksums.toml

No changes. `checksums.toml` remains a point-in-time manifest of current
HEAD binaries. It is the "phenotype registry" — what's currently expressed.

### Depot Pruning (depot.prune)

New command: `membrane depot.prune`

Enforces an allowlist from `ecosystem_manifest.toml` — only binaries matching
known primal names survive. Test binaries, demo binaries, bench binaries, and
non-`.exe` Linux binaries in the Windows arch directory are removed.

```
Allowlist source:  ecosystem_manifest.toml [primals] keys
Arch convention:   {primal_name}       (musl/gnu/aarch64)
                   {primal_name}.exe   (windows-gnu)
Protected files:   checksums.toml, BLAKE3SUMS, provenance.toml
```

### Lineage Query (depot.lineage)

New command: `membrane depot.lineage --primal songBird --arch x86_64-unknown-linux-musl`

Queries the provenance spine for the harvest event chain for a given
`(primal, arch)` pair. Returns the commit chain with BLAKE3 at each point.

```json
{
  "primal": "songbird",
  "arch": "x86_64-unknown-linux-musl",
  "generations": [
    { "gen": 0, "commit": "af0d8fa8", "blake3": "old1...", "builder": "sporeGate", "date": "2026-07-15" },
    { "gen": 1, "commit": "42aba605", "blake3": "8dda...", "builder": "sporeGate", "date": "2026-08-09" }
  ],
  "head": 1,
  "total_size_bytes": 45170816
}
```

---

## Convergence with Data Braids

The binary lineage pattern and the data braid pattern are implementations
of the same abstract concept:

| Concern | Data Braids (westGate) | Binary Lineage (depot) |
|---------|----------------------|----------------------|
| Content identity | BLAKE3 of file chunk | BLAKE3 of binary |
| CAS storage | nestGate `content.put` | nestGate `content.put` |
| DAG events | rhizoCrypt `dag.event.append` | rhizoCrypt `dag.event.append` |
| Spine record | loamSpine `session.commit` | loamSpine `session.commit` |
| Attribution | sweetGrass `braid.create` | Optional — builder identity in metadata |
| Lineage | braid derivation chains | harvest parent event chain |
| HEAD pointer | `.braided` marker file | `provenance.toml` commit field |
| Archive | cold ZFS on westGate | CAS on ironGate |
| Orchestrator | `native_braid.py` (→ Rust) | `rootpulse_harvest_commit` |

Both should converge on the same trio RPCs and spine conventions.
`native_braid.py` → Rust migration and binary lineage implementation
can share abstraction patterns.

---

## Scope: Who Implements What

| Component | Owner | Scope |
|-----------|-------|-------|
| `provenance.toml` extension | sporeGate topology | Depot metadata format |
| `rootpulse_harvest_commit` lineage | sporeGate topology | cellMembrane harvest pipeline |
| `membrane depot.prune` | sporeGate topology | Depot cleanup automation |
| `membrane depot.lineage` | sporeGate topology | Lineage query CLI |
| nestGate CAS for binaries | nestGate primal team | `content.put` at binary scale |
| rhizoCrypt harvest sessions | rhizoCrypt primal team | DAG session support for binary events |
| loamSpine harvest spines | loamSpine primal team | Spine per `(primal, arch)` |
| sweetGrass binary attribution | sweetGrass primal team | Optional — builder identity braids |
| Data braid convergence | westGate / data team | Pattern alignment, shared abstractions |

sporeGate topology owns the depot pipeline and the integration orchestration.
Primal teams own their respective trio surfaces. This spec does NOT prescribe
changes to primal internals — it defines the contract between cellMembrane
(the depot pipeline) and the trio (the provenance infrastructure).

---

## Implementation Phases

### Phase 1: Depot Pruning (immediate)

- Implement `membrane depot.prune` with ecosystem manifest allowlist
- Wire into harvest pipeline finalization (after checksums, before push)
- Prevents test/demo/bench binary bloat on golgi

### Phase 2: Lineage Metadata (provenance.toml extension)

- Add `blake3`, `previous_blake3`, `generation`, `harvest_event_id` fields
- Backward compatible — old membrane binaries ignore unknown fields
- Local lineage tracking without requiring trio availability

### Phase 3: CAS Archival (binary content.put)

- On harvest, `content.put` the built binary to nestGate CAS
- BLAKE3 is already computed — CAS key is free
- Requires ironGate CAS capacity assessment (binaries are 3-40 MB each)

### Phase 4: Spine Lineage (trio integration)

- Extend `rootpulse_harvest_commit` with `parent_event_id` chaining
- Create one loamSpine spine per `(primal, arch)` for lineage queries
- Implement `membrane depot.lineage` CLI
- sweetGrass attribution optional (builder identity in event metadata suffices)

---

*G69 — Binary evolution is data evolution. The depot is a HEAD pointer; CAS is the
genome archive; the spine is the phylogenetic tree. Same trio, same pattern, same
infrastructure. Convergent evolution with data braids, not parallel invention.*
