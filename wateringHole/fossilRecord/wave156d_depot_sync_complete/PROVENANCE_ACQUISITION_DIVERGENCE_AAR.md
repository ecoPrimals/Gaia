# AAR: Provenance × Acquisition Speed Divergence

**Date**: Aug 4, 2026
**Wave**: 156a
**Gate**: westGate
**Team**: Hardware / Overwatch
**Audience**: Upstream primals teams, sporeGate topology, biomeOS signal team

---

## Objective

Make provenance tracking integral to data acquisition — no more separate
revalidation passes. "From here on out, we should be getting provenance with
the data pulls."

## What Happened

### Phase 1: Inline Provenance (Direct Approach)

Wired the full provenance chain directly into `alphafold_bulk_download.py`:

```
download .cif → BLAKE3 hash → CAS put → DAG event → spine entry
```

**Result: 12× throughput collapse.** Download rate dropped from 74 files/s to
5–6 files/s. At 5/s, the 240M remaining AlphaFold structures would take
~555 days instead of ~37 days.

### Root Cause

Each provenance step is a synchronous UDS RPC call:

| Operation | Target Socket | ~Latency (fresh) | Latency at 187K entries |
|-----------|--------------|-------------------|------------------------|
| `blake3_hash` | local CPU | < 1ms (300 KB file) | < 1ms |
| `cas_put` | nestgate.sock | 5–10ms | 54ms |
| `dag_event_append` | rhizocrypt.sock | 5–10ms | 4ms |
| `spine_entry_append` | loamspine.sock | 5–10ms | **3,536ms** |

**UPDATE (Aug 4 AM)**: The real bottleneck is `spine_entry_append` at scale.
At 187K spine entries, each append takes **3.5 seconds** — this is the dominant
cost, not UDS serialization. At 3.5s/file, the trailer can process 0.3 files/s.
For 6M already-downloaded files, that's 243 days. For 240M remaining, it's
literally years.

Total provenance per file: 3.6s (dominated by loamSpine append).

**This is the acquisition-provenance divergence**: download throughput scales
with network concurrency, but provenance throughput is bounded by loamSpine's
O(n) spine entry append at scale.

### Phase 2: Trailer Architecture

Decoupled into two companion services:

| Service | Role | Rate |
|---------|------|------|
| `alphafold-bulk.service` | Download only (full speed) | 63–74/s |
| `alphafold-prov.service` | Follows behind, braids new files | ~30–40/s |

The trailer reads the download progress file, finds unbraided .cif files on
disk, and runs the full provenance chain. It can fall behind temporarily but
catches up during pauses (rate limits, network issues, restarts).

**Problem discovered**: the initial `find_unbraided()` scan across 5.8M files
in thousands of subdirectories was itself too slow. The trailer needs a
progress-file-driven approach rather than filesystem scan.

### Phase 3: Metered Download Script

Updated `metered_download.sh` to call `revalidate_data.py --dataset` after
each download completes. This works well for the sequential queue (one file
at a time), but doesn't scale for the async bulk downloader.

### Phase 4: Standard Acquisition Pattern

Added `fetch_and_ingest()` to `bulk_ingest.py` — a single function that
downloads a URL and immediately runs it through the full provenance chain.
This is the correct pattern for small-to-medium datasets (<1000 files).

---

## Phase 5: Canonical Architecture Alignment (RESOLVED)

**UPDATE (Aug 4, 2026)**: Deep spec review revealed the root cause was not
a performance bug — it was an architectural misalignment. **Per-file spine
entries were never the canonical provenance architecture.**

The specs (`PROVENANCE_TRIO_INTEGRATION_GUIDE.md` v2.0,
`loamSpine/specs/INTEGRATION_SPECIFICATION.md` §3,
`loamSpine/specs/API_SPECIFICATION.md` §3.4) all describe the canonical flow as:

- Per file: `BLAKE3 → CAS → dag.event.append` (4ms, O(1))
- Per dataset (once): `dehydrate → session.commit → sign → braid`

