# bearDog — Wave 140: BD-TRUST-01 — Auto Trust Seeding

**Date**: Jun 4, 2026
**Version**: 0.9.0
**Wave**: 140
**Tests**: 15,004 passing (169 suites, 0 failures)
**Methods**: 226 dispatchable (217 registry + 9 pre-dispatch gate)

---

## Delivered — BD-TRUST-01

### Problem

During Wave 77d live cross-gate mesh proof, `auth.trust_issuer` was called manually.
Every gate join required operator intervention to register trust issuers. This doesn't
scale for automated mesh join via Songbird `mesh.init`.

### Solution: `auth.exchange_trust`

New gate-handled RPC method that combines key exchange + trust registration in a single
call. Requires BTSP-authenticated channel (proving family seed membership) OR a valid
ionic token.

**Flow (zero operator intervention):**
```
1. Gate A → Songbird mesh.init → connects to Gate B
2. BTSP handshake proves shared FAMILY_SEED membership
3. Gate A calls auth.exchange_trust on Gate B:
   - Provides Gate A's Ed25519 public key
   - Gate B auto-registers Gate A as trusted issuer
   - Gate B returns its own Ed25519 public key + DID
4. Gate A receives Gate B's key → calls auth.exchange_trust locally
5. Bidirectional trust established. auth.verify_ionic works cross-gate.
```

### Implementation Details

**`CallerContext.btsp_family_verified`** — new boolean field, set `true` after
successful BTSP handshake in both TCP and UDS code paths.

**`auth.exchange_trust` request:**
```json
{
  "jsonrpc": "2.0",
  "method": "auth.exchange_trust",
  "params": {
    "public_key": "<base64 Ed25519 public key>",
    "gate_id": "remote-gate",
    "family_id": "my-family"
  },
  "id": 1
}
```

**Response:**
```json
{
  "registered": true,
  "remote_did": "did:key:z6Mk...",
  "trust_method": "family_seed",
  "total_trusted_issuers": 1,
  "local_public_key": "<base64>",
  "local_did": "did:key:z6Mk...",
  "local_gate_id": "beardog"
}
```

**Security:**
- Requires `btsp_family_verified == true` OR `validated_claims.is_some()` (ionic token)
- BTSP channels use `TrustMethod::FamilySeed`; ionic token channels use `ContractExchange`
- DID is auto-derived from public key if not provided, preventing DID/key mismatch
- Emits `TrustIssuerRegistered` event (captured by `auth.events.poll` for rhizoCrypt)

### Files Changed

| File | Change |
|------|--------|
| `method_gate.rs` | Added `btsp_family_verified` to `CallerContext`, `auth.exchange_trust` to gate dispatch |
| `ionic_token_handlers.rs` | New `handle_auth_exchange_trust` function |
| `connection_handlers.rs` | Set `btsp_family_verified = true` after UDS BTSP handshake |
| `tcp_ipc/server/connection.rs` | Set `btsp_family_verified = true` after TCP BTSP handshake |
| `method_gate_tests.rs` | 5 new tests + updated struct literals |

---

## Songbird Integration Guide

After BTSP handshake succeeds in Songbird's mesh federation:

```rust
// After BTSP handshake, call auth.exchange_trust on remote bearDog
let response = rpc.call("auth.exchange_trust", json!({
    "public_key": local_beardog_public_key_b64,
    "gate_id": local_node_id,
    "family_id": local_family_id,
}));

// Remote gate's key is in the response — register it locally
let remote_key = response["local_public_key"];
let remote_did = response["local_did"];
local_rpc.call("auth.exchange_trust", json!({
    "public_key": remote_key,
}));
// Bidirectional trust established!
```

---

## Remaining Work

| Item | Priority | Notes |
|------|----------|-------|
| S4 auth graduation | P0 (passive) | ~Jun 9 |
| Songbird wire `auth.exchange_trust` in mesh.init | P1 | Completes auto-join |
| SB-TLS-02: Phase 3.5 `NoopSignatureVerifier` → `crypto.verify.ed25519` | P1 | Interface delivered W138 |
| RC-POLL-01: rhizoCrypt poll `auth.events.poll` | P2 | Interface delivered W139 |

---

## Quality Gates

- `cargo fmt` — clean
- `cargo clippy --workspace -- -D warnings` — 0 warnings
- `cargo test --workspace` — 15,004 passed, 0 failed, 169 suites
