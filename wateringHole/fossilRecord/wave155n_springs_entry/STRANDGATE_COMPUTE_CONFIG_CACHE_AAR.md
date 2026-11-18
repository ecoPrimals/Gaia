# AAR: Compute Provenance — Thermalized Config Caching via Provenance Trio

**Date**: Aug 4, 2026 AM | **Wave**: 155u | **Gate**: strandGate
**Author**: Agent (Cursor) | **Status**: CONCEPT — ready for implementation

---

## Discovery

During 16⁴ GPU production runs, CPU thermalization consumes **37+ minutes
of dead compute** per (lattice_size, β) point before a single GPU measurement
begins. The current code re-thermalizes from scratch every launch — same
dimensions, same β, same seed — pure waste on repeat runs.

The thermalized lattice configuration is a **pure mathematical object**: a
set of 262,144 × 4 SU(3) matrices (≈38 MB at 16⁴) that depends only on
`(dims, β, seed, n_therm, integrator)`. It is deterministic, reproducible,
and hardware-independent.

This is a textbook memoization target — and the provenance trio already
provides the infrastructure.

---

## The Two Sides of Provenance

| Aspect | westGate (Data) | strandGate (Compute) |
|--------|----------------|---------------------|
| **What's stored** | Acquired datasets (AlphaFold, USGS, LINCS) | Thermalized lattice configurations |
| **Content address** | BLAKE3 hash of file bytes | BLAKE3 hash of flattened link array |
| **CAS role** | nestGate CAS on ZFS | nestGate CAS (or local `.lat` cache) |
| **DAG tracking** | `dag.event`: download → hash → ingest | `dag.event`: hot_start → thermalize → hash |
| **Ledger** | `spine.entry`: when/where/who acquired | `spine.entry`: when/where/who thermalized |
| **Attribution** | sweetGrass: dataset → paper | sweetGrass: config → paper/experiment |
| **Consumer** | Springs (tideGlass, groundSpring) query data | GPUs (RTX 3090, RX 6950 XT) load configs |
| **Throughput issue** | 12× collapse with inline provenance (74→6 files/s) | 37 min dead compute per config point |
| **Solution pattern** | Trailer: download fast, braid later | Cache: thermalize once, load forever |

**The provenance trio is abstract of the content type.** rhizoCrypt doesn't
care whether the BLAKE3 hash covers a FASTA file or a lattice configuration.
loamSpine doesn't care whether the "who" is a download script or a CPU HMC
engine. sweetGrass doesn't care whether the attribution links to a drug
repurposing paper or a QCD preprint.

---

## Architecture: Compute Config Cache

### Current Flow (Wasteful)

```
For each (dims, β) GPU production run:
  1. Lattice::hot_start(dims, β, seed)           — instant
  2. for _ in 0..n_therm:                         — 37+ minutes at 16⁴
       hmc::hmc_trajectory(&mut lat, cfg)
  3. GpuHmcState::from_lattice(gpu, &lat, β)     — instant (upload)
  4. GPU production loop                           — actual science
```

### Proposed Flow (Cached)

```
For each (dims, β) GPU production run:
  key = blake3(dims, β, seed, n_therm, integrator_type)
  if config_cache.contains(key):
    lat = config_cache.load(key)                   — instant (<1s)
    log provenance: "loaded cached config {key}"
  else:
    lat = Lattice::hot_start(dims, β, seed)
    for _ in 0..n_therm:
      hmc::hmc_trajectory(&mut lat, cfg)           — 37+ minutes
    config_cache.store(key, &lat)                  — <1s (38 MB at 16⁴)
    commit_provenance(key, dims, β, ...)           — NFT braid
  GpuHmcState::from_lattice(gpu, &lat, β)
  GPU production loop
```

### Hardware Distribution

```
        Dual EPYC 7742 (128 threads)
            ┌──────────┴──────────┐
       NUMA node 0            NUMA node 1
            │                     │
       RTX 3090 (PCIe)      RX 6950 XT (PCIe)
```

**Both GPUs share the same config cache.** A configuration thermalized for
the RTX 3090 run can be loaded by the RX 6950 XT for cross-vendor parity
checks — the math is identical, only the silicon differs.

**Parallel pipeline**: while GPU₁ runs production on config(β=6.0), CPU
thermalizes config(β=6.2) in a background thread. The CPU is idle during
GPU production — this is free compute.

**Multi-seed ensembles**: for statistics, we want independent thermalized
configs at the same (dims, β) but different seeds. Each gets its own cache
entry. Launch both GPUs with different seeds → 2× statistics throughput.

### Storage Budget

