# primalSpring Wave 150w — sporeGate Phase 2 Shadow Deploy Status

**Date**: 2026-07-23 | **Wave**: 150w | **Gate**: sporeGate (10.13.37.2)
**Role**: Build authority, benchmark driver
**Phase**: 2 — Shadow Deploy

---

## Operator Actions Completed

| # | Task | Status | Detail |
|---|------|--------|--------|
| 1 | `MEMBRANE_BUILD_AUTHORITY=1` | **DONE** | systemd override at `songbird-gateway.service.d/build-authority.conf` |
| 2 | `golgi-post-receive-ci.sh` to golgiBody | **DONE** | 43 repos × 4 orgs (`hooks/post-receive.d/30-sovereign-ci`) |
| 3 | `benchScale/tower_shadow/` metrics dir | **DONE** | Created, 4 benchmark results filed |
| 4 | WG production traffic verified | **DONE** | golgiBody 37.5ms, all 3 surfaces 200 OK |
| 5 | `membrane tower.shadow --enable` | **BLOCKED** | Command not yet in cellMembrane v0.1.0 — see below |

---

## Phase 1 Verification — Benchmark Results from sporeGate

### sporeGate → eastGate (via golgiBody hub, not direct LAN)

| Metric | Tower Atomic | WireGuard | Ratio |
|--------|-------------|-----------|-------|
| Latency p50 | 154.2ms | 153.3ms | **1.006x** |
| Latency p95 | 156.9ms | 154.7ms | 1.014x |
| Latency p99 | 160.9ms | 157.0ms | 1.025x |
| Jitter | 0.24ms | 0.18ms | 1.36x |
| Setup avg | 77.8ms | 76.4ms | 1.018x |
| Throughput | 6.76 Mbps | 6.78 Mbps | **0.997x** |

**Verdict**: Tower ≈ WireGuard on this path. Latency within 1.03x, throughput within 0.3%.

### sporeGate → flockGate (WAN, 2-hop through golgiBody)

| Metric | Tower Atomic | WireGuard | Ratio |
|--------|-------------|-----------|-------|
| Latency p50 | 135.8ms | 136.7ms | **0.993x** (Tower FASTER) |
| Latency p95 | 145.6ms | 145.8ms | 0.999x |
| Latency p99 | 148.9ms | 151.1ms | **0.986x** (Tower FASTER) |
| Jitter | 0.42ms | 0.50ms | **0.83x** (Tower SMOOTHER) |
| Setup avg | 66.8ms | 66.9ms | 0.999x |
| Throughput | 7.19 Mbps | 3.64 Mbps | **1.98x** (Tower 2x FASTER) |

**Verdict**: Tower exceeds WireGuard on WAN. 2x throughput, lower jitter, marginally better latency.

### Summary

| Path | Latency | Throughput | Setup | Parity |
|------|---------|------------|-------|--------|
| eastGate (hub) | 1.006x | 0.997x | 1.018x | **PASS** |
| flockGate (WAN) | 0.993x | **1.98x** | 0.999x | **EXCEEDS** |

**Note**: Both paths route through golgiBody hub (84ms / 68ms RTT). Direct LAN benchmark
(sub-1ms) requires sporeGate↔eastGate to be directly peered (not through golgiBody).

---

## Blocker: `membrane tower.shadow --enable`

cellMembrane v0.1.0 does not have the `tower.shadow` subcommand. Current membrane
knows: repo, mirror, service, gate, temporal, manifest, identity, impulse, potential,
context, plasmid, relay, webhook, caddy, forgejo. No tower namespace.

cellMembrane's `ShadowMode` enum (`cellmembrane-types/config/mod.rs`) exists for
telemetry shadow validation — NOT Tower transport shadow mode. The convergence brief's
`membrane tower.shadow --enable` requires new code in cellMembrane.

**For eastGate**: Ship `tower.shadow` command in cellMembrane that:
1. Configures songBird to duplicate inter-gate RPC on both WG and Tower paths
2. Collects latency/throughput/jitter metrics per gate pair
3. Exports to `benchScale/tower_shadow/` in JSON format per convergence brief spec

Until this ships, we can run manual benchmarks via `songbird benchmark` (done above).

---

## Infrastructure Deployed

### MEMBRANE_BUILD_AUTHORITY=1

```
/etc/systemd/system/songbird-gateway.service.d/build-authority.conf
[Service]
Environment=MEMBRANE_BUILD_AUTHORITY=1
```

Requires `sudo systemctl restart songbird-gateway` to activate. Deferred restart
to avoid disrupting live services during shadow deploy window.

### Sovereign CI Hook — golgiBody

Deployed `30-sovereign-ci` post-receive hook to all 43 Forgejo repos across 4 orgs
(ecoprimals, protokarya, sporegarden, syntheticchemistry). On push, triggers
`membrane plasmid.pipeline` on sporeGate (10.13.37.2) via SSH.

### Benchmark Results

4 benchmark JSON files in `benchScale/tower_shadow/`:
- `tower_eastgate_20260723_100715.json`
- `wg_eastgate_20260723_100730.json`
- `tower_flockgate_20260723_100746.json`
- `wg_flockgate_20260723_100803.json`

---

## Next Actions

| Action | Owner | Priority |
|--------|-------|----------|
| Ship `membrane tower.shadow` command | eastGate cellMembrane | **P0** |
| Restart songbird-gateway (activate BUILD_AUTHORITY) | sporeGate operator | **P1** — coordinate with active sessions |
| Direct LAN peering (sporeGate↔eastGate bypass golgiBody) | operator | **P2** — unlocks sub-1ms LAN benchmark |
| Exploration scenarios (6 domains) | primalSpring teams | **P1** — per convergence brief |

---

**Filed by**: sporeGate + golgiBody team (Wave 150w)
**Convergence**: No primalSpring code modified. Operator actions + benchmarks only.
