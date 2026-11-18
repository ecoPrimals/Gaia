# sweetGrass v0.7.50 — Wave 79 Handoff

**Date**: 2026-06-05
**From**: strandGate (sweetGrass)
**Wave**: 79

---

## What Landed

### Attribution Braid Provenance Chain Tests

rhizoCrypt DAG append + lifecycle wiring is DELIVERED. sweetGrass is
unblocked. Three new scenario tests validate the full mesh event
attribution pipeline:

1. **`test_provenance_chain_beardog_to_sweetgrass`** — End-to-end:
   Ed25519-signed trust event from bearDog (southGate) creates an
   attribution braid with correct `wasAttributedTo`, `on_behalf_of`
   delegation to rhizoCrypt, gateway-tier witness, cross-gate metadata,
   and roundtrip retrieval via `braid.get`.

2. **`test_all_mesh_event_types_weave_braids`** — Exhaustive validation
   of all 7 `CrossGateTrustEvent` variants against their PROV-O activity
   type mappings and MIME type consistency.

3. **`test_trust_event_provenance_query_by_gate`** — Gate-filtered
   provenance queries via `QueryFilter.source_gate` and
   `QueryFilter.mime_type` returning correct braids.

### Transport Compliance Audit

- `--socket` CLI injection works natively (5-tier UDS fallback)
- TCP is opt-in via `--port` / `SWEETGRASS_PORT`
- No `0.0.0.0` default bind
- All `TcpListener::bind` and `UnixListener::bind` calls receive injected
  addresses from parameters, not hardcoded values
- sweetGrass is Phase 2 (Songbird-routed IPC) ready per
  `wave79-transport-evolution-capability-routing` FRAGO

### Deep Debt Sweep

Zero hits across all 14 audit categories:
- No TODO/FIXME/HACK
- No unwrap/expect in production code
- No println/eprintln
- No Box<dyn Error>
- No std::sync::Mutex
- No async_trait
- No hardcoded primal names (except self-knowledge)

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.50 |
| Tests | 1,605+ |
| Coverage | 91.7% |
| Clippy | Zero warnings (pedantic + nursery) |
| Deep debt | DH-1 clean |

## Next Evolution Path

Attribution braid testing against **live** mesh events is the next step.
Low priority until VPS binary refresh lands. When live:
- bearDog emits `auth.events.subscribe` → rhizoCrypt records DAG entry →
  rhizoCrypt calls `trust.event` on sweetGrass → braid woven with full
  provenance chain
- The 3 new scenario tests validate the wire format compatibility

## Dependencies

- rhizoCrypt DAG append: **DELIVERED** (unblocked)
- VPS binary refresh: **PENDING** (blocks live testing)
- Transport Phase 2 (Songbird-routed IPC): **ACKNOWLEDGED** — sweetGrass
  is ready, awaiting songBird `ipc.resolve` evolution
