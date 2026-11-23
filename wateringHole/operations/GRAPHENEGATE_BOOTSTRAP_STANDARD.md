# grapheneGate Bootstrap Standard — Physical Dark Forest Protocol

**Status**: LIVE (Wave 132h, reviewed 155h — Tower deployed, nucleus_launcher cross-compiled, ADB tether operational)
**Owner**: eastGate (overwatch)
**Hardware**: Pixel 8a, Google Tensor G3, 8GB RAM, GrapheneOS
**Gate class**: `portable_anchor`

> **Wave 132h status**: Tower composition (bearDog + songBird + skunkBat) deployed and reachable via ADB port forwarding. 15/15 aarch64-musl binaries in depot (14 primals + nucleus_launcher). LAUNCHER-01 complete: `nucleus_launcher` cross-compiled and published to pepti warehouse. grapheneGate also serves as USB tether for eastGate internet connectivity. Enrolled in `mesh_topology.toml` with `transport = "adb"`, role `mobile`. As the tether matures, grapheneGate can spawn new mesh connections and relay for gates that lack WAN.

---

## Current Operational State (Wave 132c)

| Component | Status |
|-----------|--------|
| ADB connectivity | LIVE (device 44251JEKB04957) |
| Tower composition (bearDog+songBird+skunkBat) | RUNNING (PIDs active) |
| ADB port forwarding (9100, 9200, 9140) | ACTIVE |
| USB tethering (eastGate internet) | ACTIVE |
| aarch64-musl binaries in depot | **15/15** (14 primals + nucleus_launcher) |
| mesh_topology.toml enrollment | DONE (transport=adb, role=mobile, zone=Wan) |
| primalSpring validation scenario | PASSING (s_graphenegate_readiness) |

### Tether + Gate Duality

grapheneGate simultaneously:
1. **Provides internet** to eastGate via USB tethering (cellular → USB RNDIS)
2. **Runs Tower primals** accessible over ADB port forwarding
3. **Can relay mesh traffic** for other gates when WAN is unavailable

This dual role means grapheneGate is both infrastructure (tether) and compute (gate).
As the connection matures, songBird on grapheneGate can accept mesh.peer connections
from other gates, effectively turning the phone into a WAN relay without needing
golgi or any VPS. The cellular connection becomes sovereign backhaul.

---

## Purpose

grapheneGate is the ecosystem's **portable physical root of trust**. It bridges
the gap between the stationary gate mesh (LAN/WAN hardware) and the operator's
physical presence. Wherever the operator carries grapheneGate, it can:

1. Prove family membership via encrypted BirdSong beacon
2. Bootstrap new gates on arbitrary hardware
3. Relay mesh traffic through hostile networks

grapheneGate is **not a general-purpose compute node**. It runs minimal Tower
Atomic (BearDog + Songbird + SkunkBat) — the trust perimeter, not the payload.

---

## Trust Model

### Physical Root of Trust Chain

```
Operator physical possession of Pixel 8a
    ↓
GrapheneOS verified boot + Titan M2 secure element
    ↓
BearDog keystore (Android Keymaster / StrongBox backed)
    ├── FAMILY_SEED → HKDF → BTSP session keys
    ├── Beacon seed (MitoBeacon) → BirdSong encrypted discovery
    └── Lineage seed (nuclear) → device-unique identity
    ↓
Songbird → beacon broadcast + mesh federation
    ↓
SkunkBat → audit trail of all trust operations
```

### Why a Phone

| Property | Benefit |
|----------|---------|
| Always carried | Physical colocation = proof of operator presence |
| Hardware secure element (Titan M2) | Key material bound to hardware; extraction-resistant |
| GrapheneOS | No Google services, minimal attack surface, verified boot |
| Cellular + WiFi | Network flexibility; operates on any substrate |
| Appears normal | Under scrutiny, looks like a standard Android device |
| USB-C tethering | Can bridge to gate hardware without WiFi |

---

## Three-Role Evolution

### Role 1 — Physical Dark Forest Beacon (Immediate)

grapheneGate carries beacon and lineage seeds on a hardened mobile OS.
BearDog broadcasts encrypted BirdSong beacons on the local network.

