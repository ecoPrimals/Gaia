# sweetGrass Convergence Backpressure — Design

**Status**: IMPLEMENTED | **Wave**: 156d→156j | **Date**: Aug 6, 2026
**Gate**: westGate (design) → eastGate (implementation)
**Team**: Hardware / Overwatch (design), sporeGate (impl)
**Audience**: Download pipeline authors, sweetGrass / nestGate primal teams
**Implementation**: sweetGrass `convergence.pressure` method — see `SWEETGRASS_WAVE156J_C2_BACKPRESSURE_AUG06_2026.md`

---

## Problem

westGate's download and braiding pipelines have no flow control between
data acquisition and provenance completion. A download pipeline can ingest
data faster than the provenance trio can braid it, filling the NVMe hot
tier and causing ENOSPC. The bandwidth governance spec (BANDWIDTH_GOVERNANCE_SPEC.md)
gates the *network* pipe. This design gates the *storage* pipe — should we
download at all, given how much unbraided data is in flight?

Current state of backpressure:

| Layer | Mechanism | Status |
|-------|-----------|--------|
| Network | Manifest `rate_limit_mbps`, hardcoded concurrency | Deployed (uncoordinated) |
| Network governance | `topology.bandwidth.budget` | Spec only (stub in manifest_download.py) |
| Storage (nestGate) | `warm_tier_min_free` rejects CAS writes < 10 GB free | Deployed ✓ |
| Provenance (sweetGrass) | None | **This design** |

The nestGate storage backpressure catches the crisis (disk full). sweetGrass
convergence backpressure prevents the crisis from occurring by slowing
acquisition *before* the hot tier fills.

---

## Design Principle: Convergence Lag as Pressure Signal

**Convergence lag** = the count (or byte volume) of data that has been
acquired but not yet fully converged through the provenance trio.

A file is **converged** when all five stages are present:
1. `cas` — content stored in CAS (nestGate `content.put`)
2. `dag` — DAG event appended (rhizoCrypt `dag.event.append`)
3. `spine` — session committed to spine (loamSpine `session.commit`)
4. `braid` — attribution braid created (sweetGrass `braid.create`)
5. `signed` — cryptographic witness attached (bearDog `crypto.sign`)

sweetGrass upstream (origin/main) ships `convergence.check` and
`convergence.batch_check` which verify all five stages per content hash.

The backpressure signal is:

```
if convergence_lag > high_water:
    pause downloads until lag < low_water
```

This is a standard high-water / low-water flow control pattern, applied
at the provenance layer instead of the storage layer.

---

## Architecture

```
                      ┌─────────────────────────────┐
                      │   Download Pipeline          │
                      │   (manifest_download.py,     │
                      │    alphafold_bulk_download,   │
                      │    any future downloader)     │
                      └──────────┬──────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  convergence_gate()      │
                    │  ┌───────────────────┐   │
                    │  │ 1. warm_tier_free  │   │  ← nestGate statvfs
                    │  │ 2. convergence_lag │   │  ← sweetGrass batch_check
                    │  │ 3. bandwidth_avail │   │  ← topology.bandwidth (future)
                    │  └───────────────────┘   │
                    │  verdict: GO / WAIT / STOP│
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  InlineBraid.ingest()    │
                    │  (BLAKE3 → CAS → DAG →  │
                    │   spine → sign → braid)  │
                    └─────────────────────────┘
```

---

## API: `convergence_gate()`

A single function that download scripts call before each batch of
downloads. Returns a verdict and recommended action.

```python
def convergence_gate(
    dataset: str,
    batch_size: int = 100,
    warm_min_free_gb: float = 20.0,
    convergence_lag_max: int = 10000,
) -> dict:
    """
    Check whether the pipeline should continue downloading.

    Returns:
        {
            "verdict": "GO" | "WAIT" | "STOP",
            "warm_free_gb": float,
            "unconverged_count": int,
            "wait_seconds": int,       # suggested wait if WAIT
            "reason": str,
        }
    """
```

### Verdict logic

| Condition | Verdict | Action |
|-----------|---------|--------|
| warm_free < 10 GB (nestGate floor) | **STOP** | Do not download. Hot tier is critically low. |
| warm_free < `warm_min_free_gb` | **WAIT** | Pause, poll every 30s until free > low_water |
| unconverged > `convergence_lag_max` | **WAIT** | Too much in-flight data. Let braiding catch up. |
| unconverged > lag_max × 0.5 AND warm_free < 50 GB | **WAIT** | Combined pressure — both metrics warn |
| All clear | **GO** | Continue downloading at full rate |

