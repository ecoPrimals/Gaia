> **HISTORICAL SNAPSHOT (May 14, 2026)** — Superseded by `gardens/cellMembrane/` private repo
> (VPS_STATE.md, RUNBOOKS.md, GLACIAL_SHIFT_TRACKER.md). Live VPS has advanced beyond this
> snapshot: Channel 3 Surface LIVE (Caddy TLS on :80/:443, `membrane.primals.eco`), Tower
> composition deployed, 19MB sporePrint cache. Operational ownership transferred to
> cellMembrane team (ironGate).

# projectNUCLEUS — cellMembrane VPS Deployment Handoff

**Date**: May 14, 2026 (updated)
**From**: primalSpring (ecosystem coordination)
**For**: projectNUCLEUS (deployment & ops ownership)
**Registry**: 427-method capability registry
**Deployment Class**: fieldMouse (Tower on external substrate)

---

## Summary

The first sovereign membrane channel is **live on DigitalOcean** and has been
**hardened**. primalSpring built the tooling, deployed Channel 2 (Relay),
hardened the VPS, and classified it as a **cellMembrane fieldMouse** — a
minimal Tower atomic on external substrate where the provider is treated as
a non-family observer. Ownership now transfers to projectNUCLEUS for ongoing
ops, the NAT shadow run, and deployment of Channels 1 and 3.

---

## What's Deployed

