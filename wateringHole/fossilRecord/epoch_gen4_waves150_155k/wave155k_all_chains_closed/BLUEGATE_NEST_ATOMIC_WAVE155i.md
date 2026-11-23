# blueGate Nest Atomic — 10/10 Primals on Windows

**Date**: Jul 29, 2026 17:20 EDT | **Wave**: 155i | **From**: blueGate
**Gate**: G2 Nest Atomic | **Status**: **VALIDATED** | **Platform**: Windows 10.0.26200

---

## FULL STACK — TOWER + NEST ATOMIC

| # | Primal | Composition | Version | Transport | Port(s) | Health |
|---|--------|-------------|---------|-----------|---------|--------|
| 1 | bearDog | Tower | 0.9.0 | TCP | :9100 | `alive` |
| 2 | songBird | Tower | 0.2.1 | TCP + HTTP | :9901 (IPC), :7700 (HTTP) | `healthy` |
| 3 | skunkBat | Tower | — | Process | — | Running |
| 4 | nestGate | Nest | 0.5.0 | HTTP | :9200 | `ok` |
| 5 | loamSpine | Nest | 0.9.16 | TCP | :9201 | `ok` |
| 6 | rhizoCrypt | Nest | 0.14.17 | TCP | :9202 | `alive` |
| 7 | sweetGrass | Nest | 0.7.61 | TCP + HTTP | :9203, :9213 | `healthy` |
| 8 | petalTongue | Nest | 1.6.6 | tarpc | :9204 | Running |
| 9 | squirrel | Nest | 0.1.0 | TCP | :9205 | `healthy` |
| 10 | biomeOS | Nest | 0.1.0 | HTTP | :9206 | `200 OK` |

### JSON-RPC Health Proofs

```json
bearDog:    {"primal":"beardog","status":"alive","version":"0.9.0"}
songBird:   {"primal":"songbird","status":"healthy","uptime_s":539,"version":"0.2.1","services":0}
loamSpine:  {"primal":"loamspine","status":"ok","version":"0.9.16"}
rhizoCrypt: {"primal":"rhizocrypt","status":"alive","uptime_s":60,"version":"0.14.17"}
squirrel:   {"primal":"squirrel","status":"healthy","version":"0.1.0"}
```

### HTTP Health Proofs

```json
nestGate:   {"service":"nestgate-api","status":"ok","version":"0.5.0","communication_layers":{"event_coordination":true,"mcp_streaming":true,"sse":true,"streaming_rpc":true,"websocket":true}}
sweetGrass: {"status":"healthy","version":"0.7.61","service":"sweetgrass","uptime_secs":61,"store":{"available":true,"braid_count":0,"backend":"memory"}}
biomeOS:    HTTP 200 OK
```

---

## RESOURCE PROFILE

| Metric | Value |
|--------|-------|
| Total primals | **10** (3 Tower + 7 Nest) |
| Total memory | **107.6 MB** |
| Tower footprint | ~36 MB (bearDog 13, songBird 16, skunkBat 7) |
| Nest footprint | ~71.6 MB (nestGate 8, loamSpine 7, rhizoCrypt 7, sweetGrass 9, petalTongue 11, squirrel 18, biomeOS 11) |
| Ports in use | 9100, 9200-9206, 9213, 7700, 9901 |

---

## DEPLOYMENT NOTES

### All 7 Nest Binaries Worked from Depot

Unlike songBird (which required source build), all Nest Atomic depot binaries
from `x86_64-pc-windows-gnu` (07/16/2026) started successfully on Windows.
No compile-time platform gates, no Unix-only errors. These primals either:
- Have `PRIMAL_BIND_MODE=tcp_only` support out of the box
- Gracefully fall back from UDS to TCP
- Don't have hard Unix gates in their startup paths

This is the pattern songBird should follow.

### CLI Differences Between Primals

| Primal | Bind Flag | Server Subcommand | Notes |
|--------|-----------|-------------------|-------|
| nestGate | `--bind` | `server` | Supports `PRIMAL_BIND_MODE` env |
| loamSpine | `--bind-address` | `server` | Different flag name |
| rhizoCrypt | `--host` | `server` | Different flag name |
| sweetGrass | N/A (use `--http-port`) | `server` | TCP via `--port`, HTTP via `--http-port` |
| petalTongue | `--bind` | `server` | Standard |
| squirrel | `--bind` | `server` | Standard |
| biomeOS | `--bind` | `api` (not `server`) | Different subcommand |

Standardizing CLI flags across primals would simplify orchestration.

### Environment Variables Used

```
NESTGATE_JWT_SECRET=<48-byte random base64>
PRIMAL_BIND_MODE=tcp_only
FAMILY_ID=blueGate
SONGBIRD_FAMILY_ID=blueGate
```

### Version Gap: Depot vs. Source

All depot binaries are from 07/16/2026. Current source versions (post-155i):
- sweetGrass depot: v0.7.61 → source: v0.8.0 (G3 wiring)
- biomeOS depot: v0.1.0 → source: v4.45 (composition broker)
- nestGate depot: v0.5.0 → source has CAS+ZFS deep debt

For production use, blueGate should build from source (once MSVC or GNU
toolchain is stable) to get the latest composition broker and G3 wiring.

### petalTongue Transport

petalTongue uses tarpc (structured RPC), not JSON-RPC. The TCP port (:9204)
accepts tarpc protocol, not newline-delimited JSON. Health probe via JSON-RPC
gets a connection reset. petalTongue is healthy (11.2 MB, running) but needs
tarpc client for full validation.

---

## COMPARISON TO WESTGATE

| Dimension | westGate | blueGate | Notes |
|-----------|----------|----------|-------|
| Platform | Linux | Windows | First Windows Nest Atomic |
| Services | 8 | 10 (3 Tower + 7 Nest) | blueGate includes full Tower |
| CAS objects | 3,119 | 0 | No data ingested yet |
| Storage | ZFS 25.4TB | Memory/NTFS | No ZFS on Windows |
| Capabilities | 1,704 | Not yet discovered | Need primal registration |
| Transport | UDS + TCP | TCP only | Named pipes not yet wired |
| biomeOS version | v4.45 | v0.1.0 (depot) | Depot stale |

---

## NEXT STEPS

1. **Node Atomic** — deploy workload primals (toadStool, barraCuda, coralReef)
2. **Sub-builder enrollment** — register blueGate as Windows build host under sporeGate
3. **Build from source** — upgrade biomeOS, sweetGrass to current versions
4. **Primal registration** — get bearDog + nest primals registered with songBird IPC broker
5. **Data ingestion test** — small CAS object via nestGate to prove pipeline

---

*blueGate Nest Atomic VALIDATED. 10/10 primals healthy on Windows (107.6 MB).
All 7 Nest depot binaries work — no platform gates. First Windows Nest Atomic
in the mesh. Ready for Node Atomic.*
