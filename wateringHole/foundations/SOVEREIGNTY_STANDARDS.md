<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Sovereignty Standards — Ecosystem Behaviors for Sovereign Evolution

**Date**: May 15, 2026 (updated Jul 7, 2026 — Wave 133d: sporePrint NUCLEUS on golgi, bearDog CryptoProvider blocker identified, WAN mesh overlay live)
**Status**: Active
**Authority**: WateringHole Consensus
**Audience**: All primals, all compositions, all deployments

---

## Purpose

This document defines the **standards and behaviors** that govern the
ecoPrimals ecosystem's progressive sovereignty evolution. Every primal,
composition, and deployment inherits these constraints. They are not
aspirational — they are enforced by validation tooling (darkforest,
benchScale, deploy graphs, composition validators).

---

## Core Principles

### 1. Stability First, Sovereignty Second

External services are **calibration instruments**, not enemies. Each
provides production-grade baselines (latency, availability, throughput,
error rates, security). No external dependency is removed until its
primal replacement **proves parity or superiority** under real load.

**Priority order** (from `SOVEREIGNTY_VALIDATION_PROTOCOL.md`):
1. **Stability / Security** — system stays up, data stays safe
2. **Sovereign solutions** — replace externals with primals
3. **Rust** — prefer Rust implementations for auditability
4. **Primal composition** — prefer composed primals over monoliths

### 2. Calibrate → Shadow → Cutover

Every sovereignty replacement follows a three-step protocol:

1. **Calibrate**: Capture baseline metrics from the external service
   (p50/p95/p99 latency, uptime %, error rates, throughput). Minimum
   7-day capture window.
2. **Shadow**: Run the primal replacement in parallel. Same traffic,
   separate port. Log both paths. Compare metrics daily.
3. **Cutover**: Switch traffic to the primal replacement only when
   shadow metrics meet or exceed baselines. Keep the external as
   fallback for 7 days post-cutover.

**No big-bang migrations.** Each step is independently reversible.

### 3. Gate as Source, VPS as Touchpoint

The gate hardware is the source of truth. The VPS is a touchpoint —
it terminates TLS, relays traffic, and caches content, but it owns
nothing. All state lives inside the gate's intracellular membrane.

### 3b. Diderm Membrane Architecture (Wave 77b)

The VPS layer is refined into a diderm (double-membrane) model with a
peptidoglycan trust barrier. See `DIDERM_DOMAIN_ARCHITECTURE.md` for
the complete specification.

| Layer | Domain | Trust | Dark Forest | Example |
|-------|--------|-------|-------------|---------|
| **Intracellular** | — | Covalent (full trust) | STRICT | Active gate, 13 primals |
| **Inner membrane** | `primal.eco` | Full sovereign trust | STRICT — zero commercial | golgiBody (knot-dns, Forgejo, mesh API) |
| **Peptidoglycan** | — | Trust barrier (opaque relay) | STRICT — broker only | peptidoglycan VPS (Songbird TURN, sync) |
| **Outer membrane** | `primals.eco` | Verified by cross-validation | RELAXED — commercial OK | golgiBody-ext (Caddy, Cloudflare CDN) |
| **Content organelle** | `nestgate.io` | Content trust (BLAKE3) | STRICT — sovereign DNS/TLS | NestGate CAS (pseudoSpores, notebooks) |
| **Extracellular** | — | Weak (Dark Forest) | N/A | crates.io, NCBI, Let's Encrypt |

**Key principle**: The inner membrane MUST be fully sovereign — zero
commercial services in the `primal.eco` data path. The outer membrane
MAY use commercial services (Cloudflare). The peptidoglycan is the air
gap between them — disposable, replicable, stores nothing.

Cross-membrane validation ensures the outer membrane stays honest:
the inner membrane compares BLAKE3 content hashes, TLS certificate
fingerprints, timing baselines, and DNS consistency between both paths.

---

## Bonding Model in Infrastructure

The four-bond model from chemistry maps to infrastructure trust:

### Covalent (Shared Seed, Full Trust)
- **Scope**: All content, all methods, all state
- **Auth**: BearDog family seed, BTSP mutual auth
- **Where**: LAN cluster (active gate ↔ strandGate), covalent gate mesh
- **Routing**: Direct dispatch, zero relay overhead
- **Example**: Two machines in the same basement sharing a family seed

