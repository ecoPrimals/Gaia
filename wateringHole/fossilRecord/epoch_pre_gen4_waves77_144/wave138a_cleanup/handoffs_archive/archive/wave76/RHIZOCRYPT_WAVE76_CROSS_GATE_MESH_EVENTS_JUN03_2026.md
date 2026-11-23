# rhizoCrypt — Wave 76: Cross-Gate Mesh Event Types

**Date**: June 3, 2026
**Version**: 0.14.1 (unchanged — additive schema only)
**FRAGO**: `wave76-parity-sprint-provenance` — **ACKED**
**Gate**: strandGate

---

## Mission

Define cross-gate DAG event types for trust establishment and mesh lifecycle,
aligning with bearDog w135 `TrustedIssuerRegistry` and Ed25519 key exchange protocol.

## Schema Additions

### New `EventType` Variants (mesh domain)

5 new variants added to `EventType` enum (27→32 variants, 8 domains):

| Variant | Fields | Wire Example |
|---------|--------|-------------|
| `TrustIssuerRegistered` | `issuer_fingerprint`, `registering_gate` | `{"TrustIssuerRegistered": {"issuer_fingerprint": "a1b2c3d4...", "registering_gate": "eastGate"}}` |
| `KeyExchangeCompleted` | `local_gate`, `remote_gate`, `method` | `{"KeyExchangeCompleted": {"local_gate": "strandGate", "remote_gate": "southGate", "method": "ed25519_dh"}}` |
| `FamilyEnrollment` | `family_id`, `gate`, `primal_count` | `{"FamilyEnrollment": {"family_id": "ecoPrimal", "gate": "strandGate", "primal_count": 3}}` |
| `MeshJoin` | `gate`, `mesh_id` | `{"MeshJoin": {"gate": "ironGate", "mesh_id": "glacial-mesh-v1"}}` |
| `MeshLeave` | `gate`, `mesh_id`, `reason` | `{"MeshLeave": {"gate": "ironGate", "mesh_id": "glacial-mesh-v1", "reason": "Graceful"}}` |

### New Supporting Enum

`MeshLeaveReason`: `Graceful`, `Disconnected`, `Evicted`, `TrustRevoked`

Re-exported from `rhizo-crypt-core` lib root.

## Test Results

7 new tests added (1,663→1,670 total):

| Test | Validates |
|------|-----------|
| `test_mesh_event_types_domain` | All 5 mesh events report domain `"mesh"` |
| `test_mesh_event_types_names` | All 5 events have correct snake_case names |
| `test_mesh_event_wire_format_trust_issuer` | JSON roundtrip + field presence |
| `test_mesh_event_wire_format_key_exchange` | JSON roundtrip + externally-tagged structure |
| `test_mesh_event_wire_format_family_enrollment` | JSON roundtrip + `primal_count` numeric |
| `test_mesh_event_wire_format_mesh_join_leave` | Join roundtrip + all 4 leave reasons |
| `test_mesh_leave_reason_all_variants` | Standalone `MeshLeaveReason` roundtrip |

Existing `test_event_type_serialization_roundtrip` and `test_all_event_type_names` cover all 32 variants exhaustively.

## Hygiene

- Event tests extracted: `event.rs` 922→539L (production), `event_tests.rs` 390L
- `EVENT_TYPE_REFERENCE.md` updated: 32 variants, mesh domain documented
- All docs reconciled (README, CONTEXT, validation-summary, DEPLOYMENT_CHECKLIST)

## Files Changed

| File | Change |
|------|--------|
| `crates/rhizo-crypt-core/src/event.rs` | +5 variants, +1 enum, test extraction |
| `crates/rhizo-crypt-core/src/event_tests.rs` | NEW — extracted event tests |
| `crates/rhizo-crypt-core/src/lib.rs` | Re-export `MeshLeaveReason` |
| `specs/EVENT_TYPE_REFERENCE.md` | Mesh domain docs, 27→32 variants |
| `CHANGELOG.md` | Wave 76 entry |
| `README.md`, `CONTEXT.md` | Test count 1,663→1,670, .rs 180→181 |
| `sporeprint/validation-summary.md` | Metrics updated |
| `docs/DEPLOYMENT_CHECKLIST.md` | Test count, changelog scope |

## Integration Status

- **Not wired to bearDog**: Schemas defined + serialization tested. Ready for cross-gate
  wiring when bearDog w135 trust protocol is live on LAN mesh.
- **loamSpine + sweetGrass**: These primals should define corresponding anchor/attribution
  schemas for the same event types. Wire format is shared via `rhizo-crypt-core` types.

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 1,670 |
| Clippy | 0 warnings |
| Unsafe | 0 blocks |
| `.rs` files | 181 |
| Max prod file | 698L (rpc_integration.rs) |
| Max prod non-test | 686L (service.rs) |
