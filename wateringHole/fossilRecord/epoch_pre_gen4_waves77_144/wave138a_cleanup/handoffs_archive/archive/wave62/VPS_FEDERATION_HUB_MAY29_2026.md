# VPS Federation Hub — Tower Atomic Mesh + MitoBeacon

**Date:** 2026-05-29 (Wave 60)
**From:** eastGate (primalSpring coordination)
**To:** All gates

---

## What Changed

The VPS Tower Atomic triad is now complete:

| Service | Port | Status |
|---------|------|--------|
| BearDog (crypto spine) | UDS `/run/membrane/beardog.sock` | Running |
| Songbird (federation hub) | UDS + TCP `:7700` | **NEW — Running** |
| Songbird TURN (NAT relay) | TCP/UDP `:3478` | Running |
| skunkBat (audit/defense) | UDS `/run/membrane/skunkbat.sock` | Running |

Songbird on the VPS now operates in **dual-mode**:
- **UDS** for inter-primal IPC (local membrane NUCLEUS)
- **TCP :7700** for cross-gate federation mesh (LAN + WAN)

**Dark Forest mode enabled.** All BirdSong beacons are encrypted via BearDog crypto. No plaintext fallback.

**Node ID:** `golgiBody` — this is how the VPS appears in `discovery.peers`.

---

## Dual Membrane: SSH Shadow + Native Primal

Both auth layers run in parallel (sovereignty shadow pattern S5):

```
Outer membrane (SSH)               Native membrane (MitoBeacon)
├─ Forgejo SSH :2222               ├─ Songbird federation :7700
├─ authorized_keys                 ├─ BirdSong encrypted beacons
├─ OpenSSH dependency              ├─ BearDog ChaCha20-Poly1305
└─ Works today (nanowires)         └─ Growing underneath (genetic)
```

SSH remains the outer membrane for git push/pull. MitoBeacon/BirdSong is
the native membrane for discovery, federation, and capability routing.
As genetic auth proves out, SSH becomes fallback then dissolves.

---

## MitoBeacon Ecosystem Seed

An ecosystem-wide beacon seed has been generated on the VPS. This is the
mitochondrial DNA — shared across all family members for dark-forest
discovery.

| Field | Value |
|-------|-------|
| **Family name** | `ecoPrimals-membrane` |
| **Family ID** | `e8b62b6e` |
| **Beacon seed** | `JgWoO0wLgkig/oDn3Q/9o9s8eW4Tvew3XzwLpDZhls8=` |
| **Storage** | `/etc/membrane/family/` on VPS |

Per-gate lineage seeds (nuclear DNA — unique per device) are stored on
the VPS at `/etc/membrane/family/nodes/<gate>.lineage.seed`. These will
be distributed via secure channel (SSH session or BTSP tunnel) during
gate onboarding.

---

## Per-Gate Federation Config

Each section below is self-contained. Copy-paste the one for your gate.

### Environment Variables (all gates)

Add to `~/.bashrc` or gate environment file:

```bash
# MitoBeacon: ecosystem family membership
export FAMILY_SEED="JgWoO0wLgkig/oDn3Q/9o9s8eW4Tvew3XzwLpDZhls8="
export FAMILY_ID="e8b62b6e"

# Songbird federation: VPS mesh hub
export SONGBIRD_PEERS="golgiBody@[RELAY_PUBLIC]:7700"
export SONGBIRD_FEDERATION_PORT=7700
```

### eastGate

```bash
export SONGBIRD_NODE_ID="eastGate"
export GATE_NAME="eastGate"

# Lineage seed (nuclear DNA — unique to this gate)
# Retrieve from VPS: ssh root@[RELAY_PUBLIC] 'base64 -w0 /etc/membrane/family/nodes/eastGate.lineage.seed'
```

Start NUCLEUS with federation:

```bash
# plasmidBin path:
./nucleus_launcher.sh --family-id e8b62b6e \
  --peers "golgiBody@[RELAY_PUBLIC]:7700"

# OR Rust nucleus_launcher:
nucleus_launcher start --family-id e8b62b6e \
  --federation-port 7700 \
  --peers "golgiBody@[RELAY_PUBLIC]:7700"
```

Verify mesh connection:

```bash
# After NUCLEUS starts, check discovery
echo '{"jsonrpc":"2.0","method":"discovery.peers","id":1}' \
  | socat - UNIX-CONNECT:$XDG_RUNTIME_DIR/biomeos/songbird-e8b62b6e.sock
# Should show golgiBody in peer list
```

