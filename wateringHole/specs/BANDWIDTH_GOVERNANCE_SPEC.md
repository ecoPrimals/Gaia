# Bandwidth Governance Specification

**Status**: Design spec for sporeGate topology team
**Wave**: 155f | **Date**: Aug 3, 2026
**Owner**: cellMembrane (sporeGate team)
**Motivation**: Bandwidth saturation incident — see `aars/WESTGATE_BANDWIDTH_SATURATION_AAR.md`

---

## Principle

No single operation, composition, or agent action may monopolize shared
network infrastructure. Bandwidth is a finite resource that must be
budgeted, requested, and released — the same way ZFS manages I/O or
Linux cgroups manage CPU.

---

## Gate Network Profile

Extend `ecosystem_manifest.toml` gate profiles with a `[network]` section:

```toml
[gates.westGate.network]
ingress_capacity_mbps = 1000      # Physical uplink capacity (ISP fiber)
egress_capacity_mbps = 1000
lan_capacity_mbps = 10000         # Local mesh capacity

[gates.westGate.network.budgets]
data_acquisition_pct = 50         # Max 500 Mbps for external downloads
federation_pct = 30               # Max 300 Mbps for gate-to-gate traffic
reserved_pct = 20                 # Always available for non-mesh consumers

[gates.westGate.network.limits]
per_operation_max_mbps = 200      # No single stream exceeds this
max_concurrent_streams = 10       # Max parallel data operations
backpressure_latency_ms = 100     # Trigger backpressure when RTT exceeds this
```

The `link_speed_mbps` field already exists in gate profiles. The new
`[network]` section adds budget semantics on top of the raw link speed.

---

## RPC Interface

Four new methods in the `topology` domain. These run on whichever primal
owns topology at runtime — currently cellMembrane for CLI dispatch,
potentially nestGate's `coord.topology` for UDS dispatch.

### `topology.bandwidth.budget`

Returns current bandwidth state for this gate.

**Request**: `{}`

**Response**:
```json
{
  "ingress": {
    "capacity_mbps": 1000,
    "budget_mbps": 500,
    "allocated_mbps": 350,
    "available_mbps": 150,
    "active_streams": 3
  },
  "egress": {
    "capacity_mbps": 1000,
    "budget_mbps": 300,
    "allocated_mbps": 0,
    "available_mbps": 300,
    "active_streams": 0
  },
  "lan": {
    "capacity_mbps": 10000,
    "budget_mbps": 7000,
    "allocated_mbps": 0,
    "available_mbps": 7000,
    "active_streams": 0
  }
}
```

### `topology.bandwidth.request`

Request bandwidth allocation for a data operation. Returns the granted
amount, which may be less than requested if budget is exhausted.

**Request**:
```json
{
  "requested_mbps": 200,
  "direction": "ingress",
  "operation": "content.fetch",
  "dataset": "alphafold_structures_v6",
  "estimated_duration_s": 3600
}
```

**Response**:
```json
{
  "granted_mbps": 150,
  "lease_id": "bw-lease-abc123",
  "expires_at": "2026-08-03T12:00:00Z",
  "reason": "budget_partial"
}
```

Possible `reason` values:
- `granted` — full request satisfied
- `budget_partial` — partial allocation (budget constrained)
- `denied` — no budget available, caller should queue
- `per_op_capped` — capped by `per_operation_max_mbps`

### `topology.bandwidth.release`

Release a previously granted allocation.

**Request**:
```json
{
  "lease_id": "bw-lease-abc123",
  "bytes_transferred": 1073741824
}
```

**Response**:
```json
{
  "released_mbps": 150,
  "available_mbps": 300
}
```

### `topology.bandwidth.pressure`

Signal that the network is under pressure. Can be triggered by:
- External monitoring detecting latency spikes
- Router SNMP traps
- Manual operator intervention
- Automated health probes

**Request**:
```json
{
  "severity": "warning",
  "source": "health_probe",
  "latency_ms": 250,
  "packet_loss_pct": 2.5,
  "message": "RTT to 8.8.8.8 exceeded 200ms"
}
```

**Response**:
```json
{
  "action": "throttle",
  "active_leases_throttled": 3,
  "new_budget_mbps": 250
}
```

