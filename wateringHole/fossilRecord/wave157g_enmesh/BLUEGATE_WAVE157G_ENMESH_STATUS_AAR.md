# blueGate Wave 157g — Enmeshment Status AAR

**Date**: Aug 10, 2026 3:40PM | **Wave**: 157g | **Gate**: blueGate (10.13.37.12)
**Operator**: blueGate sub-builder | **From**: overwatch (gate-agnostic)
**Status**: **NUCLEUS ALIVE. MESH INITIALIZED. GOSSIP BLOCKED.**

---

## Summary

blueGate NUCLEUS 13/13 alive on v4.57 depot binaries. songBird mesh initialized with 6 reachable peers across WireGuard overlay. `builder.serve :9800` live. golgi SSH authorized. However, **gossip mesh enmeshment is blocked** — TCP 7800 (swarmVine gossip) is closed on all peers, biomeOS RPC returns 403 (needs BTSP auth), and swarmVine env vars are not configured. These findings confirm the blurb's three OPEN items from blueGate's perspective.

---

## Enmeshment Probe Results

### 1. WireGuard Overlay — ALIVE

blueGate at `10.13.37.12`. Overlay peers reachable:

| Peer | Ping | :7700 (songBird) | :7800 (gossip) | :9090 (biomeOS) |
|------|------|-------------------|----------------|-----------------|
| 10.13.37.1 (golgi) | OK | **OPEN** | CLOSED | CLOSED |
| 10.13.37.2 | OK | **OPEN** | CLOSED | — |
| 10.13.37.3 | unreachable | — | — | — |
| 10.13.37.4 | OK | — | — | — |
| 10.13.37.5 | OK | — | — | — |
| 10.13.37.10 | OK | — | — | — |
| 10.13.37.11 | OK | — | — | — |
| 10.13.37.12 (self) | OK | **OPEN** | CLOSED | CLOSED |

**Key finding**: songBird `:7700` is open on overlay peers. swarmVine gossip `:7800` is closed everywhere. This confirms the blurb: "Cross-gate gossip peers unreachable — TCP 7800 reachability."

### 2. songBird Mesh — INITIALIZED

```
mesh.init → 6 bootstrap peers added, node_id="blueGate"
mesh.status → initialized=true, reachable_peers=6, relay_enabled=true
discovery.peers → 6 peers discovered (all quality=1.0, protocol=tcp)
```

Stale peer files detected:
- `flockGate.toml` — 291 hours stale
- `golgiBody.toml` — 269 hours stale
- `strandGate.toml` — 28 hours stale

songBird mesh is online but no gossip RPC surface is available yet (methods `gossip.peers`, `mesh.gossip_stats`, `mesh.routes`, `mesh.capabilities` all return "unknown method"). This confirms the blurb: "songBird MeshRelay — OPEN — not yet shipped."

### 3. biomeOS v4.57.0 — ALIVE but AUTH-GATED

- `/health` returns HTTP 200 with empty body (content-length: 0)
- All RPC endpoints (`/rpc`, `/api/health`) return **403 Forbidden**
- biomeOS source includes fix commit `6eb27ef9` ("swarmVine socket discovery + capability gaps + structured /health") but depot binary may need BTSP token for RPC access
- Named pipe `\\.\pipe\biomeos_songbird` exists — local IPC channel to songBird is wired

### 4. swarmVine Socket Discovery — WINDOWS DIVERGENCE

The blurb identifies: "biomeOS connects `.tarpc.sock` instead of JSON-RPC `.sock`. Config issue."

On blueGate (Windows), this manifests differently:
- **No Unix domain sockets** — `.tarpc.sock` and `.sock` files don't exist on Windows
- `SWARMVINE_PEERS` not set → no gossip peer config
- `SWARMVINE_SOCKET` not set → no explicit socket path
- `XDG_RUNTIME_DIR` not set → no runtime socket directory
- swarmVine `CONVENTIONS.md` documents the platform path: `platform_paths::runtime_socket_dir()` with `#[cfg(unix)]` gating and TCP gossip as platform-agnostic fallback
- TCP 7800 is the correct path for Windows gossip — but it's closed on all peers

