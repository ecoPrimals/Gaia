# AAR: Jelly String Elimination — From Python Glue to Primal-Native Braiding

**Date**: Aug 7, 2026 | **Wave**: 156e | **Gate**: westGate (Data NAS)
**Event**: Discovery and elimination of Python jelly strings in bulk braiding pipeline
**Status**: native_braid.py deployed, sra_fastq braided natively, alphafold A0 tiering design identified
**Team**: Hardware / Overwatch

---

## Executive Summary

The Python braiding pipeline (`bulk_braid.py` / `prov_inline.py`) was a complete
jelly string — every primal-native bulk operation it reimplemented in Python
already existed in Rust. The Python code was 4–30x slower than the native RPCs
it bypassed, consumed 3.8 GB of RAM for sorted file lists, and critically
**never called `content.exists` for cross-tier dedup**.

---

## The Jelly String Anatomy

### What Python Did Per File (~40 files/s from HDD)

```
1. sorted(rglob("*"))        → 10M Path objects in RAM (3.8 GB)
2. fp.read_bytes()            → full file into Python heap
3. blake3.blake3(data)        → hash via Python binding
4. base64.b64encode(data)     → doubles memory per file
5. json.dumps({...})          → serialize with base64 payload
6. socket() → connect() →    → new Unix socket per content.put
   send(json) → recv() →
   close()
7. every 200 files:           → another socket roundtrip for
   dag.event.append_batch()      batch DAG append
```

**Total per file**: 2 socket connections, 2 JSON serializations, 1 full file
read, 1 base64 encode (2x memory), 1 Python BLAKE3 hash.

### What Rust Already Provides (Bypassed)

| Python Jelly String | Primal-Native Rust RPC | Status |
|---|---|---|
| `sorted(rglob("*"))` | `content.ingest` walks dir natively | In nestGate |
| `blake3.blake3(data)` | Rust BLAKE3 in `content.ingest` | In nestGate |
| `base64.b64encode` + `content.put` | `content.ingest` stores to CAS directly | In nestGate |
| Per-file `content.put` socket | Single RPC for entire directory | In nestGate |
| No dedup check | `content.exists` — cross-tier (warm→cold→legacy) | In nestGate |
| `dag.session.create` + loop | `dag.pipeline.ingest` (create + batch + dehydrate) | In rhizoCrypt (not wired) |
| `dag.event.append_batch` in 200-file batches | `dag.event.append_batch` (same, but fewer roundtrips) | In rhizoCrypt |
| Individual `braid.create` | `braid.batch_create` + `braid.batch_commit` | In sweetGrass |

### Capabilities Discovered But Not Yet Wired

| RPC | Primal | Status | Impact |
|---|---|---|---|
| `dag.pipeline.ingest` | rhizoCrypt | Code exists, not in dispatch | Would eliminate session+batch+dehydrate dance |
| `dag.dehydration.trigger_batch` | rhizoCrypt | Wired | Multi-session concurrent dehydrate |
| `braid.batch_create` | sweetGrass | Wired | Bulk braid creation |
| `braid.batch_commit` | sweetGrass | Wired | Bulk commit (forwards to loamSpine) |

**These capabilities should all be exposed through biomeOS neuralAPI for complex
dispatching and graph-based orchestration.** The current Python scripts manually
sequence what should be a biomeOS provenance graph: CAS ingest → DAG record →
spine commit → braid create. This is exactly the kind of multi-primal workflow
that neuralAPI dispatch is designed for.

---

## Dedup Failure Analysis

### Bug 1: Python Never Calls `content.exists`

The `InlineBraid.ingest()` and `ChunkedBraid.ingest()` methods blindly send
every file's data to `content.put` without checking if CAS already has it.
Even when `content.put` returns `deduplicated: true`, Python has already:
- Read the entire file from disk
- Hashed it in Python
- Base64-encoded it (doubling memory)
- Serialized to JSON
- Sent the full payload over a socket

The dedup happens AFTER all the expensive work. It should happen BEFORE reading.

### Bug 2: `content.ingest` Only Checks Hot Tier

In `ingest.rs` line 383–385:
```rust
let cas_path = content_key_path(family_id, &hash_hex);
if cas_path.exists() { return Ok(FileResult { was_dedup: true, ... }); }
```