**Operational flow:**
1. Operator arrives at location with grapheneGate
2. grapheneGate connects to local WiFi (or USB tethers to target hardware)
3. BearDog broadcasts ChaCha20-encrypted UDP beacon on LAN
4. Existing gates (or new hardware with plasmidBin) detect beacon
5. Beacon decryption proves family membership (shared beacon seed)
6. BearDog lineage exchange verifies device identity + permission level
7. BTSP session established — gate joins mesh

**What outsiders see:** Encrypted UDP noise, indistinguishable from random data.
No port scanning reveals ecosystem. Dark Forest Pillar 1 (zero metadata leakage).

**Overseas scenario:**
- Arrive at foreign location with rented/purchased hardware
- Connect grapheneGate to hardware via USB-C or shared WiFi
- `plasmidbin bootstrap --beacon-seed` on new hardware
- grapheneGate's BirdSong beacon authenticates the new gate
- New gate pulls ecosystem manifest, clones repos, deploys NUCLEUS
- All traffic routes through BTSP — local network sees encrypted noise

### Role 2 — BTSP Relay Bootstrap (Near-term)

grapheneGate runs minimal Tower Atomic and can act as a relay when VPS
infrastructure is unavailable.

**Use cases:**
- New jurisdiction where VPS providers are untrusted or blocked
- Network partition: home mesh unreachable, need local relay
- Initial bootstrap before VPS is provisioned

**Architecture:**
```
[grapheneGate — Phone]
  BearDog: key management + BTSP
  Songbird: TURN relay on phone's IP (cellular or WiFi)
  SkunkBat: audit logging

        ↕ BTSP E2E encrypted

[New gate — local hardware]
  Bootstraps through grapheneGate's Songbird relay
  Once VPS relay is reachable, migrates federation to VPS
  grapheneGate becomes optional (mesh is self-sustaining)
```

**Songbird on phone:**
- Listens on abstract socket (Android SELinux compatible, validated in ecoBin v2.0)
- Exposes TURN relay on local network for gate-to-gate traffic
- Federates with home mesh via cellular data when WiFi is hostile

### Role 3 — Sovereign Mesh Seed (Horizon)

grapheneGate as the **sole requirement** to bootstrap an entire ecosystem
instance from scratch.

**What grapheneGate carries:**
- `FAMILY_SEED` (in hardware-backed keystore, never extractable)
- Lineage seeds for known devices
- `ecosystem_manifest.toml` (repo list, gate profiles)
- `plasmidBin` binary (aarch64-android)
- `ecoBins` — compiled primals for target architectures
- Latest `wateringHole` snapshot (impulses, standards, handoffs)

**Bootstrap from zero:**
```bash
# On any Linux machine with USB:
adb shell plasmidbin bootstrap --from-graphene \
    --target $(hostname) \
    --gate-class lan_cluster

# grapheneGate:
# 1. Authenticates operator via biometric + BTSP
# 2. Exports encrypted bootstrap bundle to target
# 3. Target decrypts with BTSP session key
# 4. plasmidBin installs NUCLEUS from ecoBins
# 5. BearDog receives lineage seed for new gate
# 6. Songbird federates with home mesh (if reachable)
# 7. temporal.cascade syncs repos from nearest peer
```

**Scrutiny resistance:**
- Phone appears as standard Pixel 8a running GrapheneOS
- No ecosystem apps visible in launcher (background service only)
- BearDog data encrypted at rest with hardware-backed keys
- No ecosystem artifacts discoverable without BTSP authentication
- Duress mode (future): secondary BTSP passphrase yields decoy profile

---

## Network Profiles

| Scenario | Network | Federation Path | Trust Level |
|----------|---------|-----------------|-------------|
| Home LAN (WiFi) | 192.168.1.x / 4.x | Direct beacon + UDS-over-USB | Covalent |
| Home LAN (USB tether) | USB RNDIS | Direct UDS | Covalent |
| Remote WiFi (trusted) | Foreign subnet | TURN via cellular → home VPS | Covalent through relay |
| Remote WiFi (hostile) | Captive portal / monitored | BTSP over TURN, zero metadata | Covalent through relay |
| Cellular only | Mobile carrier | TURN → home VPS → mesh | Covalent through relay |
| Airgap (USB only) | No network | USB bootstrap bundle transfer | Covalent (offline) |

