<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Membrane Channel Architecture — External Surface Design

**Date**: May 13, 2026 (reviewed Wave 155h Jul 29, 2026 — All 3 channels LIVE. 9-gate mesh. S1-S4 GRADUATED.)
**Status**: Active
**Authority**: WateringHole Consensus

---

## Context

NUCLEUS is a closed cellular system — 13 primals communicating over Unix
sockets on a LAN, trusting each other via BTSP genetic identity. It is
self-contained. But a cell that cannot interact with its environment
cannot grow.

Three external interfaces are architecturally required for NUCLEUS to
participate in the wider internet. These are the **membrane channels** —
the controlled boundaries where the cell touches the outside world.

Each channel exists because of a physical or coordination constraint that
cannot be eliminated by software alone:

1. **Substrate** — a publicly routable IP address (physics: NAT requires a relay)
2. **Signal space** — a globally resolvable name (coordination: DNS is a shared namespace)
3. **Trust bridge** — a browser-trusted certificate (coordination: browsers ship CA root stores)

Everything inside the membrane is sovereign. Everything outside operates
on external substrate, in external signal space, or through an external
trust bridge. The membrane channels define what crosses that boundary,
how, and under what trust constraints.

---

## Three Channels

### Channel 1: Signal (DNS)

**Purpose**: Name resolution — tells the world where `primals.eco` lives.

| Property | Value |
|----------|-------|
| **Access** | Fully public, anyone can query |
| **Trust level** | Lowest — answers are public data, no secrets cross this channel |
| **What flows** | DNS queries/responses (A, AAAA, NS, MX, TXT for ACME) |
| **What cannot flow** | Content, auth tokens, encrypted sessions, relay traffic |
| **Port** | 53 (UDP/TCP) |
| **Primal owner** | knot-dns, operated under Songbird's DNS integration |
| **VPS process** | `knot-dns` (standalone, no shared state with other channels) |

**Permanently external**: The DNS registrar holds NS delegation for
`primals.eco`. This is a shared global namespace — ICANN, the `.eco`
registry, and the registrar coordinate name ownership. You cannot
self-host domain registration. This is analogous to a street address:
the postal system assigns it, you occupy it.

**Sovereign component**: Authoritative DNS resolution. knot-dns on
your infrastructure answers "where is primals.eco?" — Cloudflare is
removed from the resolution path entirely. The registrar knows your
NS IPs and nothing else.

**Mitigation**: Multiple domains on different registrars provide
redundancy. Onion addresses (`.onion` via Songbird Tor integration)
bypass DNS entirely for Tor-capable clients.

### Channel 2: Relay (NAT Traversal)

**Purpose**: Punch through NAT so peers can reach your LAN.

| Property | Value |
|----------|-------|
| **Access** | BTSP-authenticated peers only (BearDog HMAC credentials) |
| **Trust level** | Medium — relay sees encrypted packet metadata (source/dest IP, timing) but not content |
| **What flows** | BTSP-encrypted opaque bytes between NAT'd endpoints |
| **What cannot flow** | Plaintext content, DNS queries, HTTPS sessions |
| **Port** | 3478 (TURN standard, RFC 5766) |
| **Primal owner** | Songbird (`songbird relay` binary, 836 lines) |
| **VPS process** | `songbird relay` (stateless, credential-gated) |

**Permanently external**: A publicly routable IPv4 address. When two
machines are both behind NAT, neither can reach the other directly.
STUN can punch through simple NAT, but symmetric NAT (most consumer
routers) blocks it. A relay with a public IP is the only physics-level
solution. This is analogous to renting a mailbox — you need a
reachable address, but the mail is sealed.

**Sovereign component**: Everything except the IP address. The relay
binary is a stripped static ELF from plasmidBin. Credentials are
BearDog HMAC material. Traffic is BTSP-encrypted end-to-end before
reaching the relay. The VPS provider sees opaque bytes, source/dest
IPs, and timing metadata. Content is invisible.

**Portability**: The relay is stateless. Move it to a different
provider by copying one binary, one systemd unit, and updating DNS.
Zero state migration, zero vendor lock-in.

**What it replaces**: `cloudflared` (Cloudflare Tunnel). Today
cloudflared relays traffic through Cloudflare's infrastructure —
they operate the relay, see connection metadata, and control the
control plane. Songbird relay eliminates all of that.

### Channel 2b: Remote Desktop (RustDesk)

**Purpose**: Sovereign remote desktop access to geo-delocalized gates.