`content_key_path` → `content_cas_path` → `cas_content_layout(&cas_hot_root(), ...)`.
This builds the **hot tier path only**. It does NOT call `resolve_cas_object()`
which checks warm → cold → legacy tiers.

**Fix**: Replace `content_key_path` with `resolve_cas_object` in `ingest.rs`.

### Bug 3: CAS Family Mismatch

Python braider used `content.put` without specifying `family_id`, defaulting to
`standalone`. The `content.ingest` test used `family_id: "default"`. Different
families have separate `_content/` directories — **zero cross-family dedup**.

**Fix**: Standardize on a single CAS family for all braiding operations.

---

## Data Tiering Failure: "Never Work on Spinners"

### The Rule

```
Cold (HDD/ZFS)  = STORAGE ONLY. Never read for compute.
Warm (SSD/L2ARC) = Read cache. ZFS handles automatically.
Hot (NVMe)       = ALL WORK happens here. Stage → Process → Unstage.
```

### What Went Wrong

1. **rsync timeout**: Staging A0 (10M files, ~3 TB) timed out at 2 hours → fell
   back to braiding directly on HDD at 27.8 files/s

2. **Oversized chunk probe**: Added `probe_dir_size()` to detect oversized chunks,
   but the "fix" was to **skip staging and braid from HDD** — violating the rule

3. **content.ingest on cold**: Called `content.ingest` pointing at HDD path — Rust
   walks the directory on spinners (metadata I/O at 2 MB/s)

4. **CAS write overflow**: `content.ingest` copies files to NVMe CAS. For 3 TB of
   data, NVMe (1.4 TB free) overflows. No backpressure in `content.ingest`.

### The Correct Architecture

For oversized directories that exceed NVMe capacity:

```
┌──────────────────────────────────────────────────┐
│               BATCH STAGING LOOP                  │
│                                                   │
│  for batch in split(A0, batch_size=500GB):        │
│    1. rsync batch → NVMe staging                  │
│    2. content.ingest(NVMe_staging_path)            │
│       → Rust walks NVMe (fast), hashes, CAS stores │
│    3. dag.event.append_batch(manifest)             │
│    4. rm -rf NVMe staging batch                   │
│    5. repeat until all batches done                │
│  end                                              │
│  dag.dehydrate → spine.commit → braid.create      │
└──────────────────────────────────────────────────┘
```

This keeps ALL compute on NVMe. HDD is only touched for sequential `rsync` reads
(where spinners are efficient). The staging batch size is bounded by NVMe free
space (e.g., 500 GB batches with 1.4 TB free = safe margin).

### Why This Needs biomeOS

Manual Python orchestration of this loop is another jelly string. The batch
staging → ingest → clean cycle is a **graph** with dependencies and backpressure:

```
rsync_batch_N → content.ingest_N → dag.append_N → cleanup_N → rsync_batch_N+1
                                                       ↓
                                              warm_tier_free > 500GB?
                                                    (backpressure)
```

biomeOS neuralAPI should dispatch this as a provenance graph where each node is
a primal RPC call and edges are data dependencies + capacity constraints.

---

## Native Braider Results

### `native_braid.py` — Python as Thin Orchestrator

Replaced the Python file I/O pipeline with pure RPC orchestration:

```python
# BEFORE: Python reads, hashes, base64-encodes every file
data = fp.read_bytes()                    # Python heap
h = blake3.blake3(data).hexdigest()       # Python binding
_rpc("nestgate", "content.put", {         # base64 payload over socket
    "data": base64.b64encode(data).decode()
})

# AFTER: One RPC per directory, Rust does everything
manifest = rpc("nestgate", "content.ingest", {
    "directory": str(chunk_dir),          # Rust walks, hashes, CAS stores
    "family_id": "standalone",
})
# manifest = {filename: blake3_hex, ...}  ← ready for DAG events
```

### sra_fastq Benchmark

