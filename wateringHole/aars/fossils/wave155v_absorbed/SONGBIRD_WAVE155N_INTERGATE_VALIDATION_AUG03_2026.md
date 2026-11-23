# songBird — Wave 155n Handoff: Inter-gate Mesh Validation

**Date**: Aug 3, 2026 | **Wave**: 155n | **From**: eastGate overwatch
**Commits**: `ddaec109` (feat), `e44c7c6c` (debt), `90466648` (TCP fix)

---

## What Was Delivered

### 1. `mesh.connectivity_check` (new JSON-RPC method)

Active E2E inter-gate validation of all mesh peers:
- TCP connect + riboCipher MITO handshake per peer
- Bidirectional `health.ping` JSON-RPC with RTT measurement
- Cross-gate path classification (local/direct/overlay/tor/relay)
- Per-peer report: reachability, riboCipher acceptance, latency, version
- Summary: total reachable, cross-gate peer list, partition detection

**Usage**: `{"method": "mesh.connectivity_check", "params": {"timeout_ms": 5000}}`

### 2. `mesh.throughput` (new JSON-RPC method)

Sustained TCP bandwidth test for validating 10G LAN capacity:
- Configurable payload (64K–256M, default 1 MiB)
- Nagle-disabled streaming for max throughput
- Reports: MB/s achieved, bytes transferred, elapsed time
- `meets_10g_threshold` boolean (true if ≥800 MB/s)

**Usage**: `{"method": "mesh.throughput", "params": {"target_address": "10.13.37.2:7700", "payload_bytes": 104857600}}`

### 3. TCP Registration Fix (from Wave 155i, pushed same session)

Root cause: TCP IPC handler created isolated `ServiceRegistry` — registrations
via TCP (blueGate) were invisible to HTTP queries (`services: 0`). Fixed by
wiring `shared_ipc_handler` from `stage_2_start_servers` through TCP path.

### 4. Deep Debt Cleanup

- Deprecated `DEFAULT_BIND_ADDRESS` removed (zero consumers)
- `constants::legacy` module removed (zero imports)
- `serde_yaml_ng` hoisted to workspace deps
- PID file paths evolved to platform-aware
- riboCipher probe noise reduced (error→debug)
- Windows cross-compile warnings fixed

---

## What This Unblocks

| Item | How |
|------|-----|
| **P1 #4: Inter-gate content.get E2E** | `mesh.connectivity_check` verifies all peers reachable with riboCipher. `mesh.throughput` confirms link bandwidth meets 10G threshold. nestGate/biomeOS can invoke before live CAS transfers. |
| **P3 #13: mitoBeacon acceptance** | `mesh.connectivity_check` reports `ribocipher_accepted` per-peer — provides validation data for mitoBeacon probing across NUCLEUS. |
| **blueGate services: 0** | TCP registration now uses shared registry — primals registering via TCP visible to all query paths. |

---

## songBird Current State

| Metric | Value |
|--------|-------|
| Mesh methods | **20** (was 18) |
| Tests | **14,840+** |
| Clippy | **31/31 clean** (`-D warnings`) |
| Windows | **Clean** (`x86_64-pc-windows-gnu`) |
| Files >800L | **0** |
| Production mocks | **0** |
| TODO/FIXME | **0** |
| Unsafe | **0** |

---

## For Upstream Teams

### nestGate
Before running live inter-gate `content.get`, invoke:
1. `mesh.connectivity_check` on songBird — verify all target gates reachable
2. `mesh.throughput` to target gate — confirm ≥800 MB/s for streaming transfers

### biomeOS
Signal graphs can invoke `mesh.connectivity_check` as a health gate before
composition transitions that depend on cross-gate data access.

### bearDog
TCP IPC registration is now functional — `ipc.register` + `ipc.list` share
the same registry on all transport paths (UDS, HTTP, TCP).

---

*songBird GREEN. 20 mesh methods. 14,840+ tests. Zero debt markers. Inter-gate
validation tooling shipped — ready for live content.get E2E testing.*
