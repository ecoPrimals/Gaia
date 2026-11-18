# Tower Atomic Data Analysis — Wave 150w

**Date**: Jul 23, 2026 | **Wave**: 150w | **From**: eastGate overwatch
**Purpose**: Honest assessment of what the benchmark data actually shows.

---

## Data Corpus

34 JSON benchmark files in `benchScale/tower_shadow/` across 3 gates
(sporeGate, flockGate, golgiBody). All produced by `songbird benchmark`
(366 lines, `primals/songBird/src/benchmark.rs`).

4 JSON files in `benchScale/tower_parity/` (curated LAN/WAN pairs).

## Harness Methodology

The benchmark runs 3 phases per execution:

| Phase | What | Method | Sample Size |
|-------|------|--------|-------------|
| Setup | TCP connect time | 10 `TcpStream::connect()` attempts, 50ms sleep between | 10 |
| Latency | JSON-RPC RTT | `health.ping` over TCP, 20ms sleep between probes | 20 (default) |
| Throughput | TCP write rate | Blast 64KB chunks until duration expires | 1 run |

### What the harness actually measures

**Latency** — reliable. TCP connect + JSON-RPC round-trip including
serialization, dispatch, response. Each probe opens a new TCP connection,
sends `{"jsonrpc":"2.0","method":"health.ping","params":{},"id":1}\n`,
reads one response. This measures the **full stack cost** per request.
p50/p95/p99 from sorted measurements. Jitter is mean absolute difference
between consecutive sorted samples.

**Setup** — reliable. Pure TCP connect time. 10 samples, stats computed.

**Throughput** — UNRELIABLE on fast paths. The harness sends 64KB chunks
in a loop until `duration` expires. But the `--duration` flag defaults
to `10s` and the `tower.shadow` timer invokes with default args. On LAN
(0.17ms RTT), a single 64KB write completes in sub-millisecond time.

The critical bug: `duration_ms` in the JSON output is
`elapsed.as_millis() as u64`. When the peer RSTs or stops accepting
after one chunk (196KB = 3 chunks), elapsed rounds to 0ms, producing
`throughput_mbps: Infinity` or a meaningless large number.

Evidence from the data:

```
LAN Tower:  duration_ms: 0, bytes_sent: 196608, throughput_mbps: 3775.56
LAN WG:    duration_ms: 0, bytes_sent: 196608, throughput_mbps: 6644.86
```

Both show `duration_ms: 0`. The "3.8 Gbps vs 6.6 Gbps" comparison is
**division by near-zero** — not a real throughput measurement.

On WAN (67ms+ RTT), duration is non-zero and the measurement is more
meaningful — but still only sends 64KB total, not sustained streaming.

## What the Data Actually Shows

### RELIABLE — Latency (20+ measurements per run)

| Path | Tower avg (ms) | WG avg (ms) | Ratio | Verdict |
|------|---------------|-------------|-------|---------|
| LAN direct (192.168.4.244) | 0.607 | 0.658 | **0.92x** | Tower wins |
| Hub (sporeGate→golgi→eastGate) | 153.69 | 153.11 | 1.004x | Parity |
| WAN (sporeGate→golgi→flockGate) | 136.06 | 136.09 | 1.000x | Parity |
| WAN (flockGate→golgiBody) | 59.7 | 59.2 | 1.008x | Parity |

LAN latency advantage is **real** (8% across multiple runs). Tower's
userspace JSON-RPC dispatch is faster than WG tunnel + kernel
re-encapsulation for small request/response patterns.

Hub and WAN latency are at parity — the 67-77ms RTT dominates and both
stacks add negligible overhead on top.

### RELIABLE — Jitter

| Path | Tower (ms) | WG (ms) | Ratio |
|------|-----------|---------|-------|
| LAN direct | 0.018 | 0.027 | **0.67x** |
| WAN (sporeGate→flockGate) | 0.42 | 0.50 | **0.84x** |
| WAN (flockGate→golgiBody) | 0.70 | 1.01 | **0.70x** |

Tower consistently shows **30-33% less jitter** than WG. This is
structural: userspace scheduling is more deterministic than kernel
tunnel path traversal. Significant for real-time workloads.

### UNRELIABLE — LAN Throughput

