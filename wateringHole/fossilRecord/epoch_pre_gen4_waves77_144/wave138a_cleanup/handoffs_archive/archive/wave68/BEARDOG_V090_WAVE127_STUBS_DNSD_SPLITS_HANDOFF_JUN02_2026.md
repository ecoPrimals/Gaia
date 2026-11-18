# bearDog v0.9.0 — Wave 127 Handoff
## Stub Evolution, DNS-SD Wiring, File Splits, Safety Hygiene
**Date:** Jun 2, 2026
**Commit:** `e0951a019`
**Gate:** southGate

---

## 1. Production Stub Evolution

### validate_key_access (android_strongbox)
Replaced dead `if false` placeholder with real keystore existence check via `block_in_place` + `block_on` async bridge. Keys that don't exist in the transport now return `BearDogError::not_found`.

### memory_key_manager::list_keys()
Previously always returned empty despite keys being stored. Now enumerates the in-memory `HashMap`, returning `KeyMetadata` with IDs and inferred key types.

### get_network_interfaces()
Previously returned empty on all platforms. Now implements Linux network enumeration via `/sys/class/net` + `/proc/net/if_inet6`; other platforms return loopback.

---

## 2. DNS-SD / mDNS Discovery Wiring

- Wired `discover_from_mdns` and `discover_from_dns_sd` to existing `MdnsDiscoveryClient`
- Local domains (`.local`) use mDNS via `mdns-sd` crate
- Extended `MdnsDiscoveryClient` with configurable service types
- Unicast DNS-SD logs info and returns empty (hickory-resolver suspended)

---

## 3. File Splits (3 monoliths → 13 modules)

| Original | Split |
|----------|-------|
| `tcp_ipc/server.rs` (814L) | `server/{mod,connection,tests}` |
| `btsp_provider.rs` (791L) | `btsp_provider/{mod,contact_exchange,peer_discovery,session_crypto}` |
| `primal_discovery.rs` (779L) | `primal_discovery/{mod,env,mdns,upa,multi}` |

---

## 4. Safety Hygiene

Added `#![forbid(unsafe_code)]` to: `beardog-deploy/main.rs`, `beardog-installer/main.rs`, `benchmarks/lib.rs`. All workspace crates (library + binary) now forbid unsafe code.

---

## 5. Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt` | ✓ clean |
| `cargo clippy -- -D warnings` | ✓ zero warnings |
| `cargo test` | ✓ 1159 passed, 0 failed |
