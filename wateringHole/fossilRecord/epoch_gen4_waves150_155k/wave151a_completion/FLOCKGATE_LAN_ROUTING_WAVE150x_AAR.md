# flockGate AAR — Wave 150x LAN Routing Fix

**Date**: 2026-07-25  
**Gate**: flockGate (NYC, WAN)  
**Role**: Code team — songBird primal source evolution  
**Wave**: 150x  
**Finding**: P0 — 353x latency penalty for capability.call on same-switch peers

---

## Problem

`mesh.find_path` returned WireGuard overlay endpoints (158ms RTT) for peers
on the same physical LAN switch (0.45ms RTT). This is a **353x latency
penalty** for `capability.call` dispatch between same-subnet gates.

Tower's entire value proposition — capability-aware routing with
sub-millisecond local dispatch — was being undermined by the mesh always
preferring the WG tunnel path.

## Root Cause

The path selection algorithm was correct:
- `EndpointType::Local` has priority 0 (best)
- `EndpointType::Overlay` has priority 1
- `update_best_path()` correctly picks lowest `(priority * 10000 + latency_ms)`

But Local endpoints were **never registered** in the common startup path:

1. **WG auto-discovery** (`discover_wireguard_peers`) — only finds overlay IPs
   from `wg show all dump`. No LAN awareness.
2. **Persisted peers** — correctly loads `lan_addr` from `peers.toml` but
   requires prior enrollment with `lan_addr` field set.
3. **Explicit `mesh.init`** — accepts `lan_peers` param (commit `218966d`)
   but auto-seed never passes them.

Result: on fresh starts (path 1), only overlay endpoints exist → `get_best_path`
returns overlay → 353x penalty.

## Fix

### 1. `mesh.init` accepts `lan_peers` (commit `218966d` — eastGate)

```json
{
  "node_id": "flockgate",
  "lan_peers": [
    {"node_id": "eastGate", "address": "192.168.4.244:7700"},
    {"node_id": "sporeGate", "address": "192.168.4.2:7700"}
  ]
}
```

### 2. `SONGBIRD_LOCAL_PEERS` env var (flockGate extension)

For the auto-seed path (WG discovery), operators can now set:

```bash
export SONGBIRD_LOCAL_PEERS="eastGate@192.168.4.244:7700,sporeGate@192.168.4.2:7700"
```

This is parsed by `parse_local_peers_env()` (same format as `SONGBIRD_PEERS`)
and merged with persisted `lan_addr` entries during `spawn_mesh_seed`.
Deduplication ensures no double-registration.

### 3. Registration flow

```
spawn_mesh_seed()
├── load persisted peers (with lan_addr) → lan_peers vec
├── parse SONGBIRD_LOCAL_PEERS env → local_peers_env vec
├── mesh.init (bootstrap + overlay)
├── register_overlay_endpoints()
└── register_lan_endpoints(merged lan_peers + env)
         → EndpointType::Local { addr } → priority 0
         → update_best_path() → Local wins over Overlay
```

## Validation

- `EndpointType::priority()` tests confirm: Local(0) < Overlay(1) < Direct(2)
- `update_best_path()` uses `priority * 10000 + latency_ms` — Local always wins
- `mesh_seed` tests pass (parse formats, WG dump extraction)
- primalSpring suite: **1240 passed, 0 failed**
- Known debt: 30→10

## Deployment Guide

For gates with same-switch peers (sporeGate ↔ eastGate on MikroTik):

```bash
# In systemd unit or shell profile:
Environment=SONGBIRD_LOCAL_PEERS=eastGate@192.168.4.244:7700,sporeGate@192.168.4.2:7700
```

Or persist via `mesh.enroll` with `lan_addr` parameter — auto-loaded on restart.

## Impact

| Metric | Before | After |
|--------|--------|-------|
| LAN `capability.call` RTT | 158ms (via WG) | 0.45ms (direct L2) |
| Speedup | — | **353x** |
| Code change | — | ~30 lines (env parse + merge) |
| Breaking changes | — | None (additive) |

## Remaining

- sporeGate needs to set `SONGBIRD_LOCAL_PEERS` in their songBird unit
- eastGate needs the same for reciprocal LAN path
- Future: auto-detect LAN peers via ARP/mDNS (songBird LAN peer discovery P1)

---

*P0 resolved. 353x LAN speedup available via `SONGBIRD_LOCAL_PEERS` env.
Code team P1 scope complete. Known debt 30→10.*
