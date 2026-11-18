# Songbird — primalSpring Wave 38: Cross-Gate TURN Relay Dispatch

**Date**: May 22, 2026
**From**: songBird
**To**: primalSpring, biomeOS, projectNUCLEUS
**Version**: v0.2.1
**Commit**: `9c1cb516` (main)

## Context

primalSpring Wave 38 assigned songBird two items:
1. Wire JSON-RPC routing over TURN relay for `capability.call` remote dispatch
2. NAT field test for residential scenarios (CGNAT, double-NAT)

Both are now shipped.

## Shipped

### TURN Relay Fallback for Cross-Gate Dispatch

`forward_to_remote_gate()` in `songbird-universal-ipc::service::ipc_registry` now
implements two-phase remote dispatch:

1. **Phase 1 (TCP direct)**: Same as Wave 211 — iterate reachable mesh peers, connect
   via `TcpStream` to their Songbird HTTP JSON-RPC port
2. **Phase 2 (TURN relay)**: When ALL direct TCP attempts fail, allocate TURN sessions
   via `SONGBIRD_TURN_*` env vars and send JSON-RPC bytes through the sovereign relay

This handles CGNAT, double-NAT, and symmetric NAT scenarios where the remote gate
is not directly reachable. The relay is sovereign (cellMembrane VPS at :3478), and
traffic is opaque bytes (BTSP-encrypted at higher layers).

### Capability-Aware Peer Filtering

Before dispatching `capability.call` to a remote peer, songBird now probes the peer
with `capabilities.list` to verify it actually provides the target capability. This
eliminates blind fan-out across the mesh.

`peer_has_capability()` checks both:
- Flat `capabilities` string array
- Structured `provided_capabilities` array (objects with `type` field)

### NAT Field Test Harness

New module `songbird-lineage-relay::nat_field_test` provides:
- `NatScenario` descriptors for CGNAT/double-NAT/symmetric peer addresses
- `probe_turn_path()` — allocates TURN to a scenario peer, sends health check, measures RTT
- `run_field_test_matrix()` — runs full scenario set
- Unit tests (pass without TURN env — validate graceful degradation)
- Live TURN tests (`--ignored` gate — require `SONGBIRD_TURN_*` env)

## Gap Status Update

| Gap | Status | Notes |
|-----|--------|-------|
| CG-8 Cross-gate dispatch | **RESOLVED (full)** | Wave 211 TCP + Wave 38 TURN relay |
| S2 TURN relay | **TURN dispatch LIVE** | Missing only: 7-day field soak on flockGate |
| CM-3 Cross-gate testing | **Unblocked** | Harness ready, needs live flockGate deploy |
| biomeOS integration | **Downstream** | biomeOS routes to songBird UDS for remote gates |

## S2 Cutover Status

- TURN relay uptime: 100% (3+ days as of Wave 38 audit)
- Cross-gate dispatch: TCP + TURN relay both functional
- NAT field test: Harness ready, live flockGate deployment pending
- **Remaining for S2**: 7-day 100% reachable soak on residential NAT (flockGate)

## Metrics

| Metric | Value |
|--------|-------|
| Tests | All pass (0 failures) |
| Clippy | Zero warnings (`-D warnings`) |
| Format | Clean |
| New module | `nat_field_test.rs` (247 lines) |
| New dep | `songbird-turn-client` → `songbird-universal-ipc` |

## Downstream Ask

- **projectNUCLEUS**: Deploy flockGate with songBird for residential NAT soak test
- **biomeOS**: Route `capability.call` to songBird UDS when target is on remote gate
