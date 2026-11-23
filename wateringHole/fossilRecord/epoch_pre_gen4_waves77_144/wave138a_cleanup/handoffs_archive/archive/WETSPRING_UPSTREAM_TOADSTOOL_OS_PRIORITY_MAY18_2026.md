# wetSpring → toadStool: OS-Level Priority Dispatch

**Date:** May 18, 2026
**Author:** wetSpring workstream (southGate)
**Audience:** toadStool team, biomeOS team
**Status:** Proposal — derived from live production observation
**License:** AGPL-3.0-or-later

---

## Context

During a live sovereign resequencing run (Barrick 2009, 7.5M reads per clone),
a parallel biomeOS compilation needed compute bandwidth on the same machine.
We manually deprioritized the science run:

```bash
renice 19 -p $PID        # CPU: lowest scheduling priority
ionice -c 3 -p $PID      # I/O: idle class — only runs when disk is free
```

The science run continued at reduced throughput while the compilation ran at
full speed. When compilation finished, the science run automatically reclaimed
all resources with zero intervention.

This is exactly what toadStool's compute dispatch should control
programmatically from within the ecosystem.

---

## Proposal: `compute.priority` and `storage.priority` Dispatch Parameters

### New Dispatch Fields

```rust
pub struct DispatchHints {
    /// CPU scheduling priority. Maps to `nice` on Linux.
    /// Range: -20 (highest) to 19 (lowest). Default: 0.
    pub compute_priority: i8,

    /// I/O scheduling class. Maps to `ionice` on Linux.
    /// Idle = background science, BestEffort = normal, Realtime = latency-critical.
    pub storage_class: IoClass,

    /// Optional cgroup resource envelope name.
    /// When set, the workload runs inside the named cgroup with memory/CPU/IO limits.
    pub resource_envelope: Option<String>,
}

pub enum IoClass {
    /// Only gets I/O when nothing else wants it. Science background runs.
    Idle,
    /// Normal priority with 8 sub-levels (0=highest).
    BestEffort(u8),
    /// Guaranteed I/O access. Latency-critical paths (e.g., live sequencing).
    Realtime(u8),
}
```

### Kernel Facility Mapping

| toadStool Parameter | Linux | macOS | Windows |
|---------------------|-------|-------|---------|
| `compute_priority` | `nice` / `sched_setattr` | `setpriority` | `SetPriorityClass` |
| `storage_class` | `ionice` / `ioprio_set` | N/A (no equivalent) | `SetFileInformationByHandle` |
| `resource_envelope` | cgroups v2 (`cpu.max`, `memory.max`, `io.max`) | N/A | Job Objects |

### Integration with Existing Dispatch

toadStool already routes work across CPU/GPU/NPU substrates. Priority dispatch
adds a second dimension: not just *where* to run, but *how assertively* to
claim the substrate.

```
                    ┌─────────────────────────────────┐
                    │       toadStool Dispatch         │
                    ├────────────┬────────────────────┤
                    │ Substrate  │ Priority            │
                    │ (where)    │ (how assertively)   │
                    ├────────────┼────────────────────┤
                    │ CPU        │ nice + ionice        │
                    │ GPU        │ wgpu queue priority  │
                    │ NPU        │ DMA channel priority │
                    │ Distributed│ cgroup per node      │
                    └────────────┴────────────────────┘
```

---

## Use Cases from wetSpring Production

### 1. Background Science (Current)

Long-running resequencing pipelines should yield to interactive work:

```rust
toadstool::dispatch(WorkUnit::clone_pipeline(clone), DispatchHints {
    compute_priority: 19,   // lowest CPU priority
    storage_class: IoClass::Idle,
    resource_envelope: Some("wetspring-science".into()),
});
```

### 2. Deadline Escalation

When a deliverable approaches (e.g., interview braid delivery), escalate:

```rust
toadstool::escalate(&work_unit_id, DispatchHints {
    compute_priority: -5,    // above normal
    storage_class: IoClass::BestEffort(2),
    resource_envelope: None,  // remove limits
});
```

### 3. Shared Machine Coexistence

Multiple primals on the same machine (wetSpring science + biomeOS compilation +
petalTongue visualization):

```rust
// Science: background
toadstool::dispatch(science_work, DispatchHints {
    compute_priority: 15,
    storage_class: IoClass::Idle,
    ..default()
});

// Compilation: normal
toadstool::dispatch(build_work, DispatchHints {
    compute_priority: 0,
    storage_class: IoClass::BestEffort(4),
    ..default()
});

// Visualization: interactive
toadstool::dispatch(viz_work, DispatchHints {
    compute_priority: -10,
    storage_class: IoClass::BestEffort(0),
    ..default()
});
```

### 4. GPU + CPU I/O Coexistence

GPU workloads are compute-bound (no disk), CPU mapping is I/O-bound (reading
FASTQs). They can coexist without contention when I/O priority is managed:

```rust
// GPU SNP calling: high compute, no I/O
toadstool::dispatch(gpu_snp, DispatchHints {
    compute_priority: 0,
    storage_class: IoClass::Idle,  // doesn't use disk anyway
    ..default()
});

// CPU FASTQ mapping: moderate compute, heavy I/O
toadstool::dispatch(cpu_mapping, DispatchHints {
    compute_priority: 10,
    storage_class: IoClass::BestEffort(3),
    ..default()
});
```

---

## cgroups v2 Resource Envelopes

For NUCLEUS deployments, cgroups v2 provides the full resource boundary:

```ini
# /sys/fs/cgroup/wetspring-science/
cpu.max = 300000 100000      # 3 cores max
memory.max = 4G               # 4 GB memory limit
io.max = 259:0 rbps=100000000 # 100 MB/s read limit on NVMe
```

toadStool's `resource_envelope` parameter would reference a named cgroup
configuration. biomeOS could manage cgroup lifecycle (create on
`nest.instantiate`, destroy on `nest.teardown`).

---

## Architecture Considerations

### Zero-Cost Hints

`nice` and `ionice` add no runtime overhead — they only change the kernel's
scheduling decisions. This means priority dispatch is free to apply and free
to change at any time.

### Cross-Architecture

Not all facilities exist on all platforms (macOS lacks `ionice`, Windows uses
different APIs). toadStool should degrade gracefully: if `ionice` is unavailable,
skip it. The dispatch still works — it just loses one dimension of control.
This follows the primal degradation pattern: capability enrichment, not
dependency.

### Observability

Priority state should be visible in the DAG:

```json
{
  "step": "dispatch",
  "compute_priority": 19,
  "storage_class": "idle",
  "resource_envelope": "wetspring-science",
  "reason": "biomeOS compilation in progress"
}
```

This gives provenance over *why* a run was slow — the answer is in the DAG,
not in someone's memory.

---

## Request

1. Add `DispatchHints` to `toadStool::dispatch` with `compute_priority`,
   `storage_class`, and `resource_envelope` fields
2. Implement Linux backend via `nice`/`ionice`/`cgroups` syscalls
3. Degrade gracefully on platforms without full support
4. Expose `escalate` / `deprioritize` for dynamic priority changes mid-run
5. Coordinate with biomeOS for cgroup lifecycle management in NUCLEUS deployments
