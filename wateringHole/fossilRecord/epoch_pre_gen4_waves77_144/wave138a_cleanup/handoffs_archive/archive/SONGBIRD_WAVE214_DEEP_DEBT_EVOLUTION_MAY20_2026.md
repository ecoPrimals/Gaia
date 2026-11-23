# Songbird — Wave 208–214 Deep Debt Evolution Handoff

**Date**: May 20, 2026
**From**: songBird
**To**: primalSpring, biomeOS, projectNUCLEUS
**Version**: v0.2.1
**Commits**: `f2ab69f8..3ca0eafb` (main)

## Context

Since the last infra handoff (Wave 207 — Stadial Readiness), songBird has shipped
7 waves of deep debt evolution and new capability. The codebase remains at S+ tier
with zero unsafe, zero files >800L, zero production stubs remaining in networking
paths, and full clippy pedantic compliance across all 31 crates.

## Shipped Waves (208–214)

### Wave 214 — Deep Debt: Stub Evolution & Lint Narrowing
- `DirectConnection::send()` evolved from no-op stub to real UDP I/O (connected socket)
- Production HTTPS upgraded from `generate_test_certificate()` to `CertificateGenerator::generate_self_signed()`
- `upgrade_connection()` endpoint now resolves actual protocol endpoints (was stub)
- 6× hardcoded `"0.0.0.0:0"` → `EPHEMERAL_BIND_ADDR` across 5 crates
- Crate-level `clippy::too_many_lines` removed from 3 crates → 12 targeted function annotations

### Wave 213 — Full NAT Traversal Data Plane & Shadow Comparator
- `TurnSession::spawn_keepalive()` — background refresh at 80% allocation lifetime
- `TurnRelayedConnection` — full data-plane `ConnectionSession::TurnRelayed` variant
- `CloudflaredTunnel` — Tier 5 emergency tunnel orchestration (spawn, URL parse, kill-on-drop)
- `shadow_comparator` module — dual-path shadow run (TURN vs cloudflared parallel probe)
- Cross-gate `capability.call` integration tests (3 new: local UDS dispatch, routing logic)

### Wave 211 — Cross-Gate Dispatch (CG-8 Resolution)
- `capability.call` JSON-RPC method — routes RPCs to local or remote capabilities
- Mesh TCP forwarding for remote gate dispatch
- `BeaconMesh` peer discovery integration
- **CG-8 is resolved in songBird** — biomeOS consumption remains open

### Wave 208–210 — Incremental Debt Passes
- `primal_discovery.rs` (763→419L via test extraction)
- `json_rpc_method/mod.rs` (639→487L via test extraction)
- Largest file now 799L (`multi_tier_coordinator.rs`)

## Current Metrics

| Metric | Value |
|--------|-------|
| Tests | 7,803+ lib passed |
| Files >800L | 0 (max: 799) |
| Unsafe | 0 (forbid across 31 crates) |
| Clippy | Zero warnings (pedantic + nursery, -D warnings) |
| Production stubs | 0 in networking paths |
| todo!/unimplemented! | 0 |
| Crates | 31 |

## Gap Status Update

| Gap | Status | Notes |
|-----|--------|-------|
| CG-8 Cross-gate dispatch | **RESOLVED (songBird)** | `capability.call` wired Wave 211. biomeOS integration to route to Songbird UDS still open. |
| UB-1 TURN client | **RESOLVED** | `songbird-turn-client` (Wave 205) + full data-plane integration (Wave 213) |
| R10 Stale sockets | **RESOLVED** | Cleanup on startup since Wave 199 |
| S2 Shadow run | **LIVE** | `shadow_comparator` probes TURN + cloudflared in parallel; relay deployed to VPS May 2026 |

## Remaining (songBird side)

### Operational (not code debt)
- [x] Deploy relay on cellMembrane VPS — **DONE** (Songbird TURN :3478 LIVE, May 2026)
- [ ] Live STUN/TURN integration test with deployed relay
- [ ] Run `songbird_nat_parity.sh` bench scenario

### Downstream Ask (biomeOS)
- [ ] Route `capability.call` to songbird UDS for remote gates
- [ ] Capability advertisement in mesh via `primal.announce`

### Platform (future)
- [ ] NFC backends (Android JNI, iOS CoreNFC, Linux libnfc)
- [ ] iOS XPC transport
- [ ] Windows Named Pipes
- [ ] WASM support

## Fossil Record

All prior waves documented in `primals/songBird/CHANGELOG.md` (4,500+ lines).
Archived handoffs: Wave 199–207 in `handoffs/archive/SONGBIRD_WAVE*`.
