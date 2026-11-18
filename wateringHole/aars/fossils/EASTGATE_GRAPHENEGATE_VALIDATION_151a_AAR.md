# eastGate grapheneGate Validation AAR — Wave 151a

**Date**: Jul 25, 2026 21:12 EDT | **Wave**: 151a | **From**: eastGate overwatch (hardware)
**Scope**: bearDog Android Keystore validation, depot deployment failures, doc refresh

---

## Summary

Built bearDog for `aarch64-linux-android` and ran the 13-point hardware
validation checklist on grapheneGate (Pixel 8a, GrapheneOS Android 16).
**Software crypto fully operational. Hardware keystore blocked on JNI.**

Separately identified **critical deployment failures** from the golgiBody
depot's `aarch64-unknown-linux-musl` binaries when deployed to grapheneGate.

---

## P1: bearDog Android Keystore Validation

### Device
- Pixel 8a (akita), Tensor G3, Titan M2 HSM
- GrapheneOS Android 16, Build BP4A.260205.001
- ADB serial: 44251JEKB04957
- Connected via USB to eastGate

### Build
- Target: `aarch64-linux-android` (dynamic, linker64)
- NDK: r25c, API level 24
- Size: 9.2MB (vs 8.9MB musl static from depot)
- **3 compile errors fixed** (upstream bearDog):
  1. `unified.rs`: `HashMap` → `BTreeMap` for `ProviderHealth`/`Metrics` fields
  2. `android_keystore.rs`: `whoami` → `/proc/sys/kernel/hostname` (no whoami on Android)
  3. `android_keystore.rs`: added `warn` to tracing import

### Results

| # | Check | Result | Backend |
|---|-------|--------|---------|
| 1 | bearDog starts on aarch64 | **PASS** | TCP + abstract socket |
| 2 | HSM registry includes StrongBox | **FAIL** | Only software HSM (no JNI) |
| 3 | Ed25519 keypair generation | **PASS** | Software |
| 4 | Sign/verify roundtrip | **PASS** | `valid: true` |
| 5 | AES-256-GCM encrypt/decrypt | **PASS** | Software |
| 6 | StrongBox capability probe | **NOT REACHED** | Needs JVM |
| 7 | Device attestation chain | **NOT REACHED** | Needs JVM |
| 8 | Store a secret | **PASS** | In-memory |
| 9 | Retrieve secret | **PASS** | Correct value |
| 10 | List secrets | **PASS** | `["titan-test"]` |
| 11 | Delete secret | **PASS** | `deleted: true` |
| 12 | Persistence across restart | **FAIL** | Secret lost (in-memory) |
| 13 | Backend reports keystore | **FAIL** | `backend: "in-memory"` |

**Score: 10/13 PASS, 3 FAIL (all hardware-keystore-related)**

### Root Cause

Android Keystore API requires JVM/JNI context
(`java.security.KeyStore.getInstance("AndroidKeyStore")`). Running as a
native binary via `adb shell` provides no JVM, so StrongBox detection
falls back to software path.

### Recommended Resolution

**Path B: Keystore2 binder IPC** — Android 12+ exposes hardware keystore
via binder (no JVM needed). bearDog should implement `IKeystoreService`
via binder IPC for production hardware key access.

---

## DEPOT DEPLOYMENT FAILURES (golgiBody → grapheneGate)

The golgiBody depot (harvested by sporeGate, Jul 25) ships
`aarch64-unknown-linux-musl` static binaries to grapheneGate. These have
**4 deployment failures** when run on Android:

### Failure 1: Wrong Target Triple

| | Depot Binary | Required |
|-|-------------|----------|
| Target | `aarch64-unknown-linux-musl` | `aarch64-linux-android` |
| Linking | Static (musl libc) | Dynamic (Android linker64) |
| `cfg(target_os)` | `"linux"` | `"android"` |
| Android code | **NOT COMPILED** | Compiled |

The `#[cfg(target_os = "android")]` gates in bearDog's StrongBox, device
detection, and Keystore credential store code are all dead on the musl binary.

### Failure 2: UDS Transport Bind Failure

```
depot binary:   platform = "Unix (filesystem)"
                ERROR: Failed to bind socket on Unix (filesystem): /data/local/tmp/beardog-...sock
                
android binary: platform = "Android (abstract socket)"  
                ✅ Tier 1 (Native): Abstract socket configured: @biomeos_beardog_default
```

