# primalSpring Wave 77d: Live Cross-Gate Trust Chain — PROVEN

**Date**: 2026-06-04T18:04Z
**From**: primalSpring evolution (eastGate)
**FRAGO**: wave77-live-cross-gate-validation (DELIVERED)
**Status**: P0 COMPLETE — full end-to-end trust chain proven live

## Pass Criteria — ALL MET

| Check | Status | Evidence |
|-------|--------|----------|
| `security:cross_gate_verify` | **PASS** | `valid=true, verification_source=remote, issuer_gate_id=east-gate` |
| `security:reject_forged` | **PASS** | `valid=false, reason=malformed` |
| `discovery.peers` | **PASS** | strandGate sees eastGate as peer (quality=1.0) |
| Trust boundary enforcement | **PASS** | Token rejected when issuer key NOT in TrustedIssuerRegistry |

## Full Chain Log

```
╔═══════════════════════════════════════════════════════════════╗
║  LIVE CROSS-GATE TRUST CHAIN — FULL END-TO-END PROOF        ║
║  Token issued on eastGate, verified on strandGate            ║
║  TrustedIssuerRegistry seeded: eastGate → strandGate         ║
║  2026-06-04T18:04:15Z                                        ║
╚═══════════════════════════════════════════════════════════════╝

Step 1: Issue token on eastGate
  bearDog auth.issue_ionic → token with gate_id=tower1, family_id=eastgate

Step 2: Local verify (baseline)
  valid=True  source=local
  claims.gate_id=tower1  claims.family_id=eastgate

Step 3: Register eastGate as trusted issuer on strandGate
  auth.trust_issuer via capability.call → registered=true, total_trusted_issuers=1
  DID: did:key:z6MkgPnk2JKbGVQ8y96CjrymC3x9wEETrMMSGEDohka77SWN
  Public key: HNPCi3y8giOqfJ4xJPNDH9SbbY8qJsA/iUke3CeKFts= (Ed25519)

Step 4: Cross-gate verify (eastGate token → strandGate bearDog)
  Route: eastGate → HTTP POST → strandGate:7700/jsonrpc
         → Songbird capability.call → beardog-strandgate.sock
         → auth.verify_ionic(token, verification_source=remote)

  Response:
    valid=True
    verification_source=remote
    issuer_gate_id=east-gate
    issuer_family_id=eastgate
    trust_method=manual
    claims.gate_id=tower1
    claims.family_id=eastgate
    claims.scopes=['security.*', 'health.*', 'discovery.*']

  ✅ security:cross_gate_verify PASS
  ✅ BTSP trust chain PROVEN end-to-end

Step 5: Reject forged token
  valid=False  reason=malformed
  ✅ security:reject_forged PASS

Step 6: Mesh discovery
  discovery.peers from strandGate: east-gate @ 192.168.1.144:7700 (quality=1.0)
```

## Architecture Proven

```
eastGate (192.168.1.144)          strandGate (192.168.1.132)
┌─────────────────────┐           ┌─────────────────────┐
│ bearDog (w138)      │           │ bearDog (w138)      │
│ ├─ auth.issue_ionic │           │ ├─ auth.verify_ionic│
│ ├─ auth.public_key  │           │ ├─ auth.trust_issuer│
│ └─ UDS only         │           │ └─ UDS only         │
│                     │           │                     │
│ (Songbird blocked)  │           │ Songbird v0.2.1     │
│                     │     HTTP  │ ├─ :7700 federation │
│                     │ ────────> │ ├─ capability.call  │
│                     │           │ └─ discovery.peers  │
└─────────────────────┘           └─────────────────────┘
      Token issued                    Token verified
      gate_id=tower1                  verification_source=remote
      family_id=eastgate              issuer_gate_id=east-gate
```

## Songbird TLS Blocker (eastGate only)

Songbird v0.2.1 on eastGate cannot start because its TLS handshake
calls `capability.call` on the security provider. BearDog doesn't
implement `capability.call` — that's an orchestration method. StrandGate's
Songbird works because it was started by a different process chain.

**Impact**: eastGate cannot initiate mesh discovery (no local Songbird).
Cross-gate calls work via direct HTTP to strandGate's Songbird.

**Fix needed**: Songbird needs to call bearDog's `crypto.sign_ed25519`
directly instead of routing through `capability.call` for TLS material.

## cargo test output

```
856 passed; 0 failed; 2 ignored
clippy: zero warnings (-D warnings)

Phase 4 results (against live bearDog on eastGate):
  security:local_token_issue    PASS
  security:local_verify         PASS
  security:scopes_propagate     PASS
  security:verify_source_local  PASS
  security:verify_source_remote PASS
  security:btsp_gate_binding    PASS
  security:btsp_trust_chain     PASS
  security:reject_forged        PASS
```

## What This Proves

1. **BTSP tokens carry gate identity** — `gate_id` and `family_id` embedded in claims
2. **Cross-gate routing works** — Songbird's `capability.call` correctly routes to local providers
3. **TrustedIssuerRegistry works** — Remote tokens accepted only after explicit trust registration
4. **Trust boundaries enforced** — Tokens from unregistered issuers are rejected (`invalid_signature`)
5. **Forged tokens rejected** — Malformed payloads never pass verification
6. **Mesh discovery operational** — `discovery.peers` shows cross-gate visibility

## Next Steps

1. **Fix Songbird TLS** — Songbird must call bearDog crypto directly (not via capability.call)
2. **Automate trust seeding** — `auth.trust_issuer` should be part of mesh join handshake
3. **primal.eco DNS** — Unlocks full BLAKE3 cross-membrane comparison
4. **3-gate plasmodium** — Add ironGate to mesh, test 3-way trust propagation
