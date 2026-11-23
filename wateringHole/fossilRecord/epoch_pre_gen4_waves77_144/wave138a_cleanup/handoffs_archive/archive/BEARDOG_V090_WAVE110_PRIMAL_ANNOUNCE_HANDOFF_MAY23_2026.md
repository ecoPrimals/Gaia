<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 110: `primal.announce` Self-Announcement

**Date**: May 23, 2026
**Primal**: bearDog
**Version**: 0.9.0
**Resolves**: primalSpring Wave 43 bearDog item (HIGH priority)

---

## Summary

bearDog now sends a `primal.announce` JSON-RPC call to biomeOS on server
startup, registering itself as a tower-tier crypto/security provider.
This enables biomeOS v3.69+ routing weights and utilization tracking.

---

## What Changed

### New: `send_primal_announce` (beardog-ipc)

Push-style `primal.announce` via UDS JSON-RPC to biomeOS. Non-fatal on
failure (standalone operation preserved).

### Announce Payload (biomeOS v3.69+ schema)

```json
{
  "primal": "beardog-<node_id>",
  "version": "0.9.0",
  "socket": "/run/user/1000/biomeos/beardog.sock",
  "capabilities": ["crypto", "security"],
  "methods": ["crypto.sign_ed25519", "crypto.verify_ed25519", "...45 total"],
  "signal_tiers": ["tower"],
  "cost_hints": { "crypto": 5.0, "security": 10.0 },
  "latency_estimates": { "crypto": 2, "security": 15 },
  "signed_attestation": { "schema_version": 2, "algorithm": "ed25519", "..." }
}
```

### Method Categories (45 canonical names)

| Category | Count | Examples |
|----------|-------|---------|
| Ed25519/ECDSA | 4 | `crypto.sign_ed25519`, `crypto.verify_ecdsa_secp256r1` |
| Key exchange | 4 | `crypto.x25519_*`, `crypto.ecdh_p256_*` |
| AEAD | 4 | `crypto.chacha20_poly1305_*`, `crypto.aes256_gcm_*` |
| Hash/HMAC/KDF | 10 | `crypto.blake3_hash`, `crypto.sha256`, `crypto.hkdf_sha256` |
| Ionic bonds | 7 | `crypto.ionic_bond.propose/accept/seal/verify/verify_proposal/revoke/list` |
| Contracts | 5 | `crypto.contract.propose/countersign/verify`, `crypto.sign_contract` |
| Semantic | 6 | `crypto.sign`, `crypto.verify`, `crypto.encrypt`, `crypto.hash` |
| Security | 5 | `security.evaluate`, `security.lineage`, `security.verify_consent` |

### Wiring Points

Both server entry points send announce:

1. `crates/beardog-cli/src/handlers/server.rs` — CLI `beardog server` path
2. `crates/beardog-tunnel/src/modes/server.rs` — tunnel `register_with_discovery_service` path

### Backward Compatibility

Existing `capability.register` calls (legacy Neural API) remain active.
`primal.announce` is additive — biomeOS processes whichever arrives first.

---

## Validation

After bearDog announces with biomeOS running:

```bash
echo '{"jsonrpc":"2.0","method":"neural_api.routing_weights","params":{},"id":1}' | \
  socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/neural-api-ecoPrimal.sock
```

Should show bearDog entries for `crypto.*` with non-default affinity.

---

## Quality Gates

| Gate | Result |
|------|--------|
| `cargo fmt` | Clean |
| `cargo clippy --workspace -- -D warnings` | 0 warnings |
| `cargo test --workspace` | All pass, 0 failures |

---

## Files Modified

| File | Change |
|------|--------|
| `crates/beardog-ipc/src/neural_registration.rs` | Added `send_primal_announce`, `beardog_announce_method_names` |
| `crates/beardog-ipc/src/lib.rs` | Export new functions |
| `crates/beardog-ipc/src/neural_registration_comprehensive_tests.rs` | 3 new tests |
| `crates/beardog-cli/src/handlers/server.rs` | Wire announce after neural registration |
| `crates/beardog-tunnel/src/modes/server.rs` | Wire announce in discovery service path |
| `STATUS.md` | Wave 110 entry |
| `CHANGELOG.md` | Wave 110 entry |
