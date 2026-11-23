# soundStage Concept — AAR Wave 138b

**Date**: 2026-07-14 | **Wave**: 138b | **From**: eastGate primalSpring hardware team
**Gate**: eastGate | **Repo**: primalSpring

---

## Context

With FIDO2 entropy ceremonies, Loam Certificate minting, and multi-source key
generation structurally proven (Waves 138a–138b), the next gap was transparency.
Hardware security modules are opaque — you call an API and get bytes back. How
do you know they're actually entropic? How do you know mixing isn't degenerate?

The ecosystem needed an observability concept for hardware trust ceremonies.

## What soundStage Is

An ecoPrimals concept (like drawBridge, fieldMouse, darkforest). soundStage
makes ephemeral key generation visible — you watch it happen rather than trust
it's secure.

**Recording studio analogy**:
- **Channel** = microphone (one per entropy source: SoloKey, StrongBox, audio, OS)
- **Mix bus** = mixing board (where entropy converges)
- **Monitor** = studio speakers (observe the output, never export raw material)
- **Session** = session tape (timestamped recording of a full ceremony)
- **Comparator** = A/B playback (diff sessions for independence or degeneration)

## What Was Built

Reference implementation in `primalSpring/ecoPrimal/src/soundstage/`:

| Module | Purpose | Tests |
|--------|---------|-------|
| `anchor.rs` | Hardware trust root abstraction (Fido2, StrongBox, Audio, OsEntropy) | 2 |
| `channel.rs` | Observable entropy signal per anchor — timestamps, BLAKE3 fingerprints, Shannon entropy | 5 |
| `session.rs` | Complete ceremony recording — channels, mix inputs, monitor fingerprint | 3 |
| `capture.rs` | Thread-safe live observation API (Arc<Mutex>) — browser/terminal hook point | 1 |
| `comparator.rs` | Session diff engine — independence, collision, degenerate entropy detection | 5 |

**Total**: 16 tests, all passing. Full integration with existing primalSpring suite (1149 total).

## Key Design Decisions

1. **Fingerprints only in monitor** — BLAKE3 hash of key material, never the raw key.
   Enables comparison without exposing secrets.

2. **Quality gates** — Multi-source requirement (≥2 anchors) + Shannon entropy floor
   (>4.0 bits/byte). Single-source ceremonies fail quality even if entropy looks good.

3. **Shannon entropy on every signal** — real-time detection of hardware degradation.
   Constant bytes (0x00 × 32) score 0.0 and immediately flag.

4. **Comparator verdicts** — `Independent` (good), `Collision` (CRITICAL — same key
   material), `DegenerateEntropy` (hardware malfunction or attack), `Incomplete`.

5. **Thread-safe capture** — LiveCapture wraps session in Arc<Mutex>, multiple
   observers can watch same ceremony simultaneously (browser UI + audit log).

## Relationship to Existing Concepts

| Concept | soundStage Relationship |
|---------|------------------------|
| **darkforest** | darkforest reveals what probes the network. soundStage reveals what flows through the ceremony. |
| **drawBridge** | drawBridge is the crossing point. soundStage observes what happens at the ceremony inside. |
| **bearDog** | bearDog performs the ceremony. soundStage watches bearDog perform it. |
| **loamSpine** | loamSpine stores the certificate. soundStage records how the certificate was minted. |
| **Provenance trio** | Trio tracks who/when/where. soundStage tracks what/how (entropy sources, mixing, quality). |

## Metrics

- `primalSpring` v0.9.36+soundstage: **1,149 tests, 147 scenarios + 16 soundStage unit tests**
- Zero compilation warnings (after cleanup)
- Full clippy pass

## Upstream Gaps

| Priority | Gap | Owner |
|----------|-----|-------|
| P1 | Wire soundStage capture into bearDog's FIDO2 ceremony path (real hardware signals) | bearDog team |
| P1 | Browser UI component for live ceremony observation (WebSocket stream from capture) | sporePrint / esotericWebb |
| P2 | Persistent session storage — serialize SessionRecord to NestGate for audit trail | NestGate team |
| P2 | Audio channel integration — capture mic entropy with sample rate and quality metrics | toadStool team |
| P3 | Comparator batch analysis UI — visual diff of session fingerprints across users | esotericWebb |

## Glossary Update

Added `soundStage` to `wateringHole/GLOSSARY.md` — full entry in The Coordination
Layer section and Quick Lookup table.

---

**Status**: CONCEPT LANDED. Reference implementation complete. Ready for upstream
integration with live hardware paths.