| Item | Value |
|------|-------|
| **VPS** | `membrane-relay`, [RELAY_PUBLIC], Debian 12 x64, nyc1, ~$12/mo (2GB, resized from $4) |
| **Classification** | cellMembrane fieldMouse — Tower (BearDog + Songbird + SkunkBat) + RustDesk (hbbs + hbbr) |
| **Channel 2** | Songbird v0.2.1 TURN relay on UDP :3478 |
| **Channel 2b** | RustDesk relay (hbbs :21115-21116, hbbr :21117) |
| **Firewall** | UFW active, default-deny, **ports 22 + 3478 + 21115-21117** (composition-aware: relay + RustDesk) |
| **SSH** | Key-only (password auth disabled), key: `ecoPrimal`, fail2ban active |
| **Binary source** | Pulled from GitHub Releases `v2026.05.13` (not SCP'd) |
| **Credentials** | Generated on-VPS at `/etc/songbird/relay-credentials` |
| **systemd** | `songbird-relay.service` enabled, auto-restart on failure |

### Hardening Applied (May 14, 2026)

| Action | Detail |
|--------|--------|
| exim4 purged | Mail server removed — was running as root with no purpose |
| fail2ban installed | SSH brute-force protection, systemd backend, 5-retry/1h-ban |
| Firewall tightened | Ports 53/80/443 **closed** — 22/tcp + 3478/udp+tcp + 21115-21117/tcp+udp (RustDesk) |
| credentials.env removed | Redundant plaintext duplicate — canonical creds at `/etc/songbird/relay-credentials` |
| journald persistence | `/var/log/journal/` exists, logs survive reboots |

### cellMembrane fieldMouse Classification

The VPS is classified as a **cellMembrane fieldMouse** — a minimal Tower
atomic on external substrate. Key principles:

- **Dark Forest**: DigitalOcean is a non-family observer. Everything sensitive
  is encrypted at rest; the provider sees only noise (binaries, firewall rules,
  opaque relay bytes).
- **No biomeOS**: Static composition, no deploy graph. Services managed by
  systemd units from `plasmidBin/membrane/`.
- **Tower only**: BearDog (crypto), Songbird (relay), SkunkBat (defense).
  No data storage (Nest) or compute dispatch (Node) unless future channels
  require it.

See `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` for the full specification.

### Client Config (for NAT shadow run)

```bash
export SONGBIRD_TURN_SERVER=[RELAY_PUBLIC]:3478
export SONGBIRD_TURN_USERNAME=nucleus-relay
export SONGBIRD_TURN_KEY=210bcbb59980af265e48c7caaab525c6c4e88b74f9c3ca9e5d9f5b8d3a42f559
```

---

## Tooling Shipped (in plasmidBin)

### `deploy_membrane.sh`

Five modes:

```bash
./deploy_membrane.sh provision --region nyc1     # Create droplet + deploy
./deploy_membrane.sh deploy root@<ip>            # Deploy to existing VPS
./deploy_membrane.sh status root@<ip>            # Health check
./deploy_membrane.sh keys add root@<ip> --name <gate> --pubkey <key>  # Multi-gate SSH
./deploy_membrane.sh teardown --name membrane-relay  # Destroy droplet
```

All modes support `--dry-run`. Binary is pulled from GitHub Releases on the
VPS itself — no local machine dependency. This validates our plasmidBin
distribution pipeline end-to-end.

### `membrane/songbird-relay.service`

Security-hardened systemd unit: `NoNewPrivileges`, `ProtectSystem=strict`,
`MemoryMax=128M`, `CPUQuota=50%`.

---

## Secrets & API Key Sharing

### Current State

| Secret | Location | Access |
|--------|----------|--------|
| DO API token | Operator's `~/.config/doctl/token` (chmod 600) | Operator only |
| TURN credentials | VPS `/etc/songbird/relay-credentials` | Root on VPS only |
| SSH private key | Operator's `~/.ssh/id_ed25519` | Same key as GitHub + LAN gates |

### Sharing Strategy

**Phase 0 (now): Operator-held.** The DO API token lives on the operator's
machine. `deploy_membrane.sh` uses `doctl` which reads from its own auth
context. TURN credentials are generated on-VPS and never leave it.

**Phase 1 (near-term): BearDog `secrets.store` delegation.** BearDog owns
`secrets.store` and `secrets.retrieve` in the capability registry. The
composition bootstrap can store the DO API token purpose-encrypted via
BearDog, retrievable by authorized primals (biomeOS for auto-provisioning).
This requires:
- BearDog implementing `secrets.store`/`secrets.retrieve` with per-purpose
  encryption (the wire contract exists, implementation is in progress)
- A BTSP session between the operator's machine and the composition

**Phase 2 (stadial): Zero operator secrets.** The DO API token is stored
in BearDog's encrypted secret store, accessible only through BTSP-authenticated
sessions. biomeOS can provision/teardown membrane channels autonomously.
The operator's only role is initial token provisioning and rotation.

### What BearDog Can Do Today

| Capability | Status |
|------------|--------|
| `crypto.sign` / `crypto.verify` | **Shipped** — ed25519, production-ready |
| `crypto.encrypt` / `crypto.decrypt` | **Shipped** — symmetric + asymmetric |
| `btsp.server.*` / `btsp.client.*` | **Shipped** — session establishment |
| `secrets.store` / `secrets.retrieve` | **Wire contract defined**, implementation pending in NestGate |
| BTSP credential delegation | **Protocol exists**, tooling integration pending |

**Bottom line**: BearDog can encrypt/decrypt and establish BTSP sessions today.
The `secrets.store`/`secrets.retrieve` flow requires NestGate integration (it's
NestGate that persists, BearDog that encrypts). For now, operator-held tokens
with `chmod 600` is the practical approach.

---

## What projectNUCLEUS Owns Now

| Responsibility | Detail |
|----------------|--------|
| VPS uptime | Monitor `membrane-relay` droplet, respond to outages |
| NAT shadow run | Configure clients with TURN credentials, validate two-NAT relay |
| Credential rotation | Regenerate TURN credentials periodically |
| Channel 1 (DNS) | Deploy `knot-dns` when ready (opens port 53 — update firewall) |
| Channel 3 (Surface) | Deploy `beardog-tls` + `nestgate` when ready (opens 80/443 — update firewall) |
| Tower deploy | Deploy full Tower composition when ready (`--composition tower`) |
| Scaling | Evaluate Model B (multi-VPS) if single box hits limits |
| DO token rotation | Rotate via DO dashboard, update `~/.config/doctl/token` |

### Operational Commands

```bash
# Status check
./deploy_membrane.sh status root@[RELAY_PUBLIC]

# SSH to VPS
ssh root@[RELAY_PUBLIC]

# View relay logs
ssh root@[RELAY_PUBLIC] "journalctl -u songbird-relay -f"

# Restart relay
ssh root@[RELAY_PUBLIC] "systemctl restart songbird-relay"

# Update binary (re-fetches from GitHub Releases)
./deploy_membrane.sh deploy root@[RELAY_PUBLIC]

# Teardown (destroys droplet — requires confirmation)
./deploy_membrane.sh teardown
```

---

## Escalation Roadmap

What projectNUCLEUS can do next, in priority order:

| Step | What | Tooling |
|------|------|---------|
| 1. NAT shadow run | Validate two-NAT relay with TURN credentials above | Client-side Songbird config |
| 2. Tower deploy | `./deploy_membrane.sh deploy root@[RELAY_PUBLIC] --composition tower` | Deploys BearDog + SkunkBat alongside Songbird |
| 3. Encrypted-at-rest | Use `share_credentials.sh` to encrypt all sensitive files on VPS | `age` + SSH ed25519 |
| 4. Channel 1 (DNS) | Deploy `knot-dns` — will require opening port 53 | Future tooling |
| 5. Channel 3 (Surface) | Deploy `beardog-tls` + `nestgate` — will require opening 80/443 | Future tooling |
| 6. BingoCube verification | Zero-knowledge access control via progressive reveal | Pending BingoCube integration |

### ironGate Verification Procedure

This is the first **secure validation milestone**: ironGate takes ownership
by proving it can operate the cellMembrane independently.

```bash
# 1. Pull encrypted credential blob from operator
scp operator@lan-gate:/path/to/membrane-credentials.age ./

# 2. Decrypt with ironGate's SSH key
./share_credentials.sh decrypt membrane-credentials.age

# 3. Authenticate with DigitalOcean
doctl auth init --access-token <decrypted-token>

# 4. Verify cellMembrane status
./deploy_membrane.sh status root@[RELAY_PUBLIC]

# 5. Confirm relay is operational
ssh root@[RELAY_PUBLIC] "systemctl is-active songbird-relay && fail2ban-client status sshd"
```

Successful completion of all 5 steps confirms: ironGate has operational
control of the cellMembrane, credentials are securely shared, and the
handoff is complete.

### Ownership Boundary

| Domain | Owner |
|--------|-------|
| Deployment tooling (`deploy_membrane.sh`, systemd units, `share_credentials.sh`) | primalSpring |
| VPS operations, uptime, credential rotation | **projectNUCLEUS** |
| Channel deployment decisions (when to enable DNS, TLS) | **projectNUCLEUS** |
| Upstream capability evolution (BearDog Vault, BingoCube) | primalSpring |

primalSpring built and hardened the cellMembrane. projectNUCLEUS owns and
operates it from here.

---

## Cross-References

- `wateringHole/MEMBRANE_CHANNEL_ARCHITECTURE.md` — full architecture doc
- `wateringHole/CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — cellMembrane fieldMouse specification
- `wateringHole/CAPABILITY_WIRE_STANDARD.md` — SP-01, GD-01 conventions
- `wateringHole/NUCLEUS_TWO_TIER_CRYPTO_MODEL.md` — BearDog secrets delegation model
- `wateringHole/SECRETS_AND_SEEDS_STANDARD.md` — no-static-secrets principle
- `wateringHole/handoffs/SONGBIRD_WAVE202_RELAY_OPS_DEPLOYMENT_MAY12_2026.md` — relay readiness
- `wateringHole/birdsong/DARK_FOREST_BEACON_GENETICS_STANDARD.md` — Dark Forest encryption pattern
- `plasmidBin/deploy_membrane.sh` — deployment script (composition-aware firewall)
- `plasmidBin/membrane/songbird-relay.service` — Channel 2 systemd unit
- `plasmidBin/membrane/hbbs-membrane.service` — RustDesk rendezvous systemd unit
- `plasmidBin/membrane/hbbr-membrane.service` — RustDesk relay systemd unit
- `plasmidBin/membrane/beardog-membrane.service` — Tower BearDog systemd unit
- `plasmidBin/membrane/skunkbat-membrane.service` — Tower SkunkBat systemd unit
- `plasmidBin/membrane/share_credentials.sh` — `age`-based credential sharing
