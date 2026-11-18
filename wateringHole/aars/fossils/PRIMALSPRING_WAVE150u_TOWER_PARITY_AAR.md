# primalSpring AAR — Wave 150u: Tower Atomic Parity Scenario

**Date**: 2026-07-22 | **Gate**: eastGate | **Version**: v0.9.42
**Commit**: `3de00e77` | **Status**: CONVERGENCE BRIEF INTEGRATED

---

## What Was Done

primalSpring shipped the **Tower Atomic Parity Benchmark** scenario (item #3a
from the Wave 150u team actions), then evolved it to integrate the full
**songBird Parity Convergence Brief** (Wave 150t).

### Scenario: `tower-atomic-parity` (evolved)

| Property | Value |
|----------|-------|
| Track | Evolution |
| Tier | Rust |
| Checks | 29 (6 phases) |
| Result | ALL PASS |

**Phase breakdown (updated per convergence brief):**

1. **Tower Atomic stack** — bearDog crypto (Ed25519 + X25519 + ChaCha20-Poly1305),
   songBird transport (relay + connect + peers), skunkBat protocol negotiation,
   Tower composition tier, cold-start bootstrap signal
2. **Transport layer** — 5-tier NAT traversal (direct→STUN→relay→TURN→tunnel),
   BeaconMesh peer discovery, TURN relay (RFC 5766), drawbridge HTTP bridge,
   BTSP encrypted framing enforcement
3. **HMAC enrollment protocol** — mesh.enroll/init (LIVE), HMAC verification
   chain (btsp.handshake + negotiate), btsp.server.status health, ≥6 gate roster
4. **Benchmark topology** — LAN pair (sporeGate↔eastGate backbone), VPS hub
   (golgiBody .1 TURN relay), WAN peer (flockGate)
5. **Relative parity targets** (key change — per convergence brief):
   - Throughput: ≥80% of WG baseline (not absolute Mbps)
   - Latency: ≤2x WG RTT (WG ~0.3ms LAN → Tower ≤0.6ms)
   - Connection setup: ≤500ms (vs WG ~50ms — 10x budget)
   - Reconnect: ≤2s mesh re-discovery (WG is stateless/instant)
   - CPU idle: ≤1% (WG ~0%)
   - CPU saturated: ≤20% (WG ~5%)
6. **Convergence gate** — CredentialStore shipped, mesh.announce for shadow mode,
   capabilities_query for pre-activation check, Phase 0 confirmed

---

## What This Enables

The structural scenario is GREEN. The **actual parity benchmark** requires
Live-tier execution with two active peers running the Tower Atomic stack.

---

## Spin-Up Request for Upstream Teams

### Item #3b: ironGate team — LAN benchmark peer

**What**: Deploy Tower Atomic stack (bearDog + songBird + skunkBat) on ironGate
and run LAN throughput/latency tests against eastGate.

**Requirements**:
- Tower Atomic binaries from depot (all 3 in plasmidBin)
- BTSP-authenticated relay between eastGate (.5) ↔ ironGate (.7)
- iperf3-equivalent throughput test through Tower relay (target: >800 Mbps)
- ping-equivalent latency test through Tower relay (target: <5ms RTT)
- Compare against raw WireGuard baseline on same link
- Report results as `TOWER_LAN_PARITY_RESULTS.md` in wateringHole handoffs

**Topology**:
```
eastGate (10.13.37.5) ←→ Tower Atomic relay ←→ ironGate (10.13.37.7)
                         vs.
eastGate (10.13.37.5) ←→ WireGuard tunnel  ←→ ironGate (10.13.37.7)
```

### Item #3c: golgiBody team — WAN benchmark peer + TURN relay

**What**: Deploy Tower Atomic TURN relay on golgiBody and run WAN
throughput/latency tests between LAN gates and VPS.

**Requirements**:
- Tower Atomic binaries on golgiBody (bearDog + songBird minimum)
- TURN-style relay configuration (songBird mesh.relay listening on VPS)
- iperf3-equivalent throughput test through Tower WAN relay (target: >50 Mbps)
- Latency test eastGate (.5) → golgiBody (.1) → ironGate (.7) (target: <50ms)
- Compare against WG WAN baseline through same path
- Report results as `TOWER_WAN_PARITY_RESULTS.md` in wateringHole handoffs

**Topology**:
```
eastGate (10.13.37.5) ←→ golgiBody TURN (.1) ←→ ironGate (10.13.37.7)
                          vs.
eastGate (10.13.37.5) ←→ golgiBody WG hub (.1) ←→ ironGate (10.13.37.7)
```

---

## primalSpring Live Scenario (pending benchmark results)

Once #3b and #3c report results, primalSpring will ship:
- `s_tower_atomic_parity_live` (Live tier) — actual benchmark execution
- Tolerance constants in `tolerances/` for Tower vs WG parity thresholds
- Updated sovereignty-roadmap scenario with benchmark PASS/FAIL gate

---

## Upstream Gaps Tracked

| Gap | Owner | Status |
|-----|-------|--------|
| `enrollment.verify` endpoint | bearDog (P1) | PENDING — needed for HMAC proof delegation |
| `songbird benchmark` harness | songBird (P2) | TODO — throughput measurement tooling |
| TURN relay deployment | ops/golgiBody (P2) | systemd unit ready, needs deploy |
| `btsp.server.export_keys` | bearDog (P2) | Per-session key derivation for perf testing |

## Current Metrics

| Metric | Value |
|--------|-------|
| Scenarios | 174 |
| Lib tests | 1214 (0 fail, 2 ignored) |
| Clippy | 0 (pedantic + nursery) |
| KNOWN_DEBT | 2 (graphenegate-readiness: 1, composition-access-control: 15) |

---

## For Overwatch

- **primalSpring item #3a**: DONE — structural scenario shipped
- **ironGate team (#3b)**: SPIN UP — deploy Tower Atomic, run LAN benchmark
- **golgiBody team (#3c)**: SPIN UP — deploy TURN relay, run WAN benchmark
- **primalSpring (next)**: waiting on benchmark results to ship Live-tier scenario

No blockers. eastGate primalSpring is ready to consume benchmark data as soon
as the peer teams report.
