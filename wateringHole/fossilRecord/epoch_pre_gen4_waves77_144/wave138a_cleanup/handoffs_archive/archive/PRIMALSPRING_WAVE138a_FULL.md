# primalSpring Wave 138a — Full Upstream Handoff

**Date**: 2026-07-13 | **Wave**: 138a | **From**: eastGate primalSpring overwatch
**Posture**: PUBLIC + SOVEREIGN. Hardware trust activation in progress.

---

## Strategic Context

The ecosystem has evolved *outward* through Waves 107–137b: outer membrane hardened, public website live, 3-gate mesh operational, signed depot trust, Neural API live, topology visualization deployed. The infrastructure layer (golgi, sporeGate, VPS) is **stable and leverageable**.

**Wave 138 inverts the vector**: evolve *back down* to the hardware we have local access to. The goal is hardware sovereignty — key generation, entropy ceremonies, and trust anchors rooted in physical devices the operator controls, not cloud abstractions.

primalSpring's role: **validate every interaction the larger systems will leverage**, so that bearDog, loamSpine, biomeOS, and the browser UI can implement against proven topology.

---

## What Was Built (Wave 138a — eastGate local)

### 3 New Scenarios (+3 → 147 total)

| # | Scenario | Track | What it proves |
|---|----------|-------|----------------|
| 1 | `s_fido2_entropy_ceremony` | Security | SoloKey CTAP2 → bearDog IPC → genetic mixing → key derivation. All 3 FIDO2 methods + 6 genetic ceremony methods route to bearDog. Single-authority entropy flow. |
| 2 | `s_hardware_trust_pipeline` | Security | Full E2E: hardware entropy → bearDog key gen → Ed25519 signing → loamSpine certificate mint. Authority chain: bearDog owns entropy+signing, loamSpine owns certification. Separation of concerns. |
| 3 | `s_keygen_interaction_surface` | Security | Browser-accessible ceremony via Neural API dispatch. Keygen methods, ceremony state machine, multi-source entropy, ephemeral key lifecycle, NAPI dispatch compatibility. |

### Metrics

| Metric | Before (137b) | After (138a) |
|--------|---------------|--------------|
| Scenarios | 144 | 147 |
| Tests | 1,294 | 1,306 |
| Failures | 0 | 0 |
| Clippy | 0 | 0 |
| Version | 0.9.36 | 0.9.36 |

---

## Architecture Proven

### Capability Routing (all validated by primalSpring)

```
Browser UI ──HTTP──→ Neural API (biomeOS :9800)
                          │
                    capability.call
                          │
              ┌───────────┼───────────────┐
              ▼           ▼               ▼
          [bearDog]   [bearDog]      [loamSpine]
           crypto.*    genetic.*      spine.*
           fido2.*                    certificate.*
```

### Key Generation Ceremony (interaction surface proven)

```
Step 1: ceremony_init(tier=2, sources=["fido2","audio","strongbox","getrandom"])
        → bearDog allocates ceremony state

Step 2: entropy_contribute(source="fido2", data=<CTAP2 hmac-secret>)
        → SoloKey USB on eastGate

Step 3: entropy_contribute(source="audio", data=<mic capture>)
        → Headset wire on eastGate (RustDesk or direct)

Step 4: entropy_contribute(source="strongbox", data=<Titan M2 attestation>)
        → Pixel 8a over ADB from eastGate

Step 5: entropy_contribute(source="getrandom", data=<OS entropy>)
        → eastGate /dev/urandom

Step 6: mix_entropy() → combine N sources (XOF/HKDF)

Step 7: derive_key(purpose="identity") → Ed25519 keypair

Step 8: ceremony_finalize() → seal provenance record

Step 9: crypto.sign_ed25519(message=<spine_hash>) → sign for Loam Certificate

Step 10: spine.create + spine.seal → loamSpine mints certificate
         with embedded entropy provenance (which tiers contributed)
```

### Ephemeral Key Comparison Flow

```
Generate ephemeral_A (from ceremony with sources X,Y)
Generate ephemeral_B (from ceremony with sources X,Z)
Sign test message with both
Verify both signatures
Derive DIDs from pubkeys
Compare lineage proofs
→ Validates mixing determinism and source independence
```

---

## Local Hardware Available on eastGate

| Device | Interface | Role in Ceremony | Status |
|--------|-----------|------------------|--------|
| SoloKey (USB) | CTAP2/HID | Tier 2 entropy (hmac-secret) | Plugged. bearDog IPC stubs exist. Needs `ctap-hid-fido2` crate wiring. |
| Pixel 8a (Titan M2) | ADB port forward | StrongBox entropy + FAMILY_SEED store | Connected. 16 compile errors in `AndroidKeymaster`. |
| Headset/mic (RustDesk wire) | Audio capture | Ephemeral entropy (acoustic noise) | Available. Can swap wire for direct capture. |
| eastGate compute | getrandom | OS-level entropy | Always available. |
| ironGate (secondary) | SoloKey plugged | Backup FIDO2 source | Live (13/13 primals). |

---

## What primalSpring Validates vs What Teams Implement

