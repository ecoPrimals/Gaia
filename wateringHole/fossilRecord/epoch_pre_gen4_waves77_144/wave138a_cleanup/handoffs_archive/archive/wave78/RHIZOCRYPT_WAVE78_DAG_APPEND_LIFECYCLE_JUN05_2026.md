# rhizoCrypt — Wave 78 Handoff: Mesh-Trust DAG Append + Lifecycle Wiring

**Date**: 2026-06-05
**Version**: 0.14.2
**Wave**: 78
**Tests**: 1,683 (`--all-features`), 0 clippy, 0 unsafe
**Max prod file**: 678L (`rhizocrypt/mod.rs`)

## Summary

Completed all three P2 local wiring items from the Wave 78 parity blurb:

### 1. Mesh-trust session auto-provision

`spawn_mesh_poller()` on `RhizoCrypt` creates a `SessionType::Custom { domain: "mesh-trust" }`
session lazily — provisioned on the first polled trust event, reused for all subsequent events.
No session created if no events arrive.

### 2. DAG vertex append

Each `MeshTrustEvent` from bearDog's `auth.events.poll` is:
1. Deserialized from JSON-RPC response
2. Converted to `EventType` via `into_event_type()`
3. Built into a `Vertex` via `VertexBuilder`
4. Appended to the mesh-trust session via `append_vertex()`

Full provenance chain: bearDog fires → rhizoCrypt polls → DAG records.

### 3. Service-layer lifecycle wiring

`spawn_mesh_poller()` is called from the service layer immediately after
`Arc::new(primal)`, running as a background task alongside `spawn_gc_sweeper()`.
Non-fatal — poll errors are logged and retried at `MESH_POLL_INTERVAL` (30s).
If no signing provider is discovered, the poller logs and retries until one appears.

### 4. Registry hygiene

Moved `capability_registry.toml` from project root to `config/` for ecosystem
convention consistency (biomeOS, petalTongue, sweetGrass pattern). Updated all
references in README, CONTEXT, validation-summary, and constants.

## Key Files

- `crates/rhizo-crypt-core/src/rhizocrypt/mod.rs` — `spawn_mesh_poller()` (678L total)
- `crates/rhizocrypt-service/src/lib.rs` — lifecycle wiring
- `config/capability_registry.toml` — moved from root

## Provenance Chain Status

```
bearDog (auth.trust_issuer fires → AuthEventBus records)
  → rhizoCrypt MeshEventListener polls auth.events.poll [Wave 77e]
  → deserializes MeshTrustEvent from JSON-RPC response
  → maps to EventType::TrustIssuerRegistered via into_event_type()
  → auto-provisions mesh-trust session [Wave 78] ← NEW
  → appends Vertex to DAG session [Wave 78] ← NEW
  → sweetGrass can now weave attribution braids from mesh events
```

## Remaining Work

- **sweetGrass integration test**: Confirm attribution braid creation from mesh-trust DAG events
- **loamSpine**: Verify trust entry recording from mesh events via provenance chain
- **Live mesh test**: eastGate cross-gate `capability.call` test requires NUCLEUS + Songbird on strandGate

## Ecosystem Parity

rhizoCrypt now meets Wave 78 standard:
- Zero clippy (pedantic + nursery)
- Zero `#[allow]` in production
- `config/capability_registry.toml` ✓ (convention path)
- `forbid(unsafe_code)` ✓
- `METHOD_CATALOG` SSOT ✓
- Wire Standard L2+ ✓