### Ionic (Scoped Token, Metered Access)
- **Scope**: Scoped by capability token (e.g., `compute.*` but not `storage.*`)
- **Auth**: BearDog Ed25519-signed ionic tokens with expiry + JTI
- **Where**: ABG collaborators, friend's GPU, JupyterHub users
- **Routing**: Authenticated BTSP tunnel, resource envelopes enforced
- **Example**: A collaborator running notebooks through JupyterHub

### Metallic (Delocalized, Institutional)
- **Scope**: Fleet-wide capability sharing, no single-point trust
- **Auth**: Institutional certificate chain + BTSP overlay
- **Where**: University HPC (ICER), datacenter fleets
- **Routing**: biomeOS mesh routing, sunCloud economics
- **Example**: ICER cluster nodes joining as metallic compute providers

### Weak (Pre-Trust, External)
- **Scope**: Read-only public data, health checks, ACME challenges
- **Auth**: None (or Let's Encrypt ACME)
- **Where**: CDN fallback, Dark Forest beacons, initial contact
- **Routing**: VPS cache serves, no gate involvement
- **Example**: A browser hitting primals.eco for the first time

---

## Content-Aware Routing Standard

All membrane deployments must implement content-aware routing. Requests
are classified by type and routed to the appropriate backend:

| Content Class | Backend | Rationale |
|---------------|---------|-----------|
| ACME challenges | VPS local | Must be served from the IP the cert is for |
| Health/status | VPS local | Always available, zero gate dependency |
| Static assets (CSS/JS/images) | VPS cache (NestGate) | Cached locally, webhook-invalidated |
| Git operations | Gate (BTSP tunnel) | Authenticated, stateful |
| API/RPC | Gate (BTSP tunnel) | Authenticated, requires primal access |
| Auth flows | Gate (BTSP tunnel) | BearDog handles all identity |
| Large downloads (>50MB) | Songbird P2P | Avoid VPS bandwidth costs |
| Fallback | GitHub CDN | Last resort, always available |

**Cache policy**: 256MB max per VPS, 1-hour TTL, webhook-based invalidation
from gate NestGate. Cache misses proxy to gate via BTSP tunnel.

**Cost awareness**: Prefer P2P for large transfers. VPS bandwidth is metered.

---

## Membrane Channel Standards

Three channels define the cell's external interfaces (see
`MEMBRANE_CHANNEL_ARCHITECTURE.md` for full specification):

### Channel 1: Signal (DNS)
- **Process**: knot-dns on VPS
- **Port**: 53
- **Trust**: Lowest — public data
- **Status**: **PROPAGATED** (Jun 4) — `primal.eco` + `nestgate.io` zones live on sovereign knot-dns. Public resolvers (8.8.8.8, 1.1.1.1) resolve correctly. DNSSEC enabled.

### Channel 2: Relay (NAT Traversal)
- **Process**: Songbird TURN relay on VPS
- **Port**: 3478
- **Trust**: Credential-authenticated (HMAC)
- **Status**: LIVE ([RELAY_PUBLIC])

### Channel 2b: Remote Access (RustDesk)
- **Process**: hbbs/hbbr on VPS
- **Ports**: 21115-21117
- **Trust**: Key-authenticated (ed25519)
- **Status**: LIVE

