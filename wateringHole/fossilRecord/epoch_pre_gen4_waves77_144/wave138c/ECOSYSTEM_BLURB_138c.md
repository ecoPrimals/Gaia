# ecoPrimals Ecosystem Blurb — Wave 138c

**Date**: Jul 14, 2026 14:05 EDT | **Wave**: 138c | **From**: eastGate overwatch
**Posture**: **PUBLIC + SOVEREIGN.** All tracked items resolved. biomeOS delivered
NAPI-LIFECYCLE + SOCKET-DIR-UNIFY. 38/38 repos at parity. Zero remaining items.

---

## This Cascade

### bearDog: FIDO2 IPC Handler Split (NEW)

Monolithic `fido2.rs` (897 LOC) refactored into 8 focused modules:
`discover`, `register`, `authenticate`, `ceremony`, `entropy`, `helpers`, `mod`, `tests`.
ClientPIN CBOR boilerplate DRY'd. PIN error misclassification fixed
(0x2C != PinNotSet). CTAPHID magic numbers replaced with named constants.
13,883 tests pass, 0 clippy warnings.

### Cascade Pipeline Convergence

Overwatch now uses `membrane temporal.cascade --gate eastGate --with-rebuild`
as the single entry point. No more ad-hoc `git fetch/pull/push` loops.

### Cyclic Graph → DAG Fix (cellMembrane — NEW)

Root cause of perpetual wateringHole divergence: `freshness.toml` recorded
**commit SHAs** (graph-dependent) and included **self-reference** (wateringHole's
own SHA). Commit SHAs encode parentage/timestamps, so identical file trees at
different commit points produce different SHAs, creating an infinite fixpoint loop.

Fix: record `HEAD^{tree}` (content-addressed) instead of `HEAD` (graph-addressed),
and exclude wateringHole from its own freshness record. Identical file states now
produce identical hashes regardless of commit history. This cascade: **38/38 parity.**

### sporePrint Content Auto-Merge

sporePrint-bot auto-merged biomeOS lab page updates (v3.23.0). Branch-agnostic
fetch, WCAG figure/table compliance, constant sweep.

### Prior (138b): SoloKey Ceremony Breakthrough

First FIDO2 credential minted (primals.eco, ES256). Tap-sequence entropy
ceremony built (3-layer: transport timing, orchestrator, BLAKE3 mixing).
SoloKeys are **human proximity sensors and genetic generators** at this layer.
4 bugs fixed. Tier 3 human entropy model. ERR_CHANNEL_BUSY firmware issue
discovered (requires physical replug after timeout).

---

## Teams, Code, and Goals

### bearDog team (crypto / hardware trust)
**Code**: `primals/bearDog` — `beardog-hid`, `beardog-tunnel`, `beardog-security`

| Goal | Status | Next |
|------|--------|------|
| **First credential** | MINTED (primals.eco, ES256) | Authenticate → GetAssertion signature |
| **FIDO2 IPC refactor** | DONE (8 modules, 13,883 tests, 0 clippy) | — |
| **Tap-sequence ceremony** | BUILT (3-layer entropy) | Live 3-5 tap test after replug |
| **Loam Certificate seeding** | Design: Tier 1+2+3 → BLAKE3 → Loam cert seed | After ceremony validated |
| **ERR_CHANNEL_BUSY** | Discovered + CTAPHID_CANCEL mitigation | Ceremony UX must account for replug |

### biomeOS team (orchestration)
**Code**: `primals/biomeOS`

| Goal | Status | Next |
|------|--------|------|
| **NAPI-LIFECYCLE** | RESOLVED — `primal.announce` registers with LifecycleManager, `topology.rescan` auto-discovers | — |
| **SOCKET-DIR-UNIFY** | RESOLVED — all sockets → `/run/membrane/`, legacy `biomeos` deprecated with backward-compat scan | — |
| **SOCKET-UMASK** | RESOLVED — proper umask for IPC sockets | — |

### All other teams — no changes this cascade (status unchanged from prior blurb)

---

## Remaining — 0 items

All tracked items resolved.

