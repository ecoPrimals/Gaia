# flockGate Wave 150w–150x AAR — Tower Shadow + songBird P0s + Convergence

**Date**: 2026-07-24 | **Gate**: flockGate | **Wave**: 150w–150x
**From**: primalSpring overwatch on eastGate

---

## Summary

Waves 150w–150x delivered Tower Atomic Phase 1 PASS, songBird P0 fixes,
capability routing proof-of-life, and convergence on a crash-loop divergence.
flockGate served as the WAN-edge validation node for shadow benchmarks and
the primary code team for songBird transport primals.

## Deliverables

### 1. songBird P0 Fixes (Wave 150w)

Rebuilt songBird from source (`cfa84a2`) with 3 P0 fixes:
- **`mesh.prune_stale`** — RPC to evict stale peers from enrollment
- **Socket dir guard** — prevents `songbird.sock` being created as directory
- **Drawbridge diagnostics** — root-caused 502 (CapabilityProxyRouter can't proxy HTTP→JSON-RPC)

Result: Mesh 4/4 peers reachable via UDS, all direct paths confirmed.

### 2. Capability Routing — PROVEN LIVE (Domain 1/6)

`capability.call` via `songbird.sock` routes to correct providers across mesh.
Verified via socat UDS query — responses confirm routing resolution.
Domain 1 of 6 exploration scenarios now PROVEN LIVE (others structural GREEN).

### 3. Tower Shadow — 324 Results

`membrane tower.shadow` active at 60-minute intervals. Benchmarks cover all
5 WG peers (golgi, ironGate, northGate, southGate, sporeGate). Shadow data
confirms Tower exceeds WG:
- **WAN**: 2x throughput (7.19 vs 3.64 Mbps multi-hop)
- **LAN**: 8% lower latency, 33% less jitter
- **Hub-routed**: Parity

### 4. petalTongue v1.7 Stability

Deployed Wave 150n, now 2+ days stable. esotericWebb auto-discovers via UDS.
Scene graph pipeline active (11 scenes, 8 abilities, 6 NPCs). No restarts needed.

### 5. esotericWebb V22 — 4-Day Uptime

Stable since Wave 150o fix (stale nohup elimination). No incidents.
Scene binding + GET handler fully operational on WAN.

### 6. primalSpring — 196 Scenarios, 1226 Tests

Integrated 6 Tower exploration scenarios + 14 Tower hardening scenarios from
upstream. All pass with flockGate-specific known debt calibration:
- `graphenegate-readiness: 14` (no aarch64 depot)
- `composition-access-control: 15` (structural)
- `arch-fitness: 1` (no aarch64 depot)
- `mesh-reachability: 1` (ironGate DOWN, 388ms > 150ms)

## Known Issues

| Issue | Impact | Owner |
|-------|--------|-------|
| songBird HTTP→UDS bridge returns "IPC unavailable" | Non-blocking (UDS works directly) | songBird team |
| ironGate DOWN (388ms RTT) | mesh-reachability 1 known failure | topology (sporeGate) |
| Drawbridge JSON-RPC→HTTP translation | P1 — needs code change | eastGate |
| 30 Tower hardening findings | Distributed across teams | all |

## Runtime State

| Service | Unit | Uptime | Port |
|---------|------|--------|------|
| esotericWebb V22 | `esotericwebb-server.service` | 4 days | 8090 |
| petalTongue v1.7 | `petaltongue-server.service` | 2 days | 9100 + UDS |
| songBird 0.2.1 | ad-hoc (PID-managed) | on-demand | 7700/7780 + UDS |
| tower.shadow | systemd timer (membrane) | continuous | — |

## Observations

### Stash/Merge Flow for KNOWN_DEBT

Each upstream pull introduces eastGate/sporeGate-calibrated KNOWN_DEBT that
must be recalibrated for flockGate's environment. This is a recurring pattern:
- eastGate sees 1-2 failures for `graphenegate-readiness` (partial depot)
- flockGate sees 14 (no aarch64 at all)
- `sporeprint-pure-primal-parity` passes cleanly on flockGate but fails on sporeGate

The stash-pop-resolve workflow handles this cleanly but requires attention
on every cascade.

### Tower Exceeds WG — Architectural Advantage

The 2x WAN throughput is structural, not incidental. Tower's userspace TCP
with JSON-RPC dispatch avoids kernel-crossing overhead that WG pays per packet.
On LAN with small payloads, WG's kernel path still wins raw throughput (6.6 vs
3.8 Gbps at 196KB). This gap closes with larger payloads and 10G backbone.

## Posture

**GREEN.** P0 CLEAR. 196 scenarios all pass. 324 shadow results collected.
4 services stable. WAN surfaces healthy. Ready for Phase 2 shadow → Phase 3 cutover.

---

*Filed by flockGate overwatch. Waves 150w–150x.*
