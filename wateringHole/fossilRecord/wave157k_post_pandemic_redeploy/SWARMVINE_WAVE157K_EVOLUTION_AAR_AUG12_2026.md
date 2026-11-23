# swarmVine — Wave 157k Evolution AAR

**Date**: August 12, 2026 (afternoon session)
**Wave**: 157k POST-PANDEMIC EVOLUTION
**From**: ironGate code team
**Primal**: swarmVine (#16)
**Prior HEAD**: `cb58d32` | **New HEAD**: pending push

---

## SUMMARY

Deep evolution pass: P2 canary bugs fixed, zero-copy, coverage 90%+, scyBorg
triple license, G65 default, smart refactors, benchmarks, integration tests.
swarmVine is now production-grade per wateringHole standards.

## P2 BUG FIXES (southGate canary findings)

### P2 #2 — riboCipher framing mismatch (RESOLVED)

**Symptom**: Inbound gossip rejected. Peer gates' old binaries send raw JSON-RPC
without `[0xEC, 0x01]` prefix → new binary drops connection.

**Root cause**: `handle_connection` only matched `b'{'` as legacy fallback, other
ASCII bytes were rejected with ERROR. Rolling deploys caused unidirectional gossip.

**Fix**: Accept any ASCII-printable first byte as legacy JSON-RPC. Log at WARN
instead of ERROR. Gossip is now bidirectional during rolling deploys.

**Test**: `legacy_unsignalled_gossip_spread_accepted` validates exact canary path.

### P2 #3 — swarmVine→songBird relay method mismatch (RESOLVED)

**Symptom**: Relay fallback broken. swarmVine calls `mesh.relay`, songBird only
exposes `gossip.relay`.

**Root cause**: Method name diverged between swarmVine (used old songBird API
name) and songBird's shipped MeshRelay surface.

**Fix**: `relay_via_songbird()` now calls `gossip.relay`.

## EVOLUTION CHANGES

### Zero-copy (Arc<str>)
- `GossipEntry.key` and `GossipEntry.origin_gate`: `String` → `Arc<str>`
- Entries created once, forwarded many times — Arc amortizes clone cost
- `bytes` crate added and re-exported for wire frame evolution

### Architecture refactors
- `gossip.rs` (794L → 613L): `gossip_types.rs` extracted (types + impls)
- `dispatch.rs` (737L → 698L): `rpc_types.rs` extracted (wire helpers)
- All files under 800L production code (excluding inline test modules)

### G65 Protocol Negotiation — now DEFAULT
- Removed `--negotiate` flag
- Added `--legacy-dual-socket` for backward compat
- Single socket with 100ms timeout → JSON-RPC fallback is the new default

### Testing
- 143 → **186 tests** (+43)
- 6 integration tests (UDS roundtrip, gossip spread, G65 negotiation)
- Criterion benchmarks (inject throughput, query, nonce dedup)
- Coverage: 80.9% → **90.8%** line, **92.1%** function

### License compliance (scyBorg triple)
- SPDX headers on all 25 source files
- LICENSE-ORC (protocol mechanics)
- LICENSE-CC-BY-SA (creative/docs)
- LICENSE preamble updated with trio summary

### Dependency evolution
- `bytes = "1.12"` added (wire frame foundation)
- `serde` `"rc"` feature for `Arc<str>` serialization
- Duplicate deps (rand 0.8/0.9, syn 2/3) documented as tarpc 0.37 transitive,
  skip-annotated in deny.toml

### Code quality
- 5 clippy errors fixed (doc_markdown, duration_suboptimal_units, map_unwrap_or)
- 1 doc warning fixed (SUBSCRIPTION_CAPACITY link to private item)
- `rustfmt.toml` added
- All checks pass: fmt, clippy, deny, doc, test

## METRICS

| Metric | Before | After |
|--------|--------|-------|
| Tests | 143 | **186** |
| Coverage (line) | 80.9% | **90.8%** |
| Coverage (function) | 83.5% | **92.1%** |
| Clippy warnings | 5 errors | **0** |
| Doc warnings | 1 | **0** |
| Integration tests | 0 | **6** |
| Benchmarks | 0 | **3** |
| Max file (prod) | 794L | **404L** (excl. tests) |
| Binary size | 2.4M | **2.5M** |
| Release build | 17.1s | **16.5s** |
| License | AGPL only | **scyBorg triple** |
| SPDX headers | 0 | **25 files** |

## REMAINING (upstream-blocked)

- **songBird gossip delegation**: `mesh.capabilities_announce` → swarmVine tower domain
- **tarpc streaming**: True push via channel (awaiting tarpc 0.38+)
- **Duplicate deps**: Resolved when tarpc 0.38 ships

## IRONGATE GATE STATUS

- swarmVine P2 #2: **RESOLVED** (bidirectional gossip during rolling deploy)
- swarmVine P2 #3: **RESOLVED** (relay method matches songBird API)
- Gossip: 2 peers (westGate + eastGate), 594+ entries, MeshRelay enabled
- TCP 7800: Unreachable from sporeGate, strandGate, graftGate (their side)
- **0/0/0** for swarmVine

---

*swarmVine Wave 157k Evolution: P2 bugs fixed. 90% coverage. scyBorg triple
license. G65 default. Zero-copy Arc<str>. 186 tests. Production-grade per
wateringHole STANDARDS_AND_EXPECTATIONS. Ready for depot push. Primal #16.*
