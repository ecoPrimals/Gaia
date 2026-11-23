# BearDog v0.9.0 — Wave 135: Cross-Gate Trust + Covalent Mesh Security

**Date**: Jun 3, 2026  
**Owner**: southGate  
**Primal**: bearDog v0.9.0-wave135  
**Status**: P0 delivered, P1 design documented  

---

## Summary

Implements the cross-gate trust model for the covalent mesh. When gates
form a mesh, each gate's bearDog can now verify ionic tokens issued by
remote gates — defining the trust boundary for the multicellular organism.

## What Was Delivered (P0)

### 1. Cross-Gate Trust Architecture

**Trust anchor**: Per-gate Ed25519 identity key, verified via trusted issuer registry.

```
                        ┌──────────────────┐
                        │   Family Seed    │
                        │  (BTSP transport)│
                        └────────┬─────────┘
                                 │ proves family membership
                                 ▼
           ┌──────────────────────────────────────────┐
           │         BTSP Handshake (Layer 1)         │
           │  HMAC-SHA256 challenge + X25519 session   │
           └────────────────────┬─────────────────────┘
                                │ after handshake succeeds
                                ▼
           ┌──────────────────────────────────────────┐
           │     Key Exchange: auth.public_key        │
           │  Gate B sends Ed25519 VerifyingKey → A   │
           └────────────────────┬─────────────────────┘
                                │
                                ▼
           ┌──────────────────────────────────────────┐
           │     Registration: auth.trust_issuer      │
           │  Gate A registers Gate B's key + DID     │
           │  in TrustedIssuerRegistry                │
           └────────────────────┬─────────────────────┘
                                │
                                ▼
           ┌──────────────────────────────────────────┐
           │  Verification: auth.verify_ionic         │
           │  Token from B → try local key (fail)     │
           │  → try registry (Gate B's key) → ✓       │
           │  Returns: verification_source="remote"   │
           └──────────────────────────────────────────┘
```

**Three trust establishment methods**:
1. **`family_seed`** — After BTSP handshake proves same family, gates exchange public keys
2. **`contract_exchange`** — Cross-family trust via `crypto.contract.propose/countersign`
3. **`manual`** — Operator-provisioned key registration

### 2. New RPC Methods

| Method | Purpose |
|--------|---------|
| `auth.trust_issuer` | Register a remote gate's Ed25519 key as trusted |
| `auth.trusted_issuers` | List all registered trusted issuers (audit) |

### 3. Token Enrichment (v2)

`IonicTokenPayload` now carries optional cross-gate identity claims:
- `gate_id` — Issuing gate's `NODE_ID`
- `family_id` — Issuing gate's `FAMILY_ID`

Both are `serde(default, skip_serializing_if)` for backward compatibility.

### 4. Multi-Issuer Verification

`auth.verify_ionic` now tries keys in priority order:
1. **Local key** (fast path for same-gate tokens)
2. **Trusted issuer registry** (remote gates)
3. **Ad-hoc `issuer_key` param** (one-shot verification)

Response includes `verification_source` ("local" | "remote" | "adhoc")
and remote issuer metadata (`issuer_gate_id`, `issuer_family_id`, `trust_method`).

### 5. Test Coverage

- 8 new tests in `trusted_issuer_registry`:
  - `local_token_verifies_without_registry`
  - `remote_token_fails_without_registry`
  - `remote_token_verifies_with_registered_issuer`
  - `adhoc_key_verifies_unregistered_issuer`
  - `register_is_idempotent`
  - `list_returns_all_issuers` / `remove_issuer`
  - `cross_gate_roundtrip_full_flow` (token issued on gate A, verified on gate B)

---

## Design: BTSP Relay Integrity (P1)

### Current State
Songbird relay Phase 2 validates `_btsp_session` as non-empty but does
not cryptographically verify token content. bearDog's BTSP Phase 2
(handshake enforcement) is complete.

### Design for Full Verification

```
Client → Songbird Relay → bearDog

Phase 3 (relay integrity):
1. Client connects to Songbird relay with BTSP session token
2. Relay passes token opaquely (CANNOT read, modify, or forge)
3. bearDog's MethodGate verifies the bearer token:
   - Ed25519 signature check against local + trusted issuer keys
   - Scope and expiry validation
4. Audit log emitted for relay-path authenticated requests
```

**Security invariants**:
- Relay sees encrypted BTSP frames — token content is inside the encrypted channel
- Relay cannot forge tokens (no access to Ed25519 signing keys)
- Relay cannot read tokens (ChaCha20-Poly1305 or Phase 3 encrypted)
- Relay path is identified via `ConnectionOrigin::Remote` — audit log
  records `origin=remote` for all relay-mediated requests

**Implementation path**:
1. Songbird Phase 3: Replace stub `_btsp_session` check with `auth.verify_ionic`
   call to destination bearDog (or local Ed25519 verification using cached key)
2. bearDog: Add `relay_audit_log` emission in `MethodGate::check()` when
   `ConnectionOrigin::Remote` + valid token (structured log with source IP,
   issuer DID, scope, session_id)
