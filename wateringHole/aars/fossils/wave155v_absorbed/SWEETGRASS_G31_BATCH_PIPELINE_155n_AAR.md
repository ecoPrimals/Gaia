# sweetGrass — G31 Batch Provenance Pipeline — Wave 155n AAR

**Date**: Aug 3, 2026 | **Wave**: 155n | **From**: sweetGrass team (eastGate)
**Version**: v0.8.0 | **Tests**: 1,644 | **Commit**: `906bfcc`

---

## WHAT SHIPPED

**G31 batch provenance pipeline** — coordinated cross-primal batch operations
for 10× faster bulk ingestion (targeting 38 datasets / 220K PDB structures).

| Method | Purpose | Wire Format |
|--------|---------|-------------|
| `braid.batch_create` | Bulk braid creation with bounded concurrency | `{"braids": [{data_hash, mime_type, size, ...}], "concurrency": 10}` |
| `braid.batch_commit` | Pipelined loamSpine commit forwarding | `{"braid_ids": ["urn:braid:..."], "spine_id": "default", "concurrency": 10}` |

### Performance Target

- **Before**: ~30ms/object (sequential `braid.create` + `braid.commit`)
- **After**: ~3ms/object (batch store + pipelined IPC)
- **Enabler**: `put_batch`/`get_batch` on store layer + bounded concurrency

### Also Shipped

- **`BraidId::to_uuid()`** — deterministic UUID v5 derivation for hash-based
  IDs. Namespace: `Uuid::new_v5(NAMESPACE_URL, "urn:ecoPrimals:braid")`.
  Resolves P2 braid_id→UUID mismatch.
- Dispatch table: 40 → **42 methods**.

---

## WIRE FORMAT

### `braid.batch_create`

```json
{
  "jsonrpc": "2.0",
  "method": "braid.batch_create",
  "params": {
    "braids": [
      { "data_hash": "sha256:...", "mime_type": "chemical/x-pdb", "size": 12345 },
      { "data_hash": "sha256:...", "mime_type": "chemical/x-pdb", "size": 67890, "name": "1ABC.pdb" }
    ],
    "concurrency": 10
  },
  "id": 1
}
```

Response:
```json
{
  "result": {
    "created": 2,
    "total": 2,
    "errors": 0,
    "results": [
      { "id": "urn:braid:sha256:...", "status": "created" },
      { "id": "urn:braid:sha256:...", "status": "created" }
    ]
  }
}
```

### `braid.batch_commit`

```json
{
  "jsonrpc": "2.0",
  "method": "braid.batch_commit",
  "params": {
    "braid_ids": ["urn:braid:sha256:...", "urn:braid:sha256:..."],
    "spine_id": "default",
    "concurrency": 10
  },
  "id": 2
}
```

Response (with loamSpine):
```json
{
  "result": {
    "committed": 2,
    "total": 2,
    "results": [
      { "braid_id": "urn:braid:sha256:...", "status": "committed", "ledger_commit": {...} },
      { "braid_id": "urn:braid:sha256:...", "status": "committed", "ledger_commit": {...} }
    ]
  }
}
```

---

## COORDINATION PATTERN (for rhizoCrypt + loamSpine)

The G31 batch provenance pipeline across the trio:

```
1. rhizoCrypt: dag.batch_append(entries)     → DAG hashes
2. sweetGrass: braid.batch_create(specs)     → braid IDs
3. sweetGrass: braid.batch_commit(braid_ids) → loamSpine ledger refs
4. loamSpine:  (receives pipelined braid.commit calls)
```

Each primal's batch RPC is independently usable. The orchestrating caller
(biomeOS signal graph or tideGlass agent) coordinates the pipeline sequence.

---

## VALIDATION

```
cargo check --all-features              ✓
cargo clippy --all-features --all-targets  ✓ (0 warnings)
cargo test --all-features               ✓ (1,644 passed, 0 failed)
cargo check --target x86_64-pc-windows-gnu  ✓ (cross-arch clean)
```

---

## REMAINING FOR G31 FULL E2E

- [ ] loamSpine batch acceptance (does loamSpine handle rapid-fire `braid.commit`?)
- [ ] rhizoCrypt `dag.batch_append` coordination test
- [ ] biomeOS signal graph wiring (`nest.ingest_dataset` → batch pipeline)
- [ ] Performance benchmark: target <5ms/object at 220K scale on westGate ZFS

---

*sweetGrass G31 batch pipeline shipped. 42 methods. 1,644 tests. Ready for
coordinated trio bulk ingestion once biomeOS orchestrates the pipeline.*
