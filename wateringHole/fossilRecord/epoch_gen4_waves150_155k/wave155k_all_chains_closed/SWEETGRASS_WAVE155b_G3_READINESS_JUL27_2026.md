# SweetGrass — Wave 155b: G3 Readiness AAR

**Date**: Jul 28, 2026  
**Wave**: 155d  
**Version**: v0.7.64  
**Commit**: `28092a8`  
**Status**: **READY — `CertificateRef` type shipped, waiting on upstream trio IPC wiring**

---

## Current State

sweetGrass has shipped all prerequisites for Nest Atomic Phase 3
(cross-gate attribution braids). No code debt, no blockers internal to
sweetGrass. G3 convergence gap #2 (`CertificateId` on braids) is resolved.

| Capability | Status | Detail |
|------------|--------|--------|
| BTSP ClientHello | SHIPPED (Wave 151b) | `CryptoDelegate` auto-handshakes when `BEARDOG_UDS_REQUIRE_BTSP=1` |
| Cross-gate attribution types | SHIPPED | `CrossGateAttribution`, 7 trust events, `source_gate` on braids |
| **CertificateRef structured type** | **SHIPPED (Wave 155d)** | `id`, `issuing_gate`, `sealed`, `minting_authority`, `content_hash`. Backward-compat deser from plain strings |
| **CertificateRef::cross_gate()** | **SHIPPED (Wave 155d)** | Constructor for cross-gate attestation braids with gate + authority |
| Cross-gate query filter | SHIPPED | `QueryFilter::with_source_gate()` for gate-scoped provenance |
| PROV-O activity wiring | SHIPPED | `CrossGateAttribution::to_activity()` maps trust events to W3C PROV |
| Anchor signing (bearDog) | SHIPPED | `braid.anchor` signs via CryptoDelegate → bearDog `crypto.sign` |
| TransportEndpoint dispatch | SHIPPED (Wave 142b) | Platform-agnostic UDS/TCP/mesh transport |

---

## G3 Integration Pattern — What sweetGrass Needs From Upstream

### From rhizoCrypt (federate verification)

sweetGrass receives cross-gate braids with `source_gate` and
`CrossGateAttribution` metadata. To **verify** these braids came from an
authenticated gate (not spoofed), we need:

```
Method: provenance.verify_gate_origin
Params: {
  "source_gate": "<gate_name>",
  "origin_agent": "<did:key:...>",
  "signature": "<base64>",
  "content_hash": "<sha256:...>"
}
Result: {
  "verified": true/false,
  "connection_origin": "btsp_authenticated" | "unknown",
  "trust_chain": [...]
}
```

**Pattern**: sweetGrass calls rhizoCrypt at braid-create time (when
`cross_gate` metadata is present) to verify the origin gate's BTSP
authentication status. If rhizoCrypt confirms
`ConnectionOrigin::BtspAuthenticated`, the braid gets a higher witness tier.

**Discovery**: Via `PROVENANCE_PROVIDER_SOCKET` or capability symlink
`provenance.sock` in `$BIOMEOS_SOCKET_DIR`.

### From loamSpine (ledger anchoring)

After a braid is created and signed, sweetGrass anchors it to loamSpine's
append-only DAG ledger:

```
Method: ledger.append
Params: {
  "entry_type": "braid_anchor",
  "content_hash": "<sha256:...>",
  "witness": { ... },
  "source_gate": "<gate_name>"
}
Result: {
  "entry_id": "<dag_node_id>",
  "sequence": <u64>,
  "sealed": true/false
}
```

**Pattern**: After `braid.anchor` succeeds (bearDog signs), sweetGrass
appends the anchor proof to loamSpine's ledger. This creates the
immutable cross-gate provenance chain.

### From nestGate (CAS content verification)

Cross-gate braids reference content by hash. To verify content exists
and is retrievable across gates:

```
Method: cas.verify
Params: {
  "content_hash": "<sha256:...>",
  "expected_size": <u64>
}
Result: {
  "exists": true/false,
  "verified": true/false,
  "stored_at": ["flockGate", "ironGate"]
}
```

**Pattern**: Before accepting a cross-gate braid, verify the referenced
content actually exists in the CAS. Prevents phantom attribution.

---

## Implementation Plan (v0.8.0)

When upstream APIs stabilize:

1. **Add `trio_client` module** — capability-based discovery of
   rhizoCrypt, loamSpine, nestGate (via `resolve_capability_endpoint`)
2. **Wire `braid.create` hook** — when `cross_gate` is present, call
   `provenance.verify_gate_origin` before accepting
3. **Wire `braid.anchor` hook** — after signing, call `ledger.append`
4. **Wire verification** — `cas.verify` for content existence
5. **Graceful degradation** — if trio primals unavailable, braids still
   create (unsigned/unverified), flagged as `"verification": "pending"`

---

## Verification (current)

```
cargo clippy --all-features --all-targets -- -D warnings   OK (0 warnings)
cargo test --all-features                                   OK (1,618 tests)
cargo check --target x86_64-pc-windows-gnu                  OK
cargo fmt --all -- --check                                  OK
cargo deny check                                            OK
```

---

## For Upstream Teams

| Team | What sweetGrass Needs | Priority |
|------|----------------------|----------|
| **rhizoCrypt** | `provenance.verify_gate_origin` JSON-RPC method (or equivalent) returning `ConnectionOrigin` status for a given source gate + agent | P1 for G3 |
| **loamSpine** | `ledger.append` JSON-RPC method accepting braid anchor proofs | P1 for G3 |
| **nestGate** | `cas.verify` JSON-RPC method for content existence check | P2 for G3 |
| **primalSpring** | E2E scenario: cross-gate braid create → verify → anchor → ledger | P2 |

sweetGrass will consume these via standard capability-based discovery
(`resolve_capability_endpoint`) and BTSP-authenticated transport. No
compile-time coupling. Wire methods when trio APIs ship.
