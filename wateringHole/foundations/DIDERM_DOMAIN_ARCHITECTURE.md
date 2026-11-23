# Diderm Domain Architecture — Trust Barrier Model

**Authority**: Overwatch + Ecosystem Convention  
**Status**: Active (Wave 150s)  
**Date**: 2026-07-21  
**Prerequisites**: `DARK_FOREST_GLACIAL_GATE_STANDARD.md`, `SOVEREIGNTY_STANDARDS.md`, `OVERWATCH_POSITION_STANDARD.md`

---

## Abstract

The ecoPrimals ecosystem operates a diderm (double-membrane) architecture
across three web domains. The **peptidoglycan VPS layer** is the trust
barrier — an air gap between the outer membrane (world-facing, commercial
services acceptable) and the inner membrane (pure sovereign primals, zero
commercial in the data path). The peptidoglycan is disposable, replicable,
and provider-independent.

This document defines the trust model, domain assignments, Dark Forest
membrane classification, and the cross-membrane validation pattern that
makes the dual membrane stronger than either membrane alone.

---

## The Biological Model

In gram-negative bacteria, the diderm envelope has two membranes separated
by the periplasmic space containing peptidoglycan — a rigid structural
layer that gives the cell shape and mechanical strength while remaining
permeable to small molecules.

The ecoPrimals diderm follows this pattern:

```
                  Hostile Internet
                        │
          ┌─────────────┴──────────────┐
          │    OUTER MEMBRANE          │
          │    primals.eco             │
          │    Cloudflare + Caddy      │
          │    (world-facing surface)  │
          └─────────────┬──────────────┘
                        │
          ┌─────────────┴──────────────┐
          │    PEPTIDOGLYCAN           │
          │    Trust Barrier / Air Gap │
          │    Songbird TURN relay     │
          │    Temporal sync hub       │
          │    STORES NOTHING          │
          │    DISPOSABLE              │
          └─────────────┬──────────────┘
                        │
          ┌─────────────┴──────────────┐
          │    INNER MEMBRANE          │
          │    primal.eco              │
          │    Sovereign DNS + TLS     │
          │    Songbird mesh           │
          │    bearDog BTSP            │
          │    biomeOS orchestration   │
          │    (organism coordination) │
          └─────────────┬──────────────┘
                        │
          ┌─────────────┴──────────────┐
          │    CONTENT LAYER           │
          │    nestgate.io             │
          │    NestGate CAS            │
          │    BLAKE3 integrity        │
          │    pseudoSpores, notebooks │
          │    (data objects)          │
          └────────────────────────────┘
```

---

## Domain Assignments

| Domain | K-Derm Layer | DNS Authority | TLS Provider | Trust Level | Purpose |
|--------|-------------|--------------|-------------|-------------|---------|
| `primals.eco` | Intra-membrane (shared ecosystem) | Cloudflare (wildcard `*.primals.eco`) | Caddy + LE (per-site or on-demand) | **Shared trust** — ecosystem services | Ecosystem platform: depot, forge, compositions, public tools, docs |
| `primal.eco` | Inner membrane (personal sovereign) | Sovereign knot-dns | Sovereign Caddy + LE | **Full trust** — Dark Forest strict | Personal substrate: mesh API, relay, gate coordination, HPC federation, ceremonies |
| `nestgate.io` | Data service point (interaction layer) | Sovereign knot-dns | Sovereign Caddy + LE | **Content trust** — BLAKE3 integrity | Data service interaction: CAS backbone, federated APIs, weak bond data ingestion |

### Domain Identity

The three domains serve distinct roles:

- **`primals.eco`** — the **intra-membrane**. The ecosystem's shared
  infrastructure and public face. Root domain redirects to
  `sporeprint.primals.eco`. All compositions, tools, and services are
  subdomains: `prefix.primals.eco`. Subdomains are sovereign-routed:
  `*.primals.eco` resolves via a single Cloudflare wildcard A record,
  and Caddy on golgi handles all per-hostname routing. New services
  only need a Caddy block — no DNS changes. This is the layer between
  the personal inner membrane and the hostile internet. Cloudflare
  operates as the outer firebreak (DDoS, CDN), making `primals.eco`
  an intra-membrane — not directly exposed, but publicly accessible
  through the firebreak.
