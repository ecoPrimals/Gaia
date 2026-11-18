<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# cellMembrane — fieldMouse Tower on External Substrate

**Date**: May 14, 2026 (updated May 23, 2026)
**Status**: Active
**Authority**: WateringHole Consensus
**Deployment Class**: fieldMouse
**Composition**: Tower (BearDog + Songbird + SkunkBat) + RustDesk (hbbs + hbbr)
**Substrate**: DigitalOcean VPS (external, non-family)

---

## What Is cellMembrane

The cellMembrane is the first production **fieldMouse** deployment: a minimal
Tower atomic running on external substrate (DigitalOcean VPS) that provides
NUCLEUS with its three membrane channels — Signal (DNS), Relay (NAT), and
Surface (TLS).

cellMembrane is not a gate, not a niche, and does not run biomeOS. It is a
static, hardened composition deployed via `plasmidBin/deploy_membrane.sh`.
It maps exactly to the fieldMouse definition in the glossary:

> The **minimal deployable structure** for the ecoPrimals ecosystem. A
> fieldMouse is the smallest stripped system — as few as a single atomic or
> chimera — purpose-built for a constrained deployment niche.

The "constrained niche" here is **external substrate** — infrastructure the
operator does not physically own, where the substrate provider (DigitalOcean)
has theoretical root-level access to the hardware.

---

## Dark Forest Principle

The cellMembrane operates under the Dark Forest constraint: the substrate
provider is treated as a **non-family observer**. Everything on disk is either:

1. **Public** — binaries (static musl ELFs from plasmidBin), systemd units,
   firewall rules. Nothing here is secret.
2. **Encrypted** — credentials, identity material, state. Encrypted at rest
   such that the provider sees only noise.

This derives from the mitobeacon pattern (Dark Forest Beacon Genetics
Standard): "Observers without beacon genetics: [noise]". DigitalOcean lacks
the beacon genetics (FAMILY_SEED) required to decrypt anything meaningful.

### What the provider sees

| Category | On disk | Provider observes |
|----------|---------|-------------------|
| Binaries | `/opt/membrane/beardog`, `songbird`, `skunkbat`, `hbbs`, `hbbr` | Stripped static ELFs — public (plasmidBin / RustDesk GitHub) |
| systemd units | `/etc/systemd/system/*.service` | Service definitions — public templates |
| Firewall | UFW rules | Port list — TURN relay + RustDesk + SSH |
| TURN credentials | `/etc/songbird/relay-credentials` | HMAC shared secret — **to be encrypted at rest** |
| Tower identity | `/opt/membrane/tower.env` | FAMILY_SEED, GATE_ID — **encrypted at rest** |
| RustDesk keys | `/opt/membrane/rustdesk/id_ed25519*` | Server identity keypair — public key distributed to clients |
| Network traffic | Relay bytes on :3478, RustDesk on :21116-21117 | BTSP/RustDesk-encrypted opaque bytes — noise |
| Logs | journald | Operational metadata — no inner secrets |

### Encryption-at-rest roadmap

| Phase | Mechanism | Status |
|-------|-----------|--------|
| **Now** | `age` + SSH ed25519 key encryption via `share_credentials.sh` | Active |
| **Mid term** | BearDog `secrets.store`/`secrets.retrieve` — credentials never stored as files | Pending BearDog Vault |
| **Long term** | Autonomous rotation by cellMembrane BearDog — operator only provisions FAMILY_SEED | Future |

---

## Composition

cellMembrane runs the **Tower atomic** — the same three primals that handle
trust, discovery, and defense inside NUCLEUS, turned outward to face the
public internet.

| Component | Role | systemd unit | Socket/Port |
|-----------|------|-------------|-------------|
| BearDog | BTSP handshake, crypto identity, secrets delegation | `beardog-membrane.service` | `/run/membrane/beardog.sock` |
| Songbird | TURN relay (Channel 2), discovery | `songbird-relay.service` | `:3478` (UDP/TCP) |
| SkunkBat | Defense audit, threat assessment | `skunkbat-membrane.service` | `/run/membrane/skunkbat.sock` |
| hbbs | RustDesk rendezvous — ID registration, NAT hole-punch | `hbbs-membrane.service` | `:21115` (TCP), `:21116` (TCP+UDP) |
| hbbr | RustDesk relay — remote desktop traffic relay | `hbbr-membrane.service` | `:21117` (TCP) |

### Why Tower (not Node, not Nest)

The cellMembrane is a **function tower** — it provides network presence,
crypto identity, and perimeter defense. It does not store data (Nest) and
does not dispatch compute (Node). If a future cellMembrane needs data
persistence (e.g., NestGate for content serving on Channel 3), the Nest
atomic can be added without restructuring.