### ironGate

```bash
export SONGBIRD_NODE_ID="ironGate"
export GATE_NAME="ironGate"
```

Same NUCLEUS start command as eastGate. Already on Forgejo (SSH working),
so federation adds mesh discovery on top of existing git sync.

### southGate

```bash
export SONGBIRD_NODE_ID="southGate"
export GATE_NAME="southGate"
```

Note: hostname `pop-os` won't auto-detect. `GATE_NAME=southGate` in
`.bashrc` handles both cascade-pull and Songbird node identity.

### biomeGate

```bash
export SONGBIRD_NODE_ID="biomeGate"
export GATE_NAME="biomeGate"
```

Complete NUCLEUS from 9/13 to 13/13 before federation. Tower Atomic
(BearDog + Songbird + skunkBat) is the minimum for mesh participation.

### strandGate

```bash
export SONGBIRD_NODE_ID="strandGate"
export GATE_NAME="strandGate"
```

Deploy NUCLEUS from scratch on 64-core hardware. Use plasmidBin
`nucleus_launcher.sh` with `--peers` pointing to VPS.

---

## How Federation Works

```
Gate starts NUCLEUS with --peers "golgiBody@[RELAY_PUBLIC]:7700"
  ↓
Songbird connects to VPS :7700 (TCP federation)
  ↓
mesh.init exchanges node IDs and capabilities
  ↓
VPS golgiBody appears in discovery.peers
  ↓
Other gates connecting to VPS also appear in discovery.peers
  ↓
Gates can discovery.announce capabilities across the mesh
  ↓
capability.call routes requests to best-fit gate via VPS hub
```

**Star topology (now):** All gates connect to VPS hub. VPS relays
discovery and capability calls between gates.

**Full mesh (later):** Gates also connect directly to each other
on the LAN. VPS remains the WAN bridge and the always-on anchor.

---

## WAN vs LAN

| Gate Location | Transport | Path |
|---------------|-----------|------|
| LAN (east, iron, south, biome) | Direct TCP | `gate:7700 → VPS:7700` |
| WAN (strand, flock) | TURN relay | `gate:7700 → VPS:3478 → VPS:7700` |

LAN gates connect directly to the VPS public IP. WAN gates behind NAT
use the Songbird TURN relay on `:3478` (already live, credentials in
`/etc/songbird/relay-credentials` on VPS).

TURN client is built into Songbird (`songbird-turn-client` crate). Gates
behind NAT configure:

```bash
export SONGBIRD_TURN_SERVER="[RELAY_PUBLIC]:3478"
export SONGBIRD_TURN_USERNAME="nucleus-relay"
export SONGBIRD_TURN_CREDENTIAL="<from VPS /etc/songbird/relay-credentials>"
```

---

## Verification Commands

From any gate with NUCLEUS running:

```bash
# Check mesh peers (should include golgiBody)
echo '{"jsonrpc":"2.0","method":"discovery.peers","id":1}' \
  | socat - UNIX-CONNECT:$SONGBIRD_SOCKET

# Announce a capability (makes gate visible to others)
echo '{"jsonrpc":"2.0","method":"discovery.announce","params":{"capability":"test","endpoint":"local"},"id":2}' \
  | socat - UNIX-CONNECT:$SONGBIRD_SOCKET

# Call a capability on another gate via mesh
echo '{"jsonrpc":"2.0","method":"capability.call","params":{"target":"gate:ironGate","capability":"security","method":"rpc.methods"},"id":3}' \
  | socat - UNIX-CONNECT:$SONGBIRD_SOCKET
```

From VPS (verify federation is accepting connections):

```bash
echo '{"jsonrpc":"2.0","method":"discovery.peers","id":1}' \
  | socat - UNIX-CONNECT:/run/membrane/songbird.sock
```

---

## Evolution Path

| Phase | State | What's Happening |
|-------|-------|-----------------|
| S5a (now) | SSH + MitoBeacon coexist | Dual membrane, SSH for git, beacon for discovery |
| S5b | BirdSong genetic auth | Gates authenticate federation via encrypted beacons |
| S5c | Forgejo BTSP tokens | BearDog vault issues tokens alongside SSH |
| S5d | SSH fallback-only | Native membrane is primary |
| S5e | SSH dissolved | Full genetic sovereignty |

---

*Wave 60. Tower Atomic complete on VPS. Federation hub live on :7700.
Dark Forest beacons encrypted. The native membrane grows.*
