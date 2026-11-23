# SOLOKEY-CEREMONY + PIXEL-STRONGBOX + HW-INVENTORY — After Action Review

**Wave**: 138a | **Date**: Jul 13, 2026 | **Operator**: eastGate overwatch
**Status**: COMPLETE (code paths wired, hardware validation pending SoloKey physical test)

---

## Summary

Wave 138a local-first on eastGate. Three tasks completed:

1. **HW-INVENTORY-RECONCILE** — Unified hardware inventory into single canonical source
2. **SOLOKEY-CEREMONY** — Wired SoloKey FIDO2 → bearDog entropy with new IPC method
3. **PIXEL-STRONGBOX** — Fixed Android cross-compile, unblocking Pixel 8a depot builds

---

## HW-INVENTORY-RECONCILE

Reconciled two divergent hardware documents:

- `technical/HARDWARE_INVENTORY.md` (Wave 116, network topology only — missing all security/mobile/neuromorphic hardware)
- `gen3/about/HARDWARE.md` (May 2026, full compute specs — stale IPs, missing pepti VPS)

**Conflicts resolved:**
- sporeGate RAM: 28 GB measured vs 32 GB spec → documented both with measured as canonical
- ironGate vs eastGate primalSpring ownership → clarified shared ownership
- flockGate test counts: 144/1190 → 122/1095+ (canonical from primalSpring registry)
- Subnet migration 192.168.1.x → 192.168.4.x documented
- pepti VPS added (missing from gen3)

**Added:**
- All 11 towers with full CPU/GPU/RAM/storage specs
- SoloKey ×4 with ceremony roles and IPC methods
- Pixel 8a / grapheneGate with StrongBox and Titan M2 details
- Akida NPU placements (3 cards across 3 gates)
- Work card pool (8 cards, 128 GB VRAM, 56 GB HBM2)
- WireGuard overlay IPs

**Removed:** Inline credentials (WiFi passwords, device access codes). Noted "see vault" in changelog.

---

## SOLOKEY-CEREMONY

### Bug 1: Feature flag mismatch (CRITICAL)

**Problem**: Workspace `fido2` feature enabled `beardog-security/fido2` + `beardog-hid` but NOT `beardog-tunnel/ctap2`. Building with `--features fido2` left IPC handlers on **stub paths** — `beardog.fido2.register` would say "feature not enabled" even with the feature flag active.

**Fix**: Added `beardog-tunnel/ctap2` to the workspace `fido2` feature definition:

```toml
fido2 = ["beardog-security/fido2", "beardog-tunnel/ctap2", "dep:beardog-hid"]
```

### Bug 2: Authenticate key-handle persistence (CRITICAL)

**Problem**: Each `beardog.fido2.authenticate` RPC call created a **fresh** `SoloV2Provider` with an empty `key_handles` HashMap. The `sign_with_device()` method looked up `key_id` in this empty map → always "Key not found". Register and authenticate were separate RPC calls, so keys registered in one provider session were lost.

**Fix**: Added `authenticate_with_credential()` method to `SoloV2Provider` that takes raw `credential_id` bytes directly, bypassing the in-memory lookup. The CTAP2 `GetAssertion` command uses `credential_id` as an allow-list — the authenticator looks up the credential internally. Updated the IPC handler to use this stateless path.

### New: `beardog.fido2.entropy` IPC method (Tier 2 hardware entropy)

Added a new IPC method that harvests hardware entropy from a FIDO2 device:

