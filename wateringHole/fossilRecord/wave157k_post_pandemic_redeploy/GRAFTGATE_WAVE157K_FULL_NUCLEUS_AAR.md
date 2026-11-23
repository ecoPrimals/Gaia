# graftGate + iosGate — Full NUCLEUS AAR

**Date**: Aug 12, 2026 | **Wave**: 157k | **From**: graftGate
**Status**: **FULL NUCLEUS LIVE (21 capabilities ACTIVE). iosGate mesh discovery LIVE on WiFi LAN. First `aarch64-apple-ios` mesh probe successful.**

---

## What Went Well

### 1. Full NUCLEUS Bootstrap via biomeOS

`biomeos nucleus start --mode full` orchestrated the entire primal stack from scratch in under 60 seconds. 12 primals launched sequentially (bearDog → songBird → skunkBat → toadStool → coralReef → barraCuda → nestGate → rhizoCrypt → loamSpine → sweetGrass → squirrel → petalTongue), with biomeOS handling health checks, socket registration, and capability auto-discovery.

**Result**: 1830 capabilities from 19 logical primals. 36 Unix domain sockets in `/tmp/eco/membrane/`. 21 capability domains transitioned to ACTIVE.

### 2. Tower Atomic iOS Cross-Compilation

All 4 Tower Atomic + gossip binaries compiled and linked successfully for `aarch64-apple-ios`:

| Binary | Size | Toolchain | Status |
|--------|------|-----------|--------|
| beardog | 6.3M | 1.93.0 | Links against iPhoneOS26.5.sdk |
| songbird | 17M | 1.94.0 | Required `rustup target add` for 1.94.0 |
| skunkbat | 2.6M | stable | Clean first try |
| swarmvine | 2.1M | stable | Clean first try |

### 3. iosGate Deployment Pipeline

Complete iOS deployment pipeline validated: Xcode project generation (xcodegen) → automatic signing (free tier) → `devicectl install` → `devicectl process launch`. Two apps deployed:
- `eco.primals.beardog` (PID 557) — stub primal proof
- `eco.primals.iosgate` (PID 603) — mesh discovery app with WiFi LAN probing

### 4. WiFi LAN Peer Discovery from iPhone

iosGate mesh app successfully probes all known gate IPs over WiFi LAN using Apple's Network.framework (`NWConnection` TCP probes + `NWBrowser` Bonjour). No USB tether required for network access — the iPhone reaches the mesh over WiFi.

### 5. Depot Push (15 binaries, 2 rounds)

Both initial (Wave 157i) and refreshed (Wave 157k) depot pushes completed cleanly. 15 `aarch64-apple-darwin` binaries at `/opt/ecoPrimals/plasmidBin/primals/aarch64-apple-darwin/` on golgiBody (104M).

### 6. songBird LAN Discovery

7 unique peers discovered within seconds of songBird startup: westGate, ironGate (×2), sporeGate (×2), blueGate, southGate, eastGate, plus graftGate itself. Federation connections arriving from 6 LAN IPs.

---

## Divergences & Issues Found

### D1. macOS `SUN_LEN` Socket Path Limit (104 bytes)

**Problem**: macOS `$TMPDIR` is `/var/folders/zj/8rpm0b413pzc7s_w3j6z33200000gn/T/` (49 chars). Combined with primal socket names (e.g., `swarmvine-graftGate.tarpc.sock`), total path exceeds the 104-byte `SUN_LEN` limit. swarmVine, skunkBat tarpc sockets all failed with `path must be shorter than SUN_LEN`.

**Fix applied**: Override `TMPDIR=/tmp` and `XDG_RUNTIME_DIR=/tmp/eco` for all primal processes. Sockets land in `/tmp/eco/membrane/` (short prefix).

**Upstream recommendation**: All primals should detect macOS and automatically shorten socket paths. The `sourdough-core` `SocketConfig` could enforce `SUN_LEN` compliance at construction time.

### D2. `barracuda` Binary Name Mismatch

**Problem**: biomeOS NUCLEUS expects a binary named `barracuda` but the actual binary is `validate_gpu`. Bootstrap fails with `Binary not found for primal: barracuda`.

**Fix applied**: `sudo ln -sf ~/.local/bin/validate_gpu /usr/local/bin/barracuda`

**Upstream recommendation**: Either rename the barraCuda binary output to `barracuda` in `Cargo.toml` or teach biomeOS to resolve binary name aliases.

### D3. `codesign` Hangs in Headless/CLI Contexts

**Problem**: First `codesign` invocation for a new signing identity triggers a macOS keychain dialog (`codesign wants to sign using key "..." in your keychain`). This blocks indefinitely in headless/SSH/agent contexts until a human clicks "Always Allow" in the GUI.

**Impact**: Cannot automate iOS signing in CI without pre-authorizing keychain access.

**Workaround**: Run `security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "<password>" login.keychain-db` with the keychain password. Or: first codesign must be interactive.

### D4. Apple WWDR Certificates Not Pre-Installed

**Problem**: After Xcode registered the Apple ID and generated a development certificate, `security find-identity -v` showed 0 valid identities. The Apple WWDR intermediate certificates (G3/G6) were missing from the keychain, breaking the trust chain.

**Fix applied**: Downloaded and imported `AppleWWDRCAG3.cer`, `AppleWWDRCAG6.cer`, and `AppleIncRootCertificate.cer` into `login.keychain-db`.

**Upstream recommendation**: Document this as a darwin gate setup step. Xcode usually handles this automatically but may not when adding accounts via CLI or automated flows.

### D5. songBird ↔ bearDog Security Provider Connection

