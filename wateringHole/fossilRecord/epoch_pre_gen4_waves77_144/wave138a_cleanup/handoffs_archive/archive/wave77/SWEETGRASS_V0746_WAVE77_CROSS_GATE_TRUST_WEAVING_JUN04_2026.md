# sweetGrass v0.7.46 — Cross-Gate Trust Weaving

**Date**: 2026-06-04  
**Gate**: strandGate  
**Wave**: 77  
**FRAGO**: wave76-parity-sprint-provenance (evolved)

---

## What Changed

### `trust.event` JSON-RPC Method (NEW)

Auto-weaves a cross-gate braid from a trust event. When bearDog on Gate A
trusts Gate B's key, calling `trust.event` produces a fully-populated
PROV-O braid with:

- Activity type mapped from `CrossGateTrustEvent` (all 7 variants)
- `wasAttributedTo` = `origin_agent`, with `target_agent` via `actedOnBehalfOf`
- Gateway-tier `Witness` from Ed25519 signature (when provided)
- `source_gate` and `cross_gate` metadata
- `application/vnd.ecoprimals.trust-event` MIME type
- Deterministic content hash from `(origin_gate, target_gate, event, agent)`

**Wire format:**

```json
{
  "jsonrpc": "2.0",
  "method": "trust.event",
  "params": {
    "cross_gate": {
      "origin_gate": "ironGate",
      "target_gate": "strandGate",
      "trust_event": "key_exchange",
      "origin_agent": "did:key:z6MkIronAgent",
      "target_agent": "did:key:z6MkStrandAgent",
      "family_id": "my-family"
    },
    "signature": "<base64 Ed25519 signature>",
    "timestamp": 1717500000000000000
  },
  "id": 1
}
```

### Core Layer Enhancements

- `CrossGateTrustEvent::to_activity_type()` — maps all 7 events to `ActivityType`
- `CrossGateAttribution::gate_context()` — `"ironGate->strandGate"` format
- `CrossGateAttribution::to_activity(timestamp)` — builds full PROV-O Activity
- `CrossGateAttribution::content_hash_seed()` — deterministic hash seed
- `MeshJoin` + `MeshLeave` added to `ActivityType` enum
- `BraidBuilder::source_gate()` and `BraidBuilder::witness()` setters
- `identity::MIME_TRUST_EVENT` constant

### Dead Config Cleanup

- `StorageBackend::Oxigraph` / `::File` → `::Redb` / `::NestGate`
- Removed dead `QueryConfig.graphql/sparql/full_text_search` flags

---

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.46 |
| Tests | 1,607 (0 failures) |
| Methods | 40 (was 39) |
| Source files | 209 (60,377 LOC) |
| Clippy | 0 warnings |
| Max file | 783 lines |

---

## Forward Targets

- **BTSP env var snapshots** — `resolve_security_socket()` and
  `resolve_family_seed()` read env on every handshake; snapshot to AppState
- **`BraidContext::default()` env reads** — `ECOP_VOCAB_URI` /
  `ECOP_BASE_URI` read on every braid create; snapshot at startup
- **`btsp/server.rs`** (759 lines) and **`btsp/transport.rs`** (763 lines)
  approaching threshold; candidate for module extraction

---

## Key Files

- `crates/sweet-grass-core/src/braid/cross_gate.rs` — weaving logic
- `crates/sweet-grass-service/src/handlers/jsonrpc/trust.rs` — handler
- `crates/sweet-grass-service/src/handlers/jsonrpc/registry.rs` — dispatch
- `crates/sweet-grass-core/src/activity/mod.rs` — MeshJoin/MeshLeave
- `crates/sweet-grass-core/src/braid/builder.rs` — source_gate/witness