| Lattice | Sites | Bytes/config | 10 configs |
|---------|-------|-------------|------------|
| 8⁴ | 4,096 | 2.4 MB | 24 MB |
| 12⁴ | 20,736 | 12 MB | 120 MB |
| 16⁴ | 65,536 | 38 MB | 380 MB |
| 24⁴ | 331,776 | 191 MB | 1.9 GB |
| 32⁴ | 1,048,576 | 603 MB | 6 GB |

Trivial. strandGate has 2 TB NVMe. westGate has 519 GB ZFS. Even at 32⁴
with 50 cached configs, we use 30 GB — pocket change.

---

## Provenance Trio Wiring

### NFT for a Thermalized Config

```json
{
  "braid_type": "compute.thermalized_config",
  "content_hash": "blake3:a7f3...",
  "parameters": {
    "dims": [16, 16, 16, 16],
    "beta": 5.9,
    "seed": 42,
    "n_therm": 200,
    "integrator": "Omelyan2MN",
    "dt": 0.01,
    "n_md_steps": 40
  },
  "hardware": {
    "cpu": "AMD EPYC 7742",
    "gate": "strandGate",
    "threads_used": 1,
    "wall_seconds": 2200
  },
  "dag_events": [
    { "op": "hot_start", "input_hash": "blake3:seed=42" },
    { "op": "thermalize", "n_steps": 200, "output_hash": "blake3:a7f3..." }
  ],
  "spine_entry": {
    "timestamp": "2026-08-04T08:45:00Z",
    "gate": "strandGate",
    "operator": "hotSpring/arxiv_volume_scan"
  }
}
```

### NFT for a Production Run (references config NFT)

```json
{
  "braid_type": "compute.production_run",
  "input_config": "blake3:a7f3...",
  "gpu": "NVIDIA GeForce RTX 3090",
  "results": {
    "plaquette_mean": 0.58154,
    "plaquette_stderr": 1.81e-4,
    "acceptance_rate": 1.0,
    "tau_int": 13.9,
    "n_prod": 1000,
    "ms_per_traj": 611.0
  }
}
```

The **separation of config braid from result braid** mirrors westGate's
separation of dataset acquisition from dataset analysis. The config is the
data; the production run is the fermentation.

---

## Convergence with westGate Data Provenance

| Challenge | westGate Solution | strandGate Analog |
|-----------|------------------|-------------------|
| Inline provenance too slow | Trailer pattern (download fast, braid later) | Cache pattern (thermalize once, load forever) |
| Mixed states (primordial/CAS/braided) | `is_dataset_converged()` gate | `is_config_cached()` gate |
| Batch throughput | `dag.event.batch` + `spine.entry.batch` | Batch config commits (multiple β points) |
| Cross-gate sharing | nestGate CAS federation | Config CAS federation (strandGate ↔ biomeGate) |

The **batch RPC proposal** (`dag.event.batch` + `spine.entry.batch`) from
westGate's throughput divergence would directly benefit compute provenance
too — committing 10 thermalized configs in one RPC instead of 10 sequential
round-trips.

---

## Implementation Priority

1. **Lattice serialization** (P1): `Lattice::save()` / `Lattice::load()`
   using `flatten_links()` → `Vec<f64>` → bytes → BLAKE3 hash. No serde
   derive needed — the flat f64 array IS the canonical format.

2. **Config cache lookup** (P1): before thermalizing, check for
   `~/.hotspring/configs/{hash}.lat`. If found, load + skip thermalization.

3. **Provenance commit** (P2): wire rhizoCrypt `dag.event` + loamSpine
   `spine.entry` on config creation. sweetGrass attribution on paper
   submission.

4. **Parallel thermalization** (P2): `std::thread::spawn` CPU thermalization
   for next β point while GPU runs current production. The EPYC cores are
   idle during GPU production.

5. **Multi-GPU config sharing** (P3): both GPUs load same cached config for
   parity checks, or different-seed configs for independent statistics.

---

## Key Insight

> **The provenance trio is the universal interface between acquisition and
> computation.** westGate acquires data and braids it. strandGate computes
> on that data and braids the results. The same three primals (rhizoCrypt,
> loamSpine, sweetGrass) track both flows. The content type is abstract —
> FASTA files, lattice configurations, plaquette measurements — the
> provenance pattern is invariant.

This is the compute-side complement to westGate's PROVENANCE × ACQUISITION
work. Together they form the complete provenance lifecycle:

```
Acquire (westGate) → Braid (trio) → Compute (strandGate) → Braid (trio) → Publish (sweetGrass)
```

Every step is content-addressed, append-only, and independently verifiable.

---

*strandGate Wave 155u. Compute config caching via provenance trio. 37-minute
CPU thermalization bottleneck at 16⁴ eliminated on repeat runs. Same trio
pattern as westGate data acquisition — complementary and abstract of each
other. Config = braid, production = fermentation. Implementation path clear:
Lattice serialize → cache lookup → provenance commit → parallel therm.*