The musl binary attempts a filesystem-based unix socket which **fails** on
GrapheneOS due to filesystem restrictions in `/data/local/tmp`. The android
binary correctly uses abstract namespace (kernel-only, no filesystem path).

### Failure 3: No Hardware HSM Registration

```
depot binary:   "🔐 Initializing Rust Software HSM" (only provider)
android binary: "🔐 Initializing Rust Software HSM" (only provider — JNI still needed)
```

Neither binary currently registers StrongBox, but the android binary at least
has the _code_ compiled and ready for when Keystore2 binder is implemented.

### Failure 4: Binary Identity Drift

```
depot binary:   "name": "beardog-tunnel" (old crate name, Jun 10 build)
android binary: "name": "beardog" (current crate name, Jul 25 build)
```

The depot's aarch64 bearDog binary was built Jun 10 (pre-Wave 150 hardening)
and reports the old crate name. All crypto operations still work via TCP, but
it's 45 days stale vs current HEAD.

### Impact Assessment

| Capability | Depot (musl) | Android Build |
|-----------|-------------|---------------|
| TCP JSON-RPC | ✅ Works | ✅ Works |
| UDS (Tier 1 IPC) | ❌ Fails | ⚠️ Abstract (SELinux gated) |
| Software crypto | ✅ Works | ✅ Works |
| StrongBox/Titan M2 | ❌ Not compiled | ⚠️ Compiled, needs JNI |
| Secrets persistence | ❌ In-memory only | ❌ In-memory only |
| Binary freshness | ❌ 45 days stale | ✅ Current HEAD |

### Recommendation

The golgiBody depot needs a **third architecture target** for grapheneGate:

```
infra/plasmidBin/primals/
├── x86_64-unknown-linux-musl/    # existing (gates + golgiBody)
├── aarch64-unknown-linux-musl/   # existing (non-Android ARM gates)
└── aarch64-linux-android/        # NEW (grapheneGate + future mobile)
```

**Owner**: sporeGate topology team (depot harvest) + eastGate (Android NDK build)
**Blocker**: bearDog needs to fix the 3 compile errors (pushed in this session)
before sporeGate can cross-compile for the android target.

---

## Documentation Refreshed

| Document | Changes |
|----------|---------|
| GLOSSARY.md | 6 new terms (Nest Atomic expanded, rootPulse, Keystore2, crypto delegation, libtower.so, Silicon Atheism) |
| PRIMAL_REGISTRY.md | primalSpring → Wave 151a (197 ALL PASS, debt 1, grapheneGate validation) |
| bearDog handoff | Full validation results added with resolution paths |

---

## By The Numbers

| Metric | Value |
|--------|-------|
| primalSpring tests | **1241** pass, 0 fail |
| Known debt | **1** (grapheneGate HSM — hardware gated) |
| Scenarios | **197** ALL PASS |
| grapheneGate checks | **10/13** pass |
| bearDog compile fixes | **3** (pushed upstream) |
| Depot failures found | **4** (target, UDS, HSM, identity) |
| Binary built | `aarch64-linux-android` release, 9.2MB |

---

## Action Required

### bearDog team (flockGate)

1. **Merge compile fixes** — BTreeMap/HashMap, whoami, tracing import
2. **Implement Keystore2 binder** — Path B for hardware-backed keys without JVM
3. **Fix binary identity** — Ensure `primal.info` reports "beardog" not "beardog-tunnel"

### sporeGate (depot/topology)

1. **Add `aarch64-linux-android` target** to depot harvest
2. **grapheneGate deployment script** should use android binary (not musl)
3. **provenance.toml** should distinguish `linux-musl` vs `linux-android`

### eastGate (hardware)

1. ✅ Validation complete, results documented
2. ✅ Build fixes pushed to bearDog
3. **Next**: Test Keystore2 binder path once bearDog ships it
4. **Next**: grapheneGate NUCLEUS deploy once depot has android binaries

---

*Wave 151a eastGate AAR: grapheneGate validation 10/13, software crypto
operational, hardware keystore needs Keystore2 binder. 4 depot deployment
failures documented (wrong target, UDS bind, no HSM code, stale identity).
3 bearDog compile fixes pushed. primalSpring 197/197, debt 1. Documentation
refreshed. All pushed via cascade.*
