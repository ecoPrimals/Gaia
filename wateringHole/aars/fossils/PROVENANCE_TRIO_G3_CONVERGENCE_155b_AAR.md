# AAR: Provenance Trio G3 Convergence — loamSpine + rhizoCrypt + sweetGrass

**Date**: 2026-07-27 | **Wave**: 155b | **From**: loamSpine team (eastGate)
**Scope**: Nest Atomic Phase 0 — where the three data-layer primals stand and
what they need from each other.

---

## CONTEXT

The Provenance Trio (rhizoCrypt lineage, loamSpine ledger, sweetGrass attribution)
forms the memory layer of the ecosystem. Nest Atomic Phase 0 (G3) requires all
three to interoperate over BTSP-authenticated IPC for cross-gate provenance chains.

This AAR documents what each primal shipped in Wave 155b, what's working,
what's not yet wired, and what the convergence path looks like.

---

## WHAT SHIPPED (Wave 155b)

### loamSpine (commit `29307d1`)

| Delivery | Impact |
|----------|--------|
| `verify_certificate` semantic checks | `MintEntryValid` + `OwnerConsistent` — certificates now verified beyond storage existence |
| `certificate.verify` JSON-RPC | Verification exposed on wire for cross-primal queries |
| `certificate.lifecycle` JSON-RPC | Ordered lifecycle events accessible over IPC |
| `MintInfo::with_authority` builder | Delegated minting path for Nest Atomic authority model |
| Full lifecycle E2E with seal | mint → loan → return → transfer → seal → reject validated |
| 6 G3 discovery helpers pre-wired | `find_by_capability`, `negotiate_protocol`, `resolve_primal_socket_with_env` |
| `CertificateManager` marked legacy | `LoamSpineService` is the canonical API surface |
| BTSP handshake move semantics | 4 fewer String clones per connection |
| BTSP env priority fix | `BTSP_STRICT_MODE` now canonical over `BEARDOG_UDS_REQUIRE_BTSP` |
| Clone dedup in loan/sublend/return | Structural allocation reduction |
| mDNS shutdown tracing | Silent `let _ =` evolved to traced errors |

**Test count**: 1,736 (zero clippy warnings, zero failures)

### rhizoCrypt (commit `d4972b0`)

| Delivery | Impact |
|----------|--------|
| `ConnectionOrigin::BtspAuthenticated` | DAG operations now auth-aware — BTSP-authenticated callers get different trust level |
| Federate hardening | Source gate provenance on inbound DAG sync, signature verification |
| +10 tests | 1,893 total |

### sweetGrass

| Delivery | Impact |
|----------|--------|
| — | No 155b evolution shipped for G3. Attribution braids exist but aren't wired for cross-gate provenance |

---

## WHAT'S WORKING

1. **Individual primal APIs are mature**. Each primal's internal data model is
   production-quality with comprehensive test coverage.

2. **BTSP is universal**. All three primals have BTSP handshake — they can
   authenticate to bearDog/Tower and each other.

3. **IPC contract alignment**. loamSpine's `certificate.verify` and
   `certificate.lifecycle` return structured JSON-RPC responses that rhizoCrypt
   and sweetGrass can consume. Entry types are `Serialize`/`Deserialize`.

4. **Discovery infrastructure exists**. `find_by_capability("certificate-authority")`,
   `find_by_capability("lineage")`, `find_by_capability("attribution")` — all
   pre-wired in loamSpine's discovery module, tested, just need callers.

---

## WHAT'S NOT YET WIRED (Convergence Gaps)

### Gap 1: Cross-Primal Certificate Provenance

**Need**: When rhizoCrypt tracks a DAG node's provenance, it should be able to
call `loamSpine.certificate.verify` to validate the certificate backing that
node's lineage claim.

**Current state**: rhizoCrypt has the `BtspAuthenticated` origin type but doesn't
call loamSpine's RPC methods. The IPC path exists (both use `TransportEndpoint`)
but no caller code yet.

**Owner**: rhizoCrypt team
**Requires from loamSpine**: `certificate.verify` RPC (shipped)

### Gap 2: Attribution Braid ↔ Certificate Linkage

**Need**: sweetGrass braids should reference loamSpine certificate IDs for
attribution provenance. When a braid is committed, it should include the
certificate IDs it attests to.

