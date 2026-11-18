# rhizoCrypt — Wave 77e: MeshEventListener Polling Wired (RC-POLL-01)

**Date**: Jun 4, 2026
**Version**: 0.14.1
**Gate**: strandGate
**Resolves**: RC-POLL-01

## Summary

bearDog Wave 139 delivered `auth.events.poll` (Option C from our FRAGO
`wave76c-beardog-auth-events-subscribe`). rhizoCrypt's `MeshEventListener`
now polls bearDog for trust events, completing the provenance chain.

## What Was Delivered

### Polling Path (end-to-end)

```
bearDog (auth.trust_issuer fires → AuthEventBus records)
  → rhizoCrypt MeshEventListener::poll_events()
    → sends auth.events.poll JSON-RPC with since_timestamp
    → deserializes Vec<MeshTrustEvent> from response
    → record_event() maps to EventType mesh variants
    → event_log buffered for DAG session append
```

### Background Poller

`spawn_poller()` runs a `tokio::spawn` background task that polls
every 30s (`MESH_POLL_INTERVAL`). Non-fatal — failures logged and retried.
Incremental via `last_poll_timestamp` tracking.

### Previous Waves (cumulative)

- **Wave 76**: Cross-gate mesh event types (5 EventType variants, MeshLeaveReason)
- **Wave 76b**: MeshEventListener scaffold + IPC trigger path design
- **Wave 76c**: clippy guard migration (29 files)
- **Wave 77d**: lifecycle extraction (mod.rs 701→579L), mesh.events.record handler,
  niche catalog wiring (37 methods, 7 domains), CONSUMED_CAPABILITIES update

## Test Results

- **1,683 tests passing** (all features), 0 failures
- **0 clippy warnings** (including `--tests`)
- **186 `.rs` files**, ~55,506 lines
- **Max production file**: 686L (`service.rs`)
- **Zero unsafe**, zero TODO/FIXME

## Provenance Chain Status

| Hop | Status |
|-----|--------|
| bearDog `auth.trust_issuer` → `AuthEventBus` | ACTIVE (Wave 139) |
| bearDog `auth.events.poll` → rhizoCrypt | WIRED (this wave) |
| rhizoCrypt `MeshEventListener` → event_log | WIRED |
| rhizoCrypt → DAG session append | DESIGNED (needs mesh-trust session) |
| rhizoCrypt → loamSpine ledger | READY (ProvenanceNotifier) |
| loamSpine → sweetGrass attribution | READY (sweetGrass v0.7.45) |

## Remaining Local Work

1. **Mesh-trust session auto-provision**: Create dedicated session for mesh
   events on first poll result (or config-driven `RHIZOCRYPT_MESH_SESSION_ID`).
2. **DAG append integration**: Wire `poll_events()` results into
   `RhizoCrypt::append_vertex()` via the mesh-trust session.
3. **`spawn_poller()` in lifecycle**: Call from `PrimalLifecycle::start()`
   when endpoint is Connected (currently manual via `Arc<MeshEventListener>`).

## Coordination

- bearDog FRAGO: **RESOLVED** (archived to `wave77/`)
- sweetGrass: Can proceed with attribution braid testing once DAG append is live
- loamSpine: Trust entry recording ready — waiting on live mesh events
