# BearDog v0.9.0 — Wave 136: Trust Hardening + Phase 3.5 Design

**Date**: Jun 3, 2026  
**Owner**: southGate  
**Primal**: bearDog v0.9.0-wave136  
**Status**: Security fixes delivered, Phase 3.5 designs ready for downstream

---

## 1. Security Fixes Delivered

### P0: `auth.trust_issuer` moved to PROTECTED

Previously classified as `PUBLIC` — any unauthenticated caller could inject
trusted issuers into the registry, enabling trust-store poisoning.

**Fix**: Removed from `PUBLIC_METHODS` list. Now requires a valid ionic token
in Enforced mode. Read-only `auth.trusted_issuers` remains public for audit.

### P0: DID ↔ Key Binding on Registration

`TrustedIssuerRegistry::register()` now validates that the supplied DID
matches the canonical `did:key:z6Mk...` derived from the Ed25519 public key.

```
register("did:key:wrong", valid_key, ...) → Err(DidKeyMismatch)
register(canonical_did, valid_key, ...)   → Ok(true)
```

### P0: `iss` Binding in Verification

`verify_with_registry()` now checks `payload.iss == registered_did` after
Ed25519 signature verification. A token with a valid signature but
mismatched `iss` claim is rejected — prevents key-confusion attacks where
an attacker registers a legitimate key under the wrong DID.

---

## 2. Relay Phase 3.5 Design — Ed25519 Token Verification for Songbird

### Context

Songbird relay Phase 2 validates `_btsp_session` as non-empty (presence check).
Phase 3 adds structured parsing + timestamp freshness. Phase 3.5 evolves to
**full Ed25519 cryptographic verification**.

### Integration Path for Songbird

Songbird has two options for verifying ionic tokens from relayed requests:

#### Option A: `CryptoProvider::call("auth.verify_ionic", ...)` (RECOMMENDED)

```json
{
  "method": "auth.verify_ionic",
  "params": {
    "token": "<ionic_token_from_relayed_request>",
    "method": "<target_method_being_relayed>"
  }
}
```

**Response:**
```json
{
  "valid": true,
  "scope_ok": true,
  "verification_source": "local",
  "claims": {
    "iss": "did:key:z6Mk...",
    "sub": "caller-identity",
    "scope": ["*"],
    "gate_id": "eastgate-node-1",
    "family_id": "family-alpha"
  }
}
```

**Pros:**
- Full token lifecycle verification (signature + expiry + scope)
- Cross-gate aware (checks local key + trusted issuer registry)
- Returns structured claims for relay audit logging
- No crypto implementation in Songbird

**Cons:**
- IPC round-trip per verification (~50-100μs via UDS)

#### Option B: `CryptoProvider::call("crypto.verify_ed25519", ...)` (LOW-LEVEL)

```json
{
  "method": "crypto.verify_ed25519",
  "params": {
    "message": "<base64(header_b64 + '.' + payload_b64)>",
    "signature": "<base64(sig_bytes)>",
    "public_key": "<base64(cached_verifying_key)>",
    "encoding": "base64"
  }
}
```

**Pros:**
- Songbird owns the verification logic (can cache keys, batch verify)
- No dependency on bearDog's token lifecycle logic

**Cons:**
- Songbird must parse ionic token format, extract signing input, manage key cache
- No automatic expiry/scope checking — must implement separately
- No cross-gate issuer registry benefit

#### Option C: Local Verification (HIGHEST PERFORMANCE)

Songbird fetches bearDog's public key once via `auth.public_key`, caches the
`VerifyingKey`, and verifies tokens in-process using `ed25519_dalek`.

```rust
// At startup (once):
let pk_response = capability_call("auth.public_key", {}).await;
let pk_bytes = base64::decode(pk_response["public_key"]).unwrap();
let vk = VerifyingKey::from_bytes(&pk_bytes).unwrap();

// Per-request:
let (header_b64, payload_b64, sig_b64) = split_token(token_str);
let signing_input = format!("{header_b64}.{payload_b64}");
let sig = Signature::from_bytes(&base64::decode(sig_b64).unwrap());
let valid = vk.verify(signing_input.as_bytes(), &sig).is_ok();
```

**Pros:**
- Zero IPC overhead per verification
- Sub-microsecond verification

**Cons:**
- Songbird takes dependency on `ed25519_dalek`
- Must implement token parsing, expiry, scope checking
- Single-key only — no cross-gate registry benefit

### Recommendation

**Phase 3.5**: Use **Option A** (`auth.verify_ionic`). It provides full
cross-gate verification, expiry/scope checks, and structured audit data
with minimal Songbird code changes. The IPC round-trip cost is acceptable
for relay-mediated requests which already incur relay latency.

**Phase 4 (future)**: Consider **Option C** for high-throughput relay paths
where sub-microsecond verification matters.

### Songbird Implementation Sketch

