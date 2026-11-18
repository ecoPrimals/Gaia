# Tower Atomic Parity Benchmark — Wave 150w

**Date**: Jul 23, 2026
**Gate**: sporeGate (10.13.37.2)
**Harness**: `songbird benchmark` (shipped Wave 150v, commit c4d8c4b4)

## LAN Results (sporeGate ↔ eastGate, backbone)

| Metric | WireGuard | Tower Atomic | Ratio | Target | Status |
|--------|-----------|-------------|-------|--------|--------|
| Latency avg | 154.1ms | 153.5ms | **0.996x** | ≤2x WG | **PASS** |
| Latency p95 | 155.3ms | 156.9ms | 1.01x | ≤2x WG | **PASS** |
| Jitter | 0.13ms | 0.18ms | 1.36x | — | OK |
| Setup avg | 76.5ms | 77.3ms | 1.01x | ≤500ms | **PASS** |
| Throughput | 6.24 Mbps | 6.70 Mbps | **1.07x** | ≥80% WG | **PASS** |

## WAN Results (sporeGate → golgiBody TURN → flockGate)

| Metric | WireGuard | Tower Atomic | Ratio | Target | Status |
|--------|-----------|-------------|-------|--------|--------|
| Latency avg | 134.4ms | 133.3ms | **0.992x** | ≤1.5x WG | **PASS** |
| Latency p95 | 138.0ms | 140.4ms | 1.02x | ≤1.5x WG | **PASS** |
| Jitter | 0.41ms | 0.39ms | 0.96x | — | OK |
| Setup avg | 65.1ms | 66.5ms | 1.02x | ≤500ms | **PASS** |
| Throughput | 6.90 Mbps | 6.85 Mbps | **0.993x** | ≥80% WG | **PASS** |

## Analysis

Tower Atomic achieves **full WireGuard parity** on both LAN and WAN paths.
Both stacks measure application-layer TCP through their respective transport
(Tower mesh TCP vs WireGuard tunnel), so latency numbers reflect songBird's
mesh port RPC round-trip, not raw packet latency.

Key observations:
- Latency is essentially identical (within noise margin)
- Tower actually slightly outperformed WG on LAN throughput (+7%)
- WAN throughput effectively identical (0.7% difference)
- Setup times well within the 500ms target
- Jitter comparable

**Throughput caveat**: The harness sends a single 64KB payload and measures
transfer time. Real-world sustained throughput testing (e.g., iperf3-style
streaming) would be a better measure for Phase 2 shadow mode. Current results
demonstrate parity at the application layer.

## Parity Verdict

**PHASE 1 PASS.** Tower Atomic meets all parity targets. Ready for Phase 2
(shadow mode — Tower runs alongside WireGuard with metrics comparison).

## Raw Data

- `/tmp/lan-tower.json` — Tower LAN
- `/tmp/lan-wireguard.json` — WG LAN
- `/tmp/wan-tower.json` — Tower WAN
- `/tmp/wan-wireguard.json` — WG WAN