- **`primal.eco`** — the **inner membrane**. The operator's personal
  sovereign substrate. LAN/WAN mesh, private compositions, sovereign
  ceremony host. Key creation ceremonies (SoloKey FIDO2 + Pixel
  StrongBox entropy mixing), bearDog gatehouse, private compositions,
  HPC federation, and inner membrane coordination. This is where
  cryptographic sovereignty is exercised — entropy ceremonies,
  FAMILY_SEED management, BTSP authentication authority. This domain
  is a fully independent identity, not a mirror of `primals.eco`.
- **`nestgate.io`** — the **data service interaction point**. nestGate
  CAS as the content-addressed backbone. All external scientific and
  geospatial data sources (NCBI, PubMed, UniProt, USGS, FEMA, ArcGIS,
  etc.) enter through drawbridge-registered weak bonds and land in the
  CAS. The single public entry point for querying content-addressed
  sovereign data. The interaction layer for the ecosystem's data mesh.

**Composition routing by domain**: The same primals serve both domains, but
the trust level and data scope differ. A footPrint instance on
`footprint.primals.eco` shows public GIS data (shared projects, demo tiles).
A footPrint instance on `primal.eco` shows private property data, personal
measurements, and sovereign coordinates — backed by Loam Certificates for
provenance and bearDog-signed sessions for integrity. The domain determines
the membrane layer, which determines the trust model.

**Root domain standard**: `primals.eco` (bare) redirects to
`sporeprint.primals.eco`. All compositions use `prefix.primals.eco`
subdomains — no path-based routing on the root domain.

### DNS Routing Model (Wave 137b+)

