# graftGate Wave 157k — Post-Pandemic Redeploy AAR

**Date**: Aug 12, 2026 | **Wave**: 157k | **From**: graftGate
**Gate**: graftGate (M4 Mac Mini, `aarch64-apple-darwin`)
**Code Team**: sourDough
**Status**: **REDEPLOYED. Tower Atomic LIVE. 6 LAN peers discovered. Depot refreshed.**

---

## Actions Completed

### 1. Cascade Pull — 9 repos updated

barraCuda, bearDog, biomeOS, nestGate, petalTongue, swarmVine, toadStool, primalSpring, wateringHole all pulled with significant changes (songBird MeshRelay, new gossip surfaces, etc).

### 2. Full Rebuild — 15/15 Clean

All 15 primals rebuilt from latest source in ~10 minutes. Zero failures.

### 3. Depot Push — 15 binaries refreshed on golgiBody

All 15 `aarch64-apple-darwin` binaries pushed to `/opt/ecoPrimals/plasmidBin/primals/aarch64-apple-darwin/` (104M total). Timestamps: Aug 12 13:21 UTC.

### 4. NUCLEUS Redeploy — 15 binaries in `~/.local/bin`

All 15 binaries deployed locally (105M total including `squirrel-cli`).

### 5. Tower Atomic — LIVE

| Primal | Status | Socket |
|--------|--------|--------|
| bearDog | RUNNING (daemon) | `/tmp/eco/beardog-graftGate.sock` |
| songBird | RUNNING (screen) | `/tmp/eco/songbird.sock` |
| skunkBat | RUNNING (screen) | `/tmp/eco/biomeos/skunkbat-graftGate.sock` |
| swarmVine | RUNNING (screen) | `/tmp/eco/biomeos/swarmvine-graftGate.sock` |

Capability symlinks created: crypto, security, btsp, ed25519, x25519, network.

### 6. Gossip — swarmVine injected `endpoint.alive`

- swarmVine listening on port 7800 for cross-gate gossip
- `endpoint.alive` gossip entry injected for graftGate
- songBird registered as discovery service

### 7. LAN Peer Discovery — 6 peers found

| Peer | LAN IP | Port |
|------|--------|------|
| westGate | 192.168.4.149 | 7700 |
| ironGate (pop-os) | 192.168.4.237 | 7700 |
| sporeGate | 192.168.4.3 | 7700-7702 |
| blueGate (DESKTOP-9QG6LQL) | 192.168.4.212 | 7700 |
| southGate (pop-os) | 192.168.4.244 | 7700 |
| eastGate (integration-node) | 192.168.4.148 | 7700 |

Federation connections arriving from all 6 peers within seconds of songBird startup.

---

## sourDough Code Team Status

- **Service template module**: SHIPPED (`028f0cc` — cross-platform systemd + launchd)
- **Tests**: All passing (14 passed including 5 doctests)
- **Binary**: v0.4.0, doctor clean
- **No open P0/P1/P2 items**

---

## Notes

- **Socket path length**: macOS `SUN_LEN` limit requires short paths. Resolved by using `/tmp/eco/` instead of `$TMPDIR` (which is 49 chars on macOS).
- **bearDog federation security**: songBird falls back to plaintext discovery (security provider socket validation check fails despite bearDog running). Functional but not encrypted. Non-blocking for LAN mesh.
- **WireGuard**: Handshake active, ICMP filtered (mesh peers not pingable but tunnel up).
- **Xcode 26.6**: Installed, iOS SDK `iPhoneOS26.5.sdk` available. iOS cross-compile tested (bearDog links successfully).

---

*graftGate — Wave 157k redeploy complete. 15/15 rebuilt, depot pushed, Tower Atomic live, 6 LAN peers. sourDough code team: service template shipped, clean. 0/0/0.*
