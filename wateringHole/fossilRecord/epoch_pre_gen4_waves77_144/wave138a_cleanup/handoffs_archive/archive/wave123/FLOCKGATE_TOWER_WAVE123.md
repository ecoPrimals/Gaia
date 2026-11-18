# flockGate Tower Team — Wave 123 Dispatch

**Date**: Jun 22, 2026 | **From**: eastGate overwatch
**Gate**: flockGate (.6, WAN via golgi relay) | **Composition**: 13/13 NUCLEUS
**Primals**: BearDog, Songbird, SkunkBat

---

## Objective: BTSP Cross-Gate Trust (S1 → S2)

The mesh is connected (5 nodes, WireGuard proven). Your job is to make it **trusted** — gates should validate each other's identity cryptographically, not just via SSH keys.

---

## P1 Tasks

### 1. TrustedIssuerRegistry Deployment

BearDog w135 shipped the `TrustedIssuerRegistry` with multi-issuer `auth.verify_ionic`. Deploy it across the mesh:

```
auth.trust_issuer   — register a remote gate's public key
auth.trusted_issuers — list all trusted issuers
auth.public_key     — expose this gate's public key
auth.verify_ionic   — verify token from any trusted issuer
```

**Action**: On flockGate, configure bearDog to accept tokens from eastGate, sporeGate, ironGate, golgi. Exchange Ed25519 public keys via `auth.trust_issuer`.

### 2. Cross-Gate Token Validation

**Test**: Issue a BTSP token on flockGate. Send it to eastGate. Verify eastGate's bearDog accepts it via `auth.verify_ionic`.

**Success criteria**: Token issued on any mesh gate validates on any other gate.

### 3. Songbird Mesh Routing

Songbird already has `mesh.capabilities_announce` (push model, w75). Validate that:
- Capabilities registered on flockGate propagate to all peers
- `mesh.init` topology-aware routing uses latency data from health probes
- Relay Phase 3 (structured token parsing + timestamp freshness) is active

### 4. SkunkBat Defense Attestation

- Validate `MethodGate` enforcement is active on all Tower primals
- Audit ring buffer captures cross-gate auth events
- Document threat detection posture for WAN-facing gate

---

## P2 Tasks

### Sovereign Transport Envelope — Phase 2: songBird Relay Activation

sporeGate issued impulse for Sovereign Transport Envelope. Phase 2 is Tower team's:
- Activate songBird relay on golgiBody-ext (outer membrane)
- Enable sovereign `.onion` feature gate in `songbird-onion-relay`
- Wire bearDog `relay.authorize` for lineage-gated access
- This gives us a sovereign relay endpoint separate from WireGuard hub identity

Reference: `impulses/active/2026-06-22T07-40_sporeGate__wave121-sovereign-transport-envelope.toml`

### sporePrint Content Evolution

- Current: 183+ tests, taxonomy audited, static via Caddy
- Next: Wire petalTongue as backend (content from NestGate, not static files)
- This enables sovereign content serving (Layer 3 sovereignty target)

---

## Context

- flockGate is the **outer membrane** in K-Derm topology — the trust boundary facing WAN
- Tower atomic (BearDog + Songbird + SkunkBat) is the immune system + transport + defense
- Phase C in the sovereignty evolution: "Tower does secure networking" as a composition
- bearDog has 14,940+ tests, zero debt — the capability is ready, deployment is the work

## Coordination

- eastGate primalSpring team will test cross-gate `capability.call` once BTSP is deployed
- sporeGate overwatch validates enrollment pattern works for new gates
- Report progress via impulse to wateringHole or push directly to Forgejo

---

*Your gate is the trust boundary. Make the mesh authenticate, not just connect.*
