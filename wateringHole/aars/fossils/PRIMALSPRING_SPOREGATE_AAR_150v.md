# primalSpring sporeGate AAR — Wave 150v

**Date**: July 22, 2026 | **Wave**: 150v | **From**: sporeGate (10.13.37.2)
**Scope**: Tower Atomic parity benchmark — full dimensional audit + WAN readiness

---

## What Happened

sporeGate team (sporeGate + golgiBody) spun up primalSpring Wave 150v per the
Tower Atomic parity benchmark blurb. Per convergence rules, sporeGate is a
benchmark runner — no code changes to primalSpring, findings filed as handoff.

### Dimensional Audit — primalSpring v0.9.42

Full 5-dimension audit completed. primalSpring is audit-clean:

| Dimension | Status | Key Metric |
|-----------|--------|------------|
| Code Quality | **CLEAN** | 0 clippy warnings, 0 fmt issues, 0 unsafe, 0 TODO markers |
| Architecture | **COMPLIANT** | JSON-RPC 2.0, ecoBin, semantic naming, Silicon Atheism |
| Test Coverage | **75.63%** | 1,214 tests pass (0 fail), 173 scenarios, proptest present |
| Debt & Gaps | **MINIMAL** | 2 scenarios / 16 failures — all upstream blockers |
| Sovereignty | **COMPLIANT** | AGPL-3.0, Pure Rust crypto, no telemetry, no vendor lock-in |

### Tower Atomic Primals — 3/3 LIVE on sporeGate

| Primal | Status | Socket |
|--------|--------|--------|
| bearDog | LIVE | `/run/membrane/beardog.sock` |
| songBird | LIVE | `/run/membrane/songbird.sock`, :7780, :7700 |
| skunkBat | LIVE | `/run/membrane/skunkbat.sock` |

All deployed from `plasmidBin/primals/x86_64-unknown-linux-musl/`.
songBird running as systemd `songbird-gateway.service`.

### Structural Scenario — 21/21 GREEN

`tower-atomic-parity` scenario passes all checks (commit `1ab0bfea`).

### WireGuard Baseline Measured

| Path | RTT |
|------|-----|
| sporeGate → golgiBody (.1) | **37.8ms** |
| sporeGate → flockGate (.6, 2-hop) | **68.1ms** |

### WAN Benchmark — BLOCKED

Two operational blockers prevent benchmark execution:

1. **P0 — TURN relay not deployed on golgiBody**: songBird `relay` mode is code
   complete but not deployed as a systemd unit on golgiBody ([RELAY_PUBLIC]).
   Without this, there is no Tower relay path to test.

2. **P1 — Benchmark harness not implemented**: The proposed `songbird benchmark`
   CLI (from `TOWER_ATOMIC_CONVERGENCE.md`) does not exist. Need throughput +
   latency measurement through the Tower relay stack.

---

## Findings for eastGate

### P2: Doc Warning

`ecoPrimal/src/bin/nucleus_launcher/orchestrator/registry.rs:55` — unclosed HTML
tag `Vec<domain>` should be `` `Vec<domain>` ``. Only real `cargo doc` warning.

### ~~P3: WAN Latency Target Recalibration~~ — RESOLVED

eastGate updated `TOWER_ATOMIC_CONVERGENCE.md` to use relative targets
(≥80% of WG throughput, ≤2x WG latency) instead of absolute thresholds.
Our measured WG baselines (37.8ms to golgiBody, 68.1ms to flockGate) are
now the reference — Tower just needs to stay within 2x of those.

### Coverage Note

75.63% line coverage is below the 90% target. Gap is almost entirely in
Live-tier scenario branches that require running primals — structural paths
are near 100%. This is structural to a validation crate; consider either
mock-backed integration tests or adjusted targets for harness crates.

---

## Artifacts

| Artifact | Location |
|----------|----------|
| Full handoff | `handoffs/PRIMALSPRING_WAVE150v_TOWER_PARITY_SPOREGATE_AUDIT.md` |
| This AAR | `aars/PRIMALSPRING_SPOREGATE_AAR_150v.md` |

---

## Next Actions

| Action | Owner | Priority |
|--------|-------|----------|
| Deploy TURN relay on golgiBody | golgiBody ops | **P0** |
| Implement benchmark harness | eastGate songBird | **P1** |
| Verify flockGate Tower peer status | flockGate team | **P1** |
| Fix `Vec<domain>` doc warning | eastGate primalSpring | **P2** |
| ~~Recalibrate WAN latency target~~ | ~~eastGate~~ | **RESOLVED** — convergence brief updated to relative targets |
| LAN benchmark (when ironGate returns) | sporeGate | **DEFERRED** |

---

**Filed by**: sporeGate + golgiBody team
**Convergence**: No primalSpring code modified. Handoff + AAR only.