Severity levels:
- `info` — log only, no action
- `warning` — reduce budgets by 50%
- `critical` — pause all non-essential data operations
- `emergency` — kill all data streams immediately

---

## Backpressure Flow

```
1. nest.acquire_file signal dispatched
2. check_bandwidth node calls topology.bandwidth.request(200 Mbps, ingress)
3. If denied → signal queues, retries after backoff
4. If granted → proceed with content.fetch at granted rate
5. On completion → release_bandwidth calls topology.bandwidth.release
6. If pressure signal arrives mid-transfer → rate is dynamically reduced
```

The `nest_acquire_file.toml` signal graph already includes `check_bandwidth`
and `release_bandwidth` nodes (Phase 2 deliverable). The runtime
implementation is what this spec defines.

---

## State Management

Bandwidth leases are held in-memory by the governance service. On gate
restart, all leases are cleared (operations resume via DAG session
frontier tracking, not lease persistence).

Lease expiry prevents orphaned allocations: if an operation dies without
releasing, the lease expires after `estimated_duration_s` + grace period.

---

## Implementation Options

### Option A: cellMembrane CLI (immediate, no new Rust service)

Add `topology.bandwidth.*` subcommands to `membrane-shadow`. State is
managed in a TOML/JSON file under `/run/membrane/bandwidth_state.json`.
Scripts query this via `membrane topology.bandwidth.budget` before
starting downloads.

Pros: No new service, works today.
Cons: No real-time enforcement, relies on scripts cooperating.

### Option B: nestGate extension (medium-term)

Add `topology.bandwidth.*` methods to nestGate's coordinator module
alongside `coord.topology`. State is in-memory in the nestGate process.
`content.fetch` (Phase 4) queries it internally before starting transfers.

Pros: Real enforcement, integrated with CAS pipeline.
Cons: Requires Rust changes to nestGate.

### Option C: Dedicated bandwidth governance service (long-term)

A new lightweight service (or a sporeGate primal if one is created)
that owns all bandwidth state. All data-moving primals query it.

Pros: Clean separation, works across all primals.
Cons: New service to maintain.

**Recommended**: Start with Option A for immediate protection, evolve to
Option B when `content.fetch` is implemented in Phase 4.

---

## Federated Bandwidth

When a remote gate requests data via `nest.sync`:

1. Remote gate's governance checks its ingress budget
2. Local gate's governance checks its egress budget
3. Transfer proceeds at `min(remote_ingress_grant, local_egress_grant)`
4. Both gates hold leases for the duration

This prevents any gate from being overwhelmed by `content.replicate.pull`
requests, whether from LAN peers or WAN mesh nodes.

---

## Integration with DataManifest

The `[manifest.acquisition]` section specifies `rate_limit_mbps` and
`concurrency`. These are hints to the governance system:

- `rate_limit_mbps` → used as the `requested_mbps` in bandwidth.request
- `concurrency` → max_concurrent_streams for this manifest
- The governance system may grant less than the manifest requests

This means manifests declare intent, but the gate's bandwidth governance
has final authority. A manifest requesting 400 Mbps on a gate with only
150 Mbps available will get 150 Mbps.

---

## Immediate Tactical Fix (until governance is implemented)

The `metered_download.sh` script and `alphafold_bulk_download.py` use
hardcoded rate limits. These should be replaced with governance queries
as each phase lands:

| Phase | Script | Current | After governance |
|-------|--------|---------|------------------|
| Now | `metered_download.sh` | `curl --limit-rate 50M` | `topology.bandwidth.request` → apply granted rate |
| Now | `alphafold_bulk_download.py` | `CONCURRENCY = 20` | Query budget, adjust concurrency dynamically |
| Phase 4 | `content.fetch` | N/A (new) | Built-in governance from day one |
| Phase 5 | Signal composition | N/A (new) | `check_bandwidth` / `release_bandwidth` nodes |

---

*Bandwidth governance spec complete. sporeGate topology team: implement
Option A (cellMembrane CLI) immediately for tactical protection, then
evolve to Option B (nestGate integration) with content.fetch in Phase 4.*
