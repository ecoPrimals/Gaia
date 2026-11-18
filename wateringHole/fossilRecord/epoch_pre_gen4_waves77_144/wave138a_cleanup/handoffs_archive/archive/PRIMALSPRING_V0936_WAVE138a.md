# primalSpring v0.9.36 — Wave 138a Handoff

**Date**: 2026-07-13 | **Wave**: 138a | **From**: eastGate primalSpring overwatch

---

## Summary

Hardware trust activation — structural validation of the FIDO2 entropy ceremony
and end-to-end Loam Certificate pipeline. Two new scenarios prove the topology
is ready for live SoloKey + Pixel ceremonies once bearDog IPC stubs are wired.

## New Scenarios (+2 → 146 total)

| Scenario | Track | What it validates |
|----------|-------|-------------------|
| `s_fido2_entropy_ceremony` | Security | FIDO2 → bearDog → genetic mixing → key derivation. All 3 FIDO2 methods + 6 genetic ceremony methods route to bearDog. Single-authority entropy flow proven. |
| `s_hardware_trust_pipeline` | Security | Full E2E: hardware entropy → bearDog key gen → Ed25519 signing → loamSpine certificate mint. Authority chain: bearDog owns entropy+signing, loamSpine owns certification. Separation of concerns validated. |

## Metrics

| Metric | Value |
|--------|-------|
| Version | 0.9.36 |
| Scenarios | 146 (12 tracks, 3 tiers) |
| Tests | 1,301 pass / 0 fail |
| Clippy | Zero warnings |
| Wave | 138a |

## Capability Coverage

- **FIDO2 domain**: `beardog.fido2.{discover,register,authenticate}` — registered, routed, bearDog-owned
- **Genetic domain**: `genetic.{ceremony_init,ceremony_finalize,entropy_contribute,mix_entropy,derive_key,derive_lineage_key}` — registered, routed, bearDog-owned
- **Signing**: `crypto.sign_ed25519` → bearDog
- **Certificate**: `spine.{create,seal}` → loamSpine
- **Verification**: `crypto.verify_ed25519` → bearDog

## Upstream Gaps (for primal teams)

| Gap ID | Owner | What's needed |
|--------|-------|---------------|
| **FIDO2-CTAP2-WIRE** | bearDog | Wire actual CTAP2 hmac-secret via `ctap-hid-fido2` crate. IPC stubs exist; need real hardware backend. SoloKey plugged on eastGate (USB). |
| **STRONGBOX-ADB** | bearDog/grapheneGate | Fix 16 compile errors in `AndroidKeymaster`. ADB port forwards from eastGate → Pixel. |
| **CEREMONY-E2E-LIVE** | bearDog + loamSpine | Integration test: SoloKey entropy + Pixel biometric → bearDog key gen → loamSpine mint. Blocked on FIDO2-CTAP2-WIRE + STRONGBOX-ADB. |
| **HW-INVENTORY** | ecosystem | Canonical `HARDWARE_INVENTORY.md` — resolve spec conflicts between parallel sessions. |
| **LOAM-PROVENANCE** | loamSpine | Certificate should embed entropy source provenance (which hardware tier contributed). |

## Evolution Path (from blurb)

```
Phase 1 — LOCAL (THIS WAVE)
  ✓ primalSpring structural validation of FIDO2 + pipeline topology
  → bearDog team: wire CTAP2 crate + ADB keystore
  → local ceremony E2E test once hardware backends are live

Phase 2 — INNER MEMBRANE (primal.eco)
  Ceremony endpoints on primal.eco
  bearDog gatehouse TLS cutover
  Private footPrint with Loam Certificate provenance

Phase 3 — SUBSTRATE EXPANSION
  Android NDK depot target
  RISC-V, WASM depot targets
```

---

*primalSpring overwatch: topology proven. bearDog team can wire hardware with confidence that routing, authority chain, and certificate pipeline are structurally sound.*