### Implementation sketch

```python
def convergence_gate(dataset, batch_size=100, warm_min_free_gb=20.0,
                     convergence_lag_max=10000):
    result = {"verdict": "GO", "reason": "clear"}

    # 1. Storage pressure (nestGate warm tier)
    try:
        tier_info = rpc_result("nestgate", "substrate.tiers", {})
        warm = next((t for t in tier_info.get("tiers", [])
                     if t.get("tier") == "warm"), None)
        if warm:
            free_gb = warm.get("free_bytes", 0) / (1024**3)
            result["warm_free_gb"] = round(free_gb, 1)
            if free_gb < 10:
                result["verdict"] = "STOP"
                result["reason"] = f"warm tier critically low ({free_gb:.1f} GB free)"
                return result
            if free_gb < warm_min_free_gb:
                result["verdict"] = "WAIT"
                result["wait_seconds"] = 30
                result["reason"] = f"warm tier low ({free_gb:.1f} GB < {warm_min_free_gb} GB)"
    except Exception:
        pass  # nestGate unavailable — fall through to convergence check

    # 2. Convergence lag (sweetGrass)
    try:
        conv = rpc_result("sweetgrass", "convergence.batch_check", {
            "dataset": dataset,
            "limit": convergence_lag_max + 1,
        })
        if isinstance(conv, dict):
            unconverged = conv.get("unconverged_count", 0)
            result["unconverged_count"] = unconverged
            if unconverged > convergence_lag_max:
                result["verdict"] = "WAIT"
                result["wait_seconds"] = 60
                result["reason"] = (f"convergence lag too high "
                                    f"({unconverged} > {convergence_lag_max})")
    except Exception:
        pass  # sweetGrass unavailable — proceed without convergence check

    return result
```

### Integration in download scripts

**manifest_download.py** — wrap the download loop:

```python
for i, entry in enumerate(entries):
    if i % batch_size == 0:
        gate = convergence_gate(dataset)
        while gate["verdict"] == "WAIT":
            log(f"  BACKPRESSURE: {gate['reason']} — waiting {gate['wait_seconds']}s")
            time.sleep(gate["wait_seconds"])
            gate = convergence_gate(dataset)
        if gate["verdict"] == "STOP":
            log(f"  STOPPED: {gate['reason']}")
            break

    # ... existing download + braid logic ...
```

**bulk_braid.py** — check before staging each dataset:

```python
gate = convergence_gate(dataset_name, warm_min_free_gb=STAGE_MIN_FREE_GB)
if gate["verdict"] == "STOP":
    log(f"  SKIP {dataset_name}: {gate['reason']}")
    continue
```

**alphafold_bulk_download.py** — check before each batch of 5000:

```python
gate = convergence_gate("alphafold_structures", convergence_lag_max=50000)
while gate["verdict"] == "WAIT":
    await asyncio.sleep(gate["wait_seconds"])
    gate = convergence_gate("alphafold_structures", convergence_lag_max=50000)
```

---

## Convergence States for Backpressure

sweetGrass `convergence.batch_check` returns per-hash stage completion.
For backpressure, we aggregate into a dataset-level convergence ratio:

```
convergence_ratio = converged_count / total_count
```

| Ratio | Meaning | Pipeline action |
|-------|---------|-----------------|
| > 0.95 | Dataset nearly fully converged | Download next dataset |
| 0.5 - 0.95 | Partial convergence, braiding in progress | Continue, but check warm tier |
| < 0.5 | Large backlog — braiding is behind | Pause downloads, let trio catch up |
| 0.0 | No convergence data — primordial state | Proceed (nothing to backpressure against) |

---

## Relationship to Existing Backpressure

This design layers on top of existing mechanisms:

```
Layer 4 (future):  sweetGrass convergence-aware flow control  ← THIS DESIGN
Layer 3 (deployed): nestGate warm_tier_min_free (10 GB)       ← Storage floor
Layer 2 (deployed): bulk_braid.py STAGE_MIN_FREE_GB (20 GB)  ← Staging gate
Layer 1 (deployed): Manifest rate_limit_mbps, curl limits     ← Network cap
Layer 0 (spec):     topology.bandwidth.budget                 ← Network governance
```