| Property | Value |
|----------|-------|
| **Access** | RustDesk-encrypted, server public key required |
| **Trust level** | Medium — relay sees only opaque encrypted desktop traffic |
| **What flows** | RustDesk-encrypted remote desktop sessions |
| **What cannot flow** | Plaintext content, DNS queries, BTSP IPC, credentials |
| **Ports** | 21115 (TCP, NAT test), 21116 (TCP+UDP, ID/hole-punch), 21117 (TCP, relay) |
| **Software** | RustDesk `hbbs` + `hbbr` (AGPL-3.0 symbiotic partner) |
| **VPS process** | `hbbs` (rendezvous) + `hbbr` (relay) — two lightweight Rust binaries |

**Relationship to Channel 2**: RustDesk complements Songbird. Both are
relay services on the cellMembrane that see only encrypted opaque bytes.
Songbird relays BTSP-encrypted primal IPC; RustDesk relays encrypted
remote desktop sessions. Together they provide the full NAT traversal
surface for both programmatic and human access to remote gates.

**Sovereignty**: The RustDesk server is self-hosted — no third-party
rendezvous or relay. The server generates its own `id_ed25519` keypair;
only clients configured with the matching public key can connect. The
VPS provider sees encrypted traffic — noise.

### Channel 3: Surface (TLS + Content)

**Purpose**: Browser-accessible HTTPS surface for `primals.eco` and API endpoints.

| Property | Value |
|----------|-------|
| **Access** | Public for content download; BTSP-authenticated for API/interactive |
| **Trust level** | Highest external — TLS private keys live here, session state crosses this boundary |
| **What flows** | HTTPS sessions, static content (Zola site, plasmidBin downloads), ACME challenges |
| **What cannot flow** | Relay traffic, DNS resolution, internal NUCLEUS IPC |
| **Ports** | 443 (HTTPS), 80 (ACME HTTP-01 challenge only) |
| **Primal owner** | BearDog (TLS termination, ACME client) + NestGate (content serving) |
| **VPS process** | `beardog-tls` + `nestgate` (or reverse-proxied from gate hardware) |

**Permanently external**: Let's Encrypt (or any ACME-compatible CA)
provides browser-trusted certificate signatures. Browsers won't
connect to HTTPS without a certificate signed by a CA they trust.
Running your own CA doesn't help — no browser ships your root cert.
This is analogous to a passport stamp: your cell is fully functional
without it, but the broader organism (the browser ecosystem) will
reject you without this surface marker.

**Sovereign component**: All TLS termination, private key generation,
content serving, and session management. Let's Encrypt sees your domain
name and that you requested a cert. They do NOT see your traffic, your
keys, or your content. The ACME protocol is open (RFC 8555), the
client is BearDog's, and alternative CAs exist (ZeroSSL, BuyPass,
Google Trust Services).

**What it replaces**: Cloudflare edge TLS proxy. Today Cloudflare
terminates TLS for `primals.eco`, holds the certificate private keys,
and sees all traffic in plaintext at their edge. BearDog TLS
eliminates all of that — the private key never leaves your
infrastructure.

---

## Channel Isolation

Channels are **process-isolated** — separate binaries with no shared
state, no shared sockets, no shared memory. Even on a single VPS, a
compromise of one channel does not grant access to another.

| Boundary | Enforced by |
|----------|-------------|
| Channel 1 cannot read relay traffic | Separate process, different port, no relay credentials |
| Channel 2 cannot serve content | No TLS keys, no content store, no HTTP listener |
| Channel 2b cannot access TURN | Separate process, different port, no TURN credentials |
| Channel 3 cannot resolve DNS | No knot-dns zone files, different process |
| No channel can reach internal NUCLEUS | VPS has no LAN access; relay forwards opaque bytes only |

### Firewall Rules (per-channel, composition-aware)

Firewall rules are **composition-aware**: only ports required by deployed
channels are opened. `deploy_membrane.sh` configures UFW based on the
active composition, not a static full-channel list.