---

## Security Invariants

1. **FAMILY_SEED never leaves hardware secure element** — derived keys only
2. **Beacon seed shared via out-of-band provisioning** — never over network
3. **Lineage seed unique per device** — grapheneGate's identity is non-transferable
4. **All network traffic BTSP-encrypted** — observers see random noise
5. **No persistent network identity** — IP/MAC change does not break trust
6. **Beacon broadcasts time-limited** — automatic expiry, no permanent advertisement
7. **SkunkBat audit trail** — every trust operation logged locally
8. **Verified boot chain** — GrapheneOS -> Titan M2 -> BearDog keystore

---

## Prerequisites

| Requirement | Status | Notes |
|-------------|--------|-------|
| GrapheneOS installed on Pixel 8a | DONE | Currently plugged into eastGate (tether + gate) |
| BearDog deployed on Android | **DONE** | aarch64-musl static binary, TCP fallback mode |
| aarch64-android build target | CONFIGURED | `.cargo/config.toml` has target |
| ecoBin abstract socket transport | DONE | Driven by GrapheneOS SELinux constraints |
| BirdSong beacon broadcast | IMPLEMENTED | Two-seed genetics standard validated |
| Hardware-backed keystore integration | NOT STARTED | Android Keymaster / StrongBox API |
| plasmidBin aarch64-musl binaries | **14/14 BUILT** | Full depot: all primals built and deployable |
| TURN relay on Android | NOT TESTED | Songbird abstract socket -> network relay |
| deploy_pixel.sh handlers | **DONE** (Wave 99) | All 13+ primal startup handlers wired |
| ADB port forwarding | **DONE** (Wave 132c) | bearDog:9100, songBird:9200, skunkBat:9140 |
| USB tether dual-role | **LIVE** (Wave 132c) | Tether + gate simultaneously operational |

---

## Relation to Existing Standards

| Standard | Relation |
|----------|----------|
| `../foundations/DARK_FOREST_GLACIAL_GATE_STANDARD.md` | grapheneGate enforces all 5 pillars on mobile |
| `DARK_FOREST_BEACON_GENETICS_STANDARD.md` | Two-seed model: beacon (family) + lineage (device) |
| `../protocols/BTSP_PROTOCOL_STANDARD.md` | All grapheneGate sessions use BTSP |
| `../foundations/K_DERM_TOPOLOGY_STANDARD.md` | grapheneGate operates at plasma membrane boundary |
| `GATE_SETUP_STANDARD.md` | grapheneGate is a specialized gate; follows onboarding flow |
| `DISTRIBUTED_COVALENT_DEPLOYMENT.md` | grapheneGate extends the WAN covalent pattern |
| `../fossilRecord/wave150s_standards/ECOBIN_ARCHITECTURE_STANDARD.md` | ecoBin v2.0 abstract-socket already validated |

---

## Evolution Timeline

| Wave | Milestone | Status |
|------|-----------|--------|
| 68 | grapheneGate in ecosystem manifest + matrix | DONE |
| 68 | This bootstrap standard published | DONE |
| 99 | deploy_pixel.sh all 13 primal handlers | DONE |
| 103 | 3/14 aarch64 binaries in depot (songbird, skunkbat, sourdough) | DONE |
| 113 | bearDog pure Rust (aws-lc-rs eliminated) | DONE |
| 128 | Full aarch64 plasmidBin depot (14/14 binaries) | DONE |
| 132c | Tower deployed + ADB tether live | **DONE** |
| 132c | Enrolled in mesh_topology.toml (transport=adb) | **DONE** |
| NEXT | Role 1: beacon broadcast + lineage verification E2E test | P2 |
| NEXT | songBird mesh.peer via cellular (tether as relay) | P2 |
| TBD | BearDog Keymaster/StrongBox integration design | P3 |
| TBD | Role 2: BTSP relay on phone, bootstrap via USB | P3 |
| TBD | Role 3: full sovereign mesh seed | Horizon |

---

*Wave 132c. The phone is live: tether + gate + future relay. The mesh absorbs.*
