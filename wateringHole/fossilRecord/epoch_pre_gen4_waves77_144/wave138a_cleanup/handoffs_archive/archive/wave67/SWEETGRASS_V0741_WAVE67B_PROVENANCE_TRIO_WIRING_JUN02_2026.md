# sweetGrass v0.7.41 — Provenance Trio Wiring (Wave 67b)

**Date:** 2026-06-02
**Gate:** strandGate
**Primal:** sweetGrass v0.7.41
**LOC:** 56,018 (194 .rs files)
**Tests:** 1,565 (0 failures)
**Methods:** 39 registered capabilities

## Summary

Wired sweetGrass to accept inbound provenance events from the trio pipeline.
Three handler evolutions close the gap between "attribution sink" and
"active trio participant."

## Changes

### 1. `contribution.record_provenance` (NEW)

JSON-RPC method accepting provenance chain events from rhizoCrypt's
`ProvenanceNotifier::notify_provenance()`. Wire format:

```json
{
  "source_primal": "rhizocrypt",
  "vertices": [
    {
      "session_id": "...",
      "vertex_id": "...",
      "event_type": "dag.event.append",
      "agent": "did:key:...",
      "timestamp": 1717300000000000000
    }
  ],
  "agent_count": 1
}
```

Creates one attribution braid per vertex with agent DID, session reference,
and event type in `EcoPrimalsAttributes.niche`. Vertex timestamps preserved
in braid metadata as `vertex_timestamp`. Empty vertex list creates a
single placeholder braid.

### 2. `pipeline.attribute` (WIRED)

Previously returned empty `dehydration_merkle_root` and `commit_ref`.
Now computes:

- **`dehydration_merkle_root`**: SHA-256 hash of all braid IDs created
  during the pipeline attribution pass.
- **`commit_ref`**: `sweetgrass:pipeline:{session_id}:{root_prefix}`
  where root_prefix is the first 16 hex chars of the merkle root.

Full outbound rhizoCrypt/loamSpine calls deferred to v0.8.0 (requires
integration crate trio clients).

### 3. `anchoring.verify` (EVOLVED)

Upgraded from stub returning `"pending_integration"` to actual braid
inspection:

- Retrieves full braid from store (was: existence check only)
- Inspects `witness.is_signed()` for tower-level Ed25519 signature
- Returns `"signed"` or `"unanchored"` with `data_hash` and
  `generated_at_time`
- Includes witness object when present

Full loamSpine ledger verification deferred to v0.8.0.

### 4. `braid.create` Compatibility Verified

Confirmed wire-compatible with projectNUCLEUS `trio.rs`:
- Accepts `data_hash`, `name`, `mime_type`, `description`, `size`
- Flattened convenience fields merge into `BraidMetadata`
- `source_session` and `source_merkle_root` fields available

## Ecosystem State After This Wave

| Item | Status |
|------|--------|
| Phase 0 southGate P0 fixes | DONE (code-complete, documented) |
| Phase 1 mesh validation | IN PROGRESS (blocked: binary refresh) |
| sweetGrass trio inbound | READY (braid.create + record_provenance) |
| sweetGrass trio outbound | v0.8.0 (needs integration crate clients) |
| strandGate gate deploy | Blocked on Phase 1 mesh proof |
| Songbird on strandGate | Needs `plasmidbin install songbird` |

## Next (v0.8.0 targets)

- Outbound JSON-RPC clients for rhizoCrypt (`dag.merkle.root`) and
  loamSpine (`ledger.commit`) in the integration crate
- `anchoring.verify` cross-primal ledger proof via loamSpine
- `pipeline.attribute` end-to-end with live trio partners
- sled→redb awareness for Songbird/BearDog local deployment
