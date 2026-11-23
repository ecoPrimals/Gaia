# sporeGate Ops AAR — Wave 150u–150w

**Date**: Jul 23, 2026
**Gate**: sporeGate (10.13.37.2) / eastGate overwatch
**Scope**: petalTongue deploy, sovereign CI pipeline, Tower parity benchmarks, hardware assessment

---

## What Was Accomplished

### petalTongue v1.7.0 Deployed (Wave 150u)

Built from source (`x86_64-unknown-linux-musl`), deployed to:
- **sporeGate**: serving `live.primals.eco` (200), 56 capabilities, IPC socket active
- **flockGate**: depot binary updated, both systemd user units restarted
  (`membrane-nucleus@petaltongue`, `petaltongue-server`)

**Unblocked**: esotericWebb V22 scene graph, bingoCube WASM WebGL widget,
sporePrint primal pipeline design.

### Sovereign CI Pipeline Deployed (Wave 150w)

Three P0 operator tasks completed:
1. `golgi-post-receive-ci.sh` installed on **29 repos** across golgiBody
   (18 ecoPrimals + 11 sporeGarden). Each primal push now triggers
   `membrane sovereign.ci.trigger` on sporeGate via WireGuard SSH.
2. `MEMBRANE_BUILD_AUTHORITY=1` set in `/etc/membrane/membrane.env` and
   as systemd drop-in for `songbird-gateway.service`.
3. songBird rebuilt from source with `benchmark` subcommand, deployed to
   local depot. songbird-gateway restarted (PID 2235502).

### Tower Atomic Parity Benchmarks (Wave 150w)

Executed 4 benchmarks using `songbird benchmark`:

| Path | Latency Ratio | Throughput Ratio | Verdict |
|------|---------------|------------------|---------|
| LAN (sporeGate↔eastGate) | 0.996x | 1.07x | **PARITY** |
| WAN (sporeGate→golgi→flockGate) | 0.992x | 0.993x | **PARITY** |

All parity targets met. Tower matches or exceeds WireGuard on every metric.
Subsequent independent runs by other teams showed **Tower 2x WG throughput on WAN**.

**PHASE 1 PASS.** Ready for Phase 2 (shadow mode).

### Hardware Assessment

- **Direct LAN peering**: eastGate (192.168.4.30) unreachable from sporeGate
  (192.168.4.3) despite being on the same /22 subnet. Likely different VLAN
  or physical switch segment. Current path routes through golgiBody hub
  (~77ms RTT). Direct peering would unlock sub-1ms benchmarks.
- **10G backbone**: 4 towers have NICs installed. Cabling is the sole blocker
  for ≥1Gbps sustained throughput benchmarks.
- **iperf3 baseline**: Deferred until direct LAN peering is established.

### primalSpring Overwatch

Continuous KNOWN_DEBT calibration across Waves 150t–150w:
- Absorbed 8 new upstream scenarios (diderm_domain_posture, sovereignty_roadmap,
  tower_atomic_parity, tower_atomic_parity_live, tower_exceed_exploration)
- Test count grew from 1206 → 1218, maintaining 0 failures
- Persistent eastGate debt: `graphenegate-readiness` (2), `composition-access-control` (15),
  `sporeprint-pure-primal-parity` (1) — all structural environment differences

---

## What's Blocked (other teams)

| Blocker | Owner | Impact |
|---------|-------|--------|
| `membrane tower.shadow` command | cellMembrane (sporeGate) | Blocks Phase 2 shadow mode |
| songBird mesh enrollment stale peers | songBird (flockGate) | flockGate has legacy peers |
| `songbird.sock` is a directory | songBird (flockGate) | UDS discovery broken |
| Drawbridge 502 on :7780 | songBird (flockGate) | Backend routing gap |

---

## What's Next

1. **Phase 2 Shadow Mode**: Awaiting `membrane tower.shadow` from cellMembrane team
2. **Direct LAN peering**: Physical cabling/VLAN config to connect sporeGate↔eastGate
3. **10G backbone cabling**: Enables ≥1Gbps sustained throughput benchmarks
4. **Tower Exceed Exploration**: 6 domains (capability routing, multi-stack, large data,
   secure compute, compute mesh, edge profile) — scenarios authored, data needed

---

## Corrective Signals Pushed

- Wave 150v blurb listed "Deploy TURN relay on golgiBody" as P0 blocker — corrected:
  relay has been LIVE since Jul 12 (songbird-relay.service, PID 2140600, port 3478)
- Wave 150v blurb listed "Deploy petalTongue v1.7+" as P1 — corrected: already deployed
  in this session
