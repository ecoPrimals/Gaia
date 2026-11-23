# Songbird Wave 131b — LAN Peering + Security Hardening + Health Honesty

**Date**: July 4, 2026  
**Gate**: flockGate  
**Primal**: songBird v0.2.1-wave131b  
**Type**: LAN peering critical path + deep debt security + dependency diet  

---

## Changes

### 1. LAN Direct-Connect Bypass (P1 — eastGate mesh peering)

| Component | Change |
|-----------|--------|
| `udp_peer_connector.rs` | `try_lan_direct_connect()` — detects same-subnet private IPs via `/proc/net/fib_trie`, attempts TCP probe on federation port before UDP punch; reports honest "failed" instead of "punching" |
| `onion-relay/coordinator/punch.rs` | LAN fast-path — skips signaling for private-IP peers, direct UDP to `local_addr` |
| `bin_interface/server.rs` | Federation port defaults to `DEFAULT_MESH_PEER_PORT` (7700); binds 0.0.0.0 for cross-gate reachability |

New helpers: `is_private_ipv4()`, `local_ipv4_from_proc()` (parses `/proc/net/fib_trie` LOCAL markers).

### 2. Security Hardening (Fail-Closed)

| Location | Before | After |
|----------|--------|-------|
| `bluetooth_pure.rs` | Returns hardcoded fake credentials | Returns `GenesisError::PhysicalChannelError` (fail-closed) |
| `discovery_bridge.rs` | `PeerTrustDecision::AutoAccept` when no security provider | Reject peer (fail-closed) |
| `connection.rs` riboCipher | `_ => unreachable!()` for unknown tier | Error log + drop connection |
| `trust.rs` | `TrustLevel::None => unreachable!()` | `Err(anyhow!(...))` |

### 3. Health Honesty (SubsystemStatus)

`health_readiness()` and `health_check()` now require a `SubsystemStatus` struct. Subsystems report "degraded" unless explicitly marked ready. Updated all call sites (3 crates).

### 4. Dependency Diet (continued)

| Dependency | Before | After |
|------------|--------|-------|
| `tarpc` | `features = ["full"]` | `["tokio1", "serde-transport", "serde-transport-bincode", "tcp"]` |
| `hyper` | `features = ["full"]` | `["http1", "client", "server"]` |

### 5. Hardcoding Elimination

`internal_ip: String::from("192.0.2.10:8000")` → env-derived (`SONGBIRD_FEDERATION_BIND` / `SONGBIRD_PRODUCTION_BIND_ADDRESS`).

---

## Verification

- Zero clippy warnings (`--workspace --all-targets -D warnings`)
- All tests pass including 3 new LAN-specific tests + updated health tests
- Zero unsafe blocks, zero production unwrap, zero TODO/FIXME

---

## Upstream Review Targets

1. **LAN topology**: Other gates should verify their `/proc/net/fib_trie` returns expected local IPs for subnet detection
2. **Health consumers**: Any dashboard or monitoring reading `health.readiness` should expect `"degraded"` until subsystems fully wire their status
3. **Federation port**: All gates should confirm `SONGBIRD_FEDERATION_PORT=7700` or rely on new default
4. **Security provider**: With fail-closed now enforced, gates without a security provider will reject genesis/discovery peers — expected until BearDog is live

---

## Status

Songbird is **CLEAR** — LAN peering unblocked, security posture hardened, health reporting honest, dependency surface reduced.