```bash
# Always open: management
-A INPUT -p tcp --dport 22 -j ACCEPT   # SSH (key-only, fail2ban)

# Channel 2: Relay — open when relay or tower composition is active
-A INPUT -p udp --dport 3478 -j ACCEPT
-A INPUT -p tcp --dport 3478 -j ACCEPT

# Channel 2b: RustDesk — open when rustdesk or tower composition is active
-A INPUT -p tcp --dport 21115 -j ACCEPT   # NAT type test
-A INPUT -p tcp --dport 21116 -j ACCEPT   # ID registration
-A INPUT -p udp --dport 21116 -j ACCEPT   # Hole punching
-A INPUT -p tcp --dport 21117 -j ACCEPT   # Relay

# Channel 1: Signal — open only when DNS channel is deployed
-A INPUT -p udp --dport 53 -j ACCEPT
-A INPUT -p tcp --dport 53 -j ACCEPT

# Channel 3: Surface — open only when TLS channel is deployed
-A INPUT -p tcp --dport 443 -j ACCEPT
-A INPUT -p tcp --dport 80 -j ACCEPT

# Default deny
-A INPUT -j DROP
```

Each channel binds only to its assigned port(s). No channel listens
on another channel's ports. The `songbird relay` binary does not open
port 443. The `beardog-tls` binary does not open port 3478. Ports for inactive channels remain closed. The current Tower + Channel 3 Surface
deployment opens 22/tcp, 80/tcp, 443/tcp, 3478/udp+tcp, and 21115-21117/tcp+udp.

---

## Deployment Models

### Model A: Single VPS (interstadial start)

All three channels on one box. Current: ~$12/mo (2GB RAM, Tower composition).
Channels are separated by port and process, not by machine.

```
VPS (one public IP)
  :53          → knot-dns process       [Channel 1: Signal]
  :3478        → songbird relay         [Channel 2: Relay]
  :21115-21117 → hbbs + hbbr           [Channel 2b: RustDesk]
  :443         → beardog-tls + nestgate [Channel 3: Surface]
  :80          → ACME challenge only    [Channel 3: Surface]
  :22          → SSH (operator only)    [Management]
```

All binaries are static musl ELFs from plasmidBin. No runtime
dependencies on the VPS beyond a Linux kernel. Deploy by copying
binaries + systemd units. Tear down by wiping the box.

### Model B: Multi-VPS tiered (stadial hardening)

Each channel on a separate VPS, potentially with different providers
or in different jurisdictions. Higher isolation (~$12-15/mo).
Compromise or seizure of one channel does not expose the others.

```
VPS-1 (provider A, jurisdiction X)     [Channel 1: Signal]
  :53   → knot-dns

VPS-2 (provider B, jurisdiction Y)     [Channel 2: Relay]
  :3478 → songbird relay

VPS-3 (provider C, jurisdiction Z)     [Channel 3: Surface]
  :443  → beardog-tls + nestgate
  :80   → ACME
```

DNS NS records point to VPS-1. TURN credentials reference VPS-2.
TLS terminates at VPS-3. Each box is independently replaceable.

### Model C: Hybrid (router + VPS)

If your ISP provides a static IP (or you configure DDNS), Channel 3
can run directly on gate hardware behind router port forwarding.
BearDog TLS terminates on your own iron. Only Channels 1 and 2
require a VPS.

```
Your router (:443 forwarded to gate)   [Channel 3: Surface]
  gate:443 → beardog-tls + nestgate

VPS (:53 + :3478)                      [Channels 1+2: Signal + Relay]
  :53   → knot-dns
  :3478 → songbird relay
```

This eliminates the VPS from the highest-trust channel (TLS keys
never leave your hardware) while retaining a public relay point for
NAT traversal and DNS resolution.

---

## Mapping to Existing Tiering Systems

### Songbird STUN Sovereignty-First Escalation

Source: `primalSpring/ecoPrimal/src/bonding/stun_tiers.rs`

| STUN Tier | Description | Membrane Channel |
|-----------|-------------|-----------------|
| 1 | Genetic Lineage Relay (family-only, highest trust) | Internal — no membrane crossing |
| 2 | Self-Hosted STUN (your infrastructure) | **Channel 2: Relay** (your VPS) |
| 3 | Public STUN (community servers, address discovery) | External — used for address probing only |
| 4 | Rendezvous (future, gaming platforms) | External — future channel |

The VPS relay is STUN Tier 2 — your infrastructure, your binary, your
credentials. LAN traffic stays at Tier 1 and never touches the
membrane. The sovereignty-first strategy ensures Tier 1 is always
preferred when available.

### CompositionContext Discovery Escalation

Source: `primalSpring/ecoPrimal/src/composition/context.rs`

