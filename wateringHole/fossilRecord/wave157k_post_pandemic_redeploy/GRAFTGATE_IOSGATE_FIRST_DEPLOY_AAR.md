# graftGate + iosGate — First iOS Deploy AAR

**Date**: Aug 12, 2026 | **Wave**: 157k | **From**: graftGate
**Status**: **iosGate LIVE. First `aarch64-apple-ios` primal deployed to iPhone XS. Tower Atomic running on graftGate. Full NUCLEUS deployment in progress.**

---

## iosGate — FIRST DEPLOY

| Property | Value |
|----------|-------|
| Device | iPhone XS (iPhone11,2) |
| CPU | arm64e |
| iOS | 18.5 (22F76) |
| UDID | `00008020-001E68D00A3A002E` |
| Serial | GR4G809UKPFV |
| Connection | USB wired → graftGate (M4 Mac Mini) |
| Bundle ID | `eco.primals.beardog` |
| PID | 557 |
| Signing | `Apple Development: eco.primal@pm.me (4DMC3GXQ65)` |
| Team ID | `XGZY4H3HRW` |
| Provisioning | Xcode automatic (free tier — paid enrollment pending Apple review) |

### What was deployed

BearDogApp — a stub iOS app signed with our development certificate, installed and launched via `devicectl`. First proof that ecoPrimals binaries can be built, signed, and deployed to physical iOS hardware from graftGate.

### Path to full iosGate

The Tower Atomic (bearDog + songBird) on iosGate would enable the iPhone XS to join the mesh as a WiFi LAN peer instead of requiring USB tether. Roadmap:

1. **bearDog iOS** — Rust binary compiles and links for `aarch64-apple-ios` (validated)
2. **songBird iOS** — Network discovery + federation over WiFi LAN
3. **swarmVine iOS** — Gossip injection from mobile device
4. **biomeOS iOS** — Neural API routing on-device

### macOS build notes

- **Socket path length**: macOS `SUN_LEN` limit (104 bytes) requires `/tmp/eco/` paths instead of `$TMPDIR` (49 chars on macOS)
- **Keychain access**: `codesign` requires GUI approval for first keychain access — blocks in headless/CI contexts
- **Free provisioning**: Works for device-local development without paid enrollment. Profile valid 7 days, apps expire if not re-signed.
- **Developer Mode**: Must be enabled on iOS device (Settings → Privacy & Security → Developer Mode)
- **Device trust**: Profile must be trusted on-device (Settings → General → VPN & Device Management)

---

## graftGate — Tower Atomic LIVE

| Primal | PID | Socket | Status |
|--------|-----|--------|--------|
| bearDog | 4157 | `/tmp/eco/beardog-graftGate.sock` | RUNNING (daemon) |
| songBird | 4234 | `/tmp/eco/songbird.sock` | RUNNING (screen) |
| skunkBat | 4347 | `/tmp/eco/biomeos/skunkbat-graftGate.sock` | RUNNING (screen) |
| swarmVine | 4348 | `/tmp/eco/biomeos/swarmvine-graftGate.sock` | RUNNING (screen) |

### LAN peer discovery (via songBird)

| Peer | Identity |
|------|----------|
| westgate | westGate |
| pop-os (×2) | ironGate + southGate |
| sporeGate | sporeGate (multi-instance) |
| DESKTOP-9QG6LQL | blueGate (Windows) |
| integration-node | eastGate |
| songbird | sporeGate secondary |

6 unique gates discovered on LAN within seconds of songBird startup.

---

## Next: Full NUCLEUS on graftGate + iosGate

Tower Atomic is live. Remaining NUCLEUS primals to deploy on graftGate:
- biomeOS (Neural API routing)
- nestGate (storage CAS)
- squirrel (AI orchestration)
- rhizoCrypt, loamSpine, sweetGrass (provenance trio)
- toadStool, barraCuda, coralReef (compute trio)
- petalTongue (HTTP gateway)
- sourDough (tooling — our code team)

Goal: Full inner membrane on graftGate, then progressively deploy primals to iosGate over WiFi LAN.

---

*graftGate + iosGate — first `aarch64-apple-ios` deploy. BearDogApp PID 557 on iPhone XS. Tower Atomic live on M4. 6 LAN peers. Full NUCLEUS deployment in progress. Wave 157k.*
