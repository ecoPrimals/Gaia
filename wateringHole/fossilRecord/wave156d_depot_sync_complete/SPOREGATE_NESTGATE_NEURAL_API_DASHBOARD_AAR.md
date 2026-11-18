# AAR: nestgate.io Neural API Bridge + Tower Atomic Dashboard

**Date**: Aug 5, 2026 | **Gate**: sporeGate | **Wave**: 156d
**Scope**: nestgate.io dashboard wiring, Tower Atomic architecture view, golgi Caddy cleanup

---

## What Worked

### Neural API Bridge (P0 — dashboard was non-functional)

- **Root cause identified**: petalTongue's `NeuralApiProvider::discover()` searches `socket_search_dirs()` (e.g., `/run/user/1000/`) for `biomeos-neural-api-{family_id}.sock`. The socket only existed at `/run/membrane/neural-api-e8b62b6e.sock` — different directory, invisible to discovery.
- **Fix**: Symlinked `/run/membrane/neural-api-e8b62b6e.sock` → `/run/user/1000/biomeos-neural-api-e8b62b6e.sock`. Added `DISCOVERY_SOCKET` and `FAMILY_ID` env vars to `petaltongue-web.service`.
- **Persistence**: Updated `membrane-nestgate.service.d/uds-socket.conf` `ExecStartPost` to create both the content-provider and Neural API symlinks on service start.
- **Result**: petalTongue discovers 20 primals via Neural API. Dashboard went from "Loading..." to live capability maps.

### Tower Atomic Architecture Dashboard

- Restructured the flat "Discovered Primals" dump into layered architecture view:
  - **Tower Atomic — Security** (bearDog): crypto identity, BLAKE3, BTSP auth
  - **Tower Atomic — Transport** (songBird): mesh routing, LAN-first TCP, drawbridge
  - **Tower Atomic — Defense** (skunkBat): threat detection, protocol negotiation
  - **Data Layer**: nestGate (96 caps), rhizoCrypt, loamSpine, sweetGrass
  - **Compute Layer**: barraCuda (99 caps), coralReef, toadStool
  - **Composition & Intelligence**: Neural API (330 caps), biomeOS, squirrel, petalTongue

- Three-state primal indicators:
  - **Full primal** (card with namespace distribution) — complete capability set on this gate
  - **Via routing** (blue pill) — reachable through Neural API routing stubs
  - **Not discovered** (yellow pill) — not registered with Neural API

### Neural API Routing Table

- **Capability → Primal Routes**: shows exact routing (`compute.dispatch.submit` → barracuda, `inference.complete` → squirrel, `dag.partial_dehydrate` → rhizocrypt)
- **Namespace Distribution**: bar chart showing capability density (stats: 49, storage: 36, content: 34, dag: 28, coord: 26)

### Data Braids (CAS Surface) Section

- Local CAS status query (content backend connection)
- Federation topology: westGate 452 GB CAS → ironGate 12.7 TB CAS via `content.replicate.pull`
- Documents blocker: westGate needs nestGate TCP + content capability registration

### golgi Caddy Cleanup

- Migrated deprecated `basicauth` → `basic_auth`
- Removed 10 redundant `header_up X-Forwarded-For/Proto` directives (Caddy sets these by default)
- Formatted Caddyfile, clean reload

### webb.primals.eco 502 Diagnosis

- GET returns 200 (11,768 bytes HTML). HEAD returns 502.
- Root cause: esotericWebb HTTP handler doesn't implement HEAD method properly.
- Not a golgi routing issue — Caddy reverse proxy to `10.13.37.7:8090` works correctly for GET.

---

## What Diverges

| ID | Issue | Owner | Status |
|----|-------|-------|--------|
| NG-01 | Gate mesh topology shows "Not Found" / 0 enrolled | petalTongue web mode | `mesh.peers` query not wired into HTTP API responses for gate table |
| NG-02 | Discovery service registration returns EOF | biomeOS / biomeos-api | `biomeos-api-e8b62b6e.sock` may require BTSP handshake. Non-blocking (standalone mode works) |
| NG-03 | All primals show "unknown" health | Neural API | `primal.list` response doesn't include health status (need `health.liveness` RPC per primal) |
| NG-04 | bearDog not in routing stubs | bearDog / Neural API | bearDog doesn't register a capability routing stub with the Neural API |
| NG-05 | westGate CAS braids not yet federated | westGate team | westGate needs nestGate TCP exposure + songBird content capability registration |
| NG-06 | webb.primals.eco HEAD returns 502 | esotericWebb (upstream) | HTTP handler missing HEAD method support |
| NG-07 | Binary deploy race — `cp` fails silently when process holds file | sporeGate ops | Need atomic swap pattern: stop service → rm → cp → start. Or use `install` command. |

---

## Evolution Path

### Phase 1: Gate Mesh Data (sporeGate — next)
Wire `mesh.peers` songBird query results into petalTongue's `/api/gate-mesh` endpoint. The songBird socket is at `/run/membrane/songbird.sock` and responds to `mesh.peers` RPC (confirmed: 6 online peers, 4 local, 2 overlay). This will populate the gate table and WG overlay visualization.

### Phase 2: Health Liveness (upstream)
Each primal exposes `health.liveness` via UDS. petalTongue could query each discovered primal's health and replace "unknown" with actual status. Requires iterating `primal.list` sockets and sending liveness checks.

### Phase 3: CAS Content Browse (federation blocker)
Once westGate exposes nestGate TCP and registers `content` capability with songBird:
1. ironGate's `content.replicate.pull` can sync CAS objects
2. nestgate.io can query CAS via content backend (already wired on sporeGate via UDS)
3. Dashboard "Data Braids" section can show live CAS stats, namespace counts, object lists

### Phase 4: Live Topology Graph
Replace static topology descriptions with a live force-directed graph built from:
- Neural API primal list (nodes)
- Capability routing stubs (edges)
- songBird mesh peers (transport links)
- Health liveness (node color)

---

## Files Changed

| File | Change |
|------|--------|
| `petalTongue/web/index.html` | Dashboard restructured: Tower Atomic layers, Neural API Routing table, Namespace Distribution chart, Data Braids section |
| `~/.config/systemd/user/petaltongue-web.service` | Added `DISCOVERY_SOCKET` and `FAMILY_ID` env vars |
| `/etc/systemd/system/membrane-nestgate.service.d/uds-socket.conf` (sporeGate) | `ExecStartPost` updated to create both content-provider and Neural API symlinks |
| `/etc/membrane/Caddyfile` (golgi) | `basicauth` → `basic_auth`, removed redundant `header_up`, formatted |
| `wateringHole/handoffs/ECOSYSTEM_BLURB.md` | Updated to Wave 156d Signal Dispatch + Federation Era posture |

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| nestgate.io primal count | 0 | **20** |
| nestgate.io capability edges | 0 | **1** (songbird → neural security-provider) |
| Dashboard sections functional | 3/12 | **8/12** |
| Neural API heartbeat | Failing (attempt 40+, 1920s backoff) | **Connected, 20 primals** |
| Caddy deprecated directives | 2 (`basicauth`) | **0** |
| Caddy redundant headers | 10 | **0** |
| petalTongue binary deploys this session | 3 | 3 (1 failed due to race) |

---

*Signal Dispatch + Federation Era. nestgate.io evolved from a static "Loading..." dashboard to a live Tower Atomic architecture view with 20 primals, capability routing table, and namespace distribution. Data Braids section documents the federation path to westGate CAS exposure. golgi Caddy cleaned. Next: wire mesh.peers for gate table, then CAS content browse once federation unblocks.*
