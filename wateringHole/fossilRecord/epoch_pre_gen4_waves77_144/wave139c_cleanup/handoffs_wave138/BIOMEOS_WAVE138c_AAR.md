# biomeOS Wave 138c — After Action Report

**Date**: Jul 14, 2026 14:00 EDT
**Gate**: eastGate (overwatch)
**Team**: biomeOS (orchestration)
**Commits**: `6d884266` (biomeOS), `bfbe3026` (primalSpring)

---

## Delivered

### NAPI-LIFECYCLE (P2) — RESOLVED

**Problem**: `lifecycle.status` returned count=0 because capability discovery
(`topology.rescan`) and `primal.announce` (without PID) skipped lifecycle
registration entirely. Primals appeared in `capability.call` routing but not
in the LifecycleManager.

**Fix**:
1. `primal.announce` now registers with LifecycleManager regardless of PID
   presence — socket-based health checks suffice for monitoring.
2. `discover_and_register_primals` (both UDS and TCP paths) now registers
   discovered primals with LifecycleManager after capability registration.

**Files**: `handlers/announce.rs`, `neural_api_server/discovery_init.rs`

### SOCKET-DIR-UNIFY (P2) — RESOLVED

**Problem**: Socket resolution used mixed `biomeos` and `membrane` subdirectories.
SSOT (`DEFAULT_SOCKET_DIR`) already said `/run/membrane`, but 15+ consumer files
still resolved via `BIOMEOS_SUBDIR` ("biomeos").

**Fix**:
- All socket resolution paths consolidated to `MEMBRANE_SUBDIR` ("membrane")
- `BIOMEOS_SUBDIR` deprecated with `#[deprecated]` attribute
- Backward-compat scan retained in `topology.rs` (with `#[expect(deprecated)]`)
- 27 files updated across 10 crates

**Crates touched**: biomeos-types, biomeos-core, biomeos-atomic-deploy,
biomeos-nucleus, biomeos-primal-sdk, biomeos-spore, biomeos-boot,
neural-api-client-sync, biomeos-unibin, platypus chimera

### primalSpring FIDO2 Scenarios (6 new) — DELIVERED

Dual-mode (mock CI + live hardware via `/dev/hidraw` detection):

| Scenario | Validates |
|----------|-----------|
| `s_fido2_register_e2e` | MakeCredential CBOR + attestation parsing |
| `s_fido2_authenticate_e2e` | GetAssertion + ECDSA verification model |
| `s_fido2_entropy_mixing` | 3-tier BLAKE3 + NIST SP 800-22 monobit/runs |
| `s_fido2_tap_timing_entropy` | Nanosecond jitter analysis |
| `s_fido2_ceremony_chain` | register → auth → entropy → Loam seed (atomic) |
| `s_fido2_timeout_tolerance` | ERR_CHANNEL_BUSY + keepalive + graceful degradation |

---

## Test Health

- **biomeOS**: full workspace green — 3,500+ tests / 0 fail / 0 clippy warnings
- **primalSpring**: 1,167 tests / 0 fail / 131 scenarios (up from 125)

## KNOWN_DEBT Updates

- `sporeprint-pure-primal-parity` — cleared (0 failures, removed from list)
- `graphenegate-readiness` — reduced from 2 to 1 failure

---

## biomeOS Remaining Items

**None.** Both P2 items resolved. biomeOS team has zero outstanding debt
as of this cascade.

---

## Notes for Next Wave

- The blurb still lists NAPI-LIFECYCLE and SOCKET-DIR-UNIFY as remaining —
  cascade pipeline hasn't absorbed our commits yet. Next blurb should reflect
  these as resolved.
- Deploy scripts and TOML configs still reference `/run/biomeos` in string
  literals (Tier 3 migration). These are non-blocking — the Rust resolution
  code is unified and the backward-compat scan handles deployed infrastructure.
- `capability_registry.toml` documents `run_biomeos` pattern — cosmetic update
  can happen when deploy scripts are updated.