Per-file `DataAnchor` spine entries are an **interim federation-layer pattern**
from `nest_acquire_file.toml`, not the canonical trio flow. The `rootpulse_commit`
and `nest.complete_dataset` signal graphs both finalize with one `session.commit`,
not per-file `entry.append`.

The patterns in the biomeOS signal graph specs — session-level commits, Merkle
root binding, deferred permanence — were theory until this moment. When wired
correctly, they deliver the throughput the architecture promises.

### What Changed

1. **Removed `spine_entry_append` from per-file loops** in `bulk_ingest.py`,
   `revalidate_data.py`, and `alphafold_prov_trailer.py`. The DAG Merkle root
   cryptographically binds all files — per-file spine entries are redundant.

2. **Wired bearDog signature into sweetGrass braid** — `braid_create()` now
   includes `ed25519_signature`, `signature_scope`, and `signer` fields.
   The provenance loop is closed: hash → DAG → Merkle root → signature → braid.

3. **Added `dag.event.append_batch`** to the trailer — 200 events per RPC call
   instead of individual appends. (`dag.pipeline.ingest` is specced in G31 but
   not in the running binary; `dag.event.append_batch` is available and tested.)

### Result

```
BEFORE (per-file spine entries):
  Provenance rate:   0.3 files/s  (loamSpine O(n) bottleneck at 187K entries)
  Time for 6.1M queue: 243 days
  Time for 240M files: ~27 years

AFTER (canonical architecture, no per-file spine):
  Provenance rate:   37.6 files/s sustained, 0 errors
  Time for 6.1M queue: ~45 hours
  Time for 240M files: ~74 days
```

**122× throughput improvement.** The trailer is running and braiding at the
rate the architecture was designed for.

---

## Current State

| Component | Status | Detail |
|-----------|--------|--------|
| AlphaFold bulk download | RUNNING | 6.1M done, 240M remaining, 63/s |
| AlphaFold prov trailer | **RUNNING** | **37.6 files/s**, canonical pipeline (CAS + batch DAG) |
| nestGate CAS | HEALTHY | v0.5.0 |
| metered_download.sh | UPDATED | Inline provenance per download |
| bulk_ingest.py | UPDATED | Canonical pipeline, `fetch_and_ingest()`, batch DAG |
| revalidate_data.py | UPDATED | Canonical pipeline (no per-file spine) |

### Provenance Coverage

| Data Class | Files | Braided? | Method |
|------------|-------|----------|--------|
| Priority datasets (14) | ~33K | YES | CAS ingest script |
| SRA FASTQ (785 files) | 785 | YES | Revalidation complete |
| AlphaFold structures (6.1M) | 6.1M | **BRAIDING** | Trailer at 37.6/s (~45h ETA) |
| AlphaFold proteomes (1,145) | 1,145 | COMPLETE | Background braid job |
| New downloads (metered) | varies | YES | metered_download.sh inline |
| New AlphaFold structures | 240M+ | TRAILER ACTIVE | Continuous braiding behind downloader |

---

## The Divergence Problem (NARROWED)

The original divergence:

```
Acquisition rate:    74 files/s  (bounded by network + API)
Provenance rate:     37.6 files/s  (canonical pipeline: CAS + batch DAG)
Gap:                 ~2× at current scale
```

The gap is now **2× instead of 247×** (74/s vs 0.3/s). The trailer pattern
handles this: download fast, braid behind, catch up during pauses. At 37.6/s
the trailer keeps pace with most data sources and converges during any
download pause.

The remaining 2× gap is bounded by BLAKE3 hashing + CAS put + batch DAG RPC —
real work, not a serialization bug. Further optimization would require
streaming DAG or direct CAS writes, which are evolution-path items for upstream.

### Why This Matters Beyond AlphaFold

