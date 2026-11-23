# AAR: Bandwidth Saturation Incident — Data Federation Campaign

**Date**: Aug 3, 2026 ~08:15 EDT | **Wave**: 155f | **Gate**: westGate
**Operator**: Claude (overwatch data federation session)
**Scope**: Network saturation from unmetered parallel downloads during 14 TB data federation campaign
**Severity**: P0 — loss of internet connectivity for all devices on the LAN

---

## Executive Summary

During the data federation campaign, the agent launched 6+ parallel
downloads from multiple servers (NCBI, UniProt, EBI, Maayanlab, STRING-DB)
simultaneously with no bandwidth cap. Combined throughput exceeded 1 Gbps
sustained on the residential fiber ingress, saturating the connection and
starving all other devices on the home network. The user lost internet
access on all devices and had to hard-reboot westGate to restore
connectivity. The ZFS pool required manual re-import after the reboot.

This is an architectural failure, not a configuration oversight.

---

## Timeline

| Time (approx) | Event |
|----------------|-------|
| 07:30 | Agent begins parallel download batch: NCBI NR (200 GB), UniRef100 (63 GB), STRING v12 (200 GB), ARCHS4 (87 GB), RNAcentral (15 GB), AlphaFold bulk (214M structures) |
| 07:45 | All downloads running simultaneously at maximum speed via `curl` and `rsync` with no `--limit-rate` or `--bwlimit` |
| 08:00 | Combined throughput saturates 1 Gbps fiber ingress |
| 08:10 | User reports all other devices on the network have lost internet access |
| 08:15 | User hard-reboots westGate to restore connectivity |
| 08:20 | ZFS pool `nestgate` requires manual `sudo zpool import nestgate` |
| 08:30 | Agent implements reactive fixes: `metered_download.sh` with `--limit-rate 50M`, reduces AlphaFold bulk concurrency from 200 to 20 |

---

## Root Cause Analysis

### Immediate Cause

Six independent download processes launched in parallel, each running at
maximum available bandwidth. With a 1 Gbps fiber connection shared by the
entire household, the aggregate demand exceeded the connection capacity,
causing router-level congestion, packet loss, and effective denial of
service for all other devices.

### Systemic Cause

1. **No primal-level bandwidth awareness**: Downloads happen via ad-hoc
   shell scripts (`curl`, `rsync`, `aiohttp`) outside the primal
   composition system. No primal knows how much bandwidth is being
   consumed or available.

2. **No topology awareness**: The agent treated westGate as if it had
   dedicated infrastructure. In reality, westGate shares a 1 Gbps
   residential fiber connection with family streaming, work devices,
   phones, and other systems.

3. **Optimization for speed over stability**: The agent's goal was to
   download 14 TB as fast as possible. Without architectural constraints,
   "as fast as possible" means "use everything available."

4. **No backpressure mechanism**: Nothing in the ecosystem can signal
   "slow down" when network resources are exhausted. The download scripts
   have no feedback loop from the network state.

### Contributing Factors

- `--limit-rate` / `--bwlimit` were not used on any download
- `aiohttp` concurrency was set to 200 with 250 connector limit
- Multiple `rsync` processes ran without `--bwlimit`
- No sequential queue — all downloads ran in parallel

---

## Impact

| Category | Impact |
|----------|--------|
| **Network** | Complete loss of internet for all devices on the LAN (~15 min) |
| **Storage** | ZFS pool unmounted; required manual import after reboot |
| **Data** | Partial downloads; some progress lost (curl/rsync resume on restart) |
| **Trust** | User confidence in agentic data operations reduced |
| **Operational** | Hard reboot of westGate (production gate with 13 NUCLEUS primals) |

---

## Reactive Fixes Applied

1. **Killed all rogue download processes** immediately after reboot
2. **Created `metered_download.sh`** — sequential downloads with
   `curl --limit-rate 50M` (400 Mbps, ~40% of pipe)
3. **Reduced AlphaFold bulk downloader** concurrency from 200→20,
   connector limit from 250→30
4. **Added `rsync --bwlimit=50000`** to AlphaFold proteome sync
5. **Re-imported ZFS pool** via `sudo zpool import nestgate`

These are band-aids. The real fix is architectural.

---

## Architectural Requirements (for sporeGate topology team)

### The Principle