Each layer catches a different failure mode:
- **Layer 0/1**: Network saturation (too fast)
- **Layer 2**: NVMe staging overflow (too much staged)
- **Layer 3**: CAS write rejection (disk critically full)
- **Layer 4**: Provenance backlog (downloading faster than braiding)

The layers are defense-in-depth. Layer 4 (this design) prevents Layer 3
from ever triggering under normal operation. Layer 3 remains as a safety
net for abnormal conditions (e.g., sweetGrass down, DAG corruption).

---

## Prerequisites

1. **sweetGrass updated to upstream origin/main** — needed for
   `convergence.check` and `convergence.batch_check` methods
2. **nestGate `substrate.tiers` RPC** — needed for warm tier free space
   query (alternative: direct `statvfs` in Python, which works now)
3. **`convergence_gate()` module** — add to `prov_inline.py` or create
   a `pipeline_gate.py` utility

### Fallback without upstream sync

If sweetGrass is not yet updated, `convergence_gate()` degrades to
storage-only backpressure using `os.statvfs`:

```python
def convergence_gate_fallback(warm_path="/mnt/cas-hot", min_free_gb=20.0):
    st = os.statvfs(warm_path)
    free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
    if free_gb < 10:
        return {"verdict": "STOP", "reason": f"warm {free_gb:.1f} GB free"}
    if free_gb < min_free_gb:
        return {"verdict": "WAIT", "wait_seconds": 30,
                "reason": f"warm {free_gb:.1f} GB free"}
    return {"verdict": "GO", "reason": "clear"}
```

This is equivalent to the current `STAGE_MIN_FREE_GB` check in
`bulk_braid.py` but standardized as a reusable gate.

---

## Tuning Parameters

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `warm_min_free_gb` | 20 GB | 2× the nestGate floor. Provides buffer for braiding WIP |
| `convergence_lag_max` | 10,000 | ~50 MB of CAS objects at 5 KB avg. Keeps hot tier WIP bounded |
| `batch_size` | 100 | Check every 100 downloads. Amortizes RPC cost |
| `wait_seconds` (WAIT) | 30-60 | Long enough for meaningful drain progress |
| `convergence_lag_max` (AlphaFold) | 50,000 | AlphaFold files are small (~5 KB each), higher lag OK |

These should be configurable per-manifest in the `[manifest.provenance]`
section:

```toml
[manifest.provenance]
convergence_backpressure = true
convergence_lag_max = 10000
warm_min_free_gb = 20
```

---

## Metrics and Observability

When backpressure triggers, log structured events:

```
BACKPRESSURE dataset=alphafold_structures verdict=WAIT reason="convergence lag 12345 > 10000" warm_free_gb=45.2
BACKPRESSURE dataset=alphafold_structures verdict=GO reason="clear" waited_seconds=90
```

These can be aggregated to understand:
- How often backpressure fires (too often = tune thresholds; never = thresholds too loose)
- Average wait time (indicates braiding throughput vs download throughput mismatch)
- Which datasets trigger backpressure (size-dependent tuning)

---

## Future: sweetGrass as Active Flow Controller

The design above is **passive** — download scripts poll convergence state.
The long-term architecture is **active** — sweetGrass pushes backpressure
signals through the mesh:

```
sweetGrass detects convergence lag rising
  → emits trust.event("backpressure", severity="warning")
  → cellMembrane receives event
  → cellMembrane pauses active download compositions
  → convergence lag drops
  → sweetGrass emits trust.event("backpressure", severity="clear")
  → cellMembrane resumes downloads
```

This requires:
- sweetGrass monitoring its own convergence rate (braids/s vs arrivals/s)
- Trust event propagation through cellMembrane
- Composition-level pause/resume (signal graph nodes)

This is the "convergence-aware flow control" referenced in the upgrade
path section of LATENCY_FOLDING_HARDWARE.md.

---

*sweetGrass convergence backpressure design complete. Passive polling
via `convergence_gate()` is implementable now using `os.statvfs` fallback.
Full convergence-aware flow requires upstream sweetGrass sync for
`convergence.check` / `convergence.batch_check`. Layers with existing
nestGate storage backpressure as defense-in-depth.*

---
*FOSSILIZED Wave 157k interstadial (Aug 14, 2026). Content absorbed into ortho/blurb or implemented in code.*
