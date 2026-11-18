# sporeGate Topology & Ops AAR — Wave 150x

**Date:** 2026-07-24
**Wave:** 150x
**Author:** sporeGate (cellMembrane + topology)
**Posture:** LAN PEER DISCOVERY PROVEN. MESH OPERATIONAL. CRASH-LOOP BREAKER CLEAR.

---

## Context

Wave 150x blurb (Jul 24 08:37 EDT) assigned sporeGate four P1 topology tasks:
sustained throughput benchmarking, biomeos-beacon fix, songBird LAN peer
discovery, and gate enrollment. P0 was CLEAR.

---

## Deliverables

### 1. Sustained LAN Benchmark (P1 #1)

Ran 100-probe LAN benchmarks (sporeGate → eastGate at 192.168.4.244) via
`songbird benchmark`. Key finding: **Tower has 9.7x less jitter than WG on LAN**.

| Metric | Tower Atomic | WireGuard | Verdict |
|--------|-------------|-----------|---------|
| Latency avg | 0.602ms | 0.654ms | Tower 8% faster |
| Latency p99 | 0.839ms | 1.229ms | Tower 32% tighter tail |
| Jitter | **0.006ms** | **0.056ms** | **Tower 9.7x less** |
| Max latency | 0.912ms | 5.874ms | Tower 6.4x better worst case |
| Setup avg | 0.202ms | 0.252ms | Tower 20% faster |

Throughput metric is burst-based (196KB payloads), not sustained streaming.
iperf3 streaming requires an iperf3 server on eastGate (no SSH access from
sporeGate). Left as follow-up for physical coordination.

### 2. LAN vs WG Overlay — The 253x Gap (P1 #4)

**Critical finding**: WireGuard routes sporeGate↔eastGate traffic through
golgiBody VPS (154ms round-trip), even though both gates are on the same
MikroTik LAN (0.17ms ping). Tower Atomic with `lan_addr` discovery bypasses
the VPS entirely.

| Path | Latency | Throughput |
|------|---------|------------|
| Tower → LAN direct (192.168.4.244) | **0.61ms** | 3893 Mbps |
| WG → LAN direct (192.168.4.244) | 0.60ms | 3469 Mbps |
| WG → overlay (10.13.37.5 via VPS) | **154.5ms** | 6.8 Mbps |

**Tower LAN is 253x faster than WG overlay** — because Tower discovers
LAN peers via `lan_addr` and routes directly. WG has no concept of LAN
topology and always tunnels through the configured endpoint (golgiBody VPS).

When both modes use the LAN IP directly, latency is at parity (~0.6ms)
and Tower has 12% higher burst throughput. The structural advantage is
Tower's **topology awareness**, not raw protocol speed.

### 3. biomeos-beacon Service Unit (P1 #3)

The crash-looping `biomeos-beacon` service (11,161 restarts on eastGate)
was already stopped by the crash-loop breaker shipped in 150x. Verified:

- No `biomeos-beacon` unit exists on sporeGate, golgiBody, or flockGate
- `membrane gate.crash-loop --dry-run` → 14 services scanned, 0 crash-loops
- Actual binary fix owned by biomeOS team (flockGate)

### 4. songBird Mesh Operational Fixes

Discovered and fixed multiple issues preventing mesh auto-initialization:

| Issue | Fix |
|-------|-----|
| `songbird` CLI was a stub script (`echo songbird`) | Symlinked to real depot binary |
| Service used `SONGBIRD_MESH_PEERS` (wrong name) | Changed to `SONGBIRD_PEERS` (code reads this) |
| `spawn_mesh_seed` not triggering on startup | Added `ExecStartPost` drop-in with retry loop |
| `peers.toml` unreachable by root service | Copied to `/root/.local/share/songbird/` |
| `SONGBIRD_NODE_ID` not set | Added to service unit env |

Deployed fresh songBird binary (Jul 24 build, 26.8MB musl static) to depot.

---

## Changed Files / Config

| File / Config | Change |
|---------------|--------|
| `~/.local/bin/songbird` | Stub → symlink to depot binary |
| `/etc/systemd/system/songbird-gateway.service` | `SONGBIRD_PEERS`, `SONGBIRD_OVERLAY_PEERS`, `SONGBIRD_NODE_ID`, `HOME` env vars |
| `/etc/systemd/system/songbird-gateway.service.d/mesh-init.conf` | **NEW** — `ExecStartPost` mesh auto-init with retry loop |
| `/usr/local/bin/songbird-mesh-init.sh` | **NEW** — mesh init script (3 peers + overlay) |
| `/root/.local/share/songbird/peers.toml` | **NEW** — copy of user peers.toml for root service |
| `~/.local/share/ecoPrimals/plasmidBin/.../songbird` | Updated to Jul 24 build |
| `wateringHole/heads/sporeGate.toml` | Updated to 150x posture |
| `primalSpring/benchScale/tower_shadow/` | 8 new benchmark JSON files (LAN direct + overlay) |

---

## Current State

| System | Status |
|--------|--------|
| Tower Atomic | 3/3 LIVE (songBird, bearDog, skunkBat) |
| Mesh | 3 peers reachable (eastGate, golgiBody, flockGate), relay on |
| Shadow Timer | ACTIVE — 130+ results, 60min cycle |
| Crash-Loop Breaker | OPERATIONAL — 14 services, 0 loops |
| primalSpring | 1226+ passed, 46/46 tower scenarios, GREEN |

---

## For Upstream Teams

| Item | Owner | Action |
|------|-------|--------|
| `spawn_mesh_seed` auto-seed regression | songBird (flockGate) | Startup flow doesn't call mesh seed on `songbird server` — investigate |
| `biomeos-beacon` binary | biomeOS (flockGate) | Build beacon binary or remove service unit template |
| iperf3 sustained streaming | topology (sporeGate) | Needs iperf3 server on eastGate — physical coordination |
| SSH key for eastGate | topology (sporeGate) | Would enable remote iperf3 + deployment |