| Discovery Tier | Mechanism | Membrane Channel |
|----------------|-----------|-----------------|
| 1 | Songbird routing (`ipc.resolve`) | Internal — no membrane crossing |
| 2 | biomeOS Neural API | Internal — no membrane crossing |
| 3 | UDS filesystem convention | Internal — same machine only |
| 4 | Socket registry / manifests | Internal — self-registered |
| 5 | TCP probing on well-known ports | **VPS-reachable** — crosses membrane |

Only Discovery Tier 5 (TCP probing) can reach across the membrane via
Channel 2 (relay) or Channel 3 (surface). Tiers 1-4 operate entirely
within NUCLEUS over Unix sockets and never touch external substrate.

### BTSP Security Phases

Source: `wateringHole/compute-sharing/SOVEREIGN_COMPUTE_SHARING.md`

| BTSP Phase | Channel 1 (Signal) | Channel 2 (Relay) | Channel 3 (Surface) |
|------------|--------------------|--------------------|---------------------|
| 0: Manual | Public DNS, no auth | No relay (cloudflared) | Cloudflare TLS proxy |
| 1: Tunnel + Auth | knot-dns, no auth | Songbird relay, HMAC credentials | BearDog TLS, PAM auth |
| 2: BTSP Auth | No change | BTSP identity on relay credentials | BTSP identity on sessions |
| 3: BTSP Transport | DoT encrypted queries | BTSP AEAD on relay channel | BTSP AEAD on sessions |
| 4: Full BTSP | Sovereign DNS, policy-gated | Policy-automated relay | Full sovereign surface |

Each BTSP phase hardens the channels progressively. Phase 1 is the
interstadial entry point. Phase 4 is the stadial endgame.

### Hardware Security Evolution (SoloKey / FIDO2)

Both ironGate and eastGate have **SoloKey 2** devices plugged in,
providing a hardware security foundation for late-term BTSP evolution.

| BTSP Phase | Hardware Security Role | Status |
|------------|----------------------|--------|
| 1: Tunnel + Auth | SoloKey detected, software-only key generation | **Current** (exp096 Phase 4) |
| 2: BTSP Auth | BearDog FIDO2/CTAP2 for physical-presence authentication on BTSP handshakes | Near-term |
| 3: BTSP Transport | SoloKey as hardware attestation for gate identity — "this gate has a physical key" as a trust signal | Mid-term |
| 4: Full BTSP | SoloKey as first-class identity primitive; hardware witness in `liveSpore.json` for provenance | Long-term |

The SoloKey witness enables a stronger provenance claim: physical human
presence at the gate during validation, anchored into the `liveSpore.json`
provenance trail. This is particularly valuable for geo-delocalized gates
where the operator is not physically present at all times.

### Tunnel Evolution Ladder

Source: `wateringHole/compute-sharing/TUNNEL_ACCESS_GUIDE.md`

| Tunnel Phase | External Dependency | Membrane Channel Used |
|--------------|---------------------|-----------------------|
| 1: Tailscale | Tailscale control plane | None (bypasses membrane) |
| 2: WireGuard | None (manual key management) | None (direct tunnel) |
| 3: Songbird NAT | VPS relay (self-hosted) | **Channel 2: Relay** |
| 4: Full BTSP | **Zero** | Channel 2 with BTSP-only transport |

The membrane channel model starts at Tunnel Phase 3. Earlier phases
use external tunnel providers (Tailscale, WireGuard) that bypass the
membrane architecture entirely. Phase 3 is where the channels become
sovereign.

---

## Evolution Path

### Interstadial (current — May 2026)

Deploy Model A (single VPS). Channel 2 Relay and Channel 3 Surface operational.
Channel 1 Signal pending (knot-dns not yet deployed). Shadow runs producing
comparison data against Cloudflare baselines for S1 and S4 cutovers.

