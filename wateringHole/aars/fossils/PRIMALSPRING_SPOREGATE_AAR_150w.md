# primalSpring sporeGate AAR — Wave 150w

**Date**: July 23, 2026 | **Wave**: 150w | **From**: sporeGate (10.13.37.2)
**Scope**: Phase 2 shadow deploy — operator actions, benchmark verification, CI hook deployment

---

## What Happened

sporeGate team executed Phase 2 operator tasks from the Wave 150w blurb. Ran
Tower vs WG benchmarks to verify Phase 1 PASS from our endpoint. Deployed
sovereign CI hook to golgiBody. Set MEMBRANE_BUILD_AUTHORITY. Discovered
`membrane tower.shadow` doesn't exist yet — filed blocker.

### Benchmark Verification — Phase 1 PASS Confirmed

Ran `songbird benchmark` (shipped 150v) on both paths from sporeGate:

| Path | Latency (Tower/WG) | Throughput (Tower/WG) | Verdict |
|------|--------------------|-----------------------|---------|
| → eastGate (.5, hub path) | 1.006x | 0.997x | **PARITY** |
| → flockGate (.6, WAN) | 0.993x | **1.98x** | **TOWER EXCEEDS** |

Tower matches WG on the hub path and **doubles WG throughput on WAN** with
lower jitter (0.42ms vs 0.50ms). Phase 1 PASS confirmed from sporeGate side.

**Note**: sporeGate↔eastGate traffic routes through golgiBody hub (84ms RTT),
not direct LAN. Sub-1ms LAN benchmark requires direct peering or 10G cabling.

### Operator Actions

| # | Task | Status |
|---|------|--------|
| 1 | `MEMBRANE_BUILD_AUTHORITY=1` | **DONE** — systemd override installed at `songbird-gateway.service.d/build-authority.conf`. Pending service restart. |
| 2 | `golgi-post-receive-ci.sh` to golgiBody | **DONE** — deployed `30-sovereign-ci` hook to 43 repos across 4 orgs (ecoprimals, protokarya, sporegarden, syntheticchemistry). Correct path: `/opt/forgejo/data/repositories/`. |
| 3 | `benchScale/tower_shadow/` | **DONE** — directory created, 4 benchmark JSON results filed. |
| 4 | WG production verification | **DONE** — golgiBody 37.5ms, git.primals.eco 200, live.primals.eco 200, footprint.primals.eco 200. |
| 5 | `membrane tower.shadow --enable` | **BLOCKED** — command does not exist in cellMembrane v0.1.0. |

### Blocker: `membrane tower.shadow`

cellMembrane v0.1.0 has no `tower` namespace. The `ShadowMode` enum in
`cellmembrane-types` is for telemetry shadow validation, not Tower transport
duplication. eastGate needs to ship this command to enable continuous shadow
metrics collection across the mesh.

Until it ships, manual benchmarks via `songbird benchmark` serve as point-in-time
measurements (done above).

---

## Artifacts

| Artifact | Location |
|----------|----------|
| Full handoff | `handoffs/PRIMALSPRING_WAVE150w_SHADOW_DEPLOY_SPOREGATE.md` |
| This AAR | `aars/PRIMALSPRING_SPOREGATE_AAR_150w.md` |
| Benchmark: Tower → eastGate | `benchScale/tower_shadow/tower_eastgate_20260723_100715.json` |
| Benchmark: WG → eastGate | `benchScale/tower_shadow/wg_eastgate_20260723_100730.json` |
| Benchmark: Tower → flockGate | `benchScale/tower_shadow/tower_flockgate_20260723_100746.json` |
| Benchmark: WG → flockGate | `benchScale/tower_shadow/wg_flockgate_20260723_100803.json` |

---

## Next Actions

| Action | Owner | Priority |
|--------|-------|----------|
| Ship `membrane tower.shadow` command | eastGate cellMembrane | **P0** |
| Restart songbird-gateway (activate BUILD_AUTHORITY) | sporeGate operator | **P1** |
| Direct LAN peering (bypass golgiBody hub) | operator | **P2** |
| 6 exploration scenarios | primalSpring teams | **P1** |

---

**Filed by**: sporeGate + golgiBody team
**Convergence**: No primalSpring code modified. Operator actions + benchmarks only.
