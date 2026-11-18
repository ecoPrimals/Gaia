# AAR: Full Multi-Architecture Harvest — Wave 142b

**Date**: 2026-07-16 09:00 EDT | **Gate**: eastGate → sporeGate (builder)
**Wave**: 142b | **Operator**: sporeGate hardware team

---

## Summary

Executed the definitive multi-architecture harvest following Silicon Atheism Phase 1
completion (14/14 primals adopted). **Windows reached 14/14 COMPLETE** — the final
blocker (bearDog `UnixStream` in `beardog-ipc` + `beardog-core`) was fixed on
sporeGate with `#[cfg(unix)]` gating across 6 files. Android reached 12/14 (2
expected-fail). Musl refreshed for 5 changed primals. Total depot: **59 binaries
across 4 architectures**, signed and live on VPS.

## Results

### Windows: 14/14 COMPLETE

All 14 primals now compile and deploy for `x86_64-pc-windows-gnu`.

| Primal | Size | Notes |
|--------|------|-------|
| bearDog | 10M | **Fixed in this session** — UDS gating in beardog-core, beardog-ipc |
| songBird | 23M | |
| nestGate | 8.0M | |
| biomeOS | 19M | |
| rhizoCrypt | 5.6M | |
| squirrel | 3.6M | Fixed upstream (`110c9939`) |
| sweetGrass | 16M | |
| loamSpine | 4.0M | |
| skunkBat | 2.5M | |
| coralReef | 6.9M | |
| barraCuda | 4.9M | |
| petalTongue | 25M | Fixed upstream (`1af1a98`) |
| toadStool | 8.9M | |
| sourDough | 2.8M | Fixed upstream (`6115e4a`) |

### Android: 12/14 (2 expected-fail)

| Primal | Status | Notes |
|--------|--------|-------|
| bearDog | OK | 9.1M |
| songBird | OK | 22M |
| nestGate | OK | 7.7M |
| biomeOS | OK | 19M |
| rhizoCrypt | OK | 5.9M — **fixed in this session** (stale build in background harvest) |
| squirrel | OK | 3.6M |
| sweetGrass | OK | 11M |
| loamSpine | OK | 3.8M |
| skunkBat | OK | 2.5M |
| coralReef | OK | 6.6M |
| barraCuda | OK | 4.4M |
| sourDough | OK | 2.5M — fixed upstream (`6115e4a`) |
| **petalTongue** | **EXPECTED-FAIL** | Requires Android Activity framework (`game-activity`/`native-activity`) |
| **toadStool** | **EXPECTED-FAIL** | `SafeMmapRegion` — kernel mmap interface for hardware drivers |

### Musl Refresh: 10/10

5 primals with upstream changes rebuilt for both `x86_64-unknown-linux-musl` and
`aarch64-unknown-linux-musl`: bearDog, squirrel, petalTongue, toadStool, sourDough.

### Full Depot Summary

| Architecture | Binaries | Status |
|--------------|----------|--------|
| x86_64-unknown-linux-musl | 16 | COMPLETE |
| aarch64-unknown-linux-musl | 16 | COMPLETE |
| x86_64-pc-windows-gnu | **14** | **COMPLETE — 14/14** |
| aarch64-linux-android | 13 | 12/14 + nucleus_launcher |
| **Total** | **59** | **Signed + VPS-live** |

## bearDog Windows Fix — Technical Detail

### Root Cause

`beardog-core` and `beardog-ipc` had unconditional `use tokio::net::UnixStream`
imports and direct `UnixStream::connect()` calls in 6 files. The upstream `5d4258d`
commit fixed `beardog-tunnel` platform gating but missed the IPC layer.

### Files Changed (on sporeGate)

| File | Fix |
|------|-----|
| `beardog-core/src/primal_discovery/strategies.rs` | Split `discover_from_upa` into `#[cfg(unix)]` inner method |
| `beardog-ipc/src/isomorphic.rs` | Gate `IpcStream::Unix` variant, `AsyncStream for UnixStream`, all match arms |
| `beardog-ipc/src/client.rs` | Gate `connect()`, `send_request()`, `connect_test()` UDS calls |
| `beardog-ipc/src/neural_registration.rs` | Gate `send_primal_announce()` and `register_capability()` UDS calls |
| `beardog-ipc/src/registry_client.rs` | Gate `PrimalRegistryClient::stream` field and `connect()` |
| `beardog-tunnel/src/modes/client.rs` | Gate `std::os::unix` import |
| `beardog-tunnel/src/unix_socket_ipc/protocol.rs` | Gate `OwnedReadHalf` import |
| `beardog-tunnel/src/platform/{android,unix}.rs` | Module-level cfg gates |
| `beardog-tunnel/src/unix_socket_ipc/handlers/ionic_bond/persistence.rs` | Gate UDS connect |
| `beardog-cli/src/handlers/{client,server/health,doctor}.rs` | Gate Unix client/health/doctor |

### Pattern

Phase 1 gating: `#[cfg(unix)]` on Unix-specific code with `#[cfg(not(unix))]` fallbacks
that return clear errors or log warnings. No behavioral change on Unix/Linux.

## Handoffs

| Team | Action | Priority |
|------|--------|----------|
| bearDog team | Absorb sporeGate UDS gating into upstream (6 files in beardog-ipc, beardog-core) | P1 |
| petalTongue team | Android cdylib target config for Activity-based builds | P2 |
| toadStool team | Gate `SafeMmapRegion` for Android (or provide stub) | P2 |
| primalSpring team | `full-cross-compile` scenario to validate all 14 x 4 arches | P1 |

## Metrics

- Windows harvest: ~16 min (14 primals sequential)
- Android harvest: ~29 min (14 primals sequential, 12 succeed)
- Musl refresh: ~16 min (5 primals x 2 arches)
- Depot size: 555 MB total
- VPS sync: 84 MB transferred (delta), 4.2s