**Problem**: songBird federation module fails to connect to bearDog's security provider socket, even when the socket exists and bearDog is healthy. Error: `Failed to connect to SECURITY_PROVIDER_SOCKET: security provider socket not accessible`. Falls back to plaintext discovery.

**Impact**: Federation runs unencrypted on LAN (functional but not sovereign). Does not affect IPC over Unix sockets (which are local-only).

**Possible cause**: BTSP handshake mismatch between songBird's federation module and bearDog's production mode. songBird may be attempting a plain JSON-RPC health check against a BTSP-enforcing socket.

### D6. biomeOS `security` Capability Resurrection Loop

**Problem**: biomeOS maps a generic `security.sock` symlink to skunkBat. Periodic health pings via plain JSON-RPC fail because skunkBat uses tarpc binary protocol on that socket. biomeOS marks `security` as DEGRADED and enters a resurrection loop, trying to respawn `/usr/bin/security` (the macOS Keychain CLI tool, not skunkBat).

**Impact**: Cosmetic — `security` capability oscillates between ACTIVE and DEGRADED. skunkBat itself remains healthy.

**Upstream recommendation**: biomeOS should resolve `security.sock` symlink to the actual binary (skunkBat) and use the correct health-check protocol (tarpc or the skunkBat-specific health endpoint).

### D7. `PATH` Not Available in `screen` Sessions

**Problem**: `~/.local/bin` is in the user's login shell PATH but not inherited by `screen -dmS` sessions. biomeOS couldn't find any primal binaries.

**Fix applied**: Symlinked all 15 primal binaries to `/usr/local/bin/`.

**Upstream recommendation**: biomeOS should accept a `--bin-dir` flag or `PRIMAL_BIN_DIR` env var to specify the binary search path, rather than relying on `$PATH`.

### D8. Apple Developer Program Enrollment Delay

**Problem**: Individual enrollment submitted but stuck in "account in process" status for multiple days. Apple says to contact them. Free provisioning (7-day profiles) works as a fallback.

**Impact**: No App Store distribution. Free provisioning profiles expire after 7 days and must be re-signed. Limited to 3 app IDs.

**Workaround**: Using Xcode automatic free provisioning for device-local deployment. Sufficient for iosGate development.

### D9. iOS Developer Mode Requires Physical Interaction

**Problem**: Developer Mode must be enabled on the iPhone via Settings → Privacy & Security → Developer Mode, followed by a device restart and confirmation tap. Cannot be done remotely.

**Impact**: Every new iOS test device requires physical hands-on setup.

### D10. songBird iOS Toolchain Target Missing

**Problem**: songBird's `rust-toolchain.toml` pins to 1.94.0 but doesn't list targets. The `aarch64-apple-ios` target was not installed for that toolchain, causing `can't find crate for 'core'` on first iOS build.

**Fix applied**: `rustup target add aarch64-apple-ios --toolchain 1.94.0`

**Upstream recommendation**: Add `targets` array to songBird's `rust-toolchain.toml` like bearDog's (which already includes `aarch64-apple-darwin` + `aarch64-apple-ios`).

---

## Deployment State

### graftGate (M4 Mac Mini)

| Metric | Value |
|--------|-------|
| Primals running | 13 processes (biomeOS-managed) |
| Capabilities | 1830 registered, 21 domains ACTIVE |
| Sockets | 36 in `/tmp/eco/membrane/` |
| WireGuard | LIVE (`10.13.37.13`, handshake active) |
| LAN peers | 7 discovered (6 unique gates) |
| Depot | 15 binaries on golgiBody (104M, refreshed Aug 12) |
| Gossip | swarmVine port 7800, `endpoint.alive` injected |

### iosGate (iPhone XS)

| Metric | Value |
|--------|-------|
| Apps installed | 2 (`eco.primals.beardog`, `eco.primals.iosgate`) |
| Active PID | 603 (iosGate mesh discovery) |
| WiFi LAN | Active, probing 7 gate IPs |
| iOS binaries built | 4 (beardog 6.3M, songbird 17M, skunkbat 2.6M, swarmvine 2.1M) |
| Signing | `Apple Development: eco.primal@pm.me (4DMC3GXQ65)` |
| Provisioning | Xcode automatic (free, 7-day expiry) |

### ACTIVE Capability Domains (21)

beardog, btsp, coralreef, crypto, dag, ed25519, ledger, loamspine, nestgate, network, permanence, petaltongue, rhizocrypt, security, skunkbat, songbird, swarmvine, sweetgrass, toadstool, visualization, x25519

---

## sourDough Code Team Status

- Service template module: SHIPPED (`028f0cc`)
- All tests pass (14 + 5 doctests)
- Binary v0.4.0, doctor clean
- No open P0/P1/P2

---

## Next Steps

1. **songBird `rust-toolchain.toml`** — push iOS + darwin targets upstream (like bearDog `02ce113`)
2. **Embed Rust binaries in iOS app** — link bearDog + songBird as C libraries for on-device IPC
3. **iosGate full Tower Atomic** — bearDog crypto + songBird federation running natively on iPhone
4. **launchd service templates** — use sourDough's service module for persistent graftGate NUCLEUS
5. **Fix D5** — songBird ↔ bearDog BTSP federation security handshake
6. **Fix D6** — biomeOS security capability health-check protocol detection

---

*graftGate — Full NUCLEUS live (21 ACTIVE domains, 1830 capabilities, 13 primals). iosGate mesh discovery live on WiFi LAN (2 apps, PID 603). 4 iOS Rust binaries built. 10 divergences documented. sourDough clean. Wave 157k.*