```rust
// In VirtualRelayManager::relay_request():
async fn verify_relay_token(&self, btsp_session: &str) -> Result<TokenClaims, RelayError> {
    let result = self.crypto_provider
        .call("auth.verify_ionic", json!({
            "token": btsp_session,
            "method": &request.method,
        }))
        .await?;

    if result["valid"] != true {
        let reason = result["reason"].as_str().unwrap_or("unknown");
        warn!(reason, "relay: BTSP token verification failed");
        return Err(RelayError::AuthenticationFailed(reason.to_owned()));
    }

    // Audit: log the verified claims for relay-path tracing
    info!(
        issuer = %result["claims"]["iss"],
        subject = %result["claims"]["sub"],
        gate_id = %result["claims"]["gate_id"],
        verification_source = %result["verification_source"],
        "relay: BTSP token verified"
    );

    Ok(TokenClaims::from_json(&result["claims"]))
}
```

### Relay Security Invariants

1. Relay CANNOT forge tokens — no access to Ed25519 signing keys
2. Relay CANNOT modify tokens — modification breaks Ed25519 signature
3. Relay CANNOT read token content in BTSP-encrypted channels
4. Relay CAN verify token validity via `auth.verify_ionic` IPC
5. All relay-path verifications produce structured audit logs

---

## 3. Family Seed Fingerprint Binding Design

### Problem

`IonicTokenPayload.family_id` is a string label (`"standalone"`, `"family-alpha"`)
with no cryptographic binding to `FAMILY_SEED`. An attacker who knows the
`family_id` string can claim family membership without knowing the seed.

### Existing Implementation

`crypto.seed_fingerprint` already exists:

```
fingerprint = hex(BLAKE3(HMAC-SHA256(family_seed, "seed-fingerprint-v1"))[0..16])
```

32 hex chars (128 bits). Deterministic per seed. Does not expose the seed.

### Design: Binding `family_id` to Seed Fingerprint

#### Phase 1: Token Claims (Wave 137)

Add optional `seed_fp` claim to `IonicTokenPayload`:

```rust
#[serde(default, skip_serializing_if = "Option::is_none")]
pub seed_fp: Option<String>,
```

When `FAMILY_SEED` is available at token issue time, compute the fingerprint
and embed it. When not available (standalone mode), omit.

#### Phase 2: Trust Registration Binding (Wave 137-138)

When registering a trusted issuer via `auth.trust_issuer`, optionally
include `seed_fingerprint`. The registry stores it in `IssuerInfo`:

```rust
pub struct IssuerInfo {
    // ... existing fields ...
    pub seed_fingerprint: Option<String>,
}
```

During `verify_with_registry()`, when a token carries `seed_fp` and the
registered issuer has a `seed_fingerprint`, verify they match:

```
if token.seed_fp != Some(issuer_info.seed_fingerprint) → reject
```

#### Phase 3: Enrollment Verification (westGate)

When westGate enrolls:
1. Operator provisions same `FAMILY_SEED` to westGate
2. westGate's bearDog computes `crypto.seed_fingerprint`
3. Existing gates verify westGate's fingerprint matches their own
4. If match → same family, register as trusted issuer via `auth.trust_issuer`
5. If mismatch → reject enrollment (wrong seed)

#### Enrollment Verification Protocol

```
westGate → eastGate: "I want to join. My fingerprint is X, my public key is Y"
eastGate:
  1. Compute own fingerprint via crypto.seed_fingerprint
  2. Compare: X == own_fingerprint?
  3. If yes → same seed → register westGate as trusted issuer
  4. If no → reject (different seed, not family)
```

#### Implementation Plan

```
Wave 137:
  - Add seed_fp claim to IonicTokenPayload
  - Add seed_fingerprint to IssuerInfo
  - Issue tokens with seed_fp when FAMILY_SEED available
  - Verify seed_fp in trust registration

Wave 138:
  - Add auth.verify_enrollment RPC for westGate onboarding
  - Combine seed fingerprint + auth.public_key exchange
  - End-to-end enrollment test
```

### API: `auth.verify_enrollment` (Proposed for Wave 138)

```json
// Request from new gate
{
  "method": "auth.verify_enrollment",
  "params": {
    "public_key": "<base64 Ed25519 key>",
    "did": "did:key:z6Mk...",
    "gate_id": "westgate-node-1",
    "family_id": "family-alpha",
    "seed_fingerprint": "a1b2c3d4e5f6..."
  }
}

// Response
{
  "enrolled": true,
  "trust_method": "family_seed",
  "fingerprint_match": true,
  "registered_did": "did:key:z6Mk..."
}
```

---

## Files Changed

| File | Change |
|------|--------|
| `trusted_issuer_registry.rs` | DID↔key validation, iss binding, `RegisterError`, `did_from_verifying_key()`, 3 new tests |
| `method_gate.rs` | `auth.trust_issuer` moved to PROTECTED |
| `ionic_token_handlers.rs` | Handler error propagation for `RegisterError` |
| `CHANGELOG.md` | Wave 136 entry |

## Quality Gates

- `cargo fmt` — ✅
- `cargo clippy --workspace -- -D warnings` — ✅
- `cargo test --workspace` — ✅ (0 failures)

## Coordination

- **Songbird**: Phase 3.5 design ready — use `auth.verify_ionic` for relay token verification
- **cellMembrane**: Phase 3.5 design applies to membrane-mediated requests too
- **Provenance trio** (rhizoCrypt/loamSpine/sweetGrass): Trust event schemas should include `RegisterError` codes
- **westGate enrollment**: Seed fingerprint binding designed, implementation in Wave 137-138
- **S4 auth monitoring**: Active, ends ~Jun 9