Any high-throughput data source will hit this same wall:
- Bulk genomic data from ENA/SRA
- PDB full mirror updates
- LINCS L1000 level 5 updates
- Any mesh-based data federation (gate-to-gate transfers at 10 Gbps)

The UDS RPC model works perfectly for human-speed operations (experiment
results, manual ingests, API queries). It breaks at machine-speed bulk
acquisition.

### Potential Evolution Paths

1. **Batch RPC**: Instead of one RPC per file, send batches of 100–1000
   events in a single DAG/spine call. This requires `dag.event_batch` and
   `spine.entry_batch` methods in rhizoCrypt and loamSpine.

2. **Direct CAS write**: For bulk imports, bypass the UDS RPC and write
   directly to the CAS storage layer (ZFS path). Then create a single DAG
   session covering the entire batch with a manifest hash.

3. **Provenance-at-rest**: Instead of inline provenance, write a manifest
   file alongside the download progress. A periodic job (timer) processes
   the manifest and creates provenance records. Trades immediacy for
   throughput.

4. **Streaming DAG**: rhizoCrypt accepts a persistent connection (not
   request-response) where events stream in and acknowledgments batch out.
   This eliminates per-event RPC overhead.

5. **Sharded provenance**: Multiple DAG sessions running in parallel on
   different socket endpoints. Each provenance worker gets its own session.
   Sessions merge at dehydration time.

### CRITICAL: loamSpine O(n) Append

The loamSpine `spine.entry.append` method degrades from 5ms (fresh spine)
to **3,536ms** at 187K entries. This is likely an O(n) scan or Merkle tree
rebuild on each append. At AlphaFold scale (240M files), this makes per-file
spine entries architecturally infeasible. Options:

1. **Batch spine entries**: Accept arrays of entries in one call, rebuild
   the Merkle tree once per batch instead of per entry.
2. **Sharded spines**: One spine per subdirectory or per 10K files. Merge
   spine roots into a super-spine at dehydration time.
3. **Deferred spining**: Skip spine entries during acquisition. Create the
   spine from the DAG session at dehydration time (DAG already has all hashes).

Option 3 is the most radical but may be correct — the spine's purpose is
Merkle certification of the dataset. If the DAG already tracks every hash,
the spine can be derived from the DAG rather than built incrementally.

### Recommended for biomeOS Signal Team

Option 1 (batch RPC) is the lowest-friction evolution. The existing
`dag.event.append` signal could gain a batch variant:

```toml
[signal.dag.event.batch]
provider = "rhizoCrypt"
params = ["session_id", "events"]  # events = [{hash, name, size, source}]
returns = ["vertex_ids"]
```

Similarly for spine:

```toml
[signal.spine.entry.batch]
provider = "loamSpine"
params = ["spine_id", "entries"]  # entries = [{hash, mime, size}]
returns = ["entry_ids"]
```

This keeps the existing architecture (UDS RPC, signal graphs, capability
registry) while eliminating the per-file overhead. A batch of 500 events
in one RPC call would close the 2× gap.

---

## Mixed Provenance → Unified CAS

The local westGate challenge: we now have data in three provenance states:

| State | Description | Example |
|-------|-------------|---------|
| **Primordial** | On disk, no CAS entry, no DAG, no spine | Early ad-hoc downloads |
| **CAS-only** | BLAKE3 hashed and in CAS, but no DAG/spine/braid | Old `content.put` calls |
| **Fully braided** | CAS + DAG session + spine + Merkle root + signature + braid | All new acquisitions |

To unify:

1. **Inventory**: Walk ZFS data root, cross-reference with CAS `content.exists`,
   check for DAG session and braid records per dataset.

2. **Promote primordial → fully braided**: Run `revalidate_data.py` per
   dataset. This creates the full chain retroactively. Already running for
   the priority datasets and AlphaFold structures.

3. **Promote CAS-only → fully braided**: These files already have BLAKE3
   hashes in CAS. Just need DAG session + spine + sign + braid wrapping.
   A lightweight variant of revalidation that skips the hash + CAS put.