1. Generates a random 32-byte challenge
2. Calls CTAP2 `GetAssertion` with the challenge (requires physical touch)
3. Mixes the signature bytes (containing the authenticator's hardware RNG nonce) with the challenge via BLAKE3 keyed hash
4. Returns 32 bytes of Tier 2 hardware entropy

```json
// Request
{"method": "beardog.fido2.entropy", "params": {"rp_id": "primals.eco", "credential_id": "<base64>"}}

// Response
{"entropy": "<base64, 32 bytes>", "source": "fido2_hardware", "tier": 2, "user_present": true}
```

### New: hmac-secret extension support in MakeCredential

Added `build_make_credential_ext()` with `enable_hmac_secret` parameter. When true, the CTAP2 `MakeCredential` command includes `extensions: {"hmac-secret": true}` so the credential can later produce deterministic HMAC outputs per salt. Phase 2 will add the full ECDH-encrypted salt exchange for `GetAssertion`.

### primalSpring scenario updated

Updated `beardog-fido2` scenario (Track: Security, Tier: Both):
- Method count: 3 → 4 (added `beardog.fido2.entropy`)
- Phase 5 added: entropy error shape validation
- Capability registry updated with `beardog.fido2.entropy`

### Test results

- **30 FIDO2-related tests pass** (15 handler tests + 15 Solo V2 provider/mock tests)
- **11,175 total workspace tests pass, 0 failures**

---

## PIXEL-STRONGBOX

### Android cross-compile fix

**Problem**: `beardog-hid` had `compile_error!` on `target_os = "android"`, blocking any Android FIDO2 build. Also, `open_device()` called `BearDogError::unsupported()` which doesn't exist (correct method: `unsupported_platform()`).

**Fix**: Replaced `compile_error!` with graceful empty-vec return from `discover()` and `unsupported_platform` error from `open_device()`. On Android, HID discovery returns zero devices — FIDO2 on Android uses the Android Keystore API, not raw HID.

**Result**: `cargo check --target aarch64-linux-android --features fido2` now compiles with **0 errors** (143 warnings, all pre-existing).

---

## Artifacts Changed

| File | Change |
|------|--------|
| `whitePaper/technical/HARDWARE_INVENTORY.md` | Reconciled to canonical single source |
| `bearDog/Cargo.toml` | `fido2` feature now includes `beardog-tunnel/ctap2` |
| `beardog-tunnel/.../fido2.rs` | New `beardog.fido2.entropy` method, authenticate uses `authenticate_with_credential` |
| `beardog-tunnel/.../provider.rs` | New `authenticate_with_credential()` stateless method |
| `beardog-tunnel/.../ctap2_protocol.rs` | `build_make_credential_ext()` with hmac-secret |
| `beardog-tunnel/.../hid_transport.rs` | Mock fields `pub(crate)`, import fix |
| `beardog-hid/src/lib.rs` | Android `compile_error!` → graceful empty, `unsupported_platform` fix |
| `primalSpring/.../s_beardog_fido2.rs` | Phase 5 (entropy), 4 methods |
| `primalSpring/config/capability_registry.toml` | `beardog.fido2.entropy` added |

---

## What's Next (Phase 1 hardware test)

With a SoloKey plugged into eastGate:

```bash
# Build with FIDO2 enabled
cargo build -p beardog --features fido2 --release

# Start bearDog
./target/release/beardog server --socket /tmp/beardog-test.sock

# Test discover
echo '{"jsonrpc":"2.0","id":1,"method":"beardog.fido2.discover"}' | socat - UNIX-CONNECT:/tmp/beardog-test.sock

# Test register (touch the key when it blinks)
echo '{"jsonrpc":"2.0","id":2,"method":"beardog.fido2.register","params":{"rp_id":"primals.eco","user_id":"dXNlcg==","user_name":"operator"}}' | socat - UNIX-CONNECT:/tmp/beardog-test.sock

# Test entropy harvest (touch again)
echo '{"jsonrpc":"2.0","id":3,"method":"beardog.fido2.entropy","params":{"rp_id":"primals.eco","credential_id":"<from_register_response>"}}' | socat - UNIX-CONNECT:/tmp/beardog-test.sock
```

Phase 2: Wire `beardog.fido2.entropy` output into the entropy hierarchy manager as a Tier 2 source. Currently the entropy orchestrator falls back to OS RNG — the plumbing is ready.