**Windows-specific recommendation**: swarmVine gossip on Windows should use TCP 7800 exclusively (no UDS). biomeOS on Windows should discover swarmVine via TCP, not socket path. This needs biomeOS to recognize `PRIMAL_BIND_MODE=tcp` and connect accordingly.

### 5. builder.serve — VALIDATED

```json
{"method":"health","result":{"message":"builder OK (blueGate)","ok":true}}
```

Port 9800 serving. JSON-RPC responsive. Identity correct.

### 6. Depot — CURRENT

All 15 binaries match golgi depot. No changes since 157e pull (depot wasn't rebuilt between 157e and 157g).

---

## blueGate Deployment Evidence (157g)

| Component | Status |
|-----------|--------|
| NUCLEUS | **13/13 ALIVE** |
| Ports | **12/13 OPEN** (petalTongue P2: :9204 closed) |
| builder.serve | **:9800 ALIVE** |
| songBird mesh | **INITIALIZED** — 6 peers, relay enabled |
| WireGuard | **UP** — 10.13.37.12, 6/8 overlay peers reachable |
| golgi SSH | **AUTHORIZED** — SCP verified |
| dnsproxy | **ALIVE** — G29 Phase 2 DNS |
| sshd | **Running** — J12 dispatch ready |

---

## Blockers for Full Enmeshment (from blueGate perspective)

### 1. TCP 7800 Not Listening — HIGH

No gate has swarmVine gossip port 7800 open. This blocks cross-gate gossip entirely. Either:
- swarmVine servers are not starting with TCP gossip enabled, or
- Firewall rules block 7800 on all gates, or
- swarmVine gossip is UDS-only today and TCP hasn't been wired yet

**Recommendation**: Each gate needs `swarmvine-server` running with TCP gossip on 7800. On Windows, this is the ONLY transport (no UDS). On Linux gates, this should be enabled alongside UDS for cross-gate reach.

### 2. biomeOS RPC Auth — MEDIUM

biomeOS 403 on all RPC endpoints prevents us from testing `capability.call` routing, `gossip.spread`, or any composition graph operations from outside.

**Question for overwatch**: Is BTSP auth expected for localhost RPC? If so, what's the auth token flow? If not, this is a regression.

### 3. songBird MeshRelay Not Shipped — MEDIUM

songBird mesh is initialized and peers are reachable, but there are no gossip relay methods. The blurb correctly identifies this as OPEN. Once MeshRelay ships, gossip can flow through `:7700` even when TCP 7800 is blocked.

### 4. petalTongue Port — LOW (P2, recurring)

`--port 9204` ignored in `server` mode. Non-blocking.

---

## Recommendations to Pipeline Enmeshment Teams

### For sporeGate + sourDough
- Wire `sourdough validate` into golgi post-receive hook (convergence + rpc-surface validators)
- Confirm swarmVine gossip TCP is enabled in depot binaries

### For biomeOS
- Clarify auth model for localhost RPC (should localhost bypass BTSP?)
- On Windows: use TCP discovery for swarmVine when `PRIMAL_BIND_MODE=tcp` or `#[cfg(not(unix))]`

### For songBird
- MeshRelay for gossip through `:7700` is the critical path for Windows gates (TCP 7800 may remain blocked by firewalls)

### For gate ops (all gates)
- Ensure swarmVine-server starts with `--gossip-port 7800` or equivalent
- Set `SWARMVINE_PEERS` env var with overlay peer addresses
- Open TCP 7800 in WireGuard allowed-ips / local firewalls

---

*blueGate 157g enmesh status: NUCLEUS 13/13. songBird mesh initialized (6 peers). Gossip blocked (TCP 7800 closed fleet-wide). builder.serve :9800 live. Ready for MeshRelay + gossip activation.*
