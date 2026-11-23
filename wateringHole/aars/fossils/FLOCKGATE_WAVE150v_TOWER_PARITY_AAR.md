# AAR: flockGate Tower Atomic Parity — Wave 150v

**Date**: Jul 22, 2026
**Filed by**: flockGate team
**For**: eastGate overwatch (primalSpring code team + songBird ops)
**Priority**: P2 — WAN peer validated, benchmark blocked on upstream ops

---

## Situation

Wave 150v spun up flockGate as the **WAN peer** for Tower Atomic parity
benchmarking. Goal: validate Tower stack locally, establish WG baseline,
and stand ready to receive benchmark probes from sporeGate through
golgiBody TURN relay.

Convergence rule observed: no code changes to primalSpring. Report only.

---

## What We Did

1. Full dimensional audit of primalSpring codebase on flockGate
2. Verified Tower Atomic primals (bearDog, songBird, skunkBat) running
3. Confirmed WireGuard mesh connectivity to golgiBody and sporeGate
4. Ran structural validation scenarios (tower_atomic, flockgate_tower_wan)
5. Measured WG baseline RTT for parity comparison
6. Confirmed esotericWebb V22 + petalTongue healthy with no conflicts
7. Filed handoff with full findings

---

## What Went Right

- **Tower Atomic stack stable**: All 3 primals running since Jul 16 (6 days),
  no restarts needed. Deployed from plasmidBin depot binaries.
- **Mesh solid**: WG interface UP, golgiBody at 31ms, sporeGate at 66ms.
  Clean routing via 10.13.37.0/24 subnet.
- **primalSpring codebase quality high**: Zero TODO/FIXME/unsafe, 1,214 tests,
  73.8% line coverage. Architecture fully compliant with wateringHole standards.
- **Convergence works**: `git pull` brought us to `a515d8d` (main HEAD), matching
  eastGate latest. No drift.
- **Coexistence proven**: esotericWebb V22, petalTongue, visualization — all running
  alongside Tower Atomic without port/socket conflicts.

---

## What Went Wrong / Gaps

| Issue | Severity | Owner | Notes |
|-------|----------|-------|-------|
| `cargo fmt` regression in Wave 150t commit | Low | eastGate | `s_diderm_domain_posture.rs` + `mod.rs` sort order |
| `s_depot_architecture_coverage` flaky in parallel | Medium | eastGate | Passes alone, fails in full suite (resource contention) |
| golgiBody TURN relay not deployed | **Blocking** | Ops / songBird | Code complete, systemd unit ready, needs deploy |
| Benchmark harness does not exist | **Blocking** | songBird team | `songbird benchmark --mode tower-atomic` unbuilt |
| `PRIMALSPRING_WAVE150u_TOWER_PARITY_AAR.md` referenced but missing | Low | eastGate | Write or supersede reference |
| Line coverage 73.8% vs 90% target | Medium | eastGate | Live-only paths; honest skip semantics mitigate |

---

## WG Baseline (for parity comparison when Tower benchmark runs)

| Path | Metric | Value |
|------|--------|-------|
| flockGate → golgiBody | RTT | 30.7 ms |
| flockGate → sporeGate (via golgiBody) | RTT | 66.2 ms |
| flockGate → golgiBody | Throughput | TBD (iperf3 needed) |
| flockGate → sporeGate | Throughput | TBD (iperf3 needed) |

**Note**: Should run `iperf3` over WG to establish throughput baseline before
Tower benchmark runs. Recommend sporeGate team coordinate timing.

---

## Decisions / Actions Required

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Deploy `songbird relay` on golgiBody VPS | Ops / songBird | P1 — blocks benchmark |
| 2 | Build `songbird benchmark` harness | songBird team | P1 — blocks benchmark |
| 3 | Run `cargo fmt` on primalSpring | eastGate | P2 |
| 4 | Fix flaky `s_depot_architecture_coverage` | eastGate | P2 |
| 5 | Establish iperf3 WG baseline (flockGate ↔ sporeGate) | sporeGate + flockGate | P2 |
| 6 | Coordinate benchmark execution window | sporeGate (drives) | After #1 + #2 |

---

## Current Posture

**flockGate: GREEN / READY**

- Tower Atomic: 3/3 primals LIVE
- WG mesh: UP, peers reachable
- Structural validation: PASSING
- esotericWebb: HEALTHY, no regressions
- Code convergence: at eastGate HEAD

**Awaiting**: songBird TURN deploy on golgiBody + sporeGate to drive benchmark probes.

---

## Artifacts

- `handoffs/FLOCKGATE_PRIMALSPRING_WAVE150v_TOWER_PARITY_AUDIT.md` — full dimensional audit
- This AAR — summary for overwatch

---

*flockGate team, Wave 150v. Converging.*
