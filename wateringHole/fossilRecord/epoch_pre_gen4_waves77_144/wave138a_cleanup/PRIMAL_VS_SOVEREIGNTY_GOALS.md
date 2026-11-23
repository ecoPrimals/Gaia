<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Primal Goals vs Sovereignty Goals — A Layer Separation

**Date**: May 15, 2026
**Status**: Active
**Authority**: WateringHole Consensus

---

## Why This Separation Matters

"Make BearDog do TLS" sounds like one goal. It is actually two:

1. **Primal goal**: BearDog ships a `tls.terminate` capability in Rust
   (rustls, X.509, SNI routing, cert auto-renewal, rate limiting)
2. **Sovereignty goal**: Replace Cloudflare TLS termination with BearDog
   TLS on the inner membrane VPS, validated by 7-day shadow run parity

The primal goal is upstream work (primalSpring). The sovereignty goal is
downstream work (projectNUCLEUS). They overlap — the primal goal enables
the sovereignty goal — but they are not the same thing. Confusing them
leads to shipping capabilities that nobody deploys, or deploying
configurations that haven't been validated at the primal layer.

This document separates them, maps the overlaps, defines what "validated"
means at each layer, and charts the path to the final evolution:
**sovereign, self-hosted, safe primal compositions**.

---

## The Four Layers

```
Layer 4: SOVEREIGN COMPOSITION     (the final goal)
         Self-hosted, safe, all-primal — zero external deps
         ──────────────────────────────────────────────────
Layer 3: SOVEREIGNTY DEPLOYMENT     (replace externals)
         Shadow runs, parity validation, cutover
         ──────────────────────────────────────────────────
Layer 2: SECURITY VALIDATION        (prove it's safe)
         darkforest, Dark Forest gate, membrane audit
         ──────────────────────────────────────────────────
Layer 1: PRIMAL CAPABILITIES        (ship the Rust)
         primalSpring, method registry, BTSP, MethodGate
```

Each layer validates the one below it. Layer 3 cannot proceed until
Layer 1 ships the capability. Layer 2 validates that Layers 1 and 3
haven't introduced vulnerabilities. Layer 4 is the composition of all
three into a self-sustaining system.

---

## Layer 1: Primal Capabilities (Ship the Rust)

**Owner**: primalSpring (upstream primal teams)
**Language**: 100% Rust, zero C dependencies
**Validation**: primalSpring scenarios, LTEE reproductions, method registry

These are the raw capabilities each primal ships. They exist whether or
not anyone deploys them. They are validated by primalSpring's own
scenario-based testing, not by NUCLEUS deployment.

### Current State (May 15, 2026)

| Primal | Key Sovereignty Capabilities | Methods | Status |
|--------|------------------------------|---------|--------|
| **BearDog** | TLS termination (rustls X.509), BTSP AEAD, ionic tokens, rate limiter, key management, AES-256-GCM vault | 91+ | SHIPPED (Wave 100+) |
| **Songbird** | STUN (RFC 5389), TURN client (RFC 5766), NAT traversal, ConnectionFallbackChain, Cloudflare DDNS | 40+ | SHIPPED (Wave 196-197) |
| **SkunkBat** | MethodGate enforcement, audit ring buffer, anomaly detection, cross-primal forwarding | 30+ | SHIPPED (JH-5 Phase 2+3) |
| **NestGate** | Content pipeline (8 `content.*` methods), KV + blob, 4-transport parity | 50+ | SHIPPED (Session 60) |
| **petalTongue** | Web mode (`--docroot`), NestGate backend, SPA + CORS | 20+ | SHIPPED (Phase 60) |
| **biomeOS** | Composition deploy/reload/shadow, resource envelopes, BearDogVerifier | 50+ | SHIPPED (v3.53-54) |
| **ToadStool** | MethodGate, env contract, `toadstool.validate` | 74 | SHIPPED (S250) |
| **sweetGrass** | Provenance braid, anchoring, ed25519 witness | 30+ | SHIPPED |
| **rhizoCrypt** | DAG sessions, dehydration, Merkle roots | 30+ | SHIPPED |
| **loamSpine** | Ledger commits, spine management, method aliases | 20+ | SHIPPED |
| **Squirrel** | AI dispatch, Ollama backend | 20+ | SHIPPED |
| **barraCuda** | GPU compute, WGSL shaders, precision routing | 72 | SHIPPED (v0.4.0) |
| **coralReef** | Shader compilation, FECS stability | 40+ | SHIPPED (Sprint 7) |

