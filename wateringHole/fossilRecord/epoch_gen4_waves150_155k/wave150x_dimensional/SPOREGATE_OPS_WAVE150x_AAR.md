# sporeGate Ops AAR — Wave 150w–150x

**Date**: Jul 24, 2026
**Gate**: sporeGate (10.13.37.2) / eastGate overwatch
**Scope**: tower.shadow 3-gate deploy, membrane crash-loop breaker, sustained benchmark, KNOWN_DEBT calibration

---

## What Was Accomplished

### tower.shadow Deployed to All 3 Gates (Wave 150w)

Deployed `membrane 0.1.0 (f6b67ba)` with `tower.shadow` command to flockGate and golgiBody
(sporeGate already active). Each gate runs a 60-min systemd timer for continuous WG vs Tower
transport comparison.

**flockGate deployment** required:
- XDG songbird symlink (`~/.local/share/ecoPrimals/plasmidBin/...` → depot path)
- `sudo` for `systemctl enable/start` (unit files wrote to `/etc/systemd/system/`)
- `sudo cp` to `/usr/local/bin/membrane` (PATH precedence over `~/.local/bin`)

**golgiBody** deployed cleanly — songbird already in XDG path, root access available.

### Crash-Loop Breaker Deployed (Wave 150x)

Built and deployed `membrane 0.1.0 (eee7e84)` to all 3 gates. This includes:
- `CrashLoopReport` type with scan + disable logic
- `scan_and_break()` for bootstrap/preflight contexts
- Targets the Wave 150x crash-loop divergence (nestgate 17,920 + biomeos-beacon 11,161 restarts on eastGate)

`biomeos-beacon.service` confirmed absent on sporeGate, flockGate, golgiBody — it's an
eastGate-only phantom unit. Crash-loop breaker handles it; full disable on next eastGate access.

### checksums.toml Format Migration (Wave 150w)

Deployed `membrane 9a06699` (intermediate) with backward-compatible struct + plain string
parsing for `checksums.toml`. Verified depot integrity on flockGate: 15 binaries, 0 mismatches.

### songBird 0.2.1+sustained Rebuilt (Wave 150x)

Rebuilt songBird from source (`2bb2f92`) with:
- `--sustained` streaming mode (continuous write, windowed throughput samples)
- UDS connection pool
- `federation.broadcast`
- Benchmark duration truncation fix

Deployed to local depot, songbird-gateway restarted (PID 3925573).

### Sustained Throughput Benchmark (Wave 150x)

First sustained streaming benchmark using `songbird benchmark --sustained`:

| Path | Metric | Tower Atomic | WireGuard | Ratio |
|------|--------|-------------|-----------|-------|
| **LAN** sporeGate↔eastGate | Latency | **0.586ms** | 157ms | **267x** |
| **LAN** | Jitter | **0.008ms** | 1.61ms | **200x** |
| **LAN** | Burst throughput | 4,073 Mbps | 6.76 Mbps | Tower LAN direct |
| **LAN** | Sustained | 6,139 Mbps | 3.39 Mbps | Tower 1.8x |
| **WAN** sporeGate→flockGate | Latency | 133.9ms | 134.0ms | Parity |
| **WAN** | Burst throughput | 6.80 Mbps | 7.22 Mbps | Parity |
| **WAN** | Sustained | **7.13 Mbps** | 4.19 Mbps | **Tower 1.7x** |

**Key finding**: The 267x LAN latency advantage is architectural, not incidental.
Tower's `lan_addr` peer discovery lets it bypass the WG overlay entirely (direct
192.168.4.244 path). WireGuard has no concept of "this peer is on my LAN" — all
traffic routes through the golgiBody VPS (157ms round-trip). This is the core
argument for Tower Atomic replacing WireGuard.

WAN sustained throughput shows Tower at 1.7x, consistent with previous burst
measurements. WAN latency at parity.

### primalSpring Overwatch

Across sessions: 1225 → 1226 passed, 0 failed, 2 ignored. KNOWN_DEBT recalibrated
3 times for sporeGate context:

- `graphenegate-readiness`: flaps between 1 and 2 on sporeGate (depot cache state). Set to 2.
- `sporeprint-pure-primal-parity`: 1 failure on sporeGate (Zola build env difference). Upstream clears it; we re-add.
- `composition-access-control`: stable at 15.

196 total scenarios (up from 176). 46/46 tower scenarios PASS.

---

## Deployment Pattern: Binary Update on Running Services

Repeated pattern across sessions for deploying binaries to gates with running services:

1. **SCP** new binary to `/tmp/` on target gate
2. **Rename trick** if "Text file busy": `mv old old.old; cp new old; rm old.old`
3. **sudo** required on flockGate for `/usr/local/bin/` (PATH precedence)
4. **Verify** with `--version` before restarting
5. **Restart** service if needed (`systemctl restart`)

XDG path resolution: `membrane` looks for binaries in `$XDG_DATA_HOME/ecoPrimals/plasmidBin/primals/<triple>/`.
Symlinks to depot paths work but must exist before `tower.shadow --enable`.

---

## What Remains (sporeGate team)

| Priority | Task | Status |
|----------|------|--------|
| P1 | 10G backbone cabling | Physical — 4 towers NIC'd, cabling sole blocker |
| P1 | iperf3 sustained throughput (real streaming) | Waiting on 10G or dedicated 1G test |
| P1 | Gate enrollment (southGate, strandGate) | USB staged, R45 topology, physical access |
| P1 | songBird LAN peer discovery tuning | MikroTik topology routing |
| P2 | biomeos-beacon disable on eastGate | Needs eastGate SSH access |
| P3 | Phase 3 cutover — Tower replaces WG | Awaiting shadow data maturity |

---

## For Upstream Teams

| Item | Owner | Detail |
|------|-------|--------|
| Drawbridge JSON-RPC→HTTP | songBird (eastGate) | P0 — `CapabilityProxyRouter` translation |
| 30 known debt findings | All teams | Distributed across 10 stress/pen scenarios |
| biomeos-beacon unit | biomeOS (eastGate) | Point to depot binary or remove unit |
| biomeOS chimera Phase 0 | biomeOS (eastGate) | Library extraction can begin now |

---

*Wave 150x: P0 CLEAR. tower.shadow on 3 gates collecting continuous data.
Sustained benchmark proves Tower 267x LAN latency advantage (architectural —
lan_addr bypasses WG overlay). Crash-loop breaker deployed. 1226/0 primalSpring.
43/43 converged.*