| Record | Type | Content | Notes |
|--------|------|---------|-------|
| `primals.eco` | A | golgi VPS IP | Root domain (wildcard doesn't cover root) |
| `*.primals.eco` | A | golgi VPS IP | Wildcard — Caddy is routing authority |
| `www.primals.eco` | CNAME | `primals.eco` | www redirect |
| `ns2.primals.eco` | A | sovereign DNS IP | Different IP — keep explicit |

Caddy handles Host-header routing for all `*.primals.eco` subdomains.
Explicit Caddy server blocks take precedence over the wildcard catch-all.
Unknown subdomains return 404 via the catch-all block.

### Registrar

All three domains are on Porkbun. NS records are set per-domain:
- `primals.eco` → Cloudflare nameservers (outer membrane, wildcard DNS)
- `primal.eco` → `ns1.primals.eco` / `ns2.primals.eco` (sovereign)
- `nestgate.io` → `ns1.primals.eco` / `ns2.primals.eco` (sovereign)

---

## The Peptidoglycan Trust Barrier

### Properties

The peptidoglycan layer sits between outer and inner membranes. It is the
**only** point where they touch. It has these invariant properties:

| Property | Requirement |
|----------|------------|
| **Stores nothing** | Broker/relay only. No primary data, no user data, no secrets beyond `tower.env`. |
| **Disposable** | Can be torn down and reprovisioned from `membrane.toml` + `tower.env`. No state loss. |
| **Replicable** | Deployable on any VPS provider or self-hosted from a WAN-facing gate. |
| **Provider-as-adversary** | VPS provider is a non-family observer. Secrets encrypted at rest. |
| **BTSP-opaque** | All relay traffic is encrypted end-to-end. Peptidoglycan relays but cannot read, modify, or forge inner membrane traffic. |
| **Unidirectional flow** | Outer pushes TO peptidoglycan. Inner pulls FROM peptidoglycan. Neither reaches the other directly. |

### Current Deployment

| Node | IP | Layer | Role |
|------|----|-------|------|
| golgiBody-ext | 137.184.197.151 | Outer membrane | Caddy TLS, sporePrint, DNS ns2 |
| peptidoglycan | [RELAY_PUBLIC] | Trust barrier | Songbird TURN, temporal sync, Forgejo relay |
| golgiBody | [RELAY_PUBLIC] | Inner membrane | knot-dns ns1, Forgejo, sovereign DNS |

### Multi-Peptidoglycan

The peptidoglycan is a **role**, not a single VPS. It can be fulfilled by:

| Instance | Provider | Purpose | Status |
|----------|----------|---------|--------|
| peptidoglycan-nyc1 | DigitalOcean | Primary relay | **OPERATIONAL** |
| peptidoglycan-eu | Hetzner | Geographic redundancy | Future |
| peptidoglycan-self | Self-hosted WAN gate | Remove VPS dependency | Future |
| peptidoglycan-abg | ABG member hosted | Federation relay | Future |

The inner membrane discovers peptidoglycan instances through Songbird TURN
peer registration. Adding a new instance requires only:
1. Deploy `membrane.toml` with `composition = "peptidoglycan"`
2. Start Songbird TURN on the new instance
3. Inner membrane gates add it to `SONGBIRD_PEERS`

### Self-Hosting Path

When a WAN-facing gate has a public IP (flockGate already does, via
cellMembrane relay), it can serve the peptidoglycan role directly. The
VPS peptidoglycan then becomes redundant — the organism grows its own
structural layer. This is the sovereignty endgame for the structural
layer: zero external substrate dependency.

---

## Dark Forest Membrane Classification

The 5 Dark Forest pillars (from `DARK_FOREST_GLACIAL_GATE_STANDARD.md`)
apply with different strictness per membrane layer:

### Pillar 1: Zero Metadata Leakage

| Layer | Classification | What Leaks | Acceptable? |
|-------|---------------|-----------|-------------|
| Outer | **RELAXED** | Cloudflare sees visitor IPs, headers, timing, geographic distribution | Yes — this is the world-facing surface. Its job is to absorb hostile traffic. |
| Peptidoglycan | **STRICT** | VPS provider sees only encrypted relay traffic volume and timing. No primal identity, no capability surface, no content. | Provider metadata (connection timing, bandwidth) is the residual. Acceptable for relay. |
| Inner | **STRICT** | Zero metadata leakage. Stripped binaries, no hostnames embedded, BirdSong encrypted. | No exceptions. |

### Pillar 2: Zero Port Exposure

| Layer | Classification | Exposed Ports |
|-------|---------------|--------------|
| Outer | **RELAXED** | 80/443 (Caddy HTTP/HTTPS), 53 (DNS ns2) |
| Peptidoglycan | **STRICT** | 3478 (TURN relay), 2222 (Forgejo SSH relay), 22 (admin SSH) |
| Inner | **STRICT** | UDS-only default. Songbird :7700 is the sole federation surface on LAN. |

### Pillar 3: Songbird as Sole Network Surface

| Layer | Classification | Network Surface |
|-------|---------------|----------------|
| Outer | **N/A** | Caddy is the network surface by design. |
| Peptidoglycan | **STRICT** | Only Songbird TURN relay handles cross-membrane traffic. |
| Inner | **STRICT** | All external traffic routes through Songbird. No primal directly opens external listeners. |

### Pillar 4: BTSP Crypto Integrity

| Layer | Classification | BTSP Role |
|-------|---------------|-----------|
| Outer | **N/A** | External users don't use BTSP. Authentication is Cloudflare-level or public. |
| Peptidoglycan | **STRICT** | BTSP tokens are **opaque** to peptidoglycan. It relays encrypted payloads. It cannot issue, verify, or modify tokens. |
| Inner | **STRICT** | Full BTSP enforcement. ChaCha20-Poly1305 AEAD. Cross-gate token verification via TrustedIssuerRegistry. |

### Pillar 5: Enclave Computing

| Layer | Classification | Compute Role |
|-------|---------------|-------------|
| Outer | **N/A** | No compute — serves static content and proxies. |
| Peptidoglycan | **STRICT** | No biomeOS, no orchestration, no compute dispatch. Pure relay. |
| Inner | **STRICT** | Full enclave boundaries. toadStool dispatch, barraCuda ML, coralReef SPIR-V — all BTSP-gated. |

### The Key Rule

**Peptidoglycan MUST NOT be able to read, modify, or forge inner membrane
traffic.** It is a dumb pipe. cellMembrane Wave 75 confirmed: "BTSP tokens
OPAQUE in all relay channels." This is the trust barrier invariant.

---

## Cross-Membrane Validation

The dual membrane creates a **permanent integrity monitoring pattern**.
The inner membrane is the ground truth. The outer membrane is always
under suspicion.

### Validation Checks

| Check | Method | What It Catches |
|-------|--------|----------------|
| Content integrity | Same resource via outer (`primals.eco`) and inner (`primal.eco`), compare BLAKE3 hashes | CDN injection, content modification, stale cache |
| Timing baseline | Inner membrane response time is the floor. Outer should be inner + CDN overhead. | Unexpected latency = interception or throttling |
| Availability cross-check | Inner healthy + outer reports down = external service failure, not real downtime | Cloudflare outage, regional blocking |
| TLS certificate verification | Inner membrane knows the real LE certificate fingerprint. Compare with outer. | Certificate substitution (Cloudflare MITM by design issues its own cert) |
| DNS consistency | Query sovereign NS (`ns1.primals.eco`) vs public resolver (`8.8.8.8`). Compare. | DNS poisoning, hijacking, registrar compromise |
| Route integrity | Traceroute from inner membrane to outer. Known hop count as baseline. | BGP hijacking, route injection |

### Why This Is Stronger Than Eliminating Cloudflare

Eliminating Cloudflare removes DDoS protection and CDN benefits.
Keeping Cloudflare on the outer membrane but validating from the inner
membrane gives you **both**:

- External traffic protection (Cloudflare absorbs DDoS, bots, scanners)
- Integrity verification (inner membrane detects any tampering)
- Graceful degradation (if outer membrane is compromised, inner membrane
  continues serving trusted peers directly)

The dual membrane is not a transitional state. It is the **target
architecture**.

---

## Inner Membrane Use Cases (primal.eco)

| Subdomain | Service | Purpose |
|-----------|---------|---------|
| `mesh.primal.eco` | Songbird | Federation endpoint for gate-to-gate mesh |
| `relay.primal.eco` | Songbird TURN | Peptidoglycan relay endpoint |
| `auth.primal.eco` | bearDog BTSP | Token exchange, trust establishment |
| `api.primal.eco` | biomeOS | Internal API for orchestration and dispatch |
| `dns.primal.eco` | knot-dns | Sovereign DNS management interface |

### ABG Federation

An ABG member spinning up their own HPC gate joins via `primal.eco` mesh:
1. Deploy their own peptidoglycan (or connect directly if LAN-reachable)
2. Start bearDog with family seed enrollment
3. Start Songbird with `SONGBIRD_PEERS` pointing to `relay.primal.eco`
4. Inner membrane discovers them via `discovery.peers`
5. Sovereign trust only — no commercial service in the data path
6. Shared compute via BTSP-authenticated `capability.call`

---

## Content Layer Use Cases (nestgate.io)

| URL Pattern | Service | Purpose |
|-------------|---------|---------|
| `nestgate.io/<blake3-hash>` | NestGate CAS | Direct content-addressed fetch |
| `nestgate.io/spore/<name>` | NestGate + pseudoSpore | Named pseudoSpore access |
| `nestgate.io/notebook/<id>` | NestGate + petalTongue | Rendered notebook view |
| `nestgate.io/manifest/<name>` | NestGate cas-manifest | sporePrint content manifests |

Content integrity is sovereign regardless of delivery path. Even if served
through a CDN, BLAKE3 hashes verify end-to-end. The content layer can
optionally use outer membrane CDN for performance while inner membrane
verifies integrity.

**Backing store**: westGate 76TB ZFS pool (primary), federated across gates
via `content.replicate.pull` on inner membrane.

---

## Sovereignty Shadow Evolution

The sovereignty shadows (S1-S5) now apply specifically to the inner membrane:

| Track | What | Inner Membrane | Outer Membrane |
|-------|------|---------------|----------------|
| S1 TLS | TLS termination | Caddy + LE on golgiBody (sovereign, MUST) | Cloudflare proxy (acceptable) |
| S2 NAT | NAT relay | Songbird TURN (GRADUATED) | N/A |
| S3 Content | Content serving | NestGate CAS on `nestgate.io` (sovereign) | sporePrint via Caddy or CDN (acceptable) |
| S4 Auth | Authentication | bearDog BTSP enforced (sovereign, MUST) | Public/Cloudflare auth (acceptable) |
| S5 DNS | DNS resolution | knot-dns for `primal.eco` + `nestgate.io` (sovereign, MUST) | Cloudflare DNS for `primals.eco` (acceptable) |

The principle: **inner membrane MUST be fully sovereign. Outer membrane
MAY use commercial services.** Cross-membrane validation ensures the outer
membrane stays honest.

---

## Sovereignty Evolution Roadmap (Wave 150s)

The ecosystem contains industry tools at various membrane layers. This
roadmap classifies each by its evolution path: **Replace** (primal
composition replaces the tool), **Late-Stage** (replacement blocked on
a prerequisite primal), or **Firebreak** (stays on outer membrane by
design — industry tools absorbing hostile traffic is the correct
architecture).

### Three-Tier Classification

| Tool | Current Layer | Classification | Primal Path | Priority |
|------|-------------- |---------------|-------------|----------|
| **WireGuard** | Transport (kernel) | **REPLACE** | Tower Atomic (bearDog + songBird + skunkBat) | Phase 1 |
| **Zola** | Build (sporePrint) | **REPLACE** | petalTongue rendering + nestGate CAS content | Phase 1 |
| **Forgejo** | Intra-membrane (git hosting) | **LATE-STAGE** | rootPulse (nestGate CAS + Provenance Trio) | Phase 2 (post-rootPulse) |
| **Cloudflare** | Outer membrane (DNS/DDoS) | **FIREBREAK** | N/A — this IS the firebreak | Stays |
| **Caddy** | Outer membrane (TLS/proxy) | **FIREBREAK** | cellMembrane generates config; Caddy serves | Stays |
| **Let's Encrypt** | Outer membrane (TLS certs) | **FIREBREAK** | ACME is the standard | Stays |
| **Porkbun** | External (registrar) | **FIREBREAK** | Registrars are inherently external | Stays |
| **RustDesk** | Outer membrane (human access) | **FIREBREAK** | AGPL-3.0 compliant; learn-from-leverage | Stays |
| **JupyterHub** | Outer membrane (interface) | **FIREBREAK** | Interface only; compute is inner membrane | Stays (repositioned) |

### Phase 1: Tower Atomic Supersedes WireGuard

WireGuard currently provides the kernel-level encrypted mesh between
gates. songBird already operates as a sovereign mesh overlay on top of
WireGuard, and Tower Atomic (bearDog + songBird + skunkBat) handles
authenticated encrypted transport end-to-end.

The target: Tower Atomic **meets and exceeds** WireGuard's capabilities,
making the kernel VPN redundant. When Tower can provide:

| Capability | WireGuard Today | Tower Atomic Target |
|-----------|----------------|-------------------- |
| Encrypted tunnel | ChaCha20-Poly1305 (kernel) | BTSP ChaCha20-Poly1305 AEAD (userspace, sovereign keys) |
| Peer discovery | Static config (`wg0.conf`) | songBird dynamic peer discovery + TURN relay |
| Key management | Manual pubkey exchange | bearDog BTSP trust establishment, FAMILY_SEED rooted |
| NAT traversal | Requires manual endpoint config | songBird TURN + skunkBat hole-punching |
| Reconnection | Automatic (kernel) | songBird persistent mesh with exponential backoff |
| Performance | Kernel-space, ~1 Gbps | Userspace — must benchmark to WG baseline |

**Parity gate**: Tower must demonstrate equivalent throughput and latency
on the LAN mesh before WireGuard can be removed. Performance benchmark
is the only remaining criterion — all other capabilities are already
sovereign.

### Phase 1: Primal sporePrint Pipeline Replaces Zola

sporePrint currently uses Zola (Rust static site generator) to build
`sporeprint.primals.eco`. The primal replacement pipeline:

```
Content (markdown/data) → nestGate CAS (content-addressed storage)
  → petalTongue (rendering: WASM WebGL + SVG + description)
    → cellMembrane (serving: Caddy config generation)
      → primals.eco (public surface)
```

petalTongue's WASM WebGL pipeline (Wave 150r) is the enabling step —
browser-side rendering is now fully primal. The remaining work is
wiring sporePrint's content pipeline to emit from CAS rather than
Zola's file-based build.

### Phase 2: rootPulse Replaces Forgejo (Late-Stage)

Forgejo (`git.primals.eco`) is a solid intra-membrane tool — self-hosted,
functional, not in the inner membrane data path. Replacement only happens
when **rootPulse** is live:

- rootPulse = sovereign version control backed by nestGate CAS +
  Provenance Trio (rhizoCrypt lineage, loamSpine ledger, sweetGrass
  attribution)
- Git-compatible interface over CAS-backed storage
- Loam Certificates for commit provenance (replacing GPG signatures)
- This is explicitly **not a near-term priority** — Forgejo serves well

### Firebreak Tools: Outer Membrane by Design

**RustDesk** (AGPL-3.0): License-compliant with the ecosystem's
open-source model. The ecosystem learns from and leverages RustDesk's
relay architecture. It provides human-operator remote access on the
outer membrane, coexisting with MitoBeacon (autonomous identity on the
inner membrane). As MitoBeacon matures, RustDesk's role naturally
narrows to human-in-the-loop scenarios.

**JupyterHub**: Repositioned as **outer membrane interface only**.
ABG members, external collaborators, and human scientists use JupyterHub
as a web interface that submits work to inner membrane primals (biomeOS
orchestration → toadStool dispatch → barraCuda compute). JupyterHub
never processes sovereign data itself — it is a submission portal. The
actual workload executes entirely within the inner membrane enclave.

**Cloudflare, Caddy, Let's Encrypt, Porkbun**: These are the correct
tools for absorbing hostile internet traffic. The outer membrane's job
is to face the storm. The inner membrane's job is to coordinate the
organism. Industry tools on the outer membrane are not debt — they are
the firebreak.

---

## Peptidoglycan Composition Specification

### membrane.toml Schema

```toml
[membrane]
name = "peptidoglycan-nyc1"
composition = "peptidoglycan"

[membrane.identity]
family_id = "membrane-alpha"
gate_id = "pepti-nyc1"

[membrane.provider]
type = "digitalocean"
region = "nyc1"

[membrane.channels.relay]
enabled = true
port = 3478
primal = "songbird"

[membrane.channels.sync]
enabled = true
port = 2222

[membrane.channels.surface]
enabled = false

[membrane.trust_barrier]
inner_domain = "primal.eco"
outer_domain = "primals.eco"
opaque_relay = true
```

### Lifecycle

```
provision → harden → deploy → validate → operate → [teardown → reprovision]
                                                          │
                                                   No data loss.
                                                   tower.env is the only state.
                                                   Inner membrane unaffected.
```

### Deploy Anywhere

```bash
# DigitalOcean (current)
deploy_membrane.sh --composition peptidoglycan --provider digitalocean --region nyc1

# Hetzner (future redundancy)
deploy_membrane.sh --composition peptidoglycan --provider hetzner --region fsn1

# Self-hosted from WAN gate
deploy_membrane.sh --composition peptidoglycan --provider bare_metal --host flockgate.local
```

---

## Revised Glacial Shift Criteria

| # | Criterion | Revised Meaning |
|---|-----------|----------------|
| 1 | Sovereignty shadows graduated (inner membrane) | S1-S4 on `primal.eco` path. Outer membrane may use commercial TLS. |
| 2 | Multi-gate LAN mesh operational (3+) | Songbird mesh on inner membrane. eastGate + strandGate + westGate. |
| 3 | Peptidoglycan replicable | Can be torn down and redeployed from `membrane.toml`. Trust barrier tested. |
| 4 | Remote covalent node over WAN | Via inner membrane only (TURN through peptidoglycan). |
| 5 | DNS sovereign for inner membrane | `primal.eco` + `nestgate.io` on knot-dns. `primals.eco` on Cloudflare OK. |
| 6 | Inner membrane zero-commercial + cross-validation | Zero commercial in `primal.eco` data path. Dual-path validation operational. |

---

## References

- `DARK_FOREST_GLACIAL_GATE_STANDARD.md` — 5 security invariants
- `SOVEREIGNTY_STANDARDS.md` — Calibrate → Shadow → Cutover protocol
- `OVERWATCH_POSITION_STANDARD.md` — Floating coordination role
- `FIELDMOUSE_CONTRACT.md` — fieldMouse deployment contract (peptidoglycan is a fieldMouse)
- `MULTI_MEMBRANE_DEPLOYMENT.md` — Multi-membrane parameterization model
- `DEPLOYMENT_PHASE_PLAN.md` — Phased deployment from parity to stadial entry
- `whitePaper/gen5/foundations/COVALENT_MESH_TRUST_VALIDATION.md` — Cross-gate trust model
- `whitePaper/gen5/foundations/KDERM_DIDERM_APPLICATION.md` — K-Derm bonding model

---

## Changelog

| Wave | Change |
|------|--------|
| 77 | Initial: formalized diderm domain architecture with peptidoglycan trust barrier, Dark Forest membrane classification, cross-membrane validation pattern, revised glacial shift criteria. |
| 137b | Wildcard `*.primals.eco` DNS active. Domain identity separation formalized: `primals.eco` (public platform), `primal.eco` (sovereign substrate + entropy ceremonies + private compositions), `nestgate.io` (federated data gateway). Composition routing by domain documented (same primals, different trust/data scope per domain). Loam Certificate vs TLS credential terminology applied. |
| 150d | Domain terminology refined: `primals.eco` = intra-membrane (shared ecosystem), `primal.eco` = inner membrane (personal sovereign), `nestgate.io` = data service interaction point. Root domain redirect: `primals.eco` → `sporeprint.primals.eco`. Subdomain standard enforced for all compositions. sporePrint gets own subdomain. |
| 150j | **Git relay layer activated**: Forgejo (`git.primals.eco`) is sovereign primary for all source code. GitHub is subordinate outer membrane mirror. 39/39 repos have Forgejo push mirrors (`sync_on_commit: true`, HTTPS token auth via golgiBody). Gates push to Forgejo only — golgiBody relays to GitHub automatically on every commit. GitHub SSH surface consolidated from 12 per-gate keys to 2 (`forgejo-relay@golgiBody` + `golgiBody-ext@vps`). Sync divergence structurally eliminated. |
| 150s | **Sovereignty Evolution Roadmap**: Three-tier classification (Replace / Late-Stage / Firebreak). Phase 1: WireGuard → Tower Atomic, Zola → primal sporePrint pipeline. Phase 2: Forgejo → rootPulse (post-Provenance Trio). Firebreak stays: Cloudflare, Caddy, RustDesk (AGPL-3.0), JupyterHub (repositioned as outer membrane interface). DNSSEC 3/3 domains validated. |

---

*"The outer membrane faces the storm. The inner membrane coordinates the
organism. Between them, the peptidoglycan stands — thin, disposable,
replaceable — but structurally essential. It is the air gap that makes
sovereignty possible while the world still rages outside."*
