# primalSpring Wave 138b — Upstream Handoff

**Date**: 2026-07-14 | **Wave**: 138b | **From**: eastGate primalSpring overwatch
**Posture**: ALL 147 SCENARIOS ACTIVE. Zero known-compile-debt. 3 ecosystem items remain.

---

## What Happened

The VPS session (flockGate parallel) had commented out 22 scenarios during a health restore to unblock CI. primalSpring overwatch on eastGate re-enabled all 22 — they pass cleanly on this gate with zero compilation or runtime issues.

**Before**: 125 active scenarios, 22 commented, 1 test failure (stale known-debt)
**After**: 147 active scenarios, 0 commented, 0 failures, 1,133 tests pass

## Changes

| What | Detail |
|------|--------|
| Re-enabled 22 scenarios | All compile and pass on eastGate (Rust-tier validation) |
| `sporeprint-pure-primal-parity` | Debt cleared — was expecting 1 failure, now passes cleanly |
| `graphenegate-readiness` | Debt reduced 2→1 — depot layout resolved, deploy script remains |
| `EXPECTED_SCENARIO_COUNT` | 125 → 147 |
| README + CONTEXT | Updated to reflect 147 scenarios / 1,133 tests |

## Re-enabled Scenarios (all 22)

| Scenario | Track | Status |
|----------|-------|--------|
| `s_lan_wan_meshed_posture` | Security | PASS |
| `s_wan_dispatch_validation` | BiomeosDeploy | PASS |
| `s_composition_subtypes` | AtomicComposition | PASS |
| `s_sovereign_ci_pipeline` | Security | PASS |
| `s_mesh_auto_distribution` | BiomeosDeploy | PASS |
| `s_composition_profiles` | AtomicComposition | PASS |
| `s_outer_membrane_posture` | Security | PASS |
| `s_cascade_signing` | Security | PASS |
| `s_cross_membrane_data_flow` | Security | PASS |
| `s_topology_visualization` | BiomeosDeploy | PASS |
| `s_federation_wan_readiness` | Security | PASS |
| `s_pure_rust_crypto_audit` | Security | PASS |
| `s_mesh_federation_readiness` | Security | PASS |
| `s_live_composition_deploy` | AtomicComposition | PASS |
| `s_neural_api_lifecycle` | BiomeosDeploy | PASS |
| `s_cross_gate_mesh_deploy` | BiomeosDeploy | PASS |
| `s_socket_directory_unification` | BiomeosDeploy | PASS |
| `s_fp_api_proxy` | AtomicComposition | PASS |
| `s_drawbridge_bonds` | Security | PASS |
| `s_depot_trust_verify` | Security | PASS |
| `s_protokarya_composition_routing` | AtomicComposition | PASS |
| `s_drawbridge_weak_bond_ingestion` | AtomicComposition | PASS |

## Remaining Known Debt

| Scenario | Failures | Why |
|----------|----------|-----|
| `graphenegate-readiness` | 1 | Deploy script (eastGate-local) — not yet shipped |

## Metrics

| Metric | Value |
|--------|-------|
| Active scenarios | 147 (0 commented) |
| Tests | 1,133 pass / 0 fail / 2 ignored |
| Known debt failures | 1 (graphenegate-readiness) |
| Clippy | 0 warnings |

## Local Evolution Strategy

primalSpring on eastGate continues to **validate interaction surfaces** for the hardware trust pipeline. The evolution direction is *downward into local hardware*:

```
EXISTING (stable, leverageable)          EVOLVING (local-first)
────────────────────────────────          ──────────────────────
golgi depot (signed binaries)      ←──   bearDog + FIDO2 (SoloKey)
sporeGate NAPI (HTTP)              ←──   ceremony manager (stateful)
primals.eco (public membrane)      ←──   browser ceremony UI
songBird mesh (3-gate)             ←──   multi-gate witness
cascade pipeline (CI/CD)           ←──   deploy hardware-backed bearDog
                                         audio entropy (headset)
                                         Pixel StrongBox (ADB)
                                         Loam Certificate (provenance)
```

**The 147 scenarios validate the topology that hardware backends wire into.** No upper-layer changes needed — bearDog wires SoloKey/Pixel/audio, cascade distributes, mesh federates, browser UI calls through NAPI.

## For Overwatch

- **flockGate parallel session**: Can now uncomment their 22 scenarios too (or pull from upstream). The source files are identical; they compiled and passed on eastGate.
- **bearDog team**: HIDRAW-REPORT-ID is the P0 blocker (one byte). Once fixed, `s_fido2_entropy_ceremony` + `s_hardware_trust_pipeline` + `s_keygen_interaction_surface` will transition from structural to live validation.
- **biomeOS team**: NAPI-LIFECYCLE and SOCKET-DIR-UNIFY are P2 — can proceed at pace. primalSpring validates both structurally.

---

## P0 HIDRAW-REPORT-ID — RESOLVED

**Root cause**: `rk=true` (resident key) hardcoded in `build_make_credential_ext`. Solo 2 firmware ≥2.3 requires PIN for discoverable credentials. MakeCredential timed out silently because device rejected without proper PIN ceremony.

**Fix**: `let rk = pin_uv_auth.is_some();` — non-discoverable credentials for entropy ceremony (credential_id stored in depot). PIN ceremony path available when discoverable credentials are needed.

**Also shipped**: `client_pin.rs` (CTAP2 ClientPIN Protocol pinProtocol 1), `p256` with ecdh for key agreement, IPC handler accepts optional `pin` param.

**Status**: Pushed to `origin/main` (`bearDog 94d58b6b2`). Forgejo sync deferred (diverged history).

**Remaining items**: 2 (NAPI-LIFECYCLE P2, SOCKET-DIR-UNIFY P2). HID-BLOCKING-IO (P1) still open but non-blocking with EAGAIN retry works for ceremony.

---

*Wave 138b: 147/147 scenarios active. 1,133 tests / 0 fail. P0 HIDRAW-REPORT-ID resolved. All compile-debt resolved. primalSpring is the validation authority for the hardware trust pipeline. Local-first evolution leverages existing VPS/depot/mesh infrastructure.*