**Current state**: sweetGrass has braid types but no `CertificateId` field.
loamSpine's `ProvenanceSource` trait has `"attributed-to"` relationship type
but it's populated from sweetGrass mock data, not live braids.

**Owner**: sweetGrass team + loamSpine coordination
**Requires from loamSpine**: `certificate.lifecycle` RPC (shipped), stable `CertificateId` type

### Gap 3: MintingAuthority Delegation

**Need**: An external authority (resolved via capability discovery) should be
able to delegate minting rights. loamSpine validates the delegation chain before
accepting a mint request with `MintingAuthority`.

**Current state**: `MintingAuthority` struct exists with `authority: Did` and
`authorization_entry: EntryHash`. `MintInfo::with_authority()` builder shipped.
No validation logic in `mint_certificate()` yet — authority is always `None`.

**Owner**: loamSpine team
**Requires from rhizoCrypt**: Trust anchor validation for authority DIDs
**Requires from sweetGrass**: Attribution attestation for delegated authority

### Gap 4: Cross-Gate Provenance Chain

**Need**: When certificates exist on multiple gates (after federation sync),
the provenance chain must track which gate minted, transferred, and verified.

**Current state**: rhizoCrypt's federate hardening adds source gate provenance.
loamSpine's `CertificateLocation` tracks spine/entry but not gate origin.
No cross-gate verification flow exists.

**Owner**: All three + cellMembrane (mesh coordination)

---

## CONVERGENCE PATH

```
Phase 0 (NOW — each primal evolves independently):
  loamSpine: MintingAuthority validation logic
  rhizoCrypt: Call loamSpine.certificate.verify from DAG auth
  sweetGrass: Add CertificateId to braid attestation type

Phase 1 (Wire — IPC callers):
  rhizoCrypt ←→ loamSpine: certificate verification on DAG commit
  sweetGrass ←→ loamSpine: attribution braid references certificates
  Discovery helpers: wire find_by_capability callers

Phase 2 (Cross-gate):
  loamSpine.certificate.verify over mesh relay
  rhizoCrypt federate carries certificate provenance
  sweetGrass braids include cross-gate attestation chain

Phase 3 (rootPulse):
  biomeOS orchestrates Provenance Trio as unified data layer
  rootPulse composition replaces waterFall for content-addressed lineage
```

---

## ACTION ITEMS

| # | Owner | Action | Priority |
|---|-------|--------|----------|
| 1 | **sweetGrass** | Add `CertificateId` field to braid attestation types | P1 |
| 2 | **sweetGrass** | Implement BTSP `ClientHello` (reference: songBird/loamSpine) | P1 |
| 3 | **rhizoCrypt** | Wire `loamSpine.certificate.verify` call from DAG auth path | P1 |
| 4 | **rhizoCrypt** | Add `CertificateId` to `ProvenanceNode` metadata | P2 |
| 5 | **loamSpine** | Implement `MintingAuthority` validation in `mint_certificate` | P1 |
| 6 | **loamSpine** | Wire `find_by_capability` callers for Nest Atomic IPC | P1 |
| 7 | **primalSpring** | Add G3 guidestone scenario: delegated mint + verify | P1 |
| 8 | **All three** | Cross-gate provenance chain integration test | P2 |

---

## POSITIVE FINDINGS

- The Provenance Trio architecture is sound. Each primal handles a clear,
  non-overlapping concern: loamSpine = ledger, rhizoCrypt = lineage DAG,
  sweetGrass = attribution braids. No overlap, clean seams.

- BTSP standardization (13/13) means the auth layer is solved. The remaining
  work is purely application-level IPC wiring.

- loamSpine's discovery helpers (`find_by_capability`, `negotiate_protocol`)
  are tested and G3-labeled — they're ready to call, not ready to write.

- The `ProvenanceSource` trait in loamSpine already defines the relationship
  vocabulary (`anchored-by`, `attributed-to`, `committed-from`, `chain-anchored`,
  `certified-by`) — sweetGrass and rhizoCrypt can adopt these directly.

---

*Wave 155b. Three primals, one data layer. The primitives exist. The wire
contracts are stable. The remaining work is callers, not APIs. Phase 0
concludes when each primal can call the other two's verify/commit endpoints
over BTSP-authenticated IPC.*
