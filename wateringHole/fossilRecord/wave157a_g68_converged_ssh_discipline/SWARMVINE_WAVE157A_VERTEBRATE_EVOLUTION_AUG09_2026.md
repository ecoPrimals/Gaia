# swarmVine — Wave 157a Vertebrate Evolution Handoff

**Primal**: swarmVine (#16)
**Date**: August 09, 2026
**Wave**: 157a VERTEBRATE EVOLUTION
**Gate**: eastGate
**Status**: Self-audit complete, production-ready for mesh integration

---

## Summary

swarmVine underwent full vertebrate evolution: deep audit, structural refactoring,
async dispatch evolution, zero-copy improvements, riboCipher centralization,
comprehensive test coverage expansion, and self-audit conformance testing.

All CI gates pass. RPC surface verified against `capability_registry.toml`.
No bearDog silent-health anti-pattern. Unknown methods return `-32601`.

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 39 | 124 |
| Coverage (line) | 43% | 82% |
| Clippy warnings | 55+ errors | 0 |
| Formatting | 20+ diffs | Clean |
| Doc warnings | 22 | 0 |
| Max file size | 669 LOC | 678 LOC (all < 1000) |
| Total codebase | ~3,800 LOC | 5,519 LOC (with tests) |

## Architectural Evolution

### Async dispatch (P1)
- Eliminated all 5 `block_in_place`/`block_on` calls in dispatch.rs
- `handle_request` is now `pub(crate) async fn`
- Gossip handlers called with `.await` directly

### Gossip engine (P1)
- Nonce dedup: `Vec<String>` O(n) → `HashSet` + `VecDeque` O(1) with FIFO eviction
- Nonce generation: `DefaultHasher` → timestamp nanos + pid + atomic counter
- Forward queue data loss fixed: peers discovered before draining

### Zero-copy (P1)
- Batch gossip payload shared via `Arc<str>` across peer spawns
- `handle_gossip_spread` uses reference iteration, per-entry clone only for deser

### Deduplication (P1)
- `TransportEndpoint` — single definition in core, removed server duplicate
- `discover_songbird_socket` — shared via `pub(crate)` from announce.rs
- Primal name canonicalized to `"swarmVine"` everywhere

### riboCipher centralization
- Created `swarmvine_core::ribocipher` module with named constants
- All raw `0xEC`/`0xED`/`0xEE` bytes replaced across server crate

### Hardcoding → Discovery
- All socket paths use `env_keys` constants with runtime fallbacks
- Gossip port discoverable via `GOSSIP_PORT` env var
- Negotiation timeout configurable via `NEGOTIATE_TIMEOUT_MS`

### tarpc evolution
- Service trait includes gossip methods (inject, query, status, peers)
- Handler implements all 8 methods (4 baseline + 4 gossip)
- `capabilities_list` returns full method surface
- G65 single-socket limitation documented (tarpc 0.37 constraint)

### Self-audit (Wave 157a)
- `self_audit_rpc_surface_matches_registry` test added
- Verifies 1:1 match between `METHODS` array and `capability_registry.toml`
- Verifies every declared method returns a `result` (not error)
- Verifies unknown methods return `-32601` (no silent fallback)

## RPC Surface (12 methods, all verified)

```
health.liveness     health.readiness    health.check
capabilities.list   primal.announce     btsp.negotiate
gossip.spread       gossip.inject       gossip.query
gossip.subscribe    gossip.status       gossip.peers
```

## Integration Readiness

| Integration | Status |
|-------------|--------|
| songBird gossip delegation | Ready — tower domain via `gossip.inject` |
| nestGate/loamSpine data gossip | Ready — data domain operational |
| toadStool/coralReef compute gossip | Ready — compute domain operational |
| vine-bat loop (skunkBat) | Operational — graceful degradation |
| biomeOS Neural API announce | Implemented — fire-and-forget |
| songBird ipc.register | Implemented — capability routing |

## Tracked Debt

| Item | Priority | Notes |
|------|----------|-------|
| Coverage 82% → 90% | P2 | main.rs, announce.rs need integration tests |
| G65 single-socket tarpc | P3 | Blocked on tarpc 0.38+ |
| gossip.subscribe streaming | P4 | Returns honest Phase 4 status |
| BTSP null cipher | P3 | Awaiting ecosystem convergence |

## Upstream Dependencies

None on other primals. swarmVine is self-contained — discovers peers at runtime.

## Files Changed

All source files modified (26 files). Key additions:
- `crates/swarmvine-core/src/ribocipher.rs` — centralized transport signal constants
- `LICENSE` — AGPL-3.0-or-later (was missing)

---

*swarmVine — vine spreads, bat validates. 124 tests, 82% coverage, 12/12 methods verified.*