**No single operation, composition, or agent action should be able to
monopolize shared infrastructure.** This applies to network bandwidth,
disk I/O, CPU, and any other shared resource. It is the same principle
as ZFS I/O scheduling or Linux cgroups, applied to the mesh network.

### What Needs to Exist

1. **Ingress/Egress Budget**: A gate-level configuration declaring total
   available bandwidth and the fraction reserved for data acquisition.

   ```toml
   # Example: westGate network profile
   [network]
   ingress_capacity_mbps = 1000    # 1 Gbps fiber
   egress_capacity_mbps = 1000
   lan_capacity_mbps = 10000       # 10 Gbps mesh
   
   [network.budgets]
   data_acquisition_pct = 50       # max 500 Mbps for downloads
   federation_pct = 30             # max 300 Mbps for gate-to-gate
   reserved_pct = 20               # always available for other devices
   ```

2. **Per-Operation Caps**: No single `content.fetch` stream exceeds a
   configured maximum (e.g., 200 Mbps).

3. **Aggregate Enforcement**: Total bandwidth across all concurrent
   data operations stays within the `data_acquisition` budget.

4. **Backpressure Signaling**: When bandwidth pressure is detected
   (latency spikes, packet loss, or budget exhaustion), compositions
   receive a signal to throttle or pause.

5. **Topology Awareness**: The bandwidth governance system knows about
   other consumers on the network — not by monitoring their traffic, but
   by reserving headroom (the `reserved_pct`).

### Proposed Interface (cellMembrane topology extension)

```
topology.bandwidth.budget    → { ingress: {capacity, allocated, available}, egress: {...} }
topology.bandwidth.request   → request N Mbps; returns granted amount (may be less)
topology.bandwidth.release   → release a previously granted allocation
topology.bandwidth.pressure  → signal that the network is under pressure
```

These compose with the existing `coord.topology` (gate/connection mesh
state) and `cellMembrane topology.*` CLI commands. They add the resource
dimension: not just "who is connected" but "what capacity is available."

### The Federated Bandwidth Principle

The same mechanism that prevents westGate from starving the home network
also prevents a consumer gate from starving westGate when pulling data:

- southGate calls `nest.sync(remote_gate=westGate)` to pull AlphaFold
- westGate's bandwidth governance checks budget before serving `content.replicate`
- If westGate is also downloading from EBI, it throttles inter-gate
  transfer to stay within its aggregate budget
- southGate's governance does the same on its ingress side

No gate can starve another. No operation can starve a gate. The mesh
self-regulates.

---

## LAN Evolution Considerations

As more gates come online (southGate, eastGate, ironGate on LAN), the
10 Gbps mesh must also have bandwidth governance:

- Inter-gate replication should not saturate the LAN switch
- A `nest.sync` pulling 15 TB of AlphaFold should not prevent other
  gates from communicating
- The `site_topology: "triangle_3hub"` config in `ecosystem_manifest.toml`
  should inform bandwidth allocation (hub ports get more budget)
- sporeGate as `cascade_hub` needs to be able to throttle cascade
  federation to prevent thundering herd on LAN during depot rebuilds

---

## What Overwatch Should Absorb

1. **Bandwidth governance is a primal capability, not a shell flag.**
   `--limit-rate` on curl is a workaround. The real solution is
   `topology.bandwidth.request` before any data transfer begins.

2. **Downloads must happen inside compositions, not outside them.**
   Shell scripts writing to ZFS with provenance bolted on afterward
   bypass every safety mechanism the ecosystem provides.

3. **Agent actions need resource awareness.** An agentic session that
   launches parallel downloads needs to check available bandwidth the
   same way it would check available disk space before writing.

4. **The 50/30/20 budget split is a starting point.** Real values should
   be tunable per gate based on its role and network position. A
   dedicated data gate might use 80/10/10; a shared-network gate like
   westGate needs the conservative split.

5. **ZFS auto-import worked.** Despite the hard reboot, the ZFS pool
   came back cleanly after manual import. The persistence hardening
   (cachefile, auto-import service) proved its value — the data survived
   the incident intact.

---

*westGate bandwidth saturation AAR complete. sporeGate topology team:
please incorporate bandwidth governance into LAN evolution work. The
interface contract (`topology.bandwidth.*`) and budget model are
specified above. This is a prerequisite for safe agentic data federation
at scale.*
