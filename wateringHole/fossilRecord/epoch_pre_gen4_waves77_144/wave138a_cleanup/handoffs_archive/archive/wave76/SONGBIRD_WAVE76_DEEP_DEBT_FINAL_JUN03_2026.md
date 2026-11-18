# Songbird Wave 76 — Deep Debt Final (Consolidation)

**Date**: June 3, 2026  
**From**: southGate (Songbird)  
**Version**: v0.2.8-wave76  
**Commits**: `a436a7e0`, `ed0c5c55`, `79455f72`

---

## Summary

Wave 76 consolidated deep debt, hygiene, and evolution across two passes:

### Pass 1: Hygiene + Retry + Phase 3.5 Scaffold (`a436a7e0`)
- Broker readiness propagation fixed (High severity)
- `post_jsonrpc_fire_and_forget` HTTP status + body drain
- Mesh lock hold reduction in `announce_capabilities_to_peers`
- BTSP `ts` required on structured tokens + future-skew bound (60s)
- Capability announce peer validation (unknown peers rejected)
- `BtspSignatureVerifier` trait + `NoopSignatureVerifier` placeholder
- Retry queue: failed announcements retried on health cycle (max 3)

### Pass 2: SRP Refactor + Advisory Mitigation (`ed0c5c55`)
- `mesh_handler/mod.rs` 1004L → 783L via `capability_propagation.rs` extraction (238L)
- RUSTSEC-2026-0118 (hickory-proto NSEC3 loop) mitigated in `deny.toml` — not reachable without DNSSEC features
- 4 new tests added (retry drain, peer rejection, capabilities empty)

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 13,966+ passed, 0 failures |
| Clippy | Zero warnings workspace-wide |
| Files >800L | 0 (largest: `virtual_relay.rs` 791L) |
| Unsafe | 0 (`forbid(unsafe_code)` all 31 crates) |
| `cargo deny` | All OK (advisories, bans, licenses, sources) |
| Build artifacts | Cleaned (89.9 GiB freed) |

---

## Standing Ready

- Mesh validation partner for eastGate live `discovery.peers` + `capability.call`
- Phase 3.5 activation when bearDog ships CryptoProvider design
- Cross-subnet TURN relay (P2, when VPS relay is staged)

## Known Advisory (Low Risk)

- `hickory-proto` 0.25.2 RUSTSEC-2026-0118: NSEC3 infinite loop in `DnssecDnsHandle`. Songbird uses plain stub resolver (no DNSSEC). Upgrade to 0.26 deferred — major API breaking changes in SRV/TXT record access require dedicated migration wave.