| Metric | Python (`bulk_braid.py`) | Native (`native_braid.py`) |
|---|---|---|
| Time | Never completed (would stage 267 GB) | **114 seconds** |
| Chunks | 5 | 5 |
| Files | 753 | 753 |
| Dedup | 0 first run, unknown on re-run | **351/351 on re-run (100%)** |
| Python memory | ~500 MB (sorted list + base64) | **13 MB** (RPC orchestrator only) |
| File I/O in Python | Every byte | **Zero** |
| Sockets opened | 753 × 2 = 1,506 | **5 × 3 = 15** |

### Key Insight: Dedup Verified

```
Run 1: 351 files (0 dedup) — Rust hashed and CAS-stored all files
Run 2: 351 files (351 dedup) — Rust checked CAS paths, skipped all writes
```

`content.ingest` dedup works correctly within-tier. Cross-tier dedup bug is
separate (needs `resolve_cas_object` fix in `ingest.rs`).

---

## Jelly Strings Resolved This Wave

| Jelly String | Root Cause | Resolution |
|---|---|---|
| Python file I/O for braiding | Didn't know `content.ingest` existed | Use `content.ingest` — zero Python file I/O |
| No dedup before read | Never called `content.exists` | `content.ingest` dedup is native |
| 3.8 GB sorted file list | `sorted(rglob("*"))` on 10M files | `content.ingest` walks in Rust, no Python list |
| Base64 encoding every file | `content.put` requires base64 payload | `content.ingest` reads files directly, no encoding |
| Per-file socket roundtrip | One `content.put` per file | One `content.ingest` per directory |
| HDD fallback for oversized chunks | Staging timeout / size exceeded NVMe | **Open**: batch staging loop needed |
| CAS family mismatch | Python default vs explicit family_id | Standardized on `standalone` family |
| `content.ingest` hot-only dedup | Uses `content_key_path` not `resolve_cas_object` | **Open**: Rust fix needed in `ingest.rs` |

---

## Open Items for Next Wave

### 1. Wire `dag.pipeline.ingest` into rhizoCrypt Dispatch

The handler exists in code (`dispatch_pipeline_ingest` in `dehydration.rs`) but
is not registered in the RPC dispatch table. Wiring it eliminates the
session.create → append_batch → dehydrate dance.

### 2. Fix Cross-Tier Dedup in `content.ingest`

Replace `content_key_path` with `resolve_cas_object` in `ingest.rs` line 383.
One-line change, massive impact for retrospective braiding where CAS objects
may already exist on cold tier.

### 3. Batch Staging for Oversized Chunks

Build the batch staging loop (or expose it as a biomeOS graph). For A0:
- 10M files, ~3 TB
- NVMe has 1.4 TB free
- Stage 500 GB batches, ingest, cleanup, repeat
- ~6 batches × (stage + ingest + cleanup) = several hours total

### 4. biomeOS neuralAPI Provenance Graph

All these capabilities should be composable through biomeOS:
- `content.ingest` → `dag.pipeline.ingest` → `session.commit` → `braid.create`
- Backpressure: warm tier free space, convergence lag
- Batch sizing: dynamic based on NVMe capacity
- Crash resume: spine state as graph checkpoint

The current Python scripts are manually sequencing what the neuralAPI dispatch
graph should handle natively with topology-aware routing and backpressure.

### 5. `content.ingest` Warm Tier Backpressure

`content.ingest` does not check `warm_tier_capacity()` before writing CAS objects.
For multi-TB directories, this can overflow NVMe. Either:
- Add backpressure (reject when warm tier low), or
- Add a `hash_only` mode that returns the manifest without CAS writes
  (for retrospective braiding of data already stored on cold)

---

## Hardware Topology Profile

```
westGate Tower 155f — Aug 7, 2026

T0  RAM     64 GB DDR4    ZFS ARC 26 GB, 96.4% hit rate
T1  NVMe    1.8 TB        CAS hot writes, staging, OS — 1.4 TB free
T2  SSD     (2× via L2ARC) ZFS warm read cache
T3  HDD     8× in raidz1  nestGate cold, ZFS, 45.7 TB pool

Primals: nestGate, rhizoCrypt, loamSpine, sweetGrass, bearDog
Transport: membrane UDS (Unix domain sockets), riboCipher framed JSON-RPC
```

---

*"The fastest code is the code you don't write. The fastest I/O is the I/O you
don't do. Every line of Python between the user's intent and the Rust primal is
a jelly string waiting to slow you down."*