- Channel 1: knot-dns — **PROPAGATED** (Jun 4) — `primal.eco` + `nestgate.io` zones live, DNSSEC enabled, public resolvers confirming
- Channel 2: Songbird relay — **LIVE** (replacing cloudflared)
- Channel 3: Caddy TLS on :80/:443 — **LIVE** (`membrane.primals.eco`, Let's Encrypt E8, 19MB sporePrint cache). BearDog TLS shadow on :8443 pending cutover.

### Stadial (next)

Harden channel isolation. Optionally split to Model B (multi-VPS).
BTSP Phase 2/3 authentication on Channels 2 and 3.

- Cloudflare fully removed (TLS cutover complete)
- cloudflared fully removed (relay cutover complete)
- Forgejo on Channel 3 surface (`git.primals.eco`)
- NestGate content serving replaces GitHub Pages
- Let's Encrypt ACME auto-renewal on Channel 3

### Post-stadial (H3 horizon)

Full sovereignty within the constraints of the three permanently
external interfaces (registrar, public IP, CA).

- Channel 3 optionally moves to gate hardware (Model C)
- GitHub becomes read-only mirror or is removed
- JupyterHub PAM replaced by BTSP-only auth
- All tunneling via BTSP Phase 4 — zero external software

---

## Atomic / Channel Correspondence

The membrane channels are not arbitrary — they map directly to the
NUCLEUS atomic model. The same primals that solve trust, discovery,
and content internally also solve those problems externally. The
membrane channels are the atomics turned inside-out.

| Membrane Channel | External Problem | Atomic |
|-----------------|-----------------|--------|
| **Channel 1: Signal** (DNS) | Name resolution, discovery | **Tower** — Songbird handles discovery + routing |
| **Channel 2: Relay** (NAT) | Authenticated encrypted forwarding | **Tower** — Songbird (relay) + BearDog (credentials) |
| **Channel 3: Surface** (TLS + content) | Content serving, certificate trust | **Node + Nest** — BearDog (TLS), NestGate (content) |

Channels 1+2 are **Tower deployed outward** — the trust boundary
facing the public internet. Channel 3 is **Node + Nest deployed
outward** — compute dispatch and content storage facing browsers.

Internally, Tower primals communicate over Unix sockets on the LAN.
Externally, the same Tower primals (Songbird, BearDog) run on a VPS
and relay encrypted traffic back to the LAN. The membrane is where
internal atomics become external surfaces.

---

## Inner/Outer Crypto Layer Architecture

The membrane is not just a firewall — it is a **cryptographic boundary**
with two distinct trust regimes. Traffic arriving from the public internet
uses one set of credentials and protocols; traffic arriving from inner
gates uses a completely different set. The membrane Tower mediates the
transition between them.

### Two Crypto Layers

```
┌──────────────────────────────────────────────────────────────────┐
│                    PUBLIC INTERNET (outer)                       │
│   Browsers, remote peers, DNS resolvers, ACME CAs               │
└───────┬────────────────────┬─────────────────────┬──────────────┘
        │ TLS (public CA)    │ TURN (HMAC)         │ DNS (plain)
        ▼                    ▼                     ▼
┌───────────────────── MEMBRANE VPS ──────────────────────────────┐
│                                                                  │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │  OUTER LAYER — Extracellular Crypto                        │ │
│   │                                                            │ │
│   │  Protocol: TLS 1.3 (ACME certs), DNS, TURN HMAC            │ │
│   │  Trust:    Public CAs, shared DNS, credential-gated relay   │ │
│   │  Keys:     Let's Encrypt cert/key, TURN HMAC shared secret  │ │
│   │  Visible:  Domain names, IP addresses, timing metadata      │ │
│   │  Actors:   Browsers, remote peers, bots, scanners — anyone  │ │
│   └─────────────────────┬──────────────────────────────────────┘ │
│                         │                                        │
│   ┌─────────────────────▼──────────────────────────────────────┐ │
│   │  SELECTIVE PERMEABILITY — BearDog + SkunkBat                │ │
│   │                                                            │ │
│   │  BearDog:  Validates BTSP handshakes, manages crypto keys   │ │
│   │  SkunkBat: Audits cross-boundary traffic, threat assessment │ │
│   │  Policy:   Public content → pass through                    │ │
│   │            Private API → require BTSP identity              │ │
│   │            Relay bytes → opaque forwarding                  │ │
│   │            Credentials → inner-only, never cross outward    │ │
│   └─────────────────────┬──────────────────────────────────────┘ │
│                         │                                        │
│   ┌─────────────────────▼──────────────────────────────────────┐ │
│   │  INNER LAYER — Intracellular Crypto                        │ │
│   │                                                            │ │
│   │  Protocol: BTSP (genetic identity, AEAD sessions)           │ │
│   │  Trust:    FAMILY_SEED (shared between all gates)           │ │
│   │  Keys:     Ed25519 identity keys, BTSP session keys         │ │
│   │  Visible:  Only to gates that prove family membership       │ │
│   │  Actors:   ironGate, NUC, other NUCLEUS gates — family only │ │
│   └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└────────┬──────────────────────────────────────────┬─────────────┘
         │ BTSP tunnel (family key)                 │
         ▼                                          ▼
┌─────────────────┐                      ┌─────────────────┐
│  ironGate (LAN) │                      │  NUC (intake)   │
│  Full NUCLEUS   │                      │  Compute gate   │
└─────────────────┘                      └─────────────────┘
```

### Outer Layer: Extracellular Crypto

The outer layer speaks the internet's native protocols. Any actor on the
public internet can interact at this layer:

| Component | Protocol | Keys | Issuer |
|-----------|----------|------|--------|
| Channel 3 TLS | TLS 1.3 | ACME cert/key pair | Let's Encrypt (public CA) |
| Channel 2 TURN | HMAC-SHA256 | Shared secret | Self-generated |
| Channel 1 DNS | DNS (no encryption) | None | N/A |

The outer layer's security properties are limited by public internet
constraints: TLS certificates are issued by external CAs, DNS is
unauthenticated, and TURN credentials are HMAC shared secrets.
BearDog on the membrane manages all outer-layer key material.

### Inner Layer: Intracellular Crypto

The inner layer uses BTSP — the ecosystem's own genetic identity protocol.
Only gates that share the `FAMILY_SEED` can reach through the membrane:

| Component | Protocol | Keys | Issuer |
|-----------|----------|------|--------|
| Gate ↔ membrane | BTSP Phase 2+ | Ed25519 identity keys | Self-generated from FAMILY_SEED |
| Secrets delegation | BTSP-authenticated RPC | Session keys | BearDog handshake |
| Credential retrieval | `secrets.retrieve` | BTSP session token | BearDog on membrane |

The inner layer never speaks TLS, never uses public CAs, and never
exposes material to the outer layer. A browser cannot reach the inner
layer — it lacks the FAMILY_SEED required for BTSP handshake.

### Selective Permeability Rules

The membrane Tower (BearDog + SkunkBat) enforces what crosses between
layers. The rules are content-aware, not just port-based:

| Traffic Type | Direction | Policy |
|-------------|-----------|--------|
| Public content (website, downloads) | Outer → Inner | Pass through Channel 3 |
| API calls (authenticated) | Outer → Inner | Require BTSP identity via BearDog |
| Relay traffic (peer-to-peer) | Outer ↔ Inner | Opaque forwarding, no inspection |
| DNS queries | Outer → Inner | Answer from zone file, no inner contact |
| Credentials (API tokens, secrets) | Inner only | **Never cross outward** |
| FAMILY_SEED / identity keys | Inner only | **Never leave inner layer** |
| Audit logs | Inner → Outer | SkunkBat may export to inner gates, never outward |

### Credential Sharing Evolution

The mechanism for sharing credentials between gates evolves in lockstep
with the crypto layers:

| Phase | Mechanism | Trust Anchor | Where Credentials Live |
|-------|-----------|-------------|----------------------|
| **Short term** (now) | `age` + SSH ed25519 keys | Shared SSH key pair | Encrypted blob on VPS + gates |
| **Mid term** | BearDog `secrets.store`/`secrets.retrieve` via BTSP | FAMILY_SEED + BTSP handshake | BearDog's encrypted store on membrane |
| **Long term** | Autonomous rotation by membrane Tower | Membrane identity key | Generated and rotated by membrane BearDog, never shared as files |

Short-term tooling: `plasmidBin/membrane/share_credentials.sh` wraps
`age` encryption to SSH public keys. Any gate with the corresponding
private key can decrypt. See the script for usage.

### Tower on Membrane — Composition

When deployed with `--composition tower`, the membrane VPS runs the full
Tower atomic alongside the relay channels:

| Service | Role | Unit |
|---------|------|------|
| BearDog | BTSP handshake, secrets delegation, crypto key management | `beardog-membrane.service` |
| Songbird | Relay + discovery (Channel 2) | `songbird-relay.service` |
| SkunkBat | Defense audit, threat assessment, cross-boundary monitoring | `skunkbat-membrane.service` |

This composition enables the mid-term credential delegation pattern:
inner gates authenticate via BTSP to BearDog on the membrane, then
retrieve credentials without any file sharing.

### Evolution Milestones

1. **biomeOS on ironGate auto-provisions membrane channels** via
   `secrets.retrieve("membrane:doctl:token")` + `doctl`
2. **Membrane BearDog rotates TURN credentials autonomously** — no
   operator intervention for credential refresh
3. **Membrane NestGate serves public content** — replaces GitHub Pages,
   Channel 3 becomes sovereign
4. **Membrane SkunkBat audits all cross-boundary traffic** — anomaly
   detection on the membrane surface
5. **Operator's only role is initial FAMILY_SEED provisioning** and
   domain registration — everything else is autonomous

---

## cellMembrane fieldMouse Classification

The membrane VPS is formally classified as a **fieldMouse** deployment — the
first production instance of the fieldMouse deployment class on external
substrate.

| Property | Value |
|----------|-------|
| **Deployment class** | fieldMouse |
| **Composition** | Tower atomic (BearDog + Songbird + SkunkBat) + RustDesk (hbbs + hbbr) |
| **Substrate** | External (DigitalOcean VPS, nyc1) |
| **biomeOS** | None — static composition, no deploy graph |
| **Topology** | `ecoprimals-fieldmouse-chimera.yaml` (benchScale) |
| **Dark Forest** | Provider treated as non-family observer; sensitive data encrypted at rest |

The cellMembrane is not a gate, not a niche. It runs exactly the Tower
atomic turned outward — the same primals that handle trust, discovery, and
defense inside NUCLEUS, deployed to face the public internet.

### Hardening profile

Firewall is composition-aware — only ports required by active channels are
open. Current state (Tower + Channel 3 Surface live, May 2026):

| Port | Protocol | Purpose | Status |
|------|----------|---------|--------|
| 22 | TCP | SSH management (key-only, fail2ban) | **Open** |
| 80 | TCP | Channel 3: ACME challenge + redirect | **Open** (Caddy) |
| 443 | TCP | Channel 3: Surface (HTTPS) | **Open** (Caddy TLS, `membrane.primals.eco`) |
| 3478 | TCP + UDP | Channel 2: Relay (TURN) | **Open** |
| 21115 | TCP | Channel 2b: RustDesk NAT test | **Open** |
| 21116 | TCP + UDP | Channel 2b: RustDesk ID/hole-punch | **Open** |
| 21117 | TCP | Channel 2b: RustDesk relay | **Open** |
| 53 | UDP + TCP | Channel 1: Signal (DNS) | **Open** (knot-dns LIVE, Jun 4 — `primal.eco` + `nestgate.io`) |

Services purged: `exim4` (unnecessary mail server), `droplet-agent`
(opaque DO monitoring). Services added: `fail2ban` (SSH brute-force
protection), `hbbs-membrane` + `hbbr-membrane` (RustDesk relay).

See `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` for the full fieldMouse
specification, escalation ladder, and BingoCube verification roadmap.

---

## Deployment Tooling

### `plasmidBin/deploy_membrane.sh`

Provisions and deploys membrane channels to a VPS. Five modes, three
compositions:

```bash
./deploy_membrane.sh provision --region nyc1                  # Create droplet + deploy (relay)
./deploy_membrane.sh deploy root@<ip>                         # Deploy relay to existing VPS
./deploy_membrane.sh deploy root@<ip> --composition rustdesk  # Relay + RustDesk
./deploy_membrane.sh deploy root@<ip> --composition tower     # Full Tower + RustDesk
./deploy_membrane.sh keys add root@<ip> --name "gate" --pubkey "ssh-ed25519 ..."
./deploy_membrane.sh keys list root@<ip>
./deploy_membrane.sh status root@<ip>                         # Health check
./deploy_membrane.sh teardown --name membrane-relay           # Destroy droplet
```

All modes support `--dry-run` for plan-only inspection.

| Composition | Components | Use case |
|-------------|------------|----------|
| `relay` (default) | Songbird only | Channel 2 relay, minimal footprint |
| `rustdesk` | Songbird + hbbs/hbbr | Relay + remote desktop for geo-delocalized gates |
| `tower` | BearDog + Songbird + SkunkBat + hbbs/hbbr | Full Tower atomic + RustDesk |

### `plasmidBin/membrane/` — unit templates and tooling

| File | Purpose | Status |
|------|---------|--------|
| `songbird-relay.service` | Channel 2: Relay (:3478) | **Active** |
| `hbbs-membrane.service` | Channel 2b: RustDesk rendezvous (:21116) | **Active** |
| `hbbr-membrane.service` | Channel 2b: RustDesk relay (:21117) | **Active** |
| `beardog-membrane.service` | Tower: BTSP + crypto identity | **Active** (deployed with `--composition tower`) |
| `skunkbat-membrane.service` | Tower: Defense + audit | **Active** (deployed with `--composition tower`) |
| `share_credentials.sh` | `age`-based credential sharing between gates | **Active** |
| `knot-dns.service` | Channel 1: Signal (:53) | Future |
| `beardog-tls.service` | Channel 3: Surface (:443) | Future |
| `nestgate-content.service` | Channel 3: Surface (:443) | Future |

Each unit is security-hardened (`NoNewPrivileges`, `PrivateTmp`,
`ProtectSystem=strict`, `MemoryMax`, `CPUQuota`).

### Credential management

| Phase | Tool | Storage |
|-------|------|---------|
| **Current** | `age` + SSH ed25519 keys via `share_credentials.sh` | Encrypted blob on VPS (`/opt/membrane/credentials.age`) |
| **Mid term** | BearDog `secrets.store`/`secrets.retrieve` via BTSP | BearDog encrypted store on membrane |
| **Long term** | Autonomous rotation by membrane BearDog | Never stored as files |

DigitalOcean API tokens are stored at `~/.config/doctl/token` with
`chmod 600`. The deployment script uses `doctl` CLI (authenticated
separately) and never reads the token file directly.

---

## What Is Permanently External

| Dependency | Why | Risk | Mitigation |
|------------|-----|------|------------|
| DNS registrar | Shared global namespace (ICANN) | Domain seizure | Multiple domains, different registrars; `.onion` as bypass |
| Public IP (VPS) | NAT requires a routable relay point | Provider misbehavior | Stateless binary, switch providers in minutes; Model B across jurisdictions |
| Let's Encrypt (CA) | Browsers require CA-signed certs | CA compromise or policy change | Multiple ACME CAs; Certificate Transparency detects mis-issuance; BTSP for non-browser clients |

These three cannot be eliminated by software. They are structural
properties of the internet as a shared medium. The membrane channel
architecture ensures they are the *only* external dependencies, and
that each one sees the minimum possible information about NUCLEUS
internals.

---

## biomeOS Support (v3.58)

As of biomeOS v3.58, `composition.deploy(graph)` recognizes `composition_model = "membrane"`
as a first-class deployment topology. Graph metadata is parsed, validated, and preserved
through the neural-to-deployment conversion pipeline. The `composition.deploy.shadow`
dry-run also reports the composition model in its validation output.

The `CompositionModel` enum (`nucleated` | `membrane`) is orthogonal to
`AtomicComposition` (Tower/Node/Nest/Nucleus) — the former describes infrastructure
topology, the latter describes which primal bundles are required.

---

## Cross-References

- `GLACIAL_SHIFT_READINESS.md` — Pillar 2 deployment targets map to membrane channels
- `compute-sharing/SOVEREIGN_COMPUTE_SHARING.md` — NUC intake pattern is Channel 3 surface
- `compute-sharing/TUNNEL_ACCESS_GUIDE.md` — Tunnel evolution phases map to Channel 2
- `plasmidBin/deploy_membrane.sh` — Agentic provisioning and deployment script (supports `--composition relay|rustdesk|tower`, `keys` management)
- `plasmidBin/membrane/songbird-relay.service` — Channel 2 systemd unit template
- `plasmidBin/membrane/hbbs-membrane.service` — Channel 2b RustDesk rendezvous unit template
- `plasmidBin/membrane/hbbr-membrane.service` — Channel 2b RustDesk relay unit template
- `plasmidBin/membrane/beardog-membrane.service` — Tower BearDog systemd unit template
- `plasmidBin/membrane/skunkbat-membrane.service` — Tower SkunkBat systemd unit template
- `plasmidBin/membrane/share_credentials.sh` — `age`-based credential sharing between gates
- `handoffs/SONGBIRD_WAVE202_RELAY_OPS_DEPLOYMENT_MAY12_2026.md` — Songbird relay ops readiness
- `CELLMEMBRANE_FIELDMOUSE_DEPLOYMENT.md` — cellMembrane as fieldMouse Tower on external substrate
- `handoffs/PROJECTNUCLEUS_MEMBRANE_VPS_HANDOFF_MAY14_2026.md` — cellMembrane VPS ownership handoff
- `primalSpring/ecoPrimal/src/bonding/stun_tiers.rs` — STUN sovereignty-first escalation
- `primalSpring/ecoPrimal/src/composition/context.rs` — Discovery escalation hierarchy
- `BTSP_PROTOCOL_STANDARD.md` — BTSP phase definitions
- `EVOLUTION_STATUS_WAVE66.md` — Interstadial/stadial transition model