**Total**: 445 methods across 13 primals. Zero open upstream gaps.
8/8 springs at zero debt, 13,750+ tests.

### What "Shipped" Means at Layer 1

A primal capability is shipped when:
- The method exists in the registry (445 canonical)
- It passes primalSpring scenarios (27 scenarios, 77 graphs)
- It has BTSP Phase 3 AEAD (13/13 primals)
- It passes MethodGate enforcement (13/13)
- It passes `cargo deny` (zero ring/openssl deps)
- It has Edition 2024 compliance
- It has plasmidBin binaries with BLAKE3 checksums

**Layer 1 does NOT validate**:
- Whether the capability works in production deployment
- Whether it can replace an external service
- Whether it's secure on external substrate
- Whether it composes safely with other primals

Those are Layer 2, 3, and 4 concerns.

---

## Layer 2: Security Validation (Prove It's Safe)

**Owner**: projectNUCLEUS (darkforest, security_validation.sh)
**Language**: Rust (darkforest v0.2.1) + bash validation scripts
**Validation**: 5-layer pen test, Dark Forest gate, membrane audit

Layer 2 validates that primal capabilities (Layer 1) and sovereignty
deployments (Layer 3) haven't introduced security vulnerabilities. This
layer runs continuously — before and after every evolution step.

### What Layer 2 Validates

| Scope | Tool | Checks | Result |
|-------|------|--------|--------|
| Gate OS/network | `security_validation.sh` Layer 1 | UFW, hidepid, iptables, DNS | PASS |
| Primal API surface | `security_validation.sh` Layer 2 | MethodGate, binding, auth modes | 13/13 enforced |
| Application surface | `security_validation.sh` Layer 3 | JupyterHub headers, paths, sessions | PASS |
| ABG tier enforcement | `tier_enforcement_test.sh` Layer 4 | Filesystem, network, process isolation | 62 assertions, 0 FAIL |
| Pentest + fuzz + crypto | darkforest v0.2.1 Layer 5 | 3 threat actors, 13 crypto checks | 175 PASS, 0 FAIL |
| Observer surface | `darkforest --suite observer` | Theme, nav, links, source stripping | 86 PASS, 0 FAIL |
| Deploy graph structure | `dark_forest_gate_local.sh` | 5 pillars, 33 checks | PASS |
| VPS membrane | `darkforest_membrane.sh` Layer 6 | MEM-01 through MEM-15 | 17 PASS, 0 FAIL |

### What Layer 2 Does NOT Validate