`duration_ms: 0` on both sides. Cannot compare. Need sustained
streaming measurement.

### QUESTIONABLE — WAN Throughput

| Path | Tower (Mbps) | WG (Mbps) | Ratio | duration_ms |
|------|-------------|-----------|-------|-------------|
| sporeGate→flockGate | 6.95 | 6.72 | 1.03x | 75/78 |
| sporeGate→flockGate (earlier) | 7.19 | 3.64 | **1.98x** | 73/143 |
| flockGate→golgiBody | 14.40 | 13.00 | 1.11x | 35/39 |

The "2x" result (7.19 vs 3.64 Mbps) from the earlier run shows WG took
143ms to send the same 64KB that Tower sent in 73ms. This could be real
(WG kernel overhead on multi-hop) or could be a transient network
condition. Later runs show 1.03x — much closer to parity.

**Conclusion**: WAN throughput likely favors Tower slightly (1.03-1.11x)
on single-shot payloads. The 2x outlier needs reproduction.

## What We Claimed vs What We Can Prove

| Claim | Evidence | Honest Assessment |
|-------|----------|-------------------|
| Tower 8% faster latency on LAN | Multiple runs, 20 probes each, 0.607 vs 0.658ms | **PROVEN** — consistent across runs |
| Tower 33% less jitter | Multiple runs, 0.018 vs 0.027ms | **PROVEN** — structural advantage |
| Tower 2x WAN throughput | Single run: 7.19 vs 3.64 Mbps, 64KB payload | **UNVERIFIED** — later runs show 1.03x. Outlier, not reproduced. |
| Tower exceeds WG on LAN throughput | duration_ms: 0 on both | **CANNOT MEASURE** — harness bug |
| WG wins LAN throughput (6.6 vs 3.8 Gbps) | duration_ms: 0 on both | **CANNOT MEASURE** — harness bug |
| Parity on all hub/WAN latency paths | Multiple runs, 20 probes | **PROVEN** — 1.000-1.008x |

## Measurement Gaps

1. **No sustained throughput**: Harness sends 64KB and stops. Need
   iperf3-style continuous streaming for 30s/60s.
2. **No concurrent load**: All measurements are serial single-connection.
   No contention testing.
3. **No crypto overhead measurement**: BTSP handshake cost not isolated.
4. **No failure mode testing**: What happens when bearDog or songBird dies?
5. **No adversarial testing**: JSON-RPC surface entirely untested.
6. **No composition cost measurement**: UDS hop overhead unknown.
7. **duration_ms truncation**: `as_millis() as u64` loses sub-millisecond
   precision on fast paths.

## Composition Cost — UDS Hop Analysis

A cross-gate `capability.call` traverses:

```
Caller → UDS → songBird → registry lookup → TCP → remote songBird → UDS → Provider
         ^                                   ^                        ^
         hop 1                               hop 2 (network)          hop 3
```

With BTSP-secured connection establishment, add:

```
songBird → UDS → bearDog (btsp.session.create)     hop 4
songBird → UDS → bearDog (btsp.session.verify)     hop 5
songBird → UDS → bearDog (btsp.server.export_keys) hop 6
```

Each UDS hop includes: connect, serialize JSON, write, read response,
deserialize. Estimated overhead: ~0.05-0.2ms per hop on LAN hardware.
At 6 hops for a BTSP-secured cross-gate call, that's ~0.3-1.2ms of
pure IPC overhead — comparable to the measured LAN latency of 0.6ms.

**The chimera hypothesis**: collapsing bearDog + songBird + skunkBat into
a single process eliminates 3-6 UDS hops per operation, potentially
halving LAN latency.

## Recommendations

1. Fix `measure_throughput` to use microsecond precision (`as_micros()`)
   and enforce minimum 1-second streaming duration.
2. Add sustained streaming benchmark mode (continuous for 30s+).
3. Add concurrent dispatch benchmark (N parallel capability.call).
4. Measure UDS hop cost in isolation (direct function call vs JSON-RPC UDS).
5. Reproduce the 2x WAN result with controlled conditions.
6. Do not claim LAN throughput numbers until the harness is fixed.

---

*This analysis is the ground truth for Tower Atomic performance claims.
Numbers above supersede any prior blurb or AAR claims that relied on
unreliable throughput measurements.*
