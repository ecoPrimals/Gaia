# Wave 97 — sourDough Convergent Evolution Blurbs
**Date**: 2026-06-08
**From**: eastGate / primalSpring overwatch
**Context**: sourDough has absorbed the canonical TransportEndpoint pattern, scaffold templates now emit transport-injected primals, and `sourdough validate transport` can audit any primal. Cross-arch deployment to Pixel 8 (aarch64-linux-android) validated.

---

## sourDough Team

**Status**: v0.3.1 — transport absorption complete, cross-arch proven

**What shipped**:
- `sourdough-core::TransportEndpoint` — wire-compatible with `songbird_types::TransportEndpoint` (same serde tagged format: `uds`/`tcp`/`mesh_relay`)
- `connect_transport()` — connects to any resolved endpoint without knowing the transport
- `IpcClient` — transport-aware JSON-RPC 2.0 client (replaces raw socket code)
- `TransportStream` — unified async read/write across UDS and TCP
- Scaffold templates now emit transport-injected primals: `TRANSPORT_ENDPOINT` env var / CLI flag, no more hardcoded `TcpListener::bind` or `UnixListener::bind`
- `sourdough validate transport` — audits any primal for transport compliance (self-binding anti-patterns, injection patterns, platform guards)
- Release CI matrix includes `aarch64-linux-android` target
- systemd template uses `TRANSPORT_ENDPOINT` JSON instead of `--socket` flag
- Successfully cross-compiled and deployed to Pixel 8 (GrapheneOS, aarch64-linux-android)
- Depot updated: `primals/x86_64-unknown-linux-musl/sourdough` + new `primals/aarch64-linux-android/sourdough`

**Remaining work**:
- `sourdough migrate transport` (v0.4+) — automated migration tool for existing primals
- Run `sourdough validate transport` against all 13 remaining primals and file compliance reports
- Scaffold a test primal using the new templates and validate full lifecycle on Pixel 8

---

## beardog Team

**Status**: `capability.call` shipped (Wave 94) — cross-arch blocker remains

**Blocker**: `beardog-security` fails to compile for `aarch64-linux-android`:
```
error[E0425]: cannot find value `android_device_count` in this scope
```
This is in a `#[cfg(target_os = "android")]` code path. Needs either a proper implementation or a `#[cfg]` gate that stubs it on Android.

**Action**: Fix the `android_device_count` compile error so beardog can deploy to Pixel 8. All other primals cross-compile clean.

---

## songBird Team

**Status**: SB-TLS-LAN-01 and SB-STARTUP-01 fixes shipped (Wave 96) — depot refreshed

**What's validated**:
- Updated songbird binary in depot (`x86_64-unknown-linux-musl`)
- sourDough now uses songbird-compatible `TransportEndpoint` wire format
- `ipc.resolve` response format is consumed by `sourdough-core::IpcClient`

**Next**: songbird should expose `ipc.register` for primals to register capabilities at startup. sourDough scaffold templates are ready to emit `ipc.register` calls — waiting on songbird to implement the method.

---

## cellMembrane / ironGate Team

**Status**: Deployment validation passed (Wave 95 ACK)

**What's new**:
- sourDough v0.3.1 in depot with transport injection support
- New `aarch64-linux-android` depot directory available
- `sourdough validate transport` can audit primals deployed via cellMembrane

**Action**: 
1. Deploy updated sourDough from depot to ironGate
2. Run `sourdough validate transport .` against any primal codebase on ironGate to verify transport compliance
3. Test `TRANSPORT_ENDPOINT` env var injection in your launcher scripts

---

## hotSpring / strandGate Team

**Status**: Mesh ACK (Wave 95) — redeploy validated

**What's new**:
- sourDough v0.3.1 available in depot
- All scaffold templates now emit transport-agnostic primals
- `sourdough validate transport` available for compliance auditing

**Action**: Pull updated sourDough from depot, run `sourdough validate transport` against local primals to identify any remaining self-binding patterns before the transport injection evolution wave.
