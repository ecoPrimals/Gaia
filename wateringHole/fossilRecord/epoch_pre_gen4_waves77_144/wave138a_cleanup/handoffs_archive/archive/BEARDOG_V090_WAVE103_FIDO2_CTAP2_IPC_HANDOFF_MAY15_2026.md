<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 Wave 103 Handoff — FIDO2/CTAP2 IPC Surface

**Date**: May 15, 2026
**Primal**: BearDog (crypto + identity)
**Audit Item**: UB-2 (MEDIUM) — FIDO2/CTAP2 protocol support
**Requestor**: primalSpring (lithoSpore upstream)

---

## Summary

Wave 103 exposes BearDog's existing CTAP2 infrastructure as JSON-RPC IPC
methods, enabling downstream primals to request hardware-attested signatures
from USB security keys without embedding HID or CTAP2 dependencies.

## Methods Added

| Method | CTAP2 Operation | Feature Gate |
|--------|----------------|--------------|
| `beardog.fido2.discover` | HID enumeration | `ctap2` (graceful fallback without) |
| `beardog.fido2.register` | `MakeCredential` | `ctap2` (error without) |
| `beardog.fido2.authenticate` | `GetAssertion` | `ctap2` (error without) |

## Architecture

```text
lithoSpore / downstream primal
  → JSON-RPC: beardog.fido2.authenticate(rp_id, credential_id, challenge)
    → Fido2Handler (unix_socket_ipc/handlers/fido2.rs)
      → SoloV2Provider::sign_with_device()
        → HidCtap2Transport (CTAPHID framing + reassembly)
          → USB HID (/dev/hidrawN) → SoloKey / YubiKey
            ← user touch → assertion signature
          ← CTAP2 response
        ← signature bytes
      ← base64 signature
    ← JSON-RPC response {signature, user_present, rp_id}
  ← hardware-attested signature for liveSpore.json
```

## Feature Gating

The `ctap2` feature in `beardog-tunnel` controls access to real hardware:

- **With `ctap2`**: Full CTAP2 path via `HidCtap2Transport` + `SoloV2Provider`
- **Without `ctap2`**: Discovery returns empty list with guidance note;
  register/authenticate return clear error with `--features ctap2` hint

This allows bearDog to advertise the FIDO2 capability surface even in builds
without HID access, while downstream primals can check availability via
`beardog.fido2.discover` before attempting operations.

## lithoSpore Integration Path

1. Call `beardog.fido2.discover` to check for connected security keys
2. If no credential exists: `beardog.fido2.register` with `rp_id: "primals.eco"`
3. For witness signatures: `beardog.fido2.authenticate` with challenge from
   spore chain hash — signature goes into `liveSpore.json` witness entry

## Files Changed

| File | Change |
|------|--------|
| `handlers/fido2.rs` | **NEW** — Handler module (discover/register/authenticate) |
| `handlers/mod.rs` | Module registration, `MethodHandlerKind::Fido2`, registry wiring |
| `capabilities.rs` | FIDO2 capability type + cost estimates |
| `STATUS.md` | Wave 103 entry, method count 123→126 |
| `CHANGELOG.md` | Wave 103 entry |

## Tests

12 new tests covering:
- Method list assertion (3 methods)
- Discovery response structure
- Parameter validation (6 tests: missing rp_id, user_id, user_name, credential_id, challenge, params)
- Handler routing (discover via handler)
- Unknown method error

## Quality Gates

- `cargo fmt --all`: clean
- `cargo clippy -p beardog-tunnel --lib -- -D warnings`: clean
- `RUSTDOCFLAGS="-D warnings" cargo doc --workspace --no-deps`: clean
- `cargo test --workspace`: 12 new FIDO2 tests pass; 1 pre-existing environment-dependent failure in `beardog-ipc` (`isomorphic::test_discover_beardog_endpoint_fails_without_service`)

## Known Limitations

1. **PIN/UV not implemented** — `SoloV2Provider` passes cached PIN as raw bytes
   into CBOR `pinUvAuthParam`, which is not spec-correct for devices requiring
   ClientPIN protocol. Phase 2 item.
2. **Single-device selection** — Auto-selection picks the first FIDO2 device;
   no multi-device arbitration. Callers can pass explicit `device_path`.
3. **No credential management** — Enumerate/delete resident keys not yet
   exposed as IPC methods.

## Downstream Impact

- **lithoSpore**: Can now wire `beardog.fido2.authenticate` into witness
  signature generation for `liveSpore.json` hardware-attested provenance.
- **primalSpring**: UB-2 audit item resolved at IPC surface level.
- **All primals**: FIDO2 capability advertised in `primal.capabilities` response.