4. **Convergence marker**: Once a dataset has a sealed Merkle root + braid,
   mark it as "converged" in a manifest. Springs can check convergence
   before trusting data for computation.

### Convergence Check Pattern

```python
def is_dataset_converged(dataset_name):
    """Check if a dataset has full provenance — safe for spring consumption."""
    braids = rpc_result("sweetgrass", "braid.list", {"dataset": dataset_name})
    if not braids:
        return False
    latest = braids[-1]
    sig = rpc_result("beardog", "signature.verify", {"hash": latest["merkle_root"]})
    return sig and sig.get("valid", False)
```

This becomes the gate between "data available" and "data trusted."

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/alphafold_bulk_download.py` | Reverted to clean download-only (removed inline prov) |
| `scripts/alphafold_prov_trailer.py` | Canonical pipeline: CAS + batch DAG, no per-file spine |
| `scripts/bulk_ingest.py` | Canonical pipeline, `dag_event_append_batch()`, signature in braid |
| `scripts/revalidate_data.py` | Canonical pipeline: no per-file spine, signature in braid |
| `scripts/metered_download.sh` | Added inline provenance per download |
| `scripts/alphafold_full_sync.sh` | Added provenance pass after sync |
| `systemd/alphafold-prov.service` | Trailer service unit |

---

## Upstream Actions

- **biomeOS signal team**: Design `dag.event.batch` and `spine.entry.batch`
  signals. This is the single highest-impact evolution for data throughput.
- **rhizoCrypt team**: Implement batch event append (accept array of events,
  return array of vertex IDs, single RPC round trip).
- **loamSpine team**: Implement batch entry append (same pattern).
- **sporeGate topology**: The acquisition-provenance divergence will also
  appear in mesh data transfers. Design bandwidth governance to account for
  provenance overhead in federation throughput calculations.
- **westGate local**: Fix the prov trailer's file discovery (use progress
  file diff instead of filesystem scan). Continue revalidation of existing
  data. Target: all spring-critical data fully braided before Phase 4 boot.

---

## Lessons

1. **Read the spec before optimizing.** The 122× improvement came not from
   clever batching or sharding, but from aligning with the canonical
   architecture. Per-file spine entries were an interim federation pattern,
   not the designed flow. The specs had the answer the whole time.

2. **Spec patterns are often theory until load proves them.** The biomeOS
   signal graphs described session-level commits, Merkle root binding, and
   deferred permanence — but nobody had pushed 187K entries through loamSpine
   before. Real load exposed the gap between "this should work" and "this
   does work." When wired correctly, the architecture delivers.

3. **The trailer pattern works** as a bridge. Download fast, braid behind,
   catch up during pauses. With the canonical pipeline at 37.6/s, the trailer
   keeps pace with most data sources. No data exists on ZFS without eventually
   getting a Merkle root and braid.

4. **Mixed provenance is a real state** that the system handles gracefully.
   The trio is explicitly non-atomic with graceful degradation — partial
   states (DAG-only, CAS-only, fully braided) are valid. The convergence
   check pattern gates spring consumption.

5. **The `fetch_and_ingest()` pattern is the right default** for everything
   except bulk downloads. One function call: download + full provenance.
   All future acquisition scripts should use it.

6. **Close the provenance loop.** bearDog signatures were being computed but
   orphaned — not attached to the sweetGrass braid. The signature is the
   cryptographic proof that the Merkle root is authentic. Without it in the
   braid, the chain has a gap. Now closed.

7. **`dag.event.append_batch` already exists.** rhizoCrypt's G31 batch
   operations were implemented but not used by westGate scripts. The trailer
   now sends 200 events per RPC call. The infrastructure was ahead of the
   consumption patterns.

---

*The provenance divergence was the first real-world scaling test for the
primal composition model. The resolution proves the architecture: when
wired canonically, five primals compose at machine speed. The specs weren't
aspirational — they were right.*