### Channel 3: Surface (TLS)
- **Process**: Caddy (transitional) → BearDog (sovereign)
- **Ports**: 80 (ACME/redirect), 443 (TLS termination)
- **Trust**: ACME cert (Let's Encrypt E8), content-aware routing
- **Status**: **LIVE** — `membrane.primals.eco`, Caddy TLS. sporePrint NUCLEUS deployed on golgi (212 pages, Zola-rendered). BearDog ACME shadow **BLOCKED** — `CryptoProvider` panic in `rustls-rustcrypto` (UNIT-DIV-04). Caddy→bearDog cutover deferred to Wave 134b sovereignty sprint. DNS `primals.eco` still on Cloudflare (acceptable per diderm outer membrane).

**Primal role clarification**:
- **Songbird** handles TLS termination (long-term sovereign TLS)
- **BearDog** handles cryptographic identity (key management, BTSP, encryption)
- **Caddy** is transitional — used until Songbird absorbs TLS capability

---

## Credential Management Standard

### At Rest
All credentials on external substrate (VPS) must be encrypted at rest:
- **Method**: BearDog AES-256-GCM with Argon2id KDF
- **Key storage**: BearDog keyring (`beardog key generate`)
- **Format**: `.age` files (e.g., `/opt/membrane/credentials.age`)
- **Verification**: darkforest MEM-15 checks encryption at rest

### In Transit
- **BTSP Phase 3 AEAD** for all inter-primal communication
- **TLS** for browser-facing connections
- **SSH key-only** for VPS management (no passwords)

### Rotation
- Cookie secrets: monthly via `rotate_cookie_secret.sh`
- SSH keys: via `deploy_membrane.sh keys {add,revoke}`
- Ionic tokens: scoped expiry (purpose-based via `auth.issue_session`)

---

## VPS Deployment Standard

### Sizing
| Phase | SKU | RAM | Services | Cost |
|-------|-----|-----|----------|------|
| 0.5 (relay-only) | s-1vcpu-512mb-10gb | 512MB | Songbird + RustDesk | ~$4/mo |
| 1.0 (Tower) | s-1vcpu-2gb | 2GB | + BearDog + SkunkBat + Caddy | ~$12/mo |
| 2.0 (full membrane) | s-2vcpu-4gb | 4GB | + knot-dns + NestGate cache | ~$24/mo |

### Service Persistence
- All services managed by systemd with `Restart=always`
- Runtime directories via `tmpfiles.d/membrane.conf` (survives reboots)
- All primal ports on `127.0.0.1` except explicit public listeners
- Logs via journald (persistent to `/var/log/journal/`)

### Security Baseline
Validated by `darkforest_membrane.sh` (MEM-01 through MEM-15):
- SSH: key-only, fail2ban, multi-gate managed
- Firewall: UFW deny-default + targeted allows
- Services: no unnecessary packages (exim4, droplet-agent, snapd purged)
- Credentials: 600 permissions, root-owned, encrypted where possible
- Binary integrity: BLAKE3 checksums (when b3sum installed)

---

## Forgejo as Inner Membrane Mirror

### Standard (current model — May 24, 2026)
- **GitHub is operationally primary** (outer membrane) — all dev pushes go here
- **Forgejo is the trailing inner membrane mirror** — pulls from GitHub server-side
- **No per-machine sync required** — dev happens across multiple gates
- **When covalent gates host Forgejo, we invert**: Forgejo becomes primary

### Operational Reality (Jul 2026, Wave 133d)

Forgejo runs on golgi (`git.primals.eco`). 39 repos tracked via golgi
bidirectional relay (`membrane-temporal-cascade.timer`, 15-min cycle).
Relay handles GitHub↔Forgejo sync automatically. All primals, springs,
gardens, infra repos synced bidirectionally. Push protocol: gates push to
BOTH remotes (origin=GitHub, forgejo=Sovereign). golgi relay reconciles
any drift.

CI runs on GitHub Actions. See `REPO_MEMBRANE_BOUNDARY.md` for the full
repo classification (inner-only / trailing mirror / outer-only).

**cellMembrane** is the only private repo in the sporeGarden org on GitHub.
It should move to Forgejo-only when covalent gates host Forgejo.

### Organization Mapping
| Forgejo Org | GitHub Org | Repo Count |
|-------------|-----------|------------|
| sporeGarden | sporeGarden | 5 (4 public + 1 private: cellMembrane) |
| ecoPrimals | ecoPrimals | 19 |
| syntheticChemistry | syntheticChemistry | 8 |

### Migration Path
1. ~~GitHub-only development~~ — completed May 23, 2026
2. ~~Push-based sync~~ — replaced May 23 (doesn't scale to multi-gate)
3. **Current**: Forgejo pulls from GitHub server-side. GitHub primary for CI/dev.
4. **Near-term**: Port `notify-sporeprint.yml` to Forgejo Actions, CI parity
5. **Inversion**: Covalent gates host Forgejo → primary. GitHub becomes push mirror.

See: `REPO_MEMBRANE_BOUNDARY.md` for detailed repo classification and sync tooling

---

## Validation Standards

### Dark Forest Glacial Gate (deploy graph validation)
All deploy graphs must pass `dark_forest_gate_local.sh` (33 checks, 5 pillars):
- `secure_by_default = true` in `[graph.metadata]`
- All nodes reference valid plasmidBin binaries
- Dependency ordering is acyclic
- Port assignments are unique
- Auth mode defaults to `enforced`

### Membrane Audit (VPS validation)
`darkforest_membrane.sh` validates MEM-01 through MEM-15:
- SSH hardening, firewall posture, credential permissions
- Service inventory, listener audit, binary integrity
- Credential encryption at rest

### Sovereignty Parity (shadow run validation)
benchScale scenarios validate replacement parity:
- `btsp_tls_parity.sh` — BearDog TLS vs Cloudflare TLS
- `songbird_nat_parity.sh` — Songbird TURN vs cloudflared
- `nestgate_content_parity.sh` — NestGate+petalTongue vs GitHub Pages
- `dot_sovereign_parity.sh` — knot-dns vs Cloudflare DNS

---

## Sovereignty Shadow Membrane Applicability (Wave 77b)

Under the diderm model, the sovereignty shadow tracks (S1-S5) apply
specifically to the **inner membrane** (`primal.eco`). The outer membrane
(`primals.eco`) may retain commercial services.

| Track | What | Inner Membrane (`primal.eco`) | Outer Membrane (`primals.eco`) |
|-------|------|------------------------------|-------------------------------|
| **S1** TLS | TLS termination | Sovereign Caddy + LE (**MUST**) | Cloudflare proxy (acceptable) |
| **S2** NAT | NAT relay | Songbird TURN (**GRADUATED**) | N/A |
| **S3** Content | Content serving | NestGate CAS on `nestgate.io` (sovereign) | sporePrint NUCLEUS on golgi (212pp, Zola). Inner membrane cutover pending bearDog fix (134b). |
| **S4** Auth | Authentication | bearDog BTSP enforced (**MUST**) | Public/Cloudflare auth (acceptable) |
| **S5** DNS | DNS resolution | knot-dns for `primal.eco` + `nestgate.io` (**MUST**) | Cloudflare DNS for `primals.eco` (acceptable) |

**Cutover protocol unchanged**: Each track still follows Calibrate → Shadow
→ Cutover. The change is that graduation criteria apply to the inner membrane
path, not the outer.

---

## Wave 68 Strategic Domains

Four new strategic tracks added to the sovereignty evolution:

| Domain | Description | Design Doc | Status |
|--------|-------------|-----------|--------|
| **Songbird Routing Consolidation** | TCP Tier 5 blocked in release; virtual endpoint relay for single-ingress; membrane TLS sovereignty | `SONGBIRD_VIRTUAL_ENDPOINT_RELAY_DESIGN.md` | Phase A: DONE. Phase B: DESIGNED. Phase C: ironGate. |
| **Neural API Perceptron** | Evolve rule-based routing to learned single-layer perceptron; shadow mode graduation protocol | `NEURAL_API_PERCEPTRON_DESIGN.md` | L4 impulse dispatched. L5: DESIGNED. |
| **grapheneGate Trust Anchor** | Pixel 8a as portable physical root of trust; Dark Forest beacon; sovereign mesh seed | `GRAPHENEGATE_BOOTSTRAP_STANDARD.md` | Manifest + standard: DONE. Role 1: P2. |
| **Topology-Aware Routing** | Network segment model; latency in discovery.peers; affinity-biased dispatch | `TOPOLOGY_MAP.toml` | Topology map: DONE. Routing impulse: dispatched. |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-07 | Wave 133d: sporePrint NUCLEUS deployed on golgi (212 pages). bearDog CryptoProvider panic (UNIT-DIV-04) blocks Caddy→bearDog TLS cutover — deferred to 134b sovereignty sprint. WAN mesh overlay live (flockGate↔sporeGate WireGuard). Forgejo relay upgraded to bidirectional 39-repo golgi relay (15-min cycle). SHOW_HN S-10 (sporePrint inner membrane) added as external proof target. Channel 3 status updated. |
| 2026-06-10 | Wave 107: **S4 GRADUATED** — 7-day BTSP auth gate PASSED (Jun 9). All 4 sovereignty shadows (S1-S4) now sovereign on inner membrane. 4-gate mesh collective LIVE. Deterministic deployment codified. NUCLEUS supervision shipped. |
| 2026-06-04 | Wave 77b: Diderm membrane architecture — added §3b layer model, sovereignty shadow membrane applicability table. S-tracks now apply to inner membrane (`primal.eco`); outer membrane may retain commercial. Cross-membrane validation added. |
| 2026-06-02 | Wave 68: grapheneGate, topology routing, perceptron design, Songbird relay design, TCP Tier 5 release enforcement |
| 2026-05-15 | Initial version — sovereignty standards codified from ecosystem practice |
