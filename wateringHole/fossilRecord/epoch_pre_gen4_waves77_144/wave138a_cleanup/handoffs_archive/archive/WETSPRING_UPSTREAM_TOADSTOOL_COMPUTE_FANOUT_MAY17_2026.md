# Upstream Ask: toadStool `compute.fan_out` DAG-Aware Dispatch

**Date:** May 17, 2026 (PM)
**Author:** wetSpring workstream
**Audience:** toadStool team, primalSpring
**Status:** Request — enables distributed clone-level processing
**License:** AGPL-3.0-or-later

---

## Context

wetSpring's sovereign resequencing pipeline currently processes clones
sequentially in a single binary. Each clone is independent: it loads its own
FASTQ reads, maps them against a shared FM-index, generates a pileup, and calls
variants. The pipeline already emits per-clone DAG events and `loamSpine` aglets.

For the Barrick 2009 dataset (7 clones), sequential processing is acceptable.
For Tenaillon 2016 (264 clones, ~200 GB of reads), sequential processing takes
days. The clone-level parallelism is natural — each clone is an independent work
unit that reads from a shared reference and writes independent results.

## The Ask

Add a `compute.fan_out` method to toadStool that accepts a DAG session and a
list of work units, dispatches each to available compute substrate (CPU cores,
GPU, remote nodes), and manages completion callbacks.

### Wire Format (proposed)

```json
{
  "jsonrpc": "2.0",
  "method": "compute.fan_out",
  "params": {
    "dag_session_id": "dag-...",
    "work_units": [
      {
        "id": "REL1164M",
        "accession": "SRR032370",
        "type": "sovereign_resequencing_clone"
      },
      {
        "id": "REL2179M",
        "accession": "SRR032371",
        "type": "sovereign_resequencing_clone"
      }
    ],
    "shared_context": {
      "reference_path": "/path/to/reference.gbk",
      "fm_index_path": "/path/to/fm_index.bin",
      "caller_config": { "min_depth": 3, "min_frequency": 0.8 }
    },
    "on_complete": "dag/event.append + loamspine/aglet"
  },
  "id": 1
}
```

### Expected Behavior

1. toadStool assigns each work unit to available substrate based on current load
   (CPU cores, GPU availability, memory pressure)
2. Each unit's completion triggers:
   - `provenance::record_step` with clone results → `dag / event.append`
   - `loamSpine` aglet commit for the sealed node
   - `partial_dehydrate` if available (see rhizoCrypt upstream ask)
   - `braid.partial_update` signal via biomeOS (see biomeOS upstream ask)
3. toadStool reports aggregate completion status

### Substrate Routing

wetSpring has already established the substrate dispatch pattern:

| Pipeline stage | Optimal substrate | Reason |
|----------------|-------------------|--------|
| Read mapping (seed-extend) | CPU | Short reads (36bp), GPU dispatch overhead exceeds compute |
| Pileup coverage scan | GPU (`Tensor::scan`) | Prefix sum, highly parallel |
| SNP calling | GPU (`SnpCallingF64`) | Column-parallel, batch-efficient |
| FM-index build | CPU | Sequential SA-IS construction |

toadStool should respect these substrate preferences per work-unit stage, or
allow the work unit to self-select (the sovereign binary already handles this
internally via `#[cfg(feature = "gpu")]` dispatch).

## What It Unlocks

- **264-clone parallelism**: Tenaillon 2016 can process multiple clones
  simultaneously across available cores/GPUs
- **Multi-node distribution**: future expansion to processing across networked
  nodes, each sealing results into the shared DAG
- **DAG-aware scheduling**: toadStool can prioritize work units that have
  dependencies or that would complete the DAG session
- **Natural map-reduce**: fan-out for per-clone processing, fan-in via DAG
  dehydrate + braid weave

## Current Workaround

Sequential `for` loop in the sovereign binary. Each clone runs to completion
before the next starts. The pipeline uses CPU for mapping and GPU for
pileup/SNP calling, but cannot process multiple clones simultaneously.

## Degradation Behavior

If toadStool fan-out is unavailable, the sovereign binary continues sequential
processing. This is slower but produces identical results. The DAG events and
aglets are emitted the same way — only the dispatch mechanism changes.

## References

- wetSpring sovereign pipeline: `barracuda/src/bin/validate_sovereign_resequencing.rs`
- toadStool dispatch: `barracuda/src/ipc/` (existing IPC patterns)
- GPU substrate dispatch: `barracuda/src/bio/read_mapper.rs` (hybrid CPU/GPU)
- Existing `neuralSpring` GPU parity: `s_gpu_parity` scenario
