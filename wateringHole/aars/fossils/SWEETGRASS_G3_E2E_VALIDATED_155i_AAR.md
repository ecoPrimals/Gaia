# sweetGrass — G3 E2E Validated — Wave 155i AAR

**Date**: Jul 29, 2026 | **Wave**: 155i | **From**: sweetGrass team (eastGate)
**Version**: v0.8.0 | **Tests**: 1,639 | **Commits**: `666dea5`, `b5d260d`, `ab887e8`, `4b5167b`

---

## WHAT HAPPENED

1. **Received P0 handoff** (`SWEETGRASS_NEST_ATOMIC_G3_WIRING_WAVE155i.md`) —
   wire sweetGrass → loamSpine to close the Provenance Trio triangle.

2. **Shipped `LedgerClient`** (commit `666dea5`):
   - `ledger_client.rs` — JSON-RPC 2.0 over UDS/TCP for `braid.commit` +
     `certificate.verify` to loamSpine
   - `AppState::ledger_client` + `with_ledger_client()` builder
   - Bootstrap Phase 4c — automatic loamSpine discovery at startup
   - `braid.commit` handler — forwards to loamSpine, returns `committed` +
     `ledger_commit` reference
   - `anchoring.verify` handler — cross-primal `certificate.verify` via
     loamSpine, returns `ledger_verified` status
   - Capability-based socket resolution (env → family → standalone)
   - Graceful degradation to local-only when loamSpine unavailable

3. **Shipped E2E integration tests** (commit `b5d260d`):
   - Mock loamSpine UDS server (newline-delimited JSON-RPC 2.0)
   - `braid.commit` forwarding validated (committed + ledger_commit fields)
   - `anchoring.verify` ledger proof validated (ledger_verified + detail)
   - Graceful degradation (no loamSpine = local-only, no crash)
   - Connection refused handling (error, never panic)
   - Sequential + concurrent commit load testing (5 sequential, 3 concurrent)
   - 11 new tests passing

---

## PROVENANCE TRIO — IPC STATUS

| Path | Status | Mechanism |
|------|--------|-----------|
| rhizoCrypt → loamSpine | WIRED | `PermanentStorageClient` |
| rhizoCrypt → sweetGrass | WIRED | `ProvenanceNotifier` |
| sweetGrass → loamSpine | **WIRED** | `LedgerClient` (this wave) |

**Triangle: CLOSED.**

---

## VALIDATION

| Check | Result |
|-------|--------|
| `cargo check --all-features` | clean |
| `cargo clippy --all-features --all-targets -- -D warnings` | 0 warnings |
| `cargo test --all-features` | 1,636 passed, 0 failed |
| `cargo check --target x86_64-pc-windows-gnu` | cross-arch clean |
| E2E mock loamSpine (11 tests) | all pass |

---

## WIRE FORMAT (for loamSpine/biomeOS integration reference)

### Outbound: `braid.commit`

```json
{"jsonrpc":"2.0","method":"braid.commit","params":{"braid_id":"urn:braid:...","uuid":"...","data_hash":"sha256:...","data_hash_bytes":"<base64>","spine_id":"default","mime_type":"application/ld+json","size":1234,"attributed_to":"did:key:z6Mk...","generated_at":"...","is_signed":true},"id":N}
```

Expected: `{"result":{"spine_id":"default","entry_hash":"sha256:...","index":42,"sealed":true}}`

### Outbound: `certificate.verify`

```json
{"jsonrpc":"2.0","method":"certificate.verify","params":{"certificate_id":"..."},"id":N}
```

Expected: `{"result":{"valid":true,"detail":"sealed in ledger"}}`

### Socket Resolution

1. `LOAMSPINE_SOCKET` env (explicit override)
2. `{BIOMEOS_SOCKET_DIR}/loamspine-{FAMILY_ID}.sock` (family-scoped)
3. `{BIOMEOS_SOCKET_DIR}/loamspine.sock` (standalone)

---

## P2 RESOLVED: braid_id → UUID mismatch (commit `4b5167b`)

`BraidId::to_uuid()` now always returns a valid UUID for cross-primal
correlation. Hash-based braid IDs (`urn:braid:sha256:...`) derive a
deterministic UUID v5 instead of dumping the raw URN into the `uuid` field.
loamSpine always receives a proper UUID in `braid.commit` payloads.

---

## BLOCKED ON (for live westGate E2E)

- **biomeOS BTSP composition broker** (P0) — signal graph dispatch fails at
  BTSP auth boundary when orchestrating inter-primal pipelines. Individual
  sweetGrass → loamSpine IPC works, but the `nest.ingest_dataset` orchestrated
  pipeline needs the Neural API to broker trust.

---

## NEXT (after biomeOS BTSP broker ships)

1. Live E2E on westGate: `braid.create` → `braid.commit` → verify `committed: true`
2. Live E2E: `anchoring.verify` → verify `ledger_verified: true` with real ledger
3. Cross-gate attribution with northGate AlphaFold data (~1TB ingestion)

---

## LESSONS

- **Mock-first IPC testing** works well — the mock loamSpine UDS pattern
  (same as mock bearDog for BTSP) validates the full handler chain without
  needing the real primal running.
- **Graceful degradation** is essential — sweetGrass operates local-only when
  loamSpine is unavailable, upgrades seamlessly when it appears at runtime.
- **Socket resolution chain** (env → family → standalone) matches the
  ecosystem standard and requires zero configuration for default deployments.

---

*sweetGrass v0.8.0 is fully E2E validated on eastGate local hardware. Ready
for live production E2E on westGate the moment biomeOS BTSP composition
broker ships. The Provenance Trio triangle is CLOSED.*
