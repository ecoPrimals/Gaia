# AAR — Topology Ops + Shadow Deploy Across Mesh — sporeGate

**Wave**: 150w | **Date**: Jul 23, 2026 (afternoon) | **Gate**: sporeGate | **Team**: cellMembrane + topology

---

## Summary

Resolved P0 #3 (shadow deploy on remaining gates), discovered eastGate's
actual LAN IP (not at 192.168.4.30 — found at 192.168.4.244 via nmap),
achieved sub-1ms LAN benchmarks, and shipped LAN peer discovery in songBird.

## Completed

| # | Task | Status | Detail |
|---|------|--------|--------|
| 1 | Enable tower.shadow on golgiBody | DONE | Timer active at 60min, 7 peers |
| 2 | Enable tower.shadow on flockGate | DONE | Timer active at 60min, 6 peers |
| 3 | Deploy updated membrane binary | DONE | golgiBody + flockGate updated |
| 4 | Diagnose LAN unreachable | DONE | eastGate NOT at 192.168.4.30 — found at 192.168.4.244 |
| 5 | LAN benchmark (sporeGate ↔ eastGate) | DONE | 0.17ms ping, 0.6ms songBird latency |
| 6 | songBird `lan_addr` in peers.toml | DONE | Shipped to songBird, pushed to Forgejo |
| 7 | Update ecosystem manifest | DONE | Added `lan_ip` for sporeGate + eastGate |
| 8 | Configure local peers.toml | DONE | eastGate LAN endpoint set |

## Key Findings

### LAN Peering Discovery

The blurb listed eastGate at 192.168.4.30 — **wrong IP**. nmap scan of
192.168.4.0/24 for :7700 found 3 hosts:
- 192.168.4.3 (sporeGate — us)
- 192.168.4.244 (eastGate — **0.17ms, wired via enp5s0**)
- 192.168.4.103 (eastGate — wireless backup, 33ms)

SSH confirmed: `eastgate@192.168.4.244` → hostname `pop-os`, WG IP `10.13.37.5`.

### LAN Benchmark Results (sporeGate → eastGate, 192.168.4.244)

| Metric | Tower Atomic | WireGuard | Winner |
|--------|-------------|-----------|--------|
| Avg Latency | **0.607ms** | 0.658ms | Tower (8% faster) |
| P50 Latency | **0.610ms** | 0.671ms | Tower |
| Jitter | **0.018ms** | 0.027ms | Tower (33% less) |
| Throughput | 3,776 Mbps | 6,645 Mbps | WG (small payload) |

**Sub-1ms achieved.** Tower shows lower latency and significantly less jitter
on LAN. Throughput comparison needs larger payloads (196KB test too small).

### Shadow Deploy Status

| Gate | Timer | Peers | Status |
|------|-------|-------|--------|
| sporeGate | ACTIVE (60min) | 7 | 76+ result files |
| golgiBody | ACTIVE (60min) | 7 | Just activated |
| flockGate | ACTIVE (60min) | 6 | Just activated |

### songBird LAN Peer Discovery

Shipped `lan_addr` support to songBird persistence:
- `PersistedPeer` struct extended with optional `lan_addr`
- `mesh.enroll` accepts `lan_addr` parameter
- `load_persisted_peers_full()` returns `LoadedPeer` with LAN info
- `mesh_seed` registers `EndpointType::Local` endpoints (priority 0)
- Backward-compatible: existing peers.toml without `lan_addr` still works
- 4 persistence tests pass, build clean

## Code Changes

| Repo | Commit | Lines |
|------|--------|-------|
| songBird | `feat: LAN peer discovery — lan_addr in peers.toml` | +112/-8 |
| wateringHole | `topology: add lan_ip for sporeGate + eastGate` | +3/-1 |

## Remaining

| # | Item | Owner |
|---|------|-------|
| 1 | Restart songbird-gateway to pick up new peers.toml | sporeGate ops (next restart) |
| 2 | Drawbridge JSON-RPC→HTTP translation | eastGate (P0) |
| 3 | checksums.toml format migration | eastGate (P0) |
| 4 | 10G backbone cabling | hardware/operator |
| 5 | iperf3 sustained throughput | deferred until 10G |
| 6 | Gate enrollment (southGate, strandGate) | physical access |
