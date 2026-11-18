# BearDog v0.9.0 — Wave 131: BTSP Trust Issuer Exchange + Deep Evolution

**Date**: Jul 4, 2026  
**From**: flockGate (BearDog agent)  
**Scope**: P1 mesh auth unblock + deep evolution sweep  
**Commits**: `389dbb9` (trust exchange), `075f62e` (evolution sweep)

---

## Summary

Wave 131 delivers the **BTSP trust_issuer exchange** — the P1 that blocked mesh authentication for songBird's LAN peering. Also includes a comprehensive deep evolution sweep addressing type safety, mock/stub hygiene, smart refactoring, and capability-based discovery.

---

## Wave 131a: BTSP Trust Issuer Exchange (P1 — Blocks Mesh Auth)

### mesh_join orchestrator (`beardog-tunnel/src/mesh_join.rs`)
- Single async call: BTSP connection → `auth.exchange_trust` → local registry registration
- Returns `MeshJoinResult` with bidirectional trust confirmation
- Enables songBird to call `mesh_join()` after BTSP handshake without manual env var exchange

### Registry persistence
- `TrustedIssuerRegistry::save_to_file()` / `load_from_file()` — JSON v1 format
- `save_path()` resolves `$XDG_DATA_HOME/beardog/trusted_issuers.json`
- DID/key binding validated on load; survives restarts

### exchange_trust polish
- Response includes `local_family_id` for downstream consumers
- Emits `KeyExchangeCompleted` event for mesh listeners (rhizoCrypt, songBird)
- `BtspConnection::session_id()` accessor for tracing correlation

### E2E integration test
- `mesh_join_e2e_over_tcp`: real TCP + BTSP handshake + handler dispatch
- Proves two gates populate bidirectional registries via single `mesh_join` call

---

## Wave 131b: Deep Evolution Sweep

### P0 — Security & Type Safety
| Fix | Impact |
|-----|--------|
| Android attestation fail-closed | `jni_initialize` returns `not_yet_available` instead of fake `Ok(())` |
| SimpleHsmTier deduplicated | Two conflicting enums unified to one canonical definition |
| TLS provider hardened | `custom-provider` feature; explicit CryptoProvider install in ACME + tunnel |

### P1 — Smart Refactoring
| Fix | Impact |
|-----|--------|
| `trusted_issuer_registry.rs` (826L) → module directory | 6 focused files (did, types, registry, persistence, verify, tests); zero production files > 800L |

### P1 — Mock/Stub Evolution
| Fix | Impact |
|-----|--------|
| `MdnsDiscovery::default()` | No longer panics; gracefully degrades to disabled state |
| `get_discovered_services_count` | Propagates errors instead of masking with `Ok(0)` |
| DNS SRV discovery | Returns `BackendUnavailable` instead of silent empty Vec |
| HSM health monitor | Placeholder documented with EVOLUTION marker + debug tracing |

### P1 — Capability-Based Discovery
| Fix | Impact |
|-----|--------|
| `primal.announce` wired to HandlerRegistry | Method names and domains derived at runtime from registered handlers |
| Static `beardog_announce_method_names()` deprecated | Will be removed after biomeOS integration update |
| `UnixSocketIpcServer::handler_registry()` | New accessor for runtime introspection |

### Debris Cleanup
- 5 HTTP-era config templates deleted (orphaned, no code references)
- 2 docs annotated with archive notices (broken internal refs from HTTP era)
- Root docs synced to Wave 131 dates

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests (workspace) | 13,860+ passing |
| Clippy | 0 warnings |
| Production files > 800L | 0 |
| Unsafe blocks | 0 |
| TODO/FIXME markers | 0 |
| ring in compiled graph | No (phantom lockfile only) |

---

## What This Unblocks

1. **songBird mesh auth** — `mesh_join()` provides the trust exchange primitive songBird needs for `peer.connect`
2. **Runtime discovery** — `primal.announce` now reflects actual registered capabilities
3. **Registry durability** — trust survives gate restarts without env var re-seeding
4. **Policy compliance** — zero production mocks returning fake success; all stubs fail closed

---

## Upstream Dependencies

- **songBird**: can now call `beardog_tunnel::mesh_join::mesh_join()` after BTSP handshake
- **cellMembrane**: `capability.call` route validation once peers are trusted
- **biomeOS**: `primal.announce` payload now accurate and dynamic

---

## Remaining BearDog Debt (P2, monitored)

- 9 test-only files > 800L (refactor opportunistically)
- `graph_security/audit.rs` at 799L (one line from threshold)
- 6 workspace-excluded dormant crates (architecture decision, not debris)
- `collaboration_service.rs` unwired (blocked on multi-primal deployment)
- HTTP-era `beardog-integration` REST surface (songBird owns transport evolution)

---

*The mesh absorbs. One key pair proves lineage.*
