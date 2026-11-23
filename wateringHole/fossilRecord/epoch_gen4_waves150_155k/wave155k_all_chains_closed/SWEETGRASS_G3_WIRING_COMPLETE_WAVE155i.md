# sweetGrass — G3 Wiring COMPLETE — Wave 155i

**Date**: Jul 29, 2026 | **Wave**: 155i | **From**: sweetGrass team
**Team**: sweetGrass (Provenance Trio) | **Gate**: westGate
**Status**: DONE — Provenance Trio triangle CLOSED
**Version**: v0.8.0 (commit `666dea5`)

---

## WHAT SHIPPED

| Item | Status |
|------|--------|
| `LedgerClient` module (`ledger_client.rs`) | SHIPPED |
| `AppState::ledger_client` + builder | SHIPPED |
| Bootstrap Phase 4c (resolve loamSpine) | SHIPPED |
| `braid.commit` → loamSpine forwarding | SHIPPED |
| `anchoring.verify` ledger proof | SHIPPED |
| Socket resolution chain (env/family/standalone) | SHIPPED |
| Graceful degradation (local-only without loamSpine) | SHIPPED |
| Version bump v0.7.64 → v0.8.0 | SHIPPED |

---

## IPC PATHS NOW WIRED

| IPC Path | Status |
|----------|--------|
| rhizoCrypt → loamSpine | **WIRED** (`PermanentStorageClient`) |
| rhizoCrypt → sweetGrass | **WIRED** (`ProvenanceNotifier`) |
| sweetGrass → loamSpine | **WIRED** (`LedgerClient`) ← this wave |

The Provenance Trio triangle is now **CLOSED**.

---

## WIRE FORMAT

### `braid.commit` (outbound to loamSpine)

```json
{
  "jsonrpc": "2.0",
  "method": "braid.commit",
  "params": {
    "braid_id": "urn:braid:...",
    "uuid": "...",
    "data_hash": "sha256:...",
    "data_hash_bytes": "<base64>",
    "spine_id": "default",
    "mime_type": "application/ld+json",
    "size": 1234,
    "attributed_to": "did:key:z6Mk...",
    "generated_at": "...",
    "is_signed": true
  },
  "id": 1
}
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "spine_id": "default",
    "entry_hash": "sha256:...",
    "index": 42,
    "sealed": true
  },
  "id": 1
}
```

### `certificate.verify` (outbound to loamSpine)

```json
{
  "jsonrpc": "2.0",
  "method": "certificate.verify",
  "params": { "certificate_id": "..." },
  "id": 2
}
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "result": { "valid": true, "detail": "sealed in ledger" },
  "id": 2
}
```

---

## SOCKET RESOLUTION

Resolution order for loamSpine socket:
1. `LOAMSPINE_SOCKET` env var (explicit override)
2. `{BIOMEOS_SOCKET_DIR}/loamspine-{FAMILY_ID}.sock` (family-scoped)
3. `{BIOMEOS_SOCKET_DIR}/loamspine.sock` (standalone)

---

## VALIDATION

```
cargo check --workspace --all-features     ✓
cargo clippy --all-features --all-targets   ✓ (0 warnings)
cargo test --all-features                   ✓ (1,625 passed, 0 failed)
cargo check --target x86_64-pc-windows-gnu  ✓ (cross-arch clean)
```

---

## INTEGRATION TESTING (REQUIRES loamSpine RUNNING)

When loamSpine is available on westGate:

1. `braid.create` → `braid.commit` → verify `"committed": true` in response
2. `anchoring.verify` → verify `"ledger_verified": true` in response
3. Without loamSpine: verify graceful degradation (local-only, no crash)

---

## UPSTREAM DEPENDENCIES MET

- loamSpine registry drift FIXED (commit `d79231a`) — `certificate.verify/lifecycle/history` discoverable
- sweetGrass `CertificateRef` structured type shipped in v0.7.64 — ready for loamSpine sealed certificate refs
- `TransportEndpoint` abstraction used for all IPC — TCP fallback automatic on Windows

---

*Nest Atomic can now track provenance end-to-end:
content → DAG → certificate → attribution braid.*