3. bearDog: Wire `ConnectionOrigin::Remote` into gate policy as an optional
   stricter enforcement tier

**Key question for primalSpring**: Should relay-mediated requests require
BTSP transport encryption (Phase 3 channel), or is bearer token over
cleartext JSON-RPC acceptable for local-subnet relay?

---

## Design: Family Seed Cross-Enrollment Protocol (P1)

### Scenario: westGate Joining the Mesh

When a new gate (westGate) wants to join an existing covalent mesh
(southGate + eastGate), what is the enrollment protocol?

### Option A: Shared Family Seed (Recommended for v1)

```
Operator Action:
1. Copy FAMILY_SEED from existing gate to westGate
2. Set same FAMILY_ID on westGate
3. Start westGate's bearDog

Automatic Trust Establishment:
4. westGate → BTSP handshake with existing gates → proves family membership
5. Gates exchange auth.public_key → register via auth.trust_issuer
6. Cross-gate ionic token verification is now operational
```

**Pros**: Simple, deterministic, uses existing BTSP infrastructure.  
**Cons**: Single shared secret — compromise of one gate compromises all.  
**Mitigation**: GENETIC_LINEAGE_EVOLUTION_SPEC describes evolution to
derived device seeds (HKDF from master seed + device identity).

### Option B: Key Exchange via Contract (For Cross-Family)

```
1. westGate operator initiates: crypto.contract.propose
   - Terms: "mesh_enrollment" + westGate identity + public key
   - Signed by westGate's Ed25519 key
2. Existing gate operator approves: crypto.contract.countersign
   - Counter-signed with existing gate's key
   - Includes existing gate's public key
3. Both gates call auth.trust_issuer with the other's public key
4. Contract serves as audit trail for trust establishment
```

**When to use**: Cross-family enrollment, or when operator wants
explicit bilateral trust instead of implicit shared-seed trust.

### Is `family_id` Sufficient?

**No — `family_id` alone is NOT sufficient for trust.**

Currently `family_id` is a string label with no cryptographic binding
to `FAMILY_SEED`. The federation handler uses string equality only.

**Recommended evolution**:
1. Bind `family_id` to seed via `crypto.seed_fingerprint` (BLAKE3 of
   HMAC-SHA256(seed, "seed-fingerprint-v1"))
2. Token `family_id` claim should include seed fingerprint
3. Trust establishment should verify seed fingerprint matches

This is tracked for a future wave when multi-family mesh is needed.

---

## The Dark Forest Security Model — Trust Boundary Definition

### Question: When gates mesh, what is the trust boundary?

**Answer: The trust boundary is the family seed.**

| Boundary | Trust Level | Verification |
|----------|-------------|--------------|
| Same family, same gate | Full (covalent) | Local Ed25519 key |
| Same family, different gate | Sibling (covalent) | BTSP handshake + registered issuer key |
| Different family, contracted | Ionic (scoped) | Contract exchange + registered key |
| Unknown | None (Dark Forest) | Rejected |

Each gate remains sovereign — it controls its own `TrustedIssuerRegistry`
and decides which remote gates to trust. The mesh is opt-in, not automatic.

bearDog is the immune system: it defines who is "self" (family) and who
is "other" (Dark Forest), using cryptographic proofs rather than
infrastructure assumptions.

---

## Files Changed

| File | Change |
|------|--------|
| `crates/beardog-tunnel/src/trusted_issuer_registry.rs` | **NEW** — Cross-gate trusted issuer registry |
| `crates/beardog-tunnel/src/ionic_token.rs` | Added `gate_id`, `family_id` to payload; `GateIdentity` struct; `issue_ionic_token_with_gate()` |
| `crates/beardog-tunnel/src/ionic_token_handlers.rs` | Extended `verify_ionic` for multi-issuer; added `trust_issuer`, `trusted_issuers` handlers |
| `crates/beardog-tunnel/src/method_gate.rs` | Added `TrustedIssuerRegistry` to gate; updated `check()` for cross-gate tokens |
| `crates/beardog-tunnel/src/method_gate_tests.rs` | Updated for new gate-handled methods |
| `crates/beardog-tunnel/src/lib.rs` | Registered `trusted_issuer_registry` module |
| `capability_registry.toml` | Added `auth.trust_issuer`, `auth.trusted_issuers` |
| `CHANGELOG.md` | Wave 135 entry |

## Quality Gates

- `cargo fmt` — ✅
- `cargo clippy --workspace -- -D warnings` — ✅
- `cargo test --workspace` — ✅ (169 test suites, 0 failures)

## Coordination

- **Downstream**: primalSpring cross-gate security scenarios
- **Downstream**: Songbird relay Phase 3 (full BTSP token verification)
- **Downstream**: All gates depend on bearDog trust chain
- **Reference**: This handoff defines the trust model for gen5 paper
- **S4 auth monitoring**: Passive, ends ~Jun 9
