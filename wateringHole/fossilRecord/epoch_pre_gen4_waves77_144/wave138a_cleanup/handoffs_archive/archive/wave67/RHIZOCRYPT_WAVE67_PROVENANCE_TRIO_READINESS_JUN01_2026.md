# rhizoCrypt — Wave 67 strandGate Impulse Ack + Provenance Trio Readiness

**Date**: 2026-06-01
**Wave**: 67
**Impulse**: `2026-06-01T13-32-eastGate-wave67-strandgate-provenance-compute-gate-deploy`
**Status**: Acknowledged — stadial-current, wire fix applied

---

## Impulse Response

rhizoCrypt acknowledges strandGate assignment as provenance trio + compute trio gate.
Gate deployment planned after Phase 1 mesh validation (3+ gates proven on LAN).

**Sync confirmation**: wateringHole pull received `GLACIAL_CUTOVER_PLAN.md` +
`GATE_TEAM_COORDINATION_MATRIX.md` + strandGate impulse via temporal cascade.
Sync chain validated.

---

## Wire Fix Applied (v0.14.0 → v0.14.1)

**Bug**: `PermanentStorageClient` used underscore-separated method names
(`"commit"`, `"verify_commit"`, `"get_commit"`, `"checkout_slice"`, `"resolve_slice"`)
that do not match LoamSpine's native JSON-RPC methods
(`commit.session`, `commit.verify`, `commit.get`, `slice.checkout`, `slice.resolve`).

**Impact**: Provenance trio wiring (`content.put` → DAG + LoamSpine ledger) would
fail on the dehydration commit path when LoamSpine is discovered at runtime.

**Fix**: All 5 method names corrected and centralized in `permanent.rs::wire`
constants module. Aligned with LoamSpine's method negotiation protocol.

**Bug 2**: `ProvenanceNotifier.connect()` was never called in production — all
push notifications (`contribution.record_session`, `record_dehydration`,
`record_provenance`) were silent no-ops.

**Fix**: `connect()` now called during `PrimalLifecycle::start()` with graceful
failure. `notify_session_commit()` hooked to the dehydration commit path.

**Validation**: 1,654 tests passing, 0 clippy warnings.

---

## Provenance Trio Readiness Assessment

### Track 1: content.put → rhizoCrypt DAG + LoamSpine Ledger

| Component | Status | Notes |
|-----------|--------|-------|
| DAG ingest (`dag.event.append`) | Ready | 36 JSON-RPC methods, provenance aliases wired |
| Hash interop (`parse_hash32`) | Ready | Hex + byte array dual-format acceptance |
| `PermanentStorageClient` wire | **Fixed** (v0.14.1) | Now aligned with LoamSpine `commit.session` |
| `LoamSpineHttpClient` | Ready | Full JSON-RPC 2.0 client with method negotiation |
| Dehydration pipeline | Ready | `dehydrate → commit → permanent` lifecycle complete |
| Capability discovery | Ready | Env-based + Songbird; no hardcoded endpoints |

**Remaining**: Unify dehydration path to route through `LoamSpineHttpClient`/`PermanentStorageProvider` trait. Enable `http-clients` feature in service build for deployed gate.

### Track 2: sweetGrass Braid Integration

| Component | Status | Notes |
|-----------|--------|-------|
| `provenance.create_braid` | Manifest only | In CONSUMED_CAPABILITIES; no client method yet |
| `ProvenanceNotifier` | **Fixed** (v0.14.1) | Connected at startup; push on dehydration + session commit |
| `ProvenanceClient` | Query only | Read ops wired; write (braid create) not yet |

**Remaining**: Implement `ProvenanceClient::create_braid` + post-append hook.

### Track 3: Cross-Gate Compute Dispatch

| Component | Status | Notes |
|-----------|--------|-------|
| `ComputeClient` discovery | Scaffold | Connect + `is_available()` only |
| Dispatch methods | Not wired | No submit/job API on client or handler |

**Remaining**: Depends on biomeOS `capability.call` (southGate P0 blocker).

---

## Gate Metrics

| Metric | Value |
|--------|-------|
| Version | 0.14.1 |
| Tests | 1,654 |
| Clippy warnings | 0 |
| `.rs` files | 175 |
| Lines | ~54,300 |
| METHOD_CATALOG | 36 (31 stable, 5 evolving) |
| Max prod file | 698 lines |
| Deep debt markers | 0 |

---

## Blocked On

- **Phase 1 mesh validation** — southGate Songbird socket fix + biomeOS `capability.call`
- strandGate hardware deployment (Dual EPYC 7452, 256GB ECC) after mesh proven

## No Action Required Until

Gate deployment. rhizoCrypt is stadial-current and wire-ready for provenance trio.
