# sporeGate Production Hardening AAR — Wave 151a

**Date**: Jul 25, 2026 | **Wave**: 151a | **From**: sporeGate topology/hardware team
**To**: All teams

---

## Context

flockGate code teams shipped bearDog publication pen test (3 CRITICAL fixes)
and songBird BTSP ClientHello. With those deliveries, flockGate code teams
are CLEAR — no remaining P0/P1 code tasks. sporeGate deployed the production
hardening configuration and rebuilt binaries.

## Actions Taken

### 1. bearDog + songBird Rebuilt (x86_64 + aarch64)

| Primal | Old HEAD | New HEAD | Key Changes |
|--------|----------|----------|-------------|
| bearDog | 6a351b8 | d528ef9 | Pen test: error sanitization, auth gating, cipher floor. Android compile fixes. Unused import cleanup |
| songBird | 59c221b | 9b7eb6e | BTSP ClientHello (268L): full 4-step handshake, HMAC-SHA256 challenge-response |

Both rebuilt for x86_64-unknown-linux-musl and aarch64-unknown-linux-musl,
stripped, deployed to local depot, pushed to golgiBody.

### 2. bearDog Production Hardening

Deployed via systemd drop-in override (clean, reversible):

```
/etc/systemd/system/membrane-beardog.service.d/hardening.conf
```

| Setting | Before | After |
|---------|--------|-------|
| `BEARDOG_AUTH_MODE` | Permissive (default) | **enforced** |
| `BEARDOG_UDS_REQUIRE_BTSP` | OFF (default) | **1** (required) |

Both services restarted. bearDog confirmed enforcing BTSP — plaintext
JSON-RPC over UDS correctly rejected with WARN log.

### 3. songBird BTSP ClientHello Activated

songBird restarted with new binary containing BTSP ClientHello implementation.
Mesh-init succeeded (3 bootstrap peers + 1 LAN peer). Health endpoint returns OK.

## Observations

### Legacy UDS Connections Rejected (Expected)

Other NUCLEUS services still speak plaintext JSON-RPC over UDS:
- barracuda, loamspine, sweetgrass, squirrel, coralreef, rhizocrypt

These are correctly rejected by bearDog's BTSP enforcement. This is
defense-in-depth working as designed. These services will need BTSP
ClientHello support in their next evolution cycle.

**Impact**: These services lose access to bearDog crypto capabilities
(signing, encryption, key derivation) until they implement BTSP handshake.
For most, this is non-critical — they operate independently. For services
that depend on bearDog crypto in hot paths, the impact will surface as
degraded functionality, not crashes.

### Startup Race Condition

songBird logged one "Security provider not found" error at startup —
timing race between songBird and bearDog socket creation. Resolved
automatically via songBird's `forward_to_local_provider_with_retry`
(exponential backoff). No action needed.

## Depot Status

| Architecture | Primals | bearDog | songBird | Provenance |
|-------------|---------|---------|----------|------------|
| x86_64-unknown-linux-musl | 14 | d528ef9 | 9b7eb6e | Fresh |
| aarch64-unknown-linux-musl | 14 | d528ef9 | 9b7eb6e | Fresh |

golgiBody synced — both architectures confirmed.

## Wave 150 Final Status

| Item | Status |
|------|--------|
| Tower Atomic | COMPLETE (7/7 debt) |
| Crypto delegation | 6/6 seams DONE |
| bearDog pen test | SHIPPED (3 CRITICAL) |
| songBird BTSP ClientHello | SHIPPED |
| Production hardening | DEPLOYED |
| Depot | 28 binaries × 2 arch, fresh |
| Known debt | 1 (grapheneGate HSM) |
| Scenarios | 197, all PASS |
| flockGate code teams | CLEAR |

## Remaining (sporeGate)

| # | Task | Priority | Notes |
|---|------|----------|-------|
| 1 | Gate enrollment (southGate, strandGate) | P1 | Physical cabling |
| 2 | grapheneGate standalone | P2 | aarch64 depot ready |
| 3 | Chimera Phase 0 | P2 | Unblocked by crypto delegation |

## Forward: What Other Teams Should Know

- **cellMembrane team**: NUCLEUS services need BTSP ClientHello to talk to
  bearDog. Current services are rejected. Priority for high-crypto-dependency
  services first.
- **eastGate overwatch**: grapheneGate aarch64 binaries are in the depot.
  Android Keystore validation can proceed.
- **All teams**: Wave 150 is formally closed. Next horizon is Nest Atomic
  (data + provenance + rootPulse).

---

*Wave 150 CODE COMPLETE. Production hardened. Forward: Nest Atomic.*