### RustDesk Co-Hosting

RustDesk (`hbbs` + `hbbr`) is a **symbiotic partner** (AGPL-3.0, same
license family) that provides sovereign remote desktop relay for
geo-delocalized gates. It shares the cellMembrane VPS because:

- Same principle: relay sees only opaque encrypted bytes (Dark Forest)
- Same resource class: ~20-30MB combined, fits the minimal footprint
- Same architectural role as Songbird: NAT traversal, but for remote
  desktop instead of primal IPC

The RustDesk server generates its own `id_ed25519` keypair. Only clients
configured with the matching public key can use the relay. The VPS
provider sees encrypted RustDesk traffic — noise.

### Deployment ordering

On external substrate, BearDog must boot **first**:

1. `beardog-membrane.service` — establishes crypto identity from FAMILY_SEED
2. `songbird-relay.service` — starts relay, credentials validated by BearDog
3. `skunkbat-membrane.service` — begins defense audit with Tower identity

This differs from internal gates where biomeOS orchestrates boot order.
On the cellMembrane, systemd dependency ordering (`After=beardog-membrane.service`)
enforces the sequence.

---

## Hardening Profile

The cellMembrane runs with a minimal attack surface:

### Firewall (UFW)

Only ports required by active channels are open:

| Port | Protocol | Purpose |
|------|----------|---------|
| 22 | TCP | SSH management (key-only, fail2ban protected) |
| 80 | TCP | Channel 3: ACME HTTP-01 + redirect (Caddy) |
| 443 | TCP | Channel 3: Surface HTTPS (`membrane.primals.eco`, Let's Encrypt E8) |
| 3478 | TCP + UDP | Channel 2: Relay (TURN) |
| 21115 | TCP | RustDesk: NAT type test |
| 21116 | TCP + UDP | RustDesk: ID registration + hole punching |
| 21117 | TCP | RustDesk: relay |

Port 53 remains **closed** until Channel 1 (knot-dns) is deployed.
Ports 21118, 21119 (RustDesk web client) are **closed** — not needed.

### Services removed

| Service | Reason |
|---------|--------|
| exim4 | Mail server running as root with no purpose — purged |
| droplet-agent | DigitalOcean monitoring agent — opaque root-level software — **purged** |

### Services added

| Service | Purpose |
|---------|---------|
| fail2ban | SSH brute-force protection (systemd backend, 5-attempt threshold, 1h ban) |
| journald persistence | Logs survive reboots (`/var/log/journal/`) |

### systemd hardening (all units)

All primal services run with:
- `NoNewPrivileges=true`
- `PrivateTmp=true`
- `ProtectSystem=strict`
- `ProtectHome=true`
- `ReadWritePaths=/run/membrane` (sockets only)
- `ReadOnlyPaths=/opt/membrane` (binaries + config)
- `MemoryMax` / `CPUQuota` resource limits

---

## Multi-Gate SSH Key Management

As the cellMembrane evolves from a single-operator system to a
geo-delocalized rendezvous for multiple gates, SSH key management
becomes critical. The `deploy_membrane.sh keys` subcommand provides
managed `authorized_keys` with an audit trail:

```bash
./deploy_membrane.sh keys add root@[RELAY_PUBLIC] --name "irongate@pop-os" --pubkey "ssh-ed25519 AAAA..."
./deploy_membrane.sh keys list root@[RELAY_PUBLIC]
./deploy_membrane.sh keys revoke root@[RELAY_PUBLIC] --name "irongate@pop-os"
```

Each key is tagged with the gate name and add date (`# gate:<name> added:<date>`)
for auditability. When BearDog Vault ships, `keys add` can be replaced
by BTSP identity proof — no operator involvement for key authorization.

### Geo-Delocalized Gate Architecture

Gates at friends' and family's houses connect back to NUCLEUS through
the cellMembrane. Each remote gate is a fieldMouse that uses:

- **Songbird TURN** (`:3478/udp`) — for BTSP-encrypted primal IPC across NAT
- **RustDesk** (`:21116-21117`) — for human remote desktop access to the gate

The cellMembrane is the **rendezvous, not the data plane**. It never stores
your data or runs your compute. It brokers connections. All relay traffic
is encrypted end-to-end (BTSP for IPC, RustDesk for desktop). The provider
sees only opaque bytes — Dark Forest extended to geo-delocalized gates.

---

## BingoCube Verification (Future)

The cellMembrane is a natural target for **BingoCube** zero-knowledge access
control. Instead of sharing credentials directly, a remote gate proves
knowledge of a shared commitment via progressive reveal:

1. Operator provisions a BingoCube commitment on the cellMembrane
2. Remote gate (ironGate) requests access by revealing a subcube
3. cellMembrane BearDog verifies `verify_subcube()` — correct reveal grants
   a time-limited BTSP session
4. No credentials are ever transmitted — only commitment proofs

This pattern eliminates the need for `age`-encrypted credential sharing
entirely. The cellMembrane BearDog holds the commitment; the remote gate
holds the preimage. Neither alone is useful to the substrate provider.

---

## Escalation Ladder

```
Phase 0: Relay only (Songbird on :3478)
  └── TURN credentials in plaintext on disk (to be encrypted)

Phase 1: Tower composition — BearDog + Songbird + SkunkBat + RustDesk ← CURRENT
  └── Songbird TURN + RustDesk hbbs/hbbr co-hosted
  └── Channel 3 Surface: Caddy TLS on :80/:443 (membrane.primals.eco, Let's Encrypt E8)
  └── 19 MB sporePrint content cache synced from NestGate
  └── Multi-gate SSH key management via deploy_membrane.sh keys
  └── droplet-agent purged, geo-delocalized gates supported
  └── deploy_membrane.sh --composition tower

Phase 1.5: Nest expansion + Channel 1 DNS + Channel 3 TLS hardening ← NEXT
  └── deploy_membrane.sh --composition nest (NestGate + rhizoCrypt + loamSpine + sweetGrass)
  └── knot-dns sovereign DNS on Channel 1
  └── Caddy → BearDog ACME cutover on Channel 3

Phase 2: Encrypted-at-rest
  └── BearDog Vault encrypts all credentials on disk
  └── Provider sees only noise (Dark Forest)
  └── age-based sharing replaced by BTSP delegation

Phase 3: BingoCube challenge
  └── Zero-knowledge access control
  └── No credential files exist — only commitment proofs
  └── ironGate verifies via progressive reveal

Phase 3.5: SoloKey hardware attestation
  └── BearDog FIDO2/CTAP2 integration for physical-presence auth
  └── Gate identity includes hardware attestation signal
  └── liveSpore.json provenance includes SoloKey witness signature

Phase 4: Full autonomy
  └── cellMembrane BearDog rotates credentials autonomously
  └── Operator's only role: initial FAMILY_SEED + domain registration
  └── biomeOS on ironGate auto-provisions membrane channels
  └── SoloKey as first-class identity primitive in BTSP Phase 4
```

**Hardware security**: SoloKey 2 devices are plugged into both ironGate
and eastGate. Currently detected but software-only (exp096 Phase 4).
BearDog FIDO2/CTAP2 integration is the enabler for Phases 3.5+.

---

## Topology Reference

The cellMembrane corresponds to the `ecoprimals-fieldmouse-chimera.yaml`
topology from benchScale, adapted for external substrate:

```
fieldMouse-cellMembrane
├── Tower atomic (chimera)
│   ├── BearDog  — crypto, BTSP, secrets
│   ├── Songbird — relay, discovery
│   └── SkunkBat — defense, audit
├── Symbiotic partners
│   ├── hbbs — RustDesk rendezvous (ID, NAT)
│   └── hbbr — RustDesk relay (remote desktop)
├── Substrate: DigitalOcean VPS (nyc1)
├── Channels: 2 active (Relay + RustDesk), 3 active (Surface/TLS), 1 planned (DNS)
└── Owner: cellMembrane team / ironGate (ops), projectNUCLEUS (validation), primalSpring (tooling)
```

---

## Cross-References

- `MEMBRANE_CHANNEL_ARCHITECTURE.md` — full three-channel architecture, BTSP phases, SoloKey evolution
- `LITHOSPORE_USB_DEPLOYMENT.md` — lithoSpore USB as hypogeal cotyledon, geo-delocalized validation
- `GLOSSARY.md` — fieldMouse definition
- `birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md` — mitobeacon / Dark Forest encryption
- `plasmidBin/deploy_membrane.sh` — deployment script (supports `--composition relay|rustdesk|tower`, `keys` management)
- `plasmidBin/membrane/share_credentials.sh` — `age`-based credential sharing
- `plasmidBin/membrane/*.service` — systemd unit templates (Songbird, RustDesk, Tower primals)
- `handoffs/PROJECTNUCLEUS_MEMBRANE_VPS_HANDOFF_MAY14_2026.md` — ownership handoff
- `benchScale/topologies/ecoprimals-fieldmouse-chimera.yaml` — reference topology
- `primalSpring/experiments/exp096_pixel_cross_arch_bonding/` — SoloKey/HSM probing (Phase 4)