| primalSpring proves (topology/interaction) | Team implements (hardware/runtime) |
|---|---|
| FIDO2 methods registered + routed to bearDog | bearDog: wire `ctap-hid-fido2` → actual SoloKey |
| Ceremony state machine complete | bearDog: stateful ceremony manager with timeout/rollback |
| Multi-source entropy routing | bearDog: XOF/HKDF mixing with source isolation |
| Browser dispatch path (NAPI) | biomeOS: HTTP→UDS→capability.call bridge for ceremony |
| Certificate mint separation | loamSpine: embed entropy provenance in certificate |
| Ephemeral key comparison | bearDog: deterministic derivation from same mixed material |
| Audio entropy contribution | bearDog: audio capture → conditioning → entropy_contribute |
| ADB StrongBox routing | bearDog: `AndroidKeymaster` → ADB port forward → genetic.entropy_contribute |

---

## Leveraging Existing Infrastructure

The local evolution **does not** require rebuilding upper layers. It leverages:

| Layer | What we use | How |
|-------|-------------|-----|
| **golgi depot** | Signed binary distribution | bearDog binary (once FIDO2 wired) pushed to depot → signed → deployed to all gates |
| **VPS (sporeGate)** | Neural API HTTP exposure | Browser on any device → `primal.eco:443` → Caddy → biomeOS → ceremony endpoints |
| **Website (primals.eco)** | Public ceremony documentation | Ceremony flow described on philosophy pages; public keys published for verification |
| **Mesh (songBird)** | Multi-gate ceremony witness | ironGate SoloKey can witness eastGate ceremony (federation) |
| **Cascade pipeline** | Build + sign + deploy | Once bearDog ships FIDO2, cascade distributes to all gates automatically |
| **primalSpring (this)** | Continuous validation | Every gate runs scenarios confirming ceremony topology is intact |

---

## Upstream Gaps (for primal teams)

### P0 — Blocking Local Ceremony

| Gap | Owner | What | Blocked by |
|-----|-------|------|-----------|
| **FIDO2-CTAP2-WIRE** | bearDog | Wire `ctap-hid-fido2` to actual SoloKey USB. IPC stubs exist (`beardog.fido2.*`). | Nothing — can start now |
| **STRONGBOX-ADB** | bearDog | Fix 16 compile errors in `AndroidKeymaster`. ADB port forwards configured. | Nothing — can start now |
| **AUDIO-ENTROPY** | bearDog | Audio capture → conditioning → `genetic.entropy_contribute`. Simple: read PCM, hash, contribute. | Nothing — can start now |

### P1 — Ceremony Runtime

| Gap | Owner | What | Blocked by |
|-----|-------|------|-----------|
| **CEREMONY-MANAGER** | bearDog | Stateful ceremony: timeout, rollback, source tracking. Currently methods are stateless stubs. | P0 sources working |
| **NAPI-CEREMONY-HTTP** | biomeOS | HTTP endpoints for browser-driven ceremony (POST /ceremony/init, /contribute, /finalize). | CEREMONY-MANAGER |
| **LOAM-PROVENANCE** | loamSpine | Embed entropy source provenance (which hardware tier contributed) in certificate body. | CEREMONY-MANAGER |

### P2 — Integration

| Gap | Owner | What | Blocked by |
|-----|-------|------|-----------|
| **CEREMONY-E2E-LIVE** | bearDog + loamSpine | Integration test: real hardware entropy → real certificate. | P0 + P1 |
| **BROWSER-CEREMONY-UI** | sporePrint / footPrint | UI for interactive ceremony (WebAuthn for FIDO2, ADB bridge for Pixel). | NAPI-CEREMONY-HTTP |
| **MULTI-GATE-WITNESS** | songBird | Federation ceremony: ironGate SoloKey witnesses eastGate ceremony. | CEREMONY-E2E-LIVE |
| **HW-INVENTORY** | ecosystem | Canonical `HARDWARE_INVENTORY.md` resolving parallel session conflicts. | Nothing |

---

## Evolution Path

```
NOW (Wave 138a — validated by primalSpring)
├── Topology proven: browser → NAPI → bearDog → loamSpine
├── Interaction surface: ceremony state machine, multi-source, ephemeral comparison
├── All 147 scenarios GREEN (1,306 tests)
└── primalSpring can test locally with live bearDog as stubs get wired

NEXT (Wave 138b — bearDog implements)
├── SoloKey CTAP2 wired (eastGate local)
├── Audio entropy capture (eastGate local)
├── AndroidKeymaster compiles (Pixel ADB)
├── First real ceremony produces first real Loam Certificate
└── primalSpring live probe validates real hardware responses

THEN (Wave 139 — evolve outward)
├── biomeOS exposes ceremony via HTTP (browser accessible)
├── primal.eco gets ceremony endpoints
├── Browser UI for interactive key creation
├── Multi-gate witness via songBird federation
└── Cascade deploys bearDog with FIDO2 to all gates
```

---

## For Upstream Overwatch

**What's stable and leverageable** (do not disrupt):
- golgi depot + signed trust
- sporeGate Neural API + HTTP
- primals.eco outer membrane
- 3-gate mesh + songBird federation
- Cascade pipeline + CI

**What's evolving locally** (eastGate focus):
- Hardware trust anchors (SoloKey, Pixel, audio)
- bearDog FIDO2/genetic ceremony backends
- Local ceremony E2E testing
- primalSpring interaction validation

**The thesis**: Everything above the hardware layer is proven. We evolved outward to public presence, mesh, signed depot. Now we evolve *inward/downward* to root trust in physical hardware the operator controls. primalSpring validates the interaction patterns; bearDog team wires the actual devices. When bearDog ships, cascade distributes automatically to all gates.

---

*primalSpring overwatch: 147 scenarios / 1,306 tests / 0 fail. Hardware trust topology proven. bearDog team can implement against validated interaction surface. Local-first, then outward via existing infrastructure.*