**Resolved this wave**:
- ~~HIDRAW-REPORT-ID~~ — 0x00 report ID prefix in HID writes
- ~~FORGEJO-PERMS-RECUR~~ — 3-layer permanent fix deployed to golgi
- ~~BIOMEOS-TEMPLATE~~ — `service.template` subcommand implemented
- ~~FIDO2-MONOLITH~~ — 897 LOC split into 8 focused modules
- ~~AD-HOC-CASCADE~~ — overwatch now uses `membrane temporal.cascade`
- ~~FRESHNESS-CYCLE~~ — tree hashes + no self-reference → cyclic graph becomes DAG
- ~~NAPI-LIFECYCLE~~ — `primal.announce` + `topology.rescan` register with LifecycleManager
- ~~SOCKET-DIR-UNIFY~~ — all sockets → `/run/membrane/`, legacy deprecated
- ~~SOCKET-UMASK~~ — proper umask for IPC sockets

---

## Three Tracks → Glacial Goals

### Track 1: Hardware Trust → NUCLEUS USB Kit

```
DONE    beardog.fido2.discover → SoloKey enumeration
DONE    CTAPHID_INIT handshake (firmware 2.3.196, CBOR+WINK)
DONE    HIDRAW-REPORT-ID fix (0x00 prefix)
DONE    First credential minted (primals.eco, ES256)
DONE    Tap-sequence ceremony built (3-layer entropy)
DONE    FIDO2 IPC refactor → 8 modules (13,883 tests, 0 clippy)
NOW     Authenticate: GetAssertion → verify credential works
NOW     Live tap-sequence test (3-5 taps after replug)
NEXT    Entropy harvest: Tier 1+2+3 → BLAKE3 → Loam cert seed
NEXT    Pixel StrongBox ceremony (ADB, Titan M2)
GOAL    SoloKey = human proximity sensor + genetic generator
        User is their own key. USB kit deploys NUCLEUS identity.
```

### Track 2: K-Derm Extrication → Sovereign Membrane Parity

```
DONE    *.primals.eco wildcard DNS
DONE    FORGEJO-PERMS 3-layer defense
DONE    100% Rust deployment pipeline
DONE    BIOMEOS-TEMPLATE resolved
DONE    NAPI-LIFECYCLE — LifecycleManager wired
DONE    SOCKET-DIR-UNIFY — /run/membrane/ canonical
NOW     primal.eco separation (inner membrane)
GOAL    Full sovereign membrane parity
```

### Track 3: Live Compositions → External Science Production

```
DONE    footPrint GIS at primals.eco/footprint/
DONE    JupyterHub at lab.primals.eco
DONE    Composition routing standard shipped
NOW     ABG user accounts, tideGlass Phase 0
GOAL    External science through sovereign compositions
```

---

## primalSpring Scenarios to Write (from ceremony exploration)

| Scenario | Validates |
|----------|-----------|
| `s_fido2_register_e2e` | MakeCredential → valid credential_id + COSE key |
| `s_fido2_authenticate_e2e` | GetAssertion signature verifies against registered key |
| `s_fido2_entropy_mixing` | Tier 1+2+3 mixed, output passes NIST SP 800-22 basics |
| `s_fido2_tap_timing_entropy` | Nanosecond timing capture, non-zero values |
| `s_fido2_ceremony_chain` | register → authenticate → entropy → Loam cert seed |
| `s_fido2_timeout_tolerance` | UserActionTimeout handled gracefully |

Mock (CI) + Live (gate with SoloKey) dual-mode via `/dev/hidraw` detection.

---

## Gate Status

```
eastGate     — PRIMARY. Cascade via membrane pipeline. bearDog refactor absorbed.
sporeGate    — NUCLEUS. SoloKey plugged. First credential minted. Depot authority.
golgiBody    — Outer membrane. Wildcard DNS. Auto-publishing heads.
flockGate    — bearDog FIDO2 + primalSpring scenarios.
ironGate     — ABG/NF compute. JupyterHub. 13/13 active.
grapheneGate — StrongBox target. Android compile unblocked.
```

---

*Wave 138c: all tracked items resolved. biomeOS delivered NAPI-LIFECYCLE + SOCKET-DIR-UNIFY + SOCKET-UMASK. FIDO2 IPC refactored to 8 modules. Cascade pipeline converged. 38/38 repos at parity. Zero remaining items. Ready for next wave scope.*