- Whether a primal capability exists (that's Layer 1)
- Whether a sovereignty deployment achieves parity (that's Layer 3)
- Whether the full composition is self-sustaining (that's Layer 4)

Layer 2 answers one question: **is it safe?**

### Security ≠ Sovereignty

A system can be secure but not sovereign (Cloudflare terminates TLS
perfectly securely — but we don't own it). A system can be sovereign but
not secure (a home server with no firewall is fully owned but fully
exposed).

Security validation is a **gate**, not a goal. Every sovereignty step
must pass through it. But passing Layer 2 does not mean sovereignty is
achieved — it means sovereignty hasn't broken anything.

---

## Layer 3: Sovereignty Deployment (Replace Externals)

**Owner**: projectNUCLEUS (deploy scripts, benchScale, shadow runs)
**Language**: Bash orchestration + Rust validation
**Validation**: Calibrate → shadow → cutover protocol

Layer 3 is where primal capabilities (Layer 1) replace external services.
Each replacement follows the three-step protocol: capture baselines from
the external, run the primal in parallel, cut over when parity is proven.

### The Separation: Primal Goal vs Sovereignty Goal

| External Service | Primal Goal (L1) | Sovereignty Goal (L3) | Overlap | Status |
|-----------------|-------------------|----------------------|---------|--------|
| **Cloudflare TLS** | BearDog ships `tls.terminate` with rustls, SNI, ACME, rate limiter | Replace Cloudflare :443 with BearDog :8443 on VPS, prove p50 < 73ms | BearDog TLS capability enables the replacement | L1: SHIPPED. L3: shadow LIVE (3ms RPC). `membrane.primals.eco` ACME cert LIVE |
| **cloudflared tunnel** | Songbird ships STUN/TURN/NAT/fallback chain | Replace cloudflared with Songbird relay on VPS, prove 100% reachability | Songbird NAT capability enables the replacement | L1: SHIPPED. L3: relay LIVE, **HTTP parity PASS** (68ms vs 89ms) |
| **Cloudflare DNS** | Songbird ships DDNS integration | Deploy knot-dns on VPS, transfer NS records, run sovereign authoritative DNS | Songbird DDNS is a helper, not the DNS server itself | L1: SHIPPED (DDNS). L3: NOT STARTED (knot-dns) |
| **PAM passwords** | BearDog ships ionic tokens + `auth.issue_session` | Replace PAM auth with BTSP tokens on JupyterHub, prove 99.9% success rate | BearDog token capability enables BTSP auth | L1: SHIPPED. L3: dual-auth ACTIVE |
| **GitHub Pages** | NestGate ships `content.*` pipeline; petalTongue ships web mode | Serve primals.eco from NestGate cache via petalTongue, prove TTFB within 10% | NestGate + petalTongue compose into a content server | L1: SHIPPED. L3: Content synced to VPS (19MB). Caddy serving at parity. petalTongue backend pending |
| **GitHub Repos** | (No primal capability needed) | Forgejo pulls from GitHub server-side (25 native mirrors + 6 timer-synced). Inversion when covalent gates host Forgejo. | No overlap — this is pure ops | L3: ACTIVE (31 repos synced + 1 inner-only) |
| **GitHub Actions** | (No primal capability needed) | Port 74 workflows to Forgejo Actions or self-hosted runners | No overlap — this is pure ops | L3: NOT STARTED |
| **GitHub Releases** | NestGate ships blob storage | Wire `fetch.sh` to NestGate instead of GitHub Releases API | NestGate blob capability enables the replacement | L1: SHIPPED. L3: UNBLOCKED |
| **crates.io / PyPI** | (No primal capability needed) | Vendor deps, private registry, offline builds | No overlap — build tooling | L3: LOW PRIORITY |
| **Docker Hub** | NestGate ships OCI blob store potential | Wire ToadStool to NestGate OCI backend | NestGate capability enables OCI storage | L1: SHIPPED. L3: UNBLOCKED |
| **Anthropic / OpenAI** | barraCuda ships WGSL inference | Run Ollama locally, route Squirrel through barraCuda | barraCuda GPU capability enables local AI | L1: PARTIAL. L3: PARTIAL (Ollama works) |
| **NCBI / UniProt** | (No primal capability needed) | Local mirror + provenance tracking via sweetGrass | sweetGrass witnesses data lineage, not the data itself | L3: PARTIAL (registry exists) |

### Key Insight: Not All Sovereignty Is Primal

Some sovereignty goals have **zero primal overlap**:
- Forgejo adoption (pure ops — git server configuration)
- GitHub Actions migration (pure ops — CI workflow porting)
- VPS provisioning (pure ops — DigitalOcean API + systemd)
- Credential rotation (pure ops — key management scripts)

These are infrastructure work. They don't need new Rust code. They need
deploy scripts, configuration, and operational discipline.

Other sovereignty goals are **entirely primal-dependent**:
- Replacing Cloudflare TLS → needs BearDog TLS capability
- Replacing cloudflared → needs Songbird NAT capability
- Replacing GitHub Pages → needs NestGate + petalTongue composition

These cannot begin until Layer 1 ships. But Layer 1 shipping does not
mean they're done — Layer 3 deployment and Layer 2 validation remain.

### What "Sovereign" Means at Layer 3

A service is sovereign when:
- The external dependency is **removed** (not just shadowed)
- The primal replacement runs on **owned infrastructure** (gate or VPS)
- 7-day shadow run proves **parity or superiority**
- darkforest validation passes **before and after** cutover
- Rollback path is documented and tested

### The L3+L4 Membrane Bridge: Continuous Telemetry

Layer 3 (external membrane / VPS) and Layer 4 (internal membrane / gate)
are two faces of the same cell membrane. The key architectural insight:
**shadow runs do not end at cutover**. They become permanent telemetry.

The calibrate-shadow-cutover protocol remains, but shadow collection
continues even after a primal reaches parity and replaces an external:

- **Regression detection**: sovereign TLS could degrade after a BearDog update
- **Baseline drift**: Cloudflare's behavior changes over time (their edge moves)
- **Cost monitoring**: VPS bandwidth, gate CPU, Songbird relay load
- **Bonding model validation**: different trust levels produce different latency profiles

Implementation:
- `deploy/membrane_telemetry.sh` — unified collection across both membranes (cron every 15 min)
- `deploy/membrane_summary.sh` — rolling 7-day summary with cutover gates
- `validation/baselines/membrane_7day.toml` — canonical state snapshot (committed)
- `routing_config.toml [telemetry]` — `shadow_mode = "permanent"`, SkunkBat correlation enabled

The telemetry data feeds both Layer 3 (parity validation before cutover)
and Layer 4 (composition health after cutover). This is how the two
layers connect: through a shared data plane that never stops collecting.

---

## Layer 4: Sovereign Composition (The Final Goal)

**Owner**: projectNUCLEUS + primalSpring (composition is cross-cutting)
**Language**: Rust (all primals) + TOML (deploy graphs)
**Validation**: Full NUCLEUS deployment with zero external dependencies

Layer 4 is the composition of Layers 1-3 into a self-sustaining system.
It is the end state: **sovereign, self-hosted, safe primal compositions**.

### What Layer 4 Looks Like

```
A request arrives at primals.eco:
  → DNS resolves via sovereign knot-dns on VPS (not Cloudflare)
  → TLS terminates via Songbird on VPS (not Cloudflare)
  → Content-aware routing classifies the request
  → Static content served from NestGate cache on VPS
  → Dynamic content proxied to gate via BTSP tunnel
      → BearDog authenticates with ionic token
      → biomeOS routes to appropriate primal
      → ToadStool dispatches workload
      → Provenance trio records execution
      → NestGate stores output
      → sweetGrass braids attribution
  → Response returns through Songbird tunnel
  → SkunkBat audits the entire chain
  → No external service touched. Zero. None.
```

### What Layer 4 Requires

| Requirement | Layer | Status |
|-------------|-------|--------|
| All 13 primal capabilities shipped | L1 | DONE (445 methods) |
| All primal APIs secure (MethodGate, BTSP) | L2 | DONE (13/13 enforced) |
| Gate security validated (5-layer + gate) | L2 | DONE (267+ PASS) |
| VPS membrane validated | L2 | DONE (17 PASS) |
| TLS sovereign on VPS | L3 | Shadow LIVE (BearDog 51x faster) |
| NAT sovereign on VPS | L3 | Relay LIVE (100% reachable) |
| DNS sovereign on VPS | L3 | NOT STARTED |
| Auth sovereign (BTSP replaces PAM) | L3 | Dual-auth ACTIVE |
| Content sovereign (NestGate + petalTongue) | L3 | UNBLOCKED |
| Git sovereign (Forgejo primary) | L3 | ACTIVE (32 repos) |
| CI/CD sovereign (Forgejo Actions) | L3 | NOT STARTED |
| biomeOS composition orchestration | L1+L4 | SHIPPED (v3.53-54) |
| Deploy graph validation | L2 | DONE (Dark Forest PASS) |

### The Final Composition: What It Validates

Layer 4 validates something none of the other layers can: that the
**composed system works end-to-end without external dependencies**. A
primal can ship a capability (L1), the capability can be secure (L2),
and the deployment can replace an external (L3) — but if the composed
system falls over when you remove Cloudflare, all three layers proved
nothing useful.

Layer 4 is the integration test of sovereignty.

---

## The Overlaps (Where Primal and Sovereignty Converge)

Some work is genuinely both a primal goal and a sovereignty goal. These
overlaps are where the ecosystem's evolution is most efficient — shipping
one capability advances both fronts:

### Direct Overlaps (one capability, two purposes)

| Capability | Primal Purpose | Sovereignty Purpose |
|-----------|----------------|-------------------|
| BearDog TLS termination | Sovereign trust boundary (crypto identity) | Replace Cloudflare TLS on membrane |
| BearDog AES-256-GCM vault | Key management primitive | Encrypt credentials on external substrate |
| Songbird TURN relay | NAT traversal for cross-gate routing | Replace cloudflared tunnel |
| Songbird DDNS | Dynamic DNS for mobile gates | Sovereign DNS record management |
| NestGate content pipeline | Content-addressed storage | Replace GitHub Pages CDN |
| petalTongue web mode | UI rendering from NestGate | Sovereign content serving |
| SkunkBat MethodGate | API security enforcement | Validates all sovereignty deployments |
| sweetGrass attribution | Provenance for science workloads | Witnesses sovereignty cutover events |

### Layer Validations (one layer validates another)

| Validator Layer | Validates | What It Checks |
|----------------|-----------|----------------|
| L2 (security) | L1 (primal) | "Does this capability bind localhost? Does MethodGate enforce?" |
| L2 (security) | L3 (sovereignty) | "Did this deployment introduce new attack surface?" |
| L3 (sovereignty) | L1 (primal) | "Does this capability work in production under real load?" |
| L4 (composition) | L1+L2+L3 | "Does the whole thing work with zero external dependencies?" |

### Non-Overlaps (pure primal or pure sovereignty)

| Pure Primal (no sovereignty implication) | Pure Sovereignty (no primal needed) |
|----------------------------------------|--------------------------------------|
| barraCuda WGSL shader compilation | Forgejo adoption (git server ops) |
| coralReef FECS stability proofs | GitHub Actions migration (CI ops) |
| loamSpine ledger commit mechanics | VPS sizing and provisioning |
| rhizoCrypt DAG session internals | SSH key rotation |
| ToadStool workload dispatch | `.gitignore` and repo hygiene |
| Squirrel AI routing internals | Cloudflare dashboard management |

---

## The Evolution Arc

### Phase A: Security Foundation (mostly Rust)

**Priority**: Stability/security comes first.

This phase is complete. darkforest (Rust), MethodGate (Rust in every
primal), BTSP Phase 3 AEAD (Rust), ionic tokens (Rust Ed25519),
hidepid/iptables/UFW (OS hardening).

All security validation tooling is in Rust (darkforest v0.2.1: 8
modules, zero runtime deps, 175 PASS). Bash scripts orchestrate the
Rust validators — they don't implement security logic.

**What Rust gives us**: auditable, compiled, no runtime dependencies,
no supply chain injection, deterministic security checks.

### Phase B: Sovereign Parallels (Rust capabilities + deployment ops)

**Priority**: Sovereign solutions — replace externals with primals.

This phase is active. The Rust work (L1) is mostly shipped. The
deployment work (L3) is in progress:

| Sovereign Parallel | Rust Work (L1) | Deployment Work (L3) |
|-------------------|-----------------|---------------------|
| TLS termination | BearDog rustls (SHIPPED) | Shadow on :8443 (LIVE) |
| NAT traversal | Songbird TURN (SHIPPED) | VPS relay (LIVE) |
| Auth | BearDog ionic tokens (SHIPPED) | JupyterHub dual-auth (ACTIVE) |
| Content serving | NestGate + petalTongue (SHIPPED) | Shadow run (UNBLOCKED) |
| DNS | Songbird DDNS (SHIPPED) | knot-dns deploy (NOT STARTED) |
| Git hosting | N/A | Forgejo primary (ACTIVE) |
| Credential vault | BearDog AES-256-GCM (SHIPPED) | VPS encryption (DONE) |

The pattern: Rust capabilities ship upstream, then deployment validates
them downstream. The gap is always in the deployment, not the Rust.

### Phase C: Sovereign Self-Hosted (Rust compositions)

**Priority**: Primal composition — composed primals replace monoliths.

This is the final evolution. Not "BearDog does TLS" and "Songbird does
NAT" separately, but **Tower does secure networking** — the Tower atomic
(BearDog + Songbird) composing TLS termination with NAT traversal with
BTSP authentication with audit logging into a single deployed boundary.

```
Tower Atomic = BearDog (crypto identity)
             + Songbird (transport + TLS)
             + SkunkBat (defense + audit)
             Composed via biomeOS deploy graph
             Deployed as systemd services (or biomeOS-managed)
             Validated by darkforest --suite membrane
```

The composition layer is where Rust and sovereignty fully converge:
- The deploy graph is a TOML file (validated by Dark Forest gate)
- Each node is a Rust binary from plasmidBin (BLAKE3-checksummed)
- The composition runs on owned hardware (gate or VPS)
- The composition replaces an entire external service cluster
- The composition is validated end-to-end by Layer 4

### Phase D: The Endgame — biomeOS as Sovereign OS

When all three atomics (Tower, Node, Nest) run as compositions on
sovereign hardware, orchestrated by biomeOS deploy graphs, with all
external services replaced by primal compositions:

```
Full NUCLEUS = Tower (BearDog + Songbird + SkunkBat)
             + Node  (ToadStool + barraCuda + coralReef)
             + Nest  (NestGate + rhizoCrypt + loamSpine + sweetGrass)
             + Meta  (biomeOS + Squirrel + petalTongue)

Running on: owned gate hardware + VPS touchpoints
Auth:       BTSP (BearDog), not PAM/Cloudflare Access
TLS:        Songbird, not Cloudflare/Let's Encrypt edge
NAT:        Songbird, not cloudflared
DNS:        knot-dns, not Cloudflare NS
Content:    NestGate + petalTongue, not GitHub Pages
CI:         Forgejo Actions, not GitHub Actions
Git:        Forgejo, not GitHub
Storage:    NestGate, not S3/Docker Hub
Compute:    ToadStool + barraCuda, not cloud VMs
AI:         Squirrel + Ollama + barraCuda, not Anthropic/OpenAI
```

Zero external service dependencies. Fully sovereign. Fully in Rust.
Fully composed from primals. Every interaction validated by darkforest.

The irreducible externals remain: domain registrar, Linux kernel, GPU
drivers, ACME browser trust chain, VPS commodity substrate. These are
physics and coordination constraints, not sovereignty failures.

---

## Tracking: Where Are We Today?

```
Layer 1 (Primal Caps):     ██████████  COMPLETE — 445 methods, 13/13 primals, zero upstream gaps
Layer 2 (Security):        ██████████  COMPLETE — Horizon 1 resolved, darkforest + gate + membrane PASS
Layer 3 (Sovereignty):     ██████░░░░  IN PROGRESS — TLS LIVE (ACME cert), HTTP parity PASS, 4 shadows LIVE, 4 not started
Layer 4 (Composition):     ██░░░░░░░░  EARLY — Tower on VPS (no biomeOS), Full NUCLEUS on gate
```

### Layer 3 Detail

| Sovereignty Target | Score | Blocking |
|-------------------|-------|----------|
| TLS replacement | █████████░ | `membrane.primals.eco` ACME cert LIVE (Let's Encrypt E8). BearDog 3ms RPC vs 120ms CF. DNS grey-cloud proven — expand to `primals.eco` when ready |
| NAT replacement | ████████░░ | HTTP parity PASS (VPS 68ms vs GH Pages 89ms, 10 samples). TLS parity 130ms vs 96ms (within 35%, expected VPS vs CDN) |
| Auth replacement | ██████░░░░ | 7-day shadow run completion |
| DNS sovereignty | ██░░░░░░░░ | knot-dns deployment |
| Content sovereignty | █████░░░░░ | sporePrint synced to VPS NestGate cache (19MB). Caddy serves real content. petalTongue backend wiring pending |
| Git sovereignty | ███████░░░ | Forgejo Actions (CI) |
| CI sovereignty | █░░░░░░░░░ | 74 workflows to port |
| Registry sovereignty | █░░░░░░░░░ | NestGate OCI wiring |
| AI sovereignty | ████░░░░░░ | barraCuda WGSL maturity |
| Data sovereignty | █████░░░░░ | KEGG license, mirror completeness |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-15 | Sovereignty targets executed: `membrane.primals.eco` ACME cert LIVE, HTTP parity PASS (68ms vs 89ms), BearDog probe fixed (3ms), BTSP auth journald wiring, content synced to VPS |
| 2026-05-15 | L3+L4 membrane bridge: continuous telemetry model, permanent shadow collection |
| 2026-05-15 | Initial version — primal/sovereignty goal separation formalized |
