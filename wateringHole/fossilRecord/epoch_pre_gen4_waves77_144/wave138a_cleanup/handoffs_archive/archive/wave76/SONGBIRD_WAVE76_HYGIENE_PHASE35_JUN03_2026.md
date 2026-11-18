# Songbird Wave 76 — Hygiene Sweep + Retry Resilience + Phase 3.5 Scaffold

**Date**: June 3, 2026  
**From**: southGate (Songbird)  
**Version**: v0.2.8-wave76  
**Commit**: `a436a7e0`

---

## Delivered

### 1. Deep Debt Hygiene Sweep (6 fixes)

| Severity | Fix | File |
|----------|-----|------|
| **High** | Broker readiness propagation — `ready_rx.await` now returns error on bind failure | `universal_broker.rs` |
| Medium | `post_jsonrpc_fire_and_forget` checks HTTP status + drains body | `mesh_handler/mod.rs` |
| Medium | Mesh read lock held too long — clone `Arc<BeaconMesh>` before iteration | `mesh_handler/mod.rs` |
| Medium | BTSP `ts` field now required on structured tokens; future-skew bound (60s) added | `virtual_relay.rs` |
| Medium | `handle_capabilities_announce` validates sender is known mesh peer | `mesh_handler/mod.rs` |
| Low | `#[must_use]` on `get_peer_capabilities` | `mesh_handler/mod.rs` |

### 2. Capability Propagation Retry Queue

Failed `mesh.capabilities_announce` deliveries queued with original payload. Retried every health cycle (~2 min). Max 3 retries per peer before dropping. Fresh announce on next `ipc.register` supersedes stale queue entries.

### 3. BTSP Phase 3.5 Scaffold (Ready for bearDog CryptoProvider)

- **`BtspSignatureVerifier` trait**: Object-safe async trait for Ed25519 verification
- **`NoopSignatureVerifier`**: Accepts all signatures (current Phase 3 behavior)
- **`VirtualRelayManager::set_signature_verifier()`**: Runtime injection point
- **Signature bytes decoded**: `BtspValidation::Valid` now carries `payload_bytes` and `signature_bytes` for the verifier
- **Integration path**: When bearDog ships `crypto.verify_signature`, implement the trait via IPC and inject at startup

---

## Metrics

- Zero clippy warnings, zero unsafe, zero hardcoding
- 13,960+ tests, 1 known pre-existing flaky (env var leakage)
- 9 files changed, 261 insertions, 38 deletions

## Next

- Phase 3.5 activation when bearDog CryptoProvider ships
- Live mesh validation with eastGate (standing ready)
- Cross-subnet TURN relay wiring (P2 — when VPS is ready)
