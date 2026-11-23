# Wave 98 — Ecosystem Blurbs
**Date**: 2026-06-08
**From**: eastGate overwatch

---

## songBird Team

sourDough now has a wire-compatible `TransportEndpoint` (same serde tagged format as `songbird_types::TransportEndpoint`). Scaffold templates emit primals that accept `TRANSPORT_ENDPOINT` env var. The ecosystem is ready to consume structured endpoints.

**Action**: Implement `ipc.resolve` returning `TransportEndpoint` JSON. This is the Phase 2 M1 gate — once songbird returns structured endpoints, all 14 primals can adopt transport injection. sourDough's `IpcClient` already consumes the format. Also: implement `ipc.register` so primals can register capabilities at startup (scaffold templates are ready to emit the call).

NUCLEUS tower is live on eastGate (beardog + songbird + skunkbat, UDS-only). Songbird socket is at `/run/user/1000/biomeos/songbird.sock` and responding to `health.liveness`.

---

## bearDog Team

`capability.call` is proven and deployed. Tower Atomic is live on eastGate.

**Action**: Fix `beardog-security` compile error for `aarch64-linux-android`:
```
error[E0425]: cannot find value `android_device_count` in this scope
```
This blocks beardog deployment to Pixel 8. All other primals (including sourDough) cross-compile clean for Android. Needs a `#[cfg(target_os = "android")]` gate or stub implementation.

Secondary: beardog socket is not appearing at `/run/user/1000/biomeos/beardog.sock` after NUCLEUS tower deploy (process is running but socket absent). May need UDS bind path fix.

---

## sweetGrass Team

strandGate audit (Wave 97) flagged `ring` in your dev-dependency tree via `testcontainers → bollard → rustls`. Production binary is pure Rust, but the dev-dep chain:
1. Breaks ecoBin cross-arch (ring fails on aarch64-linux-android)
2. Violates Tower Atomic security posture — all crypto routes through bearDog

**Action**: Remove `testcontainers` + `bollard` from dev-deps (replace with mock/stub). Verify: `cargo tree -i ring --no-dev` returns empty. Run `sourdough validate ecobin` to confirm clean. All crypto operations should use `capability.call(capability='crypto')` via bearDog.

---

## cellMembrane / ironGate Team

Good evolution incoming — we see `transport.rs` absorbed into `cellmembrane-types` and harvest improvements. NUCLEUS tower redeployed from plasmidBin on eastGate (3/3 primals running).

**Action**:
1. Pull updated sourDough from depot (musl segfault FIXED — now static-pie linked)
2. Run `sourdough validate transport .` on ironGate to verify transport compliance
3. Deploy updated sourDough from depot and validate `sourdough --version` returns `0.3.1`
4. Test `TRANSPORT_ENDPOINT` env var injection in your launcher scripts — scaffold templates now emit primals that accept it

The `aarch64-linux-android` depot directory is live with sourDough. Once beardog Android fix ships, full cross-arch depot is available.

---

## hotSpring / strandGate Team

ACK received (Wave 97) — transport audit results noted. 5/5 primals clean for self-binding. sourDough musl segfault is FIXED (static-pie rebuild in depot).

**Action**:
1. Pull fresh sourDough from depot (the segfault is fixed)
2. `cargo fmt` across 5 primals (flagged in audit)
3. Add `[[bin]]` sections to workspace Cargo.toml for UniBin compliance
4. When songbird ships `ipc.resolve` with structured endpoints, adopt `TransportEndpoint` in primal server code

---

## sourDough Team (self / evolution team)

Wave 97 complete. v0.3.1 with transport absorption deployed to depot (musl + Android). All scaffold templates emit transport-injected primals. `sourdough validate transport` operational.

**Remaining**:
- `sourdough migrate transport` (v0.4+) — automated migration tool for existing primals
- Run transport audit against all 14 primals and publish compliance report
- Scaffold a test primal from new templates, cross-compile for Android, deploy to Pixel 8 to validate full lifecycle
